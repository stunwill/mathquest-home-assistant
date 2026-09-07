from __future__ import annotations

import json
from collections import defaultdict
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0410, v0420

app = v0420.app
app.version = '0.43.0'
legacy.APP_VERSION = '0.43.0'

DIAGNOSTIC_OUTCOME_ALIASES = {
    'VC2M5N06': 'VC2M4N06',
    'VC2M6N03': 'VC2M4N03',
}


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _diagnostic_worksheets(session: Session, student_id: int) -> list[legacy.Worksheet]:
    return list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.session_kind == 'diagnostic',
    ).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())).all())


def _latest_completed_diagnostic(session: Session, student_id: int) -> legacy.Worksheet | None:
    return session.scalar(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.session_kind == 'diagnostic',
        legacy.Worksheet.completed_at.is_not(None),
    ).order_by(legacy.Worksheet.completed_at.desc(), legacy.Worksheet.id.desc()))


def _diagnostic_question_row(question: legacy.Question) -> dict[str, Any]:
    attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
    first = attempts[0] if attempts else None
    eventual = any(item.correct for item in attempts)
    support_used = bool((question.hint_count or 0) or question.mentor_started or question.mentor_example_seen)
    independent = bool(first and first.correct and not support_used)
    payload = _payload(question)
    code = (question.skill or '').split(':', 1)[0]
    skill = (question.skill or '').split(':', 1)[-1]
    return {
        'question_id': question.id,
        'level': question.level,
        'outcome_code': code,
        'mapped_outcome_code': DIAGNOSTIC_OUTCOME_ALIASES.get(code, code),
        'skill': skill,
        'independent_correct': independent,
        'eventual_correct': eventual,
        'support_used': support_used,
        'hints': int(question.hint_count or 0),
        'worked_example_seen': bool(question.mentor_example_seen),
        'confidence': None,
        'curriculum_level': payload.get('curriculum_level', question.level),
    }


def _prior_evidence_count(session: Session, student_id: int, outcome_code: str, current_diagnostic_id: int) -> int:
    questions = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.session_kind != 'parent_test',
        legacy.Worksheet.id != current_diagnostic_id,
        legacy.Question.answered_at.is_not(None),
    )).all())
    return sum(1 for question in questions if v0230._outcome_code(question) == outcome_code)


def diagnostic_placement_snapshot(session: Session, student_id: int) -> dict[str, Any]:
    worksheet = _latest_completed_diagnostic(session, student_id)
    if not worksheet:
        return {
            'status': 'not_completed',
            'worksheet_id': None,
            'completed_at': None,
            'levels': [],
            'demonstrated': [],
            'supported': [],
            'needs_more_evidence': [],
            'recommended_focus': None,
            'student_message': 'Complete the Level 5 and Level 6 diagnostic so MathQuest can choose a useful starting point.',
        }

    confidence = v0230._confidence_events(session, student_id)
    rows = []
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        row = _diagnostic_question_row(question)
        row['confidence'] = confidence.get(question.id)
        rows.append(row)

    levels = []
    for level in (5, 6):
        level_rows = [row for row in rows if row['level'] == level]
        levels.append({
            'level': level,
            'attempted': len(level_rows),
            'independent_correct': sum(row['independent_correct'] for row in level_rows),
            'eventual_correct': sum(row['eventual_correct'] for row in level_rows),
            'support_used': sum(row['support_used'] for row in level_rows),
        })

    by_outcome: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_outcome[row['mapped_outcome_code']].append(row)

    mastery = {item['code']: item for item in v0230.outcome_mastery(session, student_id)}
    demonstrated: list[dict[str, Any]] = []
    supported: list[dict[str, Any]] = []
    needs_more: list[dict[str, Any]] = []
    for code, evidence_rows in by_outcome.items():
        existing = mastery.get(code, {})
        title = existing.get('title') or code
        strand = existing.get('strand') or 'Mathematics'
        independent = sum(row['independent_correct'] for row in evidence_rows)
        eventual = sum(row['eventual_correct'] for row in evidence_rows)
        support_count = sum(row['support_used'] for row in evidence_rows)
        item = {
            'code': code,
            'strand': strand,
            'title': title,
            'diagnostic_questions': len(evidence_rows),
            'independent_correct': independent,
            'eventual_correct': eventual,
            'support_used': support_count,
            'prior_evidence_questions': _prior_evidence_count(session, student_id, code, worksheet.id),
            'current_evidence_questions': int(existing.get('questions', 0) or 0),
            'historical_status': existing.get('status', 'not_assessed'),
            'target_skill': existing.get('target_skill'),
        }
        if independent == len(evidence_rows) and len(evidence_rows) >= 3:
            demonstrated.append(item)
        elif eventual > independent or support_count:
            supported.append(item)
        else:
            needs_more.append(item)

    outcomes = list(mastery.values())
    recommendation = v0230.next_session_recommendation(session, student_id, outcomes)
    explanation = v0410.student_recommendation_explanation(recommendation, outcomes)
    if demonstrated and supported:
        student_message = 'MathQuest found some strong starting evidence and some skills that need a little more practice together.'
    elif demonstrated:
        student_message = 'MathQuest found some strong starting evidence. Your next sessions will gather a little more evidence before increasing difficulty.'
    else:
        student_message = 'MathQuest has a useful starting point, but needs a little more evidence before making stronger claims.'

    return {
        'status': 'complete',
        'worksheet_id': worksheet.id,
        'completed_at': worksheet.completed_at.isoformat() if worksheet.completed_at else None,
        'levels': levels,
        'demonstrated': demonstrated,
        'supported': supported,
        'needs_more_evidence': needs_more,
        'recommended_focus': {
            'mode': recommendation.get('mode'),
            'title': recommendation.get('title'),
            'outcome_code': recommendation.get('outcome_code'),
            'target_skill': recommendation.get('target_skill'),
            'prerequisite_for': recommendation.get('prerequisite_for'),
            'explanation': explanation.get('text'),
        },
        'student_message': student_message,
        'limitations': 'This six-question diagnostic is placement evidence only and does not certify mastery of an entire curriculum level.',
    }


