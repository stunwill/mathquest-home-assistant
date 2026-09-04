from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0321, v0390


def make_session():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='quality-student', password_hash='x', role='student', display_name='Learner')
    session.add(student)
    session.flush()
    session.add(legacy.Setting(student_id=student.id, question_count=6, adaptive_mode=True, enabled_topics='["number"]', manual_levels='{}'))
    session.commit()
    return session, student


def _question(position: int, prompt: str, skill: str, payload: dict | None = None, answered_at=None) -> legacy.Question:
    return legacy.Question(
        worksheet_id=1,
        topic='number',
        skill=skill,
        level=4,
        prompt=prompt,
        answer_type='number',
        payload=json.dumps(payload or {}),
        correct_answer='0',
        working='',
        position=position,
        answered_at=answered_at,
    )


def test_direct_arithmetic_structure_groups_meaningful_near_duplicates_without_collapsing_all_hundreds_addition():
    a = _question(1, 'Calculate 121 + 22.', 'VC2M4N06:written_addition')
    b = _question(2, 'Calculate 132 + 23.', 'VC2M4N06:written_addition')
    c = _question(3, 'Calculate 468 + 357.', 'VC2M4N06:written_addition')
    assert v0390.question_structure(a) == v0390.question_structure(b)
    assert v0390.question_structure(a) == 'direct:addition:3d+2d:regroup0'
    assert v0390.question_structure(c) == 'direct:addition:3d+3d:regroup2'
    assert v0390.question_structure(c) != v0390.question_structure(a)


def test_difficulty_dimensions_capture_operation_digits_and_regrouping():
    q = _question(1, 'Calculate 468 + 357.', 'VC2M4N06:written_addition')
    dimensions = v0390.difficulty_dimensions(q)
    assert dimensions['operation'] == 'addition'
    assert dimensions['left_digits'] == 3
    assert dimensions['right_digits'] == 3
    assert dimensions['regroup_steps'] >= 2


def test_tiny_and_two_digit_arithmetic_are_low_complexity_when_not_purposeful():
    tiny = _question(1, 'Calculate 8 + 8.', 'VC2M4N06:written_addition')
    two_digit = _question(2, 'Calculate 50 + 38.', 'VC2M4N06:written_addition')
    assert v0390._is_low_complexity(tiny) is True
    assert v0390._is_low_complexity(two_digit) is True


def test_purposeful_review_is_not_classified_as_accidental_low_complexity():
    review = _question(
        1,
        'Calculate 8 + 8.',
        'VC2M4N06:written_addition',
        {'learning_purpose': 'review', 'retrieval_item': True},
    )
    assert v0390._purposeful_foundation(review) is True
    assert v0390._is_low_complexity(review) is False


def test_reasoning_structure_uses_reasoning_type_not_numbers():
    q = _question(
        1,
        'Which estimate is most reasonable for 405 + 260?',
        'VC2M4N07:reasonableness_reasoning',
        {'reasoning_type': 'reasonableness'},
    )
    assert v0390.question_structure(q) == 'reasoning:reasonableness'


def test_parent_test_is_not_recomposed():
    session, student = make_session()
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='number',
        session_kind='parent_test',
        total=1,
    )
    session.add(ws)
    session.flush()
    q = legacy.Question(
        worksheet_id=ws.id,
        topic='number',
        skill='VC2M4N06:written_addition',
        level=4,
        prompt='Calculate 8 + 8.',
        answer_type='number',
        payload='{}',
        correct_answer='16',
        working='8 + 8 = 16',
        position=1,
    )
    session.add(q)
    session.commit()
    before = q.prompt
    result = v0390.enforce_session_learning_quality(session, ws, student.id)
    assert result.questions[0].prompt == before
    assert json.loads(result.questions[0].payload) == {}


