import React, { useEffect, useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  CheckCircle2, ChevronRight, Database, Download, Eye, Flame, Lightbulb, List,
  LogOut, Play, Settings, SkipForward, Sparkles, Star, Trophy, X
} from 'lucide-react';
import './styles.css';
import {APP_VERSION} from './version';

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
  counts:{correct:number;incorrect:number;skipped:number;remaining:number;hints:number}; questions:Question[];
};

async function req(path:string, opts:any={}) {
  const token=localStorage.getItem('token');
  const response=await fetch(API+path,{
    ...opts,
    headers:{
      ...(opts.body instanceof FormData?{}:{'Content-Type':'application/json'}),
      ...(token?{Authorization:`Bearer ${token}`}:{}) ,...opts.headers
    }
  });
  if(!response.ok) throw new Error((await response.json()).detail||'Request failed');
  const type=response.headers.get('content-type')||'';
  return type.includes('json')?response.json():response.blob();
}

function Brand({compact=false}:{compact?:boolean}){
  return <div className={'mq-brand '+(compact?'compact':'')} aria-label="MathQuest by Stu">
    <div className="mq-emblem" aria-hidden="true"><span>+</span><span>×</span><span>−</span><span>÷</span></div>
    <div className="mq-wordmark-wrap"><strong className="mq-wordmark">MathQuest</strong><span className="mq-by-stu">by Stu</span></div>
  </div>;
}

function App(){
  const[user,setUser]=useState<User|null>(null);
  const[loading,setLoading]=useState(true);
  useEffect(()=>{req('/me').then(setUser).catch(()=>{}).finally(()=>setLoading(false))},[]);
  if(loading)return <div className="splash"><Brand/></div>;
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
  const load=()=>{req('/dashboard/student').then(setDashboard);req('/worksheets/today').then(setWorksheet)};
  useEffect(load,[]);
  if(!dashboard)return <div className="splash"><Brand/></div>;
  if(working&&worksheet&&!worksheet.completed_at&&!summary)return <Worksheet ws={worksheet} onUpdate={setWorksheet} onExit={()=>{setWorking(false);load()}} onDone={x=>{setSummary(x);setWorking(false);load()}}/>;
  if(summary)return <Result data={summary} back={()=>{setSummary(null);load()}}/>;
  if(choosing&&!worksheet)return <QuestCategoryPicker cancel={()=>setChoosing(false)} start={async topic=>{const next=await req('/worksheets/today',{method:'POST',body:JSON.stringify({topic})});setWorksheet(next);setChoosing(false);setWorking(true)}}/>;
  const hasProgress=worksheet&&!worksheet.completed_at;
  return <><Header user={user} logout={logout}/><main className="page">
    <section className="hero"><div><p className="eyebrow">TODAY’S ADVENTURE</p><h1>{hasProgress?'Your quest is waiting':'Ready to power up your maths?'}</h1>
      <p>{hasProgress?`${worksheet.counts.correct+worksheet.counts.incorrect} of ${worksheet.total} questions completed. Your progress is saved.`:'Complete one worksheet, strengthen weak spots and keep your streak alive.'}</p>
      <button className="primary" disabled={!!worksheet?.completed_at} onClick={()=>{
        if(worksheet){setWorking(true)}else{setChoosing(true)}
      }}><Play size={20}/>{worksheet?.completed_at?'Today complete':hasProgress?'Continue Today’s Quest':'Begin Today’s Adventure'}</button>
    </div><div className="level-orb"><small>LEVEL</small><strong>{dashboard.user.level}</strong><span>{dashboard.user.xp%250}/250 XP</span></div></section>
    <section className="cards"><Metric icon={<Flame/>} label="Daily streak" value={`${dashboard.streak} days`}/><Metric icon={<CheckCircle2/>} label="Accuracy" value={`${dashboard.accuracy}%`}/><Metric icon={<Star/>} label="Questions" value={dashboard.questions_answered}/><Metric icon={<Trophy/>} label="Highest level" value={dashboard.user.highest_level}/></section>
    <section className="panel"><h2>Skill map</h2><div className="skills">{dashboard.skills.map((s:any)=><div className="skill" key={s.topic}><div><b>{s.topic}</b><span>Level {s.level}</span></div><div className="bar"><i style={{width:`${s.accuracy}%`}}/></div><small>{s.accuracy}% accuracy</small></div>)}</div></section>
    <section className="grid2"><div className="panel"><h2>Completion calendar</h2><Calendar items={dashboard.calendar}/></div><div className="panel"><h2>Badges</h2><div className="badges">{dashboard.badges.length?dashboard.badges.map((b:string)=><span key={b}>⭐ {b}</span>):<p>Your first badge is waiting.</p>}</div></div></section>
  </main></>;
}

