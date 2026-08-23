from __future__ import annotations

import json
import math
import re
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0200, v0260, v0290, v0291

app = v0291.app
app.version = '0.30.0'
legacy.APP_VERSION = '0.30.0'


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _skill(question: legacy.Question) -> str:
    return (question.skill or '').split(':', 1)[-1].lower()


def _numbers(prompt: str) -> list[int]:
    return [int(value) for value in re.findall(r'\d+', prompt or '')]


def visual_model_for(question: legacy.Question) -> str:
    skill = _skill(question)
    prompt = (question.prompt or '').lower()
    if 'fraction' in skill or re.search(r'\b\d+\s*/\s*\d+\b', prompt):
        return 'fractions'
    if any(token in skill for token in ('written_', 'place_value', 'regroup')):
        return 'place-value'
    if any(token in skill for token in ('multiplication', 'division', 'fact_famil')):
        return 'arrays'
    if any(token in skill for token in ('addition', 'subtraction', 'unknown', 'equation', 'number_line')):
        return 'number-line'
    if any(token in skill for token in ('clock', 'duration', 'time')):
        return 'clock'
    if any(token in skill for token in ('grid', 'coordinate')):
        return 'grid'
    if question.topic == 'measurement':
        return 'measurement'
    return v0260._recommended_model(question)


def visual_reason(model: str) -> str:
    return {
        'fractions': 'Equal-sized wholes and common partitions make the compared amounts visible.',
        'arrays': 'Equal rows or an area model show the factors, groups and total together.',
        'place-value': 'Aligned place-value parts show regrouping without changing the number.',
        'number-line': 'The jumps on the number line match the changes made in the calculation.',
        'measurement': 'A labelled scale connects the measurement marks to the chosen unit.',
        'clock': 'The clock connects elapsed-time jumps to the movement of the hands.',
        'grid': 'The labelled axes show position while keeping the assessed reference hidden.',
    }.get(model, 'The visual shows the same mathematical relationship as the written strategy.')


def _safe_fraction_items(question: legacy.Question) -> list[dict[str, Any]]:
    payload = _payload(question)
    existing = payload.get('visual') if isinstance(payload.get('visual'), dict) else {}
    if existing.get('type') == 'fraction_compare' and isinstance(existing.get('items'), list):
        return existing['items'][:2]
    fractions = re.findall(r'(\d+)\s*/\s*(\d+)', question.prompt or '')
    if len(fractions) >= 2:
        items = []
        for index, (numerator, denominator) in enumerate(fractions[:2]):
            d = max(1, int(denominator))
            n = max(0, min(d, int(numerator)))
            items.append({'label': 'First fraction' if index == 0 else 'Second fraction', 'numerator': n, 'denominator': d})
        return items
    return [{'label': 'Example A', 'numerator': 2, 'denominator': 3}, {'label': 'Example B', 'numerator': 3, 'denominator': 4}]


def _teaching_example(question: legacy.Question, model: str) -> dict[str, Any]:
    values = _numbers(question.prompt)
    if model == 'fractions':
        return {
            'type': 'fraction_compare',
            'items': [{'label': 'Example A', 'numerator': 2, 'denominator': 3}, {'label': 'Example B', 'numerator': 3, 'denominator': 4}],
            'equal_whole': True,
            'assessed_values': False,
        }
    if model == 'arrays':
        return {'type': 'array', 'rows': 4, 'columns': 6, 'assessed_values': False}
    if model == 'place-value':
        return {'type': 'place_value', 'value': 364, 'assessed_values': False}
    if model == 'measurement':
        return {'type': 'measurement', 'length': 7, 'width': 4, 'unit': 'cm', 'assessed_values': False}
    if model == 'clock':
        return {'type': 'clock', 'hour': 2, 'minute': 35, 'assessed_values': False}
    if model == 'grid':
        return {'type': 'grid_practice', 'columns': ['A', 'B', 'C', 'D'], 'rows': 4, 'assessed_values': False}
    start = max(0, (values[0] if values else 36) - 6)
    return {'type': 'number_line', 'min': start, 'max': start + 30, 'marker': start + 12, 'assessed_values': False}


