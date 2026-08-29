from __future__ import annotations

import json
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0330, v090

app = v0330.app
app.version = '0.34.0'
legacy.APP_VERSION = '0.34.0'


STAGES = [
    'Start',
    'Challenge',
    'Discovery',
    'Harder Challenge',
    'Final Challenge',
    'Completion',
]


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _story_stage(index: int, total: int) -> tuple[int, str]:
    if total <= 1:
        return 5, STAGES[4]
    ratio = index / max(1, total - 1)
    if ratio <= 0.18:
        return 1, STAGES[0]
    if ratio <= 0.40:
        return 2, STAGES[1]
    if ratio <= 0.62:
        return 3, STAGES[2]
    if ratio <= 0.82:
        return 4, STAGES[3]
    return 5, STAGES[4]


def _context_for(theme: str, question: legacy.Question, stage_name: str) -> dict[str, str]:
    story = v090.ADVENTURES[theme]
    skill = (question.skill or '').split(':', 1)[-1].replace('_', ' ')
    topic = (question.topic or 'maths').replace('_', ' ')
    templates = {
        'bakery': f'At {stage_name.lower()}, the bakery team needs your {topic} thinking to keep the morning plan on track.',
        'camping': f'At {stage_name.lower()}, the group needs your {topic} thinking before moving to the next checkpoint.',
        'space': f'At {stage_name.lower()}, mission control needs your {topic} thinking before the crew can continue.',
        'animal_rescue': f'At {stage_name.lower()}, the rescue team needs your {topic} thinking before the next task can begin.',
    }
    return {
        'lead_in': templates.get(theme, f'Use your {topic} thinking to continue the mission.'),
        'challenge_label': skill.title(),
        'success_text': f'Good mathematical thinking moves the {story["title"].lower()} forward.',
    }


def _adventure_learning_goals(worksheet: legacy.Worksheet) -> list[str]:
    goals: list[str] = []
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        if question.topic not in goals:
            goals.append(question.topic)
    return goals


def _ensure_adaptive_annotation(session: Session, student_id: int, question: legacy.Question) -> dict[str, Any]:
    payload = _payload(question)
    if payload.get('learning_purpose'):
        return payload
    outcomes = v0230.outcome_mastery(session, student_id)
    purpose, reason = v0330._purpose_for_question(session, student_id, question, {item['code']: item for item in outcomes})
    evidence = v0330._question_evidence(session, student_id, question.skill)
    state = v0330._progression_state(evidence)
    payload['learning_purpose'] = purpose
    payload['learning_purpose_label'] = v0330.PURPOSE_LABELS[purpose]
    payload['adaptive_reason'] = reason
    payload['progression_state'] = state
    payload['adaptive_evidence'] = {
        'questions': evidence['questions'],
        'independent_accuracy': round(evidence['independent'] * 100),
        'eventual_accuracy': round(evidence['eventual'] * 100),
        'support_dependency': round(evidence['support'] * 100),
    }
    return payload


def apply_adventure_presentation(session: Session, worksheet: legacy.Worksheet, student_id: int, theme: str) -> dict[str, Any]:
    if worksheet.session_kind == 'parent_test':
        raise HTTPException(400, 'Parent Tests cannot become Story Adventures')
    if theme not in v090.ADVENTURES:
        raise HTTPException(400, 'Unknown adventure')

    story = v090.ADVENTURES[theme]
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if not questions:
        raise HTTPException(400, 'Adventure requires learning questions')

    mission_id = f'{theme}-{worksheet.id}'
    learning_goals = _adventure_learning_goals(worksheet)

    for index, question in enumerate(questions):
        payload = _ensure_adaptive_annotation(session, student_id, question)
        stage_number, stage_name = _story_stage(index, len(questions))
        purpose = payload.get('learning_purpose', 'current')
        adaptive = payload.get('adaptive') if isinstance(payload.get('adaptive'), dict) else {}
        context = _context_for(theme, question, stage_name)
        payload['adventure'] = {
            'version': 3,
            'mission_id': mission_id,
            'theme': theme,
            'title': story['title'],
            'mission': story['mission'],
            'objective': story['objective'],
            'outcome': story['outcome'],
            'stage': stage_name,
            'stage_number': stage_number,
            'stages': STAGES,
            'question': index + 1,
            'total': len(questions),
            'learning_goal': question.topic,
            'learning_goals': learning_goals,
            'learning_purpose': purpose,
            'learning_purpose_label': payload.get('learning_purpose_label', v0330.PURPOSE_LABELS.get(purpose, 'Practising this skill')),
            'adaptive_reason': payload.get('adaptive_reason'),
            'difficulty_band': payload.get('difficulty_band'),
            'prerequisite_for': adaptive.get('prerequisite_for'),
            'adaptive_mode': adaptive.get('mode'),
            'context': context,
        }
        question.payload = json.dumps(payload)

    worksheet.selected_topic = story['title']
    worksheet.session_kind = 'adventure'
    session.commit()
    session.refresh(worksheet)
    return {
        'theme': theme,
        'title': story['title'],
        'mission': story['mission'],
        'objective': story['objective'],
        'learning_goals': learning_goals,
        'stages': STAGES,
        'questions_linked': len(questions),
    }


def _remove_legacy_adventure_route() -> None:
    app.router.routes[:] = [
        route for route in app.router.routes
        if not (
            getattr(route, 'path', None) == '/api/worksheets/{wid}/adventure'
            and 'POST' in getattr(route, 'methods', set())
        )
    ]


_remove_legacy_adventure_route()


@app.post('/api/worksheets/{wid}/adventure')
@app.post('/api/worksheets/{wid}/adventure-v0340')
def apply_adventure_v0340(
    wid: int,
    payload: v090.AdventureIn,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    worksheet = session.get(legacy.Worksheet, wid)
    if not worksheet or worksheet.student_id != user.id:
        raise HTTPException(404, 'Worksheet not found')
    return apply_adventure_presentation(session, worksheet, user.id, payload.theme)


@app.get('/api/adventures-v0340')
def adventures_v0340(
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    items = []
    for key, story in v090.ADVENTURES.items():
        goals = story['topics'][:2]
        if user.role == 'student':
            goals = v090._adventure_goals(session, user.id, story)[:2]
        items.append({
            'id': key,
            **story,
            'recommended_goals': goals,
            'session_lengths': [5, 10, 15],
            'presentation_only': True,
        })
    return items


@app.get('/api/v0340/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.34.0',
        'adaptive_story_adventures': True,
        'backend_authoritative_learning_plan': True,
        'presentation_only_story_layer': True,
        'story_learning_evidence_shared': True,
        'parent_test_isolation': True,
        'session_lengths': [5, 10, 15],
        'inherits_v0330': True,
    }


v0120._move_spa_fallback_to_end()
