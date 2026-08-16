from __future__ import annotations

import random
from datetime import datetime
from typing import Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import main as legacy
from . import v080

app = legacy.app
app.version = '0.9.0'


class ConfidenceEvent(legacy.Base):
    __tablename__ = 'confidence_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(index=True)
    student_id: Mapped[int] = mapped_column(index=True)
    confidence: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ConfidenceIn(BaseModel):
    confidence: str


class AdventureIn(BaseModel):
    theme: str


CONFIDENCE_WEIGHT = {'guessed': 0.75, 'pretty_sure': 0.9, 'knew_it': 1.0}
ADVENTURES = {
    'bakery': {
        'title': 'Bakery Challenge', 'icon': '🧁',
        'intro': 'Prepare every order and open the bakery before the morning rush.',
        'mission': 'Open the bakery on time',
        'objective': 'Check supplies, prepare trays, organise orders and complete the final delivery.',
        'outcome': 'The doors open on time and every customer receives the right order.',
        'topics': ['number', 'measurement', 'statistics'],
        'chapters': ['Check the pantry', 'Prepare the trays', 'Handle the rush', 'Pack the delivery', 'Open the doors'],
    },
    'camping': {
        'title': 'Camping Adventure', 'icon': '🏕️',
        'intro': 'Plan the route and get the whole group safely to camp before dark.',
        'mission': 'Reach the campsite before sunset',
        'objective': 'Pack supplies, follow the map, measure the campsite and plan the return trip.',
        'outcome': 'The group reaches camp safely with the correct supplies and a clear route home.',
        'topics': ['measurement', 'space', 'number'],
        'chapters': ['Pack the gear', 'Choose the trail', 'Cross the lookout', 'Set up camp', 'Plan the journey home'],
    },
    'space': {
        'title': 'Space Mission', 'icon': '🚀',
        'intro': 'Launch, navigate and return the research crew safely to Earth.',
        'mission': 'Bring the research crew home',
        'objective': 'Load supplies, navigate the grid, check the flight data and prepare re-entry.',
        'outcome': 'The research crew lands safely with all mission data secured.',
        'topics': ['space', 'number', 'measurement', 'statistics'],
        'chapters': ['Prepare for launch', 'Reach orbit', 'Navigate the asteroid field', 'Prepare re-entry', 'Land safely'],
    },
    'animal_rescue': {
        'title': 'Animal Rescue', 'icon': '🐶',
        'intro': 'Organise the shelter and help every animal receive the care it needs.',
        'mission': 'Prepare every animal for adoption day',
        'objective': 'Count supplies, organise enclosures, review care data and finish the adoption plan.',
        'outcome': 'Every animal is cared for and the shelter is ready for adoption day.',
        'topics': ['number', 'measurement', 'statistics'],
        'chapters': ['Morning care', 'Prepare the enclosures', 'Check the supplies', 'Match the families', 'Open adoption day'],
    },
}

STORY_DETAILS = {
    'bakery': {'container': 'trays', 'item': 'cupcakes', 'used': 'orders', 'place': 'delivery shelf'},
    'camping': {'container': 'packs', 'item': 'meal portions', 'used': 'hikers', 'place': 'water station'},
    'space': {'container': 'cargo pods', 'item': 'energy cells', 'used': 'engine checks', 'place': 'rescue beacon'},
    'animal_rescue': {'container': 'food tubs', 'item': 'meal portions', 'used': 'morning feeds', 'place': 'medical supplies'},
}


def _adventure_goals(session: Session, student_id: int, story: dict[str, Any]) -> list[str]:
    """Put the least-secure relevant learning areas first."""
    ranked = []
    for order, topic in enumerate(story['topics']):
        skill = session.scalar(select(legacy.Skill).where(
            legacy.Skill.student_id == student_id, legacy.Skill.topic == topic
        ))
        assessed = bool(skill and skill.attempts)
        mastery = skill.rolling_accuracy if assessed else -1.0
        ranked.append((mastery, skill.attempts if assessed else 0, order, topic))
    return [item[-1] for item in sorted(ranked)]


def _mission_facts(theme: str, rng: random.Random) -> dict[str, Any]:
    details = STORY_DETAILS[theme]
    mode = rng.randint(2, 8)
    other_readings = rng.sample([value for value in range(2, 12) if value != mode], 4)
    readings = [mode, mode, mode, *other_readings]
    rng.shuffle(readings)
    return {
        **details,
        'containers': rng.randint(4, 8),
        'items_per_container': rng.randint(6, 12),
        'items_used': rng.randint(3, 9),
        'length': rng.randint(6, 12),
        'width': rng.randint(3, 6),
        'duration_hours': rng.randint(1, 3),
        'duration_minutes': rng.choice([15, 30, 45]),
        'readings': readings,
    }