const QUEST_CATEGORIES=[
  {id:'number_algebra',icon:'🎯',name:'Number & Algebra Focus',description:'Recommended: number facts, efficient strategies and missing-number equations'},
  {id:'measurement',icon:'📏',name:'Measurement',description:'Length, area, perimeter, time, temperature and angles'},
  {id:'algebra',icon:'🧩',name:'Algebra',description:'Unknown values, patterns and number facts'},
  {id:'probability',icon:'🎲',name:'Probability',description:'Chance, likelihood and repeated experiments'},
  {id:'number',icon:'🔢',name:'Number',description:'Place value, fractions, operations, money and estimation'},
  {id:'space',icon:'⬡',name:'Space',description:'Shapes, grids, symmetry and position'},
  {id:'statistics',icon:'📊',name:'Statistics',description:'Data, graphs, surveys and investigations'},
  {id:'mixed',icon:'✨',name:'Mixed Adventure',description:'A balanced quest across all learning areas'}
];

function QuestCategoryPicker({start,cancel}:{start:(topic:string)=>Promise<void>;cancel:()=>void}){
  const[selected,setSelected]=useState('mixed');
  const[busy,setBusy]=useState(false);
  return <main className="category-page"><section className="category-card">
    <Brand compact/><p className="eyebrow">CHOOSE TODAY’S QUEST</p><h1>What would you like to practise?</h1><p>Pick one Victorian Curriculum learning area, or choose a mixed adventure.</p>
    <div className="category-grid">{QUEST_CATEGORIES.map(c=><button type="button" key={c.id} className={'category-option '+(selected===c.id?'selected':'')} onClick={()=>setSelected(c.id)}><span>{c.icon}</span><b>{c.name}</b><small>{c.description}</small></button>)}</div>
    <div className="category-actions"><button onClick={cancel}>Back</button><button className="primary" disabled={busy} onClick={async()=>{setBusy(true);try{await start(selected)}finally{setBusy(false)}}}><Play size={20}/>{busy?'Building your quest…':'Start this quest'}</button></div>
  </section></main>;
}

function Metric({icon,label,value}:any){return <div className="metric">{icon&&<i>{icon}</i>}<div><small>{label}</small><strong>{value}</strong></div></div>}
function StrategyCard({card}:{card:any}){if(!card)return null;return <div className="mq-strategy-card"><div><span>🧠</span><p><small>STRATEGY FOR THIS QUESTION</small><b>{card.title}</b></p></div><h3>{card.strategy}</h3><p className="mq-strategy-rule">{card.rule}</p><ol>{(card.steps||[]).map((step:string)=><li key={step}>{step}</li>)}</ol>{card.example&&<small className="mq-strategy-example">{card.example}</small>}</div>}
function Calendar({items}:{items:any[]}){const map=Object.fromEntries(items.map(x=>[x.date,x]));const now=new Date(),days=[];for(let i=27;i>=0;i--){const d=new Date(now);d.setDate(now.getDate()-i);const key=d.toISOString().slice(0,10),it=map[key];days.push(<div className={'day '+(it?.completed?'done':'')+(i===0?' today':'')} key={key}><small>{d.toLocaleDateString('en-AU',{weekday:'short'}).slice(0,1)}</small><b>{d.getDate()}</b><span>{it?.completed?'✓':''}</span>{it?.hints>0&&<em title={`${it.hints} hints used`}>💡{it.hints}</em>}</div>)}return <div className="calendar">{days}</div>}

