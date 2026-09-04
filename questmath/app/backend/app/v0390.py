from __future__ import annotations

import json
import random
import re
from collections import Counter
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0301, v0321, v0330, v0381

app = v0381.app
app.version = '0.39.0'
legacy.APP_VERSION = '0.39.0'

_prior_create_worksheet = legacy.create_worksheet


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _regroup_steps(operation: str, left: int, right: int) -> int:
    if operation == 'addition':
        carry = 0
        count = 0
        a, b = left, right
        while a or b or carry:
            total = (a % 10) + (b % 10) + carry
            if total >= 10:
                count += 1
            carry = 1 if total >= 10 else 0
            a //= 10
            b //= 10
        return count
    if operation == 'subtraction' and left >= right:
        count = 0
        borrow = 0
        a, b = left, right
        while a or b:
            top = (a % 10) - borrow
            bottom = b % 10
            if top < bottom:
                count += 1
                borrow = 1
            else:
                borrow = 0
            a //= 10
            b //= 10
        return count
    return 0


def difficulty_dimensions(question: legacy.Question) -> dict[str, Any]:
    prompt = (question.prompt or '').strip()
    match = re.fullmatch(r'Calculate\s+(\d+)\s*([+−\-×x÷/])\s*(\d+)\.', prompt)
    payload = _payload(question)
    if match:
        left, operator, right = int(match.group(1)), match.group(2), int(match.group(3))
        operation = {
            '+': 'addition', '−': 'subtraction', '-': 'subtraction',
            '×': 'multiplication', 'x': 'multiplication',
            '÷': 'division', '/': 'division',
        }[operator]
        return {
            'operation': operation,
            'left_digits': len(str(left)),
            'right_digits': len(str(right)),
            'regroup_steps': _regroup_steps(operation, left, right),
            'representation': question.answer_type,
            'reasoning_type': payload.get('reasoning_type'),
        }
    visual = payload.get('visual') if isinstance(payload.get('visual'), dict) else {}
    adaptive = payload.get('adaptive') if isinstance(payload.get('adaptive'), dict) else {}
    return {
        'operation': payload.get('operation'),
        'representation': visual.get('type') or question.answer_type,
        'reasoning_type': payload.get('reasoning_type'),
        'prerequisite_dependency': bool(adaptive.get('prerequisite_for')),
    }


def question_structure(question: legacy.Question) -> str:
    payload = _payload(question)
    reasoning = payload.get('reasoning_type')
    if reasoning:
        return f"reasoning:{reasoning}"
    dims = difficulty_dimensions(question)
    if dims.get('left_digits'):
        symbol = 'x' if dims['operation'] in {'multiplication', 'division'} else '+'
        return (
            f"direct:{dims['operation']}:"
            f"{dims['left_digits']}d{symbol}{dims['right_digits']}d:"
            f"regroup{min(2, int(dims['regroup_steps']))}"
        )
    return v0301.question_family(question)


def _purposeful_foundation(question: legacy.Question) -> bool:
    payload = _payload(question)
    return payload.get('learning_purpose') in {'review', 'consolidation'} or bool(payload.get('retrieval_item'))


def _is_low_complexity(question: legacy.Question) -> bool:
    dims = difficulty_dimensions(question)
    if dims.get('operation') not in {'addition', 'subtraction'} or not dims.get('left_digits'):
        return False
    max_digits = max(int(dims['left_digits']), int(dims['right_digits']))
    return max_digits <= 2 and int(dims.get('regroup_steps') or 0) <= 1 and not _purposeful_foundation(question)


def _recent_structures(session: Session, student_id: int, current_worksheet_id: int, limit: int = 24) -> Counter[str]:
    rows = list(session.scalars(
        select(legacy.Question)
        .join(legacy.Worksheet)
        .where(
            legacy.Worksheet.student_id == student_id,
            legacy.Worksheet.id != current_worksheet_id,
            legacy.Worksheet.session_kind.in_(['practice', 'adventure']),
            legacy.Question.answered_at.is_not(None),
        )
        .order_by(legacy.Question.answered_at.desc(), legacy.Question.id.desc())
        .limit(limit)
    ).all())
    return Counter(question_structure(question) for question in rows)


def _copy_candidate(question: legacy.Question, worksheet: legacy.Worksheet, candidate: tuple[Any, ...]) -> None:
    skill, prompt, answer_type, payload, answer, working = candidate
    previous_payload = _payload(question)
    preserved = {key: previous_payload[key] for key in ('adventure', 'story', 'mission') if key in previous_payload}
    next_payload = dict(payload if isinstance(payload, dict) else {})
    next_payload.update(preserved)
    question.skill = skill
    question.prompt = prompt
    question.answer_type = answer_type
    question.payload = json.dumps(next_payload)
    question.correct_answer = str(answer)
    question.working = working
    v0321._restore_runtime_annotations(question, worksheet)