def _mission_question(theme: str, topic: str, index: int, chapter: str,
                      facts: dict[str, Any], rng: random.Random):
    """Build a theme-specific applied question from shared mission data."""
    prefix = ''
    if topic == 'number':
        containers = facts['containers'] + index
        each = facts['items_per_container']
        used = facts['items_used']
        answer = containers * each - used
        prompt = (
            f"{prefix}There are {containers} {facts['container']} with {each} {facts['item']} in each. "
            f"After {used} are used for {facts['used']}, how many remain?"
        )
        return legacy.q(
            'VC2M5N06', 'story_multi_step_operations', prompt, 'number',
            {'operation': 'multiply_then_subtract', 'applied_steps': 2}, answer,
            f'First calculate {containers} × {each} = {containers * each}. Then subtract {used} to get {answer}.',
        )
    if topic == 'measurement':
        if index % 2:
            hours, minutes = facts['duration_hours'], facts['duration_minutes']
            answer = hours * 60 + minutes
            return legacy.q(
                'VC2M5M03', 'story_duration',
                f'{prefix}This stage takes {hours} hours and {minutes} minutes. How many minutes is that altogether?',
                'number', {'unit': 'minutes', 'applied_steps': 2}, answer,
                f'Convert {hours} hours to {hours * 60} minutes, then add {minutes} to get {answer} minutes.',
            )
        length, width = facts['length'] + index, facts['width']
        answer = length * width
        return legacy.q(
            'VC2M5M02', 'story_area',
            f"{prefix}A rectangular {facts['place']} is {length} m long and {width} m wide. What area must be prepared?",
            'number', {'unit': 'm²', 'length': length, 'width': width, 'applied_steps': 1}, answer,
            f'Area = length × width, so {length} × {width} = {answer} m².',
        )
    if topic == 'space':
        columns = ['A', 'B', 'C', 'D']; rows = [1, 2, 3, 4]
        target = f'{rng.choice(columns)}{rng.choice(rows)}'
        choices = [f'{column}{row}' for column in columns for row in rows]
        return legacy.q(
            'VC2M5SP03', 'story_grid_reference',
            f"{prefix}The {facts['place']} is highlighted on the mission grid. Which grid reference contains it?",
            'choice', {'choices': choices, 'visual': {'type': 'grid', 'columns': columns, 'rows': len(rows), 'target': target}, 'applied_steps': 1}, target,
            f'Read the highlighted column first and then its row. The location is {target}.',
        )
    readings = [value + index for value in facts['readings']]
    mode = max(set(readings), key=readings.count)
    return legacy.q(
        'VC2M5ST01', 'story_data_frequency',
        f'{prefix}The latest mission readings are {readings}. Which value occurs most often?',
        'number', {'data': readings, 'applied_steps': 2}, mode,
        f'Tally each reading, then compare the frequencies. {mode} occurs most often.',
    )


def _confidence(session: Session, qid: int, sid: int) -> str | None:
    row = session.scalar(select(ConfidenceEvent).where(ConfidenceEvent.question_id == qid, ConfidenceEvent.student_id == sid).order_by(ConfidenceEvent.created_at.desc()))
    return row.confidence if row else None


def skill_mastery(session: Session, sid: int) -> list[dict[str, Any]]:
    rows = list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Question.answered_at.is_not(None)).order_by(legacy.Question.answered_at.desc()).limit(300)).all())
    grouped: dict[str, list[legacy.Question]] = {}
    for q in rows:
        grouped.setdefault(q.skill.split(':', 1)[0], []).append(q)
    result=[]
    for code, qs in grouped.items():
        recent=qs[:12]; scores=[]; hints=0
        for q in recent:
            correct=any(a.correct for a in q.attempts)
            base=1.0 if correct and not (q.hint_count or 0) else 0.7 if correct and q.hint_count==1 else 0.4 if correct else 0.0
            conf=_confidence(session,q.id,sid)
            base*=CONFIDENCE_WEIGHT.get(conf,1.0)
            scores.append(base); hints += q.hint_count or 0
        mastery=round(sum(scores)/max(1,len(scores))*100)
        status='mastered' if len(recent)>=5 and mastery>=85 else 'strong' if mastery>=75 else 'developing' if mastery>=60 else 'needs_support'
        strand,title=legacy.LEVEL4_OUTCOMES.get(code,('Other',code))
        result.append({'code':code,'strand':strand,'title':title,'attempts':len(recent),'mastery':mastery,'status':status,'hints':hints})
    return sorted(result,key=lambda x:(x['mastery'],x['code']))


