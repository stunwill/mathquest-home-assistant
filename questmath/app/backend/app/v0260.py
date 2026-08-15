from __future__ import annotations

import json
import random
import re
from datetime import datetime
from typing import Any, Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0110, v0120, v0160, v0170, v0230, v0240, v0250

app = v0250.app
app.version = legacy.APP_VERSION

_prior_create_worksheet = legacy.create_worksheet
_prior_worksheet_view = legacy.worksheet_view
_prior_dashboard_stats = v0110.dashboard_stats

INTERVENTION_FOCUSES = (
    'addition', 'subtraction', 'multiplication', 'division', 'equations', 'fact_families',
)


class InterventionCreateIn(BaseModel):
    minutes: Literal[5, 10, 15] = 10
    focus: Literal['auto', 'addition', 'subtraction', 'multiplication', 'division', 'equations', 'fact_families'] = 'auto'


def _safe_payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _recommended_model(question: legacy.Question) -> str:
    skill = question.skill.split(':', 1)[-1].lower()
    prompt = (question.prompt or '').lower()
    if 'fraction' in skill or '/' in prompt:
        return 'fractions'
    if any(value in skill for value in ('written_', 'place_value')):
        return 'place-value'
    if any(value in skill for value in ('multiplication', 'division', 'fact_famil')):
        return 'arrays'
    if any(value in skill for value in ('unknown', 'equation')) or '□' in prompt:
        return 'number-line'
    if any(value in skill for value in ('addition', 'subtraction', 'operations', 'fact_recall')):
        return 'number-line'
    if any(value in skill for value in ('clock', 'duration', 'time')):
        return 'clock'
    if any(value in skill for value in ('grid', 'coordinate')):
        return 'grid'
    if question.topic == 'measurement':
        return 'measurement'
    return 'number-line'


def _operation_values(prompt: str) -> list[int]:
    return [int(value) for value in re.findall(r'\d+', prompt or '')[:2]]


