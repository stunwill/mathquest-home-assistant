from __future__ import annotations

from datetime import date, datetime
from typing import Any

from fastapi import Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from . import main as legacy
from . import v070

app = legacy.app
app.version = '0.8.0'
_original_make_question = legacy.make_question


class AssignmentProgress(legacy.Base):
    __tablename__ = 'assignment_progress'
    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(index=True)
    student_id: Mapped[int] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(String(30), default='assigned')
    worksheet_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    hints: Mapped[int] = mapped_column(default=0)


class PaperAnswerIn(BaseModel):
    answers: dict[int, Any]


STORY_NAMES = ['Mary', 'Margaret', 'Sienna', 'Ruby', 'Mia', 'Chloe', 'Olivia', 'Jack']
STORY_OBJECTS = ['cupcake', 'pizza', 'chocolate bar', 'ribbon', 'water bottle', 'garden bed']


def _fraction_story(level: int, rng: Any):
    a_num, a_den = rng.choice([(1,2),(2,3),(3,4),(3,5),(4,5)])
    b_num, b_den = rng.choice([(1,3),(2,5),(2,3),(3,4),(4,5)])
    while a_num * b_den == b_num * a_den:
        b_num, b_den = rng.choice([(1,3),(2,5),(2,3),(3,4),(4,5)])
    first, second = rng.sample(STORY_NAMES, 2)
    item = rng.choice(STORY_OBJECTS)
    answer = first if a_num * b_den > b_num * a_den else second
    prompt = f'{first} has {a_num}/{a_den} of a {item}. {second} has {b_num}/{b_den} of a {item}. Who has more?'
    payload = {
        'choices': [first, second],
        'visual': {
            'type': 'fraction_compare',
            'items': [
                {'label': first, 'numerator': a_num, 'denominator': a_den},
                {'label': second, 'numerator': b_num, 'denominator': b_den},
            ],
        },
        'story': True,
    }
    working = f'Compare {a_num}/{a_den} and {b_num}/{b_den}. The larger fraction belongs to {answer}.'
    return legacy.q('VC2M4N03', 'fraction_story_compare', prompt, 'choice', payload, answer, working)


def _visual_number_line(rng: Any):
    denominator = rng.choice([4,5,8,10])
    numerator = rng.randint(1, denominator - 1)
    prompt = f'Select the point that represents {numerator}/{denominator} on the number line.'
    payload = {'visual': {'type': 'number_line', 'min': 0, 'max': 1, 'steps': denominator, 'target': numerator}, 'choices': [str(x) for x in range(denominator + 1)]}
    return legacy.q('VC2M4N04', 'visual_number_line', prompt, 'choice', payload, str(numerator), f'{numerator}/{denominator} is {numerator} equal steps from 0 when the line is divided into {denominator} parts.')


def _visual_clock(rng: Any):
    hour = rng.randint(1, 12); minute = rng.choice([0, 15, 30, 45])
    display = f'{hour}:{minute:02d}'
    prompt = 'What time is shown on the analogue clock?'
    payload = {'visual': {'type': 'clock', 'hour': hour, 'minute': minute}, 'choices': [display, f'{(hour%12)+1}:{minute:02d}', f'{hour}:{(minute+15)%60:02d}']}
    return legacy.q('VC2M4M03', 'visual_clock', prompt, 'choice', payload, display, f'The short hand shows {hour}; the long hand shows {minute} minutes.')


def _visual_angle(rng: Any):
    angle, name = rng.choice([(45,'acute'),(90,'right'),(120,'obtuse'),(180,'straight')])
    payload = {'visual': {'type': 'angle', 'degrees': angle}, 'choices': ['acute','right','obtuse','straight']}
    return legacy.q('VC2M4M04', 'visual_angle', 'What type of angle is shown?', 'choice', payload, name, f'{angle}° is a {name} angle.')


def _visual_bar_chart(rng: Any):
    labels = ['Apples','Bananas','Pears','Oranges']
    values = [rng.randint(2,9) for _ in labels]
    top = max(range(len(values)), key=values.__getitem__)
    payload = {'visual': {'type': 'bar_chart', 'labels': labels, 'values': values}, 'choices': labels}
    return legacy.q('VC2M4ST02', 'visual_bar_chart', 'Which fruit has the highest value on the chart?', 'choice', payload, labels[top], 'Find the tallest bar and read its label.')


def _visual_grid(rng: Any):
    column = rng.choice(['A','B','C','D']); row = rng.randint(1,4)
    payload = {'visual': {'type': 'grid', 'columns': ['A','B','C','D'], 'rows': 4, 'target': f'{column}{row}'}, 'choices': [f'{c}{r}' for c in ['A','B','C','D'] for r in range(1,5)]}
    return legacy.q('VC2M4SP03', 'visual_grid', 'Which grid reference contains the highlighted square?', 'choice', payload, f'{column}{row}', 'Read the column letter first, then the row number.')