def _replacement(
    question: legacy.Question,
    worksheet: legacy.Worksheet,
    rng: random.Random,
    blocked_structures: set[str],
    recent: Counter[str],
) -> bool:
    best: tuple[int, tuple[Any, ...]] | None = None
    for _ in range(220):
        candidate = legacy.make_question(question.topic, max(3, min(4, question.level)), rng)
        skill, prompt, answer_type, payload, answer, working = candidate
        q = legacy.Question(
            worksheet_id=worksheet.id,
            topic=question.topic,
            skill=skill,
            level=question.level,
            prompt=prompt,
            answer_type=answer_type,
            payload=json.dumps(payload if isinstance(payload, dict) else {}),
            correct_answer=str(answer),
            working=working,
            position=question.position,
        )
        structure = question_structure(q)
        if structure in blocked_structures or _is_low_complexity(q):
            continue
        score = recent.get(structure, 0)
        if best is None or score < best[0]:
            best = (score, candidate)
            if score == 0:
                break
    if best is None:
        return False
    _copy_candidate(question, worksheet, best[1])
    return True


def _refresh_adaptive_annotations(session: Session, worksheet: legacy.Worksheet, student_id: int) -> None:
    outcomes = v0230.outcome_mastery(session, student_id)
    outcome_map = {item['code']: item for item in outcomes}
    challenge_used = 0
    challenge_budget = 1 if len(worksheet.questions) >= 5 else 0
    for question in sorted(worksheet.questions, key=lambda item: item.position):
        payload = _payload(question)
        purpose, reason = v0330._purpose_for_question(session, student_id, question, outcome_map)
        if purpose == 'challenge':
            if challenge_used >= challenge_budget:
                purpose = 'current'
                reason = 'Challenge is limited so the session stays balanced.'
            else:
                challenge_used += 1
        evidence = v0330._question_evidence(session, student_id, question.skill)
        state = v0330._progression_state(evidence)
        questions = int(evidence.get('questions', evidence.get('attempts', 0)) or 0)
        independent = float(evidence.get('independent', 0.0) or 0.0)
        eventual = float(evidence.get('eventual', 0.0) or 0.0)
        support = float(evidence.get('support', 0.0) or 0.0)
        payload['learning_purpose'] = purpose
        payload['learning_purpose_label'] = v0330.PURPOSE_LABELS[purpose]
        payload['adaptive_reason'] = reason
        payload['progression_state'] = state
        payload['adaptive_evidence'] = {
            'questions': questions,
            'independent_accuracy': round(independent * 100) if independent <= 1 else round(independent),
            'eventual_accuracy': round(eventual * 100) if eventual <= 1 else round(eventual),
            'support_dependency': round(support * 100) if support <= 1 else round(support),
        }
        question.payload = json.dumps(payload)


def enforce_session_learning_quality(session: Session, worksheet: legacy.Worksheet, student_id: int) -> legacy.Worksheet:
    if worksheet.session_kind == 'parent_test':
        return worksheet

    questions = sorted(worksheet.questions, key=lambda item: item.position)
    if not questions:
        return worksheet

    readiness = v0321.learner_readiness(session, student_id)
    recent = _recent_structures(session, student_id, worksheet.id)
    rng = random.Random(f'v0390:{worksheet.id}:session-quality')
    seen: Counter[str] = Counter()
    low_complexity_budget = 0 if readiness['ready'] else max(1, len(questions) // 6)
    low_complexity_seen = 0

    for question in questions:
        structure = question_structure(question)
        repeated_in_session = seen[structure] >= 1
        overexposed_recently = recent.get(structure, 0) >= 4 and not _purposeful_foundation(question)
        low_complexity = _is_low_complexity(question)
        if low_complexity:
            low_complexity_seen += 1
        over_budget = low_complexity and low_complexity_seen > low_complexity_budget

        if (repeated_in_session or overexposed_recently or over_budget) and not _purposeful_foundation(question):
            blocked = {key for key, count in seen.items() if count}
            if _replacement(question, worksheet, rng, blocked, recent):
                structure = question_structure(question)

        seen[structure] += 1

    _refresh_adaptive_annotations(session, worksheet, student_id)
    for question in questions:
        payload = _payload(question)
        structure = question_structure(question)
        payload['difficulty_dimensions'] = difficulty_dimensions(question)
        payload['session_quality'] = {
            'structure': structure,
            'recent_exposure': int(recent.get(structure, 0)),
            'purposeful_foundation': _purposeful_foundation(question),
            'low_complexity': _is_low_complexity(question),
            'learner_ready': bool(readiness['ready']),
        }
        question.payload = json.dumps(payload)

    session.commit()
    session.refresh(worksheet)
    return worksheet


def create_worksheet_v0390(session: Session, student_id: int, selected: str, **kwargs: Any) -> legacy.Worksheet:
    worksheet = _prior_create_worksheet(session, student_id, selected, **kwargs)
    return enforce_session_learning_quality(session, worksheet, student_id)


legacy.create_worksheet = create_worksheet_v0390


@app.get('/api/v0390/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.39.0',
        'session_level_learning_quality': True,
        'multidimensional_difficulty_metadata': True,
        'recent_structure_exposure': True,
        'near_duplicate_structure_control': True,
        'adaptive_metadata_reconciled_after_quality': True,
        'parent_test_isolation': True,
        'inherits_v0381': True,
    }


v0120._move_spa_fallback_to_end()
