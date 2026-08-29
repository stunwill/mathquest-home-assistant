from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0110, v0120, v0240, v0290, v0320, v0330, v0340

app = v0340.app
app.version = '0.35.0'
legacy.APP_VERSION = '0.35.0'

ELIGIBLE_SESSION_KINDS = {'practice', 'adventure'}
ENTITY_IDS = {
    'daily': 'mathquest_daily_learning',
    'focus': 'mathquest_learning_focus',
    'review': 'mathquest_review_status',
    'support': 'mathquest_support_status',
    'weekly': 'mathquest_weekly_summary',
}


def _payload(question: legacy.Question) -> dict[str, Any]:
    try:
        value = json.loads(question.payload or '{}')
    except (TypeError, ValueError):
        value = {}
    return value if isinstance(value, dict) else {}


def _questions(worksheet: legacy.Worksheet) -> list[legacy.Question]:
    return [q for q in worksheet.questions if q.attempts or q.answered_at]


def _first_attempt_independent(question: legacy.Question) -> bool:
    attempts = sorted(question.attempts, key=lambda item: item.attempt_number)
    return bool(attempts and attempts[0].correct and not (question.hint_count or 0) and not question.mentor_started and not question.mentor_example_seen)


def _eventual_success(question: legacy.Question) -> bool:
    return any(attempt.correct for attempt in question.attempts)


def _daily_summary(session: Session, sid: int, today: date) -> dict[str, Any]:
    works = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.worksheet_date == today,
    ).order_by(legacy.Worksheet.started_at.asc(), legacy.Worksheet.id.asc())).all())
    learner_works = [w for w in works if w.session_kind in ELIGIBLE_SESSION_KINDS]
    answered = [q for w in learner_works for q in _questions(w)]
    completed = [w for w in learner_works if w.completed_at and _questions(w)]
    independent = sum(_first_attempt_independent(q) for q in answered)
    eventual = sum(_eventual_success(q) for q in answered)
    actual_seconds = sum(max(0.0, float(w.elapsed_seconds or 0.0)) for w in learner_works)
    planned_minutes = sum(int(w.target_minutes or 0) for w in completed if w.target_minutes)
    latest = max(learner_works, key=lambda w: (w.last_active_at or w.completed_at or w.started_at or datetime.min, w.id), default=None)
    session_label = None
    if latest:
        session_label = 'Story Adventure' if latest.session_kind == 'adventure' else 'Daily Practice'
    return {
        'state': 'Completed' if completed else ('In progress' if answered else 'Not completed'),
        'completed': bool(completed),
        'activities_completed': len(completed),
        'questions_attempted': len(answered),
        'independent_accuracy': round(independent / len(answered) * 100) if answered else None,
        'eventual_accuracy': round(eventual / len(answered) * 100) if answered else None,
        'active_minutes': round(actual_seconds / 60, 1) if actual_seconds else None,
        'planned_minutes_completed': planned_minutes or None,
        'latest_session_type': session_label,
        'latest_focus': latest.selected_topic if latest else None,
        'parent_tests_today': sum(w.session_kind == 'parent_test' for w in works),
    }


def _recent_learning_metadata(session: Session, sid: int, skill: str) -> dict[str, Any]:
    recent = session.scalar(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.session_kind != 'parent_test',
        legacy.Question.skill == skill,
    ).order_by(legacy.Question.id.desc()))
    if not recent:
        return {}
    payload = _payload(recent)
    adaptive = payload.get('adaptive') if isinstance(payload.get('adaptive'), dict) else {}
    adventure = payload.get('adventure') if isinstance(payload.get('adventure'), dict) else {}
    return {
        'learning_purpose': payload.get('learning_purpose'),
        'learning_purpose_label': payload.get('learning_purpose_label'),
        'adaptive_reason': payload.get('adaptive_reason'),
        'prerequisite_for': adaptive.get('prerequisite_for') or adventure.get('prerequisite_for'),
    }


def _purpose_for_skill(session: Session, sid: int, skill: str) -> tuple[str, str]:
    metadata = _recent_learning_metadata(session, sid, skill)
    purpose = metadata.get('learning_purpose')
    if purpose in v0330.PURPOSE_LABELS:
        return str(purpose), str(metadata.get('learning_purpose_label') or v0330.PURPOSE_LABELS[purpose])
    evidence = v0330._question_evidence(session, sid, skill)
    state = v0330._progression_state(evidence)
    if evidence['support'] >= v0330.THRESHOLDS.high_support or state in ('developing', 'consolidating'):
        return 'consolidation', v0330.PURPOSE_LABELS['consolidation']
    if state == 'ready_to_progress':
        return 'challenge', v0330.PURPOSE_LABELS['challenge']
    return 'current', v0330.PURPOSE_LABELS['current']