def make_question_v080(topic: str, level: int, rng: Any):
    roll = rng.random()
    if topic == 'number' and roll < 0.22:
        return _fraction_story(level, rng)
    if topic == 'number' and roll < 0.38:
        return _visual_number_line(rng)
    if topic == 'measurement' and roll < 0.18:
        return _visual_clock(rng)
    if topic == 'measurement' and roll < 0.34:
        return _visual_angle(rng)
    if topic == 'statistics' and roll < 0.30:
        return _visual_bar_chart(rng)
    if topic == 'space' and roll < 0.28:
        return _visual_grid(rng)
    return _original_make_question(topic, level, rng)


legacy.make_question = make_question_v080


@app.on_event('startup')
def create_v080_tables():
    legacy.Base.metadata.create_all(legacy.engine)


@app.get('/api/assignments/all')
def assignments_all(_=Depends(legacy.parent), session: Session = Depends(legacy.db)):
    student = session.scalar(select(legacy.User).where(legacy.User.role == 'student'))
    rows = session.scalars(select(v070.Assignment).where(v070.Assignment.student_id == student.id).order_by(v070.Assignment.created_at.desc())).all()
    result=[]
    for row in rows:
        progress=session.scalar(select(AssignmentProgress).where(AssignmentProgress.assignment_id==row.id,AssignmentProgress.student_id==student.id))
        status=progress.status if progress else ('overdue' if row.due_date and row.due_date < date.today() else 'assigned')
        result.append({'id':row.id,'title':row.title,'topics':legacy.json.loads(row.topics),'question_count':row.question_count,'due_date':row.due_date.isoformat() if row.due_date else None,'active':row.active,'status':status,'score':progress.score if progress else 0,'total':progress.total if progress else row.question_count,'hints':progress.hints if progress else 0})
    return result


@app.post('/api/assignments/{assignment_id}/start')
def start_assignment(assignment_id:int,user:legacy.User=Depends(legacy.current_user),session:Session=Depends(legacy.db)):
    if user.role!='student': raise HTTPException(403,'Student access required')
    assignment=session.get(v070.Assignment,assignment_id)
    if not assignment or assignment.student_id!=user.id or not assignment.active: raise HTTPException(404,'Assignment not found')
    progress=session.scalar(select(AssignmentProgress).where(AssignmentProgress.assignment_id==assignment.id,AssignmentProgress.student_id==user.id))
    if not progress:
        progress=AssignmentProgress(assignment_id=assignment.id,student_id=user.id,status='in_progress',started_at=datetime.utcnow(),total=assignment.question_count)
        session.add(progress)
    else:
        progress.status='in_progress'; progress.started_at=progress.started_at or datetime.utcnow()
    session.commit()
    return {'id':assignment.id,'status':progress.status,'topics':legacy.json.loads(assignment.topics),'question_count':assignment.question_count}


@app.post('/api/assignments/from-insight')
def assignment_from_insight(payload:v070.AssignmentIn,_=Depends(legacy.parent),session:Session=Depends(legacy.db)):
    return v070.create_assignment(payload,_,session)


@app.post('/api/worksheets/{worksheet_id}/paper-answers')
def paper_answers(worksheet_id:int,payload:PaperAnswerIn,_=Depends(legacy.parent),session:Session=Depends(legacy.db)):
    worksheet=session.get(legacy.Worksheet,worksheet_id)
    if not worksheet: raise HTTPException(404,'Worksheet not found')
    student=session.get(legacy.User,worksheet.student_id)
    entered=0; correct=0
    for question in worksheet.questions:
        if question.id not in payload.answers: continue
        entered+=1
        answer=str(payload.answers[question.id]).strip()
        is_correct=answer.lower()==str(question.correct_answer).strip().lower()
        session.add(legacy.Attempt(question_id=question.id,student_id=student.id,answer=answer,correct=is_correct,attempt_number=len(question.attempts)+1,seconds=0))
        question.answered_at=datetime.utcnow(); question.state='correct' if is_correct else 'incorrect'
        if is_correct: correct+=1
    worksheet.score=sum(1 for q in worksheet.questions if any(a.correct for a in q.attempts))
    worksheet.status='completed' if entered==worksheet.total else 'in_progress'
    if worksheet.status=='completed' and not worksheet.completed_at: worksheet.completed_at=datetime.utcnow()
    session.commit()
    return {'entered':entered,'correct':correct,'score':worksheet.score,'total':worksheet.total,'status':worksheet.status}


@app.get('/api/question-formats')
def question_formats(_:legacy.User=Depends(legacy.current_user)):
    return {'visual':['fraction_compare','number_line','clock','angle','bar_chart','grid'],'storytelling':True,'version':'0.8.0'}
