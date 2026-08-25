from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0290, v0310

app = v0310.app
app.version = '0.32.0'
legacy.APP_VERSION = '0.32.0'

SKILL_LABELS = {
    'efficient_add_subtract': 'Efficient addition and subtraction',
    'written_addition': 'Addition with regrouping',
    'written_subtraction': 'Subtraction with decomposition',
    'multiplication_facts': 'Multiplication facts',
    'division_facts': 'Division facts',
    'equivalent_fractions': 'Equivalent fractions',
    'fraction_number_line': 'Fractions on a number line',
    'fraction_understanding': 'Fraction understanding',
    'money_change': 'Money and change',
    'perimeter': 'Perimeter',
    'area': 'Area',
}


def _label(skill: str) -> str:
    key = (skill or '').split(':', 1)[-1]
    return SKILL_LABELS.get(key, key.replace('_', ' ').strip().title() or 'Unknown skill')


def _detail(row: v0290.LearningEvidence) -> dict[str, Any]:
    try:
        value = json.loads(row.detail or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _evidence_confidence(attempts: int) -> str:
    if attempts < 4:
        return 'limited'
    if attempts < 10:
        return 'moderate'
    return 'strong'


def _status(attempts: int, independent_rate: float, eventual_rate: float, support_rate: float, review_due: bool) -> str:
    if attempts < 4:
        return 'not_enough_evidence'
    if review_due and independent_rate >= 0.75:
        return 'review_due'
    if independent_rate >= 0.8 and eventual_rate >= 0.85 and support_rate <= 0.25:
        return 'secure'
    if independent_rate < 0.5 or support_rate >= 0.6:
        return 'needs_support'
    return 'developing'


def _difficulty_state(attempts: int, independent_rate: float, eventual_rate: float, support_rate: float) -> str:
    if attempts < 6:
        return 'not_enough_evidence'
    if independent_rate >= 0.88 and support_rate <= 0.15:
        return 'ready_for_more_challenge'
    if eventual_rate >= 0.7 and independent_rate >= 0.55 and support_rate <= 0.45:
        return 'at_instructional_level'
    if eventual_rate >= 0.7:
        return 'building_confidence'
    return 'needs_consolidation'


def _attempt_rows(session: Session, student_id: int, since: datetime | None = None) -> list[legacy.Attempt]:
    statement = select(legacy.Attempt).where(legacy.Attempt.student_id == student_id).order_by(legacy.Attempt.id.asc())
    rows = list(session.scalars(statement).all())
    if since is None:
        return rows
    result: list[legacy.Attempt] = []
    for row in rows:
        question = session.get(legacy.Question, row.question_id)
        worksheet = session.get(legacy.Worksheet, question.worksheet_id) if question else None
        stamp = getattr(question, 'answered_at', None) or getattr(worksheet, 'last_active_at', None) or getattr(worksheet, 'created_at', None)
        if stamp and stamp >= since:
            result.append(row)
    return result


def _skill_evidence(session: Session, student_id: int) -> list[dict[str, Any]]:
    attempts = _attempt_rows(session, student_id)
    grouped: dict[str, list[legacy.Attempt]] = defaultdict(list)
    question_map: dict[int, legacy.Question] = {}
    for attempt in attempts:
        question = session.get(legacy.Question, attempt.question_id)
        if not question:
            continue
        worksheet = session.get(legacy.Worksheet, question.worksheet_id)
        if worksheet and worksheet.session_kind == 'parent_test':
            continue
        question_map[question.id] = question
        grouped[question.skill].append(attempt)

    evidence = session.scalars(select(v0290.LearningEvidence).where(v0290.LearningEvidence.student_id == student_id)).all()
    evidence_by_question: dict[int, list[v0290.LearningEvidence]] = defaultdict(list)
    for row in evidence:
        evidence_by_question[row.question_id].append(row)

    misconception_rows = session.scalars(select(v0290.MisconceptionEvidence).where(v0290.MisconceptionEvidence.student_id == student_id, v0290.MisconceptionEvidence.resolved == False)).all()
    misconception_counts: dict[str, int] = defaultdict(int)
    for row in misconception_rows:
        misconception_counts[row.skill] += 1

    now = datetime.utcnow()
    results: list[dict[str, Any]] = []
    for skill, rows in grouped.items():
        per_question: dict[int, list[legacy.Attempt]] = defaultdict(list)
        for row in rows:
            per_question[row.question_id].append(row)
        first_attempts = []
        eventual = []
        supported = []
        last_seen: datetime | None = None
        for question_id, question_attempts in per_question.items():
            question_attempts.sort(key=lambda item: item.attempt_number)
            first = question_attempts[0]
            first_attempts.append(bool(first.correct))
            eventual.append(any(item.correct for item in question_attempts))
            q_evidence = evidence_by_question.get(question_id, [])
            help_used = any((_detail(item).get('hints_used', 0) or 0) > 0 or _detail(item).get('worked_example_seen') for item in q_evidence)
            question = question_map.get(question_id)
            if question:
                help_used = help_used or bool((question.hint_count or 0) > 0 or question.mentor_example_seen or question.mentor_started)
                last_seen = max(filter(None, [last_seen, getattr(question, 'answered_at', None)]), default=last_seen)
            supported.append(bool(help_used))
        count = len(per_question)
        independent_rate = sum(first_attempts) / count if count else 0.0
        eventual_rate = sum(eventual) / count if count else 0.0
        support_rate = sum(supported) / count if count else 0.0
        days_since = (now - last_seen).days if last_seen else None
        review_due = bool(count >= 4 and independent_rate >= 0.75 and days_since is not None and days_since >= 7)
        key = skill.split(':', 1)[-1]
        prerequisites = list(v0290.GRAPH.get(key, []))
        results.append({
            'skill': skill,
            'label': _label(skill),
            'attempts': count,
            'first_attempt_accuracy': round(independent_rate * 100),
            'eventual_accuracy': round(eventual_rate * 100),
            'independent_accuracy': round(independent_rate * 100),
            'supported_rate': round(support_rate * 100),
            'support_dependency': round(support_rate * 100),
            'status': _status(count, independent_rate, eventual_rate, support_rate, review_due),
            'confidence': _evidence_confidence(count),
            'review_due': review_due,
            'last_seen': last_seen.isoformat() if last_seen else None,
            'misconception_count': misconception_counts.get(skill, 0),
            'prerequisites': prerequisites,
        })
    return sorted(results, key=lambda item: (item['status'] == 'not_enough_evidence', item['label']))


def _misconceptions(session: Session, student_id: int) -> list[dict[str, Any]]:
    rows = session.scalars(select(v0290.MisconceptionEvidence).where(v0290.MisconceptionEvidence.student_id == student_id, v0290.MisconceptionEvidence.resolved == False).order_by(v0290.MisconceptionEvidence.created_at.desc())).all()
    grouped: dict[tuple[str, str], list[v0290.MisconceptionEvidence]] = defaultdict(list)
    for row in rows:
        grouped[(row.skill, row.misconception_type)].append(row)
    output = []
    for (skill, kind), values in grouped.items():
        if len(values) < 2:
            continue
        output.append({
            'skill': skill,
            'skill_label': _label(skill),
            'type': kind,
            'label': kind.replace('_', ' ').title(),
            'count': len(values),
            'last_seen': values[0].created_at.isoformat(),
            'message': values[0].message,
            'response': f'MathQuest will prioritise {_label(skill).lower()} practice and revisit relevant prerequisites.',
        })
    return sorted(output, key=lambda item: (-item['count'], item['label']))


def _recommendations(skills: list[dict[str, Any]], misconceptions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    recs: list[dict[str, Any]] = []
    for misconception in misconceptions[:2]:
        recs.append({
            'priority': 'high_priority',
            'title': f"Review {misconception['skill_label']}",
            'reason': f"The {misconception['label'].lower()} pattern has appeared {misconception['count']} times.",
            'skill': misconception['skill'],
        })
    for item in skills:
        if len(recs) >= 5:
            break
        if item['status'] == 'review_due':
            recs.append({'priority': 'review', 'title': f"Review {item['label']}", 'reason': 'This previously strong skill is due for a quick spaced-retrieval check.', 'skill': item['skill']})
        elif item['status'] == 'needs_support':
            reason = f"First-attempt accuracy is {item['first_attempt_accuracy']}% and support is used on {item['support_dependency']}% of recent questions."
            recs.append({'priority': 'practise', 'title': f"Practise {item['label']}", 'reason': reason, 'skill': item['skill']})
    if not recs:
        developing = next((item for item in skills if item['status'] == 'developing'), None)
        if developing:
            recs.append({'priority': 'keep_going', 'title': f"Keep going with {developing['label']}", 'reason': 'Recent evidence is developing appropriately and more independent practice will strengthen confidence.', 'skill': developing['skill']})
    return recs[:5]


def _summary(skills: list[dict[str, Any]], recommendations: list[dict[str, Any]]) -> list[str]:
    if not skills:
        return ['Not enough recent evidence yet. Complete a few learner worksheets to build a reliable picture.']
    secure = [item for item in skills if item['status'] == 'secure']
    support = [item for item in skills if item['status'] == 'needs_support']
    developing = [item for item in skills if item['status'] == 'developing']
    lines: list[str] = []
    if secure:
        lines.append(f"{secure[0]['label']} is currently secure based on mostly independent recent evidence.")
    elif developing:
        lines.append(f"{developing[0]['label']} is developing and benefits from continued practice.")
    if support:
        lines.append(f"{support[0]['label']} needs support, with help still used on {support[0]['support_dependency']}% of recent questions.")
    if recommendations:
        lines.append(f"Next priority: {recommendations[0]['title']}.")
    return lines or ['Recent evidence is still building. MathQuest will avoid strong conclusions until more attempts are available.']


def _trend(session: Session, student_id: int, days: int) -> dict[str, Any]:
    now = datetime.utcnow()
    current = _attempt_rows(session, student_id, now - timedelta(days=days))
    previous = _attempt_rows(session, student_id, now - timedelta(days=days * 2))
    previous = [row for row in previous if row not in current]

    def stats(rows: list[legacy.Attempt]) -> dict[str, Any]:
        by_question: dict[int, list[legacy.Attempt]] = defaultdict(list)
        for row in rows:
            question = session.get(legacy.Question, row.question_id)
            worksheet = session.get(legacy.Worksheet, question.worksheet_id) if question else None
            if worksheet and worksheet.session_kind == 'parent_test':
                continue
            by_question[row.question_id].append(row)
        first = []
        eventual = []
        for values in by_question.values():
            values.sort(key=lambda item: item.attempt_number)
            first.append(bool(values[0].correct))
            eventual.append(any(item.correct for item in values))
        count = len(by_question)
        return {
            'questions': count,
            'first_attempt_accuracy': round(sum(first) / count * 100) if count else None,
            'eventual_accuracy': round(sum(eventual) / count * 100) if count else None,
        }

    return {'days': days, 'current': stats(current), 'previous': stats(previous)}


@app.get('/api/learning/parent-intelligence-v0320')
def parent_intelligence_v0320(
    days: int = Query(30, ge=7, le=3650),
    _: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    try:
        student = v0120.resolve_learner(session)
    except HTTPException:
        return {'version': '0.32.0', 'summary': ['No learner profile is available yet.'], 'skills': [], 'recommendations': [], 'misconceptions': [], 'difficulty': {'state': 'not_enough_evidence'}, 'trend': {'days': days, 'current': {}, 'previous': {}}, 'retention': []}
    skills = _skill_evidence(session, student.id)
    misconceptions = _misconceptions(session, student.id)
    recommendations = _recommendations(skills, misconceptions)
    attempts = sum(item['attempts'] for item in skills)
    independent = sum(item['independent_accuracy'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    eventual = sum(item['eventual_accuracy'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    support = sum(item['support_dependency'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    return {
        'version': '0.32.0',
        'learner': {'id': student.id, 'display_name': student.display_name},
        'summary': _summary(skills, recommendations),
        'skills': skills,
        'recommendations': recommendations,
        'misconceptions': misconceptions,
        'retention': [item for item in skills if item['review_due'] or item['status'] == 'secure'],
        'difficulty': {
            'state': _difficulty_state(attempts, independent, eventual, support),
            'attempts': attempts,
            'independent_accuracy': round(independent * 100) if attempts else None,
            'eventual_accuracy': round(eventual * 100) if attempts else None,
            'support_dependency': round(support * 100) if attempts else None,
        },
        'trend': _trend(session, student.id, days),
    }


@app.get('/api/v0320/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.32.0',
        'parent_learning_intelligence': True,
        'independent_supported_mastery': True,
        'evidence_confidence': True,
        'prioritised_recommendations': True,
        'misconception_intelligence': True,
        'retention_visibility': True,
        'difficulty_calibration': True,
    }
