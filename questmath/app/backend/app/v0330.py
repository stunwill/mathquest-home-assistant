from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0290, v0301, v0310, v0320, v0321, v0323

app = v0323.app
app.version = '0.33.0'
legacy.APP_VERSION = '0.33.0'

_prior_create_worksheet = legacy.create_worksheet


@dataclass(frozen=True)
class AdaptiveThresholds:
    minimum_questions: int = 6
    ready_accuracy: float = 0.82
    ready_support: float = 0.25
    consolidate_accuracy: float = 0.60
    high_support: float = 0.55
    prerequisite_misconceptions: int = 2


THRESHOLDS = AdaptiveThresholds()
PURPOSE_LABELS = {
    'current': 'Practising this skill',
    'consolidation': 'Building confidence',
    'review': 'Quick review',
    'challenge': "Today's challenge",
}


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _normalise_skill(skill: str) -> str:
    return (skill or '').split(':', 1)[-1]


def _question_evidence(session: Session, student_id: int, skill: str) -> dict[str, Any]:
    questions = list(session.scalars(
        select(legacy.Question)
        .join(legacy.Worksheet)
        .where(
            legacy.Worksheet.student_id == student_id,
            legacy.Worksheet.session_kind != 'parent_test',
            legacy.Question.skill == skill,
            legacy.Question.answered_at.is_not(None),
        )
        .order_by(legacy.Question.answered_at.desc(), legacy.Question.id.desc())
        .limit(20)
    ).all())
    if not questions:
        return {'questions': 0, 'independent': 0.0, 'eventual': 0.0, 'support': 0.0, 'recent_failures': 0}
    independent = eventual = supported = recent_failures = 0
    for question in questions:
        attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
        first = attempts[0] if attempts else None
        final_correct = any(attempt.correct for attempt in attempts)
        help_used = bool((question.hint_count or 0) or question.mentor_started or question.mentor_example_seen)
        eventual += int(final_correct)
        independent += int(bool(first and first.correct and not help_used))
        supported += int(help_used)
        recent_failures += int(not final_correct)
    total = len(questions)
    return {
        'questions': total,
        'independent': independent / total,
        'eventual': eventual / total,
        'support': supported / total,
        'recent_failures': recent_failures,
    }


def _misconception_count(session: Session, student_id: int, skill: str) -> int:
    return len(list(session.scalars(select(v0290.MisconceptionEvidence).where(
        v0290.MisconceptionEvidence.student_id == student_id,
        v0290.MisconceptionEvidence.skill == skill,
        v0290.MisconceptionEvidence.resolved == False,
    )).all()))


def _progression_state(evidence: dict[str, Any]) -> str:
    count = evidence['questions']
    independent = evidence['independent']
    support = evidence['support']
    eventual = evidence['eventual']
    if count < THRESHOLDS.minimum_questions:
        return 'not_ready'
    if independent >= THRESHOLDS.ready_accuracy and support <= THRESHOLDS.ready_support:
        return 'ready_to_progress'
    if independent >= 0.75 and support <= 0.35:
        return 'secure'
    if eventual >= 0.72 and independent >= THRESHOLDS.consolidate_accuracy:
        return 'consolidating'
    return 'developing'


def _purpose_for_question(session: Session, student_id: int, question: legacy.Question, outcome_map: dict[str, dict[str, Any]]) -> tuple[str, str]:
    payload = _payload(question)
    skill = question.skill
    evidence = _question_evidence(session, student_id, skill)
    state = _progression_state(evidence)
    outcome_code = (question.skill or '').split(':', 1)[0]
    outcome = outcome_map.get(outcome_code)
    if outcome and outcome.get('review_due'):
        return 'review', 'This skill is due for spaced retrieval.'
    if _misconception_count(session, student_id, skill) >= THRESHOLDS.prerequisite_misconceptions:
        return 'consolidation', 'Recent misconception evidence calls for targeted consolidation.'
    if state == 'ready_to_progress' and payload.get('difficulty_band') == 'challenge':
        return 'challenge', 'Strong independent evidence supports a slightly harder question.'
    if evidence['support'] >= THRESHOLDS.high_support or state in ('developing', 'consolidating'):
        return 'consolidation', 'Recent success still uses support, so MathQuest is reinforcing the skill before progressing.'
    if payload.get('difficulty_band') == 'retrieval':
        return 'review', 'This is deliberate retrieval practice rather than the main instructional level.'
    return 'current', 'This matches the current instructional level.'


