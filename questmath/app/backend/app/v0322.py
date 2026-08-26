from __future__ import annotations

import json
import random
import re
from typing import Any, Callable

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0170, v0200, v0290, v0301, v0310, v0321

app = v0321.app
app.version = '0.32.2'
legacy.APP_VERSION = '0.32.2'

_prior_make_question = legacy.make_question
_prior_question_family = v0301.question_family
_prior_tutoring_content = v0310.tutoring_content
_prior_aligned_worked_example = v0321.aligned_worked_example

VARIABLES = ['a', 'b', 'm', 'n', 'p', 't', 'x', 'y']
NAMES = ['Ava', 'Liam', 'Mia', 'Noah', 'Sophie', 'Jack', 'Ruby', 'Ethan']
CONTEXTS = [
    ('marbles', 'marbles'),
    ('stickers', 'stickers'),
    ('cards', 'cards'),
    ('books', 'books'),
    ('toy cars', 'toy cars'),
    ('points', 'points'),
    ('pencils', 'pencils'),
    ('shells', 'shells'),
]


def _q(code: str, skill: str, prompt: str, payload: dict[str, Any], answer: int, working: str):
    payload = dict(payload)
    payload['grade_band'] = 5
    payload['algebra_structure'] = skill
    return legacy.q(code, skill, prompt, 'number', payload, answer, working)


def _strategy(title: str, rule: str, steps: list[str], example: str, operation: str = 'equation') -> dict[str, Any]:
    return v0170._card(title, 'Use the relationship and inverse operation', rule, steps, example, operation)


def _pattern(rng: random.Random):
    mode = rng.choice(['add', 'subtract', 'multiply'])
    if mode == 'multiply':
        factor = rng.choice([2, 3])
        start = rng.randint(1, 6)
        values = [start]
        for _ in range(5):
            values.append(values[-1] * factor)
        shown = values[:4]
        answer = values[4]
        rule = f'Multiply by {factor} each time.'
    else:
        step = rng.randint(2, 9)
        if mode == 'add':
            start = rng.randint(2, 35)
            shown = [start + step * i for i in range(4)]
            answer = shown[-1] + step
            rule = f'Add {step} each time.'
        else:
            start = rng.randint(step * 5 + 5, step * 8 + 30)
            shown = [start - step * i for i in range(4)]
            answer = shown[-1] - step
            rule = f'Subtract {step} each time.'
    prompt = 'Continue the pattern: ' + ', '.join(str(value) for value in shown) + ', ___, ___ . What number goes in the first blank?'
    payload = {
        'pattern_rule': mode,
        'strategy_card': _strategy('Continue a number pattern', rule, ['Compare neighbouring terms.', 'Identify the operation repeated each time.', 'Apply the same rule once more to reach the first blank.'], 'Example: 6, 10, 14, 18, ___ uses +4 each time.'),
    }
    return _q('VC2M5N10', 'grade5_number_pattern', prompt, payload, answer, f'{rule} The next value is {answer}.')


def _addition_unknown(rng: random.Random):
    unknown = rng.randint(8, 48); change = rng.randint(4, 25); total = unknown + change; variable = rng.choice(VARIABLES)
    prompt = f'Find the value of {variable}: {variable} + {change} = {total}.'
    payload = {'operation': 'equation', 'variable': variable, 'strategy_card': _strategy('Find an unknown value', f'Undo + {change} by subtracting {change}.', ['Start with the total.', 'Subtract the amount that was added.', 'Substitute the value back to check the equation.'], 'Example: x + 7 = 19 → calculate 19 − 7.')}
    return _q('VC2M4A01', 'grade5_addition_unknown', prompt, payload, unknown, f'Use the inverse operation: {total} − {change} = {unknown}.')


def _subtraction_unknown(rng: random.Random):
    change = rng.randint(4, 25); result = rng.randint(7, 40); unknown = result + change; variable = rng.choice(VARIABLES)
    prompt = f'Find the value of {variable}: {variable} − {change} = {result}.'
    payload = {'operation': 'equation', 'variable': variable, 'strategy_card': _strategy('Find an unknown value', f'Undo − {change} by adding {change}.', ['Start with the result.', 'Add back the amount that was subtracted.', 'Check by subtracting it again.'], 'Example: n − 6 = 14 → calculate 14 + 6.')}
    return _q('VC2M4A01', 'grade5_subtraction_unknown', prompt, payload, unknown, f'Use the inverse operation: {result} + {change} = {unknown}.')


