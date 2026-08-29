from __future__ import annotations

import json
from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0290, v0330, v0350


def session_with_student():
    engine = create_engine('sqlite:///:memory:')
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='student-v0350', password_hash='x', role='student', display_name='Sienna')
    session.add(student); session.flush()
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()
    return session, student


def add_activity(session, student, *, kind='practice', completed=True, answered=True, correct=True, hints=0, mentor=False, target=10, elapsed=420, skill='VC2M4N03:equivalent_fractions', when=None, payload=None):
    when = when or date.today()
    ws = legacy.Worksheet(student_id=student.id, worksheet_date=when, total=1, status='completed' if completed else 'in_progress', session_kind=kind, target_minutes=target, elapsed_seconds=elapsed, started_at=datetime.combine(when, datetime.min.time()))
    if completed:
        ws.completed_at = datetime.combine(when, datetime.min.time()) + timedelta(minutes=target)
    session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic='number', skill=skill, level=4, prompt='Test?', answer_type='text', payload=json.dumps(payload or {}), correct_answer='1', working='', position=1, state='answered_correct' if answered and correct else 'not_started', hint_count=hints, mentor_started=mentor, answered_at=datetime.combine(when, datetime.min.time()) + timedelta(minutes=2) if answered else None)
    session.add(q); session.flush()
    if answered:
        session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='1' if correct else '0', correct=correct, attempt_number=1, seconds=10))
    session.commit()
    return ws, q


def test_no_activity_is_not_completed_and_builds_evidence():
    session, student = session_with_student()
    state = v0350.parent_ha_learning_state(session, student.id)
    assert state['daily_learning']['state'] == 'Not completed'
    assert state['daily_learning']['completed'] is False
    assert state['current_focus']['state'] == 'Building evidence'
    assert state['review']['state'] == 'No review due'


def test_completed_daily_practice_counts_as_daily_learning():
    session, student = session_with_student(); add_activity(session, student, kind='practice')
    daily = v0350.parent_ha_learning_state(session, student.id)['daily_learning']
    assert daily['completed'] is True
    assert daily['latest_session_type'] == 'Daily Practice'
    assert daily['questions_attempted'] == 1
    assert daily['active_minutes'] == 7.0
    assert daily['planned_minutes_completed'] == 10


def test_story_adventure_counts_as_legitimate_learning_activity():
    session, student = session_with_student(); add_activity(session, student, kind='adventure')
    daily = v0350.parent_ha_learning_state(session, student.id)['daily_learning']
    assert daily['completed'] is True
    assert daily['latest_session_type'] == 'Story Adventure'


def test_parent_test_does_not_satisfy_daily_learning():
    session, student = session_with_student(); add_activity(session, student, kind='parent_test')
    daily = v0350.parent_ha_learning_state(session, student.id)['daily_learning']
    assert daily['completed'] is False
    assert daily['parent_tests_today'] == 1


def test_abandoned_no_evidence_session_does_not_satisfy_completion():
    session, student = session_with_student(); add_activity(session, student, completed=False, answered=False)
    daily = v0350.parent_ha_learning_state(session, student.id)['daily_learning']
    assert daily['state'] == 'Not completed'
    assert daily['completed'] is False


def test_one_supported_question_does_not_create_persistent_support_alert():
    session, student = session_with_student(); add_activity(session, student, hints=2)
    assert v0350.parent_ha_learning_state(session, student.id)['support']['needed'] is False


def test_repeated_support_dependency_becomes_actionable():
    session, student = session_with_student()
    for i in range(4):
        add_activity(session, student, hints=2, when=date.today() - timedelta(days=i))
    state = v0350.parent_ha_learning_state(session, student.id)
    assert state['support']['needed'] is True
    assert state['support']['support_dependency'] >= 60


def test_repeated_misconception_evidence_becomes_actionable_but_one_does_not():
    session, student = session_with_student(); _, q = add_activity(session, student, correct=False)
    session.add(v0290.MisconceptionEvidence(student_id=student.id, question_id=q.id, skill=q.skill, misconception_type='fraction_whole', message='Check equal wholes.'))
    session.commit()
    assert v0350.parent_ha_learning_state(session, student.id)['misconception']['active'] is False
    session.add(v0290.MisconceptionEvidence(student_id=student.id, question_id=q.id, skill=q.skill, misconception_type='fraction_whole', message='Check equal wholes.'))
    session.commit()
    assert v0350.parent_ha_learning_state(session, student.id)['misconception']['active'] is True


def test_review_due_uses_existing_retention_evidence():
    session, student = session_with_student()
    old = date.today() - timedelta(days=8)
    for _ in range(4): add_activity(session, student, when=old)
    review = v0350.parent_ha_learning_state(session, student.id)['review']
    assert review['due'] is True
    assert review['state'] == 'Review due'


def test_existing_learning_purposes_are_parent_readable():
    for purpose, label in v0330.PURPOSE_LABELS.items():
        session, student = session_with_student()
        add_activity(session, student, payload={'learning_purpose': purpose, 'learning_purpose_label': label})
        actual, actual_label = v0350._purpose_for_skill(session, student.id, 'VC2M4N03:equivalent_fractions')
        assert actual == purpose
        assert actual_label == label


def test_prerequisite_routing_can_be_represented_in_current_focus():
    session, student = session_with_student()
    add_activity(session, student, payload={
        'learning_purpose': 'consolidation',
        'learning_purpose_label': 'Building confidence',
        'adaptive': {'prerequisite_for': 'VC2M5A01:equations'},
    })
    focus = v0350.parent_ha_learning_state(session, student.id)['current_focus']
    assert focus['learning_purpose'] == 'consolidation'
    assert focus['prerequisite_for'] == 'VC2M5A01:equations'


def test_entity_contract_uses_stable_non_transient_ids():
    session, student = session_with_student()
    model = v0350.parent_ha_learning_state(session, student.id)['entity_model']
    ids = {value['unique_id'] for value in model.values()}
    assert ids == set(v0350.ENTITY_IDS.values())
    assert all(not any(char.isdigit() for char in uid) for uid in ids)


def test_alerts_are_idempotent_and_do_not_duplicate_unchanged_conditions():
    session, student = session_with_student()
    for i in range(4): add_activity(session, student, hints=2, when=date.today() - timedelta(days=i))
    first = v0350.parent_ha_learning_state(session, student.id)['alerts']
    second = v0350.parent_ha_learning_state(session, student.id)['alerts']
    assert first == second
    assert len({item['id'] for item in first}) == len(first)


def test_weekly_summary_excludes_parent_tests():
    session, student = session_with_student()
    add_activity(session, student, kind='practice')
    add_activity(session, student, kind='parent_test')
    weekly = v0350.parent_ha_learning_state(session, student.id)['weekly']
    assert weekly['activities_completed'] == 1
    assert weekly['days_practised'] == 1


def test_service_token_discovery_includes_new_learning_endpoints():
    data = v0350.ha_service_token_v0350()
    assert data['learning_endpoint'] == '/api/ha/learning'
    assert data['weekly_summary_endpoint'] == '/api/ha/weekly-summary'
    assert data['entity_unique_ids'] == v0350.ENTITY_IDS


def test_restart_safe_state_is_derived_from_persisted_database_rows():
    session, student = session_with_student(); add_activity(session, student)
    first = v0350.parent_ha_learning_state(session, student.id)
    session.expire_all()
    second = v0350.parent_ha_learning_state(session, student.id)
    assert first['daily_learning'] == second['daily_learning']
    assert first['entity_model'] == second['entity_model']
