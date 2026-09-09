from __future__ import annotations

from app import v0460

def test_follow_through_reteaches_when_support_does_not_lead_to_success():
    decision = v0460._decision_from_evidence({
        'answered': 6, 'eventual_successes': 2, 'independent_successes': 0,
        'support_used_questions': 5, 'independent_checks': 0, 'check_questions': 1,
    })
    assert decision == 'reteach'

def test_follow_through_recognises_support_to_independence():
    decision = v0460._decision_from_evidence({
        'answered': 6, 'eventual_successes': 6, 'independent_successes': 3,
        'support_used_questions': 2, 'independent_checks': 1, 'check_questions': 1,
    })
    assert decision == 'transfer'

def test_follow_through_is_conservative_about_progression():
    decision = v0460._decision_from_evidence({
        'answered': 1, 'eventual_successes': 1, 'independent_successes': 1,
        'support_used_questions': 0, 'independent_checks': 1, 'check_questions': 1,
    })
    assert decision == 'gather_more_evidence'

def test_follow_through_keeps_skill_specific_challenge():
    decision = v0460._decision_from_evidence({
        'answered': 6, 'eventual_successes': 6, 'independent_successes': 5,
        'support_used_questions': 0, 'independent_checks': 2, 'check_questions': 2,
    })
    assert decision == 'challenge'

def test_follow_through_review_does_not_erase_history():
    decision = v0460._decision_from_evidence({
        'answered': 6, 'eventual_successes': 5, 'independent_successes': 4,
        'support_used_questions': 0, 'independent_checks': 1, 'check_questions': 1,
    }, purpose='review')
    assert decision == 'review_later'
