from __future__ import annotations

from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0440, v0450

app = v0450.app
app.version = '0.46.0'
legacy.APP_VERSION = '0.46.0'

FOLLOW_THROUGH = {
    'continue': 'Continue practising this skill.',
    'consolidate': 'Build confidence with less help.',
    'reteach': 'Revisit the idea with a smaller step.',
    'check_independence': 'Try a similar question independently.',
    'transfer': 'Use the idea in a different situation.',
    'review_later': 'Return to this skill later to help it stick.',
    'return_to_original_target': 'Return to the original target now that its prerequisite is stronger.',
    'progress_to_related_skill': 'Move to a related skill with a careful challenge.',
    'challenge': 'Try a slightly harder application.',
    'gather_more_evidence': 'Gather a little more evidence before deciding what comes next.',
}

def _latest_targeted(session: Session, student_id: int) -> legacy.Worksheet | None:
    worksheets = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.completed_at.is_not(None),
    ).order_by(legacy.Worksheet.completed_at.desc(), legacy.Worksheet.id.desc()).limit(20)).all())
    for worksheet in worksheets:
        if any(isinstance(v0450._payload(question).get('targeted_session_plan'), dict) for question in worksheet.questions):
            return worksheet
    return None

def _decision_from_evidence(evidence: dict[str, Any], purpose: str | None = None,
                            prerequisite_for: str | None = None) -> str:
    answered = int(evidence.get('answered', 0) or 0)
    if answered < 3:
        return 'gather_more_evidence'
    eventual = int(evidence.get('eventual_successes', 0) or 0)
    independent = int(evidence.get('independent_successes', 0) or 0)
    support = int(evidence.get('support_used_questions', 0) or 0)
    checks = int(evidence.get('independent_checks', 0) or 0)
    check_questions = int(evidence.get('check_questions', 0) or 0)
    if not eventual:
        return 'reteach'
    if support >= max(2, round(answered * 0.55)) and independent == 0:
        return 'reteach'
    if prerequisite_for and checks:
        return 'return_to_original_target'
    if support and independent:
        return 'transfer' if checks else 'check_independence'
    if checks and independent >= 2:
        return 'challenge' if check_questions >= 2 else 'progress_to_related_skill'
    if purpose == 'review':
        return 'review_later' if independent else 'continue'
    if independent >= max(3, round(answered * 0.82)):
        return 'review_later'
    return 'consolidate'

def _detail(session: Session, worksheet: legacy.Worksheet, student_id: int) -> dict[str, Any]:
    detail = v0450._detail(session, worksheet, student_id)
    detail['follow_through'] = _decision_from_evidence(
        detail['evidence'],
        detail.get('purpose'),
        detail.get('prerequisite_for'),
    )
    detail['follow_through_label'] = FOLLOW_THROUGH[detail['follow_through']]
    detail['next_action'] = {
        'decision': detail['follow_through'],
        'student_message': FOLLOW_THROUGH[detail['follow_through']],
        'same_target': detail['follow_through'] in ('continue', 'consolidate', 'reteach', 'check_independence'),
    }
    return detail