def _substitution_add(rng: random.Random):
    variable = rng.choice(VARIABLES); value = rng.randint(2, 15); add = rng.randint(3, 18); answer = value + add
    prompt = f'If {variable} = {value}, what is {variable} + {add}?'
    payload = {'operation': 'substitution', 'variable': variable, 'variable_value': value, 'strategy_card': _strategy('Substitute the given value', f'{variable} represents {value}. Replace the letter with {value} before calculating.', ['Replace the letter with its given value.', 'Read the expression again as a number sentence.', 'Calculate the result.'], 'Example: if a = 5, then a + 8 becomes 5 + 8.', 'addition')}
    return _q('VC2M4A01', 'grade5_substitution_add', prompt, payload, answer, f'Replace {variable} with {value}: {value} + {add} = {answer}.')


def _substitution_multiply(rng: random.Random):
    variable = rng.choice(VARIABLES); value = rng.randint(2, 12); factor = rng.randint(2, 10); answer = value * factor
    prompt = f'If {variable} = {value}, what is {factor} × {variable}?'
    payload = {'operation': 'substitution', 'variable': variable, 'variable_value': value, 'strategy_card': _strategy('Substitute the given value', f'{variable} represents {value}. Replace the letter with {value}.', ['Replace the letter with its given value.', f'Calculate {factor} × {value} using a known multiplication fact.', 'Check the product is sensible.'], 'Example: if b = 4, then 3 × b becomes 3 × 4.', 'multiplication')}
    return _q('VC2M5A01', 'grade5_substitution_multiply', prompt, payload, answer, f'Replace {variable} with {value}: {factor} × {value} = {answer}.')


def _mystery_number(rng: random.Random):
    unknown = rng.randint(8, 55); change = rng.randint(5, 24); mode = rng.choice(['plus', 'minus'])
    if mode == 'plus':
        total = unknown + change
        prompt = f'A mystery number plus {change} equals {total}. What is the mystery number?'
        working = f'Undo adding {change}: {total} − {change} = {unknown}.'
        rule = f'Use subtraction to undo the + {change}.'
    else:
        result = max(1, unknown - change)
        unknown = result + change
        prompt = f'A mystery number minus {change} equals {result}. What is the mystery number?'
        working = f'Undo subtracting {change}: {result} + {change} = {unknown}.'
        rule = f'Use addition to undo the − {change}.'
    payload = {'operation': 'equation', 'strategy_card': _strategy('Solve a mystery number', rule, ['Identify what happened to the mystery number.', 'Use the opposite operation to work backwards.', 'Check the result in the original statement.'], 'Example: a mystery number plus 9 equals 24 → calculate 24 − 9.')}
    return _q('VC2M4A01', 'grade5_mystery_number', prompt, payload, unknown, working)


def _unknown_start_context(rng: random.Random):
    name = rng.choice(NAMES); item, unit = rng.choice(CONTEXTS); start = rng.randint(7, 45); gained = rng.randint(4, 22); total = start + gained
    prompt = f'{name} has some {item}. {name} gets {gained} more and now has {total} {unit}. How many {unit} did {name} have at the start?'
    payload = {'operation': 'equation', 'context': item, 'strategy_card': _strategy('Work backwards from the final amount', f'The starting amount increased by {gained}, so subtract {gained} from the final total.', ['Identify the final amount.', 'Identify how many were added.', 'Subtract the added amount to recover the starting value.'], 'Example: Mia has some cards, gets 6 more and has 21. Calculate 21 − 6.')}
    return _q('VC2M4A01', 'grade5_unknown_start_context', prompt, payload, start, f'Work backwards: {total} − {gained} = {start}.')


