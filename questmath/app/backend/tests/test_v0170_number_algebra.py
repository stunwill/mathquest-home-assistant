from __future__ import annotations

import json
import random
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0170


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-focus', password_hash='x', role='student', display_name='Sienna')
    session.add(student); session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=20, adaptive_mode=True, enabled_topics=json.dumps(legacy.LEVEL4_STRANDS), manual_levels='{}'))
    for topic in legacy.LEVEL4_STRANDS: session.add(legacy.Skill(student_id=student.id, topic=topic, level=1))
    session.commit()

    def test_db(): yield session

    v0170.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0170.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session


def close(session: Session):
    v0170.app.dependency_overrides.clear(); session.close()


def test_number_algebra_focus_route_excludes_other_strands():
    client, session = make_client()
    response = client.post('/api/worksheets/today', json={'topic': 'number_algebra'})
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['selected_topic'] == 'number_algebra'
    assert {question['topic'] for question in worksheet['questions']} <= {'number', 'algebra'}
    assert {'number', 'algebra'} == {question['topic'] for question in worksheet['questions']}
    close(session)


def test_navigation_can_return_to_an_earlier_unfinished_question():
    client, session = make_client()
    worksheet = client.post('/api/worksheets/today', json={'topic': 'number_algebra'}).json()
    first, second = worksheet['questions'][:2]
    moved_forward = client.post(f"/api/worksheets/{worksheet['id']}/navigate/{second['id']}", json={'elapsed_seconds': 4})
    assert moved_forward.status_code == 200
    moved_back = client.post(f"/api/worksheets/{worksheet['id']}/navigate/{first['id']}", json={'elapsed_seconds': 7})
    assert moved_back.status_code == 200
    assert moved_back.json()['current_question_id'] == first['id']
    close(session)


def test_all_four_fact_operations_have_contextual_strategy_cards():
    generated = [
        v0170._addition_fact(random.Random(1)),
        v0170._subtraction_fact(random.Random(2)),
        v0170._multiplication_fact(random.Random(3)),
        v0170._division_fact(random.Random(4)),
    ]
    operations = {item[3]['operation'] for item in generated}
    assert operations == {'addition', 'subtraction', 'multiplication', 'division'}
    for item in generated:
        card = item[3]['strategy_card']
        assert card['rule'] and card['steps'] and card['example']
        assert 'finger' not in item[1].lower()


def test_subtraction_strategy_covers_all_column_cases():
    cases = {}
    for seed in range(100):
        item = v0170._written_subtraction(random.Random(seed))
        cases[item[3]['subtraction_case']] = item[3]['strategy_card']
    assert set(cases) == {'no_regroup', 'regroup', 'equal'}
    assert 'No need to stop' in cases['no_regroup']['rule']
    assert 'Regroup next door' in cases['regroup']['rule']
    assert 'Zero is the game' in cases['equal']['rule']


def test_subtraction_hint_uses_the_question_case_without_revealing_answer():
    item = next(v0170._written_subtraction(random.Random(seed)) for seed in range(100) if v0170._written_subtraction(random.Random(seed))[3]['subtraction_case'] == 'regroup')
    question = SimpleNamespace(skill=item[0], payload=json.dumps(item[3]), correct_answer=item[4], working=item[5])
    first = v0170.hint_text_v0170(question, 1)
    second = v0170.hint_text_v0170(question, 2)
    assert 'Regroup next door' in first
    assert 'Trade 1 ten for 10 ones' in second
    assert str(item[4]) not in first


def test_unknown_addition_and_subtraction_equations_use_inverse_operations():
    prompts = [v0170._unknown_equation(random.Random(seed)) for seed in range(30)]
    assert any('□ +' in item[1] for item in prompts)
    assert any('□ −' in item[1] or '− □' in item[1] for item in prompts)
    assert all(item[0].startswith('VC2M4A01:unknown_add_subtract') for item in prompts)
    assert all(item[3]['strategy_card']['strategy'] == 'Use the inverse operation' for item in prompts)


def test_focus_capabilities_and_empty_progress_are_available_over_http():
    client, session = make_client()
    capabilities = client.get('/api/v0170/capabilities')
    assert capabilities.status_code == 200
    assert capabilities.json()['fact_recall_operations'] == ['addition', 'subtraction', 'multiplication', 'division']
    progress = client.get('/api/learning/focus-v0170')
    assert progress.status_code == 200
    assert progress.json()['recommended_quest'] == 'number_algebra'
    assert all(item['status'] == 'not assessed' for item in progress.json()['operations'])
    close(session)


def test_subtraction_teaching_lesson_explains_place_value_regrouping():
    question = SimpleNamespace(skill='VC2M4N06:written_subtraction')
    lesson = v0170.mini_lesson_v0170(question)
    assert 'place value' in lesson['title'].lower()
    assert 'trade 1 ten' in lesson['example'].lower()
    assert '73' in lesson['example']
