from __future__ import annotations

import json
import random
import re

from app import main as legacy
from app import v0310, v0321, v0323


def question(topic: str, skill: str, prompt: str, answer: str, payload: dict | None = None):
    return legacy.Question(
        worksheet_id=1,
        topic=topic,
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type='number',
        payload=json.dumps(payload or {}),
        correct_answer=str(answer),
        working='',
        position=0,
    )


def test_multidigit_multiplication_hints_teach_written_place_value_without_answer():
    q = question('number', 'VC2M4N06:efficient_multiply_divide', 'Calculate 327 × 6.', '1962')
    content = v0323.tutoring_content_v0323(q)
    assert content['strategy'] == 'written multiplication using place value'
    text = ' '.join(content['hints']).lower()
    assert 'ones' in text and 'carry' in text and 'tens' in text
    assert '1962' not in text


def test_multiplication_worked_example_uses_different_values_and_explains_partitioning():
    q = question('number', 'VC2M4N06:efficient_multiply_divide', 'Calculate 327 × 6.', '1962')
    example = v0323.aligned_worked_example_v0323(q)
    assert '327 × 6' not in example
    assert 'ones' in example.lower()
    assert 'hundreds' in example.lower()
    assert 'partition' in example.lower()
    assert 'why it works' in example.lower()


def test_division_hints_use_partitioning_and_inverse_check_without_quotient():
    q = question('number', 'VC2M4N06:efficient_multiply_divide', 'Calculate 864 ÷ 8.', '108')
    content = v0323.tutoring_content_v0323(q)
    text = ' '.join(content['hints']).lower()
    assert 'break' in text or 'parts' in text
    assert 'multiply' in text
    assert '108' not in text


def test_division_worked_example_is_mathematically_valid_and_checks_inverse():
    q = question('number', 'VC2M4N06:efficient_multiply_divide', 'Calculate 864 ÷ 8.', '108')
    example = v0323.aligned_worked_example_v0323(q)
    assert '864 ÷ 8' not in example
    match = re.search(r'Worked example: (\d+) ÷ (\d+)', example)
    assert match
    dividend, divisor = map(int, match.groups())
    quotient_match = re.search(r'Therefore \d+ ÷ \d+ = (\d+)', example)
    assert quotient_match
    quotient = int(quotient_match.group(1))
    assert dividend // divisor == quotient
    assert quotient * divisor == dividend
    assert 'inverse operation' in example.lower()


def test_decimal_fraction_question_keeps_denominator_100():
    for seed in range(80):
        skill, prompt, answer_type, payload, answer, working = v0323._decimal_fraction_question(random.Random(seed))
        assert skill.endswith(':decimal_fraction_hundredths')
        assert prompt.endswith('as a fraction out of 100.')
        assert answer_type == 'text'
        assert answer.endswith('/100')
        assert payload['denominator_required'] == 100
        assert 'denominator as 100' in working


def test_decimal_fraction_hints_explain_place_value_without_revealing_answer():
    q = question('number', 'VC2M4N01:decimal_fraction_hundredths', 'Write 0.36 as a fraction out of 100.', '36/100')
    content = v0323.tutoring_content_v0323(q)
    text = ' '.join(content['hints']).lower()
    assert 'tenths' in text and 'hundredths' in text
    assert 'denominator as 100' in text
    assert '36/100' not in text


def test_decimal_fraction_worked_example_uses_different_decimal_and_retains_100():
    q = question('number', 'VC2M4N01:decimal_fraction_hundredths', 'Write 0.36 as a fraction out of 100.', '36/100')
    example = v0323.aligned_worked_example_v0323(q)
    assert '0.36' not in example
    assert '/100' in example
    assert 'tenths' in example.lower() and 'hundredths' in example.lower()
    assert 'leave the denominator as 100' in example.lower()


def test_perimeter_hints_teach_around_outside_before_formula_and_use_cm():
    q = question('measurement', 'VC2M4M02:perimeter', 'A rectangle is 9 cm by 6 cm. What is its perimeter?', '30', {'unit': 'cm'})
    content = v0323.tutoring_content_v0323(q)
    text = ' '.join(content['hints']).lower()
    assert 'around the outside' in text
    assert 'two sides of 9 cm' in text
    assert '2 × (length + width)' in text
    assert '30' not in text


def test_perimeter_worked_example_uses_different_values_and_explains_formula():
    q = question('measurement', 'VC2M4M02:perimeter', 'A rectangle is 9 cm by 6 cm. What is its perimeter?', '30', {'unit': 'cm'})
    example = v0323.aligned_worked_example_v0323(q)
    dimensions = re.search(r'Worked example: a rectangle is (\d+) cm long and (\d+) cm wide', example)
    assert dimensions
    assert tuple(map(int, dimensions.groups())) != (9, 6)
    assert 'around the outside' in example.lower()
    assert 'two equal lengths and two equal widths' in example.lower()
    assert 'cm²' not in example


def test_area_hints_explain_square_units_and_distinguish_perimeter():
    q = question('measurement', 'VC2M4M02:area', 'A rectangle is 9 cm by 6 cm. What is its area?', '54', {'unit': 'cm²'})
    content = v0323.tutoring_content_v0323(q)
    text = ' '.join(content['hints']).lower()
    assert 'space is inside' in text
    assert '1 cm² squares' in text
    assert '9 squares in each row' in text
    assert 'cm²' in text
    assert '54' not in text


def test_area_worked_example_counts_rows_and_columns_and_uses_square_centimetres():
    q = question('measurement', 'VC2M4M02:area', 'A rectangle is 9 cm by 6 cm. What is its area?', '54', {'unit': 'cm²'})
    example = v0323.aligned_worked_example_v0323(q)
    dimensions = re.search(r'Worked example: a rectangle is (\d+) cm by (\d+) cm', example)
    assert dimensions
    assert tuple(map(int, dimensions.groups())) != (9, 6)
    assert 'squares in each row' in example.lower()
    assert 'rows' in example.lower()
    assert 'cm²' in example
    assert 'perimeter would use cm' in example.lower()


def test_new_number_question_is_minor_supplement_and_grade5_bounded():
    rng = random.Random(239)
    skills = [v0323.make_question_v0323('number', 4, rng)[0].split(':', 1)[-1] for _ in range(500)]
    count = skills.count('decimal_fraction_hundredths')
    assert 20 <= count <= 90
    assert any(skill != 'decimal_fraction_hundredths' for skill in skills)
    for seed in range(100):
        _, prompt, _, _, answer, _ = v0323._decimal_fraction_question(random.Random(seed))
        value = float(re.search(r'\d+\.\d+', prompt).group())
        numerator = int(answer.split('/')[0])
        assert 0.10 < value < 1.0
        assert numerator == round(value * 100)


def test_existing_tutoring_falls_through_for_unrelated_question_types():
    q = question('statistics', 'VC2M4ST01:data_frequency', 'The survey results are [1, 2, 2, 3]. Which value occurs most often?', '2')
    assert v0323.tutoring_content_v0323(q) == v0323._prior_tutoring_content(q)


def test_runtime_hooks_use_v0323_tutoring_and_examples():
    q = question('number', 'VC2M4N06:efficient_multiply_divide', 'Calculate 327 × 6.', '1962')
    assert v0310.tutoring_content(q)['strategy'] == 'written multiplication using place value'
    assert 'Worked example' in v0321.aligned_worked_example(q)
