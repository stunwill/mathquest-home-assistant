from __future__ import annotations

from typing import Literal

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0200, v0260

app = v0260.app
app.version = legacy.APP_VERSION

MentorAction = Literal['guide', 'hint', 'why', 'teach', 'worked_example']


def _question_for_mentor(qid: int, user: legacy.User, session: Session) -> legacy.Question:
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(user, worksheet):
        raise HTTPException(403, 'Question does not belong to this worksheet account')
    return question


def _mentor_payload(question: legacy.Question, action: MentorAction, *, reset: bool = False) -> dict:
    plan = v0200.guided_plan(question)
    stage = min(3, max(1, question.mentor_stage or question.hint_count or 1))
    guide = plan['stages'][0]
    if action == 'guide':
        body = guide
    elif action == 'hint':
        body = v0200.hint_text_v0200(question, stage)
    elif action == 'why':
        body = plan['why']
    elif action == 'teach':
        body = ' '.join(plan['stages'][:2])
    else:
        body = v0200.safe_worked_example(question, plan['family'])
    memory_tips = {
        'arithmetic': 'Use a known fact or a nearby ten instead of counting one by one.',
        'equation': 'Use the inverse operation, then check the value in the original equation.',
        'fraction': 'Only compare fractions when the wholes are the same size.',
        'measurement': 'Name the attribute and unit before choosing a rule.',
        'grid': 'Read the agreed first label, then the second label, in the same order every time.',
        'time': 'Use a nearby hour as a landmark for counting time jumps.',
        'data': 'Read the title, labels and scale before counting or comparing.',
        'general': 'Say what you need to find before choosing the first step.',
    }
    return {
        'action': action,
        'family': plan['family'],
        'title': plan['title'],
        'stage': stage,
        'guiding_question': guide,
        'body': body,
        'why': plan['why'],
        'common_mistake': (v0200._latest_misconception(question) or {}).get('message'),
        'memory_tip': memory_tips[plan['family']],
        'worked_example': v0200.safe_worked_example(question, plan['family']),
        'example_is_distinct': True,
        'reset': reset,
        'final_answer_revealed': False,
    }


@app.get('/api/questions/{qid}/math-mentor')
def math_mentor(
    qid: int,
    action: MentorAction = 'guide',
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    question = _question_for_mentor(qid, user, session)
    if action == 'guide':
        question.mentor_started = True
        session.commit()
    if action == 'worked_example':
        question.mentor_example_seen = True
        session.commit()
    return _mentor_payload(question, action)


@app.post('/api/questions/{qid}/math-mentor/start-over')
def restart_math_mentor(
    qid: int,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    question = _question_for_mentor(qid, user, session)
    if legacy.question_status(question) in ('correct', 'incorrect'):
        raise HTTPException(400, 'Completed questions cannot restart tutoring')
    question.mentor_started = True
    session.commit()
    return _mentor_payload(question, 'guide', reset=True)


@app.get('/api/v0280/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'math_mentor': True,
        'collapsible_panel': True,
        'actions': ['hint', 'why', 'teach', 'worked_example', 'start_over', 'read_aloud'],
        'guided_recovery': ['attempt', 'guiding_question', 'retry', 'hint_1', 'hint_2', 'hint_3', 'worked_example', 'retry'],
        'parent_tests_preserve_assessment_flow': True,
        'browser_read_aloud_framework': True,
    }


v0120._move_spa_fallback_to_end()
