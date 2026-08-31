from __future__ import annotations

import json
import random

from app import main, v0360


def _question(prompt: str, *, skill: str = 'VC2M5N04:written_addition', payload: dict | None = None):
    return main.Question(
        worksheet_id=1,
        topic='number',
        skill=skill,
        level=3,
        prompt=prompt,
        answer_type='number',
        payload=json.dumps(payload or {}),
        correct_answer='48',
        working='',
        position=0,
    )


def test_interactive_number_line_is_a_first_class_answer_type():
    generated = v0360._number_line_question(random.Random(12))
    skill_key, prompt, answer_type, payload, answer, working = generated
    code, skill = skill_key.split(':', 1)
    visual = payload['visual']
    target_index = (int(answer) - int(visual['min'])) // int(visual['interval'])

    assert code == 'VC2M4N02'
    assert skill == 'number_line_location'
    assert prompt == f'Select {answer} on the number line.'
    assert answer_type == 'number_line'
    assert visual['interactive'] is True
    assert target_index not in visual['label_indices']
    assert payload['number_line_selection']['interval'] == visual['interval']
    assert str(answer) not in working


def test_simple_two_digit_addition_detects_real_usage_example():
    assert v0360._simple_two_digit_addition(_question('Calculate 20 + 28.')) is True
    assert v0360._simple_two_digit_addition(_question('Calculate 327 + 286.')) is False
    assert v0360._simple_two_digit_addition(_question('□ + 28 = 73.', skill='VC2M5A01:missing_number')) is False


def test_purposeful_foundation_is_preserved_for_review_and_retrieval():
    review = _question('Calculate 20 + 28.', payload={'learning_purpose': 'review'})
    retrieval = _question('Calculate 20 + 28.', payload={'retrieval_item': {'reason': 'spaced review'}})
    current = _question('Calculate 20 + 28.', payload={'learning_purpose': 'current'})

    assert v0360._purposeful_foundation(review) is True
    assert v0360._purposeful_foundation(retrieval) is True
    assert v0360._purposeful_foundation(current) is False


def test_number_line_generator_never_labels_the_requested_internal_tick():
    for seed in range(100):
        _, _, answer_type, payload, answer, _ = v0360._number_line_question(random.Random(seed))
        visual = payload['visual']
        target_index = (int(answer) - int(visual['min'])) // int(visual['interval'])
        assert answer_type == 'number_line'
        assert 0 < target_index < int(visual['steps'])
        assert target_index not in visual['label_indices']
