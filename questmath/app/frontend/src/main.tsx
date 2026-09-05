import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  CheckCircle2, ChevronLeft, ChevronRight, Database, Download, Eye, Flame, Lightbulb, List,
  LogOut, Play, Settings, SkipForward, Sparkles, Star, Trophy, X
} from 'lucide-react';
import './styles.css';
import './interactive-math.css';
import './student-feedback.css';
import {APP_VERSION} from './version';
import {ApiError, apiRequest as req, createSession, loadActiveWorksheet, questionDraft, rememberActiveWorksheet, rememberQuestionDraft} from './api';
import {ErrorNotice, StudentDestination, StudentMobileNavigation, StudentSection} from './student-foundation';
import {MathsLab} from './maths-lab';
import {MissionOutcome, StoryMissionProgress} from './story-adventure';
import {AdaptiveRecommendation} from './adaptive-recommendation';
import {HomeAssistantConnection, ParentLearningInsight} from './parent-insight';
import {ParentLearningIntelligence} from './parent-intelligence';
import {ParentTestWorksheets, TestQuestionFeedback, TestWorksheetResult} from './parent-testing';
import {InterventionCard, InterventionGoal} from './intervention';
import {QuestionVisual} from './question-visual';
import {ConfidenceCheck, QuestionTools} from './question-tools';
import {FractionBarAnswer, FractionNumberLineAnswer, GridSelectAnswer, RulerAnswer} from './interactive-math';
import {PostAnswerFeedbackModal} from './post-answer-feedback';
import {speakText} from './speech';

const API = 'api';

type User = { id:number; username:string; role:string; display_name:string; xp:number; level:number; highest_level:number };
type QuestionStatus = 'not_started'|'current'|'skipped'|'correct'|'incorrect'|'retry_available';
type Question = {
  id:number; topic:string; skill:string; level:number; prompt:string; summary:string;
  answer_type:string; payload:any; position:number; status:QuestionStatus; skipped_count:number;
  hint_count:number; last_hint:string|null;
  attempts:{answer:string;correct:boolean;attempt_number:number}[];
};
type WorksheetData = {
  id:number; date:string; completed_at:string|null; score:number; total:number; xp_earned:number;
  current_question_id:number|null; current_phase:'main'|'skipped'; elapsed_seconds:number; status:string; selected_topic:string;
  session_kind:string; test_mode:boolean;
  counts:{correct:number;incorrect:number;skipped:number;remaining:number;hints:number;answered?:number;completed?:number}; questions:Question[];
};

function Brand({compact=false}:{compact?:boolean}){
  return <div className={'mq-brand '+(compact?'compact':'')} aria-label="MathQuest by Stu">
    <div className="mq-emblem" aria-hidden="true"><span>+</span><span>×</span><span>−</span><span>÷</span></div>
    <div className="mq-wordmark-wrap"><strong className="mq-wordmark">MathQuest</strong><span className="mq-by-stu">by Stu</span></div>
  </div>;
}
export function App(){
  const[user,setUser]=useState<User|null>(null);
  const[loading,setLoading]=useState(true);
  const[error,setError]=useState('');
  const recoverExpiredAuth=()=>{localStorage.removeItem('token');setUser(null);setError('')};
  const restore=()=>{setLoading(true);setError('');req<User>('/me').then(setUser).catch((e:Error)=>{
    if(e instanceof ApiError&&e.category==='mathquest_auth'){recoverExpiredAuth();return}
    if(localStorage.getItem('token'))setError(e.message)
  }).finally(()=>setLoading(false))};
  useEffect(restore,[]);
  useEffect(()=>{const handler=()=>recoverExpiredAuth();window.addEventListener('mathquest-auth-expired',handler);return()=>window.removeEventListener('mathquest-auth-expired',handler)},[]);
  if(loading)return <div className="splash"><Brand/></div>;
  if(error)return <main className="login"><section className="login-card"><Brand/><ErrorNotice message={error} retry={restore}/><button type="button" onClick={recoverExpiredAuth}>Sign in again</button></section></main>;
  if(!user)return <Login onLogin={setUser}/>;
  const logout=()=>{localStorage.removeItem('token');setUser(null)};
  return user.role==='parent'?<Parent user={user} logout={logout}/>:<Student user={user} logout={logout}/>;
}