def _focus_summary(session: Session, sid: int, intelligence: dict[str, Any]) -> dict[str, Any]:
    recommendations = intelligence.get('recommendations') or []
    skills = intelligence.get('skills') or []
    rec = recommendations[0] if recommendations else None
    skill = None
    if rec and rec.get('skill'):
        skill = next((item for item in skills if item.get('skill') == rec.get('skill')), None)
    if skill is None:
        skill = next((item for item in skills if item.get('status') not in ('secure', 'not_enough_evidence')), None)
    if skill is None and skills:
        skill = skills[0]
    if not skill:
        return {
            'state': 'Building evidence', 'skill': None, 'skill_label': None, 'curriculum_area': None,
            'outcome': None, 'learning_purpose': None, 'learning_purpose_label': None, 'prerequisites': [],
            'prerequisite_for': None, 'recommendation': rec.get('title') if rec else 'Complete learner practice to build a recommendation.',
            'reason': rec.get('reason') if rec else 'MathQuest needs more learner evidence before identifying a priority.',
            'evidence_confidence': 'limited',
        }
    purpose, purpose_label = _purpose_for_skill(session, sid, str(skill['skill']))
    metadata = _recent_learning_metadata(session, sid, str(skill['skill']))
    outcome = str(skill['skill']).split(':', 1)[0] if ':' in str(skill['skill']) else None
    topic = legacy.LEVEL4_OUTCOMES.get(outcome, (None, None))[0] if outcome else None
    reason = rec.get('reason') if rec else None
    return {
        'state': skill.get('status', 'developing').replace('_', ' ').title(),
        'skill': skill.get('skill'),
        'skill_label': skill.get('label'),
        'curriculum_area': topic,
        'outcome': outcome,
        'learning_purpose': purpose,
        'learning_purpose_label': purpose_label,
        'prerequisites': skill.get('prerequisites') or [],
        'prerequisite_for': metadata.get('prerequisite_for'),
        'recommendation': rec.get('title') if rec else f"Keep going with {skill.get('label', 'current learning')}",
        'reason': reason or metadata.get('adaptive_reason') or 'MathQuest is using accumulated learner evidence to choose the next useful focus.',
        'evidence_confidence': skill.get('confidence', 'limited'),
    }


def _review_summary(intelligence: dict[str, Any]) -> dict[str, Any]:
    due = [item for item in intelligence.get('retention', []) if item.get('review_due')]
    if not due:
        return {'state': 'No review due', 'due': False, 'skill': None, 'skill_label': None, 'evidence_confidence': None, 'recommended_action': None}
    item = due[0]
    return {
        'state': 'Review due', 'due': True, 'skill': item.get('skill'), 'skill_label': item.get('label'),
        'evidence_confidence': item.get('confidence'), 'last_seen': item.get('last_seen'),
        'recommended_action': f"Quick review of {item.get('label', 'this skill')}",
    }


def _support_summary(intelligence: dict[str, Any]) -> dict[str, Any]:
    candidates = [item for item in intelligence.get('skills', []) if item.get('attempts', 0) >= 4 and item.get('support_dependency', 0) >= 60]
    if not candidates:
        return {'state': 'No persistent support need', 'needed': False, 'skill': None, 'skill_label': None, 'support_dependency': None, 'evidence_confidence': None}
    item = sorted(candidates, key=lambda x: (-x.get('support_dependency', 0), -x.get('attempts', 0)))[0]
    return {
        'state': 'Support needed', 'needed': True, 'skill': item.get('skill'), 'skill_label': item.get('label'),
        'support_dependency': item.get('support_dependency'), 'independent_accuracy': item.get('independent_accuracy'),
        'eventual_accuracy': item.get('eventual_accuracy'), 'evidence_confidence': item.get('confidence'),
        'recommended_action': f"Practise {item.get('label', 'this skill')} with a focus on independent attempts before using support.",
    }


def _misconception_summary(intelligence: dict[str, Any]) -> dict[str, Any]:
    items = intelligence.get('misconceptions') or []
    if not items:
        return {'state': 'No repeated misconception', 'active': False, 'skill': None, 'summary': None, 'evidence_strength': None}
    item = items[0]
    strength = 'strong' if item.get('count', 0) >= 4 else 'moderate'
    return {
        'state': 'Misconception detected', 'active': True, 'skill': item.get('skill'), 'skill_label': item.get('skill_label'),
        'summary': item.get('message'), 'evidence_strength': strength, 'occurrences': item.get('count'),
        'recommended_action': item.get('response'),
    }


