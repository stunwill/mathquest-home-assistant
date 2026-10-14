from __future__ import annotations

from contextvars import ContextVar
from typing import Any
from sqlalchemy.orm import Session

from . import main as legacy, v0120, v0290, v0310, v0321, v0323, v0330, v0440, v0490, grade5_arithmetic

app = v0490.app
app.version = '0.50.0'
legacy.APP_VERSION = '0.50.0'

_composing_targeted: ContextVar[bool] = ContextVar('v0500_composing_targeted', default=False)
_previous_create = legacy.create_worksheet
_previous_compose = v0440.compose_targeted_session


def create_worksheet(session: Session, student_id: int, selected: str, **kwargs: Any):
    worksheet = _previous_create(session,student_id,selected,**kwargs)
    return worksheet if _composing_targeted.get() else grade5_arithmetic.improve_worksheet(session,worksheet,student_id)


def compose_targeted_session(session: Session, student_id: int, plan: dict[str, Any], session_kind: str = 'practice'):
    token = _composing_targeted.set(True)
    try:
        worksheet = _previous_compose(session,student_id,plan,session_kind=session_kind)
    finally:
        _composing_targeted.reset(token)
    return grade5_arithmetic.improve_worksheet(session,worksheet,student_id,plan)


legacy.create_worksheet = create_worksheet
v0440.compose_targeted_session = compose_targeted_session

_previous_content = v0310.tutoring_content
_previous_hint = legacy.hint_text
_previous_example = v0290.aligned_worked_example
_previous_runtime_example = v0323.aligned_worked_example_v0323
_previous_public_example = v0321.aligned_worked_example


def tutoring_content(question):
    return v0330._payload(question).get('grade5_support') or _previous_content(question)


def hint_text(question, number):
    support = v0330._payload(question).get('grade5_support')
    return support['hints'][min(3,max(1,number))-1] if support else _previous_hint(question,number)


def worked_example(question):
    support = v0330._payload(question).get('grade5_support')
    return support['worked_example'] if support else _previous_example(question)


def runtime_worked_example(question):
    support = v0330._payload(question).get('grade5_support')
    return support['worked_example'] if support else _previous_runtime_example(question)


def public_worked_example(question):
    support = v0330._payload(question).get('grade5_support')
    return support['worked_example'] if support else _previous_public_example(question)


v0310.tutoring_content = tutoring_content
legacy.hint_text = hint_text
v0290.aligned_worked_example = worked_example
v0323.aligned_worked_example_v0323 = runtime_worked_example
v0321.aligned_worked_example = public_worked_example
v0120._move_spa_fallback_to_end()
