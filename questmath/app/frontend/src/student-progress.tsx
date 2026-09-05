import React, {useEffect, useMemo, useState} from 'react';
import {ArrowUpRight, Brain, RefreshCw, Sparkles} from 'lucide-react';
import {apiRequest} from './api';
import './student-progress.css';

type LearningStateKey = 'not_enough_evidence'|'practising'|'building_confidence'|'getting_stronger'|'ready_for_challenge'|'review_due';
type LearningRow = {
  code:string;
  strand:string;
  title:string;
  questions:number;
  last_practised:string|null;
  review_due:boolean;
  state:{
    key:LearningStateKey;
    label:string;
    message:string;
    target_skill:string|null;
    evidence:{questions:number;independent_accuracy:number;eventual_accuracy:number;support_dependency:number};
  };
};
type ProgressPayload = {
  recommendation?:any;
  recommendation_explanation?:{label:string;text:string};
  learning_now?:LearningRow[];
  summary?:{getting_stronger:number;building_confidence:number;review_due:number};
};

const GROUPS: {key:LearningStateKey; title:string; description:string}[] = [
  {key:'ready_for_challenge', title:'Ready for a challenge', description:'You have repeated independent success here.'},
  {key:'getting_stronger', title:'Getting stronger', description:'Your recent answers show strong independent work.'},
  {key:'building_confidence', title:'Building confidence', description:'You can solve these with support, so MathQuest will keep consolidating them.'},
  {key:'practising', title:'Practising now', description:'These skills are still part of your current learning.'},
  {key:'review_due', title:'Coming back for review', description:'These are returning because spaced practice helps learning stick.'},
  {key:'not_enough_evidence', title:'Still learning about this', description:'There is not enough recent evidence for MathQuest to make a stronger claim yet.'},
];

function friendlySkill(value:string|null){return value ? value.replaceAll('_',' ') : ''}

export function StudentProgress({onStart}:{onStart?:()=>void}){
  const[data,setData]=useState<ProgressPayload|null>(null);
  const[error,setError]=useState('');
  const[showDetail,setShowDetail]=useState(false);
  const[showAllAreas,setShowAllAreas]=useState(false);
  const load=()=>{setError('');apiRequest<ProgressPayload>('/learning/student-progress-v0410').then(value=>setData(value && !Array.isArray(value) ? value : {})).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  const learningRows=Array.isArray(data?.learning_now)?data.learning_now:[];
  const summary=data?.summary??{getting_stronger:0,building_confidence:0,review_due:0};
  const visibleRows=useMemo(()=>{
    if(showAllAreas)return learningRows;
    const meaningful=learningRows.filter(row=>row.state.key!=='not_enough_evidence');
    return meaningful.length ? meaningful.slice(0,6) : learningRows.slice(0,3);
  },[learningRows,showAllAreas]);
  const grouped=useMemo(()=>GROUPS.map(group=>({...group,rows:visibleRows.filter(row=>row.state.key===group.key)})).filter(group=>group.rows.length),[visibleRows]);

  return <section id="mq-student-progress" className="panel student-progress" aria-labelledby="student-progress-title">
    <div className="student-progress-head"><div><p className="eyebrow">YOUR LEARNING NOW</p><h2 id="student-progress-title"><Brain size={22}/> What MathQuest is noticing</h2><p>Progress explains what you are practising, what has strong recent evidence and what is coming back for review.</p></div>{data?.recommendation&&onStart&&<button type="button" className="primary" onClick={onStart}><ArrowUpRight size={18}/>Start best next step</button>}</div>
    {error&&<div className="mq-error-notice" role="alert"><div><b>Progress could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div>} {!data&&!error&&<p>Loading your learning progress…</p>}
    {data&&<>
      <div className="student-progress-summary" aria-label="Learning summary"><article><Sparkles size={18}/><span><b>{summary.getting_stronger}</b> strong or challenge-ready</span></article><article><Brain size={18}/><span><b>{summary.building_confidence}</b> building confidence</span></article><article><RefreshCw size={18}/><span><b>{summary.review_due}</b> review due</span></article></div>
      {data.recommendation&&data.recommendation_explanation&&<article className="student-progress-why"><p className="eyebrow">{data.recommendation_explanation.label}</p><h3>{data.recommendation.title}</h3><p>{data.recommendation_explanation.text}</p></article>}
      <div className="student-progress-groups">{grouped.map(group=><section key={group.key} className={`student-progress-group state-${group.key}`}><div><h3>{group.title}</h3><p>{group.description}</p></div><div className="student-progress-list">{group.rows.map(row=><article key={row.code} className="student-progress-row"><div><small>{row.strand}</small><h4>{row.title}</h4>{row.state.target_skill&&<span className="student-progress-skill">{friendlySkill(row.state.target_skill)}</span>}</div><div><strong>{row.state.label}</strong><p>{row.state.message}</p></div></article>)}</div></section>)}</div>
      {learningRows.length>visibleRows.length&&<button type="button" className="student-progress-detail-toggle" aria-expanded={showAllAreas} onClick={()=>setShowAllAreas(!showAllAreas)}>{showAllAreas?'Show priority learning only':'View all learning areas'}</button>}
      <button type="button" className="student-progress-detail-toggle" aria-expanded={showDetail} onClick={()=>setShowDetail(!showDetail)}>{showDetail?'Hide learning detail':'Show learning detail'}</button>
      {showDetail&&<div className="student-progress-detail"><p>MathQuest uses repeated answers, independent versus supported success, retention and current adaptive evidence to decide these labels. It does not use a separate student score.</p>{visibleRows.map(row=><details key={row.code}><summary>{row.title} · {row.state.label}</summary><dl><div><dt>Recent skill questions</dt><dd>{row.state.evidence.questions}</dd></div><div><dt>Independent success</dt><dd>{row.state.evidence.independent_accuracy}%</dd></div><div><dt>Eventually correct</dt><dd>{row.state.evidence.eventual_accuracy}%</dd></div><div><dt>Support used</dt><dd>{row.state.evidence.support_dependency}%</dd></div></dl></details>)}</div>}
    </>}
  </section>;
}
