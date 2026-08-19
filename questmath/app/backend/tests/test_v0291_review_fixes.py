from __future__ import annotations

import json
from datetime import date

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app import main as legacy
from app import v0291


def test_grid_reference_question_always_has_labelled_grid_visual():
    question = legacy.Question(
        skill='VC2M4SP03:grid_references',
        prompt='A treasure is at column A, row 6. Write its grid reference.',
        payload='{}',
        correct_answer='A6',
    )
    v0291.ensure_grid_visual(question)
    payload = json.loads(question.payload)
    assert payload['visual']['type'] == 'grid'
    assert payload['visual']['columns'] == ['A', 'B', 'C', 'D', 'E']
    assert payload['visual']['rows'] == 6
    assert payload['visual']['target'] == 'A6'


def test_grouped_meal_problem_names_the_unit_being_used():
    question = legacy.Question(
        skill='mathematical_modelling',
        prompt='There are 9 packs with 7 meal portions in each. After 6 are used for hikers, how many remain?',
        payload='{}',
        correct_answer='57',
    )
    v0291.clarify_grouped_units(question)
    assert 'After 6 meal portions are used for hikers' in question.prompt
    assert question.prompt.endswith('how many meal portions remain?')


def test_final_quality_pass_replaces_duplicate_question_concepts(monkeypatch):
    engine = create_engine('sqlite:///:memory:', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    legacy.Base.metadata.create_all(engine)
    session = Session(engine)
    user = legacy.User(username='student-v0291', password_hash='x', role='student', display_name='Student')
    session.add(user); session.flush()
    worksheet = legacy.Worksheet(student_id=user.id, worksheet_date=date.today(), total=2, selected_topic='measurement')
    session.add(worksheet); session.flush()
    duplicate_prompt = 'This stage takes 3 hours and 30 minutes. How many minutes is that altogether?'
    for position in range(2):
        session.add(legacy.Question(
            worksheet_id=worksheet.id,
            topic='measurement',
            skill='VC2M4M03:duration_conversion',
            level=4,
            prompt=duplicate_prompt,
            answer_type='number',
            payload='{}',
            correct_answer='210',
            working='3 hours is 180 minutes; add 30 minutes.',
            position=position,
        ))
    session.commit(); session.refresh(worksheet)

    def replacement(*_args, **_kwargs):
        return legacy.q(
            'VC2M4M03',
            'duration_conversion',
            'How many minutes are in 2 hours and 15 minutes?',
            'number',
            {'unit': 'minutes'},
            135,
            '2 hours is 120 minutes; add 15 minutes.',
        )

    monkeypatch.setattr(legacy, 'make_question', replacement)
    v0291.repair_worksheet_questions(session, worksheet)
    concepts = [v0291.question_concept(question) for question in sorted(worksheet.questions, key=lambda item: item.position)]
    assert len(concepts) == len(set(concepts))
    assert sorted(question.prompt for question in worksheet.questions).count(duplicate_prompt) == 1
    session.close()
