from __future__ import annotations

import json
from collections import Counter
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0110, v0120, v0230

app = v0230.app
app.version = legacy.APP_VERSION


def _canonical_code(question: legacy.Question) -> str:
    return v0230.STORY_OUTCOME_ALIASES.get(question.skill.split(':', 1)[0], question.skill.split(':', 1)[0])


def _independent(question: legacy.Question) -> bool:
    attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
    return bool(attempts and attempts[0].correct and not (question.hint_count or 0))


def _supported(question: legacy.Question) -> bool:
    return any(attempt.correct for attempt in question.attempts)


def _accuracy(questions: list[legacy.Question], predicate) -> int | None:
    return round(sum(predicate(question) for question in questions) / len(questions) * 100) if questions else None


def _diagnostic_level(worksheet: legacy.Worksheet | None) -> int | None:
    if not worksheet or not worksheet.completed_at:
        return None
    secure = []
    for level in range(2, 7):
        questions = [question for question in worksheet.questions if question.level == level]
        if len(questions) == 3 and _accuracy(questions, _supported) >= 67:
            secure.append(level)
    return max(secure) if secure else None


def _estimated_levels(session: Session, sid: int) -> dict[str, Any]:
    diagnostics = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.session_kind == 'diagnostic',
        legacy.Worksheet.completed_at.is_not(None),
    ).order_by(legacy.Worksheet.completed_at.asc(), legacy.Worksheet.id.asc())).all())
    baseline = _diagnostic_level(diagnostics[0]) if diagnostics else None
    current = _diagnostic_level(diagnostics[-1]) if diagnostics else None
    return {
        'baseline': baseline,
        'current': current,
        'target': 5,
        'growth': current - baseline if current is not None and baseline is not None else None,
        'diagnostics_completed': len(diagnostics),
    }


def _outcome_growth(session: Session, sid: int, mastery: list[dict[str, Any]]) -> list[dict[str, Any]]:
    questions = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Question.answered_at.is_not(None),
    ).order_by(legacy.Question.answered_at.asc(), legacy.Question.id.asc())).all())
    grouped: dict[str, list[legacy.Question]] = {code: [] for code in legacy.LEVEL4_OUTCOMES}
    for question in questions:
        code = _canonical_code(question)
        if code in grouped:
            grouped[code].append(question)
    mastery_by_code = {item['code']: item for item in mastery}
    result = []
    for code, records in grouped.items():
        current = mastery_by_code[code]
        midpoint = len(records) // 2
        baseline_window = records[:min(5, midpoint)] if len(records) >= 6 else []
        current_window = records[-min(5, len(records) - midpoint):] if len(records) >= 6 else records[-5:]
        baseline_accuracy = _accuracy(baseline_window, _independent)
        current_accuracy = _accuracy(current_window, _independent)
        result.append({
            **current,
            'baseline_independent_accuracy': baseline_accuracy,
            'current_independent_accuracy': current_accuracy,
            'growth_points': current_accuracy - baseline_accuracy if baseline_accuracy is not None and current_accuracy is not None else None,
        })
    return result


def _period_summary(session: Session, sid: int, start: date, end: date) -> dict[str, Any]:
    worksheets = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.worksheet_date >= start,
        legacy.Worksheet.worksheet_date <= end,
    )).all())
    questions = [question for worksheet in worksheets for question in worksheet.questions if question.attempts or question.answered_at]
    first_seconds = [
        sorted(question.attempts, key=lambda item: item.attempt_number)[0].seconds
        for question in questions if question.attempts and sorted(question.attempts, key=lambda item: item.attempt_number)[0].seconds > 0
    ]
    return {
        'start': start.isoformat(),
        'end': end.isoformat(),
        'learning_days': len({worksheet.worksheet_date for worksheet in worksheets if worksheet.completed_at}),
        'activities_completed': sum(bool(worksheet.completed_at) for worksheet in worksheets),
        'questions': len(questions),
        'independent_accuracy': _accuracy(questions, _independent),
        'supported_accuracy': _accuracy(questions, _supported),
        'hints_used': sum(question.hint_count or 0 for question in questions),
        'average_seconds': round(sum(first_seconds) / len(first_seconds), 1) if first_seconds else None,
    }


def _strategies_used(session: Session, sid: int, start: date) -> list[dict[str, Any]]:
    questions = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.worksheet_date >= start,
        legacy.Question.answered_at.is_not(None),
    )).all())
    strategies = Counter()
    for question in questions:
        try:
            card = json.loads(question.payload or '{}').get('strategy_card') or {}
        except (TypeError, ValueError):
            card = {}
        title = card.get('title')
        if title:
            strategies[str(title)] += 1
    return [{'strategy': name, 'questions': count} for name, count in strategies.most_common(5)]


