from __future__ import annotations

import json
import re
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0291, v0300

app = v0300.app
app.version = '0.30.1'
legacy.APP_VERSION = '0.30.1'

_prior_create_worksheet = legacy.create_worksheet
_prior_summary = legacy.summary


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def question_family(question: legacy.Question) -> str:
    skill = (question.skill or '').split(':', 1)[-1].strip().lower()
    prompt = (question.prompt or '').lower()
    if question.topic == 'probability' and 'coin was tossed' in prompt and 'variation from exactly 50 each normal' in prompt:
        return 'probability:coin_toss_variation'
    if skill:
        return f'{question.topic}:{skill}'
    return f'{question.topic}:{re.sub(r"\\d+(?:\\.\\d+)?", "#", prompt)}'


def _fraction_number_line_visual(question: legacy.Question) -> dict[str, Any] | None:
    prompt = question.prompt or ''
    match = re.search(r'represents\s+(\d+)\s*/\s*(\d+)\s+on the number line', prompt, flags=re.IGNORECASE)
    if not match:
        return None
    numerator = int(match.group(1))
    denominator = max(1, int(match.group(2)))
    numerator = max(0, min(denominator, numerator))
    return {
        'type': 'number_line',
        'min': 0,
        'max': 1,
        'marker': numerator / denominator,
        'steps': denominator,
        'fraction': {'numerator': numerator, 'denominator': denominator},
        'tick_labels': 'endpoints_only',
    }


def repair_fraction_number_lines(worksheet: legacy.Worksheet) -> None:
    for question in worksheet.questions:
        visual = _fraction_number_line_visual(question)
        if not visual:
            continue
        payload = _payload(question)
        payload['visual'] = visual
        payload['visual_key'] = f'{question.id}:fraction-number-line:{visual["steps"]}'
        question.payload = json.dumps(payload)


def enforce_question_family_diversity(session: Session, worksheet: legacy.Worksheet) -> legacy.Worksheet:
    seen_families: set[str] = set()
    previous_family: str | None = None
    ordered = sorted(worksheet.questions, key=lambda item: item.position)

    for question in ordered:
        family = question_family(question)
        if family in seen_families or family == previous_family:
            replaced = v0291._replace_question(
                question,
                worksheet,
                {v0291.question_concept(item) for item in ordered if item.id != question.id},
                __import__('random').Random(f'v0301:{worksheet.id}:{question.position}'),
            )
            if replaced:
                family = question_family(question)
        seen_families.add(family)
        previous_family = family

    repair_fraction_number_lines(worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0301(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    worksheet = enforce_question_family_diversity(session, worksheet)
    return v0300.annotate_visual_mathematics(session, worksheet)


def learner_summary_recommendations(session: Session, student_id: int) -> tuple[str, str]:
    outcomes = v0230.outcome_mastery(session, student_id)
    assessed = [item for item in outcomes if item['questions'] >= 3]
    if not assessed:
        return 'Keep exploring', 'More practice needed'

    strongest = max(
        assessed,
        key=lambda item: (item['mastery'], item['independent_accuracy'] or 0, item['questions'], item['code']),
    )
    recommendation = v0230.next_session_recommendation(session, student_id, outcomes)
    practise_topic = recommendation.get('topic')
    practise_next = practise_topic.title() if practise_topic else 'More practice needed'
    return strongest['strand'], practise_next


def summary_v0301(session: Session, worksheet: legacy.Worksheet, user: legacy.User) -> dict[str, Any]:
    result = _prior_summary(session, worksheet, user)
    if getattr(worksheet, 'session_kind', 'practice') == 'parent_test':
        return result
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    strongest, practise_next = learner_summary_recommendations(session, student_id)
    result['strongest'] = strongest
    result['weakest'] = practise_next
    result['practise_next'] = practise_next
    return result


def visual_model_for(question: legacy.Question) -> str:
    if question.topic == 'probability':
        return 'probability'
    return v0300.visual_model_for(question)


def visual_reason(model: str) -> str:
    if model == 'probability':
        return 'A frequency comparison shows how experimental results can vary from an expected even split.'
    return v0300.visual_reason(model)


v0300.visual_model_for = visual_model_for
v0300.visual_reason = visual_reason
legacy.create_worksheet = create_worksheet_v0301
legacy.summary = summary_v0301


@app.get('/api/v0301/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.30.1',
        'learner_history_completion_summary': True,
        'question_family_diversity': True,
        'fraction_number_line_denominator_ticks': True,
        'probability_visual_relevance_guard': True,
        'inherits_v0300': True,
    }


v0120._move_spa_fallback_to_end()