def _replace_for_purpose(question: legacy.Question, worksheet: legacy.Worksheet, rng: random.Random, blocked_families: set[str], require_nontrivial: bool = True) -> bool:
    for _ in range(180):
        skill, prompt, answer_type, payload, answer, working = legacy.make_question(question.topic, min(4, max(2, question.level)), rng)
        candidate = legacy.Question(
            worksheet_id=worksheet.id,
            topic=question.topic,
            skill=skill,
            level=question.level,
            prompt=prompt,
            answer_type=answer_type,
            payload=json.dumps(payload if isinstance(payload, dict) else {}),
            correct_answer=str(answer),
            working=working,
            position=question.position,
        )
        family = v0301.question_family(candidate)
        if family in blocked_families:
            continue
        if require_nontrivial and v0321._is_trivial_arithmetic(candidate):
            continue
        question.skill = skill
        question.prompt = prompt
        question.answer_type = answer_type
        question.payload = json.dumps(payload if isinstance(payload, dict) else {})
        question.correct_answer = str(answer)
        question.working = working
        v0321._restore_runtime_annotations(question, worksheet)
        return True
    return False


def apply_adaptive_daily_learning(session: Session, worksheet: legacy.Worksheet, student_id: int) -> legacy.Worksheet:
    if worksheet.session_kind == 'parent_test':
        return worksheet
    outcomes = v0230.outcome_mastery(session, student_id)
    outcome_map = {item['code']: item for item in outcomes}
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    rng = random.Random(f'v0330:{worksheet.id}:adaptive-daily')
    seen_families: set[str] = set()
    challenge_budget = 1 if len(questions) >= 5 else 0
    challenge_seen = 0

    for question in questions:
        family = v0301.question_family(question)
        if family in seen_families:
            _replace_for_purpose(question, worksheet, rng, seen_families)
            family = v0301.question_family(question)
        seen_families.add(family)

        purpose, reason = _purpose_for_question(session, student_id, question, outcome_map)
        evidence = _question_evidence(session, student_id, question.skill)
        state = _progression_state(evidence)
        payload = _payload(question)
        if purpose == 'challenge':
            if challenge_seen >= challenge_budget:
                purpose = 'current'
                reason = 'Challenge is limited so the session stays balanced.'
            else:
                challenge_seen += 1
        if state == 'ready_to_progress' and purpose == 'current' and payload.get('difficulty_band') == 'instructional' and challenge_seen < challenge_budget:
            purpose = 'challenge'
            reason = 'Repeated independent success supports a small progression step.'
            challenge_seen += 1
        if evidence['support'] >= THRESHOLDS.high_support and purpose == 'challenge':
            purpose = 'consolidation'
            reason = 'Support use is still high, so MathQuest is consolidating before increasing difficulty.'

        payload = _payload(question)
        payload['learning_purpose'] = purpose
        payload['learning_purpose_label'] = PURPOSE_LABELS[purpose]
        payload['adaptive_reason'] = reason
        payload['progression_state'] = state
        payload['adaptive_evidence'] = {
            'questions': evidence['questions'],
            'independent_accuracy': round(evidence['independent'] * 100),
            'eventual_accuracy': round(evidence['eventual'] * 100),
            'support_dependency': round(evidence['support'] * 100),
        }
        question.payload = json.dumps(payload)

    v0301.repair_fraction_number_lines(worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0330(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return apply_adaptive_daily_learning(session, worksheet, student_id)


legacy.create_worksheet = create_worksheet_v0330


@app.get('/api/v0330/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.33.0',
        'adaptive_daily_learning': True,
        'learning_purposes': ['current', 'consolidation', 'review', 'challenge'],
        'controlled_progression': True,
        'support_aware_progression': True,
        'spaced_retrieval_integration': True,
        'parent_explainability_metadata': True,
        'inherits_v0323': True,
    }


v0120._move_spa_fallback_to_end()
