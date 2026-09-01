from __future__ import annotations

import json
import random
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0200, v0290, v0300, v0301, v0310, v0321, v0360

app = v0360.app
app.version = '0.37.0'
legacy.APP_VERSION = '0.37.0'

_prior_create_worksheet = legacy.create_worksheet
_prior_make_question = legacy.make_question
_prior_mentor_payload = v0310.mentor_payload_v0310


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _fraction_bar_question(rng: random.Random):
    denominator = rng.choice([3, 4, 5, 6, 8, 10])
    numerator = rng.randint(1, denominator - 1)
    payload = {
        'visual': {
            'type': 'fraction_bar_select',
            'interactive': True,
            'denominator': denominator,
            'label': 'One whole split into equal parts',
        },
        'fraction_selection': {'denominator': denominator, 'max_selected': denominator},
    }
    return legacy.q(
        'VC2M4N03',
        'fraction_bar_selection',
        f'Shade {numerator}/{denominator} of the fraction bar.',
        'fraction_bar',
        payload,
        numerator,
        f'The whole is split into {denominator} equal parts. Shade {numerator} equal parts to represent the fraction.',
    )


def _fraction_number_line_question(rng: random.Random):
    denominator = rng.choice([4, 5, 6, 8, 10])
    numerator = rng.randint(1, denominator - 1)
    payload = {
        'visual': {
            'type': 'fraction_number_line_select',
            'interactive': True,
            'denominator': denominator,
            'label_indices': [0, denominator],
        },
        'fraction_number_line_selection': {'denominator': denominator},
    }
    return legacy.q(
        'VC2M4N04',
        'fraction_number_line_location',
        f'Select {numerator}/{denominator} on the number line.',
        'fraction_number_line',
        payload,
        numerator,
        f'Divide the distance from 0 to 1 into {denominator} equal intervals, then count {numerator} intervals from 0.',
    )


def _ruler_question(rng: random.Random):
    interval = rng.choice([1, 2, 5])
    steps = rng.choice([6, 8, 10])
    target_index = rng.randint(1, steps - 1)
    target = target_index * interval
    label_indices = sorted({0, steps, rng.choice([i for i in range(1, steps) if i != target_index])})
    payload = {
        'visual': {
            'type': 'ruler_select',
            'interactive': True,
            'unit': 'cm',
            'interval': interval,
            'steps': steps,
            'label_indices': label_indices,
        },
        'measurement_selection': {'unit': 'cm', 'interval': interval, 'steps': steps},
    }
    return legacy.q(
        'VC2M4M01',
        'scaled_ruler_reading',
        f'Select {target} cm on the ruler.',
        'ruler',
        payload,
        target,
        f'Each ruler mark increases by {interval} cm. Use the labelled marks to identify the scale before counting to the target.',
    )


def _grid_selection_question(rng: random.Random):
    columns = ['A', 'B', 'C', 'D', 'E']
    rows = 5
    column = rng.choice(columns)
    row = rng.randint(1, rows)
    reference = f'{column}{row}'
    payload = {
        'visual': {
            'type': 'grid_select',
            'interactive': True,
            'columns': columns,
            'rows': rows,
        },
        'grid_selection': {'columns': columns, 'rows': rows},
    }
    return legacy.q(
        'VC2M4SP03',
        'grid_reference_selection',
        f'Select square {reference} on the grid.',
        'grid_select',
        payload,
        reference,
        'Read the column label first, then the row number. Find where those two labels meet.',
    )


def _reasoning_question(topic: str, rng: random.Random):
    if topic in ('number', 'algebra'):
        mode = rng.choice(['operation', 'reasonableness', 'error'])
        if mode == 'operation':
            groups = rng.randint(4, 9)
            each = rng.randint(6, 14)
            prompt = f'There are {groups} equal groups with {each} items in each group. Which operation would find the total?'
            return legacy.q('VC2M4N09', 'operation_selection', prompt, 'choice', {'choices': ['addition', 'subtraction', 'multiplication', 'division'], 'reasoning_type': 'operation_selection'}, 'multiplication', 'Equal groups of the same size can be represented with multiplication.')
        if mode == 'reasonableness':
            a = rng.randint(280, 780)
            b = rng.randint(120, 390)
            estimate = round(a, -2) + round(b, -2)
            choices = sorted({estimate, max(0, estimate - 300), estimate + 300, estimate + 100})
            while len(choices) < 4:
                choices.append(max(0, estimate + 200 * len(choices)))
            rng.shuffle(choices)
            return legacy.q('VC2M4N07', 'reasonableness_reasoning', f'Which estimate is most reasonable for {a} + {b}?', 'choice', {'choices':[str(x) for x in choices[:4]], 'reasoning_type': 'reasonableness'}, estimate, f'Round each addend to a nearby hundred, then add the rounded values. This gives an estimate near {estimate}.')
        a = rng.randint(220, 480)
        b = rng.randint(120, min(280, a - 20))
        correct = a + b
        wrong = correct - 100
        choices = ['A hundred was not regrouped correctly.', 'The addition sign should have been subtraction.', 'The numbers must always be rounded first.', 'The ones digits should be multiplied.']
        return legacy.q('VC2M4N06', 'error_analysis_regrouping', f'A student says {a} + {b} = {wrong}. Which explanation best describes the mistake?', 'choice', {'choices': choices, 'reasoning_type': 'error_analysis', 'misconception_type': 'place_value_regrouping'}, choices[0], 'When the ones or tens make a new group of ten or one hundred, that regrouped value must be carried into the next place.')
    if topic == 'measurement':
        l, w = rng.randint(5, 12), rng.randint(3, 8)
        return legacy.q('VC2M4M02', 'perimeter_area_reasoning', f'A rectangle is {l} cm long and {w} cm wide. Which statement is true?', 'choice', {'choices':['Perimeter measures the distance around the outside.','Area is measured in centimetres, not square centimetres.','Perimeter is found by multiplying only length × width.','Area counts only the four outside edges.'], 'reasoning_type':'statement_reasoning'}, 'Perimeter measures the distance around the outside.', 'Perimeter is the distance around the boundary. Area measures the space inside and uses square units.')
    if topic == 'space':
        return legacy.q('VC2M4SP04', 'symmetry_reasoning', 'Which statement about a line of symmetry is true?', 'choice', {'choices':['It divides a shape into matching mirror halves.','Every shape has exactly two lines of symmetry.','It must always be horizontal.','It changes the size of the shape.'], 'reasoning_type':'statement_reasoning'}, 'It divides a shape into matching mirror halves.', 'A line of symmetry splits a figure so one side mirrors the other.')
    return _prior_make_question(topic, 4, rng)


