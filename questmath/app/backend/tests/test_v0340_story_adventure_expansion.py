from __future__ import annotations

import json
from datetime import datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0230, v0290, v0340


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


def add_evidence(session: Session, student: legacy.User, skill: str, *, correct=True, supported=False, days_ago=0, difficulty_band='instructional'):
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
        payload=json.dumps({'difficulty_band': difficulty_band}),
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


def build_adventure(session: Session, student: legacy.User, count: int = 6, theme: str = 'space', payload_extra: dict | None = None, difficulty_band='instructional'):
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='mixed',
        status='in_progress',
        session_kind='practice',
        target_minutes=5 if count <= 6 else 10 if count <= 12 else 15,
    )
    session.add(ws); session.flush()
    for index in range(count):
        data = {'difficulty_band': difficulty_band, **(payload_extra or {})}
        q = legacy.Question(
            worksheet_id=ws.id,
            topic='number',
            skill='VC2M4N06:written_addition',
            level=4,
            prompt=f'Calculate {240 + index} + 68.',
            answer_type='number',
            payload=json.dumps(data),
            correct_answer=str(308 + index),
            working='Add using place value.',
            position=index,
        )
        session.add(q)
    ws.total = count
    session.commit(); session.refresh(ws)
    result = v0340.apply_adventure_presentation(session, ws, student.id, theme)
    return ws, result


def test_story_adventure_preserves_adaptive_selection_difficulty_and_learning_purpose():
    session, student = make_session()
    ws, result = build_adventure(session, student)
    assert result['questions_linked'] == 6
    for q in ws.questions:
        payload = json.loads(q.payload)
        assert payload['learning_purpose'] in {'current', 'consolidation', 'review', 'challenge'}
        assert payload['adventure']['learning_purpose'] == payload['learning_purpose']
        assert payload['difficulty_band'] == 'instructional'
        assert payload['adventure']['difficulty_band'] == 'instructional'
        assert q.prompt.startswith('Calculate ')
        assert payload['adventure']['version'] == 3
    session.close()


def test_story_adventure_retains_challenge_selected_by_adaptive_engine():
    session, student = make_session()
    for _ in range(8):
        add_evidence(session, student, 'VC2M4N06:written_addition')
    ws, _ = build_adventure(session, student, difficulty_band='challenge')
    purposes = [json.loads(q.payload)['learning_purpose'] for q in ws.questions]
    assert 'challenge' in purposes
    session.close()


def test_insufficient_evidence_does_not_cause_inappropriate_progression():
    session, student = make_session()
    for _ in range(3):
        add_evidence(session, student, 'VC2M4N06:written_addition')
    ws, _ = build_adventure(session, student)
    payloads = [json.loads(q.payload) for q in ws.questions]
    assert all(payload['progression_state'] == 'not_ready' for payload in payloads)
    assert all(payload['learning_purpose'] != 'challenge' for payload in payloads)
    session.close()


def test_supported_success_does_not_false_progress_in_story_adventure():
    session, student = make_session()
    for _ in range(8):
        add_evidence(session, student, 'VC2M4N06:written_addition', supported=True)
    ws, _ = build_adventure(session, student, difficulty_band='challenge')
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
    assert payload['learning_purpose'] in {'review', 'consolidation'}
    assert 'misconception' in payload['adaptive_reason'].lower() or 'spaced retrieval' in payload['adaptive_reason'].lower()
    session.close()


def test_spaced_review_purpose_is_retained_in_story_adventure():
    session, student = make_session()
    for day in range(8, 0, -1):
        add_evidence(session, student, 'VC2M4N06:written_addition', days_ago=day + 8)
    ws, _ = build_adventure(session, student)
    payloads = [json.loads(q.payload) for q in ws.questions]
    assert any(payload['learning_purpose'] == 'review' for payload in payloads)
    assert any('spaced retrieval' in payload['adaptive_reason'].lower() for payload in payloads if payload['learning_purpose'] == 'review')
    session.close()


def test_prerequisite_routing_metadata_survives_story_presentation():
    session, student = make_session()
    ws, _ = build_adventure(
        session,
        student,
        payload_extra={
            'adaptive': {
                'mode': 'guided',
                'outcome_code': 'VC2M4N06',
                'prerequisite_for': 'VC2M4M02',
            }
        },
    )
    stories = [json.loads(q.payload)['adventure'] for q in ws.questions]
    assert all(story['prerequisite_for'] == 'VC2M4M02' for story in stories)
    assert all(story['adaptive_mode'] == 'guided' for story in stories)
    session.close()


def test_story_answers_feed_existing_learning_model_without_duplicate_mastery_system():
    session, student = make_session()
    ws, _ = build_adventure(session, student)
    question = sorted(ws.questions, key=lambda item: item.position)[0]
    question.answered_at = datetime.utcnow()
    session.add(legacy.Attempt(
        question_id=question.id,
        student_id=student.id,
        answer=question.correct_answer,
        correct=True,
        attempt_number=1,
        seconds=12,
    ))
    session.commit()
    evidence = v0340.v0330._question_evidence(session, student.id, question.skill)
    outcomes = {item['code']: item for item in v0230.outcome_mastery(session, student.id)}
    assert evidence['questions'] == 1
    assert evidence['independent'] == 1.0
    assert outcomes['VC2M4N06']['questions'] == 1
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
    with pytest.raises(HTTPException) as exc:
        v0340.apply_adventure_presentation(session, ws, student.id, 'space')
    assert exc.value.status_code == 400
    assert 'Parent Tests' in str(exc.value.detail)
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


@pytest.mark.parametrize(('count', 'minutes'), [(6, 5), (12, 10), (18, 15)])
def test_adventure_uses_existing_session_size(count: int, minutes: int):
    session, student = make_session(question_count=count)
    ws, result = build_adventure(session, student, count=count)
    assert result['questions_linked'] == count
    assert ws.total == count
    assert ws.target_minutes == minutes
    stages = [json.loads(q.payload)['adventure']['stage'] for q in sorted(ws.questions, key=lambda item: item.position)]
    assert stages[0] == 'Start'
    assert stages[-1] == 'Final Challenge'
    session.close()
