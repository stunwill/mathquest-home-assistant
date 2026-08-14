from __future__ import annotations

import re
from typing import Any, Literal

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0190, v090

app = v0190.app
app.version = legacy.APP_VERSION


SupportAction = Literal['hint', 'why', 'teach', 'another']


PLANS: dict[str, dict[str, Any]] = {
    'arithmetic': {
        'title': 'Choose an efficient operation strategy',
        'stages': [
            'What operation is being used, and what known fact could make the calculation easier?',
            'Partition by place value or use a nearby known fact. Work on one part at a time, then recombine the parts.',
            'Try the same strategy with different numbers: 47 + 28 becomes 47 + 20 + 8. Complete that example, then return to your question.',
        ],
        'why': 'Breaking a calculation into known facts reduces working-memory load and makes each step easier to check.',
        'another': 'Use the inverse operation to check your result. For subtraction, add the difference back; for division, multiply the quotient.',
        'example': 'For 63 − 27, regroup one ten: 13 − 7 = 6, then 5 tens − 2 tens = 3 tens, so the example gives 36.',
    },
    'equation': {
        'title': 'Keep the equation balanced',
        'stages': [
            'What has happened to the unknown number, and which inverse operation would undo it?',
            'Work backwards from the total. Undo addition with subtraction, and undo subtraction with addition.',
            'Try a different equation: □ + 7 = 19. Undo +7 by calculating 19 − 7, then check the value in the original equation.',
        ],
        'why': 'An equals sign says both sides have the same value. An inverse operation isolates the unknown while preserving that equality.',
        'another': 'Use a fact family: write the related addition and subtraction facts, then choose the fact containing the missing value.',
        'example': 'For □ − 6 = 15, calculate 15 + 6 = 21, then check that 21 − 6 = 15.',
    },
    'fraction': {
        'title': 'Compare equal-sized wholes',
        'stages': [
            'If both fractions described the same-sized whole, which shaded amount would cover more of it?',
            'Draw equal-length bars, split each bar into its denominator number of equal parts, and shade the numerator.',
            'Try different fractions: compare 3/4 and 2/3 by renaming them as twelfths. Work out 3/4 = 9/12 and 2/3 = 8/12.',
        ],
        'why': 'Numerators and denominators only make sense relative to the same whole. Equal-width models make the actual quantities comparable.',
        'another': 'Use a common denominator or compare each fraction with a useful benchmark such as one half or one whole.',
        'example': 'For 3/4 and 2/3, twelfths give 9/12 and 8/12, so 3/4 is larger in this separate example.',
    },
    'measurement': {
        'title': 'Identify what is being measured',
        'stages': [
            'Is the question asking about distance around, space inside, length, mass, capacity or an elapsed amount?',
            'Write the matching unit and rule before substituting any values. Convert measurements to the same unit first.',
            'Try a different rectangle: for length 8 cm and width 3 cm, perimeter uses 8 + 3 + 8 + 3 while area uses 8 × 3.',
        ],
        'why': 'Choosing the attribute and unit first prevents common mix-ups such as using an area rule for perimeter.',
        'another': 'Sketch and label the measurement. Trace the outside for perimeter, or cover the inside with equal squares for area.',
        'example': 'A 6 cm by 4 cm rectangle has perimeter 20 cm and area 24 cm². Notice that the units are different.',
    },
    'grid': {
        'title': 'Read the grid in the agreed order',
        'stages': [
            'Which column contains the highlighted square, and which row contains it?',
            'Trace from the square to the column label first, then trace to the row label. Keep those two labels in that order.',
            'Try a different location: a square in column B and row 4 has reference B4. Now apply that order to your highlighted square.',
        ],
        'why': 'A consistent column-then-row convention means everyone identifies the same square without printing the answer inside it.',
        'another': 'Say the movement aloud: across to the column, then down or up to the row.',
        'example': 'If a different square is in column D and row 2, its reference is D2.',
    },
    'time': {
        'title': 'Use time landmarks',
        'stages': [
            'What does the minute hand show, and what does the shorter hour hand show?',
            'Count minutes in groups of five around a clock, or place both times on a timeline before finding the duration.',
            'Try a different duration: from 2:35 to 3:00 is 25 minutes, then from 3:00 to 3:20 is 20 minutes. Combine those jumps.',
        ],
        'why': 'Splitting a duration at an hour landmark makes the jumps easier to calculate and check.',
        'another': 'Convert both times to minutes after midnight, subtract, then convert the result back to hours and minutes.',
        'example': 'From 2:35 to 3:20 takes 25 + 20 = 45 minutes.',
    },
    'data': {
        'title': 'Read what the data representation shows',
        'stages': [
            'What do the title, labels and scale say each mark or value represents?',
            'Locate only the category or values named in the question, then count or compare using the displayed scale.',
            'Try separate data: in 2, 3, 3, 4, 3, the value 3 appears three times. That makes its frequency 3.',
        ],
        'why': 'Titles, labels and scales define the meaning of the marks. Reading them first prevents counting the wrong quantity.',
        'another': 'Make a small tally table for the relevant categories, then compare the totals.',
        'example': 'For 1, 2, 2, 2, 5, the mode is 2 because it occurs most often.',
    },
    'general': {
        'title': 'Make the question smaller',
        'stages': [
            'What is the question asking you to find, and which information matters?',
            'Underline the useful information, choose one operation or representation, and complete only the first step.',
            'Try a smaller example with different numbers, explain its first step, then use the same structure on your question.',
        ],
        'why': 'Separating the goal, information and first step reduces the amount you need to hold in mind at once.',
        'another': 'Draw a diagram, act out the quantities, or explain the problem aloud in your own words.',
        'example': 'For a separate problem asking for 3 groups of 4, draw three equal groups before calculating.',
    },
}


