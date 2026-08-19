from __future__ import annotations

import json
import random
import re
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import main as legacy
from . import v0120, v0200, v0260, v0280, v090

app = v0280.app
app.version = '0.29.0'
legacy.APP_VERSION = '0.29.0'


class LearningEvidence(legacy.Base):
    __tablename__ = 'learning_evidence'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), index=True)
    worksheet_id: Mapped[int] = mapped_column(ForeignKey('worksheets.id'), index=True)
    event_type: Mapped[str] = mapped_column(String(40), index=True)
    skill: Mapped[str] = mapped_column(String(80), index=True)
    detail: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class MisconceptionEvidence(legacy.Base):
    __tablename__ = 'misconception_evidence'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), index=True)
    skill: Mapped[str] = mapped_column(String(80), index=True)
    misconception_type: Mapped[str] = mapped_column(String(60), index=True)
    message: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class PrerequisiteLink(legacy.Base):
    __tablename__ = 'prerequisite_links'
    __table_args__ = (UniqueConstraint('skill', 'prerequisite', name='uq_prerequisite_skill_pair'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    skill: Mapped[str] = mapped_column(String(80), index=True)
    prerequisite: Mapped[str] = mapped_column(String(80))
    depth: Mapped[int] = mapped_column(default=1)


GRAPH: dict[str, list[str]] = {
    'equivalent_fractions': ['fraction_understanding', 'multiplication_facts', 'division_facts'],
    'fraction_number_line': ['fraction_understanding', 'number_line'],
    'efficient_add_subtract': ['place_value', 'addition_facts', 'subtraction_facts'],
    'efficient_multiply_divide': ['multiplication_facts', 'division_facts'],
    'written_addition': ['place_value', 'addition_facts'],
    'written_subtraction': ['place_value', 'subtraction_facts'],
    'fact_families': ['multiplication_facts', 'division_facts'],
    'unknown_add_subtract': ['addition_facts', 'subtraction_facts'],
    'powers_of_ten': ['place_value', 'multiplication_facts'],
    'money_change': ['place_value', 'subtraction_facts'],
    'perimeter': ['length_measurement', 'addition_facts'],
    'area': ['length_measurement', 'multiplication_facts'],
}


def _family(question: legacy.Question) -> str:
    return v0200.question_family(question)


def _numbers(prompt: str) -> list[str]:
    return re.findall(r'\d+(?:\.\d+)?(?:/\d+)?', prompt or '')


def aligned_worked_example(question: legacy.Question) -> str:
    """Return a different-number example with the same operation and strategy."""
    prompt = question.prompt or ''
    skill = question.skill.split(':', 1)[-1].lower()
    nums = _numbers(prompt)
    if any(token in skill for token in ('multiplication', 'multiply')) or '×' in prompt:
        a, b = (int(nums[0]) if nums else 42), (int(nums[1]) if len(nums) > 1 else 6)
        a = max(12, min(99, a + 5)); b = max(3, min(12, b + 1))
        return f'For {a} × {b}, partition {a} into {a // 10 * 10} and {a % 10}. Calculate {a // 10 * 10} × {b}, then {a % 10} × {b}, and add the partial products.'
    if any(token in skill for token in ('division', 'quotient')) or '÷' in prompt:
        divisor = max(2, min(12, int(nums[1]) + 1 if len(nums) > 1 else 6))
        quotient = max(3, min(20, int(nums[0]) // divisor + 2 if nums else 8))
        dividend = divisor * quotient
        return f'For {dividend} ÷ {divisor}, ask how many groups of {divisor} make {dividend}. Use the related multiplication fact {divisor} × {quotient} = {dividend}, so the quotient is {quotient}.'
    if any(token in skill for token in ('subtraction', 'subtract')) or '−' in prompt or ' - ' in prompt:
        a, b = (int(nums[0]) if nums else 63), (int(nums[1]) if len(nums) > 1 else 27)
        a += 7; b = max(2, b - 1)
        return f'For {a} − {b}, regroup one ten if the ones do not subtract. Subtract the ones first, then subtract the tens, and combine the place-value results.'
    if any(token in skill for token in ('addition', 'add')) or ' + ' in prompt:
        a, b = (int(nums[0]) if nums else 47), (int(nums[1]) if len(nums) > 1 else 28)
        a += 6; b += 4
        return f'For {a} + {b}, partition {b} into tens and ones. Add {a} + {b // 10 * 10}, then add the remaining {b % 10}, and check the total.'
    if any(token in skill for token in ('unknown', 'equation')) or '□' in prompt:
        value = max(7, int(nums[-1]) + 3 if nums else 19)
        addend = max(3, int(nums[0]) + 1 if nums else 7)
        return f'For □ + {addend} = {value + addend}, undo addition with subtraction: {value + addend} − {addend}. Substitute the result back to check both sides.'
    if _family(question) == 'fraction' or '/' in prompt:
        return 'For a separate comparison, compare 5/8 and 3/4 by renaming 3/4 as eighths: 3/4 = 6/8. Compare the numerators only after the wholes match.'
    if _family(question) == 'measurement':
        return 'For a different rectangle measuring 8 cm by 3 cm, choose the requested attribute first. Perimeter traces the outside, 8 + 3 + 8 + 3; area covers the inside, 8 × 3.'
    return 'For a different problem, identify the known information, choose the same operation or representation, complete one step, and check the result against the question.'


def _too_easy(question: legacy.Question) -> bool:
    values = [int(value) for value in re.findall(r'(?<![A-Za-z])\d+(?![A-Za-z])', question.prompt or '')]
    return len(values) >= 2 and max(values) <= 10 and any(symbol in question.prompt for symbol in ('+', '−', '×', '÷'))


def create_worksheet_v0290(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = v0260.create_worksheet_v0260(session, student_id, selected, **kwargs)
    rng = random.Random(f'v0290:{worksheet.id}')
    for index, question in enumerate(sorted(worksheet.questions, key=lambda item: item.position)):
        if _too_easy(question) and index % 6 != 0:
            skill, prompt, answer_type, payload, answer, working = legacy.make_question(question.topic, min(4, question.level + 1), rng)
            question.skill, question.prompt, question.answer_type = skill, prompt, answer_type
            question.payload, question.correct_answer, question.working = json.dumps(payload), str(answer), working
    session.commit()
    session.refresh(worksheet)
    return worksheet


def _record(session: Session, user: legacy.User, question: legacy.Question, event: str, detail: dict[str, Any]) -> None:
    session.add(LearningEvidence(student_id=user.id, question_id=question.id, worksheet_id=question.worksheet_id, event_type=event, skill=question.skill, detail=json.dumps(detail)))


def _misconception(question: legacy.Question, answer: str) -> tuple[str, str] | None:
    detected = v090.misconception_for(question, answer)
    if detected:
        return detected.get('type', 'reasoning'), detected.get('message', 'Check the strategy and try the question again.')
    family = _family(question)
    return {
        'arithmetic': ('operation_or_place_value', 'Check the operation and place value before recalculating.'),
        'equation': ('inverse_operation', 'Use the inverse operation, then substitute the value back into the equation.'),
        'fraction': ('fraction_whole', 'Make sure the fractions describe equal-sized wholes before comparing them.'),
        'data': ('scale_or_label', 'Read the title, labels and scale before counting or comparing.'),
    }.get(family)


def _next_support(question: legacy.Question) -> str:
    if not question.mentor_started:
        return 'guiding_question'
    hint_count = question.hint_count or 0
    return ('hint_1', 'hint_2', 'hint_3')[min(hint_count, 2)] if hint_count < 3 else 'worked_example'


def _remove_route(path: str, method: str) -> None:
    app.router.routes[:] = [route for route in app.router.routes if not (getattr(route, 'path', None) == path and method in getattr(route, 'methods', set()))]


_remove_route('/api/questions/{qid}/answer', 'POST')


@app.post('/api/questions/{qid}/answer')
def answer_optional_tutor(qid: int, data: legacy.AnswerIn, u: legacy.User = Depends(legacy.current_user), s: Session = Depends(legacy.db)):
    question = s.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = s.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(u, worksheet):
        raise HTTPException(404, 'Worksheet not found')
    count = s.query(legacy.Attempt).filter_by(question_id=qid, student_id=u.id).count()
    max_attempts = 2 if worksheet.session_kind == 'parent_test' or u.role == 'parent' else 6
    if count >= max_attempts:
        raise HTTPException(400, 'No attempts remaining')
    correct = legacy.normalise(data.answer) == legacy.normalise(question.correct_answer)
    s.add(legacy.Attempt(question_id=qid, student_id=u.id, answer=str(data.answer), correct=correct, attempt_number=count + 1, seconds=max(0, data.seconds)))
    reveal = correct or count + 1 >= max_attempts
    question.state = 'answered_correct' if correct else 'answered_incorrect' if reveal else 'mentor_active'
    question.answered_at = datetime.utcnow() if reveal else question.answered_at
    _record(s, u, question, 'first_attempt_success' if count == 0 and correct else 'attempt', {'attempt_number': count + 1, 'correct': correct, 'hints_used': question.hint_count or 0, 'worked_example_seen': bool(question.mentor_example_seen)})
    if not correct:
        detected = _misconception(question, str(data.answer))
        if detected:
            kind, message = detected
            s.add(MisconceptionEvidence(student_id=u.id, question_id=qid, skill=question.skill, misconception_type=kind, message=message))
            _record(s, u, question, 'misconception_signal', {'type': kind, 'message': message})
    worksheet.last_active_at = datetime.utcnow()
    s.commit()
    return {'correct': correct, 'attempt_number': count + 1, 'retry_allowed': not reveal, 'correct_answer': question.correct_answer if reveal else None, 'working': question.working if reveal else None, 'mentor_required': False, 'next_support': _next_support(question) if not correct and not reveal else None, 'message': 'Great job!' if correct else ('Have another look, or choose a Math Mentor tool when you want one.' if not reveal else 'Here is how to solve it.')}


_remove_route('/api/questions/{qid}/math-mentor', 'GET')


@app.get('/api/questions/{qid}/math-mentor')
def math_mentor_v0290(qid: int, action: str = 'guide', user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(user, worksheet):
        raise HTTPException(403, 'Question does not belong to this worksheet account')
    if action == 'worked_example':
        question.mentor_example_seen = True
        session.commit()
    payload = v0280._mentor_payload(question, action if action in ('guide', 'hint', 'why', 'teach') else 'worked_example')
    payload['worked_example'] = aligned_worked_example(question)
    payload['example_is_aligned'] = True
    return payload


@app.get('/api/learning/prerequisite-graph')
def prerequisite_graph(_: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    with session.no_autoflush:
        for skill, prerequisites in GRAPH.items():
            for depth, prerequisite in enumerate(prerequisites, 1):
                if not session.scalar(select(PrerequisiteLink).where(PrerequisiteLink.skill == skill, PrerequisiteLink.prerequisite == prerequisite)):
                    session.add(PrerequisiteLink(skill=skill, prerequisite=prerequisite, depth=depth))
    session.commit()
    return {'graph': [{'skill': skill, 'prerequisites': prerequisites} for skill, prerequisites in GRAPH.items()]}


@app.get('/api/learning/recommendations')
def recommendations(user: legacy.User = Depends(legacy.parent), session: Session = Depends(legacy.db)):
    try:
        student = v0120.resolve_learner(session)
    except HTTPException:
        return {'recommendations': [{'type': 'retrieval', 'title': 'Practice a recently learned skill tomorrow', 'reason': 'Short spaced retrieval will confirm whether recent success is retained.', 'minutes': 10}], 'evidence_events': 0}
    signals = session.scalars(select(MisconceptionEvidence).where(MisconceptionEvidence.student_id == student.id, MisconceptionEvidence.resolved == False).order_by(MisconceptionEvidence.created_at.desc())).all()
    grouped: dict[str, int] = {}
    for signal in signals:
        grouped[signal.misconception_type] = grouped.get(signal.misconception_type, 0) + 1
    repeated = sorted(grouped.items(), key=lambda item: (-item[1], item[0]))
    return {'recommendations': ([{'type': 'misconception', 'title': f'Review {kind.replace("_", " ")}', 'reason': f'This pattern has appeared {count} times.', 'minutes': 10} for kind, count in repeated if count >= 2][:3] or [{'type': 'retrieval', 'title': 'Practice a recently learned skill tomorrow', 'reason': 'Short spaced retrieval will confirm whether recent success is retained.', 'minutes': 10}]), 'evidence_events': session.query(LearningEvidence).filter_by(student_id=student.id).count()}


@app.get('/api/v0290/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {'version': '0.29.0', 'optional_tutoring': True, 'question_aligned_examples': True, 'prerequisite_graph': True, 'misconception_detection': True, 'evidence_collection': True, 'parent_recommendations': True}


legacy.create_worksheet = create_worksheet_v0290
v0120._move_spa_fallback_to_end()