def _safe_visual_payload(question: legacy.Question, worksheet: legacy.Worksheet | None) -> dict[str, Any]:
    model = visual_model_for(question)
    assessment = bool(worksheet and worksheet.session_kind == 'parent_test')
    result: dict[str, Any] = {
        'recommended_model': model,
        'visual_reason': visual_reason(model),
        'teaching_visual_available': not assessment,
        'assessment_restricted': assessment,
    }
    if model == 'fractions':
        result['fraction_comparison'] = {
            'items': _safe_fraction_items(question),
            'equal_whole': True,
            'vertical_alignment': True,
            'number_line_available': True,
            'equivalence_available': True,
        }
    if not assessment:
        result['teaching_example'] = _teaching_example(question, model)
    return result


def _strategy_set(question: legacy.Question) -> list[dict[str, str]]:
    skill = _skill(question)
    prompt = question.prompt or ''
    values = _numbers(prompt)
    if ('addition' in skill or ' + ' in prompt) and len(values) >= 2:
        a, b = values[:2]
        tens, ones = (b // 10) * 10, b % 10
        return [
            {'id': 'partition', 'title': 'Partition the second number', 'explanation': f'Keep {a} whole, add {tens}, then add {ones}.', 'visual_model': 'number-line'},
            {'id': 'compensate', 'title': 'Compensate to a friendly number', 'explanation': 'Adjust one number to a nearby ten, calculate, then undo the adjustment.', 'visual_model': 'number-line'},
            {'id': 'place-value', 'title': 'Add by place value', 'explanation': 'Combine matching place values, regroup if needed, then recombine.', 'visual_model': 'place-value'},
        ]
    if ('subtraction' in skill or '−' in prompt or ' - ' in prompt) and len(values) >= 2:
        return [
            {'id': 'partition', 'title': 'Subtract in parts', 'explanation': 'Subtract tens first, then subtract the remaining ones.', 'visual_model': 'number-line'},
            {'id': 'compensate', 'title': 'Count from a friendly number', 'explanation': 'Bridge through a nearby ten and combine the jumps.', 'visual_model': 'number-line'},
            {'id': 'place-value', 'title': 'Use place value and regrouping', 'explanation': 'Regroup one higher place only when the lower place needs it.', 'visual_model': 'place-value'},
        ]
    if 'fraction' in skill or '/' in prompt:
        return [
            {'id': 'equal-wholes', 'title': 'Compare equal-sized fraction bars', 'explanation': 'Keep both wholes the same size and compare the shaded lengths.', 'visual_model': 'fractions'},
            {'id': 'equivalent', 'title': 'Rename with equivalent fractions', 'explanation': 'Create matching partitions before comparing the numerators.', 'visual_model': 'fractions'},
            {'id': 'number-line', 'title': 'Place both fractions on one number line', 'explanation': 'The fraction farther to the right is larger.', 'visual_model': 'number-line'},
        ]
    if any(token in skill for token in ('multiplication', 'division', 'fact_famil')):
        return [
            {'id': 'array', 'title': 'Use an array', 'explanation': 'Show equal rows and columns so the factors or groups are visible.', 'visual_model': 'arrays'},
            {'id': 'partition', 'title': 'Partition a factor', 'explanation': 'Split one factor into friendly parts, calculate partial products, then combine.', 'visual_model': 'arrays'},
            {'id': 'inverse', 'title': 'Use the inverse relationship', 'explanation': 'Connect multiplication and division using the same fact family.', 'visual_model': 'arrays'},
        ]
    return [{'id': 'model', 'title': 'Represent the relationship', 'explanation': visual_reason(visual_model_for(question)), 'visual_model': visual_model_for(question)}]


def evidence_visual_recommendation(session: Session, student_id: int, question: legacy.Question) -> dict[str, Any] | None:
    skill = _skill(question)
    signals = list(session.scalars(select(v0290.MisconceptionEvidence).where(
        v0290.MisconceptionEvidence.student_id == student_id,
        v0290.MisconceptionEvidence.resolved == False,
    ).order_by(v0290.MisconceptionEvidence.created_at.desc()).limit(30)).all())
    relevant = [signal for signal in signals if signal.skill == question.skill or ('fraction' in skill and 'fraction' in signal.misconception_type)]
    if len(relevant) < 2:
        return None
    model = 'fractions' if 'fraction' in skill else visual_model_for(question)
    return {
        'model': model,
        'message': f'Try comparing these with {"equal-whole fraction bars" if model == "fractions" else model.replace("-", " ")}.',
        'reason': 'A similar misconception has appeared more than once in recent learning evidence.',
        'automatic_open': False,
    }


def annotate_visual_mathematics(session: Session, worksheet: legacy.Worksheet) -> legacy.Worksheet:
    for question in worksheet.questions:
        payload = _payload(question)
        payload['visual_mathematics'] = _safe_visual_payload(question, worksheet)
        payload['solution_strategies'] = _strategy_set(question)
        question.payload = json.dumps(payload)
    session.commit()
    session.refresh(worksheet)
    return worksheet


_prior_create_worksheet = legacy.create_worksheet


def create_worksheet_v0300(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return annotate_visual_mathematics(session, worksheet)


@app.get('/api/questions/{qid}/visual-mathematics')
def question_visual_mathematics(qid: int, user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(user, worksheet):
        raise HTTPException(403, 'Question does not belong to this worksheet account')
    visual = _safe_visual_payload(question, worksheet)
    recommendation = None if worksheet.session_kind == 'parent_test' else evidence_visual_recommendation(session, user.id, question)
    return {
        'visual': visual,
        'strategies': _strategy_set(question),
        'recommendation': recommendation,
        'answer_preserved': True,
        'mentor_state_preserved': True,
        'lab_state_client_owned': True,
    }


@app.get('/api/questions/{qid}/math-mentor-v0300')
def math_mentor_visual(qid: int, action: str = 'guide', user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    question = session.get(legacy.Question, qid)
    if not question:
        raise HTTPException(404, 'Question not found')
    worksheet = session.get(legacy.Worksheet, question.worksheet_id)
    if not legacy.worksheet_accessible(user, worksheet):
        raise HTTPException(403, 'Question does not belong to this worksheet account')
    payload = v0290.math_mentor_v0290(qid, action, user, session)
    model = visual_model_for(question)
    payload['visual_recommendation'] = {
        'model': model,
        'message': f'Try the {model.replace("-", " ")} model. {visual_reason(model)}',
        'automatic_open': False,
    }
    payload['visual_connection'] = visual_reason(model)
    payload['strategies'] = _strategy_set(question)
    if worksheet.session_kind != 'parent_test':
        payload['evidence_visual_recommendation'] = evidence_visual_recommendation(session, user.id, question)
    else:
        payload['evidence_visual_recommendation'] = None
    return payload


@app.get('/api/v0300/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.30.0',
        'release_name': 'Visual Mathematics',
        'equal_whole_fraction_comparison': True,
        'interactive_fraction_models': True,
        'shared_visual_models': ['fraction', 'number_line', 'array', 'place_value', 'measurement'],
        'multiple_solution_strategies': True,
        'mentor_visual_recommendations': True,
        'learning_evidence_visual_recommendations': True,
        'parent_test_teaching_aids_hidden': True,
        'retry_first_preserved': True,
        'inherits_v0291': True,
    }


legacy.create_worksheet = create_worksheet_v0300
v0120._move_spa_fallback_to_end()
