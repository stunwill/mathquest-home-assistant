import json
import random
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0150


def make_session():
    engine = create_engine('sqlite:///:memory:')
    legacy.Base.metadata.create_all(engine)
    return Session(engine)


def add_student(session):
    user = legacy.User(username='student-v0150', password_hash='x', role='student', display_name='Learner', xp=0)
    session.add(user); session.flush()
    session.add(legacy.Setting(student_id=user.id, question_count=3, enabled_topics='["measurement"]'))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=user.id, topic=topic, level=1))
    session.commit()
    return user


def test_clock_question_has_visual_and_unique_choices():
    result = v0150._simple_clock(random.Random(4))
    _, prompt, answer_type, payload, answer, _ = result
    assert prompt == 'What time is shown on the analogue clock?'
    assert answer_type == 'choice'
    assert payload['visual']['type'] == 'clock'
    assert len(payload['choices']) == len(set(payload['choices']))
    assert payload['choices'].count(answer) == 1


def test_angle_question_is_diagram_based():
    result = v0150._simple_angle(random.Random(7))
    _, prompt, answer_type, payload, answer, _ = result
    assert prompt == 'What type of angle is shown?'
    assert answer_type == 'choice'
    assert payload['visual']['type'] == 'angle'
    assert 0 < payload['visual']['degrees'] <= 180
    assert answer in payload['choices']


def test_choice_deduplication_keeps_correct_once():
    payload = v0150._dedupe_choices({'choices': ['degrees Celsius', 'litres', 'degrees Celsius']}, 'degrees Celsius')
    assert payload['choices'].count('degrees Celsius') == 1
    assert len(payload['choices']) == len(set(payload['choices']))


def test_new_worksheet_creates_second_same_day_worksheet(monkeypatch):
    session = make_session(); student = add_student(session)
    counter = {'n': 0}

    def generator(topic, level, rng):
        counter['n'] += 1
        n = counter['n']
        return legacy.q('VC2M4M03', f'generated_{n}', f'Question {n}?', 'choice', {'choices': [f'A{n}', f'B{n}', f'C{n}']}, f'A{n}', 'Working')

    monkeypatch.setattr(legacy, 'make_question', generator)
    first = legacy.create_worksheet(session, student.id, 'measurement')
    second = legacy.create_worksheet(session, student.id, 'measurement')
    rows = session.query(legacy.Worksheet).filter_by(student_id=student.id, worksheet_date=date.today()).all()
    assert len(rows) == 2
    assert second.id != first.id
    assert first.completed_at is None


def test_worksheet_retries_duplicate_prompts(monkeypatch):
    session = make_session(); student = add_student(session)
    calls = {'n': 0}

    def generator(topic, level, rng):
        calls['n'] += 1
        # The first two candidates are identical. The worksheet builder must retry.
        n = 1 if calls['n'] <= 2 else calls['n']
        return legacy.q('VC2M4M01', f'unit_{n}', f'Unique prompt {n}', 'choice', {'choices': ['one', 'two', 'three']}, 'one', 'Working')

    monkeypatch.setattr(legacy, 'make_question', generator)
    ws = legacy.create_worksheet(session, student.id, 'measurement')
    prompts = [q.prompt for q in ws.questions]
    assert len(prompts) == len(set(prompts))
    assert calls['n'] > len(prompts)


def test_level_one_measurement_area_is_deferred(monkeypatch):
    def area_generator(topic, level, rng):
        return legacy.q('VC2M4M02', 'area', 'A rectangle is 7 cm by 12 cm. What is its area?', 'number', {'unit': 'cm²'}, '84', '7 × 12')

    monkeypatch.setattr(v0150, '_prior_make_question', area_generator)
    skill, prompt, _, payload, _, _ = v0150.make_question_v0150('measurement', 1, random.Random(3))
    assert skill.endswith('visual_clock')
    assert prompt == 'What time is shown on the analogue clock?'
    assert payload['visual']['type'] == 'clock'