def _plan_with_memory(session: Session, student_id: int, minutes: int | None = None) -> dict[str, Any]:
    plan = _original_build(session, student_id, minutes)
    previous = _latest_targeted(session, student_id)
    if not previous or plan.get('kind') != 'targeted':
        plan['previous_follow_through'] = None
        return plan
    previous_detail = _detail(session, previous, student_id)
    previous_target = (previous_detail.get('target_skill'), previous_detail.get('outcome_code'))
    current_target = ((plan.get('primary_target') or {}).get('skill'), (plan.get('primary_target') or {}).get('outcome_code'))
    decision = previous_detail['follow_through']
    plan['previous_follow_through'] = {
        'decision': decision,
        'target_skill': previous_target[0],
        'outcome_code': previous_target[1],
        'evidence': previous_detail.get('evidence'),
    }
    if previous_target == current_target:
        plan['follow_through'] = decision
        if decision == 'reteach':
            plan['purpose'] = 'learn'
            plan['student_reason'] = f'Revisit {plan["student_title"].lower()} with a smaller step and a clear example.'
        elif decision == 'check_independence':
            plan['purpose'] = 'consolidate'
            plan['student_reason'] = f'Practise {plan["student_title"].lower()} again, this time with less help.'
        elif decision == 'transfer':
            plan['purpose'] = 'practice'
            plan['student_reason'] = f'Use {plan["student_title"].lower()} in a different way.'
        elif decision == 'review_later':
            plan['student_reason'] = f'Revisit {plan["student_title"].lower()} so it stays fresh.'
        elif decision == 'gather_more_evidence':
            plan['purpose'] = 'learn'
            plan['student_reason'] = f'Practise {plan["student_title"].lower()} so MathQuest can learn what to do next.'
    return plan

_original_build = v0440.build_learning_plan
def build_learning_plan(session: Session, student_id: int, minutes: int | None = None) -> dict[str, Any]:
    return _plan_with_memory(session, student_id, minutes)
v0440.build_learning_plan = build_learning_plan

_original_compose = v0450.compose_targeted_session
def compose_targeted_session(session: Session, student_id: int, plan: dict[str, Any],
                             session_kind: str = 'practice') -> legacy.Worksheet:
    worksheet = _original_compose(session, student_id, plan, session_kind=session_kind)
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if questions:
        payload = v0450._payload(questions[0])
        metadata = payload.get('targeted_session_plan') or {}
        metadata['follow_through_context'] = {
            'previous_decision': plan.get('previous_follow_through', {}).get('decision'),
            'same_target': bool(plan.get('previous_follow_through')),
        }
        payload['targeted_session_plan'] = metadata
        questions[0].payload = __import__('json').dumps(payload)
        session.commit()
        session.refresh(worksheet)
    return worksheet
v0440.compose_targeted_session = compose_targeted_session

@app.get('/api/learning/session-plan-v0460')
def learning_plan_v0460(user: legacy.User = Depends(legacy.current_user),
                        session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    plan = build_learning_plan(session, student_id)
    if user.role == 'student':
        return {
            'kind': plan['kind'],
            'minutes': plan['minutes'],
            'purpose': plan['purpose'],
            'title': plan['student_title'],
            'reason': plan['student_reason'],
            'target_skill': (plan.get('primary_target') or {}).get('skill'),
            'follow_through': plan.get('follow_through'),
        }
    return plan

@app.get('/api/worksheets/{wid}/targeted-summary-v0460')
def targeted_summary_v0460(wid: int, user: legacy.User = Depends(legacy.current_user),
                           session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    worksheet = v0450._find_targeted(session, wid, student_id)
    detail = _detail(session, worksheet, student_id)
    return v0450._student_safe(detail) | {
        'follow_through': detail['follow_through'],
        'next_action': detail['next_action']['student_message'],
    } if user.role == 'student' else detail

@app.get('/api/learning/targeted-session-detail-v0460')
def targeted_session_detail_v0460(user: legacy.User = Depends(legacy.current_user),
                                  session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    worksheet = _latest_targeted(session, student_id)
    if not worksheet:
        return {'available': False}
    detail = _detail(session, worksheet, student_id)
    return v0450._student_safe(detail) | {
        'follow_through': detail['follow_through'],
        'next_action': detail['next_action']['student_message'],
    } if user.role == 'student' else detail

@app.get('/api/v0460/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.46.0',
        'next_session_intelligence': True,
        'explicit_follow_through': sorted(FOLLOW_THROUGH),
        'session_to_session_memory': True,
        'reuses_existing_evidence': True,
        'skill_sensitive_progression': True,
        'inherits_v0450': True,
    }

v0120._move_spa_fallback_to_end()
