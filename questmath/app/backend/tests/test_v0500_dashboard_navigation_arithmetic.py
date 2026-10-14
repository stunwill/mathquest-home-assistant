from datetime import datetime
import json
import random
import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import main as legacy, v0230, v0330, v0440, grade5_arithmetic as maths


@pytest.fixture
def learning(tmp_path):
    from app import v0500
    engine=create_engine(f'sqlite:///{tmp_path / "progress.db"}',connect_args={'check_same_thread':False})
    legacy.Base.metadata.create_all(engine)
    session=Session(engine)
    learner=legacy.User(username='sienna-test',password_hash='x',role='student',display_name='Sienna',xp=2450,highest_level=12)
    other=legacy.User(username='other',password_hash='x',role='student',display_name='Other',xp=500,highest_level=3)
    session.add_all([learner,other]);session.flush()
    for student in (learner,other):
        session.add(legacy.Setting(student_id=student.id,question_count=10,adaptive_mode=True,enabled_topics='["number","algebra"]',manual_levels='{}'))
    session.commit()
    def db(): yield session
    v0500.app.dependency_overrides[legacy.db]=db
    yield session,learner,other,engine,TestClient(v0500.app)
    v0500.app.dependency_overrides.clear();session.close();engine.dispose()


def headers(learner): return {'Authorization':f'Bearer {legacy.token_for(learner)}'}


def worksheet(session,learner,count=6,skill='VC2M4N06:written_subtraction',kind='practice'):
    ws=legacy.Worksheet(student_id=learner.id,worksheet_date=datetime.utcnow().date(),selected_topic='number',session_kind=kind,total=count,status='in_progress')
    session.add(ws);session.flush()
    for position in range(count):
        q=legacy.Question(worksheet_id=ws.id,position=position,topic='algebra' if 'A0' in skill else 'number',skill=skill,level=4,prompt='Calculate 624 − 137.',answer_type='number',payload='{}',correct_answer='487',working='624 − 137 = 487.',state='not_started')
        session.add(q)
    session.commit();session.refresh(ws);return ws


def evidence(session,learner,skill='VC2M4N06:written_subtraction',supported=False):
    ws=worksheet(session,learner,12,skill)
    for q in ws.questions:
        q.answered_at=datetime.utcnow();q.state='answered_correct';q.hint_count=int(supported)
        session.add(legacy.Attempt(question_id=q.id,student_id=learner.id,answer=q.correct_answer,correct=True,attempt_number=1,seconds=10))
    ws.completed_at=datetime.utcnow();ws.status='completed';session.commit()
    return ws


def test_dashboard_reads_preserve_rewards_and_are_scoped_to_authenticated_learner(learning):
    session,learner,other,engine,client=learning
    for _ in range(3):
        data=client.get('/api/dashboard/student',headers=headers(learner)).json()['user']
        assert (data['xp'],data['level'],data['highest_level'])==(2450,10,12)
        assert (data['level_progress'],data['xp_per_level'],data['xp_until_next_level'],data['next_level'])==(200,250,50,11)
    assert client.get('/api/dashboard/student',headers=headers(other)).json()['user']['xp']==500
    with Session(engine) as restarted:
        assert restarted.get(legacy.User,learner.id).xp==2450
        assert restarted.get(legacy.User,learner.id).highest_level==12


def test_completion_rejects_unanswered_work_and_awards_rewards_only_once(learning):
    session,learner,_,engine,client=learning
    ws=worksheet(session,learner,5)
    assert client.post(f'/api/worksheets/{ws.id}/complete',headers=headers(learner)).status_code==400
    assert learner.xp==2450
    for q in ws.questions:
        q.answered_at=datetime.utcnow();q.state='answered_correct'
        session.add(legacy.Attempt(question_id=q.id,student_id=learner.id,answer=q.correct_answer,correct=True,attempt_number=1,seconds=10))
    session.commit()
    first=client.post(f'/api/worksheets/{ws.id}/complete',headers=headers(learner))
    second=client.post(f'/api/worksheets/{ws.id}/complete',headers=headers(learner))
    assert first.status_code==second.status_code==200
    assert first.json()['xp_earned']==second.json()['xp_earned']==100
    for _ in range(2): client.get('/api/dashboard/student',headers=headers(learner))
    with Session(engine) as restarted: assert restarted.get(legacy.User,learner.id).xp==2550


