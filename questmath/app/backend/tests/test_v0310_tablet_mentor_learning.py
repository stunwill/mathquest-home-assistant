from __future__ import annotations

import json
import random

from app import main
from app import v0310


def make_question(prompt: str, skill: str = 'VC2M4N06:written_addition') -> main.Question:
    return main.Question(
        worksheet_id=1,
        topic='number',
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type='number',
        payload='{}',
        correct_answer='0',
        working='',
        position=0,
    )


def test_teach_me_uses_current_addition_operands_without_revealing_answer():
    question = make_question('Calculate 47 + 63.')
    content = v0310.tutoring_content(question)
    assert content['strategy'] in {'bridge to the next ten', 'regroup the ones', 'partition by place value'}
    maths = ' '.join(line for step in content['teach_steps'] for line in step.get('math', []))
    text = ' '.join(step.get('text', '') for step in content['teach_steps'])
    assert '47 = 40 + 7' in maths
    assert '63 = 60 + 3' in maths
    assert '7 and 3' in text
    assert '110' not in maths
    assert '110' not in text


def test_progressive_hints_are_distinct_and_stronger():
    question = make_question('Calculate 47 + 63.')
    hints = v0310.tutoring_content(question)['hints']
    assert len(hints) == 3
    assert len(set(hints)) == 3
    assert 'ones digits' in hints[0]
    assert '47 = 40 + 7' in hints[1]
    assert 'whole ten' in hints[2]
    assert all('110' not in hint for hint in hints)


def test_subtraction_teaching_detects_regrouping():
    question = make_question('Calculate 125 − 19.', 'VC2M4N06:written_subtraction')
    content = v0310.tutoring_content(question)
    assert content['strategy'] == 'decompose one ten'
    assert 'need to regroup one ten' in content['hints'][1]
    assert '125 = 100 + 20 + 5' in content['hints'][1]
    assert '19 = 10 + 9' in content['hints'][1]
    assert '106' not in ' '.join(content['hints'])


def test_simple_addition_can_be_upgraded_to_hundreds():
    question = make_question('Calculate 14 + 21.')
    changed = v0310._upgrade_simple_arithmetic(question, random.Random(7))
    assert changed is True
    values = v0310._numbers(question.prompt)
    assert values[0] >= 100
    assert values[1] >= 10
    assert int(question.correct_answer) == sum(values[:2])
    assert json.loads(question.payload)['instructional_band'] == 'hundreds'


def test_simple_subtraction_can_be_upgraded_and_remains_valid():
    question = make_question('Calculate 25 - 9.', 'VC2M4N06:written_subtraction')
    changed = v0310._upgrade_simple_arithmetic(question, random.Random(9))
    assert changed is True
    values = v0310._numbers(question.prompt)
    assert values[0] >= 100
    assert values[0] > values[1]
    assert int(question.correct_answer) == values[0] - values[1]


def test_question_context_is_structured_for_math_mentor():
    question = make_question('Calculate 214 + 37.')
    context = v0310._question_context(question)
    assert context['operation'] == 'addition'
    assert context['operands'] == [214, 37]
    assert context['topic'] == 'number'
    assert context['question_family']
    assert context['answer_type'] == 'number'
