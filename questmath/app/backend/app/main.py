from __future__ import annotations

import csv
import io
import json
import logging
import os
import random
import shutil
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from .auth_security import LoginRateLimiter
from .security import load_signing_secret

DATA_DIR = Path(os.getenv('QUESTMATH_DATA_DIR', '/data'))
BACKUP_DIR = Path(os.getenv('QUESTMATH_BACKUP_DIR', str(DATA_DIR / 'backups')))
DB_PATH = DATA_DIR / 'questmath.db'
DATA_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)
SECRET_KEY = load_signing_secret(DATA_DIR)
ALGORITHM = 'HS256'
APP_VERSION = '0.16.3'
logger = logging.getLogger('mathquest.security')
login_rate_limiter = LoginRateLimiter()

LEVEL4_STRANDS = ['number','algebra','measurement','space','statistics','probability']
LEVEL4_OUTCOMES = {
    'VC2M4N01': ('Number', 'Decimals: tenths and hundredths'),
    'VC2M4N02': ('Number', 'Sequences and multiples'),
    'VC2M4N03': ('Number', 'Equivalent fractions and decimals'),
    'VC2M4N04': ('Number', 'Fractions on number lines'),
    'VC2M4N05': ('Number', 'Multiply and divide by powers of 10'),
    'VC2M4N06': ('Number', 'Efficient calculation strategies'),
    'VC2M4N07': ('Number', 'Estimation and reasonableness'),
    'VC2M4N08': ('Number', 'Purchases and change'),
    'VC2M4N09': ('Number', 'Mathematical modelling'),
    'VC2M4N10': ('Number', 'Algorithms and patterns'),
    'VC2M4A01': ('Algebra', 'Unknown values in equations'),
    'VC2M4A02': ('Algebra', 'Multiplication and related division facts'),
    'VC2M4M01': ('Measurement', 'Scaled instruments and units'),
    'VC2M4M02': ('Measurement', 'Perimeter and area'),
    'VC2M4M03': ('Measurement', 'Duration and time conversion'),
    'VC2M4M04': ('Measurement', 'Angles relative to a right angle'),
    'VC2M4SP01': ('Space', 'Properties of shapes and objects'),
    'VC2M4SP02': ('Space', 'Composite shapes and objects'),
    'VC2M4SP03': ('Space', 'Grid references and directions'),
    'VC2M4SP04': ('Space', 'Line and rotational symmetry'),
    'VC2M4ST01': ('Statistics', 'Collect and represent data'),
    'VC2M4ST02': ('Statistics', 'Compare data displays'),
    'VC2M4ST03': ('Statistics', 'Statistical investigations'),
    'VC2M4P01': ('Probability', 'Likelihood and dependent events'),
    'VC2M4P02': ('Probability', 'Repeated chance experiments'),
}

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__='users'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))
    display_name: Mapped[str] = mapped_column(String(80))
    xp: Mapped[int] = mapped_column(default=0)
    highest_level: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Setting(Base):
    __tablename__='settings'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), unique=True)
    question_count: Mapped[int] = mapped_column(default=20)
    adaptive_mode: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled_topics: Mapped[str] = mapped_column(Text, default='["number","algebra","measurement","space","statistics","probability"]')
    manual_levels: Mapped[str] = mapped_column(Text, default='{}')
    theme: Mapped[str] = mapped_column(String(30), default='aurora')

class Skill(Base):
    __tablename__='skills'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    topic: Mapped[str] = mapped_column(String(40), index=True)
    level: Mapped[int] = mapped_column(default=1)
    highest_level: Mapped[int] = mapped_column(default=1)
    rolling_accuracy: Mapped[float] = mapped_column(Float, default=0)
    avg_seconds: Mapped[float] = mapped_column(Float, default=0)
    attempts: Mapped[int] = mapped_column(default=0)

class Worksheet(Base):
    __tablename__='worksheets'
    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    worksheet_date: Mapped[date] = mapped_column(Date, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    score: Mapped[int] = mapped_column(default=0)
    total: Mapped[int] = mapped_column(default=0)
    xp_earned: Mapped[int] = mapped_column(default=0)
    current_question_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_phase: Mapped[str] = mapped_column(String(20), default='main')
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    elapsed_seconds: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default='in_progress')
    selected_topic: Mapped[str] = mapped_column(String(40), default='mixed')
    questions: Mapped[list['Question']] = relationship(cascade='all, delete-orphan')

class Question(Base):
    __tablename__='questions'
    id: Mapped[int] = mapped_column(primary_key=True)
    worksheet_id: Mapped[int] = mapped_column(ForeignKey('worksheets.id'), index=True)
    topic: Mapped[str] = mapped_column(String(40))
    skill: Mapped[str] = mapped_column(String(60))
    level: Mapped[int] = mapped_column(default=1)
    prompt: Mapped[str] = mapped_column(Text)
    answer_type: Mapped[str] = mapped_column(String(30))
    payload: Mapped[str] = mapped_column(Text)
    correct_answer: Mapped[str] = mapped_column(Text)
    working: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column()
    state: Mapped[str] = mapped_column(String(30), default='not_started')
    skipped_count: Mapped[int] = mapped_column(default=0)
    hint_count: Mapped[int] = mapped_column(default=0)
    first_viewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    attempts: Mapped[list['Attempt']] = relationship(cascade='all, delete-orphan')
    hints: Mapped[list['HintEvent']] = relationship(cascade='all, delete-orphan')

