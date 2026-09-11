from __future__ import annotations

import json
import random
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0170, v0460

app = v0460.app
app.version = '0.47.0'
legacy.APP_VERSION = '0.47.0'

def _tag(payload: dict[str, Any], family: str, representation: str, evidence_type: str) -> dict[str, Any]:
    return {**payload, 'question_family': family, 'representation': representation, 'evidence_type': evidence_type, 'grade_band': 5}

def _equivalent_fraction(rng: random.Random):
    denominator = rng.choice([2, 3, 4, 5, 8, 10])
    numerator = rng.randint(1, denominator - 1)
    factor = rng.choice([2, 3])
    mode = rng.choice(['missing_numerator', 'missing_denominator', 'comparison'])
    if mode == 'missing_numerator':
        prompt = f'Complete the equivalent fraction: {numerator}/{denominator} = □/{denominator * factor}.'
        answer = numerator * factor
        working = f'Multiply the numerator and denominator by {factor}: {numerator} × {factor} = {answer}.'
    elif mode == 'missing_denominator':
        prompt = f'Complete the equivalent fraction: {numerator}/{denominator} = {numerator * factor}/□.'
        answer = denominator * factor
        working = f'Multiply the denominator by {factor}: {denominator} × {factor} = {answer}.'
    else:
        other = numerator * factor
        prompt = f'Which fraction is equivalent to {numerator}/{denominator}?'
        choices = [f'{other}/{denominator * factor}', f'{numerator + 1}/{denominator}', f'{numerator}/{denominator + 1}']
        rng.shuffle(choices)
        return legacy.q('VC2M4N03', 'equivalent_fractions', prompt, 'choice',
                        _tag({'choices': choices}, 'equivalent_fraction_choice', 'symbolic', 'conceptual'),
                        f'{other}/{denominator * factor}',
                        f'{other}/{denominator * factor} has both parts multiplied by {factor}.')
    return legacy.q('VC2M4N03', 'equivalent_fractions', prompt, 'number',
                    _tag({}, f'equivalent_fraction_{mode}', 'symbolic', 'conceptual'), answer, working)

def _multiplication_family(rng: random.Random):
    factor = rng.choice([3, 4, 6, 7, 8])
    base = rng.randint(12, 48)
    product = base * factor
    mode = rng.choice(['direct', 'missing_factor', 'inverse', 'context'])
    if mode == 'direct':
        prompt, answer = f'Calculate {base} × {factor}.', product
        working = f'Partition {base}: ({base // 10 * 10} × {factor}) + ({base % 10} × {factor}) = {product}.'
        representation, evidence = 'symbolic', 'procedural'
    elif mode == 'missing_factor':
        prompt, answer = f'Find the missing factor: □ × {factor} = {product}.', base
        working = f'Use the inverse operation: {product} ÷ {factor} = {base}.'
        representation, evidence = 'equation', 'conceptual'
    elif mode == 'inverse':
        prompt, answer = f'If {base} × {factor} = {product}, what is {product} ÷ {factor}?', base
        working = f'Multiplication and division are inverse operations, so {product} ÷ {factor} = {base}.'
        representation, evidence = 'inverse', 'conceptual'
    else:
        prompt, answer = f'{factor} boxes each contain {base} pencils. How many pencils are there?', product
        working = f'Model equal groups: {factor} × {base} = {product} pencils.'
        representation, evidence = 'context', 'transfer'
    return legacy.q('VC2M4N06', 'efficient_multiply_divide', prompt, 'number',
                    _tag({}, f'multiplication_{mode}', representation, evidence), answer, working)

def _pattern_family(rng: random.Random):
    step, start = rng.randint(2, 9), rng.randint(4, 30)
    mode = rng.choice(['next_term', 'missing_rule', 'missing_middle'])
    values = [start + step * i for i in range(4)]
    if mode == 'next_term':
        prompt, answer = f'Continue the pattern: {", ".join(map(str, values))}, □.', values[-1] + step
    elif mode == 'missing_rule':
        prompt, answer = f'The pattern {", ".join(map(str, values))} follows which rule?', f'add {step}'
        return legacy.q('VC2M4N02', 'number_sequences', prompt, 'text',
                        _tag({}, 'pattern_rule', 'sequence', 'conceptual'), answer, f'Each term increases by {step}.')
    else:
        prompt, answer = f'Find the missing number: {values[0]}, □, {values[2]}, {values[3]}.', values[1]
    return legacy.q('VC2M4N02', 'number_sequences', prompt, 'number',
                    _tag({}, f'pattern_{mode}', 'sequence', 'conceptual'), answer, f'Add {step} each time.')