def parent_diagnostic_snapshot(session: Session, student_id: int) -> dict[str, Any]:
    placement = diagnostic_placement_snapshot(session, student_id)
    attempts = _diagnostic_worksheets(session, student_id)
    placement['attempt_history'] = [{
        'worksheet_id': item.id,
        'started_at': item.started_at.isoformat() if item.started_at else None,
        'completed_at': item.completed_at.isoformat() if item.completed_at else None,
        'status': item.status,
        'score': item.score,
        'total': item.total,
    } for item in attempts]
    return placement


@app.get('/api/learning/diagnostic-placement-v0430')
def diagnostic_placement(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    snapshot = diagnostic_placement_snapshot(session, student_id)
    if user.role == 'student':
        return {
            'status': snapshot['status'],
            'completed_at': snapshot['completed_at'],
            'student_message': snapshot['student_message'],
            'demonstrated': [{k: item.get(k) for k in ('strand', 'title', 'target_skill')} for item in snapshot['demonstrated']],
            'supported': [{k: item.get(k) for k in ('strand', 'title', 'target_skill')} for item in snapshot['supported']],
            'needs_more_evidence': [{k: item.get(k) for k in ('strand', 'title', 'target_skill')} for item in snapshot['needs_more_evidence']],
            'recommended_focus': {
                'title': (snapshot.get('recommended_focus') or {}).get('title'),
                'target_skill': (snapshot.get('recommended_focus') or {}).get('target_skill'),
                'explanation': (snapshot.get('recommended_focus') or {}).get('explanation'),
            },
        }
    return parent_diagnostic_snapshot(session, student_id)


@app.get('/api/learning/parent-diagnostic-v0430')
def parent_diagnostic(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'parent':
        raise HTTPException(403, 'Parent access required')
    return parent_diagnostic_snapshot(session, v0120.resolve_learner(session).id)


@app.get('/api/v0430/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.43.0',
        'diagnostic_placement_interpretation': True,
        'reuses_outcome_mastery': True,
        'reuses_adaptive_thresholds': True,
        'no_parallel_mastery_score': True,
        'no_global_grade_classification': True,
        'diagnostic_levels': [5, 6],
        'diagnostic_question_count': 6,
        'retake_history_preserved': True,
        'inherits_v0420': True,
    }


v0120._move_spa_fallback_to_end()
