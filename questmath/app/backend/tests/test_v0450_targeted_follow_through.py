from __future__ import annotations

import json
from datetime import datetime

from app import main as legacy
from app import v0230, v0440, v0450
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

def make_session():
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    student = legacy.User(username='sienna-v0450', password_hash='x', role='student', display_name='Sienna')
    legacy_session = Session(engine)
    legacy_session.add(student); legacy_session.flush()
    legacy_session.add(legacy.Setting(student_id=student.id, question_count=10, adaptive_mode=True, enabled_topics='["number"]', manual_levels='{}'))
    legacy_session.commit()
    return legacy_session, student

def test_targeted_detail_records_before_after_and_real_session_evidence(monkeypatch):
    session, student = make_session()
    outcomes = [{'code':'VC2M4N06','title':'Efficient calculation strategies','topic':'number','questions':4,'status':'developing','review_due':False,'target_skill':'written_subtraction'}]
    recommendation = {'mode':'practice','minutes':5,'topic':'number','outcome_code':'VC2M4N06','title':'Efficient calculation strategies','reason':'Keep practising','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230, 'outcome_mastery', lambda *_: outcomes)
    plan = v0440.build_learning_plan(session, student.id, 5)
    worksheet = v0450.compose_targeted_session(session, student.id, plan)
    questions = sorted(worksheet.questions, key=lambda item: item.position)
    for index, question in enumerate(questions):
        question.answered_at = datetime.utcnow()
        question.state = 'answered_correct'
        question.hint_count = 1 if index == 1 else 0
        session.add(legacy.Attempt(question_id=question.id, student_id=student.id, answer=question.correct_answer, correct=True, attempt_number=1, seconds=10))
    worksheet.completed_at = datetime.utcnow()
    session.commit()
    detail = v0450._detail(session, worksheet, student.id)
    assert detail['before']['questions'] == 4
    assert detail['evidence']['answered'] == 6
    assert detail['evidence']['support_used_questions'] == 1
    assert detail['evidence']['independent_checks'] == 1
    assert detail['evidence_change']['questions_added'] >= 0
    session.close()

def test_student_safe_summary_does_not_expose_parent_analytics():
    detail={'purpose':'consolidate','target_skill':'written_subtraction','evidence':{'support_then_independent':True,'independent_checks':1,'eventual_successes':4},'evidence_change':{'questions_added':2}}
    safe=v0450._student_safe(detail)
    assert 'message' in safe and 'evidence_added' in safe
    assert 'independent_accuracy' not in str(safe)
    assert 'outcome_code' not in str(safe)
