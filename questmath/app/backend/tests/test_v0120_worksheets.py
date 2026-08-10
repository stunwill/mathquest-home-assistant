from datetime import date, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0110, v0120


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


def add_completed(session, student, when, topic='number', worksheet_date=None):
    ws = legacy.Worksheet(student_id=student.id, worksheet_date=worksheet_date or date.today(), started_at=when, last_active_at=when, completed_at=when, status='completed', selected_topic=topic, score=1, total=1, xp_earned=10)
    session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic=topic, skill='VC2M4N03:equivalent_fractions', level=1, prompt='1/2 = ?/4', answer_type='number', payload='{}', correct_answer='2', working='Multiply top and bottom by 2.', position=0, state='answered', answered_at=when)
    session.add(q); session.flush()
    session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='2', correct=True, attempt_number=1, seconds=2))
    session.commit(); return ws


def add_active(session, student, worksheet_date, answered=0):
    when = datetime.utcnow()
    ws = legacy.Worksheet(student_id=student.id, worksheet_date=worksheet_date, started_at=when, last_active_at=when, status='in_progress', selected_topic='number', score=answered, total=20)
    session.add(ws); session.flush()
    for position in range(20):
        q = legacy.Question(worksheet_id=ws.id, topic='number', skill='VC2M4N03:equivalent_fractions', level=1, prompt=f'Q{position}', answer_type='number', payload='{}', correct_answer='2', working='Work it out.', position=position, state='answered' if position < answered else ('active' if position == answered else 'not_started'), answered_at=when if position < answered else None)
        session.add(q); session.flush()
        if position < answered:
            session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='2', correct=True, attempt_number=1, seconds=1))
        if position == answered:
            ws.current_question_id = q.id
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


def test_previous_unfinished_is_not_todays_active_worksheet():
    session = make_session(); student = add_student(session, 'student')
    old = add_active(session, student, date.today() - timedelta(days=4), answered=3)
    assert v0120.today_active_worksheet(session, student.id) is None
    previous = v0120.previous_unfinished_worksheets(session, student.id)
    assert [w.id for w in previous] == [old.id]


def test_today_active_worksheet_is_selected_without_old_interference():
    session = make_session(); student = add_student(session, 'student')
    add_active(session, student, date.today() - timedelta(days=4), answered=3)
    today = add_active(session, student, date.today(), answered=2)
    assert v0120.today_active_worksheet(session, student.id).id == today.id


def test_ha_stats_do_not_count_old_unfinished_as_today():
    session = make_session(); student = add_student(session, 'student')
    add_active(session, student, date.today() - timedelta(days=4), answered=3)
    stats = v0110.dashboard_stats(session, student.id)
    assert stats['questions_today'] == 0
    assert stats['activities_completed_today'] == 0
    assert stats['quest_today']['exists'] is False
    assert stats['quest_today']['status'] == 'not_started'
    assert stats['quest_today']['questions_answered'] == 0
    assert stats['unfinished_previous_worksheets'] == 1


def test_ha_stats_report_only_todays_active_progress():
    session = make_session(); student = add_student(session, 'student')
    add_active(session, student, date.today() - timedelta(days=4), answered=3)
    today = add_active(session, student, date.today(), answered=2)
    stats = v0110.dashboard_stats(session, student.id)
    assert stats['questions_today'] == 2
    assert stats['quest_today']['worksheet_id'] == today.id
    assert stats['quest_today']['questions_answered'] == 2
    assert stats['unfinished_previous_worksheets'] == 1


def test_versioned_get_apis_are_registered_before_spa_fallback_when_present():
    paths = [getattr(route, 'path', None) for route in v0120.app.router.routes]
    api_paths = ('/api/worksheets/history', '/api/dashboard/parent-v0120', '/api/ha/stats', '/api/reports/weekly', '/api/worksheets/unfinished/previous')
    for path in api_paths:
        assert path in paths
    if '/{path:path}' in paths:
        fallback = paths.index('/{path:path}')
        for path in api_paths:
            assert paths.index(path) < fallback
