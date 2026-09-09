from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0330, v0440

app = v0440.app
app.version = '0.45.0'
legacy.APP_VERSION = '0.45.0'

def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}

def _snapshot(plan: dict[str, Any], outcomes: list[dict[str, Any]], session: Session, student_id: int) -> dict[str, Any]:
    target = plan.get('primary_target') or {}
    outcome = next((item for item in outcomes if item.get('code') == target.get('outcome_code')), {})
    evidence = v0330._question_evidence(session, student_id, f"{target.get('outcome_code')}:{target.get('skill')}") if target.get('outcome_code') and target.get('skill') else {}
    return {
        'captured_at': datetime.utcnow().isoformat(),
        'outcome_code': target.get('outcome_code'),
        'target_skill': target.get('skill'),
        'status': outcome.get('status'),
        'questions': int(outcome.get('questions', 0) or 0),
        'independent_accuracy': outcome.get('independent_accuracy'),
        'supported_accuracy': outcome.get('supported_accuracy'),
        'review_due': bool(outcome.get('review_due')),
        'skill_questions': int(evidence.get('questions', 0) or 0),
        'skill_independent_accuracy': round(evidence.get('independent', 0) * 100) if evidence else None,
        'skill_eventual_accuracy': round(evidence.get('eventual', 0) * 100) if evidence else None,
    }

def _session_evidence(worksheet: legacy.Worksheet) -> dict[str, Any]:
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    targeted = [(question, _payload(question).get('targeted_session')) for question in questions]
    targeted = [(question, meta) for question, meta in targeted if isinstance(meta, dict)]
    support = 0
    eventual = 0
    independent = 0
    checks = 0
    check_independent = 0
    for question, meta in targeted:
        attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
        help_used = bool((question.hint_count or 0) or question.mentor_started or question.mentor_example_seen)
        support += int(help_used)
        eventual += int(any(item.correct for item in attempts))
        independent += int(bool(attempts and attempts[0].correct and not help_used))
        if meta.get('stage') == 'check':
            checks += 1
            check_independent += int(bool(attempts and attempts[0].correct and not help_used))
    return {
        'questions': len(targeted),
        'answered': sum(bool(question.attempts) for question, _ in targeted),
        'eventual_successes': eventual,
        'independent_successes': independent,
        'support_used_questions': support,
        'independent_checks': check_independent,
        'check_questions': checks,
        'support_then_independent': bool(
            any(bool((_payload(q).get('targeted_session') or {}).get('stage') in ('supported', 'core') and
                     ((q.hint_count or 0) or q.mentor_started or q.mentor_example_seen)) for q in questions)
            and check_independent
        ),
    }

def _annotate_follow_through(session: Session, worksheet: legacy.Worksheet, student_id: int, plan: dict[str, Any]) -> legacy.Worksheet:
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if not questions:
        return worksheet
    payload = _payload(questions[0])
    payload['targeted_session_plan'] = {
        'version': 1,
        'purpose': plan.get('purpose'),
        'student_title': plan.get('student_title'),
        'student_reason': plan.get('student_reason'),
        'target': plan.get('primary_target'),
        'stages': plan.get('stages', []),
        'recommendation_mode': (plan.get('recommendation') or {}).get('mode'),
        'pre_session': _snapshot(plan, v0230.outcome_mastery(session, student_id), session, student_id),
    }
    questions[0].payload = json.dumps(payload)
    session.commit()
    session.refresh(worksheet)
    return worksheet

_original_compose = v0440.compose_targeted_session

def compose_targeted_session(session: Session, student_id: int, plan: dict[str, Any], session_kind: str = 'practice') -> legacy.Worksheet:
    worksheet = _original_compose(session, student_id, plan, session_kind=session_kind)
    return _annotate_follow_through(session, worksheet, student_id, plan)

v0440.compose_targeted_session = compose_targeted_session