def test_skipped_completion_retains_existing_rules_without_duplicate_rewards(learning):
    session,learner,_,_,client=learning
    ws=worksheet(session,learner,5)
    for q in ws.questions: q.state='skipped';q.skipped_count=1
    session.commit()
    result=client.post(f'/api/worksheets/{ws.id}/complete',headers=headers(learner))
    assert result.status_code==200 and result.json()['xp_earned']==0
    assert learner.xp==2450


@pytest.mark.parametrize('operation',list(maths.FAMILIES))
def test_generated_arithmetic_answers_formats_and_variety(operation):
    families=set();prompts=set()
    for seed in range(100):
        generated=maths.generate(operation,random.Random(seed),challenge=seed%3==0)
        p=generated['payload'];a,b=p['operands'];family=p['question_family'].removeprefix(f'grade5_{operation}_')
        answer=int(generated['answer']);families.add(family);prompts.add(generated['prompt'])
        if operation=='subtraction':
            expected=b if family=='missing' else (a+50)//100*100-(b+50)//100*100 if family=='estimate' else p['claimed']-(a-b) if family=='error' else a-b+p.get('received',0)
            assert a>=1000 and a>b
            if p['regrouping_across_zero']: assert a%1000<10 and a%10<b%10
        elif operation=='multiplication':
            expected=a if family=='missing' else a*b
            assert a>=12 and (b>=12 if seed%3==0 else b>=6)
        elif operation=='division':
            expected=a if family=='missing' else a%b if family=='remainder' else a//b
            assert a>=72
            if family!='remainder': assert a%b==0
            else: assert 'left over' in generated['prompt']
        else:
            expected=b if family=='missing_change' else a+b if family=='context' else a
        assert answer==expected
        assert generated['answer_type']=='number' and legacy.normalise(str(answer))==legacy.normalise(generated['answer'])
        assert len(p['grade5_support']['hints'])==3 and p['grade5_support']['worked_example']
        assert p['curriculum_alignment'] in ('VC2M4N06','VC2M4A01','VC2M5N06','VC2M5N07','VC2M5N08','VC2M5A02')
    assert len(families)>=3 and len(prompts)>=90


def test_difficulty_uses_independent_skill_evidence_not_supported_success(learning):
    session,learner,other,_,_=learning
    evidence(session,learner);evidence(session,other,supported=True)
    ready=worksheet(session,learner,12);supported=worksheet(session,other,12)
    maths.improve_worksheet(session,ready,learner.id);maths.improve_worksheet(session,supported,other.id)
    changed=[q for q in ready.questions if v0330._payload(q).get('arithmetic_extension')]
    assert len(changed)==10
    assert sum(v0330._payload(q)['difficulty_band']=='challenge' for q in changed)==1
    assert all(q.skill=='VC2M4N06:written_subtraction' for q in changed)
    assert all(not v0330._payload(q).get('arithmetic_extension') for q in supported.questions)
    assert v0330.THRESHOLDS.minimum_questions==6 and v0330.THRESHOLDS.ready_accuracy==.82


@pytest.mark.parametrize('protected',[{'purpose':'learn'},{'purpose':'prerequisite'},{'purpose':'review'},{'follow_through':'reteach'},{'follow_through':'gather_more_evidence'},{'evidence_focus':'subtraction_without_regrouping'}])
def test_foundational_targeted_sessions_are_not_forced_harder(learning,protected):
    session,learner,_,_,_=learning;evidence(session,learner)
    ws=worksheet(session,learner)
    before=[(q.prompt,q.correct_answer) for q in ws.questions]
    maths.improve_worksheet(session,ws,learner.id,protected)
    assert [(q.prompt,q.correct_answer) for q in ws.questions]==before


@pytest.mark.parametrize('kind',['diagnostic','parent_test'])
def test_diagnostics_and_parent_tests_remain_unchanged(learning,kind):
    session,learner,_,_,_=learning;evidence(session,learner)
    ws=worksheet(session,learner,kind=kind);before=[q.prompt for q in ws.questions]
    maths.improve_worksheet(session,ws,learner.id)
    assert [q.prompt for q in ws.questions]==before


def test_completed_and_resumed_questions_are_never_rewritten(learning):
    session,learner,_,_,_=learning
    completed=evidence(session,learner);before=[(q.id,q.prompt,q.correct_answer) for q in completed.questions]
    maths.improve_worksheet(session,completed,learner.id)
    assert [(q.id,q.prompt,q.correct_answer) for q in completed.questions]==before
    resumed=worksheet(session,learner)
    resumed.questions[0].hint_count=1;session.commit()
    before=[q.prompt for q in resumed.questions]
    maths.improve_worksheet(session,resumed,learner.id)
    assert [q.prompt for q in resumed.questions]==before


