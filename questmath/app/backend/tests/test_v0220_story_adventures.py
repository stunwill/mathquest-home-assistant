from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0340


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-story', password_hash='x', role='student', display_name='Sienna')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(
        student_id=student.id, question_count=10, adaptive_mode=True,
        enabled_topics=json.dumps(legacy.LEVEL4_STRANDS), manual_levels='{}',
    ))
    mastery = {'number': .9, 'measurement': .35, 'statistics': .6, 'space': .7}
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(
            student_id=student.id, topic=topic, level=4, attempts=10,
            rolling_accuracy=mastery.get(topic, .8),
        ))
    session.commit()

    def test_db():
        yield session

    v0340.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0340.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session


def close(session: Session):
    v0340.app.dependency_overrides.clear()
    session.close()


def test_adventure_cards_are_data_driven_and_recommend_learning_goals():
    client, session = make_client()
    response = client.get('/api/adventures-v0340')
    assert response.status_code == 200
    bakery = next(item for item in response.json() if item['id'] == 'bakery')
    assert bakery['recommended_goals'] == ['measurement', 'statistics']
    assert bakery['mission'] and bakery['objective'] and bakery['outcome']
    assert bakery['session_lengths'] == [5, 10, 15]
    assert bakery['presentation_only'] is True
    close(session)


def test_legacy_adventure_endpoint_now_preserves_selected_math_questions():
    client, session = make_client()
    worksheet = client.post('/api/sessions/new', json={'kind': 'practice', 'minutes': 10, 'topic': 'mixed'}).json()
    raw = session.get(legacy.Worksheet, worksheet['id'])
    before = [(q.skill, q.prompt, q.answer_type, q.correct_answer, q.level) for q in sorted(raw.questions, key=lambda item: item.position)]

    response = client.post(f"/api/worksheets/{worksheet['id']}/adventure", json={'theme': 'space'})
    assert response.status_code == 200
    result = response.json()
    assert result['questions_linked'] == len(before)
    assert result['stages'][-1] == 'Completion'

    session.refresh(raw)
    after = [(q.skill, q.prompt, q.answer_type, q.correct_answer, q.level) for q in sorted(raw.questions, key=lambda item: item.position)]
    assert after == before
    assert raw.session_kind == 'adventure'

    payloads = [json.loads(question.payload) for question in sorted(raw.questions, key=lambda item: item.position)]
    stories = [payload['adventure'] for payload in payloads]
    assert len({story['mission_id'] for story in stories}) == 1
    assert all(story['version'] == 3 for story in stories)
    assert all(story['mission'] == 'Bring the research crew home' for story in stories)
    assert all(story['learning_purpose'] == payload['learning_purpose'] for story, payload in zip(stories, payloads))
    assert all(story['context']['lead_in'] for story in stories)
    close(session)


def test_completed_adventure_returns_final_mission_outcome():
    client, session = make_client()
    worksheet = client.post('/api/sessions/new', json={'kind': 'practice', 'minutes': 5, 'topic': 'mixed'}).json()
    client.post(f"/api/worksheets/{worksheet['id']}/adventure", json={'theme': 'animal_rescue'})
    raw = session.get(legacy.Worksheet, worksheet['id'])
    for question in raw.questions:
        question.state = 'skipped'
        question.skipped_count = 1
    session.commit()

    response = client.post(f"/api/worksheets/{worksheet['id']}/complete")
    assert response.status_code == 200
    outcome = response.json()['adventure']
    assert outcome['mission'] == 'Prepare every animal for adoption day'
    assert outcome['status'] == 'complete_with_review'
    assert 'adoption day' in outcome['outcome'].lower()
    close(session)


def test_v0340_capability_route_is_before_spa_fallback():
    client, session = make_client()
    response = client.get('/api/v0340/capabilities')
    assert response.status_code == 200
    assert response.json()['adaptive_story_adventures'] is True
    paths = [getattr(route, 'path', None) for route in v0340.app.router.routes]
    if '/{path:path}' in paths:
        assert paths.index('/api/v0340/capabilities') < paths.index('/{path:path}')
    close(session)
