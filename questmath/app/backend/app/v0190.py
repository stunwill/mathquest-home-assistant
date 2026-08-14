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
    if requested == 2:
        a, b = rng.randint(2, 20), rng.randint(1, 10)
        return legacy.q('VC2M2N04', 'diagnostic_add_subtract', f'Calculate {a} + {b}.', 'number', {'curriculum_level': 2}, a + b, 'Count on or partition the numbers, then check the total.')
    if requested == 3:
        a, b = rng.randint(2, 10), rng.randint(2, 5)
        return legacy.q('VC2M3N04', 'diagnostic_multiplication', f'Calculate {a} × {b}.', 'number', {'curriculum_level': 3}, a * b, 'Use equal groups or a known multiplication fact.')
    if requested == 4:
        return legacy.make_question(rng.choice(['number', 'algebra']), 4, rng)
    if requested == 5:
        a, b = rng.randint(12, 99), rng.randint(2, 9)
        return legacy.q('VC2M5N06', 'diagnostic_operations', f'Calculate {a} × {b}.', 'number', {'curriculum_level': 5}, a * b, 'Partition the two-digit number and combine the partial products.')
    numerator, denominator = rng.randint(2, 8), rng.choice([10, 100])
    answer = numerator / denominator
    return legacy.q('VC2M6N03', 'diagnostic_fraction_decimal', f'Write {numerator}/{denominator} as a decimal.', 'number', {'curriculum_level': 6}, answer, 'Use place value to convert tenths or hundredths to a decimal.')


@app.post('/api/sessions/new')
def new_session(payload: SessionCreateIn, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    count = {5: 6, 10: 12, 15: 18}[payload.minutes]
    if payload.kind == 'diagnostic':
        count = 15
        worksheet = legacy.create_worksheet(session, user.id, 'number_algebra', question_count=count,
                                            session_kind='diagnostic', target_minutes=15)
        # Regenerate the authoritative worksheet's items into three checks at each level.
        for index, question in enumerate(sorted(worksheet.questions, key=lambda item: item.position)):
            level = 2 + min(4, index // 3)
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
    for level in range(2, 7):
        questions = [question for question in worksheet.questions if question.level == level]
        answered = [question for question in questions if question.attempts]
        correct = sum(any(attempt.correct for attempt in question.attempts) for question in answered)
        levels.append({'level': level, 'answered': len(answered), 'correct': correct,
                       'accuracy': round(correct / len(answered) * 100) if answered else None})
    completed = bool(worksheet.completed_at)
    secure = [item['level'] for item in levels if item['answered'] == 3 and item['accuracy'] is not None and item['accuracy'] >= 67]
    return {'status': 'complete' if completed else 'in_progress', 'worksheet_id': worksheet.id,
            'estimated_level': max(secure) if completed and secure else None, 'target_level': 5, 'levels': levels}


@app.get('/api/diagnostic/latest')
def latest_diagnostic(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    sid = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return diagnostic_summary(session, sid)


@app.get('/api/v0190/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': legacy.APP_VERSION, 'diagnostic_levels': [2, 3, 4, 5, 6],
            'target_level': 5, 'timed_sessions': [5, 10, 15]}


v0120._move_spa_fallback_to_end()
