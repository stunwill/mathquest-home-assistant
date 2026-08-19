from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0260, v0290

app = v0290.app
app.version = '0.29.1'
legacy.APP_VERSION = '0.29.1'

_prior_create_worksheet = legacy.create_worksheet


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _skill_name(skill: str) -> str:
    return (skill or '').split(':', 1)[-1].strip().lower()


def _question_concept(skill: str, prompt: str, answer: str) -> tuple[str, tuple[str, ...], str]:
    numbers = tuple(re.findall(r'\d+(?:\.\d+)?(?:/\d+)?', prompt or ''))
    return (_skill_name(skill), numbers, legacy.normalise(answer))


def question_concept(question: legacy.Question) -> tuple[str, tuple[str, ...], str]:
    return _question_concept(question.skill, question.prompt, question.correct_answer)


def ensure_grid_visual(question: legacy.Question) -> None:
    if _skill_name(question.skill) != 'grid_references':
        return
    match = re.search(r'column\s+([A-Z]),\s*row\s+(\d+)', question.prompt or '', flags=re.IGNORECASE)
    if not match:
        return
    column = match.group(1).upper()
    row = max(1, int(match.group(2)))
    column_index = max(0, ord(column) - ord('A'))
    column_count = max(5, column_index + 1)
    row_count = max(6, row)
    payload = _payload(question)
    payload['visual'] = {
        'type': 'grid',
        'columns': [chr(ord('A') + index) for index in range(column_count)],
        'rows': row_count,
        'target': f'{column}{row}',
    }
    question.payload = json.dumps(payload)


def clarify_grouped_units(question: legacy.Question) -> None:
    prompt = question.prompt or ''
    grouped_meals = re.search(
        r'There are (\d+) packs with (\d+) meal portions in each\. After (\d+) are used for hikers, how many remain\?',
        prompt,
        flags=re.IGNORECASE,
    )
    if grouped_meals:
        packs, portions, used = grouped_meals.groups()
        question.prompt = (
            f'There are {packs} packs with {portions} meal portions in each. '
            f'After {used} meal portions are used for hikers, how many meal portions remain?'
        )
        return

    # Guard against the same ambiguity appearing with a slightly different story wrapper.
    if 'meal portions in each' in prompt.lower():
        question.prompt = re.sub(
            r'After (\d+) are used\b',
            r'After \1 meal portions are used',
            prompt,
            flags=re.IGNORECASE,
        )
        question.prompt = re.sub(
            r'how many remain\?',
            'how many meal portions remain?',
            question.prompt,
            flags=re.IGNORECASE,
        )


def _replace_question(
    question: legacy.Question,
    worksheet: legacy.Worksheet,
    seen: set[tuple[str, tuple[str, ...], str]],
    rng: random.Random,
) -> bool:
    previous_payload = _payload(question)
    preserved = {key: previous_payload[key] for key in ('adventure', 'story', 'mission') if key in previous_payload}

    for _ in range(120):
        skill, prompt, answer_type, payload, answer, working = legacy.make_question(
            question.topic,
            min(4, max(1, question.level)),
            rng,
        )
        concept = _question_concept(skill, prompt, str(answer))
        if concept in seen:
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
        ensure_grid_visual(question)
        clarify_grouped_units(question)
        return True
    return False


def repair_worksheet_questions(session: Session, worksheet: legacy.Worksheet) -> legacy.Worksheet:
    """Final quality pass after all adaptive, story and difficulty transformations."""
    seen: set[tuple[str, tuple[str, ...], str]] = set()
    rng = random.Random(f'v0291:{worksheet.id}:quality')

    for question in sorted(worksheet.questions, key=lambda item: item.position):
        ensure_grid_visual(question)
        clarify_grouped_units(question)
        concept = question_concept(question)
        if concept in seen:
            _replace_question(question, worksheet, seen, rng)
            concept = question_concept(question)
        seen.add(concept)

    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0291(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return repair_worksheet_questions(session, worksheet)


@app.get('/api/v0291/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.29.1',
        'grid_reference_visual_guard': True,
        'question_autofocus': True,
        'semantic_duplicate_guard': True,
        'explicit_grouped_units': True,
        'inherits_v0290': True,
    }


legacy.create_worksheet = create_worksheet_v0291
v0120._move_spa_fallback_to_end()
