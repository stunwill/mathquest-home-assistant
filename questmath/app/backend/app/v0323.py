from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends

from . import main as legacy
from . import v0120, v0310, v0321, v0322

app = v0322.app
app.version = '0.32.3'
legacy.APP_VERSION = '0.32.3'

_prior_make_question = legacy.make_question
_prior_tutoring_content = v0310.tutoring_content
_prior_worked_example = v0321.aligned_worked_example
_prior_operation = v0310._operation


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _skill(question: legacy.Question) -> str:
    return (question.skill or '').split(':', 1)[-1].lower()


def _numbers(prompt: str) -> list[str]:
    return re.findall(r'\d+(?:\.\d+)?', prompt or '')


def _operation_v0323(question: legacy.Question) -> str | None:
    prompt = question.prompt or ''
    if '÷' in prompt or ' / ' in prompt:
        return 'division'
    if '×' in prompt:
        return 'multiplication'
    return _prior_operation(question)


def _safe_example_number(value: int, delta: int, minimum: int = 2, maximum: int = 999) -> int:
    candidate = max(minimum, min(maximum, value + delta))
    return candidate if candidate != value else max(minimum, min(maximum, value + delta + 1))


def _written_multiplication_content(question: legacy.Question) -> dict[str, Any] | None:
    if _operation_v0323(question) != 'multiplication':
        return None
    nums = _numbers(question.prompt)
    if len(nums) < 2:
        return None
    a, b = int(float(nums[0])), int(float(nums[1]))
    larger, single = (a, b) if a >= b else (b, a)
    if single < 2 or single > 12 or larger < 20:
        return None
    ones = larger % 10
    tens = (larger // 10) % 10
    hundreds = (larger // 100) % 10
    hint1 = 'This is multiplication. Start with the ones column so each place value is dealt with in order.'
    hint2 = f'Start with the ones: {single} × {ones}. Write the ones digit of that product in the ones column and carry any extra ten to the tens column.'
    if larger >= 100:
        hint3 = f'Next multiply the tens digit {tens} by {single} and add the carried tens. Then do the hundreds digit {hundreds}. Keep each result lined up with its place-value column.'
    else:
        hint3 = f'Next multiply the tens digit {tens} by {single} and add the carried tens. Keep the answer lined up in the tens and hundreds columns.'
    return {
        'strategy': 'written multiplication using place value',
        'hints': [hint1, hint2, hint3],
        'teach_steps': [
            {'label': 'Concept', 'text': 'Written multiplication works because each digit represents ones, tens, hundreds and so on.'},
            {'label': 'First step', 'text': f'Begin with {single} × {ones}. If the product is 10 or more, write its ones digit and carry the tens.'},
            {'label': 'Why it works', 'text': 'Moving right to left keeps each partial product in the correct place-value column.'},
            {'label': 'Your turn', 'text': 'Continue through the tens and hundreds, adding any carried value before writing each column.'},
        ],
    }


def _partition_division_content(question: legacy.Question) -> dict[str, Any] | None:
    if _operation_v0323(question) != 'division':
        return None
    nums = _numbers(question.prompt)
    if len(nums) < 2:
        return None
    dividend, divisor = int(float(nums[0])), int(float(nums[1]))
    if divisor < 2 or dividend <= divisor or dividend % divisor:
        return None
    hundreds = (dividend // 100) * 100
    remainder = dividend - hundreds
    if hundreds and hundreds % divisor == 0 and remainder and remainder % divisor == 0:
        partition = (hundreds, remainder)
    else:
        first = (dividend // divisor // 10) * 10 * divisor
        if first <= 0 or first >= dividend:
            first = divisor * max(1, (dividend // divisor) - 1)
        partition = (first, dividend - first)
    left, right = partition
    hint1 = 'Division can be easier if you break the dividend into parts that are easy to divide by the divisor.'
    hint2 = f'Look for two parts of {dividend} that both divide evenly by {divisor}. A useful split is based on place value or known multiplication facts.'
    hint3 = f'Divide each part by {divisor}, then add the two quotients. Check your result by multiplying it by {divisor} to see if you get back to {dividend}.'
    return {
        'strategy': 'partition the dividend into easy multiples',
        'hints': [hint1, hint2, hint3],
        'teach_steps': [
            {'label': 'Concept', 'text': 'Division asks how many equal groups fit into a number.'},
            {'label': 'Partition', 'math': [f'{dividend} = {left} + {right}']},
            {'label': 'Method', 'text': f'Divide each part by {divisor}, then combine the quotients.'},
            {'label': 'Check', 'text': f'Multiply your quotient by {divisor}. The product should be {dividend}.'},
        ],
    }


def _decimal_fraction_content(question: legacy.Question) -> dict[str, Any] | None:
    skill = _skill(question)
    prompt = question.prompt.lower()
    if 'decimal_fraction_hundredths' not in skill and not ('fraction' in prompt and '100' in prompt and '.' in prompt):
        return None
    nums = re.findall(r'\d+\.\d+', question.prompt or '')
    if not nums:
        return None
    value = nums[0]
    decimal = value.split('.')[1].ljust(2, '0')[:2]
    tenths, hundredths = decimal[0], decimal[1]
    return {
        'strategy': 'read the decimal using place value',
        'hints': [
            'A decimal can be read by looking at the place of each digit after the decimal point.',
            f'In {value}, {tenths} is in the tenths place and {hundredths} is in the hundredths place.',
            'Read the two decimal digits together as hundredths. Because the question asks for a fraction out of 100, keep the denominator as 100.',
        ],
        'teach_steps': [
            {'label': 'Concept', 'text': 'The first digit after the decimal point is tenths. The second digit is hundredths.'},
            {'label': 'Meaning', 'text': f'{value} represents a whole-number count of hundredths.'},
            {'label': 'Your turn', 'text': 'Write that count over 100. Do not simplify when the question specifically says “out of 100”.'},
        ],
    }


def _perimeter_area_content(question: legacy.Question) -> dict[str, Any] | None:
    if question.topic != 'measurement':
        return None
    skill = _skill(question)
    prompt = question.prompt.lower()
    nums = [int(float(x)) for x in _numbers(question.prompt)[:2]]
    if len(nums) < 2:
        return None
    length, width = nums
    if 'perimeter' in skill or 'perimeter' in prompt:
        return {
            'strategy': 'understand perimeter as the distance around the outside',
            'hints': [
                'Perimeter means the total distance around the outside edge of the rectangle.',
                f'A rectangle has two sides of {length} cm and two sides of {width} cm. Think about adding all four side lengths.',
                'You can add the two equal lengths and the two equal widths first. That is why 2 × (length + width) works for rectangles.',
            ],
            'teach_steps': [
                {'label': 'Concept', 'text': 'Perimeter measures around the outside, so the unit stays a length unit such as cm.'},
                {'label': 'Rectangle fact', 'text': 'Opposite sides of a rectangle are equal: two lengths and two widths.'},
                {'label': 'Your turn', 'text': 'Add all four sides, or add one length and one width and double that total.'},
            ],
        }
    if 'area' in skill or 'area' in prompt:
        return {
            'strategy': 'understand area as counting square units inside',
            'hints': [
                'Area measures how much space is inside the rectangle, not the distance around it.',
                f'Imagine the rectangle covered with 1 cm² squares. There would be {length} squares in each row and {width} rows.',
                'Multiplying the number of squares in each row by the number of rows counts all the square units. Write the unit as cm².',
            ],
            'teach_steps': [
                {'label': 'Concept', 'text': 'Area counts square units covering the inside of a shape.'},
                {'label': 'Array', 'text': f'Think of {width} rows with {length} one-centimetre squares in each row.'},
                {'label': 'Units', 'text': 'Because each counted unit is a square centimetre, the answer uses cm² rather than cm.'},
                {'label': 'Your turn', 'text': 'Multiply the number of squares in each row by the number of rows.'},
            ],
        }
    return None


def tutoring_content_v0323(question: legacy.Question) -> dict[str, Any]:
    for builder in (_written_multiplication_content, _partition_division_content, _decimal_fraction_content, _perimeter_area_content):
        content = builder(question)
        if content:
            return content
    return _prior_tutoring_content(question)


def _written_multiplication_example(question: legacy.Question) -> str:
    nums = _numbers(question.prompt)
    a, b = (int(float(nums[0])), int(float(nums[1]))) if len(nums) >= 2 else (327, 6)
    larger, single = (a, b) if a >= b else (b, a)
    ex_larger = _safe_example_number(larger, -84 if larger > 150 else 31, 120, 699)
    ex_single = 4 if single != 4 else 6
    if ex_larger % 10 * ex_single < 10:
        ex_larger += 1
    ones = ex_larger % 10
    tens = (ex_larger // 10) % 10
    hundreds = (ex_larger // 100) % 10
    p1 = ones * ex_single
    c1, write1 = divmod(p1, 10)
    p2 = tens * ex_single + c1
    c2, write2 = divmod(p2, 10)
    p3 = hundreds * ex_single + c2
    answer = ex_larger * ex_single
    partition = f'{(ex_larger // 100) * 100} × {ex_single} + {((ex_larger % 100) // 10) * 10} × {ex_single} + {ex_larger % 10} × {ex_single} = {answer}'
    return (
        f'Worked example: {ex_larger} × {ex_single}\n'
        f'1. Ones: {ex_single} × {ones} = {p1}. Write {write1} in the ones column' + (f' and carry {c1} ten.' if c1 else '.') + '\n'
        f'2. Tens: {ex_single} × {tens} tens' + (f' + {c1} carried ten' if c1 else '') + f' = {p2} tens. Write {write2} in the tens column' + (f' and carry {c2} hundred.' if c2 else '.') + '\n'
        f'3. Hundreds: {ex_single} × {hundreds} hundreds' + (f' + {c2} carried hundred' if c2 else '') + f' = {p3} hundreds.\n'
        f'Therefore {ex_larger} × {ex_single} = {answer}.\n'
        f'Why it works: partitioning gives {partition}. The written method records those place-value partial products efficiently.'
    )


def _division_example(question: legacy.Question) -> str:
    nums = _numbers(question.prompt)
    divisor = int(float(nums[1])) if len(nums) >= 2 else 8
    ex_divisor = 9 if divisor != 9 else 8
    quotient = 104 if ex_divisor == 9 else 112
    dividend = ex_divisor * quotient
    hundreds = (dividend // 100) * 100
    rest = dividend - hundreds
    if hundreds % ex_divisor or rest % ex_divisor:
        hundreds = ex_divisor * ((dividend // ex_divisor // 10) * 10)
        rest = dividend - hundreds
    return (
        f'Worked example: {dividend} ÷ {ex_divisor}\n'
        f'Break {dividend} into {hundreds} + {rest}, because both parts divide evenly by {ex_divisor}.\n'
        f'{hundreds} ÷ {ex_divisor} = {hundreds // ex_divisor}\n'
        f'{rest} ÷ {ex_divisor} = {rest // ex_divisor}\n'
        f'Combine the parts: {hundreds // ex_divisor} + {rest // ex_divisor} = {quotient}.\n'
        f'Therefore {dividend} ÷ {ex_divisor} = {quotient}.\n'
        f'Check with the inverse operation: {quotient} × {ex_divisor} = {dividend}.'
    )


def _decimal_fraction_example(question: legacy.Question) -> str:
    nums = re.findall(r'\d+\.\d+', question.prompt or '')
    current = nums[0] if nums else '0.36'
    candidate = '0.42' if current != '0.42' else '0.57'
    hundredths = int(round(float(candidate) * 100))
    return (
        f'Worked example: write {candidate} as a fraction out of 100.\n'
        'The first digit after the decimal point is tenths and the second is hundredths.\n'
        f'{candidate} means {hundredths} hundredths, so {candidate} = {hundredths}/100.\n'
        'Because the question asks for a fraction out of 100, leave the denominator as 100.'
    )


def _measurement_example(question: legacy.Question) -> str:
    skill = _skill(question)
    nums = [int(float(x)) for x in _numbers(question.prompt)[:2]]
    a, b = nums if len(nums) >= 2 else [9, 6]
    length = 8 if a != 8 else 7
    width = 5 if b != 5 and length != 5 else 4
    if 'perimeter' in skill or 'perimeter' in question.prompt.lower():
        total = 2 * (length + width)
        return (
            f'Worked example: a rectangle is {length} cm long and {width} cm wide.\n'
            'Perimeter is the distance around the outside of the shape.\n'
            f'Add the four sides: {length} + {width} + {length} + {width}.\n'
            f'Or group the equal sides: {length} + {length} = {2 * length}, and {width} + {width} = {2 * width}.\n'
            f'Then {2 * length} + {2 * width} = {total} cm.\n'
            f'The shortcut 2 × ({length} + {width}) works because a rectangle has two equal lengths and two equal widths.'
        )
    area = length * width
    return (
        f'Worked example: a rectangle is {length} cm by {width} cm.\n'
        'Area measures the amount of space inside the rectangle. Imagine covering it with 1 cm² squares.\n'
        f'There are {length} squares in each row and {width} rows.\n'
        f'{length} × {width} = {area}, so the area is {area} cm².\n'
        'Perimeter would use cm because it measures length around the edge. Area uses cm² because it counts square units.'
    )


def aligned_worked_example_v0323(question: legacy.Question) -> str:
    if _written_multiplication_content(question):
        return _written_multiplication_example(question)
    if _partition_division_content(question):
        return _division_example(question)
    if _decimal_fraction_content(question):
        return _decimal_fraction_example(question)
    if _perimeter_area_content(question):
        return _measurement_example(question)
    return _prior_worked_example(question)


def _decimal_fraction_question(rng: random.Random):
    hundredths = rng.randint(11, 98)
    while hundredths % 10 == 0:
        hundredths = rng.randint(11, 98)
    value = hundredths / 100
    prompt = f'Write {value:.2f} as a fraction out of 100.'
    payload = {'denominator_required': 100, 'decimal_value': f'{value:.2f}', 'grade_band': 5}
    return legacy.q(
        'VC2M4N01',
        'decimal_fraction_hundredths',
        prompt,
        'text',
        payload,
        f'{hundredths}/100',
        f'{value:.2f} means {hundredths} hundredths, so write {hundredths}/100. Keep the denominator as 100 because the question asks for a fraction out of 100.',
    )


def make_question_v0323(topic: str, level: int, rng: random.Random):
    if topic == 'number' and level >= 3 and rng.random() < 0.10:
        return _decimal_fraction_question(rng)
    return _prior_make_question(topic, level, rng)


def mentor_payload_v0323(question: legacy.Question, action: str) -> dict[str, Any]:
    result = v0310.mentor_payload_v0310(question, action)
    if action == 'worked_example':
        result['worked_example'] = aligned_worked_example_v0323(question)
        result['example_is_aligned'] = True
        result['method_first'] = True
    return result


legacy.make_question = make_question_v0323
v0310._operation = _operation_v0323
v0310.tutoring_content = tutoring_content_v0323
v0321.aligned_worked_example = aligned_worked_example_v0323
v0310.mentor_payload_v0310 = mentor_payload_v0323


@app.get('/api/v0323/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.32.3',
        'method_first_hints': True,
        'written_multiplication_tutoring': True,
        'partition_division_tutoring': True,
        'decimal_fraction_hundredths': True,
        'perimeter_concept_tutoring': True,
        'area_square_unit_tutoring': True,
        'different_number_worked_examples': True,
        'inherits_v0322': True,
    }


v0120._move_spa_fallback_to_end()
