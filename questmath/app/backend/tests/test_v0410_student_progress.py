from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0410, v090


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-v0410', password_hash='x', role='student', display_name='Sienna')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=10, adaptive_mode=True, enabled_topics=json.dumps(legacy.LEVEL4_STRANDS), manual_levels='{}'))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.add(legacy.Worksheet(student_id=student.id, worksheet_date=date.today() - timedelta(days=20), total=0, selected_topic='number_algebra', session_kind='diagnostic', status='completed', completed_at=datetime.utcnow() - timedelta(days=20)))
    session.commit()

    def test_db():
        yield session

    v0410.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0410.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session, student


def add_evidence(session: Session, student: legacy.User, *, when: datetime, code='VC2M4N06', skill='written_subtraction', first_correct=True, final_correct=None, hints=0, seconds=20, confidence=None):
    worksheet = legacy.Worksheet(student_id=student.id, worksheet_date=when.date(), total=1, selected_topic='number', completed_at=when, status='completed', score=int(bool(final_correct if final_correct is not None else first_correct)))
    session.add(worksheet); session.flush()
    question = legacy.Question(worksheet_id=worksheet.id, topic='number', skill=f'{code}:{skill}', level=4, prompt='Evidence', answer_type='number', payload='{}', correct_answer='10', working='Work carefully.', position=0, state='answered_correct' if (final_correct if final_correct is not None else first_correct) else 'answered_incorrect', hint_count=hints, answered_at=when)
    session.add(question); session.flush()
    session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer='10' if first_correct else '9', correct=first_correct, attempt_number=1, seconds=seconds, created_at=when))
    if final_correct is True and not first_correct:
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer='10', correct=True, attempt_number=2, seconds=seconds + 8, created_at=when))
    if confidence:
        session.add(v090.ConfidenceEvent(question_id=question.id, student_id=student.id, confidence=confidence, created_at=when))
    session.commit()


def close(session: Session):
    v0410.app.dependency_overrides.clear(); session.close()


def outcome(session: Session, student: legacy.User):
    return next(item for item in v0410.v0230.outcome_mastery(session, student.id) if item['code'] == 'VC2M4N06')


def test_insufficient_evidence_is_not_failure():
    _, session, student = make_client()
    add_evidence(session, student, when=datetime.utcnow(), first_correct=False, final_correct=False)
    state = v0410.student_learning_state(session, student.id, outcome(session, student))
    assert state['key'] == 'not_enough_evidence'
    assert 'failure' not in state['message'].lower()
    close(session)


def test_repeated_independent_success_can_be_ready_for_challenge():
    _, session, student = make_client(); now = datetime.utcnow()
    for index in range(7):
        add_evidence(session, student, when=now - timedelta(hours=index), first_correct=True, hints=0, seconds=18)
    state = v0410.student_learning_state(session, student.id, outcome(session, student))
    assert state['key'] == 'ready_for_challenge'
    assert state['evidence']['independent_accuracy'] >= 82
    assert state['evidence']['support_dependency'] <= 25
    close(session)


def test_supported_success_becomes_building_confidence_not_failure():
    _, session, student = make_client(); now = datetime.utcnow()
    for index in range(6):
        add_evidence(session, student, when=now - timedelta(hours=index), first_correct=False, final_correct=True, hints=1, seconds=42)
    state = v0410.student_learning_state(session, student.id, outcome(session, student))
    assert state['key'] == 'building_confidence'
    assert 'help' in state['message'].lower()
    close(session)


def test_review_due_uses_existing_spaced_retrieval_evidence():
    _, session, student = make_client(); now = datetime.utcnow()
    for days in (18, 15, 12, 9, 6, 3):
        add_evidence(session, student, when=now - timedelta(days=days), first_correct=True, hints=0, seconds=20)
    item = outcome(session, student)
    assert item['review_due'] is True
    state = v0410.student_learning_state(session, student.id, item)
    assert state['key'] == 'review_due'
    close(session)


def test_recommendation_explanation_matches_review_and_prerequisite_modes():
    _, session, student = make_client(); now = datetime.utcnow()
    for days in (10, 8, 6):
        add_evidence(session, student, when=now - timedelta(days=days), code='VC2M4A01', skill='unknown_add_subtract', first_correct=False, final_correct=False, seconds=55)
    snapshot = v0410.student_progress_snapshot(session, student.id)
    assert snapshot['recommendation']['mode'] == 'guided'
    assert snapshot['recommendation']['prerequisite_for'] == 'VC2M4A01'
    assert 'supports' in snapshot['recommendation_explanation']['text'].lower()
    close(session)


def test_student_progress_endpoint_and_capabilities_do_not_create_parallel_mastery():
    client, session, student = make_client()
    response = client.get('/api/learning/student-progress-v0410')
    assert response.status_code == 200
    payload = response.json()
    assert 'learning_now' in payload
    assert all('mastery' not in row['state'] for row in payload['learning_now'])
    caps = client.get('/api/v0410/capabilities').json()
    assert caps['no_parallel_mastery_score'] is True
    assert caps['reuses_outcome_mastery'] is True
    assert caps['reuses_adaptive_progression'] is True
    close(session)
