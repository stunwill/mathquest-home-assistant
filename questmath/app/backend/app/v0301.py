from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0260, v0291, v0300

app = v0300.app
app.version = '0.30.1'
legacy.APP_VERSION = '0.30.1'

_prior_create_worksheet = legacy.create_worksheet
_prior_summary = legacy.summary
_prior_visual_model_for = v0300.visual_model_for
_prior_visual_reason = v0300.visual_reason
_prior_safe_visual_payload = v0300._safe_visual_payload


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
    return f'{question.topic}:{re.sub(r"\d+(?:\.\d+)?", "#", prompt)}'


def _fraction_number_line_visual(question: legacy.Question) -> dict[str, Any] | None:
    match = re.search(
        r'represents\s+(\d+)\s*/\s*(\d+)\s+on the number line',
        question.prompt or '',
        flags=re.IGNORECASE,
    )
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


def _replace_with_distinct_family(
    question: legacy.Question,
    worksheet: legacy.Worksheet,
    blocked_families: set[str],
    seen_concepts: set[tuple[str, tuple[str, ...], str]],
    rng: random.Random,
) -> bool:
    previous_payload = _payload(question)
    preserved = {key: previous_payload[key] for key in ('adventure', 'story', 'mission') if key in previous_payload}
    original_family = question_family(question)

    for _ in range(160):
        skill, prompt, answer_type, payload, answer, working = legacy.make_question(
            question.topic,
            min(4, max(1, question.level)),
            rng,
        )
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
        family = question_family(candidate)
        concept = v0291._question_concept(skill, prompt, str(answer))
        if concept in seen_concepts or family in blocked_families or family == original_family:
            continue
        next_payload = dict(payload if isinstance(payload, dict) else {})
        next_payload.update(preserved)
        question.skill = skill
        question.prompt = prompt
        question.answer_type = answer_type
        question.payload = json.dumps(next_payload)
        question.correct_answer = str(answer)
        question.working = working
        v0260._annotate_question(question, worksheet)
        v0291.ensure_grid_visual(question)
        v0291.clarify_grouped_units(question)
        return True
    return False


def enforce_question_family_diversity(session: Session, worksheet: legacy.Worksheet) -> legacy.Worksheet:
    seen_families: set[str] = set()
    seen_concepts: set[tuple[str, tuple[str, ...], str]] = set()
    previous_family: str | None = None
    rng = random.Random(f'v0301:{worksheet.id}:families')

    for question in sorted(worksheet.questions, key=lambda item: item.position):
        family = question_family(question)
        concept = v0291.question_concept(question)
        if family in seen_families or family == previous_family or concept in seen_concepts:
            blocked = set(seen_families)
            if previous_family:
                blocked.add(previous_family)
            if _replace_with_distinct_family(question, worksheet, blocked, seen_concepts, rng):
                family = question_family(question)
                concept = v0291.question_concept(question)
        seen_families.add(family)
        seen_concepts.add(concept)
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
    assessed_strands = {item['strand'] for item in assessed}
    if len(assessed_strands) < 2:
        return 'Keep exploring', 'More practice needed'

    strongest = max(
        assessed,
        key=lambda item: (item['mastery'], item['independent_accuracy'] or 0, item['questions'], item['code']),
    )
    recommendation = v0230.next_session_recommendation(session, student_id, outcomes)
    if recommendation.get('mode') == 'diagnostic':
        practise_next = 'More practice needed'
    else:
        practise_topic = recommendation.get('topic')
        practise_next = str(practise_topic).replace('_', ' ').title() if practise_topic else 'More practice needed'
    return strongest['strand'], practise_next


def summary_v0301(session: Session, worksheet: legacy.Worksheet, user: legacy.User) -> dict[str, Any]:
    result = _prior_summary(session, worksheet, user)
    if getattr(worksheet, 'session_kind', 'practice') == 'parent_test':
        return result
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    strongest, practise_next = learner_summary_recommendations(session, student_id)
    result['strongest_topic'] = strongest
    result['weakest_topic'] = practise_next
    return result


def visual_model_for(question: legacy.Question) -> str:
    if question.topic == 'probability':
        return 'probability'
    return _prior_visual_model_for(question)


def visual_reason(model: str) -> str:
    if model == 'probability':
        return 'A frequency comparison shows how experimental results can vary from an expected even split.'
    return _prior_visual_reason(model)


def safe_visual_payload(question: legacy.Question, worksheet: legacy.Worksheet | None) -> dict[str, Any]:
    if question.topic != 'probability':
        return _prior_safe_visual_payload(question, worksheet)
    assessment = bool(worksheet and worksheet.session_kind == 'parent_test')
    return {
        'recommended_model': 'probability',
        'visual_reason': visual_reason('probability'),
        'teaching_visual_available': False,
        'assessment_restricted': assessment,
    }


v0300.visual_model_for = visual_model_for
v0300.visual_reason = visual_reason
v0300._safe_visual_payload = safe_visual_payload
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
