from __future__ import annotations

import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0220


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

    v0220.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0220.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session


def close(session: Session):
    v0220.app.dependency_overrides.clear()
    session.close()


def test_adventure_cards_recommend_relevant_weaker_learning_goals():
    client, session = make_client()
    response = client.get('/api/adventures')
    assert response.status_code == 200
    bakery = next(item for item in response.json() if item['id'] == 'bakery')
    assert bakery['recommended_goals'] == ['measurement', 'statistics']
    assert bakery['mission'] and bakery['objective'] and bakery['outcome']
    close(session)


def test_story_adventure_builds_one_coherent_adaptive_mission():
    client, session = make_client()
    worksheet = client.post('/api/worksheets/new', json={'topic': 'mixed'}).json()
    response = client.post(f"/api/worksheets/{worksheet['id']}/adventure", json={'theme': 'space'})
    assert response.status_code == 200
    result = response.json()
    assert result['questions_linked'] == 10
    assert result['learning_goals'][:2] == ['measurement', 'statistics']
    assert len(result['chapters']) == 5

    raw = session.get(legacy.Worksheet, worksheet['id'])
    payloads = [json.loads(question.payload) for question in sorted(raw.questions, key=lambda item: item.position)]
    stories = [payload['adventure'] for payload in payloads]
    assert raw.session_kind == 'adventure'
    assert len({story['mission_id'] for story in stories}) == 1
    assert all(story['version'] == 2 for story in stories)
    assert all(story['mission'] == 'Bring the research crew home' for story in stories)
    assert all(story['mission_data'] == stories[0]['mission_data'] for story in stories)
    assert {story['chapter'] for story in stories} == set(result['chapters'])
    assert len({question.prompt for question in raw.questions}) == raw.total
    assert any(payload.get('applied_steps', 0) >= 2 for payload in payloads)
    assert all(question.prompt.startswith('🚀') for question in raw.questions)
    close(session)


def test_completed_adventure_returns_the_final_mission_outcome():
    client, session = make_client()
    worksheet = client.post('/api/worksheets/new', json={'topic': 'mixed'}).json()
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


def test_v0220_capability_route_is_before_spa_fallback():
    client, session = make_client()
    response = client.get('/api/v0220/capabilities')
    assert response.status_code == 200
    assert response.json()['story_adventures_2'] is True
    paths = [getattr(route, 'path', None) for route in v0220.app.router.routes]
    if '/{path:path}' in paths:
        assert paths.index('/api/v0220/capabilities') < paths.index('/{path:path}')
    close(session)
