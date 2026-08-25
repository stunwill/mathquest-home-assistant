import React, { useEffect, useMemo, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  CheckCircle2, ChevronLeft, ChevronRight, Database, Download, Eye, Flame, Lightbulb, List,
  LogOut, Play, Settings, SkipForward, Sparkles, Star, Trophy, X
} from 'lucide-react';
import './styles.css';
import {APP_VERSION} from './version';
import {apiRequest as req, createSession, loadActiveWorksheet, questionDraft, rememberActiveWorksheet, rememberQuestionDraft} from './api';
import {ErrorNotice, LearningCalendar, StoryAdventures, WorksheetHistory} from './student-foundation';
import {MathsLab} from './maths-lab';
import {MissionOutcome, StoryMissionProgress} from './story-adventure';
import {AdaptiveRecommendation} from './adaptive-recommendation';
import {HomeAssistantConnection, ParentLearningInsight} from './parent-insight';
import {ParentLearningIntelligence} from './parent-intelligence';
import {ParentTestWorksheets, TestQuestionFeedback, TestWorksheetResult} from './parent-testing';
import {InterventionCard, InterventionGoal} from './intervention';
import {QuestionVisual} from './question-visual';
import {ConfidenceCheck, QuestionTools} from './question-tools';
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

function App(){
  const[user,setUser]=useState<User|null>(null);
  const[loading,setLoading]=useState(true);
  const[error,setError]=useState('');
  const restore=()=>{setLoading(true);setError('');req<User>('/me').then(setUser).catch((e:Error)=>{if(localStorage.getItem('token'))setError(e.message)}).finally(()=>setLoading(false))};
  useEffect(restore,[]);
  if(loading)return <div className="splash"><Brand/></div>;
  if(error)return <main className="login"><section className="login-card"><Brand/><ErrorNotice message={error} retry={restore}/><button type="button" onClick={()=>{localStorage.clear();setError('')}}>Sign in again</button></section></main>;
  if(!user)return <Login onLogin={setUser}/>;
  const logout=()=>{localStorage.clear();setUser(null)};
  return user.role==='parent'?<Parent user={user} logout={logout}/>:<Student user={user} logout={logout}/>;
}