def test_recent_structure_count_uses_answered_practice_and_adventure_only():
    session, student = make_session()
    for idx, kind in enumerate(['practice', 'adventure', 'parent_test'], start=1):
        ws = legacy.Worksheet(
            student_id=student.id,
            worksheet_date=datetime.utcnow().date(),
            selected_topic='number',
            session_kind=kind,
            total=1,
        )
        session.add(ws)
        session.flush()
        session.add(legacy.Question(
            worksheet_id=ws.id,
            topic='number',
            skill='VC2M4N06:written_addition',
            level=4,
            prompt=f'Calculate {300 + idx} + {120 + idx}.',
            answer_type='number',
            payload='{}',
            correct_answer='0',
            working='',
            position=1,
            answered_at=datetime.utcnow(),
        ))
    current = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='number',
        session_kind='practice',
        total=0,
    )
    session.add(current)
    session.commit()
    counts = v0390._recent_structures(session, student.id, current.id)
    assert sum(counts.values()) == 2


def test_session_policy_replaces_second_near_duplicate_and_records_final_quality_metadata(monkeypatch):
    session, student = make_session()
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='number',
        session_kind='practice',
        total=2,
    )
    session.add(ws)
    session.flush()
    first = legacy.Question(
        worksheet_id=ws.id, topic='number', skill='VC2M4N06:written_addition', level=4,
        prompt='Calculate 321 + 42.', answer_type='number', payload='{}', correct_answer='363', working='', position=1,
    )
    second = legacy.Question(
        worksheet_id=ws.id, topic='number', skill='VC2M4N06:written_addition', level=4,
        prompt='Calculate 342 + 51.', answer_type='number', payload='{}', correct_answer='393', working='', position=2,
    )
    session.add_all([first, second])
    session.commit()

    replacement = ('VC2M4N06:written_subtraction', 'Calculate 684 − 257.', 'number', {}, '427', '684 − 257 = 427')
    monkeypatch.setattr(legacy, 'make_question', lambda *args, **kwargs: replacement)
    monkeypatch.setattr(v0321, 'learner_readiness', lambda *args, **kwargs: {'ready': False, 'attempts': 0, 'accuracy': 0.0})

    result = v0390.enforce_session_learning_quality(session, ws, student.id)
    prompts = [q.prompt for q in sorted(result.questions, key=lambda item: item.position)]
    assert prompts == ['Calculate 321 + 42.', 'Calculate 684 − 257.']
    structures = [json.loads(q.payload)['session_quality']['structure'] for q in result.questions]
    assert len(structures) == len(set(structures))
    for q in result.questions:
        payload = json.loads(q.payload)
        assert 'difficulty_dimensions' in payload
        assert payload['learning_purpose'] in {'current', 'consolidation', 'review', 'challenge'}
        assert 'adaptive_evidence' in payload


def test_adaptive_challenge_budget_remains_limited_after_quality_refresh(monkeypatch):
    session, student = make_session()
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=datetime.utcnow().date(),
        selected_topic='number',
        session_kind='practice',
        total=6,
    )
    session.add(ws)
    session.flush()
    for index in range(6):
        session.add(legacy.Question(
            worksheet_id=ws.id,
            topic='number',
            skill=f'VC2M4N06:skill_{index}',
            level=4,
            prompt=f'Question family {index}?',
            answer_type='number',
            payload='{}',
            correct_answer='1',
            working='',
            position=index + 1,
        ))
    session.commit()
    monkeypatch.setattr(v0321, 'learner_readiness', lambda *args, **kwargs: {'ready': True, 'attempts': 8, 'accuracy': 1.0})
    monkeypatch.setattr(v0390.v0330, '_purpose_for_question', lambda *args, **kwargs: ('challenge', 'ready'))
    monkeypatch.setattr(v0390.v0330, '_question_evidence', lambda *args, **kwargs: {'attempts': 8, 'independent': 8, 'eventual': 1.0, 'support': 0.0, 'misconceptions': 0})
    monkeypatch.setattr(v0390.v0330, '_progression_state', lambda *args, **kwargs: 'ready_to_progress')

    result = v0390.enforce_session_learning_quality(session, ws, student.id)
    purposes = [json.loads(q.payload)['learning_purpose'] for q in result.questions]
    assert purposes.count('challenge') == 1
