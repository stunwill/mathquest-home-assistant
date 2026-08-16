from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0280


def make_client(role: str = 'student'):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    user = legacy.User(username=f'{role}-mentor', password_hash='x', role=role, display_name=role.title())
    session.add(user); session.flush()
    worksheet = legacy.Worksheet(student_id=user.id, worksheet_date=date.today(), total=1, session_kind='parent_test' if role == 'parent' else 'practice')
    session.add(worksheet); session.flush()
    question = legacy.Question(
        worksheet_id=worksheet.id, topic='algebra', skill='VC2M4A01:unknown_add_subtract', level=4,
        prompt='□ + 18 = 43', answer_type='number', payload='{}', correct_answer='25',
        working='Use subtraction to undo addition.', position=0, state='active',
    )
    session.add(question); session.flush(); worksheet.current_question_id = question.id; session.commit()

    def test_db():
        yield session

    v0280.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0280.app, headers={'Authorization': f'Bearer {legacy.token_for(user)}'}), session, question


def answer(client: TestClient, question: legacy.Question, value: str = '61'):
    return client.post(f'/api/questions/{question.id}/answer', json={'answer': value, 'seconds': 4})


def test_student_incorrect_path_requires_progressive_mentor_before_answer_reveal():
    client, session, question = make_client()
    first = answer(client, question)
    assert first.status_code == 200
    assert first.json()['retry_allowed'] is True
    assert first.json()['next_support'] == 'guiding_question'
    guide = client.get(f'/api/questions/{question.id}/math-mentor?action=guide')
    assert guide.status_code == 200
    assert guide.json()['guiding_question'].endswith('?')

    assert answer(client, question).json()['next_support'] == 'hint_1'
    for stage in range(1, 4):
        hint = client.post(f'/api/questions/{question.id}/hint')
        assert hint.status_code == 200
        assert hint.json()['hint_count'] == stage
        if stage < 3:
            assert answer(client, question).json()['retry_allowed'] is True
    assert answer(client, question).json()['next_support'] == 'worked_example'
    example = client.get(f'/api/questions/{question.id}/math-mentor?action=worked_example')
    assert example.status_code == 200
    assert example.json()['worked_example'] != question.prompt
    final = answer(client, question)
    assert final.status_code == 200
    assert final.json()['retry_allowed'] is False
    assert final.json()['correct_answer'] == '25'
    v0280.app.dependency_overrides.clear(); session.close()


def test_mentor_restart_preserves_question_attempts_and_support_history():
    client, session, question = make_client()
    answer(client, question)
    client.get(f'/api/questions/{question.id}/math-mentor?action=guide')
    client.post(f'/api/questions/{question.id}/hint')
    restarted = client.post(f'/api/questions/{question.id}/math-mentor/start-over')
    assert restarted.status_code == 200
    assert restarted.json()['reset'] is True
    assert restarted.json()['action'] == 'guide'
    session.refresh(question)
    assert len(question.attempts) == 1
    assert question.hint_count == 1
    assert question.state == 'mentor_active'
    v0280.app.dependency_overrides.clear(); session.close()


def test_parent_test_keeps_two_attempt_assessment_flow_but_can_read_mentor_content():
    client, session, question = make_client('parent')
    assert client.get(f'/api/questions/{question.id}/math-mentor?action=why').status_code == 200
    assert answer(client, question).json()['retry_allowed'] is True
    final = answer(client, question)
    assert final.json()['retry_allowed'] is False
    assert final.json()['correct_answer'] == '25'
    v0280.app.dependency_overrides.clear(); session.close()


def test_v0280_routes_are_registered_before_the_spa_fallback():
    paths = [getattr(route, 'path', None) for route in v0280.app.router.routes]
    assert '/api/questions/{qid}/math-mentor' in paths
    assert '/api/questions/{qid}/math-mentor/start-over' in paths
    if '/{path:path}' in paths:
        fallback = paths.index('/{path:path}')
        assert paths.index('/api/questions/{qid}/math-mentor') < fallback
