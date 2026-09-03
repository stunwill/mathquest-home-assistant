from __future__ import annotations

import json
import random
import re
from datetime import timezone
from zoneinfo import ZoneInfo

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0160, v0170, v0321, v0370

app = v0370.app
app.version = '0.38.1'
legacy.APP_VERSION = '0.38.1'

_prior_create_worksheet = legacy.create_worksheet
_prior_history_summary = v0160._history_summary
MELBOURNE = ZoneInfo('Australia/Melbourne')


def _payload(question: legacy.Question) -> dict:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _melbourne_time(value) -> str | None:
    if value is None:
        return None
    aware = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return aware.astimezone(MELBOURNE).strftime('%-I:%M %p')


def history_summary_v0381(ws: legacy.Worksheet) -> dict:
    summary = _prior_history_summary(ws)
    summary['display_time'] = _melbourne_time(ws.started_at)
    return summary


def _upgrade_direct_arithmetic(question: legacy.Question, rng: random.Random) -> bool:
    if question.topic not in ('number', 'algebra'):
        return False
    match = re.fullmatch(r'Calculate\s+(\d+)\s*([+−-])\s*(\d+)\.', (question.prompt or '').strip())
    if not match:
        return False
    left, operator, right = int(match.group(1)), match.group(2), int(match.group(3))

    # Keep direct calculation practice, but avoid the low-value two-digit / tiny-number
    # items that dominate too much of a Grade 5 Number & Algebra session.
    if operator == '+' and max(left, right) >= 200 and min(left, right) >= 25:
        return False
    if operator in ('−', '-') and left >= 200 and right >= 25:
        return False

    payload = _payload(question)
    if operator == '+':
        a = rng.randint(220, 899)
        b = rng.randint(35, 499)
        question.skill = 'VC2M4N06:written_addition'
        question.prompt = f'Calculate {a} + {b}.'
        question.correct_answer = str(a + b)
        question.working = f'Line up place values, add ones, tens and hundreds, and regroup where needed: {a} + {b} = {a+b}.'
        payload['operation'] = 'addition'
        payload['strategy_card'] = v0170._card(
            'Written addition',
            'Add by place value',
            'Line up the ones, tens and hundreds before calculating.',
            ['Add the ones.', 'Regroup if a column totals 10 or more.', 'Add the tens and hundreds.', 'Check with an estimate.'],
            'Example: 347 + 186. Add by place value and regroup when needed.',
            'addition',
        )
    else:
        a = rng.randint(260, 999)
        b = rng.randint(35, min(499, a - 40))
        question.skill = 'VC2M4N06:written_subtraction'
        question.prompt = f'Calculate {a} − {b}.'
        question.correct_answer = str(a - b)
        question.working = f'Line up place values and regroup where needed: {a} − {b} = {a-b}.'
        payload['operation'] = 'subtraction'
        payload['strategy_card'] = v0170._card(
            'Written subtraction',
            'Subtract by place value',
            'Line up the ones, tens and hundreds and regroup only when needed.',
            ['Start with the ones.', 'Regroup from the next place when required.', 'Subtract the tens and hundreds.', 'Check using addition.'],
            'Example: 582 − 147. Work from right to left and regroup when needed.',
            'subtraction',
        )
    payload['difficulty_band'] = 'instructional'
    payload['retrieval_item'] = False
    question.answer_type = 'number'
    question.payload = json.dumps(payload)
    return True


def _replace_operation_only_question(question: legacy.Question) -> bool:
    payload = _payload(question)
    if payload.get('reasoning_type') != 'operation_selection' and 'operation_selection' not in (question.skill or ''):
        return False
    values = [int(value) for value in re.findall(r'\d+', question.prompt or '')]
    if len(values) < 2:
        return False
    groups, each = values[0], values[1]
    total = groups * each
    question.skill = 'VC2M4N09:equal_groups_total'
    question.prompt = f'There are {groups} equal groups with {each} items in each group. How many items are there altogether?'
    question.answer_type = 'number'
    question.correct_answer = str(total)
    question.working = f'Equal groups use multiplication: {groups} × {each} = {total}.'
    payload.pop('choices', None)
    payload['reasoning_type'] = 'multiplicative_total'
    payload['operation'] = 'multiplication'
    question.payload = json.dumps(payload)
    return True


def improve_number_algebra_quality(session: Session, worksheet: legacy.Worksheet) -> legacy.Worksheet:
    if worksheet.session_kind == 'parent_test':
        return worksheet
    rng = random.Random(f'v0381:{worksheet.id}:number-algebra-quality')
    changed = False
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        question_changed = _replace_operation_only_question(question)
        question_changed = _upgrade_direct_arithmetic(question, rng) or question_changed
        if question_changed:
            v0321._restore_runtime_annotations(question, worksheet)
            changed = True
    if changed:
        session.commit()
        session.refresh(worksheet)
    return worksheet


def create_worksheet_v0381(session: Session, student_id: int, selected: str, **kwargs):
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return improve_number_algebra_quality(session, worksheet)


legacy.create_worksheet = create_worksheet_v0381
v0160._history_summary = history_summary_v0381


@app.get('/api/v0381/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.38.1',
        'larger_number_algebra_arithmetic': True,
        'numeric_equal_groups_questions': True,
        'history_timezone': 'Australia/Melbourne',
        'inherits_v0380': True,
    }


v0120._move_spa_fallback_to_end()
