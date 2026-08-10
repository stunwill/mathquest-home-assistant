from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0160


def make_session():
    engine = create_engine('sqlite:///:memory:')
    legacy.Base.metadata.create_all(engine)
    return Session(engine)


def add_student(session):
    user = legacy.User(username='student-v0160', password_hash='x', role='student', display_name='Learner', xp=0)
    session.add(user); session.flush()
    session.add(legacy.Setting(student_id=user.id))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=user.id, topic=topic, level=1))
    session.commit(); return user


def add_worksheet(session, student, when, answered=3, correct=2, completed=False, elapsed=420):
    ws = legacy.Worksheet(
        student_id=student.id,
        worksheet_date=when.date(),
        started_at=when,
        last_active_at=when,
        completed_at=when if completed else None,
        status='completed' if completed else 'in_progress',
        selected_topic='measurement',
        score=correct,
        total=20,
        xp_earned=50 if completed else 0,
        elapsed_seconds=elapsed,
    )
    session.add(ws); session.flush()
    for position in range(20):
        state = 'answered' if position < answered else ('active' if position == answered else 'not_started')
        q = legacy.Question(
            worksheet_id=ws.id, topic='measurement', skill='VC2M4M03:visual_clock', level=1,
            prompt=f'Question {position}', answer_type='choice', payload='{}', correct_answer='4:45',
            working='Read the clock.', position=position, state=state,
            answered_at=when if position < answered else None,
        )
        session.add(q); session.flush()
        if position < answered:
            is_correct = position < correct
            session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='4:45' if is_correct else '5:45', correct=is_correct, attempt_number=1, seconds=2))
        if position == answered:
            ws.current_question_id = q.id
    session.commit(); return ws


def test_history_summary_exposes_progress_duration_and_status():
    session=make_session(); student=add_student(session)
    ws=add_worksheet(session,student,datetime.utcnow(),answered=5,correct=4,completed=False,elapsed=601)
    result=v0160._history_summary(ws)
    assert result['answered']==5
    assert result['score']==4
    assert result['incorrect']==1
    assert result['progress']==25.0
    assert result['elapsed_seconds']==601.0
    assert result['display_title']=='Measurement'


def test_week_endpoint_is_registered_before_spa_fallback_when_present():
    paths=[getattr(route,'path',None) for route in v0160.app.router.routes]
    assert '/api/worksheets/history-v0160' in paths
    assert '/api/learning/week-v0160' in paths
    if '/{path:path}' in paths:
        fallback=paths.index('/{path:path}')
        assert paths.index('/api/worksheets/history-v0160') < fallback
        assert paths.index('/api/learning/week-v0160') < fallback


def test_completed_and_in_progress_worksheets_remain_distinct():
    session=make_session(); student=add_student(session)
    first=add_worksheet(session,student,datetime.utcnow()-timedelta(hours=1),answered=20,correct=18,completed=True)
    second=add_worksheet(session,student,datetime.utcnow(),answered=3,correct=3,completed=False)
    completed=v0160._history_summary(first)
    active=v0160._history_summary(second)
    assert completed['completed_at'] is not None
    assert active['completed_at'] is None
    assert active['progress']==15.0
