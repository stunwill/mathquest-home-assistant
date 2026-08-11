from __future__ import annotations

from datetime import date, timedelta

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0150

app = v0150.app
app.version = legacy.APP_VERSION


def _learner_id(user: legacy.User, session: Session) -> int:
    return user.id if user.role == 'student' else v0120.resolve_learner(session).id


def _history_summary(ws: legacy.Worksheet) -> dict:
    summary = v0120.worksheet_summary(ws)
    answered = sum(1 for question in ws.questions if question.attempts)
    correct = sum(1 for question in ws.questions if any(attempt.correct for attempt in question.attempts))
    total = int(summary.get('total') or 0)
    summary.update({
        'answered': answered,
        'score': correct,
        'accuracy': round(correct / answered * 100, 1) if answered else None,
        'incorrect': max(0, answered - correct),
        'progress': round(answered / total * 100, 1) if total else 0,
        'elapsed_seconds': round(float(ws.elapsed_seconds or 0), 1),
        'display_time': ws.started_at.strftime('%-I:%M %p') if ws.started_at else None,
        'display_title': (ws.selected_topic or 'mixed').replace('_', ' ').title(),
    })
    return summary


@app.get('/api/worksheets/history-v0160')
def worksheet_history_v0160(
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    sid = _learner_id(user, session)
    rows = list(session.scalars(
        select(legacy.Worksheet)
        .where(legacy.Worksheet.student_id == sid)
        .order_by(
            legacy.Worksheet.worksheet_date.desc(),
            legacy.Worksheet.started_at.desc(),
            legacy.Worksheet.id.desc(),
        )
    ).all())
    return [_history_summary(ws) for ws in rows]


@app.get('/api/learning/week-v0160')
def learning_week_v0160(
    start: str | None = None,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    sid = _learner_id(user, session)
    try:
        first = date.fromisoformat(start) if start else date.today() - timedelta(days=date.today().weekday())
    except ValueError as exc:
        raise HTTPException(400, 'start must use YYYY-MM-DD') from exc
    last = first + timedelta(days=6)
    rows = list(session.scalars(
        select(legacy.Worksheet)
        .where(
            legacy.Worksheet.student_id == sid,
            legacy.Worksheet.worksheet_date >= first,
            legacy.Worksheet.worksheet_date <= last,
        )
        .order_by(legacy.Worksheet.worksheet_date.asc(), legacy.Worksheet.started_at.asc(), legacy.Worksheet.id.asc())
    ).all())
    grouped: dict[date, list[legacy.Worksheet]] = {}
    for ws in rows:
        grouped.setdefault(ws.worksheet_date, []).append(ws)

    days = []
    for offset in range(7):
        day = first + timedelta(days=offset)
        worksheets = grouped.get(day, [])
        summaries = [_history_summary(ws) for ws in worksheets]
        answered = sum(int(item.get('answered') or 0) for item in summaries)
        correct = sum(int(item.get('score') or 0) for item in summaries)
        hints = sum(int(item.get('hints') or 0) for item in summaries)
        xp = sum(int(item.get('xp_earned') or 0) for item in summaries)
        elapsed = sum(float(item.get('elapsed_seconds') or 0) for item in summaries)
        days.append({
            'date': day.isoformat(),
            'is_today': day == date.today(),
            'is_future': day > date.today(),
            'questions': answered,
            'correct': correct,
            'incorrect': max(0, answered - correct),
            'accuracy': round(correct / answered * 100, 1) if answered else None,
            'hints': hints,
            'xp': xp,
            'elapsed_seconds': round(elapsed, 1),
            'worksheets': summaries,
        })

    return {
        'start': first.isoformat(),
        'end': last.isoformat(),
        'days': days,
    }


@app.get('/api/v0160/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'exact_worksheet_resume': True,
        'weekly_learning_calendar': True,
        'worksheet_day_links': True,
        'worksheet_duration_history': True,
        'twelve_hour_clock_face': True,
        'current_vs_today_progress': True,
    }


v0120._move_spa_fallback_to_end()
