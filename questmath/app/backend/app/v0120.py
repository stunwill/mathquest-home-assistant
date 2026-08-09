from __future__ import annotations

import json
import os
import random
from datetime import date, datetime

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0100, v0110

app = legacy.app
app.version = '0.12.1'


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
        'accuracy': round(ws.score / ws.total * 100, 1) if ws.total else None,
        'xp_earned': ws.xp_earned,
        'hints': view['counts']['hints'],
    }


def create_worksheet(session: Session, sid: int, selected: str) -> legacy.Worksheet:
    settings = legacy.student_settings(session, sid)
    enabled = json.loads(settings.enabled_topics)
    levels = json.loads(settings.manual_levels)
    selected = (selected or 'mixed').lower()
    if selected != 'mixed' and selected not in legacy.LEVEL4_STRANDS:
        raise HTTPException(400, 'Unknown learning area')
    if selected != 'mixed' and selected not in enabled:
        raise HTTPException(400, 'This learning area is disabled by the parent')
    topics = enabled if selected == 'mixed' else [selected]
    rng = random.Random(f'{sid}:{date.today().isoformat()}:{selected}:{random.SystemRandom().randint(1, 10**9)}')
    ws = legacy.Worksheet(student_id=sid, worksheet_date=date.today(), total=settings.question_count, selected_topic=selected)
    session.add(ws)
    session.flush()
    weights = legacy.weights(session, sid, topics)
    for pos in range(settings.question_count):
        topic = rng.choices(topics, weights=weights, k=1)[0]
        skill_row = session.scalar(select(legacy.Skill).where(legacy.Skill.student_id == sid, legacy.Skill.topic == topic))
        level = (skill_row.level if skill_row else 1) if settings.adaptive_mode else levels.get(topic, 1)
        if rng.random() < .2:
            level = max(1, level - 1)
        skill, prompt, answer_type, payload, answer, working = legacy.make_question(topic, min(4, level), rng)
        item = legacy.Question(worksheet_id=ws.id, topic=topic, skill=skill, level=level, prompt=prompt, answer_type=answer_type, payload=json.dumps(payload), correct_answer=answer, working=working, position=pos)
        session.add(item)
        session.flush()
        if pos == 0:
            item.state = 'active'
            item.first_viewed_at = datetime.utcnow()
            ws.current_question_id = item.id
    ws.last_active_at = datetime.utcnow()
    session.commit()
    session.refresh(ws)
    return ws


@app.get('/api/dashboard/parent-v0120')
def parent_dashboard_v0120(_: legacy.User = Depends(legacy.parent), session: Session = Depends(legacy.db)):
    learner = resolve_learner(session)
    data = legacy.dashboard(session, learner.id)
    today = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == learner.id, legacy.Worksheet.worksheet_date == date.today()).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())).all())
    data['resolved_learner'] = {'id': learner.id, 'username': learner.username, 'display_name': learner.display_name}
    data['today_worksheets'] = [worksheet_summary(w) for w in today]
    data['today_summary'] = {
        'worksheets': len(today),
        'completed': sum(1 for w in today if w.completed_at),
        'questions': sum(worksheet_summary(w)['answered'] for w in today),
        'correct': sum(legacy.worksheet_view(w)['counts']['correct'] for w in today),
        'hints': sum(legacy.worksheet_view(w)['counts']['hints'] for w in today),
        'xp': sum(w.xp_earned or 0 for w in today),
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
    rows = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())).all())
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


@app.post('/api/worksheets/new')
def new_worksheet(payload: NewWorksheetIn, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    active = session.scalar(select(legacy.Worksheet).where(legacy.Worksheet.student_id == user.id, legacy.Worksheet.completed_at.is_(None)).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc()))
    if active:
        return legacy.worksheet_view(active)
    return legacy.worksheet_view(create_worksheet(session, user.id, payload.topic))


@app.get('/api/worksheets/active/latest')
def latest_active(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    ws = session.scalar(select(legacy.Worksheet).where(legacy.Worksheet.student_id == user.id, legacy.Worksheet.completed_at.is_(None)).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc()))
    return legacy.worksheet_view(ws) if ws else None


@app.get('/api/v0120/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': '0.12.1', 'multiple_worksheets_per_day': True, 'completed_worksheet_review': True, 'worksheet_history': True, 'parent_history': True, 'consolidated_learner_resolution': True}


def _move_spa_fallback_to_end() -> None:
    """Ensure versioned JSON APIs are matched before the production SPA fallback."""
    routes = app.router.routes
    for index, route in enumerate(list(routes)):
        if getattr(route, 'path', None) == '/{path:path}':
            routes.append(routes.pop(index))
            break


_move_spa_fallback_to_end()
