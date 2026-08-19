from __future__ import annotations

from datetime import date

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0290


def make_client(role: str = 'student'):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    user = legacy.User(username=f'{role}-learning', password_hash='x', role=role, display_name=role.title())
    session.add(user); session.flush()
    worksheet = legacy.Worksheet(student_id=user.id, worksheet_date=date.today(), total=1, session_kind='parent_test' if role == 'parent' else 'practice')
    session.add(worksheet); session.flush()
    question = legacy.Question(worksheet_id=worksheet.id, topic='number', skill='VC2M4N06:efficient_multiply', level=4, prompt='Calculate 37 × 6.', answer_type='number', payload='{}', correct_answer='222', working='Partition 37 into 30 and 7.', position=0, state='active')
    session.add(question); session.flush(); worksheet.current_question_id = question.id; session.commit()

    def test_db():
        yield session

    v0290.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0290.app, headers={'Authorization': f'Bearer {legacy.token_for(user)}'}), session, question


def test_incorrect_answer_keeps_retry_available_without_tutor_gate():
    client, session, question = make_client()
    first = client.post(f'/api/questions/{question.id}/answer', json={'answer': '216', 'seconds': 3})
    assert first.status_code == 200
    assert first.json()['retry_allowed'] is True
    assert first.json()['mentor_required'] is False
    retry = client.post(f'/api/questions/{question.id}/answer', json={'answer': '222', 'seconds': 4})
    assert retry.json()['correct'] is True
    assert session.query(v0290.LearningEvidence).count() >= 2
    v0290.app.dependency_overrides.clear(); session.close()


def test_worked_example_matches_multiplication_operation_and_uses_different_values():
    client, session, question = make_client()
    response = client.get(f'/api/questions/{question.id}/math-mentor?action=worked_example')
    assert response.status_code == 200
    example = response.json()['worked_example']
    assert '×' in example
    assert '37 × 6' not in example
    assert response.json()['example_is_aligned'] is True
    v0290.app.dependency_overrides.clear(); session.close()


def test_prerequisite_graph_and_parent_recommendations_are_available():
    client, session, question = make_client('parent')
    graph = client.get('/api/learning/prerequisite-graph')
    assert graph.status_code == 200
    assert any(item['skill'] == 'equivalent_fractions' for item in graph.json()['graph'])
    recommendations = client.get('/api/learning/recommendations')
    assert recommendations.status_code == 200
    assert recommendations.json()['recommendations']
    v0290.app.dependency_overrides.clear(); session.close()


def test_parent_test_keeps_assessment_attempt_limit():
    client, session, question = make_client('parent')
    assert client.post(f'/api/questions/{question.id}/answer', json={'answer': 'wrong'}).json()['retry_allowed'] is True
    assert client.post(f'/api/questions/{question.id}/answer', json={'answer': 'wrong'}).json()['retry_allowed'] is False
    v0290.app.dependency_overrides.clear(); session.close()


def test_difficulty_guard_identifies_only_simple_arithmetic():
    easy = legacy.Question(prompt='Calculate 4 + 5.', skill='addition')
    challenging = legacy.Question(prompt='Calculate 37 × 6.', skill='efficient_multiply')
    assert v0290._too_easy(easy) is True
    assert v0290._too_easy(challenging) is False


def test_aligned_examples_preserve_subtraction_strategy():
    question = legacy.Question(prompt='Calculate 84 − 27.', skill='written_subtraction')
    example = v0290.aligned_worked_example(question)
    assert '−' in example
    assert '84 − 27' not in example
    assert 'regroup' in example.lower()