def question_family(question: legacy.Question) -> str:
    skill = question.skill.split(':', 1)[-1].lower()
    prompt = (question.prompt or '').lower()
    topic = (question.topic or '').lower()
    if any(word in skill for word in ('grid', 'coordinate')) or 'grid reference' in prompt:
        return 'grid'
    if any(word in skill for word in ('fraction', 'decimal_fraction')) or '/' in prompt:
        return 'fraction'
    if any(word in skill for word in ('clock', 'duration', 'time')) or re.search(r'\d{1,2}:\d{2}', prompt):
        return 'time'
    if topic == 'statistics' or any(word in skill for word in ('data', 'frequency', 'mode', 'graph', 'chart')):
        return 'data'
    if topic == 'measurement' or any(word in skill for word in ('area', 'perimeter', 'length', 'mass', 'capacity', 'angle')):
        return 'measurement'
    if topic == 'algebra' or any(word in skill for word in ('unknown', 'equation', 'balance')) or '□' in prompt:
        return 'equation'
    if topic == 'number' or any(word in skill for word in ('addition', 'subtraction', 'multiplication', 'division', 'fact', 'operations')):
        return 'arithmetic'
    return 'general'


def guided_plan(question: legacy.Question) -> dict[str, Any]:
    family = question_family(question)
    return {'family': family, **PLANS[family]}


def hint_text_v0200(question: legacy.Question, hint_number: int) -> str:
    plan = guided_plan(question)
    stage = min(3, max(1, hint_number))
    return plan['stages'][stage - 1]


def _latest_misconception(question: legacy.Question) -> dict[str, str] | None:
    wrong = next((attempt for attempt in reversed(sorted(question.attempts, key=lambda item: item.attempt_number)) if not attempt.correct), None)
    if not wrong:
        return None
    detected = v090.misconception_for(question, wrong.answer)
    if detected:
        return detected
    family = question_family(question)
    messages = {
        'arithmetic': 'Check whether the operation and place values were interpreted correctly before recalculating.',
        'equation': 'The unknown may not have been isolated with the inverse operation. Check the value in the original equation.',
        'time': 'Check the hour and minute landmarks separately before combining the elapsed time.',
        'data': 'Re-read the labels and scale to make sure the intended category or frequency was counted.',
    }
    message = messages.get(family)
    return {'type': f'{family}_reasoning', 'message': message} if message else None


@app.get('/api/questions/{qid}/guided-support')
def guided_support(
    qid: int,
    action: SupportAction = 'hint',
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not worksheet or worksheet.student_id != user.id:
        raise HTTPException(403, 'Question does not belong to this student')
    plan = guided_plan(question)
    stage = min(3, max(1, question.hint_count or 1))
    body = plan['stages'][stage - 1]
    if action == 'why':
        body = plan['why']
    elif action == 'another':
        body = plan['another']
    elif action == 'teach':
        body = ' '.join(plan['stages'][:2])
    return {
        'action': action,
        'family': plan['family'],
        'title': plan['title'],
        'stage': stage,
        'body': body,
        'example': plan['example'] if action in ('teach', 'another') or stage == 3 else None,
        'misconception': _latest_misconception(question),
        'final_answer_revealed': False,
    }


@app.get('/api/v0200/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'guided_tutor': True,
        'ask_before_tell': True,
        'hint_stages': 3,
        'question_families': ['arithmetic', 'fraction', 'measurement', 'grid', 'time', 'data', 'equation'],
        'actions': ['why', 'teach', 'another', 'start_over'],
        'misconception_routing': True,
        'worked_examples_use_different_questions': True,
    }


legacy.hint_text = hint_text_v0200
v0120._move_spa_fallback_to_end()
