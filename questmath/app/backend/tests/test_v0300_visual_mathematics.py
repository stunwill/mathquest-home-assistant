from __future__ import annotations

import json

from app import main as legacy
from app import v0300


def question(skill: str, prompt: str, answer: str = 'x', topic: str = 'number') -> legacy.Question:
    return legacy.Question(skill=skill, prompt=prompt, correct_answer=answer, payload='{}', topic=topic)


def test_fraction_model_selection_and_equal_whole_payload():
    q = question('VC2M5N03:fraction_compare', 'Which is larger, 3/4 or 5/8?')
    assert v0300.visual_model_for(q) == 'fractions'
    payload = v0300._safe_visual_payload(q, None)
    fraction = payload['fraction_comparison']
    assert fraction['equal_whole'] is True
    assert fraction['vertical_alignment'] is True
    assert fraction['items'][0]['numerator'] == 3
    assert fraction['items'][0]['denominator'] == 4
    assert fraction['items'][1]['numerator'] == 5
    assert fraction['items'][1]['denominator'] == 8


def test_teaching_visual_uses_different_values_for_assessment_safety():
    q = question('VC2M5N03:fraction_compare', 'Which is larger, 3/4 or 5/8?', '3/4')
    payload = v0300._safe_visual_payload(q, None)
    example = payload['teaching_example']
    assert example['assessed_values'] is False
    assert example['items'] != payload['fraction_comparison']['items']
    assert '3/4' not in json.dumps(example)
    assert '5/8' not in json.dumps(example)


def test_visual_model_selection_major_families():
    assert v0300.visual_model_for(question('written_subtraction', '432 − 178 = ?')) == 'place-value'
    assert v0300.visual_model_for(question('multiplication_facts', '8 × 7 = ?')) == 'arrays'
    assert v0300.visual_model_for(question('efficient_addition', '48 + 27 = ?')) == 'number-line'
    assert v0300.visual_model_for(question('length_measurement', 'Measure this length.', topic='measurement')) == 'measurement'


def test_addition_has_multiple_solution_strategies():
    strategies = v0300._strategy_set(question('efficient_addition', '48 + 27 = ?'))
    assert [item['id'] for item in strategies] == ['partition', 'compensate', 'place-value']
    assert len({item['visual_model'] for item in strategies}) >= 2


def test_fraction_has_equal_whole_equivalent_and_number_line_strategies():
    strategies = v0300._strategy_set(question('fraction_compare', 'Compare 3/4 and 5/8.'))
    assert [item['id'] for item in strategies] == ['equal-wholes', 'equivalent', 'number-line']


def test_visual_reason_connects_model_to_calculation():
    assert 'jumps' in v0300.visual_reason('number-line').lower()
    assert 'equal-sized wholes' in v0300.visual_reason('fractions').lower()
    assert 'regrouping' in v0300.visual_reason('place-value').lower()


def test_parent_test_visual_payload_restricts_teaching_aids():
    q = question('fraction_compare', 'Compare 3/4 and 5/8.')
    ws = legacy.Worksheet(session_kind='parent_test')
    payload = v0300._safe_visual_payload(q, ws)
    assert payload['assessment_restricted'] is True
    assert payload['teaching_visual_available'] is False
    assert 'teaching_example' not in payload


def test_corrective_v0291_grid_guard_remains_available():
    q = question('VC2M4SP03:grid_references', 'A treasure is at column A, row 6. Write its grid reference.', 'A6', 'space')
    v0300.v0291.ensure_grid_visual(q)
    payload = json.loads(q.payload)
    assert payload['visual']['type'] == 'grid'
    assert payload['visual']['target'] == 'A6'


def test_corrective_v0291_grouped_unit_clarity_remains_available():
    q = question('mathematical_modelling', 'There are 9 packs with 7 meal portions in each. After 6 are used for hikers, how many remain?', '57')
    v0300.v0291.clarify_grouped_units(q)
    assert '6 meal portions are used' in q.prompt
    assert q.prompt.endswith('how many meal portions remain?')
