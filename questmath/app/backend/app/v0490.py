from __future__ import annotations

from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import main as legacy, v0120, v0230, v0410, v0440, v0450, v0460, v0480

app = v0480.app
app.version = '0.49.0'
legacy.APP_VERSION = '0.49.0'

_previous_summary = legacy.summary


def summary(session: Session, worksheet: legacy.Worksheet, user: legacy.User):
    # Persist at completion, even if the learner never opens the completion insight.
    if worksheet.completed_at and worksheet.session_kind != 'parent_test' and any(
        v0450._payload(q).get('targeted_session_plan') for q in worksheet.questions
    ):
        v0460._detail(session, worksheet, worksheet.student_id)
    return _previous_summary(session, worksheet, user)


legacy.summary = summary

app.router.routes[:] = [route for route in app.router.routes if not (
    getattr(route, 'path', None) == '/api/sessions/recommended' and 'POST' in getattr(route, 'methods', set())
)]


@app.post('/api/sessions/recommended')
def recommended_session(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    if user.role != 'student':
        raise HTTPException(403, 'Student access required')
    active = session.scalar(select(legacy.Worksheet).join(
        v0460.FollowThroughOutcome, v0460.FollowThroughOutcome.worksheet_id == legacy.Worksheet.id
    ).where(legacy.Worksheet.student_id == user.id, legacy.Worksheet.completed_at.is_(None))
        .order_by(legacy.Worksheet.id.desc()))
    if active:
        return legacy.worksheet_view(active)
    return v0440.recommended_targeted_session(user, session)


v0120._move_spa_fallback_to_end()

# Both Best Next Step and Today's Focus must describe the session the start action creates.
v0410._remove_route('/api/learning/adaptive-v0230', 'GET')


@app.get('/api/learning/adaptive-v0230')
def adaptive_learning(user: legacy.User = Depends(legacy.current_user), session: Session = Depends(legacy.db)):
    student_id = user.id if user.role == 'student' else v0120.resolve_learner(session).id
    snapshot = v0230.adaptive_snapshot(session, student_id)
    plan = v0460.build_learning_plan(session, student_id)
    explanation = v0410.student_recommendation_explanation(plan['recommendation'], snapshot['outcomes'])
    reason = plan['student_reason'] if plan.get('follow_through') or user.role != 'student' else explanation['text']
    snapshot['recommendation'] = {**plan['recommendation'], 'reason': reason,
                                  'why_label': explanation['label']}
    return snapshot


v0120._move_spa_fallback_to_end()
