from __future__ import annotations

import json
import random
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0170, v0230, v0330, v0340, v0430

app = v0430.app
app.version = '0.44.0'
legacy.APP_VERSION = '0.44.0'

SESSION_PURPOSES = {'learn', 'practice', 'consolidate', 'review', 'prerequisite', 'challenge'}
STAGE_LABELS = {
    'reconnect': 'Reconnect',
    'supported': 'Supported practice',
    'core': 'Core practice',
    'transfer': 'Transfer',
    'check': 'Independent check',
}


def _safe_topic(value: str | None) -> str:
    topic = (value or 'number').lower().replace(' & ', '_').replace(' ', '_')
    return 'number' if topic == 'number_algebra' else topic


def _plan_purpose(recommendation: dict[str, Any], outcome: dict[str, Any] | None) -> str:
    if recommendation.get('prerequisite_for'):
        return 'prerequisite'
    if recommendation.get('mode') == 'review':
        return 'review'
    if outcome and outcome.get('questions', 0) < v0330.THRESHOLDS.minimum_questions:
        return 'learn'
    if outcome and outcome.get('status') in ('needs_support', 'developing'):
        return 'consolidate'
    return 'practice'


def build_learning_plan(session: Session, student_id: int, minutes: int | None = None) -> dict[str, Any]:
    outcomes = v0230.outcome_mastery(session, student_id)
    recommendation = v0230.next_session_recommendation(session, student_id, outcomes)
    if recommendation.get('mode') == 'diagnostic':
        return {
            'kind': 'diagnostic', 'minutes': 15, 'purpose': 'learn', 'primary_target': None,
            'student_title': 'Find the best starting point',
            'student_reason': recommendation.get('reason'), 'stages': [], 'recommendation': recommendation,
        }
    by_code = {item['code']: item for item in outcomes}
    outcome = by_code.get(recommendation.get('outcome_code'))
    purpose = _plan_purpose(recommendation, outcome)
    target_skill = recommendation.get('target_skill')
    question_count = {5: 6, 10: 12, 15: 18}[minutes or recommendation['minutes']]
    if question_count <= 6:
        roles = ['reconnect', 'supported', 'core', 'core', 'transfer', 'check']
    elif question_count <= 12:
        roles = ['reconnect', 'supported'] + ['core'] * 6 + ['transfer'] * 2 + ['check'] * 2
    else:
        roles = ['reconnect', 'supported'] + ['core'] * 10 + ['transfer'] * 3 + ['check'] * 3
    title = outcome.get('title') if outcome else recommendation.get('title')
    if purpose == 'review':
        student_reason = f'Revisit {title.lower()} so it stays fresh.'
    elif purpose == 'prerequisite':
        student_reason = f'Build {title.lower()} because it supports your next challenge.'
    elif purpose == 'learn':
        student_reason = f'Practise {title.lower()} and gather more evidence before increasing difficulty.'
    elif purpose == 'consolidate':
        student_reason = f'Build confidence with {title.lower()} and work towards doing it independently.'
    else:
        student_reason = f'Keep strengthening {title.lower()} with varied practice.'
    return {
        'kind': 'targeted',
        'minutes': minutes or recommendation['minutes'],
        'question_count': question_count,
        'purpose': purpose,
        'primary_target': {
            'outcome_code': recommendation.get('outcome_code'),
            'title': title,
            'topic': _safe_topic(recommendation.get('topic')),
            'skill': target_skill,
            'prerequisite_for': recommendation.get('prerequisite_for'),
            'evidence_questions': int((outcome or {}).get('questions', 0) or 0),
            'status': (outcome or {}).get('status'),
            'review_due': bool((outcome or {}).get('review_due')),
        },
        'student_title': title,
        'student_reason': student_reason,
        'stages': roles,
        'recommendation': recommendation,
    }


def _candidate(generator, seed: str, blocked: set[str]):
    for attempt in range(80):
        generated = generator(random.Random(f'{seed}:{attempt}'))
        key = legacy.question_identity(generated[1], generated[3])
        if key not in blocked:
            blocked.add(key)
            return generated
    return None


def _annotate_stage(question: legacy.Question, plan: dict[str, Any], role: str, index: int) -> None:
    try:
        payload = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    payload['targeted_session'] = {
        'version': 1,
        'purpose': plan['purpose'],
        'outcome_code': plan['primary_target']['outcome_code'],
        'target_skill': plan['primary_target']['skill'],
        'prerequisite_for': plan['primary_target']['prerequisite_for'],
        'stage': role,
        'stage_label': STAGE_LABELS[role],
        'position': index + 1,
        'total': plan['question_count'],
    }
    question.payload = json.dumps(payload)