def _progress_summary(intelligence: dict[str, Any]) -> dict[str, Any]:
    trend = intelligence.get('trend') or {}
    current = trend.get('current') or {}
    previous = trend.get('previous') or {}
    skills = intelligence.get('skills') or []
    secure = [item for item in skills if item.get('status') == 'secure' and item.get('confidence') in ('moderate', 'strong')]
    delta = None
    if current.get('first_attempt_accuracy') is not None and previous.get('first_attempt_accuracy') is not None:
        delta = current['first_attempt_accuracy'] - previous['first_attempt_accuracy']
    if secure:
        item = secure[0]
        return {'state': 'Meaningful progress', 'improved': True, 'reason': f"{item['label']} is secure with {item['confidence']} evidence.", 'skill': item['skill'], 'change_points': delta}
    if delta is not None and current.get('questions', 0) >= 6 and previous.get('questions', 0) >= 6 and delta >= 10:
        return {'state': 'Meaningful progress', 'improved': True, 'reason': f'Independent first-attempt accuracy improved by {delta} percentage points over the comparison period.', 'skill': None, 'change_points': delta}
    if delta is not None and current.get('questions', 0) >= 6 and previous.get('questions', 0) >= 6 and delta <= -15:
        return {'state': 'Needs attention', 'improved': False, 'reason': f'Independent first-attempt accuracy decreased by {abs(delta)} percentage points over the comparison period.', 'skill': None, 'change_points': delta}
    return {'state': 'Building evidence', 'improved': None, 'reason': 'No strong evidence of a meaningful change yet.', 'skill': None, 'change_points': delta}


def _weekly_summary(session: Session, sid: int, intelligence: dict[str, Any], today: date) -> dict[str, Any]:
    start = today - timedelta(days=6)
    works = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == sid,
        legacy.Worksheet.worksheet_date >= start,
        legacy.Worksheet.worksheet_date <= today,
        legacy.Worksheet.session_kind.in_(ELIGIBLE_SESSION_KINDS),
    )).all())
    completed = [w for w in works if w.completed_at and _questions(w)]
    active_minutes = sum(max(0.0, float(w.elapsed_seconds or 0.0)) for w in works) / 60
    skills = intelligence.get('skills') or []
    secure = [item['label'] for item in skills if item.get('status') == 'secure'][:3]
    needs = [item['label'] for item in skills if item.get('status') == 'needs_support'][:3]
    misconceptions = intelligence.get('misconceptions') or []
    recs = intelligence.get('recommendations') or []
    return {
        'state': 'Available' if completed else 'Building evidence',
        'period_start': start.isoformat(), 'period_end': today.isoformat(),
        'days_practised': len({w.worksheet_date for w in completed}),
        'activities_completed': len(completed),
        'active_minutes': round(active_minutes, 1) if active_minutes else None,
        'questions_attempted': sum(len(_questions(w)) for w in works),
        'skills_secure': secure,
        'skills_needing_support': needs,
        'review_due_count': sum(bool(item.get('review_due')) for item in intelligence.get('retention', [])),
        'recurring_misconceptions': [item.get('label') for item in misconceptions[:3]],
        'support_dependency': intelligence.get('difficulty', {}).get('support_dependency'),
        'recommended_focus': recs[0].get('title') if recs else None,
        'narrative': '; '.join(intelligence.get('summary') or ['Learning evidence is still building.']),
    }


def parent_ha_learning_state(session: Session, sid: int, today: date | None = None) -> dict[str, Any]:
    current_day = today or date.today()
    intelligence = _parent_intelligence(session, sid)
    daily = _daily_summary(session, sid, current_day)
    focus = _focus_summary(session, sid, intelligence)
    review = _review_summary(intelligence)
    support = _support_summary(intelligence)
    misconception = _misconception_summary(intelligence)
    progress = _progress_summary(intelligence)
    weekly = _weekly_summary(session, sid, intelligence, current_day)
    alerts = []
    for key, item in (('review_due', review), ('support_needed', support), ('misconception', misconception)):
        active = item.get('due') if key == 'review_due' else item.get('needed') if key == 'support_needed' else item.get('active')
        if active:
            alerts.append({'id': key, 'state': item['state'], 'skill': item.get('skill'), 'message': item.get('recommended_action') or item.get('summary')})
    if progress.get('state') in ('Meaningful progress', 'Needs attention'):
        alerts.append({'id': 'meaningful_progress' if progress.get('improved') else 'learning_change', 'state': progress['state'], 'skill': progress.get('skill'), 'message': progress.get('reason')})
    return {
        'version': '0.35.0',
        'available': True,
        'entity_model': {name: {'unique_id': uid} for name, uid in ENTITY_IDS.items()},
        'daily_learning': daily,
        'current_focus': focus,
        'review': review,
        'support': support,
        'misconception': misconception,
        'progress': progress,
        'weekly': weekly,
        'alerts': alerts,
        'privacy': {'local_first': True, 'external_telemetry': False},
    }


