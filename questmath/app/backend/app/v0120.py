from __future__ import annotations

import os
from datetime import date

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0100, v0110

app = legacy.app
app.version = '0.14.0'


class NewWorksheetIn(BaseModel):
    topic: str = 'mixed'


def resolve_learner(session: Session) -> legacy.User:
    """Resolve the learner whose data parents and integrations should display."""
    latest = session.scalar(
        select(legacy.Worksheet)
        .join(legacy.User, legacy.User.id == legacy.Worksheet.student_id)
        .where(legacy.User.role == 'student')
        .order_by(legacy.Worksheet.last_active_at.desc(), legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())
    )
    if latest:
        learner = session.get(legacy.User, latest.student_id)
        if learner:
            return learner
    configured = os.getenv('STUDENT_USERNAME', 'student')
    learner = session.scalar(select(legacy.User).where(legacy.User.role == 'student', legacy.User.username == configured))
    if learner:
        return learner
    learner = session.scalar(select(legacy.User).where(legacy.User.role == 'student').order_by(legacy.User.id.desc()))
    if not learner:
        raise HTTPException(503, 'MathQuest learner is unavailable')
    return learner


def student_id(user: legacy.User, session: Session) -> int:
    return user.id if user.role == 'student' else resolve_learner(session).id


def worksheet_summary(ws: legacy.Worksheet) -> dict:
    view = legacy.worksheet_view(ws)
    answered = view['counts']['correct'] + view['counts']['incorrect']
    return {
        'id': ws.id,
        'date': ws.worksheet_date.isoformat(),
        'started_at': ws.started_at.isoformat() if ws.started_at else None,
        'completed_at': ws.completed_at.isoformat() if ws.completed_at else None,
        'status': ws.status or ('completed' if ws.completed_at else 'in_progress'),
        'selected_topic': ws.selected_topic or 'mixed',
        'score': ws.score,
        'total': ws.total,
        'answered': answered,
        'accuracy': round(ws.score / answered * 100, 1) if answered else None,
        'xp_earned': ws.xp_earned,
        'hints': view['counts']['hints'],
        'is_today': ws.worksheet_date == date.today(),
        'is_previous_unfinished': ws.worksheet_date < date.today() and ws.completed_at is None,
    }


def create_worksheet(session: Session, sid: int, selected: str) -> legacy.Worksheet:
    return legacy.create_worksheet(session, sid, selected)


def today_worksheets(session: Session, sid: int) -> list[legacy.Worksheet]:
    return list(session.scalars(
        select(legacy.Worksheet)
        .where(legacy.Worksheet.student_id == sid, legacy.Worksheet.worksheet_date == date.today())
        .order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())
    ).all())


def today_active_worksheet(session: Session, sid: int) -> legacy.Worksheet | None:
    """Return only an unfinished worksheet belonging to today's calendar date."""
    return session.scalar(
        select(legacy.Worksheet)
        .where(
            legacy.Worksheet.student_id == sid,
            legacy.Worksheet.worksheet_date == date.today(),
            legacy.Worksheet.completed_at.is_(None),
        )
        .order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())
    )


def previous_unfinished_worksheets(session: Session, sid: int) -> list[legacy.Worksheet]:
    return list(session.scalars(
        select(legacy.Worksheet)
        .where(
            legacy.Worksheet.student_id == sid,
            legacy.Worksheet.worksheet_date < date.today(),
            legacy.Worksheet.completed_at.is_(None),
        )
        .order_by(legacy.Worksheet.worksheet_date.desc(), legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())
    ).all())


