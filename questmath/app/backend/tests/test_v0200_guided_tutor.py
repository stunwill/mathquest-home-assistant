from __future__ import annotations

import json
import re
from datetime import date
from types import SimpleNamespace

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0200


def sample(topic: str, skill: str, prompt: str):
    return SimpleNamespace(topic=topic, skill=skill, prompt=prompt, correct_answer='987654', attempts=[])


def test_representative_question_families_receive_three_scaffolded_stages():
    questions = [
        sample('number', 'VC2M4N06:written_subtraction', 'Calculate 896 − 397.'),
        sample('number', 'VC2M4N03:equivalent_fractions', 'Compare 4/5 and 2/3.'),
        sample('measurement', 'VC2M4M02:perimeter', 'Find the perimeter.'),
        sample('space', 'VC2M4SP02:grid_references', 'Which grid reference contains the square?'),
        sample('measurement', 'VC2M4M03:duration', 'How long from 5:20 to 6:15?'),
        sample('statistics', 'VC2M4ST01:data_frequency', 'Which value occurs most often?'),
        sample('algebra', 'VC2M4A01:unknown_add_subtract', '□ + 18 = 43'),
    ]
    assert [v0200.question_family(question) for question in questions] == [
        'arithmetic', 'fraction', 'measurement', 'grid', 'time', 'data', 'equation'
    ]
    for question in questions:
        stages = [v0200.hint_text_v0200(question, number) for number in (1, 2, 3)]
        assert len(set(stages)) == 3
        assert stages[0].endswith('?')
        assert question.correct_answer not in json.dumps(v0200.guided_plan(question))


def test_algebra_operation_facts_receive_arithmetic_guidance():
    multiplication = sample('algebra', 'VC2M4A02:fact_recall_multiplication', 'Calculate 7 × 8.')
    division = sample('algebra', 'VC2M4A02:fact_recall_division', 'Calculate 56 ÷ 7.')
    unknown = sample('algebra', 'VC2M4A01:unknown_add_subtract', '□ + 8 = 23')
    assert v0200.question_family(multiplication) == 'arithmetic'
    assert v0200.question_family(division) == 'arithmetic'
    assert v0200.question_family(unknown) == 'equation'


def test_worked_example_rejects_assessed_measurement_dimensions_and_answer():
    question = sample('measurement', 'VC2M4M02:area', 'A rectangle is 6 cm by 4 cm. What is its area?')
    question.correct_answer = '24'
    example = v0200.safe_worked_example(question)
    assert '6 cm by 4 cm' not in example
    assert not re.search(r'(?<!\d)24(?!\d)', example)


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='guided-student', password_hash='x', role='student', display_name='Sienna')
    session.add(student); session.flush()
    worksheet = legacy.Worksheet(student_id=student.id, worksheet_date=date.today(), total=1)
    session.add(worksheet); session.flush()
    question = legacy.Question(
        worksheet_id=worksheet.id, topic='algebra', skill='VC2M4A01:unknown_add_subtract', level=4,
        prompt='□ + 18 = 43', answer_type='number', payload='{}', correct_answer='25',
        working='Use subtraction to undo addition.', position=0, state='active'
    )
    session.add(question); session.flush(); worksheet.current_question_id = question.id; session.commit()

    def test_db():
        yield session

    v0200.app.dependency_overrides[legacy.db] = test_db
    client = TestClient(v0200.app, headers={'Authorization': f'Bearer {legacy.token_for(student)}'})
    return client, session, question


def test_hint_endpoint_progresses_to_three_stages_and_then_repeats_stage_three():
    client, session, question = make_client()
    responses = [client.post(f'/api/questions/{question.id}/hint') for _ in range(4)]
    assert all(response.status_code == 200 for response in responses)
    assert [response.json()['hint_count'] for response in responses] == [1, 2, 3, 3]
    assert [response.json()['more_available'] for response in responses] == [True, True, False, False]
    assert responses[0].json()['hint'].endswith('?')
    assert '□ + 7 = 19' in responses[2].json()['hint']
    v0200.app.dependency_overrides.clear(); session.close()


def test_guided_actions_and_misconception_routing_do_not_reveal_current_answer():
    client, session, question = make_client()
    client.post(f'/api/questions/{question.id}/answer', json={'answer': '61', 'seconds': 8})
    for action in ('hint', 'why', 'teach', 'another'):
        response = client.get(f'/api/questions/{question.id}/guided-support?action={action}')
        assert response.status_code == 200
        payload = response.json()
        assert payload['action'] == action
        assert payload['final_answer_revealed'] is False
        assert not re.search(rf'(?<!\d){re.escape(question.correct_answer)}(?!\d)', json.dumps(payload, ensure_ascii=False))
    assert client.get(f'/api/questions/{question.id}/guided-support?action=hint').json()['misconception']
    v0200.app.dependency_overrides.clear(); session.close()


def test_v0200_routes_are_registered_before_the_spa_fallback():
    paths = [getattr(route, 'path', None) for route in v0200.app.router.routes]
    assert '/api/questions/{qid}/guided-support' in paths
    assert '/api/v0200/capabilities' in paths
    if '/{path:path}' in paths:
        fallback = paths.index('/{path:path}')
        assert paths.index('/api/questions/{qid}/guided-support') < fallback
        assert paths.index('/api/v0200/capabilities') < fallback
