from __future__ import annotations

import re
from datetime import datetime
from typing import Literal

from fastapi import Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import main as legacy
from . import v0120, v0240

app = v0240.app
app.version = legacy.APP_VERSION


class TestFeedback(legacy.Base):
    __tablename__ = 'test_feedback'

    id: Mapped[int] = mapped_column(primary_key=True)
    worksheet_id: Mapped[int] = mapped_column(ForeignKey('worksheets.id'), index=True)
    question_id: Mapped[int | None] = mapped_column(ForeignKey('questions.id'), nullable=True, index=True)
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    feedback_type: Mapped[str] = mapped_column(String(20), default='note')
    note: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default='open', index=True)
    addressed_release: Mapped[str | None] = mapped_column(String(30), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TestWorksheetIn(BaseModel):
    topic: str = 'mixed'
    question_count: int = Field(default=10, ge=5, le=50)


class FeedbackIn(BaseModel):
    question_id: int | None = None
    feedback_type: Literal['bug', 'enhancement', 'note'] = 'note'
    note: str = Field(min_length=1, max_length=4000)


class FeedbackUpdateIn(BaseModel):
    feedback_type: Literal['bug', 'enhancement', 'note']
    note: str = Field(min_length=1, max_length=4000)
    status: Literal['open', 'planned', 'addressed', 'deferred']
    addressed_release: str | None = Field(default=None, max_length=30)


@app.on_event('startup')
def create_v0250_tables():
    legacy.Base.metadata.create_all(legacy.engine)


def _test_worksheet(session: Session, worksheet_id: int, parent: legacy.User) -> legacy.Worksheet:
    worksheet = session.get(legacy.Worksheet, worksheet_id)
    if not worksheet or worksheet.student_id != parent.id or worksheet.session_kind != 'parent_test':
        raise HTTPException(404, 'Test worksheet not found')
    return worksheet


def _feedback_view(item: TestFeedback, session: Session) -> dict:
    question = session.get(legacy.Question, item.question_id) if item.question_id else None
    return {
        'id': item.id,
        'worksheet_id': item.worksheet_id,
        'question_id': item.question_id,
        'question_position': question.position + 1 if question else None,
        'question_prompt': question.prompt if question else None,
        'feedback_type': item.feedback_type,
        'note': item.note,
        'status': item.status,
        'addressed_release': item.addressed_release,
        'created_at': item.created_at.isoformat(),
        'updated_at': item.updated_at.isoformat(),
    }


def _test_view(worksheet: legacy.Worksheet, session: Session, include_questions: bool = False) -> dict:
    feedback = list(session.scalars(select(TestFeedback).where(
        TestFeedback.worksheet_id == worksheet.id,
    ).order_by(TestFeedback.created_at.asc(), TestFeedback.id.asc())).all())
    base = legacy.worksheet_view(worksheet)
    item = {
        'id': worksheet.id,
        'date': worksheet.worksheet_date.isoformat(),
        'started_at': worksheet.started_at.isoformat(),
        'completed_at': worksheet.completed_at.isoformat() if worksheet.completed_at else None,
        'selected_topic': worksheet.selected_topic,
        'status': worksheet.status,
        'score': worksheet.score,
        'total': worksheet.total,
        'answered': base['counts']['correct'] + base['counts']['incorrect'],
        'skipped': base['counts']['skipped'],
        'feedback_count': len(feedback),
        'open_feedback': sum(entry.status in ('open', 'planned') for entry in feedback),
        'addressed_feedback': sum(entry.status == 'addressed' for entry in feedback),
        'addressed_releases': sorted({entry.addressed_release for entry in feedback if entry.addressed_release}),
        'feedback': [_feedback_view(entry, session) for entry in feedback],
    }
    if include_questions:
        item['worksheet'] = base
        item['questions'] = [{
            **question,
            'correct_answer': source.correct_answer,
            'working': source.working,
            'feedback': [_feedback_view(entry, session) for entry in feedback if entry.question_id == source.id],
        } for question, source in zip(base['questions'], sorted(worksheet.questions, key=lambda value: value.position))]
        item['overall_feedback'] = [_feedback_view(entry, session) for entry in feedback if entry.question_id is None]
    return item


@app.post('/api/testing/worksheets')
def create_test_worksheet(
    payload: TestWorksheetIn,
    parent: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    learner = v0120.resolve_learner(session)
    worksheet = legacy.create_worksheet(
        session,
        parent.id,
        payload.topic,
        question_count=payload.question_count,
        session_kind='parent_test',
        learning_profile_id=learner.id,
    )
    return legacy.worksheet_view(worksheet)


@app.get('/api/testing/worksheets')
def list_test_worksheets(
    parent: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    worksheets = list(session.scalars(select(legacy.Worksheet).where(
        legacy.Worksheet.student_id == parent.id,
        legacy.Worksheet.session_kind == 'parent_test',
    ).order_by(legacy.Worksheet.started_at.desc(), legacy.Worksheet.id.desc())).all())
    return [_test_view(worksheet, session) for worksheet in worksheets]


@app.get('/api/testing/worksheets/{worksheet_id}')
def get_test_worksheet(
    worksheet_id: int,
    parent: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    return _test_view(_test_worksheet(session, worksheet_id, parent), session, include_questions=True)


@app.post('/api/testing/worksheets/{worksheet_id}/feedback')
def add_test_feedback(
    worksheet_id: int,
    payload: FeedbackIn,
    parent: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    worksheet = _test_worksheet(session, worksheet_id, parent)
    if payload.question_id is not None:
        question = session.get(legacy.Question, payload.question_id)
        if not question or question.worksheet_id != worksheet.id:
            raise HTTPException(400, 'Question does not belong to this test worksheet')
        if legacy.question_status(question) not in ('correct', 'incorrect'):
            raise HTTPException(409, 'Complete the question before adding its test note')
    elif not worksheet.completed_at:
        raise HTTPException(409, 'Complete the test worksheet before adding an overall note')
    item = TestFeedback(
        worksheet_id=worksheet.id,
        question_id=payload.question_id,
        author_id=parent.id,
        feedback_type=payload.feedback_type,
        note=payload.note.strip(),
    )
    session.add(item)
    session.commit()
    session.refresh(item)
    return _feedback_view(item, session)


@app.put('/api/testing/feedback/{feedback_id}')
def update_test_feedback(
    feedback_id: int,
    payload: FeedbackUpdateIn,
    parent: legacy.User = Depends(legacy.parent),
    session: Session = Depends(legacy.db),
):
    item = session.get(TestFeedback, feedback_id)
    if not item or item.author_id != parent.id:
        raise HTTPException(404, 'Test feedback not found')
    _test_worksheet(session, item.worksheet_id, parent)
    release = (payload.addressed_release or '').strip() or None
    if payload.status == 'addressed':
        if not release or not re.fullmatch(r'v?\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?', release):
            raise HTTPException(400, 'An addressed item requires a semantic release number, such as 0.25.0')
        release = release.removeprefix('v')
    elif release:
        raise HTTPException(400, 'Only addressed feedback can have an addressed release')
    item.feedback_type = payload.feedback_type
    item.note = payload.note.strip()
    item.status = payload.status
    item.addressed_release = release
    item.updated_at = datetime.utcnow()
    session.commit()
    session.refresh(item)
    return _feedback_view(item, session)


@app.get('/api/v0250/capabilities')
def capabilities(_: legacy.User = Depends(legacy.current_user)):
    return {
        'version': legacy.APP_VERSION,
        'parent_test_worksheets': True,
        'question_feedback': True,
        'overall_feedback': True,
        'release_traceability': True,
        'learning_evidence_isolation': True,
        'inherits_v0240': True,
    }


v0120._move_spa_fallback_to_end()
