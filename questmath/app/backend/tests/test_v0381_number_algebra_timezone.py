from __future__ import annotations

from datetime import datetime

from app import main as legacy
from app import v0381


def _question(prompt: str, skill: str = 'VC2M4N06:written_addition', answer: str = '0') -> legacy.Question:
    return legacy.Question(
        worksheet_id=1,
        topic='number',
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type='number',
        payload='{}',
        correct_answer=answer,
        working='',
        position=0,
    )


def test_small_direct_addition_is_upgraded_to_larger_values():
    question = _question('Calculate 121 + 22.')
    import random
    assert v0381._upgrade_direct_arithmetic(question, random.Random(7)) is True
    values = [int(value) for value in __import__('re').findall(r'\d+', question.prompt)]
    assert max(values[:2]) >= 220
    assert min(values[:2]) >= 35
    assert question.skill.endswith('written_addition')
    assert question.answer_type == 'number'


def test_already_substantial_addition_is_not_rewritten():
    question = _question('Calculate 327 + 286.')
    import random
    assert v0381._upgrade_direct_arithmetic(question, random.Random(7)) is False
    assert question.prompt == 'Calculate 327 + 286.'


def test_operation_selection_becomes_numeric_total_question():
    question = _question(
        'There are 5 equal groups with 8 items in each group. Which operation would find the total?',
        skill='VC2M4N09:operation_selection',
        answer='multiplication',
    )
    question.answer_type = 'choice'
    question.payload = '{"choices":["addition","subtraction","multiplication","division"],"reasoning_type":"operation_selection"}'
    assert v0381._replace_operation_only_question(question) is True
    assert question.prompt == 'There are 5 equal groups with 8 items in each group. How many items are there altogether?'
    assert question.answer_type == 'number'
    assert question.correct_answer == '40'
    assert '5 × 8 = 40' in question.working


def test_history_time_is_converted_from_utc_to_melbourne():
    # September uses AEST (UTC+10).
    assert v0381._melbourne_time(datetime(2026, 9, 3, 11, 9)) == '9:09 PM'


def test_history_time_observes_melbourne_daylight_saving():
    # January uses AEDT (UTC+11).
    assert v0381._melbourne_time(datetime(2026, 1, 3, 11, 9)) == '10:09 PM'
