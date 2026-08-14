from __future__ import annotations

import json
import random
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0170, v0190, v0220, v090

app = v0220.app
app.version = legacy.APP_VERSION


PREREQUISITES = {
    'VC2M4A01': 'VC2M4N06',
    'VC2M4A02': 'VC2M4N06',
    'VC2M4N03': 'VC2M4A02',
    'VC2M4N04': 'VC2M4N03',
    'VC2M4M02': 'VC2M4N06',
    'VC2M4M03': 'VC2M4N06',
    'VC2M4ST01': 'VC2M4N02',
}

OUTCOME_TARGET_SKILLS = {
    'VC2M4N02': 'number_sequences',
    'VC2M4N03': 'equivalent_fractions',
    'VC2M4N04': 'fraction_number_line',
    'VC2M4N06': 'written_subtraction',
    'VC2M4A01': 'unknown_add_subtract',
    'VC2M4A02': 'fact_recall_multiplication',
    'VC2M4M02': 'area',
    'VC2M4M03': 'duration_conversion',
    'VC2M4SP03': 'grid_references',
    'VC2M4ST01': 'data_frequency',
}

STORY_OUTCOME_ALIASES = {
    'VC2M5N06': 'VC2M4N06',
    'VC2M5M02': 'VC2M4M02',
    'VC2M5M03': 'VC2M4M03',
    'VC2M5SP03': 'VC2M4SP03',
    'VC2M5ST01': 'VC2M4ST01',
}

STATUS_INTERVAL_DAYS = {
    'needs_support': 1,
    'developing': 3,
    'secure': 7,
    'mastered': 14,
}


def _outcome_code(question: legacy.Question) -> str:
    code = question.skill.split(':', 1)[0]
    return STORY_OUTCOME_ALIASES.get(code, code)


def _confidence_events(session: Session, student_id: int) -> dict[int, str]:
    rows = list(session.scalars(select(v090.ConfidenceEvent).where(
        v090.ConfidenceEvent.student_id == student_id
    ).order_by(v090.ConfidenceEvent.created_at.desc())).all())
    result: dict[int, str] = {}
    for event in rows:
        result.setdefault(event.question_id, event.confidence)
    return result


def _confidence_calibration(confidence: str, correct: bool) -> float:
    expected = {'guessed': .45, 'pretty_sure': .72, 'knew_it': 1.0}.get(confidence, .5)
    return max(0.0, 1.0 - abs(expected - float(correct)))


def _weighted_score(components: list[tuple[float, float]]) -> int:
    weight = sum(item[1] for item in components)
    return round(sum(value * item_weight for value, item_weight in components) / weight * 100) if weight else 0


