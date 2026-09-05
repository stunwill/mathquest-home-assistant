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
  const hasProgress=!!worksheet&&!worksheet.completed_at;
  const answered=worksheet ? worksheet.counts.correct+worksheet.counts.incorrect : 0;
  const untouched=hasProgress&&answered===0;
  const primaryLabel=hasProgress?(untouched?'Start worksheet':'Continue worksheet'):'Choose a worksheet';
  return <><Header user={user} logout={logout}/><main className="page student-destination-page">
    {error&&<ErrorNotice message={error} retry={load} dismiss={()=>setError('')}/>}
    {section==='home'&&<>
      <section className="hero"><div><p className="eyebrow">{untouched?'READY TO START':'TODAY’S LEARNING'}</p><h1>{hasProgress?(untouched?'Your worksheet is ready':'Your quest is waiting'):'Ready for your next maths step?'}</h1>
        <p>{hasProgress?(untouched?'Start when you are ready.':`${answered} of ${worksheet!.total} questions completed. Your progress is saved.`):'MathQuest will choose useful practice from your current learning plan.'}</p>
        <button className="primary" onClick={()=>{if(hasProgress&&worksheet){setWorking(true)}else{setChoosing(true)}}}><Play size={20}/>{primaryLabel}</button>
      </div></section>
      {!hasProgress&&<AdaptiveRecommendation data={adaptive} busy={recommendationBusy} onStart={startRecommended}/>}
      {!hasProgress&&<InterventionCard onOpen={openWorksheet}/>}
      <StudentDestination section="home" onOpen={openWorksheet} onCreate={()=>setChoosing(true)} onSelect={selectSection}/>
      <section className="panel mq-home-progress-preview"><p className="eyebrow">YOUR PROGRESS</p><h2>See what MathQuest is noticing</h2><p>Find skills that are getting stronger, ready for a challenge or ready to review.</p><button type="button" onClick={()=>selectSection('progress')}>View progress →</button></section>
    </>}
    {section!=='home'&&<StudentDestination section={section} onOpen={openWorksheet} onCreate={()=>setChoosing(true)} onSelect={selectSection}/>}
  </main><StudentMobileNavigation selected={section} onSelect={selectSection}/></>;
}

const QUEST_CATEGORIES=[{id:'number_algebra',icon:'🎯',name:'Number & Algebra Focus',description:'Recommended: number facts, efficient strategies and missing-number equations'},{id:'measurement',icon:'📏',name:'Measurement',description:'Length, area, perimeter, time, temperature and angles'},{id:'algebra',icon:'🧩',name:'Algebra',description:'Unknown values, patterns and number facts'},{id:'probability',icon:'🎲',name:'Probability',description:'Chance, likelihood and repeated experiments'},{id:'number',icon:'🔢',name:'Number',description:'Place value, fractions, operations, money and estimation'},{id:'space',icon:'⬡',name:'Space',description:'Shapes, grids, symmetry and position'},{id:'statistics',icon:'📊',name:'Statistics',description:'Data, graphs, surveys and investigations'},{id:'mixed',icon:'✨',name:'Mixed Adventure',description:'A balanced quest across all learning areas'}];

