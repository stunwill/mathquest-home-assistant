from __future__ import annotations

import json
import random
import re
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0200, v0280, v0290, v0300, v0301

app = v0301.app
app.version = '0.31.0'
legacy.APP_VERSION = '0.31.0'

_prior_create_worksheet = legacy.create_worksheet


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _numbers(prompt: str) -> list[int]:
    return [int(value) for value in re.findall(r'(?<![\d.])\d+(?![\d.])', prompt or '')]


def _skill_name(question: legacy.Question) -> str:
    return (question.skill or '').split(':', 1)[-1].lower()


def _operation(question: legacy.Question) -> str | None:
    prompt = question.prompt or ''
    skill = _skill_name(question)
    if ' + ' in prompt or 'addition' in skill or (skill == 'efficient_add_subtract' and '+' in prompt):
        return 'addition'
    if '−' in prompt or ' - ' in prompt or 'subtraction' in skill or (skill == 'efficient_add_subtract' and ('−' in prompt or ' - ' in prompt)):
        return 'subtraction'
    if '×' in prompt or 'multiplication' in skill or 'multiply' in skill:
        return 'multiplication'
    if '÷' in prompt or 'division' in skill or 'divide' in skill:
        return 'division'
    return None


def _question_context(question: legacy.Question) -> dict[str, Any]:
    numbers = _numbers(question.prompt)
    operation = _operation(question)
    context: dict[str, Any] = {
        'topic': question.topic,
        'skill': _skill_name(question),
        'operation': operation,
        'operands': numbers[:2],
        'difficulty_level': question.level,
        'question_family': v0200.question_family(question),
        'answer_type': question.answer_type,
    }
    payload = _payload(question)
    if payload.get('strategy_card'):
        context['expected_strategy'] = payload['strategy_card'].get('strategy')
    return context


