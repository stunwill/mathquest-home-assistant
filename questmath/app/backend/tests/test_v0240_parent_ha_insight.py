from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0110, v0240


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    parent = legacy.User(username='parent-v0240', password_hash='x', role='parent', display_name='Stu')
    student = legacy.User(username='student-v0240', password_hash='x', role='student', display_name='Sienna')
    session.add_all([parent, student])
    session.flush()
    session.add(legacy.Setting(student_id=student.id, enabled_topics=json.dumps(legacy.LEVEL4_STRANDS)))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()

    def test_db():
        yield session

    v0240.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0240.app), session, parent, student


def add_question(session: Session, student: legacy.User, *, when: datetime, correct: bool,
                 hints: int = 0, seconds: float = 20, code: str = 'VC2M4N06'):
    worksheet = legacy.Worksheet(
        student_id=student.id, worksheet_date=when.date(), total=1, selected_topic='number',
        status='completed', completed_at=when,
    )
    session.add(worksheet)
    session.flush()
    question = legacy.Question(
        worksheet_id=worksheet.id, topic='number', skill=f'{code}:written_subtraction', level=4,
        prompt='Calculate using an efficient strategy.', answer_type='number', payload=json.dumps({
            'strategy_card': {'title': 'Written subtraction with regrouping'},
        }), correct_answer='10', working='Regroup if needed.', position=0,
        state='answered_correct' if correct else 'answered_incorrect', hint_count=hints, answered_at=when,
    )
    session.add(question)
    session.flush()
    session.add(legacy.Attempt(
        question_id=question.id, student_id=student.id, answer='10' if correct else '9',
        correct=correct, attempt_number=1, seconds=seconds, created_at=when,
    ))
    session.commit()


def add_diagnostic(session: Session, student: legacy.User, *, when: datetime, secure_to: int):
    worksheet = legacy.Worksheet(
        student_id=student.id, worksheet_date=when.date(), total=15, selected_topic='number_algebra',
        session_kind='diagnostic', status='completed', completed_at=when,
    )
    session.add(worksheet)
    session.flush()
    for index, level in enumerate(level for level in range(2, 7) for _ in range(3)):
        question = legacy.Question(
            worksheet_id=worksheet.id, topic='number', skill=f'VC2M{level}N01:diagnostic', level=level,
            prompt=f'Level {level}', answer_type='number', payload='{}', correct_answer='1', working='',
            position=index, state='answered_correct', answered_at=when,
        )
        session.add(question)
        session.flush()
        session.add(legacy.Attempt(
            question_id=question.id, student_id=student.id, answer='1', correct=level <= secure_to,
            attempt_number=1, seconds=20, created_at=when,
        ))
    session.commit()


def close(session: Session):
    v0240.app.dependency_overrides.clear()
    session.close()


def test_parent_insight_reports_level_growth_outcome_growth_and_weekly_signals():
    _, session, _, student = make_client()
    now = datetime.now()
    add_diagnostic(session, student, when=now - timedelta(days=30), secure_to=3)
    add_diagnostic(session, student, when=now - timedelta(days=2), secure_to=4)
    for days, correct, hints in [(13, False, 1), (11, False, 0), (9, False, 1), (5, True, 0), (3, True, 0), (1, True, 0)]:
        add_question(session, student, when=now - timedelta(days=days), correct=correct, hints=hints)

    insight = v0240.parent_insight(session, student.id, now.date())
    outcome = next(item for item in insight['outcomes'] if item['code'] == 'VC2M4N06')
    assert insight['estimated_level']['baseline'] == 3
    assert insight['estimated_level']['current'] == 4
    assert insight['estimated_level']['growth'] == 1
    assert outcome['baseline_independent_accuracy'] == 0
    assert outcome['current_independent_accuracy'] == 100
    assert outcome['growth_points'] == 100
    assert insight['weekly']['current']['independent_accuracy'] == 67
    assert insight['strategies_used'][0]['strategy'] == 'Written subtraction with regrouping'
    close(session)


def test_ha_service_token_and_user_jwt_both_authorise_dashboard_endpoints():
    client, session, parent, student = make_client()
    add_question(session, student, when=datetime.now(), correct=True)
    assert client.get('/api/ha/summary').status_code == 401

    service = client.get('/api/ha/summary', headers={'Authorization': f'Bearer {legacy.HA_SERVICE_TOKEN}'})
    assert service.status_code == 200
    assert service.json()['available'] is True
    assert service.json()['learning']['recommendation']['minutes'] in (5, 10, 15)
    assert client.get('/api/settings', headers={'Authorization': f'Bearer {legacy.HA_SERVICE_TOKEN}'}).status_code == 401

    jwt_response = client.get('/api/ha/stats', headers={'Authorization': f'Bearer {legacy.token_for(parent)}'})
    assert jwt_response.status_code == 200
    assert set(legacy.LEVEL4_STRANDS) == set(jwt_response.json()['outcome_categories'])

    token_response = client.get('/api/ha/service-token', headers={'Authorization': f'Bearer {legacy.token_for(parent)}'})
    assert token_response.status_code == 200
    assert token_response.json()['expires'] is None
    assert token_response.json()['token'] == legacy.HA_SERVICE_TOKEN
    close(session)


def test_ha_endpoint_returns_an_unavailable_state_when_insight_aggregation_fails(monkeypatch):
    client, session, _, student = make_client()
    add_question(session, student, when=datetime.now(), correct=True)
    monkeypatch.setattr(v0110, '_dashboard_insight_provider', lambda *_: (_ for _ in ()).throw(RuntimeError('test failure')))
    response = client.get('/api/ha/stats', headers={'Authorization': f'Bearer {legacy.HA_SERVICE_TOKEN}'})
    assert response.status_code == 200
    assert response.json() == {'available': False, 'reason': 'statistics_unavailable', 'app_path': '/'}
    monkeypatch.setattr(v0110, '_dashboard_insight_provider', v0240._ha_learning_insight)
    close(session)


def test_v0240_routes_are_before_the_spa_fallback():
    client, session, parent, _ = make_client()
    response = client.get('/api/v0240/capabilities', headers={'Authorization': f'Bearer {legacy.token_for(parent)}'})
    assert response.status_code == 200
    assert response.json()['persistent_home_assistant_service_token'] is True
    paths = [getattr(route, 'path', None) for route in v0240.app.router.routes]
    if '/{path:path}' in paths:
        assert paths.index('/api/v0240/capabilities') < paths.index('/{path:path}')
    close(session)
