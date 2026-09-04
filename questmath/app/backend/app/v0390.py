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
from . import v0120, v0301, v0321, v0330, v0381

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


def _direct_arithmetic_signature(question: legacy.Question) -> tuple[str, str] | None:
    match = re.fullmatch(r'Calculate\s+(\d+)\s*([+−\-×x÷/])\s*(\d+)\.', (question.prompt or '').strip())
    if not match:
        return None
    left, operator, right = int(match.group(1)), match.group(2), int(match.group(3))
    operation = {
        '+': 'addition', '−': 'subtraction', '-': 'subtraction',
        '×': 'multiplication', 'x': 'multiplication',
        '÷': 'division', '/': 'division',
    }[operator]
    magnitude = max(left, right)
    if magnitude < 20:
        band = 'tiny'
    elif magnitude < 100:
        band = 'two_digit'
    elif magnitude < 1000:
        band = 'hundreds'
    else:
        band = 'thousands'
    return operation, band


def question_structure(question: legacy.Question) -> str:
    payload = _payload(question)
    reasoning = payload.get('reasoning_type')
    if reasoning:
        return f"reasoning:{reasoning}"
    direct = _direct_arithmetic_signature(question)
    if direct:
        return f"direct:{direct[0]}:{direct[1]}"
    return v0301.question_family(question)


def _purposeful_foundation(question: legacy.Question) -> bool:
    payload = _payload(question)
    return payload.get('learning_purpose') in {'review', 'consolidation'} or bool(payload.get('retrieval_item'))


def _is_low_complexity(question: legacy.Question) -> bool:
    direct = _direct_arithmetic_signature(question)
    return bool(direct and direct[1] in {'tiny', 'two_digit'} and not _purposeful_foundation(question))


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
        payload = _payload(question)
        payload['session_quality'] = {
            'structure': structure,
            'recent_exposure': int(recent.get(structure, 0)),
            'purposeful_foundation': _purposeful_foundation(question),
            'low_complexity': _is_low_complexity(question),
            'learner_ready': bool(readiness['ready']),
        }
        question.payload = json.dumps(payload)

    # Re-derive adaptive purpose after any replacement so recommendations and
    # evidence metadata remain aligned with the final question set.
    v0330.apply_adaptive_daily_learning(session, worksheet, student_id)
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
        'recent_structure_exposure': True,
        'near_duplicate_structure_control': True,
        'adaptive_metadata_reconciled_after_quality': True,
        'parent_test_isolation': True,
        'inherits_v0381': True,
    }


v0120._move_spa_fallback_to_end()
