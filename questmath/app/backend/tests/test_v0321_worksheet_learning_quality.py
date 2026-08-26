from __future__ import annotations

import json

from app import main as legacy
from app import v0321


def question(topic: str, skill: str, prompt: str, answer: str = '0', level: int = 4) -> legacy.Question:
    return legacy.Question(
        worksheet_id=1,
        topic=topic,
        skill=skill,
        level=level,
        prompt=prompt,
        answer_type='number',
        payload='{}',
        correct_answer=answer,
        working='',
        position=0,
    )


def test_trivial_arithmetic_is_identified_as_retrieval():
    q = question('number', 'VC2M4N06:written_addition', 'Calculate 4 + 5.', '9')
    assert v0321._is_trivial_arithmetic(q) is True
    assert v0321._difficulty_band(q) == 'retrieval'


def test_hundreds_arithmetic_is_not_retrieval():
    q = question('number', 'VC2M4N06:written_addition', 'Calculate 324 + 47.', '371')
    payload = {'instructional_band': 'hundreds'}
    q.payload = json.dumps(payload)
    assert v0321._is_trivial_arithmetic(q) is False
    assert v0321._difficulty_band(q) == 'challenge'


def test_probability_worked_example_matches_probability_family_without_answer_leak():
    q = question(
        'probability',
        'VC2M4P02:repeated_chance',
        'A coin was tossed 100 times: 60 heads and 40 tails. Is variation from exactly 50 each normal?',
        'yes',
    )
    example = v0321.aligned_worked_example(q)
    assert 'coin' in example.lower()
    assert '40 times' in example
    assert '60 heads' not in example
    assert '100 times' not in example


def test_fraction_number_line_example_uses_same_representation_with_different_values():
    q = question('number', 'VC2M4N04:fraction_number_line', 'Select the point that represents 8/10 on the number line.', '8')
    example = v0321.aligned_worked_example(q)
    assert 'number line' in example.lower()
    assert '5/8' in example
    assert '8/10' not in example


def test_measurement_examples_are_attribute_specific():
    perimeter = question('measurement', 'VC2M4M03:perimeter', 'Find the perimeter of a rectangle 8 cm by 3 cm.', '22')
    area = question('measurement', 'VC2M4M03:area', 'Find the area of a rectangle 8 cm by 3 cm.', '24')
    assert 'distance around' in v0321.aligned_worked_example(perimeter).lower()
    assert 'square units' in v0321.aligned_worked_example(area).lower()


def test_worked_example_payload_includes_alignment_metadata():
    q = question('probability', 'VC2M4P02:repeated_chance', 'A coin was tossed 100 times: 58 heads and 42 tails. Is variation from exactly 50 each normal?', 'yes')
    payload = v0321.mentor_payload_v0321(q, 'worked_example')
    assert payload['example_is_aligned'] is True
    assert payload['example_alignment']['topic'] == 'probability'
    assert payload['example_alignment']['question_family']
    assert str(q.correct_answer).lower() not in payload['worked_example'].lower()
