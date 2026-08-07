from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v090

app = legacy.app
app.version = '0.10.0'


class ScratchpadIn(BaseModel):
    content: str


# Scratchpad is deliberately session-local in v0.10. It is a thinking tool, not an assessment signal.
_scratchpads: dict[tuple[int, int], str] = {}


@app.get('/api/questions/{qid}/read-aloud')
def read_aloud(qid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    q = session.get(legacy.Question, qid)
    if not q:
        raise HTTPException(404, 'Question not found')
    ws = session.get(legacy.Worksheet, q.worksheet_id)
    if not ws or ws.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    payload = legacy.json.loads(q.payload)
    text = q.prompt.replace('×', ' multiplied by ').replace('÷', ' divided by ').replace('²', ' squared')
    return {'text': text, 'lang': 'en-AU', 'visual_description': _describe_visual(payload.get('visual'))}


def _describe_visual(v: dict[str, Any] | None) -> str | None:
    if not v:
        return None
    kind = v.get('type')
    if kind == 'fraction_compare':
        return 'Two fraction bars are shown for comparison.'
    if kind == 'number_line':
        return f"A number line from {v.get('min', 0)} to {v.get('max', 1)} divided into {v.get('steps', 1)} equal steps."
    if kind == 'clock':
        return 'An analogue clock face with an hour hand and a minute hand.'
    if kind == 'angle':
        return 'An angle diagram is shown.'
    if kind == 'bar_chart':
        return 'A bar chart is shown. Compare the heights and labels of the bars.'
    if kind == 'grid':
        return 'A labelled coordinate grid is shown. Read the column before the row.'
    return 'An interactive maths visual is shown.'


@app.get('/api/questions/{qid}/scratchpad')
def get_scratchpad(qid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    q = session.get(legacy.Question, qid)
    if not q:
        raise HTTPException(404, 'Question not found')
    ws = session.get(legacy.Worksheet, q.worksheet_id)
    if not ws or ws.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    return {'content': _scratchpads.get((user.id, qid), '')}


@app.put('/api/questions/{qid}/scratchpad')
def save_scratchpad(qid: int, payload: ScratchpadIn, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    q = session.get(legacy.Question, qid)
    if not q:
        raise HTTPException(404, 'Question not found')
    ws = session.get(legacy.Worksheet, q.worksheet_id)
    if not ws or ws.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    _scratchpads[(user.id, qid)] = payload.content[:4000]
    return {'ok': True}


@app.get('/api/questions/{qid}/manipulative')
def manipulative(qid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    q = session.get(legacy.Question, qid)
    if not q:
        raise HTTPException(404, 'Question not found')
    ws = session.get(legacy.Worksheet, q.worksheet_id)
    if not ws or ws.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    skill = q.skill.split(':', 1)[-1]
    if 'fraction' in skill:
        return {'type': 'fraction_tiles', 'pieces': [2, 3, 4, 5, 6, 8, 10, 12], 'instruction': 'Drag fraction pieces into the tray to build and compare amounts.'}
    if 'place' in skill or 'powers_of_ten' in skill or 'number' in q.topic:
        return {'type': 'place_value', 'columns': ['thousands', 'hundreds', 'tens', 'ones'], 'instruction': 'Drag base-ten blocks between columns to model the number.'}
    if q.topic == 'measurement':
        return {'type': 'ruler', 'units': 'cm', 'length': 20, 'instruction': 'Drag the marker along the ruler to model a length.'}
    if q.topic == 'space':
        return {'type': 'grid_tokens', 'columns': ['A', 'B', 'C', 'D', 'E'], 'rows': 6, 'instruction': 'Drag a token onto the grid to test a grid reference.'}
    return {'type': 'counter_tray', 'count': 20, 'instruction': 'Drag counters into groups to model the problem.'}


def weekly_report(session: Session, sid: int) -> dict[str, Any]:
    end = date.today()
    start = end - timedelta(days=6)
    works = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Worksheet.worksheet_date >= start, legacy.Worksheet.worksheet_date <= end).order_by(legacy.Worksheet.worksheet_date)).all())
    questions = [q for w in works for q in w.questions]
    attempts = [a for q in questions for a in q.attempts]
    completed = [w for w in works if w.completed_at]
    first_attempts = [a for a in attempts if a.attempt_number == 1]
    accuracy = round(sum(1 for a in first_attempts if a.correct) / max(1, len(first_attempts)) * 100)
    mastery = v090.skill_mastery(session, sid)
    strongest = sorted(mastery, key=lambda x: x['mastery'], reverse=True)[:3]
    support = [x for x in mastery if x['status'] in ('needs_support', 'developing')][:3]
    confidence_rows = []
    for q in questions:
        c = v090._confidence(session, q.id, sid)
        if c:
            confidence_rows.append(c)
    return {
        'period': {'start': start.isoformat(), 'end': end.isoformat()},
        'days_completed': len(completed),
        'questions_attempted': len(questions),
        'first_attempt_accuracy': accuracy,
        'hints_used': sum(q.hint_count or 0 for q in questions),
        'xp_earned': sum(w.xp_earned or 0 for w in completed),
        'strongest_skills': strongest,
        'skills_to_support': support,
        'confidence': {
            'responses': len(confidence_rows),
            'knew_it': confidence_rows.count('knew_it'),
            'pretty_sure': confidence_rows.count('pretty_sure'),
            'guessed': confidence_rows.count('guessed'),
        },
        'parent_summary': _parent_summary(len(completed), accuracy, strongest, support),
    }


def _parent_summary(days: int, accuracy: int, strongest: list[dict[str, Any]], support: list[dict[str, Any]]) -> str:
    strength = strongest[0]['title'] if strongest else 'recent practice'
    need = support[0]['title'] if support else None
    text = f'This week included {days} completed learning days with {accuracy}% first-attempt accuracy. The strongest current evidence is in {strength}.'
    if need:
        text += f' The next useful focus is {need}, where more guided practice would help consolidate understanding.'
    return text


@app.get('/api/reports/weekly')
def weekly(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = user.id if user.role == 'student' else session.scalar(select(legacy.User.id).where(legacy.User.role == 'student'))
    return weekly_report(session, sid)


@app.get('/api/v0100/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.10.0',
        'read_aloud': True,
        'scratchpad': True,
        'interactive_manipulatives': ['fraction_tiles', 'place_value', 'ruler', 'grid_tokens', 'counter_tray'],
        'weekly_parent_report': True,
        'multi_step_learning': True,
        'inherits_v090': True,
    }