export function Login({onLogin}:{onLogin:(u:User)=>void}){
  const[username,setUsername]=useState('sienna');
  const[password,setPassword]=useState('');
  const[error,setError]=useState('');
  async function login(event:React.FormEvent){
    event.preventDefault();
    const body=new URLSearchParams({username,password});
    try{
      const response=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body});
      const data=await response.json();
      if(!response.ok)throw Error(data.detail);
      localStorage.setItem('token',data.access_token);onLogin(data.user);
    }catch(e:any){setError(e.message)}
  }
  return <main className="login"><section className="login-card">
    <Brand/><p>Sienna’s daily adventure in maths.</p>
    <form onSubmit={login}>
      <label>Username<input value={username} onChange={e=>setUsername(e.target.value)}/></label>
      <label>Password<input type="password" value={password} onChange={e=>setPassword(e.target.value)} autoFocus/></label>
      {error&&<div className="error">{error}</div>}<button>Enter MathQuest</button>
    </form><small className="version">Version {APP_VERSION}</small>
  </section></main>;
}

const Header=({user,logout}:{user:User;logout:()=>void})=><header>
  <div className="header-brand"><Brand compact/><small className="header-version">v{APP_VERSION}</small></div><span>{user.display_name}</span>
  <button className="ghost" onClick={logout}><LogOut size={18}/> Sign out</button>
</header>;

