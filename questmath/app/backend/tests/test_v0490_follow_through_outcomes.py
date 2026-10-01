from datetime import datetime
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app import main as legacy, v0230, v0440, v0450, v0460


@pytest.fixture
def learning(tmp_path, monkeypatch):
    # Load the active runtime when exercising it, rather than changing older
    # version routes and generator registries during pytest collection.
    global v0490
    from app import v0490
    engine = create_engine(f'sqlite:///{tmp_path / "learner.db"}', connect_args={'check_same_thread': False})
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    learner = legacy.User(username='outcome-learner', password_hash='x', role='student', display_name='Learner')
    session.add(learner); session.flush()
    session.add(legacy.Setting(student_id=learner.id, question_count=10, adaptive_mode=True, enabled_topics='["number"]', manual_levels='{}'))
    session.commit()
    outcomes = [{'code': 'VC2M4N06', 'title': 'Written subtraction', 'topic': 'number', 'strand': 'Number', 'mastery': 40, 'questions': 4, 'status': 'developing', 'review_due': False, 'target_skill': 'written_subtraction'}]
    recommendation = {'mode': 'practice', 'minutes': 5, 'topic': 'number', 'outcome_code': 'VC2M4N06', 'title': 'Written subtraction', 'reason': 'Keep practising', 'prerequisite_for': None, 'target_skill': 'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    monkeypatch.setattr(v0230, 'next_session_recommendation', lambda *_: dict(recommendation))
    v0490.app.dependency_overrides[legacy.db] = lambda: session
    yield session, learner, engine
    v0490.app.dependency_overrides.clear()
    session.close(); engine.dispose()


def start(session, learner):
    return v0460.compose_targeted_session(session, learner.id, v0460.build_learning_plan(session, learner.id, 5))


def finish(session, learner, worksheet, mode='independent', persist=True):
    for question in worksheet.questions:
        question.answered_at = datetime.utcnow()
        question.state = 'answered_incorrect' if mode == 'wrong' else 'answered_correct'
        if mode in ('supported', 'mentor'):
            if mode == 'supported': question.hint_count = 1
            else: question.mentor_started = True
        session.add(legacy.Attempt(question_id=question.id, student_id=learner.id,
            answer='wrong' if mode == 'wrong' else question.correct_answer, correct=mode != 'wrong', attempt_number=1, seconds=10))
    worksheet.completed_at = datetime.utcnow(); worksheet.status = 'completed'
    session.commit()
    if persist:
        # The production completion path invokes this summary hook.
        v0490.summary(session, worksheet, learner)


def test_reteach_session_is_linked_and_independent_success_changes_direction(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    plan = v0460.build_learning_plan(session, learner.id, 5)
    assert plan['follow_through'] == 'reteach'
    second = v0460.compose_targeted_session(session, learner.id, plan)
    link = session.scalar(select(v0460.FollowThroughOutcome).where(v0460.FollowThroughOutcome.worksheet_id == second.id))
    assert session.get(v0460.AdaptiveFollowThrough, link.source_id).worksheet_id == first.id
    finish(session, learner, second)
    detail = v0460._detail(session, second, learner.id)
    assert detail['intervention_outcome']['assessment'] == 'independence_confirmed'
    assert detail['follow_through'] == 'review_later'
    assert json.loads(link.before_evidence)['independent_successes'] == 0
    assert json.loads(link.after_evidence)['independent_successes'] >= 3
    assert v0460.build_learning_plan(session, learner.id, 5)['follow_through'] != 'reteach'


@pytest.mark.parametrize('mode', ['wrong', 'supported', 'mentor'])
def test_repeated_difficulty_reconsiders_path_without_manufacturing_mastery(learning, mode):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    second = start(session, learner); finish(session, learner, second, mode)
    detail = v0460._detail(session, second, learner.id)
    assert detail['intervention_outcome']['assessment'] == 'reconsider_learning_path'
    assert detail['follow_through'] == 'gather_more_evidence'
    assert detail['evidence']['independent_successes'] == 0
    assert detail['after']['status'] == 'developing'
    if mode != 'wrong': assert detail['evidence']['support_used_questions'] >= 3


def test_support_reduction_is_improvement_but_needs_independent_check(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'supported')
    second = start(session, learner)
    targeted = [q for q in sorted(second.questions, key=lambda q: q.position) if q.skill == 'VC2M4N06:written_subtraction']
    targeted[0].hint_count = 1
    targeted[-1].hint_count = 1
    finish(session, learner, second)
    detail = v0460._detail(session, second, learner.id)
    assert detail['intervention_outcome']['assessment'] == 'improved'
    assert detail['follow_through'] == 'check_independence'
    assert detail['evidence']['independent_checks'] == 0
    third = start(session, learner); finish(session, learner, third)
    assert v0460._detail(session, third, learner.id)['intervention_outcome']['assessment'] == 'independence_confirmed'


def test_unrelated_successes_and_one_check_cannot_erase_target_difficulty(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    second = start(session, learner)
    for question in second.questions:
        meta = v0450._payload(question)['targeted_session']
        correct = question.skill != 'VC2M4N06:written_subtraction' or meta['stage'] == 'check'
        question.state = 'answered_correct' if correct else 'answered_incorrect'
        question.answered_at = datetime.utcnow()
        session.add(legacy.Attempt(question_id=question.id, student_id=learner.id, answer='x', correct=correct, attempt_number=1, seconds=10))
    second.completed_at = datetime.utcnow(); session.commit()
    detail = v0460._detail(session, second, learner.id)
    assert detail['evidence']['independent_successes'] == 1
    assert detail['follow_through'] not in ('challenge', 'progress_to_related_skill', 'review_later')
    assert detail['intervention_outcome']['assessment'] != 'independence_confirmed'


def test_previews_do_not_mutate_consumption_and_duplicate_start_resumes(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    row = session.scalar(select(v0460.AdaptiveFollowThrough))
    client = TestClient(v0490.app)
    headers = {'Authorization': f'Bearer {legacy.token_for(learner)}'}
    for _ in range(2):
        assert client.get('/api/learning/adaptive-v0230', headers=headers).status_code == 200
        assert client.get('/api/learning/session-plan-v0460', headers=headers).status_code == 200
    assert row.consumed_at is None
    assert session.query(v0460.FollowThroughOutcome).count() == 0
    plan = v0460.build_learning_plan(session, learner.id, 5)
    second = v0460.compose_targeted_session(session, learner.id, plan)
    assert v0460.compose_targeted_session(session, learner.id, plan).id == second.id
    assert client.post('/api/sessions/recommended', headers=headers).json()['id'] == second.id
    assert session.query(v0460.FollowThroughOutcome).count() == 1
    assert v0460.build_learning_plan(session, learner.id, 5)['previous_follow_through'] is None


def test_completed_outcome_and_next_decision_survive_new_database_session(learning):
    session, learner, engine = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    second = start(session, learner); finish(session, learner, second)
    sid, wid = learner.id, second.id
    with Session(engine) as restarted:
        detail = v0460._detail(restarted, restarted.get(legacy.Worksheet, wid), sid)
        assert detail['intervention_outcome']['source_worksheet_id'] == first.id
        assert detail['follow_through'] == 'review_later'
        assert v0460.build_learning_plan(restarted, sid, 5)['previous_follow_through']['worksheet_id'] == wid


def test_legacy_preview_does_not_backfill_and_start_is_compatible(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong', persist=False)
    plan = v0460.build_learning_plan(session, learner.id, 5)
    assert session.query(v0460.AdaptiveFollowThrough).count() == 0
    assert plan['follow_through'] == 'reteach'
    second = v0460.compose_targeted_session(session, learner.id, plan)
    assert second.id != first.id
    assert session.query(v0460.FollowThroughOutcome).count() == 1


@pytest.mark.parametrize('changed_family', [False, True])
def test_transfer_requires_changed_family_and_skips_do_not_confirm_independence(learning, changed_family):
    session, learner, _ = learning
    first = start(session, learner)
    for q in first.questions:
        payload = v0450._payload(q); payload['question_family'] = 'familiar'
        q.payload = json.dumps(payload)
    sorted(first.questions, key=lambda q: q.position)[0].hint_count = 1
    finish(session, learner, first)
    source = session.scalar(select(v0460.AdaptiveFollowThrough))
    assert source.decision == 'transfer'
    second = start(session, learner)
    # Familiar forms succeeding again do not confirm transfer.
    for q in second.questions:
        payload = v0450._payload(q)
        payload['question_family'] = 'changed' if changed_family and payload['targeted_session']['stage'] == 'transfer' else 'familiar'
        q.payload = json.dumps(payload)
    session.commit()
    finish(session, learner, second)
    detail = v0460._detail(session, second, learner.id)
    assert detail['follow_through'] == ('review_later' if changed_family else 'consolidate')
    assert detail['intervention_outcome']['assessment'] == ('independence_confirmed' if changed_family else 'transfer_not_confirmed')
    third = start(session, learner)
    third.completed_at = datetime.utcnow()
    for q in third.questions: q.state = 'skipped'; q.skipped_count = 1
    session.commit()
    assert v0460._detail(session, third, learner.id)['follow_through'] == 'gather_more_evidence'


def test_repeated_reteach_uses_smaller_step_then_returns_to_full_independent_check(learning):
    session, learner, _ = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    second = start(session, learner); finish(session, learner, second, 'wrong')
    plan = v0460.build_learning_plan(session, learner.id, 5)
    assert plan['evidence_focus'] == 'subtraction_without_regrouping'
    third = v0460.compose_targeted_session(session, learner.id, plan)
    target = [q for q in third.questions if q.skill == 'VC2M4N06:written_subtraction']
    assert all(v0450._payload(q)['subtraction_case'] == 'no_regroup' for q in target)
    finish(session, learner, third)
    detail = v0460._detail(session, third, learner.id)
    assert detail['intervention_outcome']['assessment'] == 'smaller_step_confirmed'
    assert detail['follow_through'] == 'check_independence'
    assert 'evidence_focus' not in v0460.build_learning_plan(session, learner.id, 5)


def test_completion_api_persists_outcome_and_is_idempotent(learning):
    session, learner, engine = learning
    first = start(session, learner); finish(session, learner, first, 'wrong')
    second = start(session, learner)
    finish(session, learner, second, persist=False)
    second.completed_at = None; session.commit()
    headers = {'Authorization': f'Bearer {legacy.token_for(learner)}'}
    client = TestClient(v0490.app)
    assert client.post(f'/api/worksheets/{second.id}/complete', headers=headers).status_code == 200
    assert client.post(f'/api/worksheets/{second.id}/complete', headers=headers).status_code == 200
    legacy.Base.metadata.create_all(engine)
    assert session.query(v0460.FollowThroughOutcome).count() == 1
    assert session.query(v0460.AdaptiveFollowThrough).count() == 2
    assert session.scalar(select(v0460.FollowThroughOutcome)).evaluated_at is not None
