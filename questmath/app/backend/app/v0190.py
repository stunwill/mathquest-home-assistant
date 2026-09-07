from __future__ import annotations

import random
from typing import Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0170

app = v0170.app
app.version = legacy.APP_VERSION

class SessionCreateIn(BaseModel):
    kind: Literal['practice', 'diagnostic'] = 'practice'
    minutes: Literal[5, 10, 15] = 10
    topic: str = 'number_algebra'


def _diagnostic_question(level, rng):
    requested = level
    if requested == 5:
        a, b = rng.randint(12, 99), rng.randint(2, 9)
        return legacy.q('VC2M5N06', 'diagnostic_operations', f'Calculate {a} × {b}.', 'number', {'curriculum_level': 5, 'diagnostic_evidence': True}, a * b, 'Partition the two-digit number and combine the partial products.')
    if requested == 6:
        numerator, denominator = rng.randint(2, 8), rng.choice([10, 100])
        answer = numerator / denominator
        return legacy.q('VC2M6N03', 'diagnostic_fraction_decimal', f'Write {numerator}/{denominator} as a decimal.', 'number', {'curriculum_level': 6, 'diagnostic_evidence': True}, answer, 'Use place value to convert tenths or hundredths to a decimal.')
    raise ValueError(f'Unsupported diagnostic level: {requested}')


@app.post('/api/sessions/new')
def new_session(payload: SessionCreateIn, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    count = {5: 6, 10: 12, 15: 18}[payload.minutes]
    if payload.kind == 'diagnostic':
        count = 6
        worksheet = legacy.create_worksheet(session, user.id, 'number_algebra', question_count=count,
                                            session_kind='diagnostic', target_minutes=15)
        for index, question in enumerate(sorted(worksheet.questions, key=lambda item: item.position)):
            level = 5 if index < 3 else 6
            question.level = level
            skill, prompt, answer_type, data, answer, working = _diagnostic_question(level, random.Random(f'{worksheet.id}:{index}'))
            question.skill, question.prompt, question.answer_type = skill, prompt, answer_type
            question.payload, question.correct_answer, question.working = legacy.json.dumps(data), str(answer), working
        session.commit(); session.refresh(worksheet)
    else:
        worksheet = legacy.create_worksheet(session, user.id, payload.topic, question_count=count,
                                            session_kind='timed', target_minutes=payload.minutes)
    return legacy.worksheet_view(worksheet)


def diagnostic_summary(session: Session, sid: int):
    worksheet = session.scalar(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid, legacy.Worksheet.session_kind == 'diagnostic'
    ).order_by(legacy.Worksheet.started_at.desc()))
    if not worksheet:
        return {'status': 'not_started', 'levels': []}
    levels = []
    for level in (5, 6):
        questions = [question for question in worksheet.questions if question.level == level]
        answered = [question for question in questions if question.attempts]
        independent = 0
        eventual = 0
        support_used = 0
        for question in answered:
            attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
            first = attempts[0] if attempts else None
            help_used = bool((question.hint_count or 0) or question.mentor_started or question.mentor_example_seen)
            independent += int(bool(first and first.correct and not help_used))
            eventual += int(any(attempt.correct for attempt in attempts))
            support_used += int(help_used)
        levels.append({'level': level, 'answered': len(answered), 'independent_correct': independent,
                       'eventual_correct': eventual, 'support_used': support_used})
    completed = bool(worksheet.completed_at)
    return {'status': 'complete' if completed else 'in_progress', 'worksheet_id': worksheet.id,
            'target_level': 5, 'levels': levels,
            'interpretation': 'placement_evidence' if completed else None,
            'limitations': 'This short diagnostic does not classify the student into an overall curriculum level.' if completed else None}


@app.get('/api/diagnostic/latest')
def latest_diagnostic(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return diagnostic_summary(session, sid)


@app.get('/api/v0190/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': legacy.APP_VERSION, 'diagnostic_levels': [5, 6],
            'target_level': 5, 'timed_sessions': [5, 10, 15],
            'diagnostic_is_placement_evidence': True}


v0120._move_spa_fallback_to_end()