export function QuestCategoryPicker({start,cancel}:{start:(topic:string,minutes:5|10|15,kind:'practice'|'diagnostic')=>Promise<void>;cancel:()=>void}){const[selected,setSelected]=useState('mixed'),[minutes,setMinutes]=useState<5|10|15>(10),[kind,setKind]=useState<'practice'|'diagnostic'>('practice'),[busy,setBusy]=useState(false),[printBusy,setPrintBusy]=useState(false),[error,setError]=useState('');async function printWorksheet(){setPrintBusy(true);setError('');try{const blob=await req<Blob>('/worksheets/today/print',{method:'POST',body:JSON.stringify({topic:selected})});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=`mathquest-${selected}-worksheet.pdf`;link.click();URL.revokeObjectURL(link.href)}catch(reason:any){setError(reason.message)}finally{setPrintBusy(false)}}return <main className="category-page"><section className="category-card"><Brand compact/><p className="eyebrow">CHOOSE TODAY’S SESSION</p><h1>How would you like to learn?</h1><div className="session-kind" role="group" aria-label="Session type"><button type="button" aria-pressed={kind==='practice'} className={kind==='practice'?'selected':''} onClick={()=>setKind('practice')}><b>Targeted practice</b><small>Work towards the Level 5 pathway</small></button><button type="button" aria-pressed={kind==='diagnostic'} className={kind==='diagnostic'?'selected':''} onClick={()=>{setKind('diagnostic');setMinutes(15)}}><b>Level 5 and Level 6 diagnostic</b><small>Check Level 5 foundations and Level 6 readiness</small></button></div>{kind==='practice'&&<><p>Choose a session length and learning area.</p><div className="duration-options" role="group" aria-label="Session length">{([5,10,15] as const).map(value=><button type="button" aria-pressed={minutes===value} key={value} className={minutes===value?'selected':''} onClick={()=>setMinutes(value)}><b>{value} minutes</b><small>{value===5?'Quick boost':value===10?'Daily session':'Deep practice'}</small></button>)}</div><div className="category-grid" role="group" aria-label="Learning area">{QUEST_CATEGORIES.map(c=><button type="button" aria-pressed={selected===c.id} key={c.id} className={'category-option '+(selected===c.id?'selected':'')} onClick={()=>setSelected(c.id)}><span>{c.icon}</span><b>{c.name}</b><small>{c.description}</small></button>)}</div></>}{kind==='diagnostic'&&<div className="diagnostic-note"><b>Six questions</b><p>Three short questions at Level 5 and three at Level 6. Results show whether Level 5 is secure and whether Level 6 is ready for challenge.</p></div>}{error&&<p className="category-error" role="alert">{error}</p>}<div className="category-actions"><button onClick={cancel}>Back</button>{kind==='practice'&&<button type="button" disabled={printBusy} onClick={printWorksheet}><Download size={18}/>{printBusy?'Preparing PDF…':'Print worksheet'}</button>}<button className="primary" disabled={busy} onClick={async()=>{setBusy(true);try{await start(kind==='diagnostic'?'number_algebra':selected,minutes,kind)}finally{setBusy(false)}}}><Play size={20}/>{busy?'Building your session…':kind==='diagnostic'?'Start diagnostic':`Start ${minutes}-minute session`}</button></div></section></main>}

function Metric({icon,label,value}:any){return <div className="metric">{icon&&<i>{icon}</i>}<div><small>{label}</small><strong>{value}</strong></div></div>}
function StrategyCard({card}:{card:any}){if(!card)return null;return <div className="mq-strategy-card"><div><span>🧠</span><p><small>STRATEGY FOR THIS QUESTION</small><b>{card.title}</b></p></div><h3>{card.strategy}</h3><p className="mq-strategy-rule">{card.rule}</p><ol>{(card.steps||[]).map((step:string)=><li key={step}>{step}</li>)}</ol>{card.example&&<small className="mq-strategy-example">{card.example}</small>}</div>}

function MathStep({step}:{step:any}){
  return <div className="mentor-step"><small>{step.label}</small>{step.text&&<p>{step.text}</p>}{Array.isArray(step.math)&&<div className="mentor-math">{step.math.map((line:string)=><code key={line}>{line}</code>)}</div>}</div>;
}

