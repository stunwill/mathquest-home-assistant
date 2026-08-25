from __future__ import annotations

from app import v0320


def test_mastery_requires_enough_evidence():
    assert v0320._status(1, 1.0, 1.0, 0.0, False) == 'not_enough_evidence'
    assert v0320._status(4, 1.0, 1.0, 0.0, False) == 'secure'


def test_supported_success_does_not_overstate_mastery():
    assert v0320._status(8, 0.45, 0.95, 0.75, False) == 'needs_support'
    assert v0320._difficulty_state(8, 0.45, 0.95, 0.75) != 'ready_for_more_challenge'


def test_review_due_is_distinct_from_needs_support():
    assert v0320._status(8, 0.9, 0.9, 0.1, True) == 'review_due'


def test_evidence_confidence_thresholds_are_conservative():
    assert v0320._evidence_confidence(2) == 'limited'
    assert v0320._evidence_confidence(6) == 'moderate'
    assert v0320._evidence_confidence(12) == 'strong'


def test_recommendations_prioritise_repeated_misconceptions():
    skills = [{
        'skill': 'number:written_subtraction',
        'label': 'Subtraction with decomposition',
        'status': 'needs_support',
        'first_attempt_accuracy': 40,
        'support_dependency': 70,
    }]
    misconceptions = [{
        'skill': 'number:written_subtraction',
        'skill_label': 'Subtraction with decomposition',
        'label': 'Regrouping Error',
        'count': 3,
    }]
    recs = v0320._recommendations(skills, misconceptions)
    assert recs[0]['priority'] == 'high_priority'
    assert '3 times' in recs[0]['reason']


def test_summary_does_not_fabricate_evidence():
    assert 'Not enough recent evidence' in v0320._summary([], [])[0]