def _reverse_multiplication(rng: random.Random):
    name = rng.choice(NAMES); factor = rng.choice([2, 3, 4, 5, 6]); original = rng.randint(2, 12); result = factor * original
    wording = 'doubles it' if factor == 2 and rng.random() < 0.7 else f'multiplies it by {factor}'
    prompt = f'{name} thinks of a number, {wording}, and gets {result}. What number did {name} start with?'
    payload = {'operation': 'equation', 'factor': factor, 'strategy_card': _strategy('Undo multiplication with division', f'The starting number was multiplied by {factor}. Divide {result} by {factor} to work backwards.', ['Identify the multiplication factor.', 'Use division as the inverse operation.', 'Check by multiplying your answer by the factor.'], 'Example: a number is tripled to make 24 → calculate 24 ÷ 3.', 'division')}
    return _q('VC2M5A02', 'grade5_reverse_multiplication', prompt, payload, original, f'Use the inverse operation: {result} ÷ {factor} = {original}.')


NEW_GENERATORS: list[Callable[[random.Random], tuple[Any, ...]]] = [
    _pattern,
    _addition_unknown,
    _subtraction_unknown,
    _substitution_add,
    _substitution_multiply,
    _mystery_number,
    _unknown_start_context,
    _reverse_multiplication,
]


def make_question_v0322(topic: str, level: int, rng: random.Random):
    if topic == 'algebra' and level >= 3 and rng.random() < 0.42:
        return rng.choice(NEW_GENERATORS)(rng)
    return _prior_make_question(topic, level, rng)


def question_family_v0322(question: legacy.Question) -> str:
    skill = (question.skill or '').split(':', 1)[-1]
    if skill.startswith('grade5_'):
        return f'algebra:{skill}'
    return _prior_question_family(question)


def tutoring_content_v0322(question: legacy.Question) -> dict[str, Any]:
    skill = (question.skill or '').split(':', 1)[-1]
    payload = v0321._payload(question)
    card = payload.get('strategy_card') if isinstance(payload, dict) else None
    if skill.startswith('grade5_') and isinstance(card, dict):
        hints = [
            str(card.get('rule') or 'Identify the relationship first.'),
            ' '.join(str(step) for step in (card.get('steps') or [])[:2]),
            ' '.join(str(step) for step in (card.get('steps') or [])[1:3]),
        ]
        return {
            'strategy': str(card.get('strategy') or 'Use the relationship and inverse operation'),
            'hints': hints,
            'teach_steps': [
                {'label': 'Notice', 'text': hints[0]},
                {'label': 'Strategy', 'text': hints[1]},
                {'label': 'Your turn', 'text': 'Apply that relationship to the numbers in this question, then enter your answer.'},
            ],
        }
    return _prior_tutoring_content(question)


def aligned_worked_example_v0322(question: legacy.Question) -> str:
    skill = (question.skill or '').split(':', 1)[-1]
    examples = {
        'grade5_number_pattern': 'For a different pattern, 7, 12, 17, 22, ___ increases by 5 each time. Identify the repeated change, then apply it once more.',
        'grade5_addition_unknown': 'For a different equation, x + 9 = 26. Undo adding 9 by subtracting 9 from 26, then substitute the value back to check.',
        'grade5_subtraction_unknown': 'For a different equation, n − 7 = 18. Undo subtracting 7 by adding 7 to 18, then check the original equation.',
        'grade5_substitution_add': 'For a different substitution, if a = 6, then a + 9 becomes 6 + 9 before you calculate.',
        'grade5_substitution_multiply': 'For a different substitution, if b = 5, then 4 × b becomes 4 × 5 before you calculate.',
        'grade5_mystery_number': 'For a different mystery number, a number plus 11 equals 30. Use subtraction to work backwards, then check by adding 11 again.',
        'grade5_unknown_start_context': 'For a different story, Ruby has some stickers, gets 7 more and finishes with 24. Work backwards from 24 by undoing the 7 that were added.',
        'grade5_reverse_multiplication': 'For a different reverse multiplication problem, a number is tripled to make 27. Use division to undo the multiplication, then check by multiplying again.',
    }
    if skill in examples:
        return examples[skill]
    return _prior_aligned_worked_example(question)


legacy.make_question = make_question_v0322
v0301.question_family = question_family_v0322
v0310.tutoring_content = tutoring_content_v0322
v0321.aligned_worked_example = aligned_worked_example_v0322


@app.get('/api/v0322/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.32.2',
        'grade5_algebra_variety': True,
        'pattern_questions': True,
        'variable_substitution': True,
        'contextual_unknowns': True,
        'reverse_multiplication': True,
        'structural_family_diversity': True,
        'inherits_v0321': True,
    }


v0120._move_spa_fallback_to_end()
