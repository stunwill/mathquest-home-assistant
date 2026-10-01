from __future__ import annotations

from typing import Any
from datetime import datetime
import json

from fastapi import Depends
from sqlalchemy import select, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Session, Mapped, mapped_column

from . import main as legacy
from . import v0120, v0330, v0440, v0450

app = v0450.app
app.version = '0.46.0'
legacy.APP_VERSION = '0.46.0'

class AdaptiveFollowThrough(legacy.Base):
    __tablename__ = 'adaptive_follow_through'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    worksheet_id: Mapped[int] = mapped_column(ForeignKey('worksheets.id'), unique=True, index=True)
    outcome_code: Mapped[str | None] = mapped_column(String(40), nullable=True, index=True)
    target_skill: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    decision: Mapped[str] = mapped_column(String(40), index=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class FollowThroughOutcome(legacy.Base):
    """One acted-upon decision and its resulting session, without altering old rows."""
    __tablename__ = 'adaptive_follow_through_outcomes'
    id: Mapped[int] = mapped_column(primary_key=True)
    source_id: Mapped[int] = mapped_column(ForeignKey('adaptive_follow_through.id'), unique=True)
    worksheet_id: Mapped[int] = mapped_column(ForeignKey('worksheets.id'), unique=True, index=True)
    before_evidence: Mapped[str] = mapped_column(Text)
    after_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment: Mapped[str | None] = mapped_column(String(40), nullable=True)
    subsequent_decision: Mapped[str | None] = mapped_column(String(40), nullable=True)
    evaluated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

legacy.Base.metadata.create_all(legacy.engine)

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

def _persist_follow_through(session: Session, worksheet: legacy.Worksheet, detail: dict[str, Any]) -> AdaptiveFollowThrough:
    existing = session.scalar(select(AdaptiveFollowThrough).where(AdaptiveFollowThrough.worksheet_id == worksheet.id))
    if existing:
        return existing
    row = AdaptiveFollowThrough(
        student_id=worksheet.student_id,
        worksheet_id=worksheet.id,
        outcome_code=detail.get('outcome_code'),
        target_skill=detail.get('target_skill'),
        decision=detail['follow_through'],
    )
    session.add(row)
    session.commit()
    session.refresh(row)
    return row

def _pending_follow_through(session: Session, student_id: int) -> AdaptiveFollowThrough | None:
    latest = _latest_targeted(session, student_id)
    if latest is None:
        return None
    return session.scalar(select(AdaptiveFollowThrough).where(
        AdaptiveFollowThrough.student_id == student_id,
        AdaptiveFollowThrough.worksheet_id == latest.id,
        AdaptiveFollowThrough.consumed_at.is_(None),
    ).order_by(AdaptiveFollowThrough.created_at.desc(), AdaptiveFollowThrough.id.desc()))

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
    if purpose == 'review':
        return 'review_later' if independent else 'continue'
    if prerequisite_for and checks:
        return 'return_to_original_target'
    if support and independent:
        return 'transfer' if checks else 'check_independence'
    if checks and independent >= 2:
        return 'challenge' if check_questions >= 2 else 'progress_to_related_skill'
    if independent >= max(3, round(answered * 0.82)):
        return 'review_later'
    return 'consolidate'

def _detail(session: Session, worksheet: legacy.Worksheet, student_id: int, *, persist: bool = True) -> dict[str, Any]:
    detail = v0450._detail(session, worksheet, student_id)
    detail['follow_through'] = _decision_from_evidence(
        detail['evidence'],
        detail.get('purpose'),
        detail.get('prerequisite_for'),
    )
    if detail['evidence']['unanswered']:
        detail['follow_through'] = 'gather_more_evidence'
    elif detail['follow_through'] in ('challenge', 'progress_to_related_skill', 'return_to_original_target'):
        historical = v0330._question_evidence(session, student_id, f"{detail['outcome_code']}:{detail['target_skill']}")
        if v0330._progression_state(historical) != 'ready_to_progress':
            detail['follow_through'] = 'consolidate'
    lineage = session.scalar(select(FollowThroughOutcome).where(FollowThroughOutcome.worksheet_id == worksheet.id))
    if lineage:
        detail['intervention_outcome'] = _evaluate_outcome(session, worksheet, detail, lineage, persist=persist)
        detail['follow_through'] = detail['intervention_outcome']['next_decision']
        if lineage.evaluated_at:
            detail['evidence'] = detail['intervention_outcome']['after_evidence']
    detail['follow_through_label'] = FOLLOW_THROUGH[detail['follow_through']]
    detail['next_action'] = {
        'decision': detail['follow_through'],
        'student_message': FOLLOW_THROUGH[detail['follow_through']],
        'same_target': detail['follow_through'] in ('continue', 'consolidate', 'reteach', 'check_independence'),
    }
    if detail.get('completed') and persist:
        _persist_follow_through(session, worksheet, detail)
    return detail


def _evaluate_outcome(session: Session, worksheet: legacy.Worksheet, detail: dict[str, Any],
                      lineage: FollowThroughOutcome, *, persist: bool = True) -> dict[str, Any]:
    source = session.get(AdaptiveFollowThrough, lineage.source_id)
    before = json.loads(lineage.before_evidence)
    after = detail['evidence']
    decision = detail['follow_through']
    assessment = 'gather_more_evidence'
    message = 'A little more practice will help us choose the next step.'
    if lineage.evaluated_at:
        assessment = lineage.assessment
        decision = lineage.subsequent_decision
        after = json.loads(lineage.after_evidence)
    elif worksheet.completed_at:
        answered = after['answered']
        independent = after['independent_successes']
        enough = answered >= 3 and not after['unanswered']
        strong = enough and independent / answered >= v0330.THRESHOLDS.ready_accuracy
        if not enough:
            decision = 'gather_more_evidence'
        elif not after['eventual_successes'] or (not independent and after['support_used_questions']):
            assessment = 'still_needs_support'
            # Reconsider a failed reteach only when both linked sessions show difficulty.
            if source.decision == 'reteach' and before.get('answered', 0) >= 3 and not before.get('independent_successes'):
                assessment = 'reconsider_learning_path'
                decision = 'gather_more_evidence'
        elif source.decision == 'transfer' and not (
            set(after['independent_transfer_families']) - set(before.get('families', []))
        ):
            assessment = 'transfer_not_confirmed'
            decision = 'consolidate'
        elif strong and after['independent_checks'] and detail.get('evidence_focus'):
            assessment = 'smaller_step_confirmed'
            decision = 'check_independence'
        elif strong and after['independent_checks']:
            assessment = 'independence_confirmed'
            decision = detail['follow_through'] if detail.get('prerequisite_for') or source.decision == 'challenge' else 'review_later'
        elif independent and (
            independent / answered > before.get('independent_successes', 0) / max(1, before.get('answered', 0))
        ):
            assessment = 'improved'
            decision = 'check_independence' if after['support_used_questions'] else 'consolidate'
        else:
            assessment = 'still_needs_support' if after['support_used_questions'] else 'partially_successful'
            decision = 'check_independence' if after['support_used_questions'] else 'consolidate'
        # Session outcomes never bypass the existing longitudinal progression model.
        if decision in ('challenge', 'progress_to_related_skill', 'return_to_original_target'):
            evidence = v0330._question_evidence(session, worksheet.student_id, f"{detail['outcome_code']}:{detail['target_skill']}")
            if v0330._progression_state(evidence) != 'ready_to_progress':
                decision = 'consolidate'
        if persist:
            lineage.after_evidence = json.dumps(after)
            lineage.assessment = assessment
            lineage.subsequent_decision = decision
            lineage.evaluated_at = datetime.utcnow()
            session.commit()
    messages = {
        'still_needs_support': 'This skill still needs support. We will keep working towards doing it independently.',
        'reconsider_learning_path': 'Let’s check a smaller step before practising this again.',
        'transfer_not_confirmed': 'Let’s practise using this idea in a different way.',
        'independence_confirmed': 'You solved this independently. We will return to it later to help it stick.',
        'smaller_step_confirmed': 'You solved the smaller step independently. Next, try the full idea without help.',
        'improved': 'You solved more of this work independently. Next, try it with less help.',
        'partially_successful': 'You made progress. More practice will help it stick.',
    }
    if assessment == 'independence_confirmed' and decision != 'review_later':
        messages['independence_confirmed'] = 'You solved this independently. You’re ready for the next careful step.'
    return {'previous_decision': source.decision, 'assessment': assessment,
            'message': messages.get(assessment, message), 'next_decision': decision,
            'source_worksheet_id': source.worksheet_id, 'worksheet_id': worksheet.id,
            'before_evidence': before, 'after_evidence': after, 'completed': bool(worksheet.completed_at)}

def _plan_with_memory(session: Session, student_id: int, minutes: int | None = None) -> dict[str, Any]:
    plan = _original_build(session, student_id, minutes)
    previous = _latest_targeted(session, student_id)
    if not previous or plan.get('kind') != 'targeted':
        plan['previous_follow_through'] = None
        return plan
    # Plan previews read evidence without persisting or resurrecting decisions.
    previous_detail = _detail(session, previous, student_id, persist=False)
    pending = _pending_follow_through(session, student_id)
    if pending is None:
        existing = session.scalar(select(AdaptiveFollowThrough).where(AdaptiveFollowThrough.worksheet_id == previous.id))
        if existing:
            plan['previous_follow_through'] = None
            return plan
        # Compatibility for completed worksheets predating persisted decisions.
    else:
        previous = session.get(legacy.Worksheet, pending.worksheet_id)
        previous_detail = _detail(session, previous, student_id, persist=False)
    previous_target = (previous_detail.get('target_skill'), previous_detail.get('outcome_code'))
    current_target = ((plan.get('primary_target') or {}).get('skill'), (plan.get('primary_target') or {}).get('outcome_code'))
    decision = pending.decision if pending else previous_detail['follow_through']
    plan['previous_follow_through'] = {
        'id': pending.id if pending else None,
        'worksheet_id': previous.id,
        'decision': decision,
        'target_skill': previous_target[0],
        'outcome_code': previous_target[1],
        'evidence': previous_detail.get('evidence'),
    }
    # Unresolved same-skill work takes precedence, but retain evidence-backed prerequisite routing.
    if previous_target != current_target and decision in ('reteach', 'check_independence', 'consolidate', 'continue', 'transfer', 'gather_more_evidence') and not (plan.get('primary_target') or {}).get('prerequisite_for'):
        first = next(q for q in previous.questions if v0450._payload(q).get('targeted_session_plan'))
        target = v0450._payload(first)['targeted_session_plan'].get('target') or {}
        if target.get('skill') and target.get('outcome_code'):
            plan['primary_target'] = dict(target)
            plan['student_title'] = target.get('title') or previous_detail.get('title') or plan['student_title']
            plan['recommendation'] = {**plan['recommendation'], 'outcome_code': target['outcome_code'], 'target_skill': target['skill'], 'topic': target['topic'], 'title': plan['student_title'], 'mode': 'practice', 'prerequisite_for': target.get('prerequisite_for')}
            current_target = previous_target
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
            outcome = session.scalar(select(FollowThroughOutcome).where(FollowThroughOutcome.worksheet_id == previous.id))
            if outcome and outcome.assessment == 'reconsider_learning_path':
                plan['student_reason'] = 'Let’s check a smaller step before practising this again.'
                if previous_target[1] == 'VC2M4N06' and previous_target[0] == 'written_subtraction':
                    plan['evidence_focus'] = 'subtraction_without_regrouping'
        plan['recommendation']['reason'] = plan['student_reason']
    return plan

_original_build = v0440.build_learning_plan
def build_learning_plan(session: Session, student_id: int, minutes: int | None = None) -> dict[str, Any]:
    return _plan_with_memory(session, student_id, minutes)
v0440.build_learning_plan = build_learning_plan

_original_compose = v0450.compose_targeted_session
def compose_targeted_session(session: Session, student_id: int, plan: dict[str, Any],
                             session_kind: str = 'practice') -> legacy.Worksheet:
    prior = plan.get('previous_follow_through') or {}
    pending = session.get(AdaptiveFollowThrough, prior.get('id')) if prior.get('id') else None
    if pending and pending.student_id == student_id and pending.consumed_at:
        link = session.scalar(select(FollowThroughOutcome).where(FollowThroughOutcome.source_id == pending.id))
        if link:
            return session.get(legacy.Worksheet, link.worksheet_id)
    worksheet = _original_compose(session, student_id, plan, session_kind=session_kind)
    if prior.get('decision') and prior.get('target_skill') == (plan.get('primary_target') or {}).get('skill') and prior.get('outcome_code') == (plan.get('primary_target') or {}).get('outcome_code'):
        pending = session.get(AdaptiveFollowThrough, prior.get('id')) if prior.get('id') else None
        if pending is None and prior.get('worksheet_id'):
            source = session.get(legacy.Worksheet, prior['worksheet_id'])
            if source and source.student_id == student_id:
                pending = _persist_follow_through(session, source, _detail(session, source, student_id))
        if pending and pending.student_id == student_id and not pending.consumed_at and pending.decision == prior.get('decision') and (pending.target_skill, pending.outcome_code) == (prior.get('target_skill'), prior.get('outcome_code')):
            source = session.get(legacy.Worksheet, pending.worksheet_id)
            session.add(FollowThroughOutcome(source_id=pending.id, worksheet_id=worksheet.id,
                                            before_evidence=json.dumps(v0450._session_evidence(source))))
            pending.consumed_at = datetime.utcnow()
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if questions:
        payload = v0450._payload(questions[0])
        metadata = payload.get('targeted_session_plan') or {}
        metadata['follow_through_context'] = {
            'previous_decision': (plan.get('previous_follow_through') or {}).get('decision'),
            'same_target': bool(prior and prior.get('target_skill') == (plan.get('primary_target') or {}).get('skill') and prior.get('outcome_code') == (plan.get('primary_target') or {}).get('outcome_code')),
            'source_follow_through_id': pending.id if pending else None,
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
        'message': (detail.get('intervention_outcome') or {}).get('message', v0450._student_safe(detail)['message']),
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