function Worksheet({ws,onUpdate,onExit,onDone}:{ws:WorksheetData;onUpdate:(x:WorksheetData)=>void;onExit:()=>void;onDone:(x:any)=>void}){
  const[answer,setAnswer]=useState('');
  const[feedback,setFeedback]=useState<any>(null);
  const[hint,setHint]=useState<string|null>(null);
  const[hintBusy,setHintBusy]=useState(false);
  const[questionStart,setQuestionStart]=useState(Date.now());
  const[sessionStart]=useState(Date.now()-(ws.elapsed_seconds||0)*1000);
  const[overview,setOverview]=useState(false);
  const[confirmExit,setConfirmExit]=useState(false);

  const active=useMemo(()=>ws.questions.find(q=>q.id===ws.current_question_id)||nextEligible(ws),[ws]);
  const q=active;
  const completed=ws.counts.correct+ws.counts.incorrect;
  const phase=ws.current_phase==='skipped'||(!ws.questions.some(x=>['not_started','current','retry_available'].includes(x.status))&&ws.counts.skipped>0)?'skipped':'main';

  useEffect(()=>{if(q&&q.id!==ws.current_question_id)goTo(q.id)},[]);
  useEffect(()=>{setHint(q?.last_hint||null)},[q?.id,q?.last_hint]);
  function elapsed(){return (Date.now()-sessionStart)/1000}
  async function refresh(updated?:WorksheetData){const data=updated||await req('/worksheets/today');onUpdate(data);setAnswer('');setFeedback(null);setHint(null);setQuestionStart(Date.now())}
  async function goTo(id:number){const updated=await req(`/worksheets/${ws.id}/navigate/${id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});setOverview(false);await refresh(updated)}
  async function submit(){const cleaned=String(answer ?? '').trim();if(!cleaned)return;const result=await req(`/questions/${q.id}/answer`,{method:'POST',body:JSON.stringify({answer:cleaned,seconds:(Date.now()-questionStart)/1000})});setFeedback(result);if(result.correct||!result.retry_allowed){const latest=await req('/worksheets/today');onUpdate(latest)}}
  async function requestHint(){setHintBusy(true);try{const result=await req(`/questions/${q.id}/hint`,{method:'POST'});setHint(result.hint);const latest=await req('/worksheets/today');onUpdate(latest)}finally{setHintBusy(false)}}
  async function skip(){const updated=await req(`/questions/${q.id}/skip`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});const next=nextEligible(updated,q.id);if(next){const moved=await req(`/worksheets/${ws.id}/navigate/${next.id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});await refresh(moved)}else await refresh(updated)}
  async function next(){const latest:WorksheetData=await req('/worksheets/today');const target=nextEligible(latest,q.id);if(target){const moved=await req(`/worksheets/${ws.id}/navigate/${target.id}`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});await refresh(moved);return}onDone(await req(`/worksheets/${ws.id}/complete`,{method:'POST'}))}
  async function exit(){await req(`/worksheets/${ws.id}/save`,{method:'POST',body:JSON.stringify({elapsed_seconds:elapsed()})});onExit()}

  if(!q)return <div className="splash">Preparing your next question…</div>;
  const currentNumber=q.position+1;
  return <main className="worksheet-shell">
    <div className="worksheet-header"><button className="ghost danger-text" onClick={()=>setConfirmExit(true)}><X size={20}/> Exit worksheet</button><Brand compact/><button className="ghost" onClick={()=>setOverview(true)}><List size={20}/> Questions</button></div>
    <div className="worksheet-layout"><section className="worksheet-main">
      <div className="worksheet-top"><b>{phase==='skipped'?`Skipped round · ${ws.counts.skipped} remaining`:`Question ${currentNumber} of ${ws.total}`}</b><div className="progress"><i style={{width:`${completed/ws.total*100}%`}}/></div><span>{q.topic} · level {q.level}</span></div>
      <section className="question-card"><div className="question-icon">{({number:'🔢',algebra:'□',measurement:'📏',space:'⬡',statistics:'📊',probability:'🎲'} as any)[q.topic]||'✦'}</div><h1>{q.prompt}</h1>{q.payload?.shape&&<FractionShape parts={q.payload.shape.parts} shaded={q.payload.shape.shaded}/>}<Answer q={q} value={answer} setValue={setAnswer}/>
        {hint&&<><div className="hint-box"><Lightbulb size={22}/><div><b>Hint {q.hint_count||1}</b><p>{hint}</p></div></div><StrategyCard card={q.payload?.strategy_card}/></>}
        {!feedback?<><div className="support-actions"><button className="hint-button" disabled={hintBusy} onClick={requestHint}><Lightbulb size={19}/>{hintBusy?'Getting a hint…':q.hint_count>=2?'Show hint again':q.hint_count===1?'Another hint':'Give me a hint'}</button><small>Hints help with the next step and do not reduce the score.</small></div><div className="question-actions"><button className="skip" onClick={skip}><SkipForward size={19}/> Skip for now</button><button type="button" className="primary" disabled={!String(answer ?? '').trim()} onClick={submit}>Check answer</button></div></>:<div className={'feedback '+(feedback.correct?'correct':'wrong')}><h3>{feedback.correct?'✅ Great job!':'❌ '+feedback.message}</h3>{feedback.working&&<p>{feedback.working}</p>}{feedback.retry_allowed?<button onClick={()=>{setFeedback(null);setAnswer('')}}>Try again</button>:<button className="primary" onClick={next}>{ws.counts.remaining<=1?'Finish worksheet':'Next question'} <ChevronRight size={18}/></button>}</div>}
      </section>
    </section><WorksheetStatus ws={ws} q={q} open={()=>setOverview(true)}/></div>
    {overview&&<QuestionOverview ws={ws} activeId={q.id} close={()=>setOverview(false)} goTo={goTo}/>} {confirmExit&&<ConfirmExit cancel={()=>setConfirmExit(false)} exit={exit}/>} 
  </main>;
}

