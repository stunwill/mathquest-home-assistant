from types import SimpleNamespace

from app import v0130


def question(prompt, skill, payload='{}', hint_count=1):
    return SimpleNamespace(prompt=prompt, skill=skill, payload=payload, hint_count=hint_count)


def test_fraction_comparison_builds_two_pie_models_without_answer():
    q = question('Which is larger: 2/3 or 4/5?', 'VC2M4N03:equivalent_fractions')
    visual = v0130.visual_hint_for(q, 1)
    assert visual['type'] == 'fraction_pies'
    assert visual['items'] == [
        {'numerator': 2, 'denominator': 3, 'label': '2/3'},
        {'numerator': 4, 'denominator': 5, 'label': '4/5'},
    ]
    assert visual['show_bars'] is False
    assert 'correct_answer' not in visual


def test_second_fraction_hint_adds_aligned_fraction_bars():
    q = question('Compare 3/4 with 5/8.', 'VC2M4N03:equivalent_fractions', hint_count=2)
    visual = v0130.visual_hint_for(q, 2)
    assert visual['type'] == 'fraction_pies'
    assert visual['show_bars'] is True
    assert visual['hint_level'] == 2


def test_single_fraction_can_be_visualised_without_revealing_missing_value():
    q = question('2/3 = ?/6', 'VC2M4N03:equivalent_fractions')
    visual = v0130.visual_hint_for(q, 1)
    assert visual['type'] == 'fraction_pie'
    assert visual['item']['label'] == '2/3'


def test_visual_payload_number_line_is_reused():
    q = question('Where is the fraction?', 'VC2M4N04:fraction_number_line', '{"visual":{"type":"number_line","min":0,"max":1,"steps":8}}')
    visual = v0130.visual_hint_for(q, 1)
    assert visual == {
        'type': 'number_line',
        'hint_level': 1,
        'min': 0,
        'max': 1,
        'steps': 8,
        'instruction': 'Count the equal spaces first, then locate the value one step at a time.',
    }


def test_decimal_place_value_visual():
    q = question('What is the hundredths digit in 7.42?', 'VC2M4N01:decimal_place_value')
    visual = v0130.visual_hint_for(q, 1)
    assert visual['type'] == 'place_value'
    assert visual['value'] == '7.42'
    assert [x['digit'] for x in visual['digits']] == ['7', '4', '2']


def test_angle_visual_from_prompt():
    q = question('Classify the 120° angle.', 'VC2M4M04:angle_names')
    visual = v0130.visual_hint_for(q, 1)
    assert visual['type'] == 'angle'
    assert visual['degrees'] == 120


def test_unknown_question_returns_no_visual_instead_of_failing():
    q = question('Explain your reasoning.', 'VC2M4N10:mathematical_modelling')
    assert v0130.visual_hint_for(q, 1) is None


def test_v0130_api_is_before_spa_fallback_when_present():
    paths = [getattr(route, 'path', None) for route in v0130.app.router.routes]
    assert '/api/questions/{qid}/hint-visual' in paths
    assert '/api/v0130/capabilities' in paths
    if '/{path:path}' in paths:
        fallback = paths.index('/{path:path}')
        assert paths.index('/api/questions/{qid}/hint-visual') < fallback
        assert paths.index('/api/v0130/capabilities') < fallback
