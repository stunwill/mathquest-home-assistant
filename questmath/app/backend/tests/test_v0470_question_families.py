from __future__ import annotations
import random
from app import v0170, v0470

def test_level5_family_generators_have_correct_answers():
    for topic, generators in v0470.FAMILY_GENERATORS.items():
        for skill, generator in generators.items():
            for seed in range(20):
                _, prompt, _, payload, answer, _ = generator(random.Random(seed))
                assert prompt and answer is not None
                assert payload['grade_band'] == 5
                assert payload['question_family']
                if skill in ('perimeter', 'area'):
                    assert int(answer) > 0

def test_targeted_focus_registry_has_high_value_level5_families():
    assert v0170.FOCUS_GENERATORS['number']['equivalent_fractions'] is v0470._equivalent_fraction
    assert v0170.FOCUS_GENERATORS['number']['efficient_multiply_divide'] is v0470._multiplication_family
    assert v0170.FOCUS_GENERATORS['number']['number_sequences'] is v0470._pattern_family
    assert v0170.FOCUS_GENERATORS['measurement']['area'] is v0470._measurement_family

def test_family_metadata_does_not_create_parallel_mastery():
    report = v0470.coverage_report()
    assert 'mastery' not in report
    assert all(':' in family for family in report['families'])