function Student({user,logout}:{user:User;logout:()=>void}){
  const[dashboard,setDashboard]=useState<any>(null);
  const[worksheet,setWorksheet]=useState<WorksheetData|null>(null);
  const[summary,setSummary]=useState<any>(null);
  const[working,setWorking]=useState(false);
  const[choosing,setChoosing]=useState(false);
  const[adaptive,setAdaptive]=useState<any>(null);
  const[recommendationBusy,setRecommendationBusy]=useState(false);
  const[error,setError]=useState('');
  const[section,setSection]=useState<StudentSection>('home');
  const load=()=>{setError('');Promise.all([req('/dashboard/student'),loadActiveWorksheet<WorksheetData>(),req('/learning/adaptive-v0230').catch(()=>null)]).then(([nextDashboard,nextWorksheet,nextAdaptive])=>{setDashboard(nextDashboard);setWorksheet(nextWorksheet);setAdaptive(nextAdaptive);if(nextWorksheet&&!nextWorksheet.completed_at&&sessionStorage.getItem('mq_open_worksheet')==='1'){sessionStorage.removeItem('mq_open_worksheet');setWorking(true)}}).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  useEffect(()=>{(window as any).__mq_ws=worksheet},[worksheet]);
  const openWorksheet=(next:WorksheetData)=>{setWorksheet(next);setSummary(null);setChoosing(false);setWorking(true)};
  const startWorksheet=async(topic:string,minutes:5|10|15,kind:'practice'|'diagnostic')=>openWorksheet(await createSession<WorksheetData>(kind,minutes,topic));
  const startRecommended=async()=>{setRecommendationBusy(true);setError('');try{const next=await req<WorksheetData>('/sessions/recommended',{method:'POST'});rememberActiveWorksheet(next.id);openWorksheet(next)}catch(e:any){setError(e.message)}finally{setRecommendationBusy(false)}};
  const selectSection=(next:StudentSection)=>{setSection(next);window.scrollTo({top:0,behavior:'auto'})};
  if(!dashboard&&error)return <><Header user={user} logout={logout}/><main className="page"><ErrorNotice message={error} retry={load}/></main></>;
  if(!dashboard)return <div className="splash"><Brand/></div>;
  if(working&&worksheet&&!worksheet.completed_at&&!summary)return <Worksheet ws={worksheet} onUpdate={setWorksheet} onExit={()=>{setWorking(false);load()}} onDone={x=>{setSummary(x);setWorking(false);load()}}/>;
  if(summary)return <Result data={summary} back={()=>{setSummary(null);load()}}/>;
  if(choosing)return <QuestCategoryPicker cancel={()=>setChoosing(false)} start={startWorksheet}/>;
  const hasProgress=worksheet&&!worksheet.completed_at;
  const answered=worksheet ? worksheet.counts.correct+worksheet.counts.incorrect : 0;
  const untouched=hasProgress&&answered===0;
  return <><Header user={user} logout={logout}/><main className="page student-destination-page">
    {error&&<ErrorNotice message={error} retry={load} dismiss={()=>setError('')}/>}
    {section==='home'&&<>
      <section className="hero"><div><p className="eyebrow">{untouched?'READY TO START':'TODAY’S LEARNING'}</p><h1>{hasProgress?(untouched?'Your worksheet is ready':'Your quest is waiting'):'Ready for your next maths step?'}</h1>
        <p>{hasProgress?(untouched?'Start when you are ready.':`${answered} of ${worksheet.total} questions completed. Your progress is saved.`):'MathQuest will choose useful practice from your current learning plan.'}</p>
        <button className="primary" disabled={!!worksheet?.completed_at} onClick={()=>{if(worksheet){setWorking(true)}else{setChoosing(true)}}><Play size={20}/>{worksheet?.completed_at?'Today complete':hasProgress?(untouched?'Start worksheet':'Continue worksheet'):'Choose a worksheet'}</button>
      </div><div className="level-orb"><small>LEVEL</small><strong>{dashboard.user.level}</strong><span>{dashboard.user.xp%250}/250 XP</span></div></section>
      {!hasProgress&&<AdaptiveRecommendation data={adaptive} busy={recommendationBusy} onStart={startRecommended}/>}
      {!hasProgress&&<InterventionCard onOpen={openWorksheet}/>}
      <StudentDestination section="home" onOpen={openWorksheet} onCreate={()=>setChoosing(true)} onSelect={selectSection}/>
      <section className="panel mq-home-progress-preview"><p className="eyebrow">YOUR PROGRESS</p><h2>See what MathQuest is noticing</h2><p>Find skills that are getting stronger, ready for a challenge or ready to review.</p><button type="button" onClick={()=>selectSection('progress')}>View progress →</button></section>
    </>}
    {section!=='home'&&<StudentDestination section={section} onOpen={openWorksheet} onCreate={()=>setChoosing(true)} onSelect={selectSection}/>}
  </main><StudentMobileNavigation selected={section} onSelect={selectSection}/></>;
}

const QUEST_CATEGORIES=[{id:'number_algebra',icon:'🎯',name:'Number & Algebra Focus',description:'Recommended: number facts, efficient strategies and missing-number equations'},{id:'measurement',icon:'📏',name:'Measurement',description:'Length, area, perimeter, time, temperature and angles'},{id:'algebra',icon:'🧩',name:'Algebra',description:'Unknown values, patterns and number facts'},{id:'probability',icon:'🎲',name:'Probability',description:'Chance, likelihood and repeated experiments'},{id:'number',icon:'🔢',name:'Number',description:'Place value, fractions, operations, money and estimation'},{id:'space',icon:'⬡',name:'Space',description:'Shapes, grids, symmetry and position'},{id:'statistics',icon:'📊',name:'Statistics',description:'Data, graphs, surveys and investigations'},{id:'mixed',icon:'✨',name:'Mixed Adventure',description:'A balanced quest across all learning areas'}];

export function QuestCategoryPicker({start,cancel}:{start:(topic:string,minutes:5|10|15,kind:'practice'|'diagnostic')=>Promise<void>;cancel:()=>void}){const[selected,setSelected]=useState('mixed'),[minutes,setMinutes]=useState<5|10|15>(10),[kind,setKind]=useState<'practice'|'diagnostic'>('practice'),[busy,setBusy]=useState(false),[printBusy,setPrintBusy]=useState(false),[error,setError]=useState('');async function printWorksheet(){setPrintBusy(true);setError('');try{const blob=await req<Blob>('/worksheets/today/print',{method:'POST',body:JSON.stringify({topic:selected})});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=`mathquest-${selected}-worksheet.pdf`;link.click();URL.revokeObjectURL(link.href)}catch(reason:any){setError(reason.message)}finally{setPrintBusy(false)}}return <main className="category-page"><section className="category-card"><Brand compact/><p className="eyebrow">CHOOSE TODAY’S SESSION</p><h1>How would you like to learn?</h1><div className="session-kind" role="group" aria-label="Session type"><button type="button" aria-pressed={kind==='practice'} className={kind==='practice'?'selected':''} onClick={()=>setKind('practice')}><b>Targeted practice</b><small>Work towards the Level 5 pathway</small></button><button type="button" aria-pressed={kind==='diagnostic'} className={kind==='diagnostic'?'selected':''} onClick={()=>{setKind('diagnostic');setMinutes(15)}}><b>Levels 2–6 diagnostic</b><small>Find a starting point across Number and Algebra</small></button></div>{kind==='practice'&&<><p>Choose a session length and learning area.</p><div className="duration-options" role="group" aria-label="Session length">{([5,10,15] as const).map(value=><button type="button" aria-pressed={minutes===value} key={value} className={minutes===value?'selected':''} onClick={()=>setMinutes(value)}><b>{value} minutes</b><small>{value===5?'Quick boost':value===10?'Daily session':'Deep practice'}</small></button>)}</div><div className="category-grid" role="group" aria-label="Learning area">{QUEST_CATEGORIES.map(c=><button type="button" aria-pressed={selected===c.id} key={c.id} className={'category-option '+(selected===c.id?'selected':'')} onClick={()=>setSelected(c.id)}><span>{c.icon}</span><b>{c.name}</b><small>{c.description}</small></button>)}</div></>}{kind==='diagnostic'&&<div className="diagnostic-note"><b>About 15 minutes</b><p>Three short questions at each Victorian Curriculum level from 2 to 6. Results identify a baseline; Level 5 remains the learning target.</p></div>}{error&&<p className="category-error" role="alert">{error}</p>}<div className="category-actions"><button onClick={cancel}>Back</button>{kind==='practice'&&<button type="button" disabled={printBusy} onClick={printWorksheet}><Download size={18}/>{printBusy?'Preparing PDF…':'Print worksheet'}</button>}<button className="primary" disabled={busy} onClick={async()=>{setBusy(true);try{await start(kind==='diagnostic'?'number_algebra':selected,minutes,kind)}finally{setBusy(false)}}><Play size={20}/>{busy?'Building your session…':kind==='diagnostic'?'Start diagnostic':`Start ${minutes}-minute session`}</button></div></section></main>}

function Metric({icon,label,value}:any){return <div className="metric">{icon&&<i>{icon}</i>}<div><small>{label}</small><strong>{value}</strong></div></div>}
function StrategyCard({card}:{card:any}){if(!card)return null;return <div className="mq-strategy-card"><div><span>🧠</span><p><small>STRATEGY FOR THIS QUESTION</small><b>{card.title}</b></p></div><h3>{card.strategy}</h3><p className="mq-strategy-rule">{card.rule}</p><ol>{(card.steps||[]).map((step:string)=><li key={step}>{step}</li>)}</ol>{card.example&&<small className="mq-strategy-example">{card.example}</small>}</div>}

function MathStep({step}:{step:any}){
  return <div className="mentor-step"><small>{step.label}</small>{step.text&&<p>{step.text}</p>}{Array.isArray(step.math)&&<div className="mentor-math">{step.math.map((line:string)=><code key={line}>{line}</code>)}</div>}</div>;
}

function MathMentor({support,open,setOpen,onHint,onAction,onStartOver,busy,canStartOver,onOpenLab}:{support:any;open:boolean;setOpen:(open:boolean)=>void;onHint:()=>Promise<void>;onAction:(action:string)=>Promise<void>;onStartOver:()=>Promise<void>;busy:boolean;canStartOver:boolean;onOpenLab:()=>void}){
  const[spokenError,setSpokenError]=useState('');
  const readAloud=()=>{const stepText=(support?.teach_steps||[]).flatMap((step:any)=>[step.label,step.text,...(step.math||[])]).filter(Boolean);const text=[support?.mentor_message,support?.why_text,support?.worked_example?.prompt,...stepText].filter(Boolean).join('. ');const result=speakText(text);setSpokenError(result.ok?'':result.message||'Read aloud is unavailable in this browser.')};
  return <aside className="math-mentor" aria-label="Math Mentor"><button type="button" className="mentor-toggle" aria-expanded={open} onClick={()=>setOpen(!open)}><span>🧠</span><b>Math Mentor</b><small>{open?'Hide help':'Need help? Ask before I tell.'}</small></button>{open&&<div className="mentor-body"><p className="mentor-message">{support?.mentor_message||'What do you notice first?'}</p><div className="mentor-actions"><button type="button" disabled={busy} onClick={onHint}>Hint</button><button type="button" disabled={busy} onClick={()=>onAction('why')}>Why?</button><button type="button" disabled={busy} onClick={()=>onAction('teach')}>Teach me</button><button type="button" disabled={busy} onClick={()=>onAction('example')}>Worked example</button><button type="button" onClick={onOpenLab}>Maths Lab</button><button type="button" onClick={readAloud}>Read aloud</button>{canStartOver&&<button type="button" disabled={busy} onClick={onStartOver}>Start over</button>}</div>{spokenError&&<p className="mentor-read-error" role="status">{spokenError}</p>}{support?.why_text&&<div className="mentor-why"><small>WHY THIS WORKS</small><p>{support.why_text}</p></div>}{support?.teach_steps?.length>0&&<div className="mentor-teach"><small>TEACH ME</small>{support.teach_steps.map((step:any,index:number)=><MathStep key={`${step.label}-${index}`} step={step}/>)}</div>}{support?.worked_example&&<div className="mentor-example"><small>WORKED EXAMPLE</small><b>{support.worked_example.prompt}</b>{support.worked_example.steps?.map((step:any,index:number)=><MathStep key={`${step.label}-${index}`} step={step}/>)}</div>}</div>}</aside>;
}

function Worksheet({ws,onUpdate,onDone,onExit}:{ws:WorksheetData;onUpdate:(w:WorksheetData)=>void;onDone:(r:any)=>void;onExit:()=>void}){
  const question=ws.questions.find(q=>q.id===ws.current_question_id)||ws.questions.find(q=>q.status==='current')||ws.questions.find(q=>q.status==='not_started')||ws.questions.find(q=>q.status==='skipped');
  const[value,setValue]=useState('');
  const[selectedChoice,setSelectedChoice]=useState('');
  const[gridSelection,setGridSelection]=useState('');
  const[mentorOpen,setMentorOpen]=useState(false);
  const[busy,setBusy]=useState(false);
  const[hint,setHint]=useState('');
  const[support,setSupport]=useState<any>(null);
  const[labOpen,setLabOpen]=useState(false);
  const[confidence,setConfidence]=useState<'low'|'medium'|'high'|null>(null);
  const[inputRef]=useState(()=>React.createRef<HTMLInputElement>());
  const draft=question?questionDraft(ws.id,question.id):'';
  useEffect(()=>{if(question){setValue(draft);setSelectedChoice(draft);setGridSelection(draft);setMentorOpen(false);setHint(question.last_hint||'');setSupport(null);setConfidence(null);setTimeout(()=>inputRef.current?.focus(),0)}},[question?.id]);
  useEffect(()=>{if(!question)return;rememberQuestionDraft(ws.id,question.id,value)},[value,ws.id,question?.id]);
  if(!question)return <div className="worksheet-shell"><div className="worksheet-header"><Brand compact/><button onClick={onExit}>Exit worksheet</button></div><main className="worksheet-layout"><section className="question-card"><h1>No question is available.</h1></section></main></div>;
  const answer=question.answer_type==='choice'?selectedChoice:question.answer_type==='grid_select'?gridSelection:value;
  const canSubmit=String(answer).trim().length>0;
  async function refresh(next:any){onUpdate(next);return next}
  async function submit(){if(!canSubmit)return;setBusy(true);try{const result:any=await req(`/questions/${question.id}/answer`,{method:'POST',body:JSON.stringify({answer,confidence})});rememberQuestionDraft(ws.id,question.id,'');if(result.summary){onDone(result.summary);return}await refresh(await req(`/worksheets/${ws.id}/view`))}finally{setBusy(false)}}
  async function skip(){setBusy(true);try{const result:any=await req(`/questions/${question.id}/skip`,{method:'POST'});if(result.summary){onDone(result.summary);return}await refresh(await req(`/worksheets/${ws.id}/view`))}finally{setBusy(false)}}
  async function hintAction(){setBusy(true);try{const result:any=await req(`/questions/${question.id}/hint`,{method:'POST'});setHint(result.hint||'');setSupport(result.support||support);setMentorOpen(true)}finally{setBusy(false)}}
  async function mentorAction(action:string){setBusy(true);try{setSupport(await req(`/questions/${question.id}/mentor`,{method:'POST',body:JSON.stringify({action})}));setMentorOpen(true)}finally{setBusy(false)}}
  async function startOver(){setBusy(true);try{setSupport(await req(`/questions/${question.id}/mentor`,{method:'POST',body:JSON.stringify({action:'start_over'})}));setValue('');setSelectedChoice('');setGridSelection('');rememberQuestionDraft(ws.id,question.id,'');setTimeout(()=>inputRef.current?.focus(),0)}finally{setBusy(false)}}
  const statusCounts=ws.counts||{correct:0,incorrect:0,skipped:0,remaining:0,hints:0};
  return <div className="worksheet-shell"><div className="worksheet-header"><Brand compact/><button onClick={onExit}>Exit worksheet</button></div><main className="worksheet-layout"><section className="worksheet-main"><div className="worksheet-top"><b>{String(ws.selected_topic||'Maths').replaceAll('_',' ')}</b><span>{statusCounts.correct+statusCounts.incorrect}/{ws.total} completed</span><div className="progress"><i style={{width:`${Math.round((statusCounts.correct+statusCounts.incorrect)/Math.max(ws.total,1)*100)}%`}}/></div></div><article className="question-card"><QuestionVisual question={question}/><h1>{question.prompt}</h1><StrategyCard card={question.payload?.strategy_card}/><InterventionGoal question={question}/>{question.answer_type==='choice'?<div className="choices">{(question.payload?.choices||[]).map((choice:string)=><button type="button" key={choice} className={selectedChoice===choice?'selected':''} onClick={()=>setSelectedChoice(choice)}>{choice}</button>)}</div>:question.answer_type==='grid_select'?<GridSelectAnswer question={question} value={gridSelection} onChange={setGridSelection}/>:question.answer_type==='fraction_bar'?<FractionBarAnswer question={question} value={value} onChange={setValue}/>:question.answer_type==='fraction_number_line'?<FractionNumberLineAnswer question={question} value={value} onChange={setValue}/>:question.answer_type==='ruler'?<RulerAnswer question={question} value={value} onChange={setValue}/>:<div className="answer-row"><input ref={inputRef} aria-label="Your answer" value={value} onChange={e=>setValue(e.target.value)} onKeyDown={e=>{if(e.key==='Enter'&&canSubmit&&!busy)submit()}}/></div>}<ConfidenceCheck value={confidence} onChange={setConfidence}/>{hint&&<div className="hint-box"><Lightbulb/><div><b>Hint</b><p>{hint}</p></div></div>}<QuestionTools question={question}/><MathMentor support={support} open={mentorOpen} setOpen={setMentorOpen} onHint={hintAction} onAction={mentorAction} onStartOver={startOver} busy={busy} canStartOver={!!support} onOpenLab={()=>setLabOpen(true)}/>{labOpen&&<MathsLab close={()=>setLabOpen(false)}/>}<div className="question-actions"><button className="skip" disabled={busy} onClick={skip}><SkipForward size={18}/>Skip</button><button className="primary" disabled={!canSubmit||busy} onClick={submit}>Check answer</button></div></article></section><aside className="worksheet-status"><h2>Worksheet</h2><dl><div><dt>Correct</dt><dd className="green">{statusCounts.correct}</dd></div><div><dt>Incorrect</dt><dd className="red">{statusCounts.incorrect}</dd></div><div><dt>Skipped</dt><dd className="amber">{statusCounts.skipped}</dd></div><div><dt>Hints</dt><dd>{statusCounts.hints}</dd></div></dl></aside></main></div>;
}

function Result({data,back}:{data:any;back:()=>void}){return <main className="result"><section><Sparkles size={42}/><h1>Quest complete!</h1><div className="result-score">{data.score}/{data.total}</div><div className="result-grid"><Metric label="Correct" value={data.score}/><Metric label="XP earned" value={data.xp_earned}/><Metric label="Hints" value={data.hints||0}/><Metric label="Skipped" value={data.skipped||0}/></div><button className="primary" onClick={back}>Back to MathQuest</button></section></main>}

function Parent({user,logout}:{user:User;logout:()=>void}){return <><Header user={user} logout={logout}/><main className="page"><ParentLearningIntelligence/><ParentLearningInsight/><HomeAssistantConnection/><ParentTestWorksheets/></main></>}

createRoot(document.getElementById('root')!).render(<App/>);
