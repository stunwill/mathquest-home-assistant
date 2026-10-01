from __future__ import annotations

from app import main as legacy
from app import v0230, v0440, v0450, v0460
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from datetime import datetime

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


def _session_with_student():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-v0460-persist', password_hash='x', role='student', display_name='Sienna')
    session.add(student); session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=10, adaptive_mode=True, enabled_topics='["number"]', manual_levels='{}'))
    session.commit()
    return session, student

def test_completed_targeted_decision_is_persisted_and_survives_new_session(monkeypatch):
    session, student = _session_with_student()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    worksheet = v0450.compose_targeted_session(session, student.id, v0440.build_learning_plan(session, student.id, 5))
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        question.answered_at = datetime.utcnow(); question.state = 'answered_incorrect'
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer='wrong', correct=False, attempt_number=1, seconds=10))
    worksheet.completed_at = datetime.utcnow(); worksheet.status = 'completed'
    session.commit()

    detail = v0460._detail(session, worksheet, student.id)
    assert detail['follow_through'] == 'reteach'
    persisted = session.query(v0460.AdaptiveFollowThrough).filter_by(worksheet_id=worksheet.id).one()
    assert persisted.decision == 'reteach' and persisted.consumed_at is None

    session.expunge_all()
    student = session.query(legacy.User).filter_by(username='sienna-v0460-persist').one()
    plan = v0460.build_learning_plan(session, student.id, 5)
    assert plan['previous_follow_through']['decision'] == 'reteach'
    assert plan['follow_through'] == 'reteach'
    assert 'smaller step' in plan['student_reason'].lower()
    persisted = session.query(v0460.AdaptiveFollowThrough).filter_by(worksheet_id=worksheet.id).one()
    assert persisted.consumed_at is None
    session.close()

def test_follow_through_is_consumed_only_when_matching_session_is_composed(monkeypatch):
    session, student = _session_with_student()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    worksheet = v0450.compose_targeted_session(session, student.id, v0440.build_learning_plan(session, student.id, 5))
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        question.answered_at = datetime.utcnow(); question.state = 'answered_correct'
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer=question.correct_answer, correct=True, attempt_number=1, seconds=10))
    worksheet.completed_at = datetime.utcnow(); worksheet.status = 'completed'
    session.commit()
    v0460._detail(session, worksheet, student.id)

    plan = v0460.build_learning_plan(session, student.id, 5)
    row = session.query(v0460.AdaptiveFollowThrough).filter_by(worksheet_id=worksheet.id).one()
    assert row.consumed_at is None
    v0460.compose_targeted_session(session, student.id, plan)
    session.refresh(row)
    assert row.consumed_at is not None
    session.close()