class Attempt(Base):
    __tablename__='attempts'
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    answer: Mapped[str] = mapped_column(Text)
    correct: Mapped[bool] = mapped_column(Boolean)
    attempt_number: Mapped[int] = mapped_column(default=1)
    seconds: Mapped[float] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class HintEvent(Base):
    __tablename__='hint_events'
    id: Mapped[int] = mapped_column(primary_key=True)
    question_id: Mapped[int] = mapped_column(ForeignKey('questions.id'), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    topic: Mapped[str] = mapped_column(String(40), index=True)
    hint_number: Mapped[int] = mapped_column(default=1)
    hint_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

engine=create_engine(f'sqlite:///{DB_PATH}', connect_args={'check_same_thread':False})
SessionLocal=sessionmaker(engine, expire_on_commit=False)
pwd=CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2=OAuth2PasswordBearer(tokenUrl='api/auth/login')
app=FastAPI(title='MathQuest', version=APP_VERSION)

class AnswerIn(BaseModel): answer: Any; seconds: float = 0
class WorksheetCreateIn(BaseModel): topic: str = 'mixed'
class SettingsIn(BaseModel): question_count:int=20; adaptive_mode:bool=True; enabled_topics:list[str]; manual_levels:dict[str,int]={}; theme:str='aurora'
class NavigateIn(BaseModel): elapsed_seconds: float = 0
class CustomQuestionIn(BaseModel): topic:str; skill:str='custom'; level:int=1; prompt:str; answer_type:str='text'; payload:dict[str,Any]={}; correct_answer:str; working:str

def db():
    s=SessionLocal()
    try: yield s
    finally: s.close()

def token_for(u:User): return jwt.encode({'sub':str(u.id),'role':u.role,'exp':datetime.now(timezone.utc)+timedelta(hours=24)}, SECRET_KEY, algorithm=ALGORITHM)
def current_user(token:str=Depends(oauth2), s:Session=Depends(db)):
    try: uid=int(jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])['sub'])
    except (JWTError,KeyError,ValueError): raise HTTPException(401,'Invalid session')
    u=s.get(User,uid)
    if not u: raise HTTPException(401,'User not found')
    return u
def parent(u:User=Depends(current_user)):
    if u.role!='parent': raise HTTPException(403,'Parent access required')
    return u

def migrate_database():
    additions = {
        'worksheets': [
            ('current_question_id', 'INTEGER'), ('current_phase', "VARCHAR(20) DEFAULT 'main'"),
            ('last_active_at', 'DATETIME'), ('elapsed_seconds', 'FLOAT DEFAULT 0'),
            ('status', "VARCHAR(20) DEFAULT 'in_progress'"),
            ('selected_topic', "VARCHAR(40) DEFAULT 'mixed'")
        ],
        'questions': [
            ('state', "VARCHAR(30) DEFAULT 'not_started'"), ('skipped_count', 'INTEGER DEFAULT 0'),
            ('hint_count', 'INTEGER DEFAULT 0'), ('first_viewed_at', 'DATETIME'), ('answered_at', 'DATETIME')
        ]
    }
    with sqlite3.connect(DB_PATH) as conn:
        for table, columns in additions.items():
            existing = {row[1] for row in conn.execute(f'PRAGMA table_info({table})')}
            for name, definition in columns:
                if name not in existing:
                    conn.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')
        conn.commit()

def seed():
    Base.metadata.create_all(engine)
    migrate_database()
    with SessionLocal() as s:
        if not s.scalar(select(User).where(User.username==os.getenv('PARENT_USERNAME','parent'))):
            s.add(User(username=os.getenv('PARENT_USERNAME','parent'),password_hash=pwd.hash(os.getenv('PARENT_PASSWORD','ChangeMeParent!')),role='parent',display_name='Parent'))
        student=s.scalar(select(User).where(User.username==os.getenv('STUDENT_USERNAME','student')))
        if not student:
            student=User(username=os.getenv('STUDENT_USERNAME','student'),password_hash=pwd.hash(os.getenv('STUDENT_PASSWORD','ChangeMeStudent!')),role='student',display_name=os.getenv('STUDENT_DISPLAY_NAME','Math Explorer'))
            s.add(student); s.flush(); s.add(Setting(student_id=student.id))
            for t in LEVEL4_STRANDS: s.add(Skill(student_id=student.id,topic=t))
        if student:
            st=s.scalar(select(Setting).where(Setting.student_id==student.id))
            if st:
                try: current=json.loads(st.enabled_topics)
                except Exception: current=[]
                if set(current).issubset({'multiplication','fractions','measurement'}) or not current:
                    st.enabled_topics=json.dumps(LEVEL4_STRANDS)
            existing={x.topic for x in s.scalars(select(Skill).where(Skill.student_id==student.id)).all()}
            for strand in LEVEL4_STRANDS:
                if strand not in existing: s.add(Skill(student_id=student.id,topic=strand))
        s.commit()

@app.on_event('startup')
def startup(): seed()

@app.get('/api/health')
def health(): return {'ok':True,'version':APP_VERSION}
@app.post('/api/auth/login')
def login(request:Request, form:OAuth2PasswordRequestForm=Depends(), s:Session=Depends(db)):
    client_host = request.client.host if request.client else None
    key = login_rate_limiter.key(client_host, form.username)
    retry_after = login_rate_limiter.retry_after(key)
    if retry_after:
        logger.warning('security_event=login_rate_limited client=%s retry_after=%s', client_host or 'unknown', retry_after)
        raise HTTPException(429, 'Too many login attempts. Try again later.', headers={'Retry-After':str(retry_after)})
    u=s.scalar(select(User).where(User.username==form.username))
    if not u or not pwd.verify(form.password,u.password_hash):
        login_rate_limiter.record_failure(key)
        logger.warning('security_event=login_failed client=%s', client_host or 'unknown')
        raise HTTPException(401,'Invalid username or password')
    login_rate_limiter.record_success(key)
    logger.info('security_event=login_succeeded client=%s', client_host or 'unknown')
    return {'access_token':token_for(u),'token_type':'bearer','user':user_view(u)}
@app.get('/api/me')
def me(u:User=Depends(current_user)): return user_view(u)