@app.get('/api/dashboard/parent-v0120')
def parent_dashboard_v0120(_: legacy.User = Depends(legacy.parent), session: Session = Depends(legacy.db)):
    learner = resolve_learner(session)
    data = legacy.dashboard(session, learner.id)
    today = today_worksheets(session, learner.id)
    stale = previous_unfinished_worksheets(session, learner.id)
    data['resolved_learner'] = {'id': learner.id, 'username': learner.username, 'display_name': learner.display_name}
    data['today_worksheets'] = [worksheet_summary(w) for w in today]
    data['previous_unfinished_worksheets'] = [worksheet_summary(w) for w in stale]
    data['today_summary'] = {
        'worksheets': len(today),
        'completed': sum(1 for w in today if w.completed_at),
        'questions': sum(worksheet_summary(w)['answered'] for w in today),
        'correct': sum(legacy.worksheet_view(w)['counts']['correct'] for w in today),
        'hints': sum(legacy.worksheet_view(w)['counts']['hints'] for w in today),
        'xp': sum(w.xp_earned or 0 for w in today),
        'previous_unfinished': len(stale),
    }
    attempted = data['today_summary']['questions']
    data['today_summary']['accuracy'] = round(data['today_summary']['correct'] / attempted * 100, 1) if attempted else None
    return data


@app.get('/api/reports/weekly-v0120')
def weekly_report_v0120(_: legacy.User = Depends(legacy.parent), session: Session = Depends(legacy.db)):
    return v0100.weekly_report(session, resolve_learner(session).id)


@app.get('/api/worksheets/history')
def worksheet_history(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = student_id(user, session)
    rows = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid).order_by(legacy.Worksheet.worksheet_date.desc(), legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())).all())
    return [worksheet_summary(ws) for ws in rows]


@app.get('/api/worksheets/{worksheet_id}/review')
def worksheet_review(worksheet_id: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = student_id(user, session)
    ws = session.get(legacy.Worksheet, worksheet_id)
    if not ws or ws.student_id != sid:
        raise HTTPException(404, 'Worksheet not found')
    if not ws.completed_at:
        raise HTTPException(409, 'Worksheet is still in progress')
    view = legacy.worksheet_view(ws)
    raw_questions = sorted(ws.questions, key=lambda x: x.position)
    for question_view, raw in zip(view['questions'], raw_questions):
        attempts = sorted(raw.attempts, key=lambda x: x.attempt_number)
        question_view['student_answers'] = [{'answer': a.answer, 'correct': a.correct, 'attempt_number': a.attempt_number} for a in attempts]
        question_view['correct_answer'] = raw.correct_answer
        question_view['working'] = raw.working
    return view


@app.get('/api/worksheets/{worksheet_id}/view')
def worksheet_view_any(worksheet_id: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    """Read a worksheet without changing its date or current/today status."""
    sid = student_id(user, session)
    ws = session.get(legacy.Worksheet, worksheet_id)
    if not ws or ws.student_id != sid:
        raise HTTPException(404, 'Worksheet not found')
    return legacy.worksheet_view(ws)


@app.post('/api/worksheets/new')
def new_worksheet(payload: NewWorksheetIn, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    # An unfinished worksheet from a previous day must never block a new worksheet today.
    active_today = today_active_worksheet(session, user.id)
    if active_today:
        return legacy.worksheet_view(active_today)
    return legacy.worksheet_view(create_worksheet(session, user.id, payload.topic))


@app.get('/api/worksheets/active/latest')
def latest_active(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    # This endpoint is consumed by the student hero. It is intentionally TODAY-only.
    ws = today_active_worksheet(session, user.id)
    return legacy.worksheet_view(ws) if ws else None


@app.get('/api/worksheets/unfinished/previous')
def unfinished_previous(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = student_id(user, session)
    return [worksheet_summary(ws) for ws in previous_unfinished_worksheets(session, sid)]


@app.get('/api/v0120/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.14.0',
        'multiple_worksheets_per_day': True,
        'completed_worksheet_review': True,
        'worksheet_history': True,
        'parent_history': True,
        'consolidated_learner_resolution': True,
        'today_state_is_date_scoped': True,
        'previous_unfinished_are_separate': True,
    }


def _move_spa_fallback_to_end() -> None:
    """Ensure versioned JSON APIs are matched before the production SPA fallback."""
    routes = app.router.routes
    for index, route in enumerate(list(routes)):
        if getattr(route, 'path', None) == '/{path:path}':
            routes.append(routes.pop(index))
            break


_move_spa_fallback_to_end()