function nextEligible(ws:WorksheetData,afterId?:number){
  const sorted=[...ws.questions].sort((a,b)=>a.position-b.position);
  const start=Math.max(0,sorted.findIndex(q=>q.id===afterId)+1);
  const main=sorted.filter(q=>['not_started','current','retry_available'].includes(q.status));
  if(main.length){return [...main.filter(q=>q.position>=start),...main.filter(q=>q.position<start)][0]}
  const skipped=sorted.filter(q=>q.status==='skipped');
  return [...skipped.filter(q=>q.position>=start),...skipped.filter(q=>q.position<start)][0]||null;
}

function WorksheetStatus({ws,q,open}:{ws:WorksheetData;q:Question;open:()=>void}){return <aside className="worksheet-status"><p className="eyebrow">TODAY’S QUEST</p><h2>{ws.current_phase==='skipped'?'Skipped round':`Question ${q.position+1} / ${ws.total}`}</h2><div className="progress"><i style={{width:`${(ws.counts.correct+ws.counts.incorrect)/ws.total*100}%`}}/></div><dl><div><dt>Completed</dt><dd>{ws.counts.correct+ws.counts.incorrect}</dd></div><div><dt>Correct</dt><dd className="green">{ws.counts.correct}</dd></div><div><dt>Incorrect</dt><dd className="red">{ws.counts.incorrect}</dd></div><div><dt>Hints</dt><dd className="purple">{ws.counts.hints||0}</dd></div><div><dt>Skipped</dt><dd className="amber">{ws.counts.skipped}</dd></div><div><dt>Remaining</dt><dd>{ws.counts.remaining}</dd></div></dl><button className="wide" onClick={open}><Eye size={18}/> View all questions</button></aside>}

