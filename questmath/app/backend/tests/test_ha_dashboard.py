"""v0.11 Home Assistant dashboard integration regression tests.

These tests exercise the pure aggregation helpers with the real SQLite models. They are
kept separate from authentication/HTTP wiring so failures identify statistics regressions.
"""
from datetime import date, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy
from app import v0110


def session_with_student():
    engine = create_engine('sqlite:///:memory:')
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    student = legacy.User(username='student-test', password_hash='x', role='student', display_name='Test Learner', xp=250)
    session.add(student); session.flush()
    for topic in legacy.LEVEL4_STRANDS:
        session.add(legacy.Skill(student_id=student.id, topic=topic, level=4))
    session.commit()
    return session, student


def add_question(session, student, *, topic='number', correct=True, hints=0):
    ws = session.query(legacy.Worksheet).filter_by(student_id=student.id, worksheet_date=date.today()).first()
    if not ws:
        ws = legacy.Worksheet(student_id=student.id, worksheet_date=date.today(), total=1, status='in_progress', last_active_at=datetime.now())
        session.add(ws); session.flush()
    q = legacy.Question(worksheet_id=ws.id, topic=topic, skill='VC2M4N03:equivalent_fractions', level=1, prompt='Test?', answer_type='text', payload='{}', correct_answer='1', working='', position=len(ws.questions)+1, state='answered', hint_count=hints, answered_at=datetime.now())
    session.add(q); session.flush()
    session.add(legacy.Attempt(question_id=q.id, student_id=student.id, answer='1' if correct else '0', correct=correct, attempt_number=1, seconds=2))
    ws.total = len(ws.questions); ws.score = sum(1 for x in ws.questions if any(a.correct for a in x.attempts)); ws.xp_earned = ws.score * 10
    session.commit(); return ws, q


def test_zero_activity_today():
    s,u=session_with_student(); d=v0110.dashboard_stats(s,u.id)
    assert d['questions_today']==0 and d['accuracy_today'] is None and d['last_activity'] is None


def test_accuracy_and_category_statistics():
    s,u=session_with_student(); add_question(s,u,correct=True); add_question(s,u,correct=False)
    d=v0110.dashboard_stats(s,u.id)
    assert d['questions_today']==2 and d['correct_today']==1 and d['incorrect_today']==1 and d['accuracy_today']==50.0
    assert d['categories']['number']['questions']==2 and d['categories']['number']['accuracy']==50.0


def test_hint_updates_dashboard():
    s,u=session_with_student(); add_question(s,u,correct=True,hints=2)
    assert v0110.dashboard_stats(s,u.id)['hints_used_today']==2


def test_completed_activity_and_last_activity():
    s,u=session_with_student(); ws,_=add_question(s,u)
    ws.completed_at=datetime.now(); ws.status='completed'; s.commit()
    d=v0110.dashboard_stats(s,u.id)
    assert d['activities_completed_today']==1 and d['last_activity'] is not None


def test_summary_is_compact():
    s,u=session_with_student(); add_question(s,u)
    summary=v0110.dashboard_summary(v0110.dashboard_stats(s,u.id))
    assert 'categories' not in summary and summary['questions_today']==1 and summary['app_path']=='/'


def test_missing_optional_category_data_does_not_break_response():
    s,u=session_with_student(); d=v0110.dashboard_stats(s,u.id)
    assert set(v0110.DASHBOARD_CATEGORIES).issubset(d['categories'])
    assert d['categories']['probability']['mastery']==0
