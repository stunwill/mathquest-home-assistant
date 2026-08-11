from __future__ import annotations

import random
import re

from fastapi import Depends, HTTPException
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


def _simple_angle(rng: random.Random):
    degrees, answer = rng.choice([(35, 'acute'), (90, 'right'), (125, 'obtuse'), (180, 'straight')])
    choices = ['acute', 'right', 'obtuse', 'straight']
    return legacy.q(
        'VC2M4M04',
        'visual_angle',
        'What type of angle is shown?',
        'choice',
        {'visual': {'type': 'angle', 'degrees': degrees}, 'choices': choices},
        answer,
        f'{degrees}° is a {answer} angle.',
    )


def make_question_v0150(topic: str, level: int, rng: random.Random):
    skill, prompt, answer_type, payload, answer, working = _prior_make_question(topic, level, rng)
    payload = dict(payload or {})
    skill_name = skill.split(':', 1)[-1]

    # Keep early Measurement practice accessible for now. Area/perimeter and reflex/revolution
    # angle classification can return at higher adaptive levels in a later release.
    if topic == 'measurement' and level <= 1 and skill_name in {'area', 'perimeter'}:
        return _simple_clock(rng)

    # Angle-name questions should be identified from a diagram, not from the degree value in text.
    if topic == 'measurement' and ('angle' in skill_name or skill.startswith('VC2M4M04')):
        match = re.search(r'(\d{1,3})\s*°', prompt or '')
        if match:
            degrees = int(match.group(1))
            if level <= 1 and degrees > 180:
                return _simple_angle(rng)
            payload['visual'] = {'type': 'angle', 'degrees': degrees}
            prompt = 'What type of angle is shown?'
            answer_type = 'choice'
            payload['choices'] = ['acute', 'right', 'obtuse', 'straight'] if degrees <= 180 else ['acute', 'right', 'obtuse', 'straight', 'reflex', 'revolution']

    payload = _dedupe_choices(payload, str(answer))
    return skill, prompt, answer_type, payload, str(answer), working


legacy.make_question = make_question_v0150


def create_unique_worksheet(session: Session, sid: int, selected: str) -> legacy.Worksheet:
    return legacy.create_worksheet(session, sid, selected)


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
