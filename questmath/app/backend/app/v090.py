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
    'bakery': {'title': 'Bakery Challenge', 'icon': '🧁', 'intro': 'Help run a busy bakery using fractions, money, time and data.', 'topics': ['number','measurement','statistics']},
    'camping': {'title': 'Camping Adventure', 'icon': '🏕️', 'intro': 'Plan a camping trip using measurement, maps, time and number skills.', 'topics': ['measurement','space','number']},
    'space': {'title': 'Space Mission', 'icon': '🚀', 'intro': 'Complete a space mission using coordinates, number, time and data.', 'topics': ['space','number','measurement','statistics']},
    'animal_rescue': {'title': 'Animal Rescue', 'icon': '🐶', 'intro': 'Help an animal shelter solve food, money, measurement and data problems.', 'topics': ['number','measurement','statistics']},
}

STORY_CONTEXT = {
    'bakery': ['The bakery is opening. Solve this to prepare the first orders:', 'A new customer order has arrived. Work this out for the baking team:', 'The lunch rush is getting busy. Solve the next bakery problem:', 'The shelves need restocking. Use your maths to help:', 'One final order remains before closing. Solve:'],
    'camping': ['The camping trip begins with some careful planning. Solve:', 'The group is packing supplies. Work out:', 'The trail presents a new challenge. Solve:', 'The campsite must be organised before dark. Work out:', 'Complete the final calculation so everyone can head home safely:'],
    'space': ['Mission control is preparing for launch. Solve:', 'The spacecraft has reached orbit. Calculate:', 'A navigation alert needs your maths skills. Work out:', 'The crew is preparing to return to Earth. Solve:', 'Complete the final mission calculation:'],
    'animal_rescue': ['The animal shelter is opening for the day. Solve:', 'A new animal has arrived and needs your help. Work out:', 'The care team needs to organise supplies. Solve:', 'Adoption preparations are underway. Calculate:', 'Complete the final task for the shelter:'],
}


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
def adventures(_:legacy.User=Depends(legacy.current_user)):
    return [{'id':k,**v} for k,v in ADVENTURES.items()]


@app.post('/api/worksheets/{wid}/adventure')
def apply_adventure(wid:int,payload:AdventureIn,user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    if user.role!='student': raise HTTPException(403,'Student access required')
    if payload.theme not in ADVENTURES: raise HTTPException(400,'Unknown adventure')
    ws=session.get(legacy.Worksheet,wid)
    if not ws or ws.student_id!=user.id: raise HTTPException(404,'Worksheet not found')
    story=ADVENTURES[payload.theme]; chapters=['Getting started','First challenge','A surprise problem','Final preparations','Mission complete'];contexts=STORY_CONTEXT[payload.theme]
    available=[q for q in sorted(ws.questions,key=lambda x:x.position) if not q.attempts]
    rng=random.Random(f'adventure:{ws.id}:{payload.theme}')
    changed=0
    for index,q in enumerate(available):
        topic=story['topics'][index%len(story['topics'])]
        skill,prompt,atype,question_payload,answer,working=legacy.make_question(topic,min(4,q.level),rng)
        chapter_index=min(len(chapters)-1,index*len(chapters)//max(1,len(available)))
        q.topic=topic;q.skill=skill;q.prompt=f"{story['icon']} {contexts[chapter_index]} {prompt}";q.answer_type=atype;q.correct_answer=str(answer);q.working=working
        q.payload=legacy.json.dumps({**question_payload,'adventure':{'theme':payload.theme,'title':story['title'],'chapter':chapters[chapter_index],'question':index+1,'total':len(available)}})
        changed+=1
    ws.selected_topic=story['title']
    session.commit(); return {'theme':payload.theme,'title':story['title'],'questions_linked':changed}


@app.get('/api/v090/capabilities')
def capabilities(_:legacy.User=Depends(legacy.current_user)):
    return {'version':'0.9.0','skill_mastery':True,'teaching_mode':True,'misconception_detection':True,'dynamic_difficulty':True,'multi_step_support':True,'story_adventures':list(ADVENTURES),'confidence_tracking':True}