def parent_insight(session: Session, sid: int, today: date | None = None) -> dict[str, Any]:
    end = today or date.today()
    current_start = end - timedelta(days=6)
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=6)
    mastery = v0230.outcome_mastery(session, sid, datetime.combine(end, datetime.min.time()))
    outcomes = _outcome_growth(session, sid, mastery)
    recommendation = v0230.next_session_recommendation(session, sid, mastery)
    current_week = _period_summary(session, sid, current_start, end)
    previous_week = _period_summary(session, sid, previous_start, previous_end)
    gains = sorted(
        (item for item in outcomes if item['growth_points'] is not None and item['growth_points'] > 0),
        key=lambda item: (-item['growth_points'], item['code']),
    )[:5]
    gaps = sorted(
        (item for item in outcomes if item['status'] in ('needs_support', 'developing')),
        key=lambda item: (item['mastery'], item['code']),
    )[:5]
    if current_week['questions']:
        summary = (
            f"This week Sienna completed {current_week['questions']} questions across {current_week['learning_days']} learning days. "
            f"Independent accuracy was {current_week['independent_accuracy']}% and supported accuracy was {current_week['supported_accuracy']}%. "
            f"The recommended next step is {recommendation['title'].lower()} for {recommendation['minutes']} minutes."
        )
    else:
        summary = f"No completed question evidence is available this week. The recommended next step is {recommendation['title'].lower()} for {recommendation['minutes']} minutes."
    return {
        'estimated_level': _estimated_levels(session, sid),
        'outcomes': outcomes,
        'summary': {
            'mastered': sum(item['status'] == 'mastered' for item in outcomes),
            'secure': sum(item['status'] == 'secure' for item in outcomes),
            'developing': sum(item['status'] == 'developing' for item in outcomes),
            'needs_support': sum(item['status'] == 'needs_support' for item in outcomes),
            'review_due': sum(item['review_due'] for item in outcomes),
        },
        'weekly': {'current': current_week, 'previous': previous_week, 'narrative': summary},
        'gains': gains,
        'persistent_gaps': gaps,
        'strategies_used': _strategies_used(session, sid, current_start),
        'recommendation': recommendation,
    }


def _ha_learning_insight(session: Session, sid: int) -> dict[str, Any]:
    insight = parent_insight(session, sid)
    by_strand: dict[str, list[dict[str, Any]]] = {}
    for outcome in insight['outcomes']:
        by_strand.setdefault(outcome['topic'], []).append(outcome)
    categories = {}
    for topic in legacy.LEVEL4_STRANDS:
        records = by_strand.get(topic, [])
        assessed = [item for item in records if item['questions']]
        categories[topic] = {
            'outcomes': len(records),
            'assessed_outcomes': len(assessed),
            'mastery': round(sum(item['mastery'] for item in assessed) / len(assessed)) if assessed else None,
            'review_due': sum(item['review_due'] for item in records),
            'needs_support': sum(item['status'] == 'needs_support' for item in records),
        }
    return {
        'learning': {
            'estimated_level': insight['estimated_level'],
            'summary': insight['summary'],
            'recommendation': insight['recommendation'],
            'weekly': insight['weekly']['current'],
        },
        'outcomes': insight['outcomes'],
        'outcome_categories': categories,
    }


v0110._dashboard_insight_provider = _ha_learning_insight


@app.get('/api/learning/parent-insight-v0240')
def parent_learning_insight(_: legacy.User = Depends(legacy.parent), session: Session = Depends(legacy.db)):
    return parent_insight(session, v0120.resolve_learner(session).id)


@app.get('/api/ha/service-token')
def ha_service_token(_: legacy.User = Depends(legacy.parent)):
    return {
        'token': legacy.HA_SERVICE_TOKEN,
        'authorization_header': f'Bearer {legacy.HA_SERVICE_TOKEN}',
        'stats_endpoint': '/api/ha/stats',
        'summary_endpoint': '/api/ha/summary',
        'expires': None,
    }


@app.get('/api/v0240/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'parent_outcome_growth': True,
        'weekly_learning_summary': True,
        'independent_and_supported_accuracy': True,
        'fluency_retention_and_review_due': True,
        'home_assistant_outcome_metrics': True,
        'persistent_home_assistant_service_token': True,
        'inherits_v0230': True,
    }


v0120._move_spa_fallback_to_end()
