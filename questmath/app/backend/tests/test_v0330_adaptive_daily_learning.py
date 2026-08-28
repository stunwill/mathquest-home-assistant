from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0290, v0330


def make_session():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='adaptive-student', password_hash='x', role='student', display_name='Adaptive Learner')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=6, adaptive_mode=True, enabled_topics='["number"]', manual_levels='{}'))
    session.commit()
    return session, student


def add_question(session: Session, student: legacy.User, *, skill='VC2M4N06:written_addition', correct=True, supported=False, days_ago=0):
    ws = legacy.Worksheet(student_id=student.id, date=datetime.utcnow().date(), selected_topic='number', status='completed', completed_at=datetime.utcnow() - timedelta(days=days_ago), session_kind='practice')
    session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic='number', skill=skill, level=4, prompt='Calculate 247 + 68.', answer_type='number', payload='{}', correct_answer='315', working='work', position=0, answered_at=datetime.utcnow() - timedelta(days=days_ago), hint_count=1 if supported else 0, mentor_started=supported)
    session.add(q); session.flush()
    session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='315' if correct else '300', correct=correct, attempt_number=1, seconds=15))
    session.commit()
    return q


def test_insufficient_evidence_does_not_progress():
    session, student = make_session()
    for _ in range(3): add_question(session, student)
    evidence = v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    assert v0330._progression_state(evidence) == 'not_ready'


def test_strong_independent_evidence_progresses():
    session, student = make_session()
    for _ in range(8): add_question(session, student)
    evidence = v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    assert v0330._progression_state(evidence) == 'ready_to_progress'


def test_high_support_slows_progression():
    session, student = make_session()
    for _ in range(8): add_question(session, student, supported=True)
    evidence = v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    assert evidence['eventual'] == 1.0
    assert v0330._progression_state(evidence) != 'ready_to_progress'


def test_single_incorrect_answer_does_not_destroy_secure_trend():
    session, student = make_session()
    for _ in range(8): add_question(session, student)
    add_question(session, student, correct=False)
    evidence = v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    assert v0330._progression_state(evidence) in ('secure', 'ready_to_progress')


def test_repeated_misconception_forces_consolidation():
    session, student = make_session()
    q = add_question(session, student)
    for _ in range(2):
        session.add(v0290.MisconceptionEvidence(student_id=student.id, question_id=q.id, skill=q.skill, misconception_type='regrouping_error', message='Regrouping issue', resolved=False))
    session.commit()
    worksheet = session.get(legacy.Worksheet, q.worksheet_id)
    purpose, reason = v0330._purpose_for_question(session, student.id, q, {})
    assert purpose == 'consolidation'
    assert 'misconception' in reason.lower()


def test_parent_test_is_not_recomposed():
    session, student = make_session()
    ws = legacy.Worksheet(student_id=student.id, date=datetime.utcnow().date(), selected_topic='number', status='in_progress', session_kind='parent_test')
    session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic='number', skill='VC2M4N06:written_addition', level=4, prompt='Calculate 247 + 68.', answer_type='number', payload=json.dumps({'difficulty_band':'challenge'}), correct_answer='315', working='work', position=0)
    session.add(q); session.commit(); session.refresh(ws)
    v0330.apply_adaptive_daily_learning(session, ws, student.id)
    assert 'learning_purpose' not in json.loads(q.payload)