def compose_targeted_session(session: Session, student_id: int, plan: dict[str, Any], session_kind: str = 'practice') -> legacy.Worksheet:
    target = plan['primary_target']
    worksheet = legacy.create_worksheet(
        session,
        student_id,
        target['topic'],
        question_count=plan['question_count'],
        session_kind=session_kind,
        target_minutes=plan['minutes'],
    )
    # Run the inherited adaptive purpose/quality policy before final target composition.
    # Later quality replacement must not erase the session's recommended target or stage metadata.
    v0330.apply_adaptive_daily_learning(session, worksheet, student_id)
    session.flush()
    session.refresh(worksheet)

    generator = v0170.FOCUS_GENERATORS.get(target['topic'], {}).get(target['skill'])
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    target_count = max(3, round(len(questions) * 0.72)) if generator else 0
    target_positions = set(range(target_count))

    # Only non-target positions need to block their existing identities. Target positions are
    # deliberately being replaced, so their old random identities must not reduce the pool.
    blocked: set[str] = set()
    for index, question in enumerate(questions):
        if index in target_positions:
            continue
        try:
            blocked.add(legacy.question_identity(question.prompt, json.loads(question.payload or '{}')))
        except (TypeError, ValueError):
            blocked.add(legacy.question_identity(question.prompt, {}))

    if generator:
        for index in sorted(target_positions):
            generated = _candidate(generator, f'v0440:{worksheet.id}:{index}', blocked)
            if not generated:
                continue
            skill, prompt, answer_type, payload, answer, working = generated
            questions[index].skill = skill
            questions[index].prompt = prompt
            questions[index].answer_type = answer_type
            questions[index].payload = json.dumps(payload)
            questions[index].correct_answer = str(answer)
            questions[index].working = working

    # Stage metadata is written last so it survives every inherited composition/quality pass.
    for index, question in enumerate(questions):
        _annotate_stage(question, plan, plan['stages'][index], index)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def targeted_session_summary(session: Session, worksheet: legacy.Worksheet, student_id: int) -> dict[str, Any]:
    rows = []
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        try:
            payload = json.loads(question.payload or '{}')
        except (TypeError, ValueError):
            payload = {}
        targeted = payload.get('targeted_session') if isinstance(payload, dict) else None
        if not isinstance(targeted, dict):
            continue
        attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
        support = bool((question.hint_count or 0) or question.mentor_started or question.mentor_example_seen)
        rows.append({
            'stage': targeted.get('stage'),
            'correct': any(item.correct for item in attempts),
            'independent': bool(attempts and attempts[0].correct and not support),
            'support': support,
        })
    if not rows:
        return {'available': False}
    target = json.loads(sorted(worksheet.questions, key=lambda item: item.position)[0].payload or '{}').get('targeted_session', {})
    independent_checks = [row for row in rows if row['stage'] == 'check' and row['independent']]
    early_support = any(row['support'] for row in rows[: max(1, len(rows)//2)])
    later_independent = any(row['independent'] for row in rows[max(1, len(rows)//2):])
    if early_support and later_independent:
        message = 'You used support earlier, then solved a similar question independently.'
    elif independent_checks:
        message = 'You finished with independent practice on this skill.'
    elif any(row['correct'] for row in rows):
        message = 'You practised this skill successfully. MathQuest will keep gathering evidence.'
    else:
        message = 'This skill still needs practice, so MathQuest will bring it back again.'
    return {
        'available': True,
        'purpose': target.get('purpose'),
        'outcome_code': target.get('outcome_code'),
        'target_skill': target.get('target_skill'),
        'message': message,
        'independent_checks': len(independent_checks),
        'support_used': sum(row['support'] for row in rows),
    }


def _remove_prior_recommended_route() -> None:
    app.router.routes[:] = [route for route in app.router.routes if not (
        getattr(route, 'path', None) == '/api/sessions/recommended' and 'POST' in getattr(route, 'methods', set())
    )]


_remove_prior_recommended_route()


@app.get('/api/learning/session-plan-v0440')
def learning_plan(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    plan = build_learning_plan(session, student_id)
    if user.role == 'student':
        return {
            'kind': plan['kind'], 'minutes': plan['minutes'], 'purpose': plan['purpose'],
            'title': plan['student_title'], 'reason': plan['student_reason'],
            'target_skill': (plan.get('primary_target') or {}).get('skill'),
        }
    return plan


@app.post('/api/sessions/recommended')
def recommended_targeted_session(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    plan = build_learning_plan(session, user.id)
    if plan['kind'] == 'diagnostic':
        from . import v0190
        return v0190.new_session(v0190.SessionCreateIn(kind='diagnostic', minutes=15, topic='number_algebra'), user, session)
    worksheet = compose_targeted_session(session, user.id, plan, session_kind=plan['recommendation']['mode'])
    result = legacy.worksheet_view(worksheet)
    result['recommendation'] = plan['recommendation']
    result['learning_plan'] = {
        'purpose': plan['purpose'], 'title': plan['student_title'], 'reason': plan['student_reason'],
        'target_skill': plan['primary_target']['skill'], 'stages': plan['stages'],
    }
    return result


@app.get('/api/worksheets/{wid}/targeted-summary-v0440')
def targeted_summary(wid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    worksheet = session.get(legacy.Worksheet, wid)
    if not worksheet:
        raise HTTPException(404, 'Worksheet not found')
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    if worksheet.student_id != student_id:
        raise HTTPException(404, 'Worksheet not found')
    summary = targeted_session_summary(session, worksheet, student_id)
    if user.role == 'student':
        return {key: summary.get(key) for key in ('available', 'purpose', 'target_skill', 'message')}
    return summary


@app.get('/api/v0440/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.44.0',
        'targeted_learning_sessions': True,
        'explicit_learning_plan': True,
        'recommendation_to_session_contract': True,
        'skill_sensitive_progression': True,
        'support_to_independence_evidence': True,
        'story_adventure_compatible': True,
        'reuses_existing_mastery': True,
        'inherits_v0430': True,
    }


v0120._move_spa_fallback_to_end()
