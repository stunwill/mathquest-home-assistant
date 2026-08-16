from __future__ import annotations

import json
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0260


def test_managed_credentials_update_existing_accounts_without_changing_ids_or_data():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    with Session(engine) as session:
        parent = legacy.User(username='parent', password_hash=legacy.pwd.hash('old-parent'), role='parent', display_name='Parent')
        student = legacy.User(username='student', password_hash=legacy.pwd.hash('old-student'), role='student', display_name='Sienna')
        session.add_all([parent, student]); session.flush()
        worksheet = legacy.Worksheet(student_id=student.id, worksheet_date=legacy.date.today(), total=0)
        session.add(worksheet); session.commit()
        parent_id, student_id, worksheet_id = parent.id, student.id, worksheet.id

        updated_parent = legacy._managed_user(session, 'parent', 'stu', 'new-parent', 'Parent')
        updated_student = legacy._managed_user(session, 'student', 'sienna', 'new-student', 'Sienna')
        session.commit()

        assert updated_parent.id == parent_id
        assert updated_student.id == student_id
        assert legacy.pwd.verify('new-parent', updated_parent.password_hash)
        assert legacy.pwd.verify('new-student', updated_student.password_hash)
        assert session.get(legacy.Worksheet, worksheet_id).student_id == student_id
        assert len(session.query(legacy.User).filter(legacy.User.role == 'parent').all()) == 1
        assert len(session.query(legacy.User).filter(legacy.User.role == 'student').all()) == 1


def test_managed_credentials_reuse_a_valid_hash():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    with Session(engine) as session:
        original_hash = legacy.pwd.hash('same-password')
        user = legacy.User(username='parent', password_hash=original_hash, role='parent', display_name='Parent')
        session.add(user); session.commit()
        updated = legacy._managed_user(session, 'parent', 'parent', 'same-password', 'Parent')
        assert updated.password_hash == original_hash


def test_recent_learner_questions_are_avoided_but_parent_tests_are_not_learning_history():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    with Session(engine) as session:
        student = legacy.User(username='student', password_hash='x', role='student', display_name='Sienna')
        parent = legacy.User(username='parent', password_hash='x', role='parent', display_name='Parent')
        session.add_all([student, parent]); session.flush()
        session.add(legacy.Setting(student_id=student.id, question_count=5, enabled_topics=json.dumps(legacy.LEVEL4_STRANDS)))
        for topic in legacy.LEVEL4_STRANDS:
            session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
        session.commit()

        first = legacy.create_worksheet(session, student.id, 'number', question_count=5)
        first_keys = {legacy.question_identity(q.prompt, json.loads(q.payload)) for q in first.questions}
        second = legacy.create_worksheet(session, student.id, 'number', question_count=5)
        second_keys = {legacy.question_identity(q.prompt, json.loads(q.payload)) for q in second.questions}
        assert first_keys.isdisjoint(second_keys)

        parent_test = legacy.create_worksheet(
            session, parent.id, 'number', question_count=5, session_kind='parent_test', learning_profile_id=student.id,
        )
        assert parent_test.total == 5


def test_rotational_symmetry_questions_receive_a_question_owned_visual():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    with Session(engine) as session:
        user = legacy.User(username='student', password_hash='x', role='student', display_name='Sienna')
        session.add(user); session.flush()
        worksheet = legacy.Worksheet(student_id=user.id, worksheet_date=legacy.date.today(), total=1)
        session.add(worksheet); session.flush()
        question = legacy.Question(
            worksheet_id=worksheet.id, topic='space', skill='VC2M4SP04:rotational_symmetry', level=4,
            prompt='Does a regular 6-sided polygon have rotational symmetry?', answer_type='choice',
            payload=json.dumps({'choices': ['yes', 'no']}), correct_answer='yes', working='Compare after a turn.', position=0,
        )
        session.add(question); session.flush()
        v0260._annotate_question(question, worksheet)
        payload = json.loads(question.payload)
        assert payload['visual'] == {'type': 'rotational_symmetry', 'sides': 6}
        assert payload['visual_key'] == f'{worksheet.id}:{question.id}'


def test_statistical_survey_generator_has_multiple_valid_variants():
    prompts = {legacy.make_question('statistics', 4, random.Random(seed))[1] for seed in range(100)}
    assert len({prompt for prompt in prompts if 'survey' in prompt.lower() or 'statistical' in prompt.lower() or 'varied' in prompt.lower()}) >= 3