def _find_targeted(session: Session, worksheet_id: int, student_id: int) -> legacy.Worksheet:
    worksheet = session.get(legacy.Worksheet, worksheet_id)
    if not worksheet or worksheet.student_id != student_id:
        raise HTTPException(404, 'Worksheet not found')
    if not any(isinstance(_payload(question).get('targeted_session_plan'), dict) for question in worksheet.questions):
        raise HTTPException(404, 'Targeted session not found')
    return worksheet

def _detail(session: Session, worksheet: legacy.Worksheet, student_id: int) -> dict[str, Any]:
    first = next((question for question in sorted(worksheet.questions, key=lambda item: item.position)
                  if isinstance(_payload(question).get('targeted_session_plan'), dict)), None)
    plan = _payload(first).get('targeted_session_plan') if first else {}
    post_outcomes = v0230.outcome_mastery(session, student_id)
    target = plan.get('target') or {}
    post = next((item for item in post_outcomes if item.get('code') == target.get('outcome_code')), {})
    evidence = _session_evidence(worksheet)
    pre = plan.get('pre_session') or {}
    before_questions = int(pre.get('questions', 0) or 0)
    after_questions = int(post.get('questions', before_questions) or before_questions)
    before_independent = pre.get('independent_accuracy')
    after_independent = post.get('independent_accuracy')
    return {
        'available': True,
        'worksheet_id': worksheet.id,
        'completed': bool(worksheet.completed_at),
        'purpose': plan.get('purpose'),
        'title': plan.get('student_title') or target.get('title'),
        'reason': plan.get('student_reason'),
        'target_skill': target.get('skill'),
        'outcome_code': target.get('outcome_code'),
        'prerequisite_for': target.get('prerequisite_for'),
        'stages': plan.get('stages') or [],
        'before': {'questions': before_questions, 'independent_accuracy': before_independent, 'status': pre.get('status')},
        'after': {'questions': after_questions, 'independent_accuracy': after_independent, 'status': post.get('status')},
        'evidence': evidence,
        'evidence_change': {
            'questions_added': max(0, after_questions - before_questions),
            'independent_accuracy_changed': before_independent is not None and after_independent is not None and before_independent != after_independent,
        },
    }

def _student_safe(detail: dict[str, Any]) -> dict[str, Any]:
    evidence = detail['evidence']
    if evidence['support_then_independent']:
        message = 'You used support earlier, then solved a similar question independently.'
    elif evidence['independent_checks'] > 0:
        message = 'You finished with an independent check on this skill.'
    elif evidence['eventual_successes'] > 0:
        message = 'You practised this skill successfully. MathQuest will keep gathering evidence.'
    else:
        message = 'This skill still needs practice, so MathQuest will bring it back again.'
    return {
        'available': True,
        'purpose': detail['purpose'],
        'target_skill': detail['target_skill'],
        'message': message,
        'evidence_added': detail['evidence_change']['questions_added'],
        'independent_checks': evidence['independent_checks'],
    }

@app.get('/api/worksheets/{wid}/targeted-summary-v0450')
def targeted_summary_v0450(wid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    detail = _detail(session, _find_targeted(session, wid, student_id), student_id)
    return _student_safe(detail) if user.role == 'student' else detail

@app.get('/api/learning/targeted-session-detail-v0450')
def targeted_session_detail_v0450(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    worksheet = session.scalar(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.completed_at.is_not(None),
    ).order_by(legacy.Worksheet.completed_at.desc(), legacy.Worksheet.id.desc()))
    if not worksheet or not any(isinstance(_payload(question).get('targeted_session_plan'), dict) for question in worksheet.questions):
        return {'available': False}
    return _student_safe(_detail(session, worksheet, student_id)) if user.role == 'student' else _detail(session, worksheet, student_id)

@app.get('/api/v0450/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.45.0',
        'targeted_session_follow_through': True,
        'before_after_evidence': True,
        'support_to_independence_summary': True,
        'reuses_v0440_plan_and_mastery': True,
        'inherits_v0440': True,
    }

v0120._move_spa_fallback_to_end()
