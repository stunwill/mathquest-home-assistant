from __future__ import annotations

import json

from app import main as legacy
from app import v0301


def question(skill: str, prompt: str, answer: str = 'yes', topic: str = 'probability') -> legacy.Question:
    return legacy.Question(
        skill=skill,
        prompt=prompt,
        correct_answer=answer,
        payload='{}',
        topic=topic,
        level=1,
        answer_type='choice',
        working='',
        position=0,
    )


def test_parameter_variants_share_probability_question_family():
    first = question('VC2M4P02:repeated_chance', 'A coin was tossed 100 times: 60 heads and 40 tails. Is variation from exactly 50 each normal?')
    second = question('VC2M4P02:repeated_chance', 'A coin was tossed 100 times: 58 heads and 42 tails. Is variation from exactly 50 each normal?')
    assert v0301.question_family(first) == 'probability:coin_toss_variation'
    assert v0301.question_family(second) == 'probability:coin_toss_variation'


def test_fraction_number_line_uses_denominator_as_equal_intervals():
    q = question('VC2M4N04:fraction_number_line', 'Select the point that represents 8/10 on the number line.', '8', 'number')
    visual = v0301._fraction_number_line_visual(q)
    assert visual is not None
    assert visual['min'] == 0
    assert visual['max'] == 1
    assert visual['steps'] == 10
    assert visual['marker'] == 0.8
    assert visual['fraction'] == {'numerator': 8, 'denominator': 10}


def test_fraction_number_line_generalises_to_other_denominators():
    for prompt, numerator, denominator in [
        ('Select the point that represents 3/4 on the number line.', 3, 4),
        ('Select the point that represents 5/8 on the number line.', 5, 8),
        ('Select the point that represents 7/10 on the number line.', 7, 10),
    ]:
        q = question('VC2M4N04:fraction_number_line', prompt, str(numerator), 'number')
        visual = v0301._fraction_number_line_visual(q)
        assert visual is not None
        assert visual['steps'] == denominator
        assert visual['marker'] == numerator / denominator


def test_probability_visual_support_does_not_offer_number_line():
    q = question('VC2M4P02:repeated_chance', 'A coin was tossed 100 times: 62 heads and 38 tails. Is variation from exactly 50 each normal?')
    assert v0301.visual_model_for(q) == 'probability'
    payload = v0301.safe_visual_payload(q, None)
    assert payload['recommended_model'] == 'probability'
    assert payload['teaching_visual_available'] is False
    assert 'number-line' not in json.dumps(payload)
    assert 'jumps on the number line' not in str(payload).lower()


def test_summary_uses_learner_history_fields(monkeypatch):
    ws = legacy.Worksheet(session_kind='practice', score=6, total=6, xp_earned=110)
    user = legacy.User(id=7, role='student', xp=1000, username='student', password_hash='x', display_name='Student')

    monkeypatch.setattr(v0301, '_prior_summary', lambda *_: {
        'strongest_topic': 'probability',
        'weakest_topic': 'probability',
    })
    monkeypatch.setattr(v0301, 'learner_summary_recommendations', lambda *_: ('Number', 'Algebra'))

    result = v0301.summary_v0301(None, ws, user)
    assert result['strongest_topic'] == 'Number'
    assert result['weakest_topic'] == 'Algebra'


def test_summary_uses_neutral_copy_when_cross_strand_evidence_is_insufficient(monkeypatch):
    outcomes = [
        {'strand': 'Probability', 'questions': 6, 'mastery': 100, 'independent_accuracy': 100, 'code': 'VC2M4P02'},
        {'strand': 'Number', 'questions': 0, 'mastery': 0, 'independent_accuracy': None, 'code': 'VC2M4N04'},
    ]
    monkeypatch.setattr(v0301.v0230, 'outcome_mastery', lambda *_: outcomes)
    assert v0301.learner_summary_recommendations(None, 1) == ('Keep exploring', 'More practice needed')
