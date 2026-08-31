from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0301, v0321, v0330, v0351

app = v0351.app
app.version = '0.36.0'
legacy.APP_VERSION = '0.36.0'

_prior_create_worksheet = legacy.create_worksheet
_prior_make_question = legacy.make_question


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _skill(question: legacy.Question) -> str:
    return (question.skill or '').split(':', 1)[-1].lower()


def _simple_two_digit_addition(question: legacy.Question) -> bool:
    if question.topic != 'number':
        return False
    if _skill(question) not in {'written_addition', 'fact_recall_addition', 'efficient_add_subtract'}:
        return False
    match = re.fullmatch(r'Calculate\s+(\d+)\s*\+\s*(\d+)\.', (question.prompt or '').strip())
    if not match:
        return False
    a, b = map(int, match.groups())
    return 10 <= a <= 99 and 10 <= b <= 99 and a + b < 100


def _purposeful_foundation(question: legacy.Question) -> bool:
    payload = _payload(question)
    return payload.get('learning_purpose') in {'review', 'consolidation'} or bool(payload.get('retrieval_item'))


def _replace_with_richer_question(question: legacy.Question, worksheet: legacy.Worksheet, rng: random.Random, blocked: set[str]) -> bool:
    for _ in range(220):
        skill, prompt, answer_type, payload, answer, working = _prior_make_question(question.topic, max(3, min(4, question.level)), rng)
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
        if family in blocked or v0321._is_trivial_arithmetic(candidate) or _simple_two_digit_addition(candidate):
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


def _number_line_question(rng: random.Random):
    interval = rng.choice([2, 5, 10])
    start = rng.choice([0, 10, 20, 30, 40])
    steps = rng.choice([5, 6, 8])
    target_index = rng.randint(1, steps - 1)
    target = start + target_index * interval
    end = start + steps * interval
    labels = sorted({0, steps, rng.randint(1, steps - 1)})
    payload = {
        'visual': {
            'type': 'number_line',
            'interactive': True,
            'min': start,
            'max': end,
            'interval': interval,
            'steps': steps,
            'label_indices': labels,
            'tick_labels': 'selected',
        },
        'number_line_selection': {
            'min': start,
            'max': end,
            'interval': interval,
            'steps': steps,
        },
    }
    return legacy.q(
        'VC2M5N02',
        'number_line_location',
        f'Select {target} on the number line.',
        'number_line',
        payload,
        target,
        f'Each interval increases by {interval}. Count from a labelled value until you reach {target}.',
    )


def make_question_v0360(topic: str, level: int, rng: random.Random):
    if topic == 'number' and level >= 3 and rng.random() < 0.14:
        return _number_line_question(rng)
    return _prior_make_question(topic, level, rng)


def apply_v0360_quality(session: Session, worksheet: legacy.Worksheet, student_id: int) -> legacy.Worksheet:
    if worksheet.session_kind == 'parent_test':
        return worksheet
    readiness = v0321.learner_readiness(session, student_id)
    rng = random.Random(f'v0360:{worksheet.id}:quality')
    seen: set[str] = set()
    simple_budget = 1 if not readiness['ready'] else 0
    simple_seen = 0

    for question in sorted(worksheet.questions, key=lambda item: item.position):
        family = v0301.question_family(question)
        payload = _payload(question)
        is_simple = _simple_two_digit_addition(question)
        purposeful = _purposeful_foundation(question)
        if is_simple:
            simple_seen += 1
            if readiness['ready'] and not purposeful:
                if _replace_with_richer_question(question, worksheet, rng, seen):
                    family = v0301.question_family(question)
            elif simple_seen > simple_budget and not purposeful:
                if _replace_with_richer_question(question, worksheet, rng, seen):
                    family = v0301.question_family(question)
        seen.add(family)
        payload = _payload(question)
        payload['v0360_quality'] = {
            'simple_two_digit_addition': _simple_two_digit_addition(question),
            'purposeful_foundation': _purposeful_foundation(question),
            'learner_ready': bool(readiness['ready']),
        }
        question.payload = json.dumps(payload)

    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0360(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return apply_v0360_quality(session, worksheet, student_id)


legacy.make_question = make_question_v0360
legacy.create_worksheet = create_worksheet_v0360


@app.get('/api/v0360/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.36.0',
        'interactive_number_line_answers': True,
        'evidence_aware_simple_arithmetic_suppression': True,
        'purposeful_foundation_preserved': True,
        'session_recovery_frontend': True,
        'inherits_v0351': True,
    }


v0120._move_spa_fallback_to_end()