def make_question_v0370(topic: str, level: int, rng: random.Random):
    if level >= 3:
        roll = rng.random()
        if topic == 'number' and roll < 0.08:
            return _fraction_bar_question(rng)
        if topic == 'number' and roll < 0.14:
            return _fraction_number_line_question(rng)
        if topic == 'measurement' and roll < 0.16:
            return _ruler_question(rng)
        if topic == 'space' and roll < 0.16:
            return _grid_selection_question(rng)
        if topic in ('number', 'algebra', 'measurement', 'space') and roll < 0.30:
            return _reasoning_question(topic, rng)
    return _prior_make_question(topic, level, rng)


def _reasoning_family(question: legacy.Question) -> bool:
    payload = _payload(question)
    return bool(payload.get('reasoning_type')) or any(token in (question.skill or '') for token in ('error_analysis', 'reasonableness_reasoning', 'operation_selection', 'reasoning'))


def apply_v0370_mix(session: Session, worksheet: legacy.Worksheet, student_id: int) -> legacy.Worksheet:
    if worksheet.session_kind == 'parent_test':
        return worksheet
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if not questions:
        return worksheet
    rng = random.Random(f'v0370:{worksheet.id}:mix')
    existing_reasoning = sum(1 for question in questions if _reasoning_family(question))
    desired = 1 if len(questions) >= 5 else 0
    if existing_reasoning < desired:
        candidates = [q for q in questions if q.topic in ('number', 'algebra', 'measurement', 'space') and not v0360._purposeful_foundation(q)]
        if candidates:
            question = rng.choice(candidates)
            skill, prompt, answer_type, payload, answer, working = _reasoning_question(question.topic, rng)
            question.skill = skill
            question.prompt = prompt
            question.answer_type = answer_type
            question.payload = json.dumps(payload)
            question.correct_answer = str(answer)
            question.working = working
            v0321._restore_runtime_annotations(question, worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0370(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return apply_v0370_mix(session, worksheet, student_id)


def mentor_payload_v0370(question: legacy.Question, action: str) -> dict[str, Any]:
    result = _prior_mentor_payload(question, action)
    skill = (question.skill or '').split(':', 1)[-1]
    if skill == 'fraction_bar_selection':
        result['visual_connection'] = 'Treat the bar as one whole. Check how many equal parts it has before deciding how many parts should be selected.'
    elif skill == 'fraction_number_line_location':
        result['visual_connection'] = 'Use 0 and 1 as landmarks. The denominator tells you how many equal intervals make one whole.'
    elif skill == 'scaled_ruler_reading':
        result['visual_connection'] = 'Read two labelled ruler marks first and work out how much each interval represents before selecting a mark.'
    elif skill == 'grid_reference_selection':
        result['visual_connection'] = 'Read the column first and the row second, then select the square where they meet.'
    elif _reasoning_family(question):
        result['visual_connection'] = 'Use the mathematical relationship shown in the question to justify the choice rather than guessing from the answer options.'
    return result


legacy.make_question = make_question_v0370
legacy.create_worksheet = create_worksheet_v0370
v0310.mentor_payload_v0310 = mentor_payload_v0370


@app.get('/api/v0370/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.37.0',
        'release_name': 'Richer Interactive Mathematics and Mathematical Reasoning',
        'interactive_fraction_bar': True,
        'interactive_fraction_number_line': True,
        'interactive_scaled_ruler': True,
        'interactive_grid_reference': True,
        'structured_reasoning_questions': True,
        'error_analysis_questions': True,
        'backend_authoritative_answers': True,
        'parent_test_isolation': True,
        'story_adventure_shared_learning_path': True,
        'inherits_v0360': True,
    }


v0120._move_spa_fallback_to_end()
