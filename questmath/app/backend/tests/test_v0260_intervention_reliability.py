from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0260


ROOT = Path(__file__).resolve().parents[4]


def make_client(role: str = 'student'):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='sienna-v0260', password_hash='x', role='student', display_name='Sienna')
    parent = legacy.User(username='parent-v0260', password_hash='x', role='parent', display_name='Stu')
    session.add_all([student, parent]); session.flush()
    session.add(legacy.Setting(
        student_id=student.id, question_count=10, adaptive_mode=True,
        enabled_topics=json.dumps(legacy.LEVEL4_STRANDS), manual_levels='{}',
    ))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()

    def test_db():
        yield session

    v0260.app.dependency_overrides[legacy.db] = test_db
    principal = student if role == 'student' else parent
    client = TestClient(v0260.app, headers={'Authorization': f'Bearer {legacy.token_for(principal)}'})
    return client, session, student, parent


def close(session: Session):
    v0260.app.dependency_overrides.clear()
    session.close()


def add_evidence(session: Session, student: legacy.User, *, first_correct: bool, final_correct: bool,
                 hints: int = 0, session_kind: str = 'practice'):
    worksheet = legacy.Worksheet(
        student_id=student.id, worksheet_date=date.today(), total=1, selected_topic='number',
        session_kind=session_kind, completed_at=datetime.utcnow(), status='completed', score=int(final_correct),
    )
    session.add(worksheet); session.flush()
    question = legacy.Question(
        worksheet_id=worksheet.id, topic='number', skill='VC2M4N06:fact_recall_addition', level=4,
        prompt='Calculate 8 + 5.', answer_type='number', payload=json.dumps({'operation': 'addition'}),
        correct_answer='13', working='Make 10.', position=0, state='answered_correct' if final_correct else 'answered_incorrect',
        hint_count=hints, answered_at=datetime.utcnow(),
    )
    session.add(question); session.flush()
    session.add(legacy.Attempt(
        question_id=question.id, student_id=student.id, answer='13' if first_correct else '12',
        correct=first_correct, attempt_number=1, seconds=10,
    ))
    if final_correct and not first_correct:
        session.add(legacy.Attempt(
            question_id=question.id, student_id=student.id, answer='13', correct=True,
            attempt_number=2, seconds=15,
        ))
    session.commit()
    return worksheet


def test_intervention_creates_a_short_focused_unique_session_with_model_metadata():
    client, session, _, _ = make_client()
    response = client.post('/api/interventions/new', json={'minutes': 5, 'focus': 'subtraction'})
    assert response.status_code == 200
    worksheet = response.json()
    assert worksheet['session_kind'] == 'intervention'
    assert worksheet['target_minutes'] == 5
    assert worksheet['total'] == 5
    assert worksheet['intervention']['focus'] == 'subtraction'
    assert {question['payload']['intervention']['phase'] for question in worksheet['questions']} >= {'check', 'teach', 'practice', 'retrieval'}
    assert all(question['payload']['visual_key'] == f"{worksheet['id']}:{question['id']}" for question in worksheet['questions'])
    assert all(question['payload']['recommended_model'] in ('number-line', 'place-value') for question in worksheet['questions'])
    identities = [legacy.question_identity(question['prompt'], question['payload']) for question in worksheet['questions']]
    assert len(identities) == len(set(identities))
    close(session)


def test_all_intervention_focuses_are_available_and_fact_families_use_inverse_operations():
    client, session, _, _ = make_client()
    capabilities = client.get('/api/v0260/capabilities').json()
    assert capabilities['intervention_focuses'] == list(v0260.INTERVENTION_FOCUSES)
    response = client.post('/api/interventions/new', json={'minutes': 5, 'focus': 'fact_families'})
    assert response.status_code == 200
    questions = response.json()['questions']
    assert any(question['skill'].endswith(':fact_families') for question in questions)
    assert all(question['topic'] == 'algebra' for question in questions)
    close(session)


def test_intervention_reporting_separates_independent_from_supported_completion():
    client, session, student, _ = make_client()
    add_evidence(session, student, first_correct=True, final_correct=True)
    add_evidence(session, student, first_correct=False, final_correct=True)
    add_evidence(session, student, first_correct=True, final_correct=True, hints=1)
    result = client.get('/api/learning/intervention-v0260').json()
    addition = next(item for item in result['focuses'] if item['focus'] == 'addition')
    assert addition['questions'] == 3
    assert addition['independent_accuracy'] == 33
    assert addition['supported_accuracy'] == 100
    assert addition['support_gap'] == 67
    assert addition['status'] == 'needs_support'
    close(session)


def test_reconciled_counts_use_question_state_and_do_not_treat_retries_as_extra_questions():
    client, session, student, _ = make_client()
    worksheet = add_evidence(session, student, first_correct=False, final_correct=True)
    evidence = v0260.worksheet_evidence(worksheet)
    assert evidence == {
        'total': 1, 'answered': 1, 'completed': 1, 'correct': 1, 'incorrect': 0,
        'skipped': 0, 'remaining': 0, 'hints': 0, 'independent_correct': 0,
        'supported_correct': 1, 'independent_accuracy': 0, 'supported_accuracy': 100,
    }
    view = client.get(f'/api/worksheets/{worksheet.id}/view').json()
    assert view['counts']['answered'] == 1
    assert view['counts']['completed'] == 1
    assert view['evidence']['independent_accuracy'] == 0
    assert view['evidence']['supported_accuracy'] == 100
    close(session)


def test_parent_tests_are_excluded_and_parent_cannot_start_a_learner_intervention():
    client, session, student, parent = make_client(role='parent')
    add_evidence(session, student, first_correct=True, final_correct=True)
    parent_test = legacy.Worksheet(
        student_id=parent.id, worksheet_date=date.today(), total=20, selected_topic='number_algebra',
        session_kind='parent_test', completed_at=datetime.utcnow(), status='completed', score=20,
    )
    session.add(parent_test); session.commit()
    denied = client.post('/api/interventions/new', json={'minutes': 5, 'focus': 'auto'})
    assert denied.status_code == 403
    stats = v0260.dashboard_stats_v0260(session, student.id)
    assert stats['evidence_reconciliation']['worksheets'] == 1
    assert stats['evidence_reconciliation']['answered'] == 1
    assert stats['evidence_reconciliation']['parent_tests_excluded'] is True
    close(session)


def test_shared_factory_adds_stable_visual_keys_to_standard_worksheets():
    client, session, _, _ = make_client()
    worksheet = client.post('/api/worksheets/new', json={'topic': 'number_algebra'}).json()
    assert worksheet['questions']
    assert all(question['payload']['visual_key'] == f"{worksheet['id']}:{question['id']}" for question in worksheet['questions'])
    assert all(question['payload']['recommended_model'] for question in worksheet['questions'])
    close(session)


def test_core_worksheet_experience_no_longer_loads_mutation_observer_layers():
    index = (ROOT / 'questmath/app/frontend/index.html').read_text(encoding='utf-8')
    assert '/src/main.tsx' in index
    for legacy_layer in ('v0120.ts', 'v0150.ts', 'v060.ts', 'v070.ts', 'v090.ts', 'v0100.ts', 'v0130.ts', 'v0140.ts', 'v0170.ts'):
        assert legacy_layer not in index
    assignments = (ROOT / 'questmath/app/frontend/src/v080.ts').read_text(encoding='utf-8')
    assert '.question-card' not in assignments
    assert 'alert(' not in assignments