def outcome_mastery(session: Session, student_id: int, now: datetime | None = None) -> list[dict[str, Any]]:
    current = now or datetime.utcnow()
    rows = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Question.answered_at.is_not(None),
    ).order_by(legacy.Question.answered_at.asc(), legacy.Question.id.asc())).all())
    confidence = _confidence_events(session, student_id)
    grouped: dict[str, list[legacy.Question]] = {code: [] for code in legacy.LEVEL4_OUTCOMES}
    for question in rows:
        code = _outcome_code(question)
        if code in grouped:
            grouped[code].append(question)

    results = []
    for code, (strand, title) in legacy.LEVEL4_OUTCOMES.items():
        questions = grouped[code][-20:]
        evidence = len(questions)
        supported_correct = 0
        independent_correct = 0
        first_attempt_seconds: list[float] = []
        fluent_independent = 0
        confidence_scores: list[float] = []
        skill_rows: dict[str, list[tuple[bool, bool]]] = {}

        for question in questions:
            attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
            first = attempts[0] if attempts else None
            supported = any(attempt.correct for attempt in attempts)
            independent = bool(first and first.correct and not (question.hint_count or 0))
            supported_correct += int(supported)
            independent_correct += int(independent)
            skill_name = question.skill.split(':', 1)[-1]
            skill_rows.setdefault(skill_name, []).append((supported, independent))
            if first and first.seconds > 0:
                first_attempt_seconds.append(first.seconds)
                fluent_independent += int(independent and first.seconds <= 45)
            if question.id in confidence:
                confidence_scores.append(_confidence_calibration(confidence[question.id], supported))

        retention_checks: list[bool] = []
        for previous, question in zip(questions, questions[1:]):
            if not previous.answered_at or not question.answered_at:
                continue
            if question.answered_at - previous.answered_at < timedelta(days=2):
                continue
            attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
            retention_checks.append(bool(attempts and attempts[0].correct and not (question.hint_count or 0)))

        independent_accuracy = independent_correct / evidence if evidence else 0.0
        supported_accuracy = supported_correct / evidence if evidence else 0.0
        fluency = fluent_independent / len(first_attempt_seconds) if first_attempt_seconds else None
        calibration = sum(confidence_scores) / len(confidence_scores) if confidence_scores else None
        retention = sum(retention_checks) / len(retention_checks) if retention_checks else None
        components = [(independent_accuracy, .45), (supported_accuracy, .15)] if evidence else []
        if fluency is not None:
            components.append((fluency, .15))
        if calibration is not None:
            components.append((calibration, .10))
        if retention is not None:
            components.append((retention, .15))
        mastery = _weighted_score(components)
        if evidence < 3:
            status = 'not_assessed'
        elif mastery >= 85 and retention_checks:
            status = 'mastered'
        elif mastery >= 75:
            status = 'secure'
        elif mastery >= 55:
            status = 'developing'
        else:
            status = 'needs_support'
        last_practised = questions[-1].answered_at if questions else None
        interval = STATUS_INTERVAL_DAYS.get(status, 0)
        next_due = (last_practised.date() + timedelta(days=interval)) if last_practised else current.date()
        review_due = bool(evidence and next_due <= current.date())

        skill_breakdown = []
        for skill_name, values in skill_rows.items():
            skill_breakdown.append({
                'skill': skill_name,
                'questions': len(values),
                'independent_accuracy': round(sum(independent for _, independent in values) / len(values) * 100),
                'supported_accuracy': round(sum(supported for supported, _ in values) / len(values) * 100),
            })
        skill_breakdown.sort(key=lambda item: (item['independent_accuracy'], item['skill']))
        target_skill = skill_breakdown[0]['skill'] if skill_breakdown else OUTCOME_TARGET_SKILLS.get(code)
        results.append({
            'code': code, 'strand': strand, 'topic': strand.lower(), 'title': title,
            'mastery': mastery, 'status': status, 'questions': evidence,
            'independent_accuracy': round(independent_accuracy * 100) if evidence else None,
            'supported_accuracy': round(supported_accuracy * 100) if evidence else None,
            'hint_rate': round(sum(1 for question in questions if question.hint_count) / evidence * 100) if evidence else None,
            'average_seconds': round(sum(first_attempt_seconds) / len(first_attempt_seconds), 1) if first_attempt_seconds else None,
            'fluency': round(fluency * 100) if fluency is not None else None,
            'confidence_calibration': round(calibration * 100) if calibration is not None else None,
            'retention_accuracy': round(retention * 100) if retention is not None else None,
            'retention_checks': len(retention_checks),
            'last_practised': last_practised.isoformat() if last_practised else None,
            'next_review_due': next_due.isoformat(), 'review_due': review_due,
            'target_skill': target_skill, 'skills': skill_breakdown,
        })
    return results


def _diagnostic_complete(session: Session, student_id: int) -> bool:
    worksheet = session.scalar(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == student_id,
        legacy.Worksheet.session_kind == 'diagnostic',
        legacy.Worksheet.completed_at.is_not(None),
    ).order_by(legacy.Worksheet.completed_at.desc()))
    return bool(worksheet)