def test_targeted_final_composition_keeps_difficulty_lineage_and_support_aligned(learning,monkeypatch):
    session,learner,_,_,client=learning
    from app import v0500
    evidence(session,learner)
    outcomes=[{'code':'VC2M4N06','title':'Written subtraction','topic':'number','questions':12,'status':'secure','review_due':False,'target_skill':'written_subtraction'}]
    recommendation={'mode':'practice','minutes':10,'topic':'number','outcome_code':'VC2M4N06','title':'Written subtraction','reason':'Practise','prerequisite_for':None,'target_skill':'written_subtraction'}
    monkeypatch.setattr(v0230,'outcome_mastery',lambda *_:outcomes)
    monkeypatch.setattr(v0230,'next_session_recommendation',lambda *_:recommendation)
    plan=v0440.build_learning_plan(session,learner.id)
    ws=v0500.compose_targeted_session(session,learner.id,plan)
    advanced=[q for q in ws.questions if v0330._payload(q).get('arithmetic_extension')]
    assert len(advanced)>=3
    first=sorted(ws.questions,key=lambda q:q.position)[0]
    assert v0330._payload(first)['targeted_session_plan']['target']['skill']=='written_subtraction'
    for q in advanced:
        payload=v0330._payload(q)
        assert payload['targeted_session']['target_skill']=='written_subtraction'
        assert legacy.hint_text(q,1)==payload['grade5_support']['hints'][0]
        support=client.get(f'/api/questions/{q.id}/math-mentor-v0310?action=teach',headers=headers(learner))
        assert support.status_code==200
        assert support.json()['teach_steps']==payload['grade5_support']['teach_steps']
        example=client.get(f'/api/questions/{q.id}/math-mentor-v0310?action=worked_example',headers=headers(learner))
        assert example.json()['worked_example']==payload['grade5_support']['worked_example']


def test_strong_multiplication_and_division_have_grade5_questions_in_successive_worksheets(learning):
    session,learner,_,_,_=learning
    skill='VC2M4N06:efficient_multiply_divide';evidence(session,learner,skill)
    prompts=[];families=set()
    for _ in range(3):
        ws=worksheet(session,learner,12,skill)
        for i,q in enumerate(ws.questions):
            q.prompt='Calculate 30 ÷ 10.' if i%2 else 'Calculate 8 × 6.'
            q.payload=json.dumps({'operation':'division' if i%2 else 'multiplication'})
        session.commit();maths.improve_worksheet(session,ws,learner.id)
        for q in ws.questions:
            p=v0330._payload(q)
            if p.get('arithmetic_extension'):
                prompts.append(q.prompt);families.add(p['question_family'])
    assert len(set(prompts))>=20 and len(families)>=5
    assert any('×' in text for text in prompts) and any('÷' in text for text in prompts)


def test_ordinary_number_algebra_api_uses_ready_questions_without_rewriting_history(learning):
    session,learner,_,_,client=learning
    historical=[]
    for skill in ('VC2M4N06:written_subtraction','VC2M4N06:efficient_multiply_divide','VC2M4A02:fact_recall_multiplication','VC2M4A02:fact_recall_division','VC2M4A01:unknown_add_subtract'):
        historical.extend(evidence(session,learner,skill).questions)
    before=[(q.id,q.prompt,q.correct_answer) for q in historical]
    advanced=[]
    for _ in range(3):
        response=client.post('/api/sessions/new',headers=headers(learner),json={'kind':'practice','minutes':10,'topic':'number_algebra'})
        assert response.status_code==200
        advanced.extend(q for q in response.json()['questions'] if q['payload'].get('arithmetic_extension'))
    assert len(advanced)>=3
    assert [(q.id,q.prompt,q.correct_answer) for q in historical]==before


def test_missing_factor_and_dividend_hints_use_the_correct_inverse_operation():
    multiply=maths.generate('multiplication',random.Random(3),family='missing')['payload']['grade5_support']
    divide=maths.generate('division',random.Random(3),family='missing')['payload']['grade5_support']
    assert 'Divide the product' in multiply['hints'][1]
    assert 'Multiply the quotient' in divide['hints'][1]
