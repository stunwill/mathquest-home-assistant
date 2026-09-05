from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import Depends
from sqlalchemy.orm import Session

from . import main as legacy
from . import v0120, v0230, v0330, v0400

app = v0400.app
app.version = '0.41.0'
legacy.APP_VERSION = '0.41.0'


STATE_LABELS = {
    'not_enough_evidence': 'Not enough evidence yet',
    'practising': 'Practising',
    'building_confidence': 'Building confidence',
    'getting_stronger': 'Getting stronger',
    'ready_for_challenge': 'Ready for a challenge',
    'review_due': 'Review due',
}


def _skill_evidence(session: Session, student_id: int, outcome: dict[str, Any]) -> dict[str, Any]:
    skill = outcome.get('target_skill')
    if not skill:
        return {'questions': 0, 'independent': 0.0, 'eventual': 0.0, 'support': 0.0, 'recent_failures': 0}
    code = outcome.get('code')
    full_skill = f'{code}:{skill}' if code else skill
    evidence = v0330._question_evidence(session, student_id, full_skill)
    if not evidence.get('questions'):
        evidence = v0330._question_evidence(session, student_id, skill)
    return evidence


def student_learning_state(session: Session, student_id: int, outcome: dict[str, Any]) -> dict[str, Any]:
    evidence = _skill_evidence(session, student_id, outcome)
    progression = v0330._progression_state(evidence)
    questions = int(evidence.get('questions', 0) or 0)
    independent = float(evidence.get('independent', 0.0) or 0.0)
    eventual = float(evidence.get('eventual', 0.0) or 0.0)
    support = float(evidence.get('support', 0.0) or 0.0)

    if outcome.get('review_due') and outcome.get('questions', 0) >= 3:
        key = 'review_due'
        message = 'You have done this before. A quick review will help keep it fresh.'
    elif questions < v0330.THRESHOLDS.minimum_questions:
        key = 'not_enough_evidence'
        message = 'Keep practising so MathQuest can understand how this skill is going.'
    elif progression == 'ready_to_progress':
        key = 'ready_for_challenge'
        message = 'You have been solving these independently, so MathQuest can stretch you a little further.'
    elif progression == 'secure':
        key = 'getting_stronger'
        message = 'You are solving these independently more often.'
    elif eventual >= 0.72 and (support >= 0.35 or independent < v0330.THRESHOLDS.consolidate_accuracy):
        key = 'building_confidence'
        message = 'You can solve these with some help. We will keep practising them.'
    else:
        key = 'practising'
        message = 'MathQuest is keeping this in your practice so you can build a stronger method.'

    return {
        'key': key,
        'label': STATE_LABELS[key],
        'message': message,
        'target_skill': outcome.get('target_skill'),
        'evidence': {
            'questions': questions,
            'independent_accuracy': round(independent * 100),
            'eventual_accuracy': round(eventual * 100),
            'support_dependency': round(support * 100),
        },
    }


def student_recommendation_explanation(recommendation: dict[str, Any], outcomes: list[dict[str, Any]]) -> dict[str, str]:
    mode = recommendation.get('mode')
    if mode == 'diagnostic':
        return {'label': 'WHY THIS?', 'text': 'This short check helps MathQuest choose a useful starting point for your practice.'}
    by_code = {item.get('code'): item for item in outcomes}
    chosen = by_code.get(recommendation.get('outcome_code'))
    if recommendation.get('prerequisite_for'):
        return {'label': 'WHY THIS?', 'text': 'This skill supports the next maths idea MathQuest wants you to work on.'}
    if mode == 'review' or (chosen and chosen.get('review_due')):
        return {'label': 'QUICK REVIEW', 'text': 'You did this before. It is back today to help you remember it.'}
    if chosen and chosen.get('status') in ('secure', 'mastered'):
        return {'label': 'WHY THIS?', 'text': 'You have strong recent evidence here, so MathQuest can keep moving you forward carefully.'}
    return {'label': 'WHY THIS?', 'text': 'This is one of the most useful skills for you to practise next based on your recent work.'}


def student_progress_snapshot(session: Session, student_id: int) -> dict[str, Any]:
    outcomes = v0230.outcome_mastery(session, student_id)
    recommendation = v0230.next_session_recommendation(session, student_id, outcomes)
    rows = []
    for outcome in outcomes:
        state = student_learning_state(session, student_id, outcome)
        rows.append({
            'code': outcome['code'],
            'strand': outcome['strand'],
            'title': outcome['title'],
            'questions': outcome['questions'],
            'last_practised': outcome['last_practised'],
            'review_due': outcome['review_due'],
            'state': state,
        })
    priority = {
        'ready_for_challenge': 0,
        'getting_stronger': 1,
        'building_confidence': 2,
        'practising': 3,
        'review_due': 4,
        'not_enough_evidence': 5,
    }
    rows.sort(key=lambda item: (priority[item['state']['key']], item['title']))
    this_week = [item for item in rows if item['state']['key'] != 'not_enough_evidence'][:3]
    return {
        'generated_at': datetime.utcnow().isoformat(),
        'recommendation': recommendation,
        'recommendation_explanation': student_recommendation_explanation(recommendation, outcomes),
        'learning_now': rows,
        'this_week': this_week,
        'summary': {
            'getting_stronger': sum(item['state']['key'] in ('getting_stronger', 'ready_for_challenge') for item in rows),
            'building_confidence': sum(item['state']['key'] == 'building_confidence' for item in rows),
            'review_due': sum(item['state']['key'] == 'review_due' for item in rows),
        },
    }


@app.get('/api/learning/student-progress-v0410')
def student_progress(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    return student_progress_snapshot(session, student_id)


@app.get('/api/v0410/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': '0.41.0',
        'student_learning_states': True,
        'student_recommendation_explanations': True,
        'reuses_outcome_mastery': True,
        'reuses_adaptive_progression': True,
        'no_parallel_mastery_score': True,
        'inherits_v0400': True,
    }


v0120._move_spa_fallback_to_end()
