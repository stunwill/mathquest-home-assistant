from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0160


def make_client(question_count: int = 12):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='route-student', password_hash='x', role='student', display_name='Route Learner')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(
        student_id=student.id,
        question_count=question_count,
        adaptive_mode=True,
        enabled_topics=json.dumps(legacy.LEVEL4_STRANDS),
        manual_levels='{}',
    ))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=1))
    session.commit()

    def test_db():
        yield session

    v0160.app.dependency_overrides[legacy.db] = test_db
    token = legacy.token_for(student)
    client = TestClient(v0160.app, headers={'Authorization': f'Bearer {token}'})
    return client, session, student


def identities(worksheet: dict) -> list[tuple[str, tuple[str, ...]]]:
    return [legacy.question_identity(question['prompt'], question['payload']) for question in worksheet['questions']]


def close_client(session: Session):
    v0160.app.dependency_overrides.clear()
    session.close()


def test_today_route_creates_duplicate_safe_first_worksheet():
    client, session, _ = make_client()
    response = client.post('/api/worksheets/today', json={'topic': 'mixed'})
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['total'] == len(worksheet['questions'])
    assert len(identities(worksheet)) == len(set(identities(worksheet)))
    close_client(session)


def test_additional_route_uses_same_duplicate_safe_service():
    client, session, _ = make_client()
    first = client.post('/api/worksheets/today', json={'topic': 'number'}).json()
    additional_response = client.post('/api/worksheets/new', json={'topic': 'number'})
    assert additional_response.status_code == 200
    additional = additional_response.json()
    assert additional['id'] != first['id']
    assert len(identities(additional)) == len(set(identities(additional)))
    close_client(session)


def test_today_route_preserves_category_selection():
    client, session, _ = make_client()
    response = client.post('/api/worksheets/today', json={'topic': 'measurement'})
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['selected_topic'] == 'measurement'
    assert {question['topic'] for question in worksheet['questions']} == {'measurement'}
    close_client(session)


def test_insufficient_unique_pool_returns_shorter_valid_worksheet(monkeypatch):
    client, session, student = make_client(question_count=4)

    def constant_question(topic, level, rng):
        return legacy.q('VC2M4N01', 'constant', 'Only unique prompt', 'choice', {'choices': ['A', 'B']}, 'A', 'Work')

    monkeypatch.setattr(legacy, 'make_question', constant_question)
    response = client.post('/api/worksheets/today', json={'topic': 'number'})
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['total'] == 1
    assert len(worksheet['questions']) == 1
    stored = session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == student.id)).all()
    assert len(stored) == 1
    close_client(session)