def _measurement_family(rng: random.Random):
    length, width = rng.randint(4, 12), rng.randint(3, 9)
    mode = rng.choice(['perimeter', 'area', 'missing_side'])
    if mode == 'perimeter':
        prompt, answer, skill = f'A rectangle is {length} cm by {width} cm. What is its perimeter?', 2 * (length + width), 'perimeter'
        working = f'Perimeter = 2 × ({length} + {width}) = {answer} cm.'
    elif mode == 'area':
        prompt, answer, skill = f'A rectangle is {length} cm by {width} cm. What is its area?', length * width, 'area'
        working = f'Area = {length} × {width} = {answer} cm².'
    else:
        perimeter = 2 * (length + width)
        prompt, answer, skill = f'A rectangle has a perimeter of {perimeter} cm and a length of {length} cm. What is its width?', width, 'perimeter'
        working = f'Half the perimeter is {perimeter // 2} cm. Subtract the length to get {width} cm.'
    return legacy.q('VC2M4M02', skill, prompt, 'number',
                    _tag({'unit': 'cm²' if skill == 'area' else 'cm'}, f'measurement_{mode}', 'symbolic', 'transfer' if mode == 'missing_side' else 'procedural'),
                    answer, working)

def _decimal_relationship(rng: random.Random):
    denominator, numerator = rng.choice([2, 4, 5, 10]), 0
    numerator = rng.randint(1, denominator - 1)
    decimal = numerator / denominator
    prompt = f'Which decimal is equal to {numerator}/{denominator}?'
    choices = [f'{decimal:g}', f'{decimal + 0.1:g}', f'{decimal + 0.2:g}']
    rng.shuffle(choices)
    return legacy.q('VC2M4N03', 'equivalent_fractions', prompt, 'choice',
                    _tag({'choices': choices}, 'fraction_decimal_match', 'symbolic', 'conceptual'),
                    f'{decimal:g}', f'{numerator}/{denominator} is equal to {decimal:g}.')

FAMILY_GENERATORS = {
    'number': {'equivalent_fractions': _equivalent_fraction, 'efficient_multiply_divide': _multiplication_family,
               'number_sequences': _pattern_family, 'decimal_place_value': _decimal_relationship},
    'measurement': {'perimeter': _measurement_family, 'area': _measurement_family},
}
for topic, generators in FAMILY_GENERATORS.items():
    v0170.FOCUS_GENERATORS.setdefault(topic, {}).update(generators)

def coverage_report() -> dict[str, Any]:
    return {
        'version': '0.47.0',
        'families': sorted(f'{topic}:{skill}' for topic, values in FAMILY_GENERATORS.items() for skill in values),
        'known_gaps': ['place-value ordering', 'fraction ordering and visual comparison', 'area/perimeter diagrams',
                       'multi-step statistics interpretation', 'equally-likely probability representation'],
    }

_original_make_question = legacy.make_question
def make_question_v0470(topic: str, level: int, rng: random.Random):
    target = getattr(v0170, '_focus_targets', None)
    target = target.get().get(topic) if target else None
    generator = FAMILY_GENERATORS.get(topic, {}).get(target)
    if generator and rng.random() < .85:
        return generator(rng)
    return _original_make_question(topic, level, rng)
legacy.make_question = make_question_v0470

@app.get('/api/v0470/curriculum-coverage')
def curriculum_coverage(_: legacy.User = Depends(legacy.current_user)):
    return coverage_report()

@app.get('/api/v0470/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': '0.47.0', 'question_families': True, 'level5_coverage_report': True,
            'targeted_generator_routing': True, 'representation_metadata': True, 'inherits_v0460': True}

v0460.app.router.routes[:] = [route for route in v0460.app.router.routes if not (
    getattr(route, 'path', None) == '/api/v0460/capabilities')]
v0120._move_spa_fallback_to_end()