def next_session_recommendation(session: Session, student_id: int,
                                outcomes: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    records = outcomes or outcome_mastery(session, student_id)
    if not _diagnostic_complete(session, student_id):
        return {
            'mode': 'diagnostic', 'minutes': 15, 'topic': 'number_algebra', 'outcome_code': None,
            'target_skill': None, 'title': 'Find the best starting point',
            'reason': 'Complete the Levels 2–6 diagnostic so MathQuest can recommend the right prerequisite and practice level.',
            'prerequisite_for': None,
        }

    by_code = {item['code']: item for item in records}
    due = sorted((item for item in records if item['review_due']), key=lambda item: (item['mastery'], item['code']))
    assessed = sorted((item for item in records if item['questions'] and item['status'] != 'mastered'), key=lambda item: (item['mastery'], item['code']))
    target = (due or assessed or [by_code['VC2M4N06']])[0]
    prerequisite_for = None
    chosen = target
    prerequisite_code = PREREQUISITES.get(target['code'])
    if target['mastery'] < 60 and prerequisite_code:
        prerequisite = by_code[prerequisite_code]
        if prerequisite['status'] not in ('secure', 'mastered'):
            chosen = prerequisite
            prerequisite_for = target['code']

    if prerequisite_for:
        mode = 'guided'
        reason = f"Build {chosen['title'].lower()} first because it supports {target['title'].lower()}."
    elif chosen['review_due']:
        mode = 'review'
        reason = f"This skill is due for retrieval practice. The last evidence gave {chosen['mastery']}% mastery."
    else:
        mode = 'practice'
        reason = f"This is the most useful current growth area, with {chosen['mastery']}% mastery from {chosen['questions']} recent questions."
    minutes = 15 if prerequisite_for or chosen['mastery'] < 55 or len(due) >= 3 else 10 if chosen['mastery'] < 75 or len(due) > 1 else 5
    return {
        'mode': mode, 'minutes': minutes, 'topic': chosen['topic'],
        'outcome_code': chosen['code'], 'target_skill': chosen['target_skill'],
        'title': f"{mode.title()} {chosen['title']}", 'reason': reason,
        'prerequisite_for': prerequisite_for,
    }


def adaptive_snapshot(session: Session, student_id: int) -> dict[str, Any]:
    outcomes = outcome_mastery(session, student_id)
    due = [item for item in outcomes if item['review_due']]
    return {
        'target_level': 5,
        'outcomes': outcomes,
        'review_due': due,
        'summary': {
            'mastered': sum(item['status'] == 'mastered' for item in outcomes),
            'secure': sum(item['status'] == 'secure' for item in outcomes),
            'developing': sum(item['status'] == 'developing' for item in outcomes),
            'needs_support': sum(item['status'] == 'needs_support' for item in outcomes),
            'review_due': len(due),
        },
        'recommendation': next_session_recommendation(session, student_id, outcomes),
    }


@app.get('/api/learning/adaptive-v0230')
def adaptive_learning(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return adaptive_snapshot(session, student_id)


@app.post('/api/sessions/recommended')
def recommended_session(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    recommendation = next_session_recommendation(session, user.id)
    if recommendation['mode'] == 'diagnostic':
        return v0190.new_session(v0190.SessionCreateIn(kind='diagnostic', minutes=15, topic='number_algebra'), user, session)

    minutes = recommendation['minutes']
    count = {5: 6, 10: 12, 15: 18}[minutes]
    worksheet = legacy.create_worksheet(
        session, user.id, recommendation['topic'], question_count=count,
        session_kind=recommendation['mode'], target_minutes=minutes,
    )
    generator = v0170.FOCUS_GENERATORS.get(recommendation['topic'], {}).get(recommendation['target_skill'])
    if generator:
        targeted = max(3, round(count * .65))
        questions = sorted(worksheet.questions, key=lambda item: item.position)
        seen = {
            legacy.question_identity(question.prompt, json.loads(question.payload or '{}'))
            for question in questions[targeted:]
        }
        for index, question in enumerate(questions[:targeted]):
            candidate = None
            for attempt in range(50):
                generated = generator(random.Random(f'adaptive:{worksheet.id}:{index}:{attempt}'))
                key = legacy.question_identity(generated[1], generated[3])
                if key not in seen:
                    candidate = generated
                    seen.add(key)
                    break
            if candidate is None:
                seen.add(legacy.question_identity(question.prompt, json.loads(question.payload or '{}')))
                continue
            skill, prompt, answer_type, payload, answer, working = candidate
            payload['adaptive'] = {
                'mode': recommendation['mode'], 'outcome_code': recommendation['outcome_code'],
                'prerequisite_for': recommendation['prerequisite_for'],
            }
            question.skill, question.prompt, question.answer_type = skill, prompt, answer_type
            question.payload, question.correct_answer, question.working = json.dumps(payload), str(answer), working
        session.commit()
        session.refresh(worksheet)
    result = legacy.worksheet_view(worksheet)
    result['recommendation'] = recommendation
    return result


@app.get('/api/v0230/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'outcome_mastery': True,
        'signals': ['independent_accuracy', 'supported_accuracy', 'hint_use', 'fluency', 'confidence', 'retention'],
        'spaced_review_due_dates': True,
        'prerequisite_routing': True,
        'recommended_sessions': [5, 10, 15],
        'inherits_v0220': True,
    }


v0120._move_spa_fallback_to_end()
