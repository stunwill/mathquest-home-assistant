from __future__ import annotations

import json
import random

from app import main, v0370


def _unpack(generated):
    skill, prompt, answer_type, payload, answer, working = generated
    return skill, prompt, answer_type, payload, answer, working


def _question(*, topic='number', skill='VC2M4N06:written_addition', prompt='Calculate 327 + 286.', payload=None):
    return main.Question(
        worksheet_id=1,
        topic=topic,
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type='number',
        payload=json.dumps(payload or {}),
        correct_answer='613',
        working='',
        position=0,
    )


def test_fraction_bar_is_first_class_interactive_answer():
    skill, prompt, answer_type, payload, answer, working = _unpack(v0370._fraction_bar_question(random.Random(3)))
    visual = payload['visual']
    assert skill.startswith('VC2M4N03:fraction_bar_selection')
    assert answer_type == 'fraction_bar'
    assert visual['type'] == 'fraction_bar_select'
    assert visual['interactive'] is True
    assert 1 <= int(answer) < int(visual['denominator'])
    assert prompt.startswith('Shade ')
    assert 'equal parts' in working


def test_fraction_number_line_hides_requested_fraction_tick():
    for seed in range(40):
        skill, prompt, answer_type, payload, answer, _ = _unpack(v0370._fraction_number_line_question(random.Random(seed)))
        visual = payload['visual']
        assert skill.startswith('VC2M4N04:fraction_number_line_location')
        assert answer_type == 'fraction_number_line'
        assert visual['label_indices'] == [0, visual['denominator']]
        assert int(answer) not in visual['label_indices']
        assert prompt.startswith('Select ')


def test_ruler_scale_is_mathematically_consistent_and_target_unlabelled():
    for seed in range(50):
        _, prompt, answer_type, payload, answer, _ = _unpack(v0370._ruler_question(random.Random(seed)))
        visual = payload['visual']
        interval = int(visual['interval'])
        target_index = int(answer) // interval
        assert answer_type == 'ruler'
        assert int(answer) == target_index * interval
        assert 0 < target_index < int(visual['steps'])
        assert target_index not in visual['label_indices']
        assert prompt.endswith('cm on the ruler.')


def test_grid_selection_uses_column_then_row_reference():
    _, prompt, answer_type, payload, answer, working = _unpack(v0370._grid_selection_question(random.Random(11)))
    assert answer_type == 'grid_select'
    assert answer[0] in payload['visual']['columns']
    assert 1 <= int(answer[1:]) <= payload['visual']['rows']
    assert answer in prompt
    assert 'column' in working.lower() and 'row' in working.lower()


def test_reasoning_questions_have_structured_choices_and_correct_answer():
    for topic in ('number', 'algebra', 'measurement', 'space'):
        for seed in range(20):
            _, _, answer_type, payload, answer, _ = _unpack(v0370._reasoning_question(topic, random.Random(seed)))
            assert answer_type == 'choice'
            assert payload.get('reasoning_type')
            assert str(answer) in [str(choice) for choice in payload['choices']]


def test_error_analysis_reuses_named_misconception_evidence():
    generated = None
    for seed in range(100):
        candidate = v0370._reasoning_question('number', random.Random(seed))
        if candidate[3].get('reasoning_type') == 'error_analysis':
            generated = candidate
            break
    assert generated is not None
    skill, prompt, answer_type, payload, answer, working = generated
    q = _question(skill=skill, prompt=prompt, payload=payload)
    q.answer_type = answer_type
    q.correct_answer = str(answer)
    q.working = working
    misconception, explanation = v0370.misconception_v0370(q, 'wrong choice')
    assert misconception == 'place_value_regrouping'
    assert 'regrouping' in explanation.lower()


def test_parent_test_mix_is_not_modified():
    class Worksheet:
        session_kind = 'parent_test'
        questions = []
    worksheet = Worksheet()
    assert v0370.apply_v0370_mix(None, worksheet, 1) is worksheet


def test_v0370_mentor_uses_different_number_worked_examples():
    skill, prompt, answer_type, payload, answer, working = _unpack(v0370._fraction_number_line_question(random.Random(2)))
    q = _question(skill=skill, prompt=prompt, payload=payload)
    q.answer_type = answer_type
    q.correct_answer = str(answer)
    q.working = working
    result = v0370.mentor_payload_v0370(q, 'worked_example')
    assert 'Example:' in result['worked_example']
    assert prompt not in result['worked_example']
    assert result['visual_connection']


def test_generator_is_deterministic_for_same_seed():
    first = v0370.make_question_v0370('measurement', 4, random.Random(1234))
    second = v0370.make_question_v0370('measurement', 4, random.Random(1234))
    assert first == second


def test_reasoning_mix_preserves_question_identity_uniqueness():
    class FakeSession:
        def commit(self):
            pass

        def refresh(self, worksheet):
            pass

    class FakeWorksheet:
        id = 42
        session_kind = 'practice'

        def __init__(self, questions):
            self.questions = questions

    first = _question(prompt='Calculate 327 + 286.')
    first.id = 1
    second = _question(prompt='Calculate 96 − 23.')
    second.id = 2
    second.topic = 'number'
    second.skill = 'VC2M4N06:written_subtraction'
    second.correct_answer = '73'
    worksheet = FakeWorksheet([first, second])
    duplicate = ('VC2M4N06:written_subtraction', second.prompt, 'number', {}, second.correct_answer, 'work')

    original = v0370._reasoning_question
    try:
        v0370._reasoning_question = lambda topic, rng: duplicate
        v0370.apply_v0370_mix(FakeSession(), worksheet, 1)
    finally:
        v0370._reasoning_question = original

    identities = [main.stored_question_identity(question) for question in worksheet.questions]
    assert len(identities) == len(set(identities))
    assert first.prompt == 'Calculate 327 + 286.'
