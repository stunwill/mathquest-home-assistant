import React, {useMemo, useState} from 'react';
import {AlertTriangle, Brain, ChevronDown, CircleHelp, Gauge, RefreshCw, Route, ShieldCheck, Sparkles, Target, TrendingUp} from 'lucide-react';

const pct = (value:number|null|undefined) => value == null ? 'Not enough evidence' : `${value}%`;
const pretty = (value:string) => value.replaceAll('_',' ').replace(/\b\w/g, c => c.toUpperCase());

function StatusPill({status}:{status:string}){
  return <span className={`learning-status ${status}`}>{pretty(status)}</span>;
}

function Why({children}:{children:React.ReactNode}){
  const[open,setOpen]=useState(false);
  return <div className="learning-why"><button type="button" onClick={()=>setOpen(!open)} aria-expanded={open}><CircleHelp size={16}/> Why?</button>{open&&<p>{children}</p>}</div>;
}

export function ParentLearningIntelligence({data,onPeriod}:{data:any;onPeriod:(days:number)=>void}){
  const[area,setArea]=useState('all');
  if(!data)return null;
  const skills=useMemo(()=>area==='all'?data.skills:(data.skills||[]).filter((item:any)=>String(item.skill||'').toLowerCase().includes(area)),[data.skills,area]);
  const needs=(data.skills||[]).filter((item:any)=>item.status==='needs_support');
  const secure=(data.skills||[]).filter((item:any)=>item.status==='secure');
  return <section className="parent-intelligence" aria-label="Parent learning intelligence">
    <section className="panel learning-summary-card">
      <div className="panel-heading"><div><p className="eyebrow">PARENT LEARNING INTELLIGENCE</p><h2><Brain size={23}/> What the learning evidence says</h2></div><div className="period-switch" role="group" aria-label="Reporting period">{[7,30,90].map(days=><button type="button" key={days} className={data.trend?.days===days?'selected':''} onClick={()=>onPeriod(days)}>{days} days</button>)}</div></div>
      <div className="learning-summary-lines">{(data.summary||[]).map((line:string)=><p key={line}>{line}</p>)}</div>
      <div className="learning-headlines">
        <article><ShieldCheck/><small>Current strengths</small><strong>{secure[0]?.label||'Still building evidence'}</strong><span>{secure.length?`${secure.length} secure skill${secure.length===1?'':'s'}`:'No secure classification yet'}</span></article>
        <article><AlertTriangle/><small>Needs attention</small><strong>{needs[0]?.label||'No high-confidence concern'}</strong><span>{needs.length?`${needs.length} skill${needs.length===1?'':'s'} need support`:'No repeated support signal yet'}</span></article>
        <article><Gauge/><small>Difficulty</small><strong>{pretty(data.difficulty?.state||'not_enough_evidence')}</strong><span>{data.difficulty?.attempts||0} assessed questions</span></article>
      </div>
    </section>

    <section className="panel practice-plan"><div className="panel-heading"><div><p className="eyebrow">WHAT TO PRACTISE NEXT</p><h2><Target size={22}/> Prioritised learning plan</h2></div></div>{data.recommendations?.length?<div className="recommendation-list">{data.recommendations.map((item:any)=><article key={`${item.priority}-${item.skill}`} className={`recommendation ${item.priority}`}><div><span className="priority">{pretty(item.priority)}</span><h3>{item.title}</h3><p>{item.reason}</p></div><Route/></article>)}</div>:<p>MathQuest needs more learner evidence before creating a reliable practice priority.</p>}</section>

    <section className="panel mastery-overview"><div className="panel-heading"><div><p className="eyebrow">SKILL MASTERY</p><h2><TrendingUp size={22}/> Independent vs supported success</h2></div><label>Filter<select value={area} onChange={e=>setArea(e.target.value)}><option value="all">All skills</option><option value="number">Number</option><option value="algebra">Algebra</option><option value="fraction">Fractions</option><option value="measurement">Measurement</option></select></label></div><div className="mastery-grid">{skills.map((item:any)=><article key={item.skill}><div className="mastery-title"><div><h3>{item.label}</h3><small>{item.confidence} evidence · {item.attempts} attempts</small></div><StatusPill status={item.status}/></div><div className="mastery-metrics"><span><small>First attempt</small><b>{pct(item.first_attempt_accuracy)}</b></span><span><small>Eventual</small><b>{pct(item.eventual_accuracy)}</b></span><span><small>Support used</small><b>{pct(item.support_dependency)}</b></span></div><Why>{item.status==='secure'?'Repeated recent evidence is mostly independent at a strong success rate.':item.status==='needs_support'?`Support is used on ${item.support_dependency}% of recent questions, so eventual accuracy is not being treated as independent mastery.`:item.status==='review_due'?'This skill was previously strong but has not been checked recently.':'MathQuest is keeping this judgement conservative until more independent evidence is available.'}</Why></article>)}</div></section>

    <div className="parent-intelligence-columns">
      <section className="panel"><p className="eyebrow">MISCONCEPTIONS</p><h2><AlertTriangle size={21}/> Repeated patterns</h2>{data.misconceptions?.length?data.misconceptions.map((item:any)=><article className="misconception" key={`${item.skill}-${item.type}`}><h3>{item.label}</h3><p>{item.skill_label}</p><b>{item.count} observations</b><small>{item.response}</small></article>):<p>No repeated misconception has enough evidence to report.</p>}</section>
      <section className="panel"><p className="eyebrow">RETENTION</p><h2><RefreshCw size={21}/> Spaced review</h2>{data.retention?.length?data.retention.slice(0,6).map((item:any)=><article className="retention" key={item.skill}><div><h3>{item.label}</h3><small>{item.review_due?'Due for a quick review':'Retained successfully'}</small></div><StatusPill status={item.review_due?'review_due':'secure'}/></article>):<p>Not enough retained-skill evidence yet.</p>}</section>
    </div>

    <section className="panel progress-comparison"><p className="eyebrow">PROGRESS</p><h2><Sparkles size={21}/> Recent learning trend</h2><div className="trend-cards"><article><small>Current {data.trend?.days}-day period</small><strong>{pct(data.trend?.current?.first_attempt_accuracy)}</strong><span>first-attempt accuracy · {data.trend?.current?.questions||0} questions</span></article><article><small>Previous comparable period</small><strong>{pct(data.trend?.previous?.first_attempt_accuracy)}</strong><span>first-attempt accuracy · {data.trend?.previous?.questions||0} questions</span></article><article><small>Current eventual accuracy</small><strong>{pct(data.trend?.current?.eventual_accuracy)}</strong><span>Includes successful retries and support</span></article></div></section>
  </section>;
}