def _parent_intelligence(session: Session, sid: int) -> dict[str, Any]:
    skills = v0320._skill_evidence(session, sid)
    misconceptions = v0320._misconceptions(session, sid)
    recommendations = v0320._recommendations(skills, misconceptions)
    attempts = sum(item['attempts'] for item in skills)
    independent = sum(item['independent_accuracy'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    eventual = sum(item['eventual_accuracy'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    support = sum(item['support_dependency'] * item['attempts'] for item in skills) / attempts / 100 if attempts else 0.0
    return {
        'summary': v0320._summary(skills, recommendations),
        'skills': skills,
        'recommendations': recommendations,
        'misconceptions': misconceptions,
        'retention': [item for item in skills if item['review_due'] or item['status'] == 'secure'],
        'difficulty': {
            'state': v0320._difficulty_state(attempts, independent, eventual, support),
            'attempts': attempts,
            'independent_accuracy': round(independent * 100) if attempts else None,
            'eventual_accuracy': round(eventual * 100) if attempts else None,
            'support_dependency': round(support * 100) if attempts else None,
        },
        'trend': v0320._trend(session, sid, 30),
    }


def _ha_provider(session: Session, sid: int) -> dict[str, Any]:
    state = parent_ha_learning_state(session, sid)
    legacy_insight = v0240._ha_learning_insight(session, sid)
    return {
        **legacy_insight,
        'parent_learning': state,
    }


v0110._dashboard_insight_provider = _ha_provider


def _remove_route(path: str, method: str) -> None:
    app.router.routes[:] = [
        route for route in app.router.routes
        if not (getattr(route, 'path', None) == path and method in getattr(route, 'methods', set()))
    ]


_remove_route('/api/ha/service-token', 'GET')


@app.get('/api/ha/service-token')
def ha_service_token_v0350(_: legacy.User = Depends(legacy.parent)):
    return {
        'token': legacy.HA_SERVICE_TOKEN,
        'authorization_header': f'Bearer {legacy.HA_SERVICE_TOKEN}',
        'stats_endpoint': '/api/ha/stats',
        'summary_endpoint': '/api/ha/summary',
        'learning_endpoint': '/api/ha/learning',
        'weekly_summary_endpoint': '/api/ha/weekly-summary',
        'entity_unique_ids': ENTITY_IDS,
        'expires': None,
    }


@app.get('/api/ha/learning')
def ha_learning(user: legacy.User | None = Depends(v0110.ha_principal), session: Session = Depends(legacy.db)):
    try:
        return parent_ha_learning_state(session, v0110._student_id(user, session))
    except Exception:
        legacy.logger.exception('Home Assistant parent learning summary is temporarily unavailable')
        return {
            'version': '0.35.0', 'available': False, 'reason': 'learning_summary_unavailable',
            'daily_learning': {'state': 'Unavailable'}, 'current_focus': {'state': 'Unavailable'},
            'review': {'state': 'Unavailable'}, 'support': {'state': 'Unavailable'}, 'weekly': {'state': 'Unavailable'},
        }


@app.get('/api/ha/weekly-summary')
def ha_weekly_summary(user: legacy.User | None = Depends(v0110.ha_principal), session: Session = Depends(legacy.db)):
    state = parent_ha_learning_state(session, v0110._student_id(user, session))
    return state['weekly']


@app.get('/api/v0350/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.35.0',
        'home_assistant_parent_learning_summary': True,
        'stable_entity_contract': True,
        'daily_learning_completion': True,
        'story_adventure_learning_activity': True,
        'parent_test_isolation': True,
        'review_due_signal': True,
        'persistent_support_signal': True,
        'repeated_misconception_signal': True,
        'meaningful_progress_signal': True,
        'weekly_parent_summary': True,
        'notification_ready_alerts': True,
        'local_first': True,
        'inherits_v0340': True,
    }


v0120._move_spa_fallback_to_end()
