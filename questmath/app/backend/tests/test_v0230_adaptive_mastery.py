from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0230, v090


def make_client(*, diagnostic_complete: bool = True):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-adaptive', password_hash='x', role='student', display_name='Sienna')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(
        student_id=student.id, question_count=10, adaptive_mode=True,
        enabled_topics=json.dumps(legacy.LEVEL4_STRANDS), manual_levels='{}',
    ))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    if diagnostic_complete:
        session.add(legacy.Worksheet(
            student_id=student.id, worksheet_date=date.today() - timedelta(days=14), total=0,
            selected_topic='number_algebra', session_kind='diagnostic', status='completed',
            completed_at=datetime.utcnow() - timedelta(days=14),
        ))
    session.commit()

    def test_db():
        yield session

    v0230.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0230.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session, student


def add_evidence(session: Session, student: legacy.User, *, code: str, skill: str,
                 when: datetime, first_correct: bool, final_correct: bool | None = None,
                 hints: int = 0, seconds: float = 20, confidence: str | None = None):
    worksheet = legacy.Worksheet(
        student_id=student.id, worksheet_date=when.date(), total=1, selected_topic='number',
        completed_at=when, status='completed', score=int(bool(final_correct if final_correct is not None else first_correct)),
    )
    session.add(worksheet)
    session.flush()
    question = legacy.Question(
        worksheet_id=worksheet.id, topic='algebra' if 'A' in code else 'number', skill=f'{code}:{skill}',
        level=4, prompt='Adaptive evidence question', answer_type='number', payload='{}',
        correct_answer='10', working='Use the relevant strategy.', position=0,
        state='answered_correct' if (final_correct if final_correct is not None else first_correct) else 'answered_incorrect',
        hint_count=hints, answered_at=when,
    )
    session.add(question)
    session.flush()
    session.add(legacy.Attempt(
        question_id=question.id, student_id=student.id, answer='10' if first_correct else '9',
        correct=first_correct, attempt_number=1, seconds=seconds, created_at=when,
    ))
    if final_correct is True and not first_correct:
        session.add(legacy.Attempt(
            question_id=question.id, student_id=student.id, answer='10', correct=True,
            attempt_number=2, seconds=seconds + 8, created_at=when,
        ))
    if confidence:
        session.add(v090.ConfidenceEvent(
            question_id=question.id, student_id=student.id, confidence=confidence, created_at=when,
        ))
    session.commit()
    return question


def close(session: Session):
    v0230.app.dependency_overrides.clear()
    session.close()


def test_mastery_separates_independent_supported_fluency_confidence_and_retention():
    client, session, student = make_client()
    now = datetime.utcnow()
    add_evidence(session, student, code='VC2M4N06', skill='written_subtraction', when=now - timedelta(days=12), first_correct=True, seconds=18, confidence='knew_it')
    add_evidence(session, student, code='VC2M4N06', skill='written_subtraction', when=now - timedelta(days=9), first_correct=False, final_correct=True, hints=1, seconds=52, confidence='pretty_sure')
    add_evidence(session, student, code='VC2M4N06', skill='written_subtraction', when=now - timedelta(days=6), first_correct=False, final_correct=False, seconds=31, confidence='knew_it')
    add_evidence(session, student, code='VC2M4N06', skill='written_subtraction', when=now - timedelta(days=4), first_correct=True, seconds=24, confidence='knew_it')

    outcome = next(item for item in v0230.outcome_mastery(session, student.id, now) if item['code'] == 'VC2M4N06')
    assert outcome['independent_accuracy'] == 50
    assert outcome['supported_accuracy'] == 75
    assert outcome['fluency'] == 50
    assert outcome['confidence_calibration'] is not None
    assert outcome['retention_checks'] == 3
    assert outcome['next_review_due']
    assert outcome['review_due'] is True
    close(session)


def test_weak_equations_route_to_the_unsecured_calculation_prerequisite():
    client, session, student = make_client()
    now = datetime.utcnow()
    for days in (8, 6, 4):
        add_evidence(session, student, code='VC2M4A01', skill='unknown_add_subtract', when=now - timedelta(days=days), first_correct=False, final_correct=False, seconds=55, confidence='knew_it')

    snapshot = v0230.adaptive_snapshot(session, student.id)
    recommendation = snapshot['recommendation']
    assert recommendation['mode'] == 'guided'
    assert recommendation['outcome_code'] == 'VC2M4N06'
    assert recommendation['prerequisite_for'] == 'VC2M4A01'
    assert recommendation['minutes'] == 15

    response = client.post('/api/sessions/recommended')
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['session_kind'] == 'guided'
    assert worksheet['target_minutes'] == 15
    assert worksheet['recommendation']['prerequisite_for'] == 'VC2M4A01'
    assert sum(question['skill'].endswith(':written_subtraction') for question in worksheet['questions']) >= 3
    identities = [
        legacy.question_identity(question['prompt'], question['payload'])
        for question in worksheet['questions']
    ]
    assert len(identities) == len(set(identities))
    close(session)


def test_missing_diagnostic_is_the_first_recommended_session():
    client, session, student = make_client(diagnostic_complete=False)
    response = client.get('/api/learning/adaptive-v0230')
    assert response.status_code == 200
    assert response.json()['recommendation']['mode'] == 'diagnostic'
    assert response.json()['recommendation']['minutes'] == 15

    created = client.post('/api/sessions/recommended')
    assert created.status_code == 200
    assert created.json()['session_kind'] == 'diagnostic'
    assert created.json()['total'] == 6
    assert [question['level'] for question in created.json()['questions']] == [5, 5, 5, 6, 6, 6]
    close(session)


def test_v0230_capabilities_and_routes_are_available_before_spa_fallback():
    client, session, _ = make_client()
    response = client.get('/api/v0230/capabilities')
    assert response.status_code == 200
    assert response.json()['spaced_review_due_dates'] is True
    assert response.json()['prerequisite_routing'] is True
    paths = [getattr(route, 'path', None) for route in v0230.app.router.routes]
    if '/{path:path}' in paths:
        assert paths.index('/api/v0230/capabilities') < paths.index('/{path:path}')
    close(session)