def misconception_for(q: legacy.Question, answer: str) -> dict[str,str] | None:
    skill=q.skill.split(':',1)[-1]; a=str(answer).strip().lower(); correct=str(q.correct_answer).strip().lower()
    if skill in ('perimeter','area'):
        return {'type':'measurement_formula','message':'This may be a perimeter-versus-area mix-up. Perimeter measures around the edge, while area measures the space inside.'}
    if 'grid' in skill and len(a)>=2 and a[::-1].lower()==correct.lower():
        return {'type':'coordinate_order','message':'The row and column appear to be reversed. Read the column first, then the row.'}
    if 'fraction' in skill:
        return {'type':'fraction_reasoning','message':'The fraction comparison may need a common visual model. Compare equal-sized wholes rather than only the numerator or denominator.'}
    if 'clock' in skill:
        return {'type':'clock_hands','message':'Check which hand shows hours and which shows minutes. The shorter hand is the hour hand.'}
    return None


def mini_lesson(q: legacy.Question) -> dict[str,Any]:
    skill=q.skill.split(':',1)[-1]
    if 'fraction' in skill:
        return {'title':'Compare fractions visually','explanation':'Imagine both fractions are the same-sized food item. Split each whole into the denominator number of equal pieces, then shade the numerator.','steps':['Make sure the wholes are the same size.','Look at how many equal parts each whole has.','Compare the shaded amount, not just the numbers.'],'example':'3/4 is larger than 2/3 because 9/12 is larger than 8/12.','visual':{'type':'fraction_compare','items':[{'label':'3/4','numerator':3,'denominator':4},{'label':'2/3','numerator':2,'denominator':3}]}}
    if skill in ('perimeter','area'):
        return {'title':'Perimeter or area?','explanation':'Perimeter is the distance around a shape. Area is the amount of surface inside it.','steps':['Ask whether the question says around or inside.','For rectangle perimeter use 2 × (length + width).','For rectangle area use length × width.'],'example':'A 5 cm by 3 cm rectangle has perimeter 16 cm and area 15 cm².'}
    if 'grid' in skill:
        return {'title':'Read a grid reference','explanation':'Grid references are read across first, then up or down. In MathQuest that means column letter first, row number second.','steps':['Find the column letter.','Find the row number.','Join them, for example B3.'],'example':'Column C and row 2 gives C2.'}
    if 'clock' in skill:
        return {'title':'Read an analogue clock','explanation':'The short hand shows the hour. The long hand shows minutes in groups of five.','steps':['Read the short hand.','Read the long hand.','Combine the hour and minutes.'],'example':'Long hand on 6 means 30 minutes.'}
    return {'title':'Break the problem into steps','explanation':q.working or 'Identify what is known, what must be found, and the operation that connects them.','steps':['Underline the important numbers.','Choose the operation or comparison.','Check whether the result is reasonable.'],'example':'Try a simpler version first, then return to this question.'}


def _regenerate_remaining(session: Session, ws: legacy.Worksheet, topic: str, level_delta: int) -> int:
    changed=0; rng=random.Random(f'adapt:{ws.id}:{datetime.utcnow().isoformat()}')
    for q in sorted(ws.questions,key=lambda x:x.position):
        if q.topic!=topic or q.attempts or legacy.question_status(q) not in ('not_started','skipped'): continue
        new_level=max(1,min(8,q.level+level_delta)); skill,prompt,atype,payload,ans,working=legacy.make_question(topic,min(4,new_level),rng)
        q.level=new_level; q.skill=skill; q.prompt=prompt; q.answer_type=atype; q.payload=legacy.json.dumps(payload); q.correct_answer=ans; q.working=working; changed+=1
        if changed>=2: break
    session.commit(); return changed


@app.on_event('startup')
def create_v090_tables():
    legacy.Base.metadata.create_all(legacy.engine)


