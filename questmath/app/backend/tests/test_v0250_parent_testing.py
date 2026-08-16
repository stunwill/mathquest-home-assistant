from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0250


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    parent = legacy.User(username='parent-v0250', password_hash='x', role='parent', display_name='Stu')
    student = legacy.User(username='student-v0250', password_hash='x', role='student', display_name='Sienna', xp=120)
    session.add_all([parent, student])
    session.flush()
    session.add(legacy.Setting(student_id=student.id, enabled_topics=json.dumps(legacy.LEVEL4_STRANDS)))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4, attempts=3, rolling_accuracy=.75))
    session.commit()

    def test_db():
        yield session

    v0250.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0250.app), session, parent, student


def headers(user: legacy.User):
    return {'Authorization': f'Bearer {legacy.token_for(user)}'}


def close(session: Session):
    v0250.app.dependency_overrides.clear()
    session.close()


def test_parent_can_complete_a_test_worksheet_and_trace_feedback_without_changing_learning_data():
    client, session, parent, student = make_client()
    student_skill_before = [(skill.topic, skill.attempts, skill.rolling_accuracy) for skill in session.scalars(
        select(legacy.Skill).where(legacy.Skill.student_id == student.id).order_by(legacy.Skill.topic)
    ).all()]
    student_xp_before = student.xp

    created = client.post('/api/testing/worksheets', headers=headers(parent), json={
        'topic': 'number_algebra', 'question_count': 5,
    })
    assert created.status_code == 200
    worksheet = created.json()
    assert worksheet['test_mode'] is True
    assert worksheet['session_kind'] == 'parent_test'
    stored = session.get(legacy.Worksheet, worksheet['id'])
    assert stored.student_id == parent.id

    first = stored.questions[0]
    hint = client.post(f'/api/questions/{first.id}/hint', headers=headers(parent))
    assert hint.status_code == 200
    answer = client.post(f'/api/questions/{first.id}/answer', headers=headers(parent), json={
        'answer': first.correct_answer, 'seconds': 4,
    })
    assert answer.status_code == 200
    refreshed = client.get(f'/api/worksheets/{stored.id}/view', headers=headers(parent))
    assert refreshed.status_code == 200
    assert refreshed.json()['counts']['correct'] == 1
    second = stored.questions[1]
    moved = client.post(f'/api/worksheets/{stored.id}/navigate/{second.id}', headers=headers(parent), json={
        'elapsed_seconds': 5,
    })
    assert moved.status_code == 200
    question_note = client.post(f'/api/testing/worksheets/{stored.id}/feedback', headers=headers(parent), json={
        'question_id': first.id, 'feedback_type': 'bug', 'note': 'The visual did not match the prompt.',
    })
    assert question_note.status_code == 200

    premature_overall = client.post(f'/api/testing/worksheets/{stored.id}/feedback', headers=headers(parent), json={
        'question_id': None, 'feedback_type': 'note', 'note': 'Overall note',
    })
    assert premature_overall.status_code == 409
    for question in stored.questions[1:]:
        skipped = client.post(f'/api/questions/{question.id}/skip', headers=headers(parent), json={'elapsed_seconds': 10})
        assert skipped.status_code == 200
    completed = client.post(f'/api/worksheets/{stored.id}/complete', headers=headers(parent))
    assert completed.status_code == 200
    assert completed.json()['test_mode'] is True
    assert completed.json()['xp_earned'] == 0

    overall = client.post(f'/api/testing/worksheets/{stored.id}/feedback', headers=headers(parent), json={
        'question_id': None, 'feedback_type': 'enhancement', 'note': 'Make the instructions clearer throughout.',
    })
    assert overall.status_code == 200
    feedback_id = question_note.json()['id']
    addressed = client.put(f'/api/testing/feedback/{feedback_id}', headers=headers(parent), json={
        'feedback_type': 'bug', 'note': 'The visual did not match the prompt.',
        'status': 'addressed', 'addressed_release': 'v0.25.1',
    })
    assert addressed.status_code == 200
    assert addressed.json()['addressed_release'] == '0.25.1'

    detail = client.get(f'/api/testing/worksheets/{stored.id}', headers=headers(parent))
    assert detail.status_code == 200
    assert detail.json()['feedback_count'] == 2
    assert detail.json()['addressed_releases'] == ['0.25.1']
    assert detail.json()['questions'][0]['feedback'][0]['status'] == 'addressed'

    session.refresh(student)
    assert student.xp == student_xp_before
    student_skill_after = [(skill.topic, skill.attempts, skill.rolling_accuracy) for skill in session.scalars(
        select(legacy.Skill).where(legacy.Skill.student_id == student.id).order_by(legacy.Skill.topic)
    ).all()]
    assert student_skill_after == student_skill_before
    close(session)


def test_test_feedback_is_parent_only_and_addressed_release_is_validated():
    client, session, parent, student = make_client()
    assert client.get('/api/testing/worksheets', headers=headers(student)).status_code == 403
    created = client.post('/api/testing/worksheets', headers=headers(parent), json={'topic': 'number', 'question_count': 5})
    worksheet_id = created.json()['id']
    stored = session.get(legacy.Worksheet, worksheet_id)
    question = stored.questions[0]
    client.post(f'/api/questions/{question.id}/answer', headers=headers(parent), json={'answer': question.correct_answer})
    item = client.post(f'/api/testing/worksheets/{worksheet_id}/feedback', headers=headers(parent), json={
        'question_id': question.id, 'feedback_type': 'bug', 'note': 'Check this question.',
    }).json()
    invalid = client.put(f"/api/testing/feedback/{item['id']}", headers=headers(parent), json={
        'feedback_type': 'bug', 'note': 'Check this question.', 'status': 'addressed', 'addressed_release': 'next release',
    })
    assert invalid.status_code == 400
    close(session)


def test_parent_test_view_does_not_allow_another_parent_or_learner_worksheet():
    client, session, parent, student = make_client()
    other = legacy.User(username='other-parent', password_hash='x', role='parent', display_name='Other')
    session.add(other); session.commit()
    created = client.post('/api/testing/worksheets', headers=headers(parent), json={'topic': 'number', 'question_count': 5})
    worksheet_id = created.json()['id']
    assert client.get(f'/api/worksheets/{worksheet_id}/view', headers=headers(other)).status_code == 404
    learner = legacy.create_worksheet(session, student.id, 'number', question_count=5)
    assert client.get(f'/api/worksheets/{learner.id}/view', headers=headers(parent)).status_code == 200
    assert client.post(f'/api/worksheets/{learner.id}/save', headers=headers(parent), json={'elapsed_seconds': 1}).status_code == 404
    close(session)


def test_v0250_routes_are_before_the_spa_fallback():
    client, session, parent, _ = make_client()
    response = client.get('/api/v0250/capabilities', headers=headers(parent))
    assert response.status_code == 200
    assert response.json()['learning_evidence_isolation'] is True
    paths = [getattr(route, 'path', None) for route in v0250.app.router.routes]
    if '/{path:path}' in paths:
        assert paths.index('/api/v0250/capabilities') < paths.index('/{path:path}')
    close(session)