def user_view(u): return {'id':u.id,'username':u.username,'role':u.role,'display_name':u.display_name,'xp':u.xp,'level':u.xp//250+1,'highest_level':u.highest_level}

def frac(n,d):
    from math import gcd
    g=gcd(n,d); return f'{n//g}/{d//g}'
def q(code, skill, prompt, answer_type, payload, answer, working):
    return (f'{code}:{skill}', prompt, answer_type, payload, str(answer), working)

def make_question(topic:str, level:int, rng:random.Random):
    if topic == 'number':
        code = rng.choice(['VC2M4N01','VC2M4N02','VC2M4N03','VC2M4N04','VC2M4N05','VC2M4N06','VC2M4N07','VC2M4N08','VC2M4N09','VC2M4N10'])
        if code == 'VC2M4N01':
            whole=rng.randint(0,99); tenths=rng.randint(0,9); hundredths=rng.randint(0,9); value=f'{whole}.{tenths}{hundredths}'
            return q(code,'decimal_place_value',f'What digit is in the hundredths place in {value}?','number',{},hundredths,f'In {value}, the second digit after the decimal point is the hundredths digit.')
        if code == 'VC2M4N02':
            multiple=rng.choice([3,4,6,7,8,9]); start=multiple*rng.randint(1,6)
            return q(code,'number_sequences',f'Continue the sequence: {start}, {start+multiple}, {start+2*multiple}, __','number',{},start+3*multiple,f'The sequence increases by {multiple} each time.')
        if code == 'VC2M4N03':
            d=rng.choice([2,4,5,10]); n=rng.randint(1,d-1); k=rng.choice([2,3])
            return q(code,'equivalent_fractions',f'Complete the equivalent fraction: {n}/{d} = __/{d*k}','number',{},n*k,f'Multiply the numerator and denominator by {k}.')
        if code == 'VC2M4N04':
            d=rng.choice([2,3,4]); whole=rng.randint(0,2); n=rng.randint(1,d-1); improper=whole*d+n
            return q(code,'fraction_number_line',f'Write {whole} {n}/{d} as an improper fraction.','text',{},f'{improper}/{d}',f'{whole} wholes are {whole*d}/{d}; add {n}/{d} to get {improper}/{d}.')
        if code == 'VC2M4N05':
            a=rng.randint(12,999); factor=rng.choice([10,100,1000]); op=rng.choice(['multiply','divide'])
            if op=='multiply': return q(code,'powers_of_ten',f'Calculate {a} × {factor}.','number',{},a*factor,f'Multiplying by {factor} shifts every digit {len(str(factor))-1} places to the left.')
            value=a*factor; return q(code,'powers_of_ten',f'Calculate {value} ÷ {factor}.','number',{},a,f'Dividing by {factor} shifts every digit {len(str(factor))-1} places to the right.')
        if code == 'VC2M4N06':
            if rng.random()<.5:
                a,b=rng.randint(100,999),rng.randint(100,999); return q(code,'efficient_add_subtract',f'Calculate {a} + {b}.','number',{},a+b,f'Partition by place value or use a written addition strategy: {a}+{b}={a+b}.')
            a,b=rng.randint(12,99),rng.randint(2,10); return q(code,'efficient_multiply_divide',f'Calculate {a} × {b}.','number',{},a*b,f'Use partitioning: ({a//10*10} × {b}) + ({a%10} × {b}) = {a*b}.')
        if code == 'VC2M4N07':
            a,b=rng.randint(120,980),rng.randint(120,980); exact=a+b; estimate=round(a,-2)+round(b,-2)
            return q(code,'estimation_reasonableness',f'Estimate {a} + {b} by rounding each number to the nearest hundred.','number',{},estimate,f'{a} rounds to {round(a,-2)} and {b} rounds to {round(b,-2)}, so the estimate is {estimate}. The exact answer is {exact}.')
        if code == 'VC2M4N08':
            price_cents=rng.randrange(105,3000,5); paid=rng.choice([2000,5000]); paid=max(paid, ((price_cents+499)//500)*500); change=paid-price_cents
            return q(code,'money_change',f'An item costs ${price_cents/100:.2f}. You pay ${paid/100:.2f}. How much change should you receive?','money',{'currency':'AUD'},f'{change/100:.2f}',f'${paid/100:.2f} − ${price_cents/100:.2f} = ${change/100:.2f}.')
        if code == 'VC2M4N09':
            packs,each,extra=rng.randint(2,8),rng.randint(5,24),rng.randint(1,20); ans=packs*each+extra
            return q(code,'mathematical_modelling',f'Sienna has {packs} packs of {each} beads and {extra} loose beads. How many beads altogether?','number',{},ans,f'Model it as ({packs} × {each}) + {extra} = {ans}.')
        start=rng.randint(1,20); add=rng.randint(2,9); third=start+2*add
        return q(code,'algorithms_patterns',f'A rule says “add {add}”. Starting at {start}, what is the fourth number generated?','number',{},start+3*add,f'Apply the rule three times: {start}, {start+add}, {third}, {start+3*add}.')

    if topic == 'algebra':
        code=rng.choice(['VC2M4A01','VC2M4A02'])
        if code=='VC2M4A01':
            x=rng.randint(10,90); b=rng.randint(5,40); return q(code,'unknown_add_subtract',f'Find the missing number: □ + {b} = {x+b}','number',{},x,f'Use the inverse operation: {x+b} − {b} = {x}.')
        a,b=rng.randint(2,10),rng.randint(2,10); product=a*b
        return q(code,'fact_families',f'If {a} × {b} = {product}, what is {product} ÷ {a}?','number',{},b,f'Multiplication and division are inverse operations, so {product} ÷ {a} = {b}.')

    if topic == 'measurement':
        code=rng.choice(['VC2M4M01','VC2M4M02','VC2M4M03','VC2M4M04'])
        if code=='VC2M4M01':
            context,answer=rng.choice([('length of a pencil','centimetres'),('mass of an apple','grams'),('capacity of a drink bottle','millilitres'),('room temperature','degrees Celsius')])
            choices=['millimetres','centimetres','metres','grams','kilograms','millilitres','litres','degrees Celsius']
            return q(code,'choose_measurement_unit',f'Which unit is most appropriate for measuring the {context}?','choice',{'choices':rng.sample([x for x in choices if x!=answer],2)+[answer]},answer,f'{answer} is an appropriate practical unit for the {context}.')
        if code=='VC2M4M02':
            a,b=rng.randint(3,20),rng.randint(3,20); mode=rng.choice(['perimeter','area']); ans=2*(a+b) if mode=='perimeter' else a*b
            return q(code,mode,f'A rectangle is {a} cm by {b} cm. What is its {mode}?','number',{'unit':'cm' if mode=='perimeter' else 'cm²'},ans,f'{mode.title()} = '+(f'2 × ({a}+{b}) = {ans} cm.' if mode=='perimeter' else f'{a} × {b} = {ans} cm².'))
        if code=='VC2M4M03':
            hours=rng.randint(1,3); minutes=rng.choice([15,30,45]); total=hours*60+minutes
            return q(code,'duration_conversion',f'How many minutes are in {hours} hours and {minutes} minutes?','number',{'unit':'minutes'},total,f'{hours} hours = {hours*60} minutes; add {minutes} to get {total}.')
        angle,answer=rng.choice([(35,'acute'),(90,'right'),(125,'obtuse'),(180,'straight'),(240,'reflex'),(360,'revolution')])
        return q(code,'angle_names',f'What type of angle is {angle}°?','choice',{'choices':['acute','right','obtuse','straight','reflex','revolution']},answer,f'A {angle}° angle is a {answer} angle.')

    if topic == 'space':
        code=rng.choice(['VC2M4SP01','VC2M4SP02','VC2M4SP03','VC2M4SP04'])
        if code=='VC2M4SP01':
            shape,answer=rng.choice([('cube','6 square faces'),('triangular prism','2 triangular and 3 rectangular faces'),('cylinder','2 circular faces and 1 curved surface')])
            return q(code,'shape_properties',f'Which description matches a {shape}?','choice',{'choices':[answer,'4 equal triangular faces','1 square face and 4 triangular faces']},answer,f'A {shape} has {answer}.')
        if code=='VC2M4SP02':
            return q(code,'composite_shapes','A house picture is made from a rectangle with a triangle on top. How many basic shapes make the composite shape?','number',{},2,'The composite shape combines one rectangle and one triangle.')
        if code=='VC2M4SP03':
            col=rng.choice(['A','B','C','D','E']); row=rng.randint(1,6)
            return q(code,'grid_references',f'A treasure is at column {col}, row {row}. Write its grid reference.','text',{},f'{col}{row}',f'Grid references name the column first, then the row: {col}{row}.')
        sides=rng.choice([3,4,5,6,8]); answer='yes'
        return q(code,'rotational_symmetry',f'Does a regular {sides}-sided polygon have rotational symmetry?','choice',{'choices':['yes','no']},answer,'A regular polygon matches itself during a turn smaller than one full revolution.')

    if topic == 'statistics':
        code=rng.choice(['VC2M4ST01','VC2M4ST02','VC2M4ST03'])
        data=[rng.randint(1,6) for _ in range(6)]; mode=max(set(data),key=data.count)
        if code=='VC2M4ST01':
            return q(code,'data_frequency',f'The survey results are {data}. Which value occurs most often?','number',{},mode,f'Count each value. {mode} has the greatest frequency.')
        if code=='VC2M4ST02':
            return q(code,'choose_data_display','Which display is usually best for comparing the number of students choosing different favourite sports?','choice',{'choices':['column graph','line graph over time','clock face']},'column graph','A column graph clearly compares frequencies across categories.')
        return q(code,'statistical_investigation','Which question is suitable for a class survey?','choice',{'choices':['What is every student’s favourite fruit?','What will happen exactly next year?','Is 7 × 8 equal to 56?']},'What is every student’s favourite fruit?','A statistical question anticipates varied responses that can be collected and analysed.')

    code=rng.choice(['VC2M4P01','VC2M4P02'])
    if code=='VC2M4P01':
        return q(code,'likelihood',"A bag has 8 blue counters and 2 red counters. Which colour is more likely to be selected?",'choice',{'choices':['blue','red','equally likely']},'blue','There are more blue counters than red counters, so blue is more likely.')
    heads=rng.randint(35,65); tails=100-heads
    return q(code,'chance_variation',f'A coin was tossed 100 times: {heads} heads and {tails} tails. Is variation from exactly 50 each normal?','choice',{'choices':['yes','no']},'yes','Repeated chance experiments vary. Results often approach the expected proportion but need not be exact.')

def student_settings(s, sid):
    st=s.scalar(select(Setting).where(Setting.student_id==sid))
    if not st: st=Setting(student_id=sid);s.add(st);s.commit()
    return st

def weights(s,sid,topics):
    out=[]
    for t in topics:
        sk=s.scalar(select(Skill).where(Skill.student_id==sid,Skill.topic==t))
        acc=sk.rolling_accuracy if sk and sk.attempts else .65
        out.append(max(.25,1.35-acc))
    return out

def question_identity(prompt:str, payload:dict[str,Any]) -> tuple[str,tuple[str,...]]:
    choices=payload.get('choices') if isinstance(payload,dict) else None
    choice_key=tuple(sorted(str(value).strip().casefold() for value in choices)) if isinstance(choices,list) else ()
    return (' '.join((prompt or '').split()).casefold(),choice_key)

def create_worksheet(s:Session,sid:int,selected:str) -> Worksheet:
    st=student_settings(s,sid); enabled=json.loads(st.enabled_topics); levels=json.loads(st.manual_levels)
    selected=(selected or 'mixed').lower()
    if selected!='mixed' and selected not in LEVEL4_STRANDS: raise HTTPException(400,'Unknown learning area')
    if selected!='mixed' and selected not in enabled: raise HTTPException(400,'This learning area is disabled by the parent')
    topics=enabled if selected=='mixed' else [selected]
    if not topics: raise HTTPException(400,'No learning areas are enabled')
    rng=random.Random(f'{sid}:{date.today().isoformat()}:{selected}:{random.SystemRandom().randint(1,10**9)}')
    ws=Worksheet(student_id=sid,worksheet_date=date.today(),total=st.question_count,selected_topic=selected);s.add(ws);s.flush()
    topic_weights=weights(s,sid,topics); seen:set[tuple[str,tuple[str,...]]]=set()
    for pos in range(st.question_count):
        candidate=None
        for _ in range(50):
            topic=rng.choices(topics,weights=topic_weights,k=1)[0]
            sk=s.scalar(select(Skill).where(Skill.student_id==sid,Skill.topic==topic))
            lvl=(sk.level if sk else 1) if st.adaptive_mode else levels.get(topic,1)
            if rng.random()<.2: lvl=max(1,lvl-1)
            skill,prompt,atype,payload,ans,working=make_question(topic,min(4,lvl),rng)
            key=question_identity(prompt,payload)
            if key not in seen:
                candidate=(topic,lvl,skill,prompt,atype,payload,ans,working,key)
                break
        if candidate is None:
            break
        topic,lvl,skill,prompt,atype,payload,ans,working,key=candidate;seen.add(key)
        item=Question(worksheet_id=ws.id,topic=topic,skill=skill,level=lvl,prompt=prompt,answer_type=atype,payload=json.dumps(payload),correct_answer=ans,working=working,position=pos)
        s.add(item);s.flush()
        if pos==0:
            item.state='active';item.first_viewed_at=datetime.utcnow();ws.current_question_id=item.id
    ws.total=len(seen)
    if not ws.total:
        s.rollback()
        raise HTTPException(503,'Unable to generate a unique worksheet from the enabled learning areas')
    ws.last_active_at=datetime.utcnow();s.commit();s.refresh(ws);return ws

@app.post('/api/worksheets/today')
def today_ws(selection:WorksheetCreateIn, u:User=Depends(current_user), s:Session=Depends(db)):
    if u.role!='student': raise HTTPException(403,'Student access required')
    existing=s.scalar(select(Worksheet).where(Worksheet.student_id==u.id,Worksheet.worksheet_date==date.today()))
    if existing: return worksheet_view(existing)
    return worksheet_view(create_worksheet(s,u.id,selection.topic))

@app.get('/api/worksheets/today')
def get_today(u:User=Depends(current_user),s:Session=Depends(db)):
    ws=s.scalar(select(Worksheet).where(Worksheet.student_id==u.id,Worksheet.worksheet_date==date.today()))
    return worksheet_view(ws) if ws else None

def question_status(q):
    attempts=sorted(q.attempts,key=lambda a:a.attempt_number)
    if any(a.correct for a in attempts): return 'correct'
    if len(attempts)>=2: return 'incorrect'
    if q.state=='skipped': return 'skipped'
    if q.state=='active': return 'current'
    if attempts: return 'retry_available'
    return 'not_started'

def worksheet_view(ws):
    questions=sorted(ws.questions,key=lambda x:x.position)
    statuses={q.id:question_status(q) for q in questions}
    return {
        'id':ws.id,'date':ws.worksheet_date.isoformat(),'completed_at':ws.completed_at.isoformat() if ws.completed_at else None,
        'score':ws.score,'total':ws.total,'xp_earned':ws.xp_earned,'current_question_id':ws.current_question_id,
        'current_phase':ws.current_phase or 'main','elapsed_seconds':ws.elapsed_seconds or 0,'status':ws.status or 'in_progress',
        'selected_topic':getattr(ws,'selected_topic','mixed') or 'mixed',
        'counts':{
            'correct':sum(v=='correct' for v in statuses.values()),'incorrect':sum(v=='incorrect' for v in statuses.values()),
            'skipped':sum(v=='skipped' for v in statuses.values()),
            'remaining':sum(v in ('not_started','current','retry_available','skipped') for v in statuses.values()),
            'hints':sum(getattr(q,'hint_count',0) or 0 for q in questions)
        },
        'questions':[{
            'id':q.id,'topic':q.topic,'skill':q.skill,'level':q.level,'prompt':q.prompt,
            'summary':q.prompt if len(q.prompt)<=55 else q.skill.replace('_',' ').title(),
            'answer_type':q.answer_type,'payload':json.loads(q.payload),'position':q.position,
            'status':statuses[q.id],'skipped_count':q.skipped_count or 0,'hint_count':getattr(q,'hint_count',0) or 0,
            'last_hint':sorted(q.hints,key=lambda h:h.hint_number)[-1].hint_text if q.hints else None,
            'attempts':[{'answer':a.answer,'correct':a.correct,'attempt_number':a.attempt_number} for a in sorted(q.attempts,key=lambda a:a.attempt_number)]
        } for q in questions]
    }

def normalise(v): return str(v).strip().lower().replace('$','').replace(',','')

def hint_text(q:Question, hint_number:int) -> str:
    working=(q.working or '').strip()
    first=working.split(';',1)[0].split('.',1)[0].strip()
    if hint_number == 1:
        if ':' in q.skill:
            skill=q.skill.split(':',1)[1].replace('_',' ')
            return f'Think about the {skill}. {first}.' if first else f'Think about the {skill} and identify the first operation or comparison you need.'
        return first + '.' if first else 'Identify what the question is asking, then choose the first operation or comparison you need.'
    if working:
        safe=working
        answer=str(q.correct_answer).strip()
        if answer:
            safe=safe.replace(answer,'the result')
        return f'Break it into smaller steps: {safe}'
    return 'Break the problem into smaller steps and check each step before moving to the next one.'

@app.post('/api/questions/{qid}/hint')
def request_hint(qid:int,u:User=Depends(current_user),s:Session=Depends(db)):
    if u.role!='student': raise HTTPException(403,'Student access required')
    q=s.get(Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    ws=s.get(Worksheet,q.worksheet_id)
    if not ws or ws.student_id!=u.id: raise HTTPException(403,'Question does not belong to this student')
    if question_status(q) in ('correct','incorrect'): raise HTTPException(400,'Completed questions do not need hints')
    next_number=(q.hint_count or 0)+1
    if next_number>2:
        last=sorted(q.hints,key=lambda h:h.hint_number)[-1] if q.hints else None
        return {'hint':last.hint_text if last else hint_text(q,2),'hint_count':q.hint_count or 0,'more_available':False}
    text=hint_text(q,next_number)
    q.hint_count=next_number
    s.add(HintEvent(question_id=q.id,student_id=u.id,topic=q.topic,hint_number=next_number,hint_text=text))
    ws.last_active_at=datetime.utcnow(); s.commit()
    return {'hint':text,'hint_count':next_number,'more_available':next_number<2}

@app.post('/api/questions/{qid}/answer')
def answer(qid:int,data:AnswerIn,u:User=Depends(current_user),s:Session=Depends(db)):
    q=s.get(Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    ws=s.get(Worksheet,q.worksheet_id)
    if not ws or ws.student_id!=u.id: raise HTTPException(403,'Question does not belong to this student')
    count=s.scalar(select(func.count(Attempt.id)).where(Attempt.question_id==qid,Attempt.student_id==u.id)) or 0
    if count>=2: raise HTTPException(400,'No attempts remaining')
    correct=normalise(data.answer)==normalise(q.correct_answer)
    s.add(Attempt(question_id=q.id,student_id=u.id,answer=str(data.answer),correct=correct,attempt_number=count+1,seconds=max(0,data.seconds)))
    reveal=correct or count+1>=2
    q.state='answered_correct' if correct else ('answered_incorrect' if reveal else 'active')
    if reveal: q.answered_at=datetime.utcnow()
    ws.last_active_at=datetime.utcnow(); s.commit()
    return {'correct':correct,'attempt_number':count+1,'retry_allowed':not reveal,'correct_answer':q.correct_answer if reveal else None,'working':q.working if reveal else None,'message':'Great job!' if correct else ('Not quite. Try once more.' if not reveal else 'Here is how to solve it.')}

@app.post('/api/questions/{qid}/skip')
def skip_question(qid:int,data:NavigateIn,u:User=Depends(current_user),s:Session=Depends(db)):
    q=s.get(Question,qid)
    if not q: raise HTTPException(404,'Question not found')
    ws=s.get(Worksheet,q.worksheet_id)
    if not ws or ws.student_id!=u.id: raise HTTPException(403,'Question does not belong to this student')
    if question_status(q) in ('correct','incorrect'): raise HTTPException(400,'Completed questions cannot be skipped')
    q.state='skipped'; q.skipped_count=(q.skipped_count or 0)+1
    ws.elapsed_seconds=max(ws.elapsed_seconds or 0,data.elapsed_seconds); ws.last_active_at=datetime.utcnow(); s.commit()
    return worksheet_view(ws)

@app.post('/api/worksheets/{wid}/navigate/{qid}')
def navigate(wid:int,qid:int,data:NavigateIn,u:User=Depends(current_user),s:Session=Depends(db)):
    ws=s.get(Worksheet,wid); q=s.get(Question,qid)
    if not ws or ws.student_id!=u.id or not q or q.worksheet_id!=wid: raise HTTPException(404,'Worksheet question not found')
    if question_status(q) in ('correct','incorrect'): raise HTTPException(400,'Completed questions are read-only')
    for other in ws.questions:
        if other.id!=q.id and other.state=='active' and question_status(other)=='current': other.state='not_started'
    if q.first_viewed_at is None: q.first_viewed_at=datetime.utcnow()
    q.state='active'; ws.current_question_id=q.id
    ws.current_phase='skipped' if all(question_status(x) in ('correct','incorrect','skipped') for x in ws.questions) else 'main'
    ws.elapsed_seconds=max(ws.elapsed_seconds or 0,data.elapsed_seconds); ws.last_active_at=datetime.utcnow(); s.commit(); return worksheet_view(ws)

@app.post('/api/worksheets/{wid}/save')
def save_progress(wid:int,data:NavigateIn,u:User=Depends(current_user),s:Session=Depends(db)):
    ws=s.get(Worksheet,wid)
    if not ws or ws.student_id!=u.id: raise HTTPException(404,'Worksheet not found')
    ws.elapsed_seconds=max(ws.elapsed_seconds or 0,data.elapsed_seconds); ws.last_active_at=datetime.utcnow(); ws.status='in_progress'; s.commit(); return {'ok':True}

@app.post('/api/worksheets/{wid}/complete')
def complete(wid:int,u:User=Depends(current_user),s:Session=Depends(db)):
    ws=s.get(Worksheet,wid)
    if not ws or ws.student_id!=u.id: raise HTTPException(404,'Worksheet not found')
    if ws.completed_at: return summary(s,ws,u)
    unresolved=[q for q in ws.questions if question_status(q) not in ('correct','incorrect')]
    if unresolved: raise HTTPException(400,f'{len(unresolved)} questions still need to be completed')
    score=0; topic_results={}
    for q in ws.questions:
        attempts=sorted(q.attempts,key=lambda a:a.attempt_number); final_correct=any(a.correct for a in attempts)
        score+=int(final_correct); topic_results.setdefault(q.topic,[]).append(final_correct)
    ws.score=score; ws.completed_at=datetime.utcnow(); ws.status='completed'; ws.current_question_id=None
    ws.xp_earned=score*10+(50 if score==ws.total else 0); u.xp+=ws.xp_earned; u.highest_level=max(u.highest_level,u.xp//250+1)
    for topic in topic_results: update_skill(s,u.id,topic)
    s.commit(); return summary(s,ws,u)

def update_skill(s,sid,topic):
    sk=s.scalar(select(Skill).where(Skill.student_id==sid,Skill.topic==topic))
    if not sk: sk=Skill(student_id=sid,topic=topic);s.add(sk);s.flush()
    rows=s.execute(select(Attempt.correct,Attempt.seconds).join(Question).join(Worksheet).where(Attempt.student_id==sid,Question.topic==topic).order_by(Attempt.created_at.desc()).limit(20)).all()
    if not rows:return
    sk.attempts+=len(rows); sk.rolling_accuracy=sum(1 for r in rows if r.correct)/len(rows); sk.avg_seconds=sum(r.seconds for r in rows)/len(rows)
    if len(rows)>=12 and sk.rolling_accuracy>=.85: sk.level=min(8,sk.level+1)
    elif len(rows)>=8 and sk.rolling_accuracy<.70: sk.level=max(1,sk.level-1)
    sk.highest_level=max(sk.highest_level,sk.level)

def summary(s,ws,u):
    by={}
    for q in ws.questions: by.setdefault(q.topic,[]).append(any(a.correct for a in q.attempts))
    rates={k:sum(v)/len(v) for k,v in by.items()}; strongest=max(rates,key=rates.get) if rates else None; weakest=min(rates,key=rates.get) if rates else None
    hints=sum((q.hint_count or 0) for q in ws.questions)
    return {'score':ws.score,'total':ws.total,'accuracy':round(ws.score/ws.total*100) if ws.total else 0,'xp_earned':ws.xp_earned,'level':u.xp//250+1,'level_progress':u.xp%250,'strongest_topic':strongest,'weakest_topic':weakest,'hints_used':hints,'perfect':ws.score==ws.total,'message':'Outstanding work!' if ws.score==ws.total else 'You are getting stronger every day.'}

def streak(s,sid):
    dates=set(s.scalars(select(Worksheet.worksheet_date).where(Worksheet.student_id==sid,Worksheet.completed_at.is_not(None))).all());n=0;d=date.today()
    if d not in dates:d-=timedelta(days=1)
    while d in dates:n+=1;d-=timedelta(days=1)
    return n

def dashboard(s,sid):
    user=s.get(User,sid)
    works=s.scalars(select(Worksheet).where(Worksheet.student_id==sid).order_by(Worksheet.worksheet_date)).all()
    completed=[w for w in works if w.completed_at]
    attempts=s.scalars(select(Attempt).where(Attempt.student_id==sid)).all()
    correct=sum(a.correct for a in attempts)
    skills=s.scalars(select(Skill).where(Skill.student_id==sid)).all()
    hints=s.scalars(select(HintEvent).where(HintEvent.student_id==sid).order_by(HintEvent.created_at.desc())).all()
    calendar=[{'date':w.worksheet_date.isoformat(),'completed':bool(w.completed_at),'score':w.score,'total':w.total,'hints':sum((q.hint_count or 0) for q in w.questions)} for w in works]
    badges=[]
    if correct>=10:badges.append('10 Correct Answers')
    if streak(s,sid)>=5:badges.append('5 Day Streak')
    if streak(s,sid)>=20:badges.append('20 Day Streak')
    if len(attempts)>=1000:badges.append('1000 Questions')

    curriculum=[]; concerns=[]
    for code,(strand,title) in LEVEL4_OUTCOMES.items():
        rows=s.execute(select(Attempt.correct,Attempt.seconds,Question.prompt,Attempt.answer,Question.correct_answer,Attempt.created_at)
            .join(Question).where(Attempt.student_id==sid,Question.skill.like(f'{code}:%'),Attempt.attempt_number==1)
            .order_by(Attempt.created_at.desc()).limit(12)).all()
        if rows:
            accuracy=sum(1 for r in rows if r.correct)/len(rows); avg=sum(r.seconds for r in rows)/len(rows)
            if len(rows)>=5 and accuracy>=.85: status='secure'
            elif len(rows)>=3 and accuracy>=.70: status='developing'
            else: status='needs_support'
        else: accuracy=0;avg=0;status='not_assessed'
        item={'code':code,'strand':strand,'title':title,'attempts':len(rows),'accuracy':round(accuracy*100),'avg_seconds':round(avg,1),'status':status}
        curriculum.append(item)
        if status=='needs_support': concerns.append(item)

    recent_incorrect=s.execute(select(Question.prompt,Question.skill,Attempt.answer,Question.correct_answer,Question.working,Attempt.created_at)
        .join(Attempt).where(Attempt.student_id==sid,Attempt.correct==False,Attempt.attempt_number>=1)
        .order_by(Attempt.created_at.desc()).limit(10)).all()
    incorrect_items=[]
    for prompt,skill,student_answer,correct_answer,working,created_at in recent_incorrect:
        code=skill.split(':',1)[0] if ':' in skill else ''
        incorrect_items.append({'prompt':prompt,'code':code,'skill':skill.split(':',1)[-1].replace('_',' '),'student_answer':student_answer,'correct_answer':correct_answer,'working':working,'date':created_at.isoformat()})

    topic_hint_stats=[]
    for topic in LEVEL4_STRANDS:
        topic_questions=s.scalar(select(func.count(Question.id)).join(Worksheet).where(Worksheet.student_id==sid,Question.topic==topic)) or 0
        hinted_questions=s.scalar(select(func.count(func.distinct(HintEvent.question_id))).where(HintEvent.student_id==sid,HintEvent.topic==topic)) or 0
        topic_hints=sum(1 for h in hints if h.topic==topic)
        topic_hint_stats.append({'topic':topic,'hints':topic_hints,'questions_with_hints':hinted_questions,'questions_seen':topic_questions,'hint_rate':round(hinted_questions/max(1,topic_questions)*100)})
    recent_hints=[]
    for h in hints[:10]:
        q=s.get(Question,h.question_id)
        recent_hints.append({'topic':h.topic,'hint_number':h.hint_number,'hint':h.hint_text,'prompt':q.prompt if q else 'Question','date':h.created_at.isoformat()})

    return {
        'user':user_view(user),'streak':streak(s,sid),'completion_percent':round(len(completed)/max(1,len(works))*100),
        'questions_answered':len(attempts),'questions_correct':correct,'accuracy':round(correct/max(1,len(attempts))*100),
        'average_completion_minutes':round(sum(((w.completed_at-w.started_at).total_seconds()/60) for w in completed)/max(1,len(completed)),1),
        'calendar':calendar,'skills':[{'topic':x.topic,'level':x.level,'highest_level':x.highest_level,'accuracy':round(x.rolling_accuracy*100),'avg_seconds':round(x.avg_seconds,1)} for x in skills if x.topic in LEVEL4_STRANDS],
        'badges':badges,'curriculum':curriculum,'concerns':concerns[:8],'recent_incorrect':incorrect_items,
        'hint_summary':{'total_hints':len(hints),'questions_with_hints':len({h.question_id for h in hints}),'by_topic':topic_hint_stats,'recent':recent_hints},
        'curriculum_summary':{'secure':sum(x['status']=='secure' for x in curriculum),'developing':sum(x['status']=='developing' for x in curriculum),'needs_support':sum(x['status']=='needs_support' for x in curriculum),'not_assessed':sum(x['status']=='not_assessed' for x in curriculum)}
    }

@app.get('/api/dashboard/student')
def student_dash(u:User=Depends(current_user),s:Session=Depends(db)): return dashboard(s,u.id)
@app.get('/api/dashboard/parent')
def parent_dash(_:User=Depends(parent),s:Session=Depends(db)):
    student=s.scalar(select(User).where(User.role=='student')); return dashboard(s,student.id)
@app.get('/api/settings')
def get_settings(_:User=Depends(parent),s:Session=Depends(db)):
    student=s.scalar(select(User).where(User.role=='student'));st=student_settings(s,student.id);return {'question_count':st.question_count,'adaptive_mode':st.adaptive_mode,'enabled_topics':json.loads(st.enabled_topics),'manual_levels':json.loads(st.manual_levels),'theme':st.theme}
@app.put('/api/settings')
def put_settings(data:SettingsIn,_:User=Depends(parent),s:Session=Depends(db)):
    student=s.scalar(select(User).where(User.role=='student'));st=student_settings(s,student.id);st.question_count=max(5,min(50,data.question_count));st.adaptive_mode=data.adaptive_mode;st.enabled_topics=json.dumps(data.enabled_topics);st.manual_levels=json.dumps(data.manual_levels);st.theme=data.theme;s.commit();return {'ok':True}
@app.post('/api/backups')
def create_backup(_:User=Depends(parent)):
    stamp=datetime.now().strftime('%Y%m%d-%H%M%S');dest=BACKUP_DIR/f'questmath-{stamp}.db';src=sqlite3.connect(DB_PATH);dst=sqlite3.connect(dest);src.backup(dst);dst.close();src.close();return {'filename':dest.name,'size':dest.stat().st_size}
@app.get('/api/backups')
def list_backups(_:User=Depends(parent)): return [{'filename':p.name,'size':p.stat().st_size,'modified':datetime.fromtimestamp(p.stat().st_mtime).isoformat()} for p in sorted(BACKUP_DIR.glob('*.db'),reverse=True)]
@app.post('/api/backups/restore/{filename}')
def restore(filename:str,_:User=Depends(parent)):
    p=(BACKUP_DIR/filename).resolve()
    if p.parent!=BACKUP_DIR.resolve() or not p.exists(): raise HTTPException(404,'Backup not found')
    shutil.copy2(DB_PATH,BACKUP_DIR/f'pre-restore-{datetime.now():%Y%m%d-%H%M%S}.db');shutil.copy2(p,DB_PATH);return {'ok':True,'restart_required':True}
@app.get('/api/reports/progress.csv')
def csv_report(_:User=Depends(parent),s:Session=Depends(db)):
    student=s.scalar(select(User).where(User.role=='student'));works=s.scalars(select(Worksheet).where(Worksheet.student_id==student.id).order_by(Worksheet.worksheet_date)).all();buf=io.StringIO();w=csv.writer(buf);w.writerow(['Date','Completed','Score','Total','Accuracy','XP','Hints'])
    for x in works:w.writerow([x.worksheet_date,bool(x.completed_at),x.score,x.total,round(x.score/max(1,x.total)*100),x.xp_earned,sum((q.hint_count or 0) for q in x.questions)])
    return StreamingResponse(iter([buf.getvalue()]),media_type='text/csv',headers={'Content-Disposition':'attachment; filename=mathquest-progress.csv'})
@app.get('/api/reports/progress.pdf')
def pdf_report(_:User=Depends(parent),s:Session=Depends(db)):
    student=s.scalar(select(User).where(User.role=='student'));d=dashboard(s,student.id);path=BACKUP_DIR/'progress-report.pdf';c=canvas.Canvas(str(path),pagesize=A4);c.setFont('Helvetica-Bold',20);c.drawString(50,800,'MathQuest Progress Report');c.setFont('Helvetica',11);y=765
    for label,val in [('Student',d['user']['display_name']),('Streak',f"{d['streak']} days"),('Questions answered',d['questions_answered']),('Accuracy',f"{d['accuracy']}%"),('Hints used',d['hint_summary']['total_hints']),('Current level',d['user']['level'])]:c.drawString(50,y,f'{label}: {val}');y-=22
    y-=10;c.setFont('Helvetica-Bold',14);c.drawString(50,y,'Topic performance');y-=24;c.setFont('Helvetica',11)
    for sk in d['skills']:c.drawString(60,y,f"{sk['topic'].title()}: Level {sk['level']}, accuracy {sk['accuracy']}%");y-=20
    c.save();return FileResponse(path,media_type='application/pdf',filename='mathquest-progress.pdf')

static=Path('/app/static')
if static.exists():
    app.mount('/assets',StaticFiles(directory=static/'assets'),name='assets')
    @app.get('/{path:path}')
    def spa(path:str):
        candidate=static/path
        return FileResponse(candidate if candidate.is_file() else static/'index.html')
