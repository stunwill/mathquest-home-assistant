from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0190, v0230, v0330, v0430


def make_client():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-v0430', password_hash='x', role='student', display_name='Sienna')
    parent = legacy.User(username='parent-v0430', password_hash='x', role='parent', display_name='Parent')
    session.add_all([student, parent]); session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=10, adaptive_mode=True, enabled_topics='["number","algebra","measurement","space","statistics","probability"]', manual_levels='{}'))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()
    def test_db(): yield session
    v0430.app.dependency_overrides[legacy.db] = test_db
    return TestClient(v0430.app), session, student, parent


def complete_diagnostic(client, session, student, answers=(True, True, True, True, False, False), support_index=None):
    response = client.post('/api/sessions/new', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}, json={'kind':'diagnostic','minutes':15,'topic':'number_algebra'})
    assert response.status_code == 200
    worksheet = session.get(legacy.Worksheet, response.json()['id'])
    for index, question in enumerate(sorted(worksheet.questions, key=lambda item: item.position)):
        answer = question.correct_answer if answers[index] else '__wrong__'
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer=answer, correct=answers[index], attempt_number=1, seconds=20, created_at=datetime.utcnow()))
        question.answered_at = datetime.utcnow()
        question.state = 'answered_correct' if answers[index] else 'answered_incorrect'
        if support_index == index:
            question.hint_count = 1
    worksheet.completed_at = datetime.utcnow(); worksheet.status = 'completed'; worksheet.score = sum(answers)
    session.commit(); session.refresh(worksheet)
    return worksheet


def close(session):
    v0430.app.dependency_overrides.clear(); session.close()


def test_diagnostic_results_feed_existing_outcome_mastery_without_parallel_score():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student)
    outcomes = {item['code']: item for item in v0230.outcome_mastery(session, student.id)}
    assert outcomes['VC2M4N06']['questions'] == 3
    assert outcomes['VC2M4N03']['questions'] == 3
    assert not outcomes['VC2M4N06']['target_skill'].startswith('diagnostic_')
    assert not outcomes['VC2M4N03']['target_skill'].startswith('diagnostic_')
    caps = client.get('/api/v0430/capabilities', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}).json()
    assert caps['reuses_outcome_mastery'] is True
    assert caps['no_parallel_mastery_score'] is True
    close(session)


def test_short_diagnostic_does_not_bypass_challenge_readiness_threshold():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student, answers=(True, True, True, True, True, True))
    level5 = v0330._question_evidence(session, student.id, 'VC2M5N06:diagnostic_operations')
    level6 = v0330._question_evidence(session, student.id, 'VC2M6N03:diagnostic_fraction_decimal')
    assert level5['questions'] == 3 and v0330._progression_state(level5) == 'not_ready'
    assert level6['questions'] == 3 and v0330._progression_state(level6) == 'not_ready'
    close(session)


def test_mixed_level6_evidence_produces_conservative_follow_up():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student, answers=(True, True, True, True, False, False))
    placement = v0430.diagnostic_placement_snapshot(session, student.id)
    assert placement['status'] == 'complete'
    assert 'little more evidence' in placement['student_message'].lower() or 'little more practice' in placement['student_message'].lower()
    assert placement['recommended_focus']['title']
    assert 'estimated_level' not in placement
    close(session)


def test_historical_evidence_is_preserved_and_combined_with_diagnostic():
    client, session, student, _ = make_client()
    prior = legacy.Worksheet(student_id=student.id, worksheet_date=date.today()-timedelta(days=2), total=1, selected_topic='number', status='completed', completed_at=datetime.utcnow()-timedelta(days=2))
    session.add(prior); session.flush()
    q = legacy.Question(worksheet_id=prior.id, topic='number', skill='VC2M4N06:written_subtraction', level=4, prompt='Prior', answer_type='number', payload='{}', correct_answer='1', working='x', position=0, state='answered_correct', answered_at=datetime.utcnow()-timedelta(days=2))
    session.add(q); session.flush(); session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='1', correct=True, attempt_number=1, seconds=10, created_at=datetime.utcnow()-timedelta(days=2))); session.commit()
    complete_diagnostic(client, session, student)
    placement = v0430.diagnostic_placement_snapshot(session, student.id)
    matching = next(item for item in placement['demonstrated'] if item['code']=='VC2M4N06')
    assert matching['prior_evidence_questions'] == 1
    assert matching['current_evidence_questions'] == 4
    close(session)


