from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0190, v0230, v0330, v0340, v0440


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-v0440', password_hash='x', role='student', display_name='Sienna')
    parent = legacy.User(username='parent-v0440', password_hash='x', role='parent', display_name='Parent')
    session.add_all([student, parent]); session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=10, adaptive_mode=True, enabled_topics='["number","algebra","measurement","space","statistics","probability"]', manual_levels='{}'))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()
    def test_db(): yield session
    v0440.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0440.app), session, student, parent


def close(session):
    v0440.app.dependency_overrides.clear(); session.close()


def complete_diagnostic(client, session, student, answers=(True, True, True, True, False, False)):
    response = client.post('/api/sessions/new', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}, json={'kind':'diagnostic','minutes':15,'topic':'number_algebra'})
    assert response.status_code == 200
    worksheet = session.get(legacy.Worksheet, response.json()['id'])
    for index, question in enumerate(sorted(worksheet.questions, key=lambda item: item.position)):
        answer = question.correct_answer if answers[index] else '__wrong__'
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer=answer, correct=answers[index], attempt_number=1, seconds=20, created_at=datetime.utcnow()))
        question.answered_at = datetime.utcnow(); question.state = 'answered_correct' if answers[index] else 'answered_incorrect'
    worksheet.completed_at = datetime.utcnow(); worksheet.status = 'completed'; worksheet.score = sum(answers)
    session.commit(); return worksheet


def test_session_plan_reuses_existing_recommendation_and_has_primary_target(monkeypatch):
    _, session, student, _ = make_client()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':2,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':10,'topic':'number','outcome_code':'VC2M4N06','title':'Practice Efficient calculation strategies','reason':'More evidence needed','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    plan = v0440.build_learning_plan(session, student.id)
    assert plan['kind'] == 'targeted'
    assert plan['primary_target']['outcome_code'] == 'VC2M4N06'
    assert plan['primary_target']['skill'] == 'written_subtraction'
    assert plan['purpose'] == 'learn'
    assert plan['stages'][0] == 'reconnect' and plan['stages'][-1] == 'check'
    close(session)


def test_prerequisite_and_review_purposes_follow_existing_recommendation(monkeypatch):
    _, session, student, _ = make_client()
    base = {'code':'VC2M4N03','title':'Equivalent fractions and decimals','topic':'number','questions':6,'status':'developing','review_due':False,'target_skill':'equivalent_fractions'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: [base])
    prereq = {'mode':'guided','minutes':5,'topic':'number','outcome_code':'VC2M4N03','title':'Build fraction foundations','reason':'Prerequisite','prerequisite_for':'VC2M4A02','target_skill':'equivalent_fractions'}
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: prereq)
    assert v0440.build_learning_plan(session, student.id)['purpose'] == 'prerequisite'
    review = {**prereq, 'mode':'review', 'prerequisite_for':None}
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: review)
    assert v0440.build_learning_plan(session, student.id)['purpose'] == 'review'
    close(session)


def test_recommended_session_is_composed_around_target_skill(monkeypatch):
    _, session, student, _ = make_client()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Practice Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    plan = v0440.build_learning_plan(session, student.id, 5)
    worksheet = v0440.compose_targeted_session(session, student.id, plan)
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    target_count = sum('written_subtraction' in item.skill for item in questions)
    assert target_count >= 3
    metadata = [json.loads(item.payload)['targeted_session'] for item in questions]
    assert metadata[0]['stage'] == 'reconnect'
    assert metadata[-1]['stage'] == 'check'
    identities = [legacy.question_identity(item.prompt, json.loads(item.payload)) for item in questions]
    assert len(identities) == len(set(identities))
    close(session)


def test_support_early_then_independent_later_is_recognised(monkeypatch):
    _, session, student, _ = make_client()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Practice Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    worksheet = v0440.compose_targeted_session(session, student.id, v0440.build_learning_plan(session, student.id, 5))
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    for index, question in enumerate(questions):
        question.state = 'answered_correct'; question.answered_at = datetime.utcnow()
        if index == 0: question.hint_count = 1
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer=question.correct_answer, correct=True, attempt_number=1, seconds=10))
    session.commit()
    summary = v0440.targeted_session_summary(session, worksheet, student.id)
    assert summary['available'] is True
    assert 'support earlier' in summary['message'].lower()
    assert summary['support_used'] == 1
    close(session)


def test_completed_diagnostic_leads_to_normal_targeted_plan_not_retest():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student)
    plan = v0440.build_learning_plan(session, student.id)
    assert plan['kind'] == 'targeted'
    assert plan['primary_target']['skill']
    assert not plan['primary_target']['skill'].startswith('diagnostic_')
    close(session)


def test_short_diagnostic_still_cannot_manufacture_challenge_readiness():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student, answers=(True,True,True,True,True,True))
    level5 = v0330._question_evidence(session, student.id, 'VC2M5N06:diagnostic_operations')
    level6 = v0330._question_evidence(session, student.id, 'VC2M6N03:diagnostic_fraction_decimal')
    assert v0330.THRESHOLDS.minimum_questions == 6
    assert v0330.THRESHOLDS.ready_accuracy == .82
    assert v0330.THRESHOLDS.ready_support == .25
    assert v0330._progression_state(level5) == 'not_ready'
    assert v0330._progression_state(level6) == 'not_ready'
    close(session)


def test_student_plan_hides_curriculum_code_parent_plan_keeps_detail(monkeypatch):
    client, session, student, parent = make_client()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':3,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Practice Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    student_data = client.get('/api/learning/session-plan-v0440', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}).json()
    parent_data = client.get('/api/learning/session-plan-v0440', headers={'Authorization': f'Bearer {legacy.token_for(parent)}'}).json()
    assert 'VC2M' not in str(student_data)
    assert parent_data['primary_target']['outcome_code'] == 'VC2M4N06'
    close(session)


def test_story_presentation_preserves_targeted_learning_metadata(monkeypatch):
    _, session, student, _ = make_client()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Practice Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: recommendation)
    worksheet = v0440.compose_targeted_session(session, student.id, v0440.build_learning_plan(session, student.id, 5))
    before = [json.loads(item.payload)['targeted_session']['target_skill'] for item in worksheet.questions]
    theme = v0340.ADVENTURE_THEMES[0]
    v0340.apply_adventure_presentation(session, worksheet, theme)
    after = [json.loads(item.payload)['targeted_session']['target_skill'] for item in worksheet.questions]
    assert before == after
    assert all(value == 'written_subtraction' for value in after)
    close(session)