def _annotate_question(question: legacy.Question, worksheet: legacy.Worksheet) -> None:
    payload = _safe_payload(question)
    payload['visual_key'] = f'{worksheet.id}:{question.id}'
    payload.setdefault('recommended_model', _recommended_model(question))
    values = _operation_values(question.prompt)
    if values:
        payload.setdefault('model_example', {
            'values': [max(2, min(12, value // 2 or 2)) for value in values],
            'uses_assessed_values': False,
        })
    question.payload = json.dumps(payload)


def create_worksheet_v0260(
    session: Session,
    student_id: int,
    selected: str,
    *,
    question_count: int | None = None,
    session_kind: str = 'practice',
    target_minutes: int | None = None,
    learning_profile_id: int | None = None,
) -> legacy.Worksheet:
    """One worksheet factory used by practice, timed, adaptive, story and parent-test flows."""
    worksheet = _prior_create_worksheet(
        session,
        student_id,
        selected,
        question_count=question_count,
        session_kind=session_kind,
        target_minutes=target_minutes,
        learning_profile_id=learning_profile_id,
    )
    for question in worksheet.questions:
        _annotate_question(question, worksheet)
    session.commit()
    session.refresh(worksheet)
    return worksheet


def worksheet_evidence(worksheet: legacy.Worksheet) -> dict[str, Any]:
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    statuses = [legacy.question_status(question) for question in questions]
    answered = [question for question in questions if question.attempts]
    independent_correct = 0
    supported_correct = 0
    for question in answered:
        attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
        if attempts and attempts[0].correct and not (question.hint_count or 0):
            independent_correct += 1
        if any(attempt.correct for attempt in attempts):
            supported_correct += 1
    return {
        'total': len(questions),
        'answered': len(answered),
        'completed': sum(status in ('correct', 'incorrect') for status in statuses),
        'correct': sum(status == 'correct' for status in statuses),
        'incorrect': sum(status == 'incorrect' for status in statuses),
        'skipped': sum(status == 'skipped' for status in statuses),
        'remaining': sum(status in ('not_started', 'current', 'retry_available', 'skipped') for status in statuses),
        'hints': sum(question.hint_count or 0 for question in questions),
        'independent_correct': independent_correct,
        'supported_correct': supported_correct,
        'independent_accuracy': round(independent_correct / len(answered) * 100) if answered else None,
        'supported_accuracy': round(supported_correct / len(answered) * 100) if answered else None,
    }


def worksheet_view_v0260(worksheet: legacy.Worksheet) -> dict[str, Any]:
    view = _prior_worksheet_view(worksheet)
    evidence = worksheet_evidence(worksheet)
    view['counts'] = {
        'correct': evidence['correct'], 'incorrect': evidence['incorrect'],
        'skipped': evidence['skipped'], 'remaining': evidence['remaining'],
        'hints': evidence['hints'], 'answered': evidence['answered'],
        'completed': evidence['completed'],
    }
    view['evidence'] = {
        'independent_correct': evidence['independent_correct'],
        'supported_correct': evidence['supported_correct'],
        'independent_accuracy': evidence['independent_accuracy'],
        'supported_accuracy': evidence['supported_accuracy'],
    }
    for item, question in zip(view['questions'], sorted(worksheet.questions, key=lambda value: value.position)):
        payload = item.get('payload') if isinstance(item.get('payload'), dict) else {}
        payload.setdefault('visual_key', f'{worksheet.id}:{question.id}')
        payload.setdefault('recommended_model', _recommended_model(question))
        item['payload'] = payload
    return view


def _fact_family(rng: random.Random):
    left, right = rng.randint(2, 10), rng.randint(2, 10)
    product = left * right
    missing = rng.choice(['factor', 'quotient'])
    if missing == 'factor':
        prompt, answer = f'Complete the fact family: {left} × □ = {product}.', right
    else:
        prompt, answer = f'Complete the fact family: {product} ÷ {left} = □.', right
    payload = {
        'operation': 'fact_families',
        'strategy_card': v0170._card(
            'Multiplication and division fact family', 'Use the inverse relationship',
            f'{left} × {right} = {product}, so {product} ÷ {left} = {right}.',
            ['Name the two factors and their product.', 'Write the related multiplication fact.',
             'Turn it into a division fact and identify the missing value.'],
            'Example: 6 × 7 = 42, so 42 ÷ 6 = 7.', 'fact_families',
        ),
    }
    return legacy.q(
        'VC2M4A02', 'fact_families', prompt, 'number', payload, answer,
        f'Use the related facts: {left} × {right} = {product} and {product} ÷ {left} = {right}.',
    )


GENERATORS = {
    'addition': [v0170._addition_fact, v0170._written_addition],
    'subtraction': [v0170._subtraction_fact, v0170._written_subtraction],
    'multiplication': [v0170._multiplication_fact, _fact_family],
    'division': [v0170._division_fact, _fact_family],
    'equations': [v0170._unknown_equation, v0170._addition_fact, v0170._subtraction_fact],
    'fact_families': [_fact_family, v0170._multiplication_fact, v0170._division_fact],
}


def intervention_report(session: Session, student_id: int) -> dict[str, Any]:
    questions = list(session.scalars(
        select(legacy.Question).join(legacy.Worksheet).where(
            legacy.Worksheet.student_id == student_id,
            legacy.Worksheet.session_kind != 'parent_test',
            legacy.Question.answered_at.is_not(None),
        ).order_by(legacy.Question.answered_at.desc(), legacy.Question.id.desc()).limit(600)
    ).all())
    results = []
    for focus in INTERVENTION_FOCUSES:
        relevant = []
        for question in questions:
            skill = question.skill.split(':', 1)[-1]
            operation = _safe_payload(question).get('operation')
            if focus == 'equations' and skill == 'unknown_add_subtract':
                relevant.append(question)
            elif focus == 'fact_families' and skill == 'fact_families':
                relevant.append(question)
            elif focus in ('addition', 'subtraction', 'multiplication', 'division') and operation == focus:
                relevant.append(question)
        relevant = relevant[:30]
        independent = 0
        supported = 0
        for question in relevant:
            attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
            independent += int(bool(attempts and attempts[0].correct and not (question.hint_count or 0)))
            supported += int(any(attempt.correct for attempt in attempts))
        count = len(relevant)
        results.append({
            'focus': focus,
            'questions': count,
            'independent_accuracy': round(independent / count * 100) if count else None,
            'supported_accuracy': round(supported / count * 100) if count else None,
            'support_gap': round((supported - independent) / count * 100) if count else None,
            'hints': sum(question.hint_count or 0 for question in relevant),
            'status': 'not_assessed' if count < 3 else 'secure' if independent / count >= .85 else 'developing' if independent / count >= .55 else 'needs_support',
        })
    assessed = [item for item in results if item['questions']]
    target = min(assessed, key=lambda item: (item['independent_accuracy'], -item['support_gap'], item['focus'])) if assessed else results[0]
    return {
        'recommended_focus': target['focus'],
        'reason': 'Build independent accuracy in the area with the weakest recent evidence.' if assessed else 'Start with efficient addition facts, then use the evidence to choose the next prerequisite.',
        'focuses': results,
        'available_minutes': [5, 10, 15],
    }


def _replace_with_intervention(
    session: Session,
    worksheet: legacy.Worksheet,
    focus: str,
) -> None:
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    generators = GENERATORS[focus]
    seen: set[tuple[str, tuple[str, ...]]] = set()
    for index, question in enumerate(questions):
        phase = 'check' if index == 0 else 'teach' if index == 1 else 'retrieval' if index == len(questions) - 1 else 'practice'
        generated = None
        for attempt in range(80):
            generator = generators[index % len(generators)]
            candidate = generator(random.Random(f'intervention:{worksheet.id}:{focus}:{index}:{attempt}'))
            identity = legacy.question_identity(candidate[1], candidate[3])
            if identity not in seen:
                generated = candidate
                seen.add(identity)
                break
        if generated is None:
            raise HTTPException(503, 'Unable to create a unique intervention session')
        skill, prompt, answer_type, payload, answer, working = generated
        payload['intervention'] = {
            'focus': focus,
            'phase': phase,
            'learning_goal': f'Use an efficient {focus.replace("_", " ")} strategy and explain how it can be checked.',
            'measure_independently': True,
        }
        question.topic = 'algebra' if focus in ('equations', 'fact_families', 'multiplication', 'division') else 'number'
        question.skill, question.prompt, question.answer_type = skill, prompt, answer_type
        question.payload, question.correct_answer, question.working = json.dumps(payload), str(answer), working
        _annotate_question(question, worksheet)
    session.commit()
    session.refresh(worksheet)


@app.get('/api/learning/intervention-v0260')
def intervention_snapshot(
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return intervention_report(session, student_id)


@app.post('/api/interventions/new')
def new_intervention(
    payload: InterventionCreateIn,
    user: legacy.User = Depends(legacy.current_user),
    session: Session = Depends(legacy.db),
):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    report = intervention_report(session, user.id)
    focus = report['recommended_focus'] if payload.focus == 'auto' else payload.focus
    count = {5: 5, 10: 8, 15: 12}[payload.minutes]
    worksheet = legacy.create_worksheet(
        session, user.id, 'number_algebra', question_count=count,
        session_kind='intervention', target_minutes=payload.minutes,
    )
    _replace_with_intervention(session, worksheet, focus)
    result = legacy.worksheet_view(worksheet)
    result['intervention'] = {
        'focus': focus,
        'minutes': payload.minutes,
        'reason': report['reason'],
        'phases': ['check', 'teach', 'practice', 'retrieval'],
    }
    return result


def dashboard_stats_v0260(session: Session, student_id: int) -> dict[str, Any]:
    result = _prior_dashboard_stats(session, student_id)
    today = datetime.now().date()
    worksheets = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.worksheet_date == today,
        legacy.Worksheet.session_kind != 'parent_test',
    )).all())
    evidence = [worksheet_evidence(worksheet) for worksheet in worksheets]
    result['evidence_reconciliation'] = {
        'worksheets': len(worksheets),
        'answered': sum(item['answered'] for item in evidence),
        'completed': sum(item['completed'] for item in evidence),
        'correct': sum(item['correct'] for item in evidence),
        'incorrect': sum(item['incorrect'] for item in evidence),
        'skipped': sum(item['skipped'] for item in evidence),
        'hints': sum(item['hints'] for item in evidence),
        'parent_tests_excluded': True,
    }
    result['intervention'] = intervention_report(session, student_id)
    return result


@app.get('/api/v0260/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'number_algebra_intervention': True,
        'intervention_focuses': list(INTERVENTION_FOCUSES),
        'intervention_minutes': [5, 10, 15],
        'shared_worksheet_factory': True,
        'question_visual_keys': True,
        'independent_supported_reporting': True,
        'parent_test_evidence_excluded': True,
        'inherits_v0250': True,
    }


legacy.create_worksheet = create_worksheet_v0260
legacy.worksheet_view = worksheet_view_v0260
v0110.dashboard_stats = dashboard_stats_v0260
v0120._move_spa_fallback_to_end()