function statusLabel(status:QuestionStatus){return({not_started:'Not started',current:'Current',skipped:'Skipped',correct:'Correct',incorrect:'Incorrect',retry_available:'Retry available'} as any)[status]}
function QuestionOverview({ws,activeId,close,goTo}:{ws:WorksheetData;activeId:number;close:()=>void;goTo:(id:number)=>void}){return <div className="modal-backdrop"><section className="overview-modal"><div className="modal-title"><div><p className="eyebrow">WORKSHEET MAP</p><h2>All questions</h2></div><button className="icon-button" onClick={close}><X/></button></div><div className="question-table"><div className="question-table-head"><b>#</b><b>Question</b><b>Status</b></div>{ws.questions.map(q=>{const locked=['correct','incorrect'].includes(q.status);return <button key={q.id} className={'question-row '+(q.id===activeId?'active':'')} disabled={locked} onClick={()=>goTo(q.id)}><span>{q.position+1}</span><span><b>{q.summary}</b><small>{q.topic} · {q.skill.replaceAll('_',' ')}{q.hint_count?` · 💡 ${q.hint_count}`:''}</small></span><span className={'status-pill '+q.status}>{statusLabel(q.status)}</span></button>})}</div><p className="overview-note">Completed questions are read-only. Skipped and unanswered questions can be opened.</p></section></div>}
function ConfirmExit({cancel,exit}:{cancel:()=>void;exit:()=>void}){return <div className="modal-backdrop"><section className="confirm-modal"><div className="question-icon">💾</div><h2>Exit today’s worksheet?</h2><p>Your progress, answers, hints, skipped questions and current position will be saved. You can continue later.</p><div className="modal-actions"><button onClick={cancel}>Keep working</button><button className="primary" onClick={exit}>Save and exit</button></div></section></div>}

function Answer({q,value,setValue}:any){if(q.answer_type==='choice')return <div className="choices">{q.payload.choices.map((x:string)=><button type="button" className={value===x?'selected':''} onClick={()=>setValue(String(x))} key={x}>{x}</button>)}</div>;const capture=(e:any)=>setValue(String(e.currentTarget.value));return <div className="answer-row">{q.answer_type==='money'&&<span>$</span>}<input inputMode={q.answer_type==='text'?'text':'decimal'} value={value} onInput={capture} onChange={capture} onKeyDown={(e:any)=>{if(e.key==='Enter'){e.preventDefault();const button=e.currentTarget.closest('.question-card')?.querySelector('.question-actions .primary:not(:disabled)') as HTMLButtonElement|null;button?.click()}}} autoComplete="off" placeholder="Type your answer"/>{q.payload.unit&&<span>{q.payload.unit}</span>}</div>}
function FractionShape({parts,shaded}:any){return <div className="fraction-shape">{Array.from({length:parts},(_,i)=><i className={i<shaded?'shade':''} key={i}/>)}</div>}
function Result({data,back}:any){return <main className="result"><section><div className="result-score">{data.score}/{data.total}</div><h1>{data.message}</h1><p>{data.accuracy}% accuracy · +{data.xp_earned} XP</p><div className="result-grid"><Metric label="Strongest" value={data.strongest_topic}/><Metric label="Practise next" value={data.weakest_topic}/><Metric icon={<Lightbulb/>} label="Hints used" value={data.hints_used||0}/><Metric label="Level" value={data.level}/></div><button className="primary" onClick={back}>Back to dashboard</button></section></main>}

function statusText(status:string){return({secure:'Secure',developing:'Developing',needs_support:'Needs support',not_assessed:'Not assessed'} as any)[status]||status}
function Parent({user,logout}:{user:User;logout:()=>void}){
  const[d,setD]=useState<any>(null),[settings,setSettings]=useState<any>(null),[backups,setBackups]=useState<any[]>([]);
  const load=()=>{req('/dashboard/parent').then(setD);req('/settings').then(setSettings);req('/backups').then(setBackups)};
  useEffect(load,[]);if(!d||!settings)return <div className="splash"><Brand/></div>;
  async function save(){await req('/settings',{method:'PUT',body:JSON.stringify(settings)});alert('Settings saved')}
  async function download(path:string,name:string){const b=await req(path);const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=name;a.click()}
  return <><Header user={user} logout={logout}/><main className="page"><section className="parent-title"><div><p className="eyebrow">PARENT VIEW · VICTORIAN CURRICULUM LEVEL 4</p><h1>Sienna’s learning overview</h1><p>Accuracy shows what is being answered correctly. Hint usage shows where Sienna is asking for extra support, even when she ultimately gets the answer right.</p></div><div className="actions"><button onClick={()=>download('/reports/progress.csv','mathquest-progress.csv')}><Download size={17}/> CSV</button><button onClick={()=>download('/reports/progress.pdf','mathquest-progress.pdf')}><Download size={17}/> PDF</button></div></section>
  <section className="cards parent-metrics"><Metric label="Streak" value={`${d.streak} days`}/><Metric label="Accuracy" value={`${d.accuracy}%`}/><Metric label="Answered" value={d.questions_answered}/><Metric icon={<Lightbulb/>} label="Hints provided" value={d.hint_summary.total_hints}/><Metric label="Needs support" value={d.curriculum_summary.needs_support}/></section>
  <section className="panel hint-insights"><div className="panel-heading"><div><p className="eyebrow">LEARNING SUPPORT</p><h2><Lightbulb size={22}/> Hint usage by learning area</h2><p>A higher hint rate can identify a topic that needs explanation or more practice, even if overall accuracy remains high.</p></div><div className="hint-total"><span>Questions using hints</span><strong>{d.hint_summary.questions_with_hints}</strong></div></div><div className="hint-topic-grid">{d.hint_summary.by_topic.map((x:any)=><div className="hint-topic" key={x.topic}><div><b>{x.topic}</b><span>{x.hints} hints</span></div><strong>{x.hint_rate}%</strong><div className="hint-rate"><i style={{width:`${Math.min(100,x.hint_rate)}%`}}/></div><small>{x.questions_with_hints} of {x.questions_seen} questions used a hint</small></div>)}</div></section>
  {d.hint_summary.recent.length>0&&<section className="panel"><h2><Sparkles size={20}/> Recent hint activity</h2><div className="recent-hints">{d.hint_summary.recent.map((x:any,i:number)=><div key={`${x.date}-${i}`}><span className="hint-topic-name">{x.topic}</span><div><b>{x.prompt}</b><p>Hint {x.hint_number}: {x.hint}</p></div></div>)}</div></section>}
  {d.concerns.length>0&&<section className="panel concern-panel"><h2>⚑ Areas to review</h2><p>These outcomes currently have less than 70% first-attempt accuracy, or limited successful evidence.</p><div className="concern-grid">{d.concerns.map((x:any)=><div key={x.code}><b>{x.code}</b><span>{x.title}</span><strong>{x.accuracy}%</strong><small>{x.attempts} recent attempts</small></div>)}</div></section>}
  <section className="panel"><h2>Level 4 curriculum tracker</h2><div className="curriculum-table"><div className="curriculum-head"><b>Outcome</b><b>Evidence</b><b>Accuracy</b><b>Status</b></div>{d.curriculum.map((x:any)=><div className="curriculum-row" key={x.code}><span><b>{x.code}</b><small>{x.strand} · {x.title}</small></span><span>{x.attempts} attempts</span><span>{x.attempts?`${x.accuracy}%`:'—'}</span><span className={'status-pill '+x.status}>{statusText(x.status)}</span></div>)}</div></section>
  <section className="grid2"><div className="panel"><h2>Strand performance</h2>{d.skills.map((s:any)=><div className="skill" key={s.topic}><div><b>{s.topic}</b><span>Adaptive level {s.level}</span></div><div className="bar"><i style={{width:`${s.accuracy}%`}}/></div><small>{s.accuracy}% · {s.avg_seconds}s average</small></div>)}</div><div className="panel"><h2><Settings size={20}/> Worksheet settings</h2><label>Questions per day<input type="number" min="5" max="50" value={settings.question_count} onChange={e=>setSettings({...settings,question_count:+e.target.value})}/></label><label className="toggle"><input type="checkbox" checked={settings.adaptive_mode} onChange={e=>setSettings({...settings,adaptive_mode:e.target.checked})}/> Adaptive learning</label><div className="topic-checks">{['number','algebra','measurement','space','statistics','probability'].map(t=><label key={t}><input type="checkbox" checked={settings.enabled_topics.includes(t)} onChange={e=>setSettings({...settings,enabled_topics:e.target.checked?[...settings.enabled_topics,t]:settings.enabled_topics.filter((x:string)=>x!==t)})}/>{t}</label>)}</div><button className="primary" onClick={save}>Save settings</button></div></section>
  <section className="panel"><h2>Recent incorrect answers</h2>{d.recent_incorrect.length?<div className="incorrect-list">{d.recent_incorrect.map((x:any,i:number)=><details key={i}><summary><b>{x.code||'Practice'}</b> {x.prompt}</summary><p>Student answer: <strong>{x.student_answer}</strong></p><p>Correct answer: <strong>{x.correct_answer}</strong></p><p>{x.working}</p></details>)}</div>:<p>No incorrect answers recorded yet.</p>}</section>
  <section className="panel"><h2><Database size={20}/> Backups</h2><button onClick={async()=>{await req('/backups',{method:'POST'});load()}}>Create backup now</button><div className="backup-list">{backups.map(b=><span key={b.filename}>{b.filename} · {(b.size/1024).toFixed(0)} KB</span>)}</div></section></main></>}

createRoot(document.getElementById('root')!).render(<App/>);
