from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0200, v0290, v0301, v0310, v0320

app = v0320.app
app.version = '0.32.1'
legacy.APP_VERSION = '0.32.1'

_prior_create_worksheet = legacy.create_worksheet


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _numbers(prompt: str) -> list[int]:
    return [int(value) for value in re.findall(r'\d+', prompt or '')]


def _question_attempts(session: Session, student_id: int, limit: int = 30) -> list[legacy.Attempt]:
    return list(session.scalars(
        select(legacy.Attempt)
        .where(legacy.Attempt.student_id == student_id)
        .order_by(legacy.Attempt.id.desc())
        .limit(limit)
    ).all())


def learner_readiness(session: Session, student_id: int) -> dict[str, Any]:
    rows = _question_attempts(session, student_id)
    if len(rows) < 6:
        return {'ready': False, 'confidence': 'limited', 'independent_accuracy': None}
    recent = rows[:12]
    accuracy = sum(1 for row in recent if row.correct) / len(recent)
    return {
        'ready': accuracy >= 0.75,
        'confidence': 'strong' if len(rows) >= 18 else 'moderate',
        'independent_accuracy': round(accuracy * 100),
    }


def _is_trivial_arithmetic(question: legacy.Question) -> bool:
    values = _numbers(question.prompt)
    operation = v0310._operation(question)
    return bool(operation in ('addition', 'subtraction', 'multiplication', 'division') and len(values) >= 2 and max(values[:2]) <= 12)


def _difficulty_band(question: legacy.Question) -> str:
    payload = _payload(question)
    if payload.get('instructional_band') == 'hundreds':
        return 'challenge'
    values = _numbers(question.prompt)
    if _is_trivial_arithmetic(question):
        return 'retrieval'
    if values and max(values[:2] or values) >= 100:
        return 'challenge'
    return 'instructional'


def _replace_question(question: legacy.Question, worksheet: legacy.Worksheet, rng: random.Random, blocked_families: set[str]) -> bool:
    original_payload = _payload(question)
    preserved = {key: original_payload[key] for key in ('adventure', 'story', 'mission') if key in original_payload}
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
        if v0301.question_family(candidate) in blocked_families:
            continue
        if _is_trivial_arithmetic(candidate):
            continue
        next_payload = dict(payload if isinstance(payload, dict) else {})
        next_payload.update(preserved)
        question.skill = skill
        question.prompt = prompt
        question.answer_type = answer_type
        question.payload = json.dumps(next_payload)
        question.correct_answer = str(answer)
        question.working = working
        return True
    return False


def enforce_learning_quality(session: Session, worksheet: legacy.Worksheet, student_id: int) -> legacy.Worksheet:
    readiness = learner_readiness(session, student_id)
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    rng = random.Random(f'v0321:{worksheet.id}:quality')

    retrieval_budget = 1 if readiness['ready'] and len(questions) >= 5 else max(1, len(questions) // 3)
    retrieval_seen = 0
    seen_families: set[str] = set()

    for question in questions:
        family = v0301.question_family(question)
        needs_replacement = family in seen_families
        if _is_trivial_arithmetic(question):
            retrieval_seen += 1
            needs_replacement = needs_replacement or retrieval_seen > retrieval_budget
        if needs_replacement:
            if _replace_question(question, worksheet, rng, seen_families):
                family = v0301.question_family(question)
        seen_families.add(family)

        payload = _payload(question)
        payload['difficulty_band'] = _difficulty_band(question)
        payload['retrieval_item'] = payload['difficulty_band'] == 'retrieval'
        payload['mentor_context'] = v0310._question_context(question)
        question.payload = json.dumps(payload)

    v0301.repair_fraction_number_lines(worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def aligned_worked_example(question: legacy.Question) -> str:
    prompt = question.prompt or ''
    skill = (question.skill or '').split(':', 1)[-1].lower()
    family = v0200.question_family(question)
    nums = _numbers(prompt)

    if question.topic == 'probability':
        if 'coin' in prompt.lower() or 'toss' in prompt.lower():
            return 'For a different experiment, suppose a coin is tossed 40 times and lands heads 23 times. Compare the observed heads fraction with one half, then decide whether a small variation from an even split is reasonable.'
        return 'For a different chance problem, list the equally likely outcomes first, count the favourable outcomes, then write favourable outcomes over total outcomes before simplifying.'

    if 'fraction_number_line' in skill or ('/' in prompt and 'number line' in prompt.lower()):
        return 'For a different example, place 5/8 on a 0-to-1 number line by dividing the whole interval into 8 equal parts and counting 5 equal steps from 0.'

    if 'equivalent_fractions' in skill:
        return 'For a different example, show that 3/4 and 6/8 are equivalent by multiplying both the numerator and denominator of 3/4 by 2, then compare the two equal-whole models.'

    if question.topic == 'measurement':
        text = prompt.lower()
        if 'perimeter' in text:
            return 'For a different rectangle measuring 9 cm by 4 cm, add all four side lengths: 9 + 4 + 9 + 4. This finds the distance around the outside.'
        if 'area' in text:
            return 'For a different rectangle measuring 7 cm by 5 cm, multiply length by width: 7 × 5. This counts the square units covering the inside.'
        if 'convert' in text or any(unit in text for unit in (' mm', ' cm', ' m', ' km')):
            return 'For a different length conversion, convert 2.4 m to centimetres by using 1 m = 100 cm, so multiply the metre value by 100.'

    if question.topic == 'space' and ('grid' in prompt.lower() or 'reference' in prompt.lower()):
        return 'For a different grid-reference example, read across the horizontal labels first, then up the vertical labels, and combine those two labels for the selected square.'

    if question.topic == 'statistics':
        return 'For a different data question, identify exactly what the graph or table measures, read the scale carefully, then use only the relevant values to calculate the requested comparison.'

    example = v0290.aligned_worked_example(question)
    current_answer = str(question.correct_answer).strip().lower()
    if current_answer and current_answer in example.strip().lower():
        return 'Use the same operation and strategy on a different set of values, complete each step in order, and check the result against the wording of the example.'
    return example


_original_mentor_payload = v0310.mentor_payload_v0310


def mentor_payload_v0321(question: legacy.Question, action: str) -> dict[str, Any]:
    result = _original_mentor_payload(question, action)
    if action == 'worked_example':
        result['worked_example'] = aligned_worked_example(question)
        result['example_is_aligned'] = True
        result['example_alignment'] = {
            'topic': question.topic,
            'skill': (question.skill or '').split(':', 1)[-1],
            'question_family': v0301.question_family(question),
        }
    return result


def create_worksheet_v0321(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return enforce_learning_quality(session, worksheet, student_id)


v0310.mentor_payload_v0310 = mentor_payload_v0321
legacy.create_worksheet = create_worksheet_v0321


@app.get('/api/v0321/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.32.1',
        'optional_retry_preserved': True,
        'worked_example_family_alignment': True,
        'evidence_driven_retrieval_budget': True,
        'post_transform_family_diversity': True,
        'difficulty_band_metadata': True,
        'inherits_v0320': True,
    }


v0120._move_spa_fallback_to_end()
