from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0290, v0340


def make_session(question_count: int = 6):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='story-v0340', password_hash='x', role='student', display_name='Story Learner')
    session.add(student); session.flush()
    session.add(legacy.Setting(
        student_id=student.id,
        question_count=question_count,
        adaptive_mode=True,
        enabled_topics=json.dumps(legacy.LEVEL4_STRANDS),
        manual_levels='{}',
    ))
    session.commit()
    return session, student


def add_evidence(session: Session, student: legacy.User, skill: str, *, correct=True, supported=False, days_ago=0):
    when = datetime.utcnow() - timedelta(days=days_ago)
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=when.date(),
        selected_topic='number',
        status='completed',
        completed_at=when,
        session_kind='practice',
    )
    session.add(ws); session.flush()
    q = legacy.Question(
        worksheet_id=ws.id,
        topic='number',
        skill=skill,
        level=4,
        prompt='Calculate 247 + 68.',
        answer_type='number',
        payload=json.dumps({'difficulty_band': 'instructional'}),
        correct_answer='315',
        working='work',
        position=0,
        answered_at=when,
        hint_count=1 if supported else 0,
        mentor_started=supported,
    )
    session.add(q); session.flush()
    session.add(legacy.Attempt(
        question_id=q.id,
        student_id=student.id,
        answer='315' if correct else '300',
        correct=correct,
        attempt_number=1,
        seconds=10,
    ))
    session.commit()
    return q


def build_adventure(session: Session, student: legacy.User, count: int = 6, theme: str = 'space'):
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='mixed',
        status='in_progress',
        session_kind='practice',
        target_minutes=5 if count <= 5 else 10 if count <= 10 else 15,
    )
    session.add(ws); session.flush()
    for index in range(count):
        q = legacy.Question(
            worksheet_id=ws.id,
            topic='number',
            skill='VC2M4N06:written_addition',
            level=4,
            prompt=f'Calculate {240 + index} + 68.',
            answer_type='number',
            payload=json.dumps({'difficulty_band': 'instructional'}),
            correct_answer=str(308 + index),
            working='Add using place value.',
            position=index,
        )
        session.add(q)
    ws.total = count
    session.commit(); session.refresh(ws)
    result = v0340.apply_adventure_presentation(session, ws, student.id, theme)
    return ws, result


def test_story_adventure_preserves_adaptive_selection_and_learning_purpose():
    session, student = make_session()
    ws, result = build_adventure(session, student)
    assert result['questions_linked'] == 6
    for q in ws.questions:
        payload = json.loads(q.payload)
        assert payload['learning_purpose'] in {'current', 'consolidation', 'review', 'challenge'}
        assert payload['adventure']['learning_purpose'] == payload['learning_purpose']
        assert q.prompt.startswith('Calculate ')
        assert payload['adventure']['version'] == 3
    session.close()


def test_story_adventure_can_retain_challenge_after_strong_independent_evidence():
    session, student = make_session()
    for _ in range(8):
        add_evidence(session, student, 'VC2M4N06:written_addition')
    ws, _ = build_adventure(session, student)
    purposes = [json.loads(q.payload)['learning_purpose'] for q in ws.questions]
    assert 'challenge' in purposes
    session.close()


def test_supported_success_does_not_false_progress_in_story_adventure():
    session, student = make_session()
    for _ in range(8):
        add_evidence(session, student, 'VC2M4N06:written_addition', supported=True)
    ws, _ = build_adventure(session, student)
    purposes = [json.loads(q.payload)['learning_purpose'] for q in ws.questions]
    assert 'challenge' not in purposes
    assert 'consolidation' in purposes
    session.close()


def test_misconception_repair_is_retained_in_story_adventure():
    session, student = make_session()
    q = add_evidence(session, student, 'VC2M4N06:written_addition')
    for _ in range(2):
        session.add(v0290.MisconceptionEvidence(
            student_id=student.id,
            question_id=q.id,
            skill=q.skill,
            misconception_type='regrouping_error',
            message='Regrouping issue',
            resolved=False,
        ))
    session.commit()
    ws, _ = build_adventure(session, student)
    payload = json.loads(sorted(ws.questions, key=lambda item: item.position)[0].payload)
    assert payload['learning_purpose'] == 'consolidation'
    assert 'misconception' in payload['adaptive_reason'].lower()
    session.close()


def test_story_completion_does_not_change_mastery_without_answer_evidence():
    session, student = make_session()
    ws, _ = build_adventure(session, student)
    before = v0340.v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    ws.status = 'completed'; ws.completed_at = datetime.utcnow(); session.commit()
    after = v0340.v0330._question_evidence(session, student.id, 'VC2M4N06:written_addition')
    assert before == after
    session.close()


def test_parent_tests_cannot_become_story_adventures():
    session, student = make_session()
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='number',
        status='in_progress',
        session_kind='parent_test',
    )
    session.add(ws); session.commit()
    with pytest.raises(Exception) as exc:
        v0340.apply_adventure_presentation(session, ws, student.id, 'space')
    assert 'Parent Tests' in str(exc.value)
    session.close()


def test_adventure_resume_is_idempotent_and_keeps_same_session():
    session, student = make_session()
    ws, _ = build_adventure(session, student, theme='camping')
    first_id = ws.id
    first_prompts = [q.prompt for q in sorted(ws.questions, key=lambda item: item.position)]
    v0340.apply_adventure_presentation(session, ws, student.id, 'camping')
    assert ws.id == first_id
    assert [q.prompt for q in sorted(ws.questions, key=lambda item: item.position)] == first_prompts
    assert all(json.loads(q.payload)['adventure']['mission_id'] == f'camping-{first_id}' for q in ws.questions)
    session.close()


def test_short_adventure_uses_existing_short_session_size():
    session, student = make_session(question_count=4)
    ws, result = build_adventure(session, student, count=4)
    assert result['questions_linked'] == 4
    assert ws.total == 4
    stages = [json.loads(q.payload)['adventure']['stage'] for q in sorted(ws.questions, key=lambda item: item.position)]
    assert stages[0] == 'Start'
    assert stages[-1] == 'Final Challenge'
    session.close()
