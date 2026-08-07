from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import main as legacy
from . import v060

app = legacy.app
app.version = '0.7.0'
_original_dashboard = legacy.dashboard
_original_complete = legacy.complete


class Assignment(legacy.Base):
    __tablename__ = 'assignments'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(100))
    topics: Mapped[str] = mapped_column(Text, default='[]')
    question_count: Mapped[int] = mapped_column(default=10)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AssignmentIn(BaseModel):
    title: str
    topics: list[str]
    question_count: int = 10
    due_date: date | None = None


def _trend(session: Session, sid: int, days: int) -> dict[str, Any]:
    since = date.today() - timedelta(days=days - 1)
    works = list(session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id == sid, legacy.Worksheet.worksheet_date >= since).order_by(legacy.Worksheet.worksheet_date)).all())
    points=[]
    for w in works:
        qs=list(w.questions); answered=[q for q in qs if q.attempts]
        independent=sum(1 for q in answered if any(a.correct for a in q.attempts) and not (q.hint_count or 0))
        hints=sum(q.hint_count or 0 for q in qs)
        points.append({'date':w.worksheet_date.isoformat(),'accuracy':round(w.score/max(1,w.total)*100) if w.completed_at else None,'independent_mastery':round(independent/max(1,len(answered))*100),'hints':hints,'minutes':round((w.elapsed_seconds or 0)/60,1)})
    return {'days':days,'points':points}


def _insights(data: dict[str,Any]) -> list[str]:
    adaptive=data.get('adaptive_learning',{}); topics=[x for x in adaptive.get('topics',[]) if x.get('questions')]
    if not topics:return ['Complete a few quests to unlock personalised learning insights.']
    strongest=max(topics,key=lambda x:x['mastery']); support=min(topics,key=lambda x:x['mastery']); hinted=max(topics,key=lambda x:x['hint_rate'])
    messages=[f"{strongest['topic'].title()} is currently the strongest area at {strongest['mastery']}% mastery.",f"{support['topic'].title()} is the best area to target next at {support['mastery']}% mastery."]
    if hinted['hint_rate']>=25:messages.append(f"{hinted['topic'].title()} is using hints on {hinted['hint_rate']}% of recent questions, so extra independent practice is recommended.")
    due=adaptive.get('review_due_topics',[])
    if due:messages.append('Spaced revision is due for '+', '.join(x.title() for x in due)+'.')
    return messages


def _personal_bests(session: Session,sid:int) -> list[dict[str,Any]]:
    rows=list(session.scalars(select(legacy.Question).join(legacy.Worksheet).where(legacy.Worksheet.student_id==sid,legacy.Question.answered_at.is_not(None)).order_by(legacy.Question.answered_at.desc()).limit(120)).all())
    result=[]; seen=set()
    for q in rows:
        code=q.skill.split(':',1)[0]
        if code in seen or (q.hint_count or 0)>0 or not any(a.correct for a in q.attempts):continue
        older=[x for x in rows if x.skill.split(':',1)[0]==code and x.answered_at and q.answered_at and x.answered_at<q.answered_at]
        if any((x.hint_count or 0)>0 or not any(a.correct for a in x.attempts) for x in older):
            seen.add(code);result.append({'code':code,'topic':q.topic,'message':f"Mastery moment: {q.topic.title()} was completed independently after previously needing support."})
        if len(result)>=5:break
    return result


def dashboard_v070(session:Session,sid:int):
    data=_original_dashboard(session,sid)
    data['parent_insights']=_insights(data)
    data['progress_trends']={'7d':_trend(session,sid,7),'30d':_trend(session,sid,30),'90d':_trend(session,sid,90)}
    data['mastery_moments']=_personal_bests(session,sid)
    moments=len(data['mastery_moments']); independent=sum(1 for w in session.scalars(select(legacy.Worksheet).where(legacy.Worksheet.student_id==sid)).all() for q in w.questions if q.attempts and any(a.correct for a in q.attempts) and not (q.hint_count or 0))
    rewards=[]
    if independent>=10:rewards.append({'name':'Independent Explorer','detail':'10 questions solved without hints'})
    if independent>=50:rewards.append({'name':'Independent Champion','detail':'50 questions solved without hints'})
    if moments>=1:rewards.append({'name':'Breakthrough','detail':'Mastered something that previously needed support'})
    if data.get('streak',0)>=7:rewards.append({'name':'Week Warrior','detail':'7-day completion streak'})
    data['rewards']=rewards
    return data

legacy.dashboard=dashboard_v070

@app.on_event('startup')
def create_v070_tables():
    legacy.Base.metadata.create_all(legacy.engine)

@app.post('/api/assignments')
def create_assignment(payload:AssignmentIn,_=Depends(legacy.parent),session:Session=Depends(legacy.db)):
    student=session.scalar(select(legacy.User).where(legacy.User.role=='student'))
    topics=[x for x in payload.topics if x in legacy.LEVEL4_STRANDS]
    if not topics:raise HTTPException(400,'Select at least one learning area')
    row=Assignment(student_id=student.id,title=payload.title.strip() or 'Practice Quest',topics=legacy.json.dumps(topics),question_count=max(5,min(50,payload.question_count)),due_date=payload.due_date)
    session.add(row);session.commit();session.refresh(row);return {'id':row.id,'title':row.title,'topics':topics,'question_count':row.question_count,'due_date':row.due_date.isoformat() if row.due_date else None,'active':row.active}

@app.get('/api/assignments')
def assignments(user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    sid=user.id if user.role=='student' else session.scalar(select(legacy.User.id).where(legacy.User.role=='student'))
    rows=session.scalars(select(Assignment).where(Assignment.student_id==sid,Assignment.active==True).order_by(Assignment.created_at.desc())).all()
    return [{'id':x.id,'title':x.title,'topics':legacy.json.loads(x.topics),'question_count':x.question_count,'due_date':x.due_date.isoformat() if x.due_date else None} for x in rows]

@app.get('/api/home-assistant/status')
def ha_status(user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    sid=user.id if user.role=='student' else session.scalar(select(legacy.User.id).where(legacy.User.role=='student'))
    d=dashboard_v070(session,sid); today=session.scalar(select(legacy.Worksheet).where(legacy.Worksheet.student_id==sid,legacy.Worksheet.worksheet_date==date.today()))
    return {'today_complete':bool(today and today.completed_at),'today_status':today.status if today else 'not_started','today_score':today.score if today else 0,'today_total':today.total if today else 0,'streak':d['streak'],'accuracy':d['accuracy'],'xp':d['user']['xp'],'level':d['user']['level'],'hints_total':d['hint_summary']['total_hints'],'recommended_topic':d.get('adaptive_learning',{}).get('recommended_topic'),'review_due_topics':d.get('adaptive_learning',{}).get('review_due_topics',[]),'mastery_moments':len(d['mastery_moments'])}