def _partition_parts(value: int) -> list[int]:
    return [part for part in (value // 100 * 100, (value % 100) // 10 * 10, value % 10) if part]


def _arithmetic_tutoring(question: legacy.Question) -> dict[str, Any] | None:
    operation = _operation(question)
    values = _numbers(question.prompt)
    if operation not in ('addition', 'subtraction') or len(values) < 2:
        return None
    a, b = values[0], values[1]
    a_o, b_o = a % 10, b % 10
    a_partition = ' + '.join(str(x) for x in _partition_parts(a)) or str(a)
    b_partition = ' + '.join(str(x) for x in _partition_parts(b)) or str(b)

    if operation == 'addition':
        regroup = a_o + b_o >= 10
        bridge = a_o + b_o == 10
        strategy = 'bridge to the next ten' if bridge else 'regroup the ones' if regroup else 'partition by place value'
        hint1 = f'Look at the ones digits first: {a_o} and {b_o}. Is there an easy combination you recognise?'
        hint2 = f'Split the numbers into place values.\n{a} = {a_partition}\n{b} = {b_partition}\nStart by combining the ones.'
        hint3 = (
            f'{a_o} + {b_o} makes at least one whole ten. Regroup that ten, then combine the remaining tens and hundreds.'
            if regroup else
            f'Combine {a_o} + {b_o} first, then combine the tens and hundreds. Keep each place value lined up.'
        )
        return {
            'strategy': strategy,
            'hints': [hint1, hint2, hint3],
            'teach_steps': [
                {'label': 'Notice', 'text': f'This is addition. A useful strategy here is to {strategy}.'},
                {'label': 'Partition', 'math': [f'{a} = {a_partition}', f'{b} = {b_partition}']},
                {'label': 'Your turn', 'text': f'What do {a_o} and {b_o} make together?'},
            ],
        }

    regroup = a_o < b_o
    strategy = 'decompose one ten' if regroup else 'subtract by place value'
    hint1 = f'Compare the ones digits first: {a_o} and {b_o}. Can the ones be subtracted directly?'
    hint2 = (
        f'Split the numbers into place values.\n{a} = {a_partition}\n{b} = {b_partition}\n'
        + ('You will need to regroup one ten before subtracting the ones.' if regroup else 'Subtract the ones first, then the tens and hundreds.')
    )
    hint3 = (
        f'Rename one ten as 10 ones, combine it with the {a_o} ones, then subtract {b_o}. After that, finish the tens and hundreds.'
        if regroup else
        f'Subtract {b_o} from {a_o}, then work left through the tens and hundreds.'
    )
    return {
        'strategy': strategy,
        'hints': [hint1, hint2, hint3],
        'teach_steps': [
            {'label': 'Notice', 'text': f'This is subtraction. A useful strategy here is to {strategy}.'},
            {'label': 'Partition', 'math': [f'{a} = {a_partition}', f'{b} = {b_partition}']},
            {'label': 'Your turn', 'text': f'Can {a_o} ones subtract {b_o} ones directly, or do you need to regroup a ten?'},
        ],
    }


def tutoring_content(question: legacy.Question) -> dict[str, Any]:
    arithmetic = _arithmetic_tutoring(question)
    if arithmetic:
        return arithmetic
    plan = v0200.guided_plan(question)
    return {
        'strategy': plan['title'],
        'hints': [plan['stages'][0], plan['stages'][1], v0200.hint_text_v0200(question, 3)],
        'teach_steps': [
            {'label': 'Notice', 'text': plan['stages'][0]},
            {'label': 'Strategy', 'text': plan['stages'][1]},
            {'label': 'Your turn', 'text': 'Use that strategy for the first step of this question, then try the answer yourself.'},
        ],
    }


def _learner_ready_for_hundreds(session: Session, student_id: int) -> bool:
    rows = session.scalars(select(legacy.Attempt).where(legacy.Attempt.student_id == student_id).order_by(legacy.Attempt.id.desc()).limit(24)).all()
    if len(rows) < 6:
        return False
    recent = list(rows[:12])
    return bool(recent) and sum(1 for row in recent if row.correct) / len(recent) >= 0.7


def _upgrade_simple_arithmetic(question: legacy.Question, rng: random.Random) -> bool:
    operation = _operation(question)
    values = _numbers(question.prompt)
    if operation not in ('addition', 'subtraction') or len(values) < 2:
        return False
    a, b = values[0], values[1]
    if a >= 100 or b >= 100:
        return False
    if operation == 'addition':
        a2 = rng.randint(1, 5) * 100 + max(12, a)
        b2 = max(11, b + rng.randint(0, 18))
        question.prompt = f'Calculate {a2} + {b2}.'
        question.correct_answer = str(a2 + b2)
        question.working = f'Partition by place value or use written addition: {a2} + {b2} = {a2 + b2}.'
    else:
        a2 = rng.randint(1, 5) * 100 + max(25, a)
        b2 = max(11, min(a2 - 1, b + rng.randint(4, 18)))
        if a2 % 10 >= b2 % 10:
            a2 += 10
        question.prompt = f'Calculate {a2} − {b2}.'
        question.correct_answer = str(a2 - b2)
        question.working = f'Use place value and regrouping where needed: {a2} − {b2} = {a2 - b2}.'
    payload = _payload(question)
    payload['instructional_band'] = 'hundreds'
    question.payload = json.dumps(payload)
    return True


def create_worksheet_v0310(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    ready = _learner_ready_for_hundreds(session, student_id)
    rng = random.Random(f'v0310:{worksheet.id}:difficulty')
    candidates = [q for q in sorted(worksheet.questions, key=lambda item: item.position) if q.topic in ('number', 'algebra')]
    upgraded = 0
    max_upgrades = max(1, len(candidates) * 2 // 3) if ready else max(0, len(candidates) // 4)
    for question in candidates:
        if upgraded >= max_upgrades:
            break
        if rng.random() < (0.78 if ready else 0.28) and _upgrade_simple_arithmetic(question, rng):
            upgraded += 1
    for question in worksheet.questions:
        payload = _payload(question)
        payload['mentor_context'] = _question_context(question)
        payload['visual_mathematics'] = v0300._safe_visual_payload(question, worksheet)
        payload['solution_strategies'] = [] if worksheet.session_kind == 'parent_test' else v0300._strategy_set(question)
        question.payload = json.dumps(payload)
    v0301.repair_fraction_number_lines(worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def _question_for_mentor(qid: int, user: legacy.User, session: Session) -> legacy.Question:
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(user, worksheet):
        raise HTTPException(403, 'Question does not belong to this worksheet account')
    return question


def mentor_payload_v0310(question: legacy.Question, action: str) -> dict[str, Any]:
    base = v0280._mentor_payload(question, action if action in ('guide', 'hint', 'why', 'teach') else 'worked_example')
    content = tutoring_content(question)
    stage = min(3, max(1, question.hint_count or question.mentor_stage or 1))
    base['question_context'] = _question_context(question)
    base['strategy_name'] = content['strategy']
    base['hint_kind'] = ('nudge', 'strategy', 'worked_next_step')[stage - 1]
    if action == 'hint':
        base['body'] = content['hints'][stage - 1]
    elif action == 'teach':
        base['body'] = ''
        base['teach_steps'] = content['teach_steps']
        base['guiding_question'] = content['teach_steps'][-1].get('text')
    elif action == 'worked_example':
        base['worked_example'] = v0290.aligned_worked_example(question)
        base['example_is_aligned'] = True
    return base


@app.get('/api/questions/{qid}/math-mentor-v0310')
def math_mentor_v0310(
    qid: int,
    action: str = 'guide',
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    question = _question_for_mentor(qid, user, session)
    if action == 'guide':
        question.mentor_started = True
    if action == 'worked_example':
        question.mentor_example_seen = True
    session.commit()
    return mentor_payload_v0310(question, action)


legacy.create_worksheet = create_worksheet_v0310


@app.get('/api/v0310/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.31.0',
        'tablet_first_worksheet': True,
        'adaptive_hundreds_arithmetic': True,
        'question_specific_teach_me': True,
        'progressive_distinct_hints': True,
        'structured_mentor_context': True,
        'inherits_v0301': True,
    }


v0120._move_spa_fallback_to_end()