def test_parent_snapshot_keeps_detailed_evidence_while_student_snapshot_hides_codes():
    client, session, student, parent = make_client(); complete_diagnostic(client, session, student, support_index=3)
    student_data = client.get('/api/learning/diagnostic-placement-v0430', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}).json()
    parent_data = client.get('/api/learning/parent-diagnostic-v0430', headers={'Authorization': f'Bearer {legacy.token_for(parent)}'}).json()
    assert 'VC2M' not in str(student_data)
    assert any('code' in item for item in parent_data['demonstrated'] + parent_data['supported'] + parent_data['needs_more_evidence'])
    assert parent_data['levels'][1]['support_used'] == 1
    close(session)


def test_diagnostic_retakes_preserve_history_without_inflating_mastery_or_progression():
    client, session, student, _ = make_client()
    first = complete_diagnostic(client, session, student, answers=(True, True, True, True, True, True))
    first.completed_at = datetime.utcnow()-timedelta(days=3); session.commit()
    second = complete_diagnostic(client, session, student, answers=(True, True, True, True, True, True))
    placement = v0430.diagnostic_placement_snapshot(session, student.id)
    parent = v0430.parent_diagnostic_snapshot(session, student.id)
    outcomes = {item['code']: item for item in v0230.outcome_mastery(session, student.id)}
    level5 = v0330._question_evidence(session, student.id, 'VC2M5N06:diagnostic_operations')
    level6 = v0330._question_evidence(session, student.id, 'VC2M6N03:diagnostic_fraction_decimal')
    assert placement['worksheet_id'] == second.id
    assert len(parent['attempt_history']) == 2
    assert parent['attempt_history'][0]['worksheet_id'] == second.id
    assert outcomes['VC2M4N06']['questions'] == 3
    assert outcomes['VC2M4N03']['questions'] == 3
    assert outcomes['VC2M4N06']['retention_checks'] == 0
    assert outcomes['VC2M4N03']['retention_checks'] == 0
    assert v0330._progression_state(level5) == 'not_ready'
    assert v0330._progression_state(level6) == 'not_ready'
    close(session)


def test_weak_level6_evidence_can_use_existing_prerequisite_routing():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student, answers=(True, True, True, False, False, False))
    recommendation = v0230.next_session_recommendation(session, student.id)
    assert recommendation['mode'] in {'guided', 'practice', 'review'}
    if recommendation['outcome_code'] == 'VC2M4A02':
        assert recommendation['prerequisite_for'] == 'VC2M4N03'
    close(session)


def test_diagnostic_completion_produces_non_diagnostic_next_learning_recommendation():
    client, session, student, _ = make_client(); complete_diagnostic(client, session, student)
    recommendation = v0230.next_session_recommendation(session, student.id)
    assert recommendation['mode'] != 'diagnostic'
    assert recommendation['title']
    assert recommendation['target_skill']
    assert not recommendation['target_skill'].startswith('diagnostic_')
    close(session)


def test_six_question_diagnostic_contract_remains_intact():
    client, session, student, _ = make_client()
    response = client.post('/api/sessions/new', headers={'Authorization': f'Bearer {legacy.token_for(student)}'}, json={'kind':'diagnostic','minutes':15,'topic':'number_algebra'})
    assert response.status_code == 200
    data = response.json()
    assert data['total'] == 6
    assert [item['level'] for item in data['questions']] == [5,5,5,6,6,6]
    close(session)
