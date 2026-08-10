from __future__ import annotations

import json
import random
import re
from datetime import date, datetime

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0140, v0120

app = v0140.app
app.version = '0.15.0'

_prior_make_question = legacy.make_question


def _dedupe_choices(payload: dict, correct_answer: str) -> dict:
    choices = payload.get('choices')
    if not isinstance(choices, list):
        return payload
    seen: set[str] = set()
    cleaned: list[str] = []
    for value in choices:
        text = str(value)
        key = text.strip().casefold()
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    correct = str(correct_answer)
    cleaned = [x for x in cleaned if x.strip().casefold() != correct.strip().casefold()]
    cleaned.append(correct)
    payload = dict(payload)
    payload['choices'] = cleaned
    return payload


def _simple_clock(rng: random.Random):
    hour = rng.randint(1, 12)
    minute = rng.choice([0, 15, 30, 45])
    display = f'{hour}:{minute:02d}'
    distractors = [
        f'{(hour % 12) + 1}:{minute:02d}',
        f'{hour}:{(minute + 15) % 60:02d}',
        f'{hour}:{(minute + 30) % 60:02d}',
    ]
    choices: list[str] = []
    for value in [display] + distractors:
        if value not in choices:
            choices.append(value)
        if len(choices) == 3:
            break
    rng.shuffle(choices)
    return legacy.q(
        'VC2M4M03',
        'visual_clock',
        'What time is shown on the analogue clock?',
        'choice',
        {'visual': {'type': 'clock', 'hour': hour, 'minute': minute}, 'choices': choices},
        display,
        f'The short hand shows {hour}; the long hand shows {minute} minutes.',
    )


def make_question_v0150(topic: str, level: int, rng: random.Random):
    skill, prompt, answer_type, payload, answer, working = _prior_make_question(topic, level, rng)
    payload = dict(payload or {})

    # Keep early Measurement practice accessible. Area/perimeter can return at higher levels,
    # but Level 1 should focus on practical units, time and visually identifying angles.
    skill_name = skill.split(':', 1)[-1]
    if topic == 'measurement' and level <= 1 and skill_name in {'area', 'perimeter'}:
        return _simple_clock(rng)

    # Angle-name questions were previously text-only (for example "What type of angle is 90°?").
    # Turn them into genuinely visual questions so the learner identifies the shown angle.
    if topic == 'measurement' and ('angle' in skill_name or skill.startswith('VC2M4M04')):
        degrees = None
        match = re.search(r'(\d{1,3})\s*°', prompt or '')
        if match:
            degrees = int(match.group(1))
        if degrees is not None:
            payload['visual'] = {'type': 'angle', 'degrees': degrees}
            prompt = 'What type of angle is shown?'
            answer_type = 'choice'
            payload['choices'] = ['acute', 'right', 'obtuse', 'straight', 'reflex', 'revolution']

    payload = _dedupe_choices(payload, str(answer))
    return skill, prompt, answer_type, payload, str(answer), working


legacy.make_question = make_question_v0150


def _question_key(prompt: str, payload: dict) -> tuple[str, tuple[str, ...]]:
    choices = payload.get('choices') if isinstance(payload, dict) else None
    choice_key = tuple(sorted(str(x).strip().casefold() for x in choices)) if isinstance(choices, list) else ()
    return (' '.join((prompt or '').split()).casefold(), choice_key)


def create_unique_worksheet(session: Session, sid: int, selected: str) -> legacy.Worksheet:
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
    seen: set[tuple[str, tuple[str, ...]]] = set()

    for pos in range(settings.question_count):
        candidate = None
        for _ in range(20):
            topic = rng.choices(topics, weights=weights, k=1)[0]
            skill_row = session.scalar(select(legacy.Skill).where(legacy.Skill.student_id == sid, legacy.Skill.topic == topic))
            level = (skill_row.level if skill_row else 1) if settings.adaptive_mode else levels.get(topic, 1)
            if rng.random() < .2:
                level = max(1, level - 1)
            skill, prompt, answer_type, payload, answer, working = legacy.make_question(topic, min(4, level), rng)
            key = _question_key(prompt, payload)
            candidate = (topic, level, skill, prompt, answer_type, payload, answer, working, key)
            if key not in seen:
                break
        if candidate is None:
            raise HTTPException(500, 'Unable to generate worksheet question')
        topic, level, skill, prompt, answer_type, payload, answer, working, key = candidate
        seen.add(key)
        item = legacy.Question(
            worksheet_id=ws.id,
            topic=topic,
            skill=skill,
            level=level,
            prompt=prompt,
            answer_type=answer_type,
            payload=json.dumps(payload),
            correct_answer=answer,
            working=working,
            position=pos,
        )
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


# Replace the v0.12 route. "New worksheet" must mean NEW, even if another worksheet
# from today is still incomplete. Older/current incomplete work remains available in history.
app.router.routes[:] = [
    route for route in app.router.routes
    if not (
        getattr(route, 'path', None) == '/api/worksheets/new'
        and 'POST' in (getattr(route, 'methods', None) or set())
    )
]


@app.post('/api/worksheets/new')
def new_worksheet_v0150(
    payload: v0120.NewWorksheetIn,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    return legacy.worksheet_view(create_unique_worksheet(session, user.id, payload.topic))


@app.get('/api/v0150/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.15.0',
        'required_question_visuals': True,
        'visual_clocks': True,
        'visual_angle_identification': True,
        'new_worksheet_while_incomplete': True,
        'duplicate_question_protection': True,
        'duplicate_choice_protection': True,
        'level_1_measurement_guardrails': True,
    }


v0120._move_spa_fallback_to_end()
