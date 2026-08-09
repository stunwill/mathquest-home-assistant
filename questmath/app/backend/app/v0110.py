from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v060, v090, v0100

app = legacy.app
app.version = '0.11.1'

DASHBOARD_CATEGORIES = ('number', 'measurement', 'space', 'algebra', 'probability')


def _student_id(user: legacy.User, session: Session) -> int:
    if user.role == 'student':
        return user.id
    sid = session.scalar(select(legacy.User.id).where(legacy.User.role == 'student'))
    if sid is None:
        raise HTTPException(503, 'MathQuest learner is unavailable')
    return sid


def _iso(dt: datetime | None) -> str | None:
    if not dt:
        return None
    return dt.isoformat()


def _answered_questions(works: list[legacy.Worksheet]) -> list[legacy.Question]:
    return [q for w in works for q in w.questions if q.attempts or q.answered_at]


def _question_correct(q: legacy.Question) -> bool:
    return any(a.correct for a in q.attempts)


def _accuracy(questions: list[legacy.Question]) -> float | None:
    if not questions:
        return None
    return round(sum(1 for q in questions if _question_correct(q)) / len(questions) * 100, 1)


def _category_stats(session: Session, sid: int, topic: str) -> dict[str, Any]:
    adaptive = v060._topic_metrics(session, sid, topic)
    rows = v060._topic_questions(session, sid, topic)
    accuracy = _accuracy(rows)
    skill = session.scalar(select(legacy.Skill).where(legacy.Skill.student_id == sid, legacy.Skill.topic == topic))
    progress = None
    if skill:
        progress = round(max(0, min(8, skill.level)) / 8 * 100)
    return {
        'progress': progress,
        'accuracy': accuracy,
        'questions': adaptive.get('questions', 0),
        'mastery': adaptive.get('mastery'),
    }


def _streak(session: Session, sid: int) -> int:
    completed = {w.worksheet_date for w in session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Worksheet.completed_at.is_not(None))).all()}
    if not completed:
        return 0
    day = date.today()
    if day not in completed:
        day -= timedelta(days=1)
    count = 0
    while day in completed:
        count += 1
        day -= timedelta(days=1)
    return count


def dashboard_stats(session: Session, sid: int) -> dict[str, Any]:
    learner = session.get(legacy.User, sid)
    if not learner:
        raise HTTPException(503, 'MathQuest learner is unavailable')
    today = date.today()
    week_start = today - timedelta(days=6)
    today_works = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Worksheet.worksheet_date == today)).all())
    week_works = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Worksheet.worksheet_date >= week_start, legacy.Worksheet.worksheet_date <= today)).all())
    today_q = _answered_questions(today_works)
    week_q = _answered_questions(week_works)
    today_correct = sum(1 for q in today_q if _question_correct(q))
    week_correct = sum(1 for q in week_q if _question_correct(q))
    adaptive = legacy.dashboard(session, sid).get('adaptive_learning', {})
    recommended = adaptive.get('recommended_topic')
    last_candidates = [x for w in week_works for x in (w.last_active_at, w.completed_at, w.started_at) if x]
    last_activity = max(last_candidates) if last_candidates else None
    categories: dict[str, Any] = {}
    for topic in DASHBOARD_CATEGORIES:
        try:
            categories[topic] = _category_stats(session, sid, topic)
        except Exception:
            categories[topic] = {'progress': None, 'accuracy': None, 'questions': 0, 'mastery': None}
    return {
        'available': True,
        'questions_today': len(today_q),
        'correct_today': today_correct,
        'incorrect_today': len(today_q) - today_correct,
        'accuracy_today': _accuracy(today_q),
        'hints_used_today': sum(q.hint_count or 0 for q in today_q),
        'activities_completed_today': sum(1 for w in today_works if w.completed_at),
        'streak_days': _streak(session, sid),
        'xp_today': sum(w.xp_earned or 0 for w in today_works),
        'xp_total': learner.xp,
        'recommended_topic': recommended.title() if recommended else None,
        'last_activity': _iso(last_activity),
        'app_path': '/',
        'categories': categories,
        'questions_this_week': len(week_q),
        'accuracy_this_week': round(week_correct / len(week_q) * 100, 1) if week_q else None,
        'hints_this_week': sum(q.hint_count or 0 for q in week_q),
        'activities_this_week': sum(1 for w in week_works if w.completed_at),
        'xp_this_week': sum(w.xp_earned or 0 for w in week_works),
    }


def dashboard_summary(stats: dict[str, Any]) -> dict[str, Any]:
    keys = ('available', 'questions_today', 'accuracy_today', 'hints_used_today', 'activities_completed_today', 'streak_days', 'xp_today', 'xp_total', 'recommended_topic', 'last_activity', 'app_path')
    return {k: stats.get(k) for k in keys}


@app.get('/api/ha/stats')
def ha_stats(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    return dashboard_stats(session, _student_id(user, session))


@app.get('/api/ha/summary')
def ha_summary(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    return dashboard_summary(dashboard_stats(session, _student_id(user, session)))


@app.get('/api/v0110/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.11.1',
        'home_assistant_dashboard_api': True,
        'stats_endpoint': '/api/ha/stats',
        'summary_endpoint': '/api/ha/summary',
        'recommended_poll_seconds': 30,
        'native_entities': False,
        'app_path': '/',
    }