function MathMentor({support,open,setOpen,onHint,onAction,onStartOver,busy,canStartOver,onOpenLab}:{support:any;open:boolean;setOpen:(open:boolean)=>void;onHint:()=>Promise<void>;onAction:(action:string)=>Promise<void>;onStartOver:()=>Promise<void>;busy:boolean;canStartOver:boolean;onOpenLab:()=>void}){
  const[spokenError,setSpokenError]=useState('');
  const readAloud=()=>{const stepText=(support?.teach_steps||[]).flatMap((step:any)=>[step.label,step.text,...(step.math||[])]);const result=speakText([support?.title,support?.guiding_question,support?.body,...stepText,support?.worked_example,support?.visual_connection].filter(Boolean).join('. '));if(!result.supported)setSpokenError(result.message)};
  const stageLabel=support?.action==='hint'?`${String(support.hint_kind||'hint').replaceAll('_',' ')} · ${support.stage} of 3`:support?.action==='teach'?'Mini lesson':support?.action==='why'?'Concept explanation':support?.action==='worked_example'?'Different-number example':'Ask before tell';
  return <section className={'math-mentor '+(open?'open':'')} data-guided-tutor="true"><button type="button" className="math-mentor-toggle" aria-expanded={open} onClick={()=>setOpen(!open)}><span aria-hidden="true">🧑‍🏫</span><span><small>MATH MENTOR</small><b>{support?.strategy_name||support?.title||'Get help without giving away the answer'}</b></span><span aria-hidden="true">{open?'⌃':'⌄'}</span></button>{open&&<div className="math-mentor-body" aria-live="polite">{support?<><p className="math-mentor-stage">{stageLabel}</p><h3>{support.action==='guide'?'Try this first':support.action==='why'?'Why this works':support.action==='teach'?'Teach me':support.action==='hint'?'Use this next':'Worked example'}</h3>{support.body&&<p className="mentor-body-copy">{support.body}</p>}{support.action==='teach'&&Array.isArray(support.teach_steps)&&<div className="mentor-lesson">{support.teach_steps.map((step:any,index:number)=><MathStep key={`${step.label}-${index}`} step={step}/>)}</div>}{support.visual_recommendation&&<div className="guided-misconception"><b>Visual strategy</b><p>{support.visual_recommendation.message}</p><button type="button" onClick={onOpenLab}>Open {String(support.visual_recommendation.model).replaceAll('-',' ')} model</button></div>}{support.evidence_visual_recommendation&&<div className="guided-misconception"><b>Based on recent practice</b><p>{support.evidence_visual_recommendation.message}</p></div>}{support.common_mistake&&<div className="guided-misconception"><b>Common mistake to watch for</b><p>{support.common_mistake}</p></div>}{support.action==='worked_example'&&<div className="guided-example"><b>Same skill, different numbers</b><p>{support.worked_example}</p><small>Use the same structure on your question, not the example’s answer.</small></div>}</>:<p>Choose the kind of help you want. You can keep typing or checking an answer at any time.</p>}<div className="guided-actions"><button type="button" disabled={busy} onClick={()=>onHint()}>💡 Hint</button><button type="button" disabled={busy} onClick={()=>onAction('why')}>Why?</button><button type="button" disabled={busy} onClick={()=>onAction('teach')}>Teach me</button><button type="button" disabled={busy} onClick={()=>onAction('worked_example')}>Worked example</button>{canStartOver&&<button type="button" disabled={busy} onClick={()=>onStartOver()}>↻ Start over</button>}<button type="button" onClick={readAloud}>🔊 Read aloud</button></div>{spokenError&&<p role="status" className="math-mentor-speech">{spokenError}</p>}</div>}</section>
}