@app.get('/api/mastery/skills')
def mastery_api(user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    sid=user.id if user.role=='student' else session.scalar(select(legacy.User.id).where(legacy.User.role=='student'))
    return {'skills':skill_mastery(session,sid)}


@app.post('/api/questions/{qid}/confidence')
def confidence(qid:int,payload:ConfidenceIn,user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    if user.role!='student': raise HTTPException(403,'Student access required')
    if payload.confidence not in CONFIDENCE_WEIGHT: raise HTTPException(400,'Unknown confidence value')
    q=session.get(legacy.Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    ws=session.get(legacy.Worksheet,q.worksheet_id)
    if not ws or ws.student_id!=user.id: raise HTTPException(403,'Question does not belong to this student')
    session.add(ConfidenceEvent(question_id=q.id,student_id=user.id,confidence=payload.confidence)); session.commit()
    correct=any(a.correct for a in q.attempts); delta=1 if correct and payload.confidence=='knew_it' and not (q.hint_count or 0) else -1 if not correct else 0
    changed=_regenerate_remaining(session,ws,q.topic,delta) if delta else 0
    return {'ok':True,'confidence':payload.confidence,'difficulty_adjusted_questions':changed}


@app.get('/api/questions/{qid}/teaching')
def teaching(qid:int,user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    q=session.get(legacy.Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    ws=session.get(legacy.Worksheet,q.worksheet_id)
    if not ws or ws.student_id!=user.id: raise HTTPException(403,'Question does not belong to this student')
    wrong=next((a for a in reversed(sorted(q.attempts,key=lambda x:x.attempt_number)) if not a.correct),None)
    lesson=mini_lesson(q); lesson['misconception']=misconception_for(q,wrong.answer) if wrong else None
    return lesson


@app.get('/api/adventures')
def adventures(user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    if user.role != 'student':
        return [{'id': key, **story, 'recommended_goals': story['topics'][:2]} for key, story in ADVENTURES.items()]
    return [
        {'id': key, **story, 'recommended_goals': _adventure_goals(session, user.id, story)[:2]}
        for key, story in ADVENTURES.items()
    ]


@app.post('/api/worksheets/{wid}/adventure')
def apply_adventure(wid:int,payload:AdventureIn,user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    if user.role!='student': raise HTTPException(403,'Student access required')
    if payload.theme not in ADVENTURES: raise HTTPException(400,'Unknown adventure')
    ws=session.get(legacy.Worksheet,wid)
    if not ws or ws.student_id!=user.id: raise HTTPException(404,'Worksheet not found')
    story=ADVENTURES[payload.theme]
    available=[q for q in sorted(ws.questions,key=lambda x:x.position) if not q.attempts]
    rng=random.Random(f'adventure:{ws.id}:{payload.theme}')
    goals=_adventure_goals(session,user.id,story)
    priority=goals[:2]
    topic_plan=priority+priority+[topic for topic in story['topics'] if topic not in priority]
    facts=_mission_facts(payload.theme,rng)
    mission_id=f'{payload.theme}-{ws.id}'
    recent_questions=list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(
        legacy.Worksheet.student_id==user.id,legacy.Worksheet.session_kind=='adventure',legacy.Worksheet.id!=ws.id,
    ).order_by(legacy.Worksheet.started_at.desc(),legacy.Question.position.asc()).limit(120)).all())
    recent={legacy.stored_question_identity(question) for question in recent_questions}
    seen=set()
    changed=0
    for index,q in enumerate(available):
        topic=topic_plan[index%len(topic_plan)]
        chapter_index=min(len(story['chapters'])-1,index*len(story['chapters'])//max(1,len(available)))
        chapter=story['chapters'][chapter_index]
        for attempt in range(25):
            variant_index=index+attempt*len(available)
            skill,prompt,atype,question_payload,answer,working=_mission_question(
                payload.theme,topic,variant_index,chapter,facts,rng
            )
            identity=legacy.question_identity(prompt,question_payload)
            if identity not in seen and (identity not in recent or attempt>=20): break
        seen.add(identity)
        adventure={
            'version':2,'mission_id':mission_id,'theme':payload.theme,'title':story['title'],
            'mission':story['mission'],'objective':story['objective'],'outcome':story['outcome'],
            'chapter':chapter,'chapter_number':chapter_index+1,'chapters':story['chapters'],
            'question':index+1,'total':len(available),'learning_goal':topic,
            'learning_goals':goals,'mission_data':facts,
        }
        q.topic=topic;q.skill=skill;q.prompt=prompt;q.answer_type=atype;q.correct_answer=str(answer);q.working=working
        q.payload=legacy.json.dumps({**question_payload,'adventure':adventure})
        changed+=1
    ws.selected_topic=story['title']
    ws.session_kind='adventure'
    session.commit()
    return {
        'theme':payload.theme,'title':story['title'],'mission':story['mission'],
        'objective':story['objective'],'learning_goals':goals,'chapters':story['chapters'],
        'questions_linked':changed,
    }


@app.get('/api/v090/capabilities')
def capabilities(_:legacy.User=Depends(legacy.current_user)):
    return {'version':'0.9.0','skill_mastery':True,'teaching_mode':True,'misconception_detection':True,'dynamic_difficulty':True,'multi_step_support':True,'story_adventures':list(ADVENTURES),'confidence_tracking':True}
