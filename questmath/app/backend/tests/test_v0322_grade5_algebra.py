from __future__ import annotations

import json
import random
import re

from app import main as legacy
from app import v0310, v0321, v0322


def generated(generator, seed=1):
    skill, prompt, answer_type, payload, answer, working = generator(random.Random(seed))
    question = legacy.Question(
        worksheet_id=1,
        topic='algebra',
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type=answer_type,
        payload=json.dumps(payload),
        correct_answer=str(answer),
        working=working,
        position=0,
    )
    return question, payload, int(answer)


def test_increasing_and_decreasing_patterns_are_generated():
    samples = [v0322._pattern(random.Random(seed)) for seed in range(100)]
    prompts = [item[1] for item in samples]
    assert any('Continue the pattern' in prompt for prompt in prompts)
    modes = {item[3]['pattern_rule'] for item in samples}
    assert {'add', 'subtract'} <= modes


def test_pattern_answers_follow_the_generated_rule():
    for seed in range(100):
        _, prompt, _, payload, answer, _ = v0322._pattern(random.Random(seed))
        values = [int(value) for value in re.findall(r'\d+', prompt)[:4]]
        if payload['pattern_rule'] == 'add':
            assert int(answer) == values[-1] + (values[1] - values[0])
        elif payload['pattern_rule'] == 'subtract':
            assert int(answer) == values[-1] - (values[0] - values[1])
        else:
            assert int(answer) == values[-1] * (values[1] // values[0])


def test_addition_and_subtraction_unknowns_are_whole_number_valid():
    for generator in (v0322._addition_unknown, v0322._subtraction_unknown):
        for seed in range(80):
            question, _, answer = generated(generator, seed)
            assert answer > 0
            numbers = [int(value) for value in re.findall(r'\d+', question.prompt)]
            assert numbers
            assert question.answer_type == 'number'


def test_substitution_questions_use_supplied_variable_value():
    for generator in (v0322._substitution_add, v0322._substitution_multiply):
        for seed in range(50):
            question, payload, answer = generated(generator, seed)
            value = payload['variable_value']
            assert str(value) in question.prompt
            if generator is v0322._substitution_add:
                other = [int(x) for x in re.findall(r'\d+', question.prompt)][-1]
                assert answer == value + other
            else:
                numbers = [int(x) for x in re.findall(r'\d+', question.prompt)]
                factor = numbers[-1] if numbers[-1] != value else numbers[-2]
                assert answer == value * factor


def test_contextual_unknowns_and_reverse_multiplication_have_sensible_answers():
    for seed in range(100):
        _, _, start = generated(v0322._unknown_start_context, seed)
        assert 1 <= start <= 60
        question, payload, original = generated(v0322._reverse_multiplication, seed)
        result = max(int(value) for value in re.findall(r'\d+', question.prompt))
        assert result == original * payload['factor']
        assert 2 <= payload['factor'] <= 6
        assert 2 <= original <= 12


def test_new_question_structures_are_distinct_families():
    families = set()
    for index, generator in enumerate(v0322.NEW_GENERATORS):
        question, _, _ = generated(generator, index + 10)
        families.add(v0322.question_family_v0322(question))
    assert len(families) == len(v0322.NEW_GENERATORS)


def test_new_pool_supplements_existing_algebra_instead_of_replacing_it():
    rng = random.Random(1234)
    skills = [v0322.make_question_v0322('algebra', 4, rng)[0].split(':', 1)[-1] for _ in range(300)]
    new_count = sum(skill.startswith('grade5_') for skill in skills)
    assert 80 <= new_count <= 180
    assert any(not skill.startswith('grade5_') for skill in skills)


def test_grade5_algebra_generation_does_not_leak_into_other_topics_or_low_levels():
    for seed in range(30):
        number_skill = v0322.make_question_v0322('number', 4, random.Random(seed))[0]
        low_algebra_skill = v0322.make_question_v0322('algebra', 2, random.Random(seed))[0]
        assert ':grade5_' not in number_skill
        assert ':grade5_' not in low_algebra_skill


def test_hints_are_structure_specific_and_do_not_reveal_answer():
    for index, generator in enumerate(v0322.NEW_GENERATORS):
        question, _, answer = generated(generator, index + 20)
        content = v0322.tutoring_content_v0322(question)
        assert len(content['hints']) == 3
        assert all(str(answer) not in hint for hint in content['hints'])
        assert content['strategy']


def test_worked_examples_match_structure_and_use_different_values():
    for index, generator in enumerate(v0322.NEW_GENERATORS):
        question, _, answer = generated(generator, index + 40)
        example = v0322.aligned_worked_example_v0322(question)
        assert example
        assert question.prompt not in example
        assert f'answer is {answer}' not in example.lower()
        assert f'= {answer}' not in example
        skill = question.skill.split(':', 1)[-1]
        if 'substitution' in skill:
            assert 'substitution' in example.lower() or 'becomes' in example.lower()
        if 'reverse_multiplication' in skill:
            assert 'division' in example.lower()


def test_math_mentor_uses_new_tutoring_content_and_worked_example():
    question, _, _ = generated(v0322._subtraction_unknown, 77)
    content = v0310.tutoring_content(question)
    assert 'undo' in ' '.join(content['hints']).lower()
    example = v0321.aligned_worked_example(question)
    assert 'different equation' in example.lower()


def test_generated_sample_is_well_formed():
    for seed in range(500):
        skill, prompt, answer_type, payload, answer, working = v0322.make_question_v0322('algebra', 4, random.Random(seed))
        assert skill and prompt and working
        assert answer_type in {'number', 'text', 'choice', 'money'}
        assert str(answer).strip()
        assert isinstance(payload, dict)
        if ':grade5_' in skill:
            assert payload['grade_band'] == 5
            assert int(answer) >= 0
