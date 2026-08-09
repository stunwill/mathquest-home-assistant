from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0120


def make_session():
    engine = create_engine('sqlite:///:memory:')
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    return session


def add_student(session, username):
    user = legacy.User(username=username, password_hash='x', role='student', display_name=username, xp=0)
    session.add(user); session.flush()
    session.add(legacy.Setting(student_id=user.id))
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=user.id, topic=topic, level=1))
    session.commit(); return user


def add_completed(session, student, when, topic='number'):
    ws = legacy.Worksheet(student_id=student.id, worksheet_date=date.today(), started_at=when, last_active_at=when, completed_at=when, status='completed', selected_topic=topic, score=1, total=1, xp_earned=10)
    session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic=topic, skill='VC2M4N03:equivalent_fractions', level=1, prompt='1/2 = ?/4', answer_type='number', payload='{}', correct_answer='2', working='Multiply top and bottom by 2.', position=0, state='answered', answered_at=when)
    session.add(q); session.flush()
    session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='2', correct=True, attempt_number=1, seconds=2))
    session.commit(); return ws


def test_parent_resolves_student_with_latest_activity(monkeypatch):
    session = make_session()
    old = add_student(session, 'old-student')
    active = add_student(session, 'student')
    add_completed(session, old, datetime.utcnow() - timedelta(days=2))
    add_completed(session, active, datetime.utcnow())
    assert v0120.resolve_learner(session).id == active.id


def test_history_keeps_multiple_same_day_worksheets_separate():
    session = make_session(); student = add_student(session, 'student')
    first = add_completed(session, student, datetime.utcnow() - timedelta(hours=1), 'number')
    second = add_completed(session, student, datetime.utcnow(), 'measurement')
    rows = session.query(legacy.Worksheet).filter_by(student_id=student.id, worksheet_date=date.today()).all()
    summaries = [v0120.worksheet_summary(w) for w in rows]
    assert len(summaries) == 2
    assert {x['id'] for x in summaries} == {first.id, second.id}
    assert {x['selected_topic'] for x in summaries} == {'number', 'measurement'}


def test_completed_worksheet_summary_contains_score_and_hints():
    session = make_session(); student = add_student(session, 'student')
    ws = add_completed(session, student, datetime.utcnow())
    ws.questions[0].hint_count = 1; session.commit()
    result = v0120.worksheet_summary(ws)
    assert result['score'] == 1 and result['total'] == 1
    assert result['accuracy'] == 100.0 and result['hints'] == 1


def test_existing_active_worksheet_can_be_identified_independently_of_completed_today():
    session = make_session(); student = add_student(session, 'student')
    add_completed(session, student, datetime.utcnow() - timedelta(hours=1))
    active = legacy.Worksheet(student_id=student.id, worksheet_date=date.today(), started_at=datetime.utcnow(), last_active_at=datetime.utcnow(), status='in_progress', selected_topic='mixed', score=0, total=10)
    session.add(active); session.commit()
    row = session.query(legacy.Worksheet).filter(legacy.Worksheet.student_id == student.id, legacy.Worksheet.completed_at.is_(None)).order_by(legacy.Worksheet.started_at.desc()).first()
    assert row.id == active.id


def test_versioned_get_apis_are_before_spa_fallback():
    paths = [getattr(route, 'path', None) for route in v0120.app.router.routes]
    fallback = paths.index('/{path:path}')
    for path in ('/api/worksheets/history', '/api/dashboard/parent-v0120', '/api/ha/stats', '/api/reports/weekly'):
        assert path in paths
        assert paths.index(path) < fallback