export function Worksheet({ws,onUpdate,onExit,onDone}:{ws:WorksheetData;onUpdate:(x:WorksheetData)=>void;onExit:()=>void;onDone:(x:any)=>void}){
  const[answer,setAnswer]=useState(''),[feedback,setFeedback]=useState<any>(null),[hint,setHint]=useState<string|null>(null),[support,setSupport]=useState<any>(null),[mentorOpen,setMentorOpen]=useState(false),[hintBusy,setHintBusy]=useState(false),[questionStart,setQuestionStart]=useState(Date.now()),[sessionStart]=useState(Date.now()-(ws.elapsed_seconds||0)*1000),[overview,setOverview]=useState(false),[confirmExit,setConfirmExit]=useState(false),[labOpen,setLabOpen]=useState(false),[actionError,setActionError]=useState('');
  const actionBusy=useRef(false),answerRef=useRef<HTMLInputElement|null>(null);const active=useMemo(()=>ws.questions.find(q=>q.id===ws.current_question_id)||nextEligible(ws),[ws]);const q=active;const completed=ws.counts.correct+ws.counts.incorrect;const phase=ws.current_phase==='skipped'||(!ws.questions.some(x=>['not_started','current','retry_available'].includes(x.status))&&ws.counts.skipped>0)?'skipped':'main';const previous=previousEligible(ws,q?.id);const canFinishWithSkipped=ws.questions.every(item=>['correct','incorrect','skipped'].includes(item.status)||(item.skipped_count>0&&!item.attempts.length));
  useEffect(()=>{if(q&&q.id!==ws.current_question_id)void safe(()=>goTo(q.id))},[]);useEffect(()=>{setHint(q?.last_hint||null);setSupport(null);setMentorOpen(false);setAnswer(q?questionDraft(ws.id,q.id):'')},[q?.id,ws.id]);
  async function safe(action:()=>Promise<void>){if(actionBusy.current)return;actionBusy.current=true;setActionError('');try{await action()}catch(e:any){setActionError(e.message||'MathQuest could not complete that action.')}finally{actionBusy.current=false}}
  function elapsed(){return (Date.now()-sessionStart)/1000}async function refresh(updated?:WorksheetData){const data:WorksheetData=updated||await req<WorksheetData>(`/worksheets/${ws.id}/view`);onUpdate(data);setAnswer('');setFeedback(null);setHint(null);setSupport(null);setQuestionStart(Date.now())}async function goTo(id:number){const updated=await req(`/worksheets/${ws.id}/navigate/${id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});setOverview(false);await refresh(updated)}async function previousQuestion(){if(previous)await goTo(previous.id)}
  async function mentor(action:string){return req(`/questions/${q.id}/math-mentor-v0310?action=${action}`)}
  async function submit(){const cleaned=String(answer ?? '').trim();if(!cleaned)return;const result=await req(`/questions/${q.id}/answer`,{method:'POST',body:JSON.stringify({answer:cleaned,seconds:(Date.now()-questionStart)/1000})});setFeedback(result);if(result.mentor_required){setSupport(await mentor('guide'));setMentorOpen(true)}if(result.correct||!result.retry_allowed){rememberQuestionDraft(ws.id,q.id,'');const latest=await req(`/worksheets/${ws.id}/view`);onUpdate(latest)}}
  function retryQuestion(openMentor=false){rememberQuestionDraft(ws.id,q.id,'');setFeedback(null);setAnswer('');setQuestionStart(Date.now());if(openMentor)setMentorOpen(true);requestAnimationFrame(()=>answerRef.current?.focus({preventScroll:true}))}
  async function requestHint(){setHintBusy(true);try{await req(`/questions/${q.id}/hint`,{method:'POST'});const mentorHint=await mentor('hint');setSupport(mentorHint);setHint(mentorHint.body);setMentorOpen(true);const latest=await req(`/worksheets/${ws.id}/view`);onUpdate(latest)}finally{setHintBusy(false)}}async function requestSupport(action:string){setHintBusy(true);try{setSupport(await mentor(action));setMentorOpen(true)}finally{setHintBusy(false)}}async function startOver(){if(feedback&&!feedback.retry_allowed)return;setSupport(await req(`/questions/${q.id}/math-mentor/start-over`,{method:'POST'}));setFeedback(null);setMentorOpen(true);setQuestionStart(Date.now())}async function skip(){const updated=await req(`/questions/${q.id}/skip`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});const next=nextEligible(updated,q.id);if(next){const moved=await req(`/worksheets/${ws.id}/navigate/${next.id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});await refresh(moved)}else await refresh(updated)}async function next(){const latest:WorksheetData=await req(`/worksheets/${ws.id}/view`);const target=nextEligible(latest,q.id);if(target){const moved=await req(`/worksheets/${ws.id}/navigate/${target.id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});await refresh(moved);return}const result=await req(`/worksheets/${ws.id}/complete`,{method:'POST'});if(!ws.test_mode)rememberActiveWorksheet(null);onDone(result)}async function finish(){const result=await req(`/worksheets/${ws.id}/complete`,{method:'POST'});if(!ws.test_mode)rememberActiveWorksheet(null);onDone(result)}async function exit(){await req(`/worksheets/${ws.id}/save`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});onExit()}
  useEffect(()=>{const keydown=(event:KeyboardEvent)=>{if(event.key!=='Enter'||event.repeat||actionBusy.current||overview||confirmExit||labOpen||feedback)return;const target=event.target as HTMLElement|null;if(!target||target.closest('textarea,select,button,[contenteditable="true"],.modal-backdrop,.lab-backdrop,.post-answer-backdrop'))return;if(target instanceof HTMLInputElement&&String(answer??'').trim()){event.preventDefault();void safe(submit)}};window.addEventListener('keydown',keydown);return()=>window.removeEventListener('keydown',keydown)});
  if(!q)return <div className="splash">Preparing your next question…</div>;const currentNumber=q.position+1;return <main className="worksheet-shell"><div className="worksheet-header"><button className="ghost danger-text" onClick={()=>setConfirmExit(true)}><X size={20}/> Exit worksheet</button><Brand compact/><button className="ghost" onClick={()=>setOverview(true)}><List size={20}/> Questions</button></div><div className="worksheet-layout"><section className="worksheet-main"><div className="worksheet-top"><b>{phase==='skipped'?`Skipped round · ${ws.counts.skipped} remaining`:`Question ${currentNumber} of ${ws.total}`}</b><div className="progress"><i style={{width:`${completed/ws.total*100}%`}}/></div><span>{q.topic} · level {q.level}</span></div><section className="question-card" key={`${q.id}:${q.payload?.visual_key||''}`} data-question-id={q.id} data-visual-key={q.payload?.visual_key} data-guided-tutor-owner="true">{actionError&&<ErrorNotice message={actionError} dismiss={()=>setActionError('')}/>} {q.payload?.adventure&&<StoryMissionProgress adventure={q.payload.adventure}/>}<InterventionGoal question={q}/><div className="question-icon">{({number:'🔢',algebra:'□',measurement:'📏',space:'⬡',statistics:'📊',probability:'🎲'} as any)[q.topic]||'✦'}</div><QuestionTools question={q} onOpenLab={()=>setLabOpen(true)} worksheetId={ws.id} answer={answer} onSupport={setSupport}/><h1>{q.prompt}</h1><QuestionVisual question={q}/>{q.payload?.shape&&<FractionShape parts={q.payload.shape.parts} shaded={q.payload.shape.shaded}/>}<Answer q={q} value={answer} setValue={(value:string)=>{setAnswer(value);rememberQuestionDraft(ws.id,q.id,value)}} inputRef={answerRef}/>{hint&&<div className="hint-box"><Lightbulb size={22}/><div><b>{support?.hint_kind?String(support.hint_kind).replaceAll('_',' '):'Hint'} {q.hint_count||1} of 3</b><p>{hint}</p></div></div>}<MathMentor support={support} open={mentorOpen} setOpen={setMentorOpen} busy={hintBusy} canStartOver={!feedback||feedback.retry_allowed} onHint={requestHint} onAction={requestSupport} onStartOver={startOver} onOpenLab={()=>setLabOpen(true)}/>{!feedback&&<><div className="question-navigation"><button type="button" disabled={!previous} onClick={()=>safe(previousQuestion)}><ChevronLeft size={19}/> Previous question</button>{canFinishWithSkipped&&<button type="button" className="finish-skipped" onClick={()=>safe(finish)}>Finish worksheet with skipped questions</button>}</div><div className="support-actions"><button className="hint-button" disabled={hintBusy} onClick={()=>safe(requestHint)}><Lightbulb size={19}/>{hintBusy?'Getting help…':q.hint_count>=3?'Review final hint':q.hint_count===2?'Show worked next step':q.hint_count===1?'Show a strategy':'Give me a hint'}</button><small>Hints become gradually stronger and do not reduce the score.</small></div><div className="question-actions"><button className="skip" onClick={()=>safe(skip)}><SkipForward size={19}/> Skip for now</button><button type="button" className="primary" disabled={!String(answer ?? '').trim()} onClick={()=>safe(submit)}>Check answer</button></div></>}</section></section><WorksheetStatus ws={ws} q={q} open={()=>setOverview(true)}/></div>{feedback&&<PostAnswerFeedbackModal feedback={feedback} working={feedback.working} primaryLabel={feedback.retry_allowed?'Try again':ws.counts.remaining<=1?'Finish worksheet':'Next question'} onPrimary={()=>feedback.retry_allowed?retryQuestion():void safe(next)} onOpenMentor={feedback.retry_allowed?()=>retryQuestion(true):undefined} reflection={!feedback.retry_allowed&&!ws.test_mode?<ConfidenceCheck questionId={q.id}/>:undefined} testFeedback={!feedback.retry_allowed&&ws.test_mode?<TestQuestionFeedback worksheetId={ws.id} question={q}/>:undefined}/>} {overview&&<QuestionOverview ws={ws} activeId={q.id} close={()=>setOverview(false)} goTo={goTo}/>} {confirmExit&&<ConfirmExit cancel={()=>setConfirmExit(false)} exit={exit}/>} {labOpen&&<MathsLab key={`${q.id}:${q.payload?.visual_key||''}`} question={q} onClose={()=>setLabOpen(false)}/>}</main>
}

function nextEligible(ws:WorksheetData,afterId?:number){const sorted=[...ws.questions].sort((a,b)=>a.position-b.position);const start=Math.max(0,sorted.findIndex(q=>q.id===afterId)+1);const main=sorted.filter(q=>['not_started','current','retry_available'].includes(q.status));if(main.length){return [...main.filter(q=>q.position>=start),...main.filter(q=>q.position<start)][0]}const skipped=sorted.filter(q=>q.status==='skipped');return [...skipped.filter(q=>q.position>=start),...skipped.filter(q=>q.position<start)][0]||null}
function previousEligible(ws:WorksheetData,currentId?:number){const sorted=[...ws.questions].sort((a,b)=>a.position-b.position);const current=sorted.find(q=>q.id===currentId);if(!current)return null;return sorted.filter(q=>q.position<current.position&&['not_started','current','skipped','retry_available'].includes(q.status)).at(-1)||null}
function WorksheetStatus({ws,q,open}:{ws:WorksheetData;q:Question;open:()=>void}){return <aside className="worksheet-status"><p className="eyebrow">TODAY’S QUEST</p><h2>{ws.current_phase==='skipped'?'Skipped round':`Question ${q.position+1} / ${ws.total}`}</h2><div className="progress"><i style={{width:`${(ws.counts.correct+ws.counts.incorrect)/ws.total*100}%`}}/></div><dl><div><dt>Completed</dt><dd>{ws.counts.correct+ws.counts.incorrect}</dd></div><div><dt>Correct</dt><dd className="green">{ws.counts.correct}</dd></div><div><dt>Incorrect</dt><dd className="red">{ws.counts.incorrect}</dd></div><div><dt>Hints</dt><dd className="purple">{ws.counts.hints||0}</dd></div><div><dt>Skipped</dt><dd className="amber">{ws.counts.skipped}</dd></div><div><dt>Remaining</dt><dd>{ws.counts.remaining}</dd></div></dl><button className="wide" onClick={open}><Eye size={18}/> View all questions</button></aside>}
function statusLabel(status:QuestionStatus){return({not_started:'Not started',current:'Current',skipped:'Skipped',correct:'Correct',incorrect:'Incorrect',retry_available:'Retry available'} as any)[status]}
function QuestionOverview({ws,activeId,close,goTo}:{ws:WorksheetData;activeId:number;close:()=>void;goTo:(id:number)=>void}){return <div className="modal-backdrop"><section className="overview-modal"><div className="modal-title"><div><p className="eyebrow">WORKSHEET MAP</p><h2>All questions</h2></div><button className="icon-button" onClick={close}><X/></button></div><div className="question-table"><div className="question-table-head"><b>#</b><b>Question</b><b>Status</b></div>{ws.questions.map(q=>{const locked=['correct','incorrect'].includes(q.status);return <button key={q.id} className={'question-row '+(q.id===activeId?'active':'')} disabled={locked} onClick={()=>goTo(q.id)}><span>{q.position+1}</span><span><b>{q.summary}</b><small>{q.topic} · {q.skill.replaceAll('_',' ')}{q.hint_count?` · 💡 ${q.hint_count}`:''}</small></span><span className={'status-pill '+q.status}>{statusLabel(q.status)}</span></button>})}</div><p className="overview-note">Completed questions are read-only. Skipped and unanswered questions can be opened.</p></section></div>}
function ConfirmExit({cancel,exit}:{cancel:()=>void;exit:()=>void}){return <div className="modal-backdrop"><section className="confirm-modal"><div className="question-icon">💾</div><h2>Exit today’s worksheet?</h2><p>Your progress, answers, hints, skipped questions and current position will be saved. You can continue later.</p><div className="modal-actions"><button onClick={cancel}>Keep working</button><button className="primary" onClick={exit}>Save and exit</button></div></section></div>}
export function NumberLineAnswer({q,value,setValue}:any){const visual=q?.payload?.visual||{};const min=Number(visual.min)||0;const steps=Math.max(1,Number(visual.steps)||1);const interval=Number(visual.interval)||1;const labels=new Set<number>((visual.label_indices||[]).map(Number));return <div className="interactive-number-line" role="group" aria-label={`Select a position on the number line from ${min} to ${min+steps*interval}`}><div className="interactive-number-line-track">{Array.from({length:steps+1},(_,index)=>{const tickValue=min+index*interval;const selected=String(value)===String(tickValue);const labelled=labels.has(index);return <button type="button" key={index} aria-label={labelled?`Tick labelled ${tickValue}`:`Unlabelled tick ${index+1}`} aria-pressed={selected} className={selected?'selected':''} onClick={()=>setValue(String(tickValue))}><i/><span>{labelled?tickValue:''}</span></button>})}</div><p aria-live="polite">{value!==''?'Position selected. Check your answer when ready.':'Tap the tick mark that matches the value in the question.'}</p></div>}
export function Answer({q,value,setValue,inputRef}:any){if(q.answer_type==='number_line')return <NumberLineAnswer q={q} value={value} setValue={setValue}/>;if(q.answer_type==='fraction_bar')return <FractionBarAnswer q={q} value={value} setValue={setValue}/>;if(q.answer_type==='fraction_number_line')return <FractionNumberLineAnswer q={q} value={value} setValue={setValue}/>;if(q.answer_type==='ruler')return <RulerAnswer q={q} value={value} setValue={setValue}/>;if(q.answer_type==='grid_select')return <GridSelectAnswer q={q} value={value} setValue={setValue}/>;if(q.answer_type==='choice')return <div className="choices">{q.payload.choices.map((x:string)=><button type="button" className={value===x?'selected':''} onClick={()=>setValue(String(x))} key={x}>{x}</button>)}</div>;const capture=(e:any)=>setValue(String(e.currentTarget.value));return <div className="answer-row">{q.answer_type==='money'&&<span>$</span>}<input ref={inputRef} inputMode={q.answer_type==='text'?'text':'decimal'} value={value} onInput={capture} onChange={capture} autoFocus autoComplete="off" aria-label="Your answer" placeholder="Type your answer"/>{q.payload.unit&&<span>{q.payload.unit}</span>}</div>}
function FractionShape({parts,shaded}:{parts:number;shaded:number}){return <div className="fraction-shape">{Array.from({length:parts}).map((_,i)=><i key={i} className={i<shaded?'on':''}/>)}</div>}
function Result({data,back}:any){return <main className="result"><section><MissionOutcome adventure={data.adventure}/><div className="result-score">{data.score}/{data.total}</div><h1>{data.message}</h1><p>{data.accuracy}% accuracy · +{data.xp_earned} XP</p><div className="result-grid"><Metric label="Strongest" value={data.strongest_topic}/><Metric label="Practise next" value={data.weakest_topic}/><Metric icon={<Lightbulb/>} label="Hints used" value={data.hints_used||0}/><Metric label="Level" value={data.level}/></div><button className="primary" onClick={back}>Back to dashboard</button></section></main>}
function Parent({user,logout}:{user:User;logout:()=>void}){
  const[d,setD]=useState<any>(null),[settings,setSettings]=useState<any>(null),[backups,setBackups]=useState<any[]>([]),[error,setError]=useState(''),[period,setPeriod]=useState(30),[intelligence,setIntelligence]=useState<any>(null),[worksheet,setWorksheet]=useState<WorksheetData|null>(null),[summary,setSummary]=useState<any>(null),[loading,setLoading]=useState(true),[backupError,setBackupError]=useState(''),[intelligenceError,setIntelligenceError]=useState('');
  const load=async()=>{
    setLoading(true);setError('');setBackupError('');setIntelligenceError('');
    try{
      const [dashboardData,settingsData]=await Promise.all([req('/dashboard/parent'),req('/settings')]);
      setD(dashboardData);setSettings(settingsData);
      const [backupResult,legacyResult,intelligenceResult]=await Promise.allSettled([
        req('/backups'),req('/learning/parent-insight'),req(`/learning/parent-intelligence-v0320?days=${period}`)
      ]);
      if(backupResult.status==='fulfilled')setBackups(backupResult.value as any[]);else setBackupError((backupResult.reason as Error)?.message||'Backups could not be loaded.');
      if(legacyResult.status==='fulfilled')setD((current:any)=>({...current,legacyInsight:legacyResult.value}));
      if(intelligenceResult.status==='fulfilled')setIntelligence(intelligenceResult.value);else{setIntelligence(null);setIntelligenceError((intelligenceResult.reason as Error)?.message||'Learning intelligence could not be loaded.');}
    }catch(e:any){setError(e.message||'MathQuest could not load the Parent Dashboard.')}finally{setLoading(false)}
  };
  useEffect(()=>{void load()},[period]);
  if(worksheet&&!worksheet.completed_at&&!summary)return <Worksheet ws={worksheet} onUpdate={setWorksheet} onExit={()=>{setWorksheet(null);void load()}} onDone={x=>{setSummary(x);setWorksheet(null);void load()}}/>;
  if(summary)return <TestWorksheetResult data={summary} onDone={()=>{setSummary(null);void load()}}/>;
  if(loading&&!d&&!settings)return <div className="splash"><Brand/></div>;
  if((!d||!settings)&&error)return <><Header user={user} logout={logout}/><main className="page"><ErrorNotice message={error} retry={()=>void load()}/><button type="button" onClick={logout}>Sign in again</button></main></>;
  if(!d||!settings)return <div className="splash"><Brand/></div>;
  async function save(){await req('/settings',{method:'PUT',body:JSON.stringify(settings)});void load()}
  async function backup(){await req('/backups',{method:'POST'});void load()}
  const statusText=(value:string)=>value==='secure'?'Secure':value==='developing'?'Developing':value==='concern'?'Needs support':value.replaceAll('_',' ');
  const openWorksheet=(next:any)=>setWorksheet(next);
  return <><Header user={user} logout={logout}/><main className="page parent-page">{error&&<ErrorNotice message={error} retry={()=>void load()} dismiss={()=>setError('')}/>} {intelligenceError&&<ErrorNotice message={`Learning intelligence is temporarily unavailable. ${intelligenceError}`} retry={()=>void load()} dismiss={()=>setIntelligenceError('')}/>}<ParentLearningIntelligence data={intelligence} onPeriod={setPeriod}/>{d.legacyInsight&&<ParentLearningInsight data={d.legacyInsight}/>}<ParentTestWorksheets onOpen={openWorksheet}/>
  {d.concerns?.length>0&&<section className="panel concern-panel"><h2>⚑ Areas to review</h2><p>These outcomes currently have less than 70% first-attempt accuracy, or limited successful evidence.</p><div className="concern-grid">{d.concerns.map((x:any)=><div key={x.code}><b>{x.code}</b><span>{x.title}</span><strong>{x.accuracy}%</strong><small>{x.attempts} recent attempts</small></div>)}</div></section>}
  <section className="panel"><h2>MathQuest evidence by Victorian Curriculum outcome</h2><p>MathQuest reports observed learning evidence and does not formally certify curriculum achievement.</p><div className="curriculum-table"><div className="curriculum-head"><b>Outcome</b><b>Evidence</b><b>Accuracy</b><b>Status</b></div>{d.curriculum.map((x:any)=><div className="curriculum-row" key={x.code}><span><b>{x.code}</b><small>{x.strand} · {x.title}</small></span><span>{x.attempts} attempts</span><span>{x.attempts?`${x.accuracy}%`:'—'}</span><span className={'status-pill '+x.status}>{statusText(x.status)}</span></div>)}</div></section>
  <section className="grid2"><div className="panel"><h2>Strand performance</h2>{d.skills.map((s:any)=><div className="skill" key={s.topic}><div><b>{s.topic}</b><span>Adaptive level {s.level}</span></div><div className="bar"><i style={{width:`${s.accuracy}%`}}/></div><small>{s.accuracy}% · {s.avg_seconds}s average</small></div>)}</div><div className="panel"><h2><Settings size={20}/> Worksheet settings</h2><label>Questions per day<input type="number" min="5" max="50" value={settings.question_count} onChange={e=>setSettings({...settings,question_count:+e.target.value})}/></label><label className="toggle"><input type="checkbox" checked={settings.adaptive_mode} onChange={e=>setSettings({...settings,adaptive_mode:e.target.checked})}/> Adaptive learning</label><div className="topic-checks">{['number','algebra','measurement','space','statistics','probability'].map(t=><label key={t}><input type="checkbox" checked={settings.enabled_topics.includes(t)} onChange={e=>setSettings({...settings,enabled_topics:e.target.checked?[...settings.enabled_topics,t]:settings.enabled_topics.filter((x:string)=>x!==t)})}/>{t}</label>)}</div><button className="primary" onClick={save}>Save settings</button></div></section>
  <section className="panel"><h2>Recent incorrect answers</h2>{d.recent_incorrect.length?<div className="incorrect-list">{d.recent_incorrect.map((x:any,i:number)=><details key={i}><summary><b>{x.code||'Practice'}</b> {x.prompt}</summary><p>Student answer: <strong>{x.student_answer}</strong></p><p>Correct answer: <strong>{x.correct_answer}</strong></p><p>{x.working}</p></details>)}</div>:<p>No incorrect answers recorded yet.</p>}</section>
  <section className="grid2"><HomeAssistantConnection/><section className="panel"><h2><Database size={20}/> Backups</h2>{backupError&&<ErrorNotice message={`Backups are temporarily unavailable. ${backupError}`} retry={()=>void load()} dismiss={()=>setBackupError('')}/>}<button onClick={backup}>Create backup now</button><div className="backup-list">{backups.map(b=><span key={b.filename}>{b.filename} · {(b.size/1024).toFixed(0)} KB</span>)}</div></section></section></main></>}

const rootElement=document.getElementById('root');
if(rootElement)createRoot(rootElement).render(<App/>);