function Login({onLogin}:{onLogin:(u:User)=>void}){
  const[username,setUsername]=useState('student');
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
  const load=()=>{setError('');Promise.all([req('/dashboard/student'),loadActiveWorksheet<WorksheetData>(),req('/learning/adaptive-v0230').catch(()=>null)]).then(([nextDashboard,nextWorksheet,nextAdaptive])=>{setDashboard(nextDashboard);setWorksheet(nextWorksheet);setAdaptive(nextAdaptive);if(nextWorksheet&&!nextWorksheet.completed_at&&sessionStorage.getItem('mq_open_worksheet')==='1'){sessionStorage.removeItem('mq_open_worksheet');setWorking(true)}}).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  useEffect(()=>{(window as any).__mq_ws=worksheet},[worksheet]);
  const openWorksheet=(next:WorksheetData)=>{setWorksheet(next);setSummary(null);setChoosing(false);setWorking(true)};
  const startWorksheet=async(topic:string,minutes:5|10|15,kind:'practice'|'diagnostic')=>openWorksheet(await createSession<WorksheetData>(kind,minutes,topic));
  const startRecommended=async()=>{setRecommendationBusy(true);setError('');try{const next=await req<WorksheetData>('/sessions/recommended',{method:'POST'});rememberActiveWorksheet(next.id);openWorksheet(next)}catch(e:any){setError(e.message)}finally{setRecommendationBusy(false)}};
  if(!dashboard&&error)return <><Header user={user} logout={logout}/><main className="page"><ErrorNotice message={error} retry={load}/></main></>;
  if(!dashboard)return <div className="splash"><Brand/></div>;
  if(working&&worksheet&&!worksheet.completed_at&&!summary)return <Worksheet ws={worksheet} onUpdate={setWorksheet} onExit={()=>{setWorking(false);load()}} onDone={x=>{setSummary(x);setWorking(false);load()}}/>;
  if(summary)return <Result data={summary} back={()=>{setSummary(null);load()}}/>;
  if(choosing)return <QuestCategoryPicker cancel={()=>setChoosing(false)} start={startWorksheet}/>;
  const hasProgress=worksheet&&!worksheet.completed_at;
  return <><Header user={user} logout={logout}/><main className="page">
    {error&&<ErrorNotice message={error} retry={load} dismiss={()=>setError('')}/>}<section className="hero"><div><p className="eyebrow">TODAY’S ADVENTURE</p><h1>{hasProgress?'Your quest is waiting':'Ready to power up your maths?'}</h1>
      <p>{hasProgress?`${worksheet.counts.correct+worksheet.counts.incorrect} of ${worksheet.total} questions completed. Your progress is saved.`:'Complete one worksheet, strengthen weak spots and keep your streak alive.'}</p>
      <button className="primary" disabled={!!worksheet?.completed_at} onClick={()=>{if(worksheet){setWorking(true)}else{setChoosing(true)}}><Play size={20}/>{worksheet?.completed_at?'Today complete':hasProgress?'Continue Today’s Quest':'Begin Today’s Adventure'}</button>
    </div><div className="level-orb"><small>LEVEL</small><strong>{dashboard.user.level}</strong><span>{dashboard.user.xp%250}/250 XP</span></div></section>
    {!hasProgress&&<AdaptiveRecommendation data={adaptive} busy={recommendationBusy} onStart={startRecommended}/>} {!hasProgress&&<InterventionCard onOpen={openWorksheet}/>}<StoryAdventures onOpen={openWorksheet}/><WorksheetHistory onCreate={()=>setChoosing(true)} onOpen={openWorksheet}/><section className="cards"><Metric icon={<Flame/>} label="Daily streak" value={`${dashboard.streak} days`}/><Metric icon={<CheckCircle2/>} label="Accuracy" value={`${dashboard.accuracy}%`}/><Metric icon={<Star/>} label="Questions" value={dashboard.questions_answered}/><Metric icon={<Trophy/>} label="Highest level" value={dashboard.user.highest_level}/></section><section className="panel"><h2>Skill map</h2><div className="skills">{dashboard.skills.map((s:any)=><div className="skill" key={s.topic}><div><b>{s.topic}</b><span>Level {s.level}</span></div><div className="bar"><i style={{width:`${s.accuracy}%`}}/></div><small>{s.accuracy}% accuracy</small></div>)}</div></section><LearningCalendar onOpen={openWorksheet}/></main></>;
}

const QUEST_CATEGORIES=[{id:'number_algebra',icon:'🎯',name:'Number & Algebra Focus',description:'Recommended: number facts, efficient strategies and missing-number equations'},{id:'measurement',icon:'📏',name:'Measurement',description:'Length, area, perimeter, time, temperature and angles'},{id:'algebra',icon:'🧩',name:'Algebra',description:'Unknown values, patterns and number facts'},{id:'probability',icon:'🎲',name:'Probability',description:'Chance, likelihood and repeated experiments'},{id:'number',icon:'🔢',name:'Number',description:'Place value, fractions, operations, money and estimation'},{id:'space',icon:'⬡',name:'Space',description:'Shapes, grids, symmetry and position'},{id:'statistics',icon:'📊',name:'Statistics',description:'Data, graphs, surveys and investigations'},{id:'mixed',icon:'✨',name:'Mixed Adventure',description:'A balanced quest across all learning areas'}];

export function QuestCategoryPicker({start,cancel}:{start:(topic:string,minutes:5|10|15,kind:'practice'|'diagnostic')=>Promise<void>;cancel:()=>void}){const[selected,setSelected]=useState('mixed'),[minutes,setMinutes]=useState<5|10|15>(10),[kind,setKind]=useState<'practice'|'diagnostic'>('practice'),[busy,setBusy]=useState(false),[printBusy,setPrintBusy]=useState(false),[error,setError]=useState('');async function printWorksheet(){setPrintBusy(true);setError('');try{const blob=await req<Blob>('/worksheets/today/print',{method:'POST',body:JSON.stringify({topic:selected})});const link=document.createElement('a');link.href=URL.createObjectURL(blob);link.download=`mathquest-${selected}-worksheet.pdf`;link.click();URL.revokeObjectURL(link.href)}catch(reason:any){setError(reason.message)}finally{setPrintBusy(false)}}return <main className="category-page"><section className="category-card"><Brand compact/><p className="eyebrow">CHOOSE TODAY’S SESSION</p><h1>How would you like to learn?</h1><div className="session-kind" role="group" aria-label="Session type"><button type="button" aria-pressed={kind==='practice'} className={kind==='practice'?'selected':''} onClick={()=>setKind('practice')}><b>Targeted practice</b><small>Work towards the Level 5 pathway</small></button><button type="button" aria-pressed={kind==='diagnostic'} className={kind==='diagnostic'?'selected':''} onClick={()=>{setKind('diagnostic');setMinutes(15)}}><b>Levels 2–6 diagnostic</b><small>Find a starting point across Number and Algebra</small></button></div>{kind==='practice'&&<><p>Choose a session length and learning area.</p><div className="duration-options" role="group" aria-label="Session length">{([5,10,15] as const).map(value=><button type="button" aria-pressed={minutes===value} key={value} className={minutes===value?'selected':''} onClick={()=>setMinutes(value)}><b>{value} minutes</b><small>{value===5?'Quick boost':value===10?'Daily session':'Deep practice'}</small></button>)}</div><div className="category-grid" role="group" aria-label="Learning area">{QUEST_CATEGORIES.map(c=><button type="button" aria-pressed={selected===c.id} key={c.id} className={'category-option '+(selected===c.id?'selected':'')} onClick={()=>setSelected(c.id)}><span>{c.icon}</span><b>{c.name}</b><small>{c.description}</small></button>)}</div></>}{kind==='diagnostic'&&<div className="diagnostic-note"><b>About 15 minutes</b><p>Three short questions at each Victorian Curriculum level from 2 to 6. Results identify a baseline; Level 5 remains the learning target.</p></div>}{error&&<p className="category-error" role="alert">{error}</p>}<div className="category-actions"><button onClick={cancel}>Back</button>{kind==='practice'&&<button type="button" disabled={printBusy} onClick={printWorksheet}><Download size={18}/>{printBusy?'Preparing PDF…':'Print worksheet'}</button>}<button className="primary" disabled={busy} onClick={async()=>{setBusy(true);try{await start(kind==='diagnostic'?'number_algebra':selected,minutes,kind)}finally{setBusy(false)}}}><Play size={20}/>{busy?'Building your session…':kind==='diagnostic'?'Start diagnostic':`Start ${minutes}-minute session`}</button></div></section></main>}

function Metric({icon,label,value}:any){return <div className="metric">{icon&&<i>{icon}</i>}<div><small>{label}</small><strong>{value}</strong></div></div>}
function StrategyCard({card}:{card:any}){if(!card)return null;return <div className="mq-strategy-card"><div><span>🧠</span><p><small>STRATEGY FOR THIS QUESTION</small><b>{card.title}</b></p></div><h3>{card.strategy}</h3><p className="mq-strategy-rule">{card.rule}</p><ol>{(card.steps||[]).map((step:string)=><li key={step}>{step}</li>)}</ol>{card.example&&<small className="mq-strategy-example">{card.example}</small>}</div>}

function MathStep({step}:{step:any}){return <div className="mentor-step"><small>{step.label}</small>{step.text&&<p>{step.text}</p>}{Array.isArray(step.math)&&<div className="mentor-math">{step.math.map((line:string)=><code key={line}>{line}</code>)}</div>}</div>}

function MathMentor({support,open,setOpen,onHint,onAction,onStartOver,busy,canStartOver,onOpenLab}:{support:any;open:boolean;setOpen:(open:boolean)=>void;onHint:()=>Promise<void>;onAction:(action:string)=>Promise<void>;onStartOver:()=>Promise<void>;busy:boolean;canStartOver:boolean;onOpenLab:()=>void}){
  const[spokenError,setSpokenError]=useState('');
  const readAloud=()=>{const stepText=(support?.teach_steps||[]).flatMap((step:any)=>[step.label,step.text,...(step.math||[])]);const result=speakText([support?.title,support?.guiding_question,support?.body,...stepText,support?.worked_example,support?.visual_connection].filter(Boolean).join('. '));if(!result.supported)setSpokenError(result.message)};
  const stageLabel=support?.action==='hint'?`${String(support.hint_kind||'hint').replaceAll('_',' ')} · ${support.stage} of 3`:support?.action==='teach'?'Mini lesson':support?.action==='why'?'Concept explanation':support?.action==='worked_example'?'Different-number example':'Ask before tell';
  return <section className={'math-mentor '+(open?'open':'')} data-guided-tutor="true"><button type="button" className="math-mentor-toggle" aria-expanded={open} onClick={()=>setOpen(!open)}><span aria-hidden="true">🧑‍🏫</span><span><small>MATH MENTOR</small><b>{support?.strategy_name||support?.title||'Get help without giving away the answer'}</b></span><span aria-hidden="true">{open?'⌃':'⌄'}</span></button>{open&&<div className="math-mentor-body" aria-live="polite">{support?<><p className="math-mentor-stage">{stageLabel}</p><h3>{support.action==='guide'?'Try this first':support.action==='why'?'Why this works':support.action==='teach'?'Teach me':support.action==='hint'?'Use this next':'Worked example'}</h3>{support.body&&<p className="mentor-body-copy">{support.body}</p>}{support.action==='teach'&&Array.isArray(support.teach_steps)&&<div className="mentor-lesson">{support.teach_steps.map((step:any,index:number)=><MathStep key={`${step.label}-${index}`} step={step}/>)}</div>}{support.visual_recommendation&&<div className="guided-misconception"><b>Visual strategy</b><p>{support.visual_recommendation.message}</p><button type="button" onClick={onOpenLab}>Open {String(support.visual_recommendation.model).replaceAll('-',' ')} model</button></div>}{support.evidence_visual_recommendation&&<div className="guided-misconception"><b>Based on recent practice</b><p>{support.evidence_visual_recommendation.message}</p></div>}{support.common_mistake&&<div className="guided-misconception"><b>Common mistake to watch for</b><p>{support.common_mistake}</p></div>}{support.action==='worked_example'&&<div className="guided-example"><b>Same skill, different numbers</b><p>{support.worked_example}</p><small>Use the same structure on your question, not the example’s answer.</small></div>}</>:<p>Choose the kind of help you want. You can keep typing or checking an answer at any time.</p>}<div className="guided-actions"><button type="button" disabled={busy} onClick={()=>onHint()}>💡 Hint</button><button type="button" disabled={busy} onClick={()=>onAction('why')}>Why?</button><button type="button" disabled={busy} onClick={()=>onAction('teach')}>Teach me</button><button type="button" disabled={busy} onClick={()=>onAction('worked_example')}>Worked example</button>{canStartOver&&<button type="button" disabled={busy} onClick={()=>onStartOver()}>↻ Start over</button>}<button type="button" onClick={readAloud}>🔊 Read aloud</button></div>{spokenError&&<p role="status" className="math-mentor-speech">{spokenError}</p>}</div>}</section>
}

export function Worksheet({ws,onUpdate,onExit,onDone}:{ws:WorksheetData;onUpdate:(x:WorksheetData)=>void;onExit:()=>void;onDone:(x:any)=>void}){
  const[answer,setAnswer]=useState(''),[feedback,setFeedback]=useState<any>(null),[hint,setHint]=useState<string|null>(null),[support,setSupport]=useState<any>(null),[mentorOpen,setMentorOpen]=useState(false),[hintBusy,setHintBusy]=useState(false),[questionStart,setQuestionStart]=useState(Date.now()),[sessionStart]=useState(Date.now()-(ws.elapsed_seconds||0)*1000),[overview,setOverview]=useState(false),[confirmExit,setConfirmExit]=useState(false),[labOpen,setLabOpen]=useState(false),[actionError,setActionError]=useState('');
  const actionBusy=useRef(false);const active=useMemo(()=>ws.questions.find(q=>q.id===ws.current_question_id)||nextEligible(ws),[ws]);const q=active;const completed=ws.counts.correct+ws.counts.incorrect;const phase=ws.current_phase==='skipped'||(!ws.questions.some(x=>['not_started','current','retry_available'].includes(x.status))&&ws.counts.skipped>0)?'skipped':'main';const previous=previousEligible(ws,q?.id);const canFinishWithSkipped=ws.questions.every(item=>['correct','incorrect','skipped'].includes(item.status)||(item.skipped_count>0&&!item.attempts.length));
  useEffect(()=>{if(q&&q.id!==ws.current_question_id)void safe(()=>goTo(q.id))},[]);useEffect(()=>{setHint(q?.last_hint||null);setSupport(null);setMentorOpen(false);setAnswer(q?questionDraft(ws.id,q.id):'')},[q?.id,ws.id]);
  async function safe(action:()=>Promise<void>){if(actionBusy.current)return;actionBusy.current=true;setActionError('');try{await action()}catch(e:any){setActionError(e.message||'MathQuest could not complete that action.')}finally{actionBusy.current=false}}
  function elapsed(){return (Date.now()-sessionStart)/1000}async function refresh(updated?:WorksheetData){const data:WorksheetData=updated||await req<WorksheetData>(`/worksheets/${ws.id}/view`);onUpdate(data);setAnswer('');setFeedback(null);setHint(null);setSupport(null);setQuestionStart(Date.now())}async function goTo(id:number){const updated=await req(`/worksheets/${ws.id}/navigate/${id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});await refresh(updated)}
  async function check(){if(!q||!answer.trim())return;rememberQuestionDraft(ws.id,q.id,answer);await safe(async()=>{const result=await req(`/worksheets/${ws.id}/questions/${q.id}/answer`,{method:'POST',body:JSON.stringify({answer,seconds_spent:(Date.now()-questionStart)/1000,elapsed_seconds:elapsed()})});setFeedback(result);if(result?.worksheet)onUpdate(result.worksheet);if(result?.correct)rememberQuestionDraft(ws.id,q.id,'')})}
  async function skip(){if(!q)return;await safe(async()=>refresh(await req(`/worksheets/${ws.id}/questions/${q.id}/skip`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})})))}
  async function getHint(){if(!q)return;setHintBusy(true);try{const result:any=await req(`/worksheets/${ws.id}/questions/${q.id}/hint`,{method:'POST'});setHint(result.hint);setSupport(result.support||null);setMentorOpen(true)}finally{setHintBusy(false)}}
  async function mentorAction(action:string){if(!q)return;setHintBusy(true);try{const result:any=await req(`/worksheets/${ws.id}/questions/${q.id}/support`,{method:'POST',body:JSON.stringify({action})});setSupport(result);setMentorOpen(true)}finally{setHintBusy(false)}}
  async function startOver(){if(!q)return;rememberQuestionDraft(ws.id,q.id,'');await safe(async()=>refresh(await req(`/worksheets/${ws.id}/questions/${q.id}/start-over`,{method:'POST'})))}
  async function finish(){await safe(async()=>{const result=await req(`/worksheets/${ws.id}/complete`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});onDone(result)})}
  if(!q)return <main className="worksheet-page"><section className="question-card"><h1>No question is currently available.</h1><button onClick={onExit}>Back</button></section></main>;
  return <main className="worksheet-page"><section className="worksheet-shell"><div className="worksheet-topbar"><button className="ghost" onClick={()=>setConfirmExit(true)}><ChevronLeft size={18}/> Exit</button><div className="worksheet-progress"><span>{completed}/{ws.total}</span><div><i style={{width:`${Math.min(100,(completed/ws.total)*100)}%`}}/></div><small>{phase==='skipped'?'Skipped review':'Main questions'}</small></div><button className="ghost" onClick={()=>setOverview(true)}><List size={18}/> Questions</button></div>{actionError&&<ErrorNotice message={actionError} dismiss={()=>setActionError('')}/>}<StoryMissionProgress worksheet={ws}/><InterventionGoal question={q}/><section className="question-card"><div className="question-meta"><span>{q.topic.replaceAll('_',' ')}</span><span>Question {q.position+1}</span></div><QuestionVisual question={q}/><h1>{q.prompt}</h1><Answer q={q} value={answer} setValue={value=>{setAnswer(value);rememberQuestionDraft(ws.id,q.id,value)}}/>{feedback&&<div className={'feedback '+(feedback.correct?'correct':'incorrect')}><b>{feedback.correct?'Correct!':'Try again'}</b><p>{feedback.message}</p></div>}<QuestionTools question={q} worksheetId={ws.id} answer={answer} onOpenLab={()=>setLabOpen(true)} onSupport={setSupport}/><MathMentor support={support} open={mentorOpen} setOpen={setMentorOpen} onHint={getHint} onAction={mentorAction} onStartOver={startOver} busy={hintBusy} canStartOver={q.attempts.length>0} onOpenLab={()=>setLabOpen(true)}/>{hint&&<div className="hint"><Lightbulb size={18}/>{hint}</div>}{ws.test_mode&&<TestQuestionFeedback worksheetId={ws.id} question={q}/>}<div className="question-actions"><button disabled={!previous} onClick={()=>previous&&safe(()=>goTo(previous.id))}><ChevronLeft size={18}/> Previous</button><button onClick={skip}><SkipForward size={18}/> Skip</button><button className="primary" disabled={!answer.trim()} onClick={check}>Check answer</button></div>{canFinishWithSkipped&&<button className="finish-with-skipped" onClick={finish}>Finish worksheet</button>}</section>{feedback?.mission&&<MissionOutcome mission={feedback.mission}/>}</section>{overview&&<QuestionOverview ws={ws} activeId={q.id} close={()=>setOverview(false)} goTo={id=>{setOverview(false);safe(()=>goTo(id))}}/>}{confirmExit&&<ConfirmExit cancel={()=>setConfirmExit(false)} exit={onExit}/>}<MathsLab open={labOpen} onClose={()=>setLabOpen(false)} question={q}/></main>
}

function nextEligible(ws:WorksheetData){return ws.questions.find(q=>['not_started','current','retry_available'].includes(q.status))||ws.questions.find(q=>q.status==='skipped')||null}
function previousEligible(ws:WorksheetData,id?:number){if(id==null)return null;const index=ws.questions.findIndex(q=>q.id===id);for(let i=index-1;i>=0;i--){if(!['correct','incorrect'].includes(ws.questions[i].status))return ws.questions[i]}return null}
function statusLabel(status:string){return status.replaceAll('_',' ')}
function QuestionOverview({ws,activeId,close,goTo}:{ws:WorksheetData;activeId:number;close:()=>void;goTo:(id:number)=>void}){return <div className="modal-backdrop"><section className="overview-modal"><div className="modal-title"><div><p className="eyebrow">WORKSHEET MAP</p><h2>All questions</h2></div><button className="icon-button" onClick={close}><X/></button></div><div className="question-table"><div className="question-table-head"><b>#</b><b>Question</b><b>Status</b></div>{ws.questions.map(q=>{const locked=['correct','incorrect'].includes(q.status);return <button disabled={locked} className={'question-row '+(q.id===activeId?'active':'')} key={q.id} onClick={()=>goTo(q.id)}><span>{q.position+1}</span><span>{q.summary||q.prompt}</span><span className={'status '+q.status}>{statusLabel(q.status)}</span></button>})}</div><button onClick={close}>Close</button></section></div>}
function ConfirmExit({cancel,exit}:{cancel:()=>void;exit:()=>void}){return <div className="modal-backdrop"><section className="confirm-modal"><h2>Exit worksheet?</h2><p>Your current progress and typed answer will be saved.</p><div><button onClick={cancel}>Keep learning</button><button className="danger" onClick={exit}>Save and exit</button></div></section></div>}
function FractionShape({parts,shaded}:{parts:number;shaded:number}){return <div className="fraction-shape">{Array.from({length:parts},(_,i)=><i className={i<shaded?'filled':''} key={i}/>)}</div>}
function Answer({q,value,setValue}:{q:Question;value:string;setValue:(x:string)=>void}){const inputRef=useRef<HTMLInputElement|null>(null);useEffect(()=>{if(q.answer_type!=='multiple_choice')inputRef.current?.focus()},[q.id,q.answer_type]);if(q.answer_type==='multiple_choice'){return <div className="choice-grid">{(q.payload?.choices||[]).map((choice:any)=><button type="button" className={String(value)===String(choice)?'selected':''} key={String(choice)} onClick={()=>setValue(String(choice))}>{String(choice)}</button>)}</div>}return <input ref={inputRef} className="answer-input" value={value} onChange={e=>setValue(e.target.value)} inputMode="decimal" aria-label="Your answer"/>}
function Result({data,back}:{data:any;back:()=>void}){return <main className="result-page"><section className="result-card"><Sparkles size={42}/><h1>Quest complete!</h1><p>{data.message||'Great work today.'}</p><div className="result-stats"><Metric label="Score" value={`${data.score}/${data.total}`}/><Metric label="Accuracy" value={`${data.accuracy}%`}/><Metric label="XP" value={`+${data.xp_earned}`}/></div>{data.strongest&&<p><b>Strongest:</b> {data.strongest}</p>}{data.practise_next&&<p><b>Practise next:</b> {data.practise_next}</p>}<button className="primary" onClick={back}>Back to dashboard</button></section></main>}

function Parent({user,logout}:{user:User;logout:()=>void}){
  const[d,setD]=useState<any>(null),[settings,setSettings]=useState<any>(null),[backups,setBackups]=useState<any[]>([]),[error,setError]=useState(''),[period,setPeriod]=useState(30),[intelligence,setIntelligence]=useState<any>(null),[worksheet,setWorksheet]=useState<WorksheetData|null>(null),[summary,setSummary]=useState<any>(null);
  const load=()=>{setError('');Promise.all([req('/dashboard/parent'),req('/settings'),req('/backups'),req('/learning/parent-insight').catch(()=>null),req(`/learning/parent-intelligence-v0320?days=${period}`).catch(()=>null)]).then(([a,b,c,legacyInsight,newInsight])=>{setD({...a,legacyInsight});setSettings(b);setBackups(c);setIntelligence(newInsight)}).catch((e:Error)=>setError(e.message))};
  useEffect(load,[period]);
  if(worksheet&&!worksheet.completed_at&&!summary)return <Worksheet ws={worksheet} onUpdate={setWorksheet} onExit={()=>{setWorksheet(null);load()}} onDone={x=>{setSummary(x);setWorksheet(null);load()}}/>;
  if(summary)return <TestWorksheetResult data={summary} onDone={()=>{setSummary(null);load()}}/>;
  if(!d||!settings)return <div className="splash"><Brand/></div>;
  async function save(){await req('/settings',{method:'PUT',body:JSON.stringify(settings)});load()}
  async function backup(){await req('/backups',{method:'POST'});load()}
  const statusText=(value:string)=>value==='secure'?'Secure':value==='developing'?'Developing':value==='concern'?'Needs support':value.replaceAll('_',' ');
  const openWorksheet=(next:any)=>setWorksheet(next);
  return <><Header user={user} logout={logout}/><main className="page parent-page">{error&&<ErrorNotice message={error} retry={load} dismiss={()=>setError('')}/>}<ParentLearningIntelligence data={intelligence} onPeriod={setPeriod}/>{d.legacyInsight&&<ParentLearningInsight data={d.legacyInsight}/>}<ParentTestWorksheets onOpen={openWorksheet}/>
  {d.concerns?.length>0&&<section className="panel concern-panel"><h2>⚑ Areas to review</h2><p>These outcomes currently have less than 70% first-attempt accuracy, or limited successful evidence.</p><div className="concern-grid">{d.concerns.map((x:any)=><div key={x.code}><b>{x.code}</b><span>{x.title}</span><strong>{x.accuracy}%</strong><small>{x.attempts} recent attempts</small></div>)}</div></section>}
  <section className="panel"><h2>MathQuest evidence by Victorian Curriculum outcome</h2><p>MathQuest reports observed learning evidence and does not formally certify curriculum achievement.</p><div className="curriculum-table"><div className="curriculum-head"><b>Outcome</b><b>Evidence</b><b>Accuracy</b><b>Status</b></div>{d.curriculum.map((x:any)=><div className="curriculum-row" key={x.code}><span><b>{x.code}</b><small>{x.strand} · {x.title}</small></span><span>{x.attempts} attempts</span><span>{x.attempts?`${x.accuracy}%`:'—'}</span><span className={'status-pill '+x.status}>{statusText(x.status)}</span></div>)}</div></section>
  <section className="grid2"><div className="panel"><h2>Strand performance</h2>{d.skills.map((s:any)=><div className="skill" key={s.topic}><div><b>{s.topic}</b><span>Adaptive level {s.level}</span></div><div className="bar"><i style={{width:`${s.accuracy}%`}}/></div><small>{s.accuracy}% · {s.avg_seconds}s average</small></div>)}</div><div className="panel"><h2><Settings size={20}/> Worksheet settings</h2><label>Questions per day<input type="number" min="5" max="50" value={settings.question_count} onChange={e=>setSettings({...settings,question_count:+e.target.value})}/></label><label className="toggle"><input type="checkbox" checked={settings.adaptive_mode} onChange={e=>setSettings({...settings,adaptive_mode:e.target.checked})}/> Adaptive learning</label><div className="topic-checks">{['number','algebra','measurement','space','statistics','probability'].map(t=><label key={t}><input type="checkbox" checked={settings.enabled_topics.includes(t)} onChange={e=>setSettings({...settings,enabled_topics:e.target.checked?[...settings.enabled_topics,t]:settings.enabled_topics.filter((x:string)=>x!==t)})}/>{t}</label>)}</div><button className="primary" onClick={save}>Save settings</button></div></section>
  <section className="panel"><h2>Recent incorrect answers</h2>{d.recent_incorrect.length?<div className="incorrect-list">{d.recent_incorrect.map((x:any,i:number)=><details key={i}><summary><b>{x.code||'Practice'}</b> {x.prompt}</summary><p>Student answer: <strong>{x.student_answer}</strong></p><p>Correct answer: <strong>{x.correct_answer}</strong></p><p>{x.working}</p></details>)}</div>:<p>No incorrect answers recorded yet.</p>}</section>
  <section className="grid2"><HomeAssistantConnection/><section className="panel"><h2><Database size={20}/> Backups</h2><button onClick={backup}>Create backup now</button><div className="backup-list">{backups.map(b=><span key={b.filename}>{b.filename} · {(b.size/1024).toFixed(0)} KB</span>)}</div></section></section></main></>}

const rootElement=document.getElementById('root');
if(rootElement)createRoot(rootElement).render(<App/>);