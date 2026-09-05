import React, {useEffect, useMemo, useState} from 'react';
import {Brain, RefreshCw, Sparkles} from 'lucide-react';
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
  };
};
type ProgressPayload = {
  recommendation?:any;
  recommendation_explanation?:{label:string;text:string};
  learning_now?:LearningRow[];
  summary?:{getting_stronger:number;building_confidence:number;review_due:number};
};

const GROUPS: {key:LearningStateKey; title:string; description:string}[] = [
  {key:'ready_for_challenge', title:'Ready for a challenge', description:'You have been solving these confidently, so MathQuest can stretch you a little further.'},
  {key:'getting_stronger', title:'Getting stronger', description:'These skills are looking strong in your recent work.'},
  {key:'building_confidence', title:'Building confidence', description:'A little support still helps here, so these will stay in your practice.'},
  {key:'practising', title:'Practising now', description:'These are part of what you are learning at the moment.'},
  {key:'review_due', title:'Ready to review', description:'You have done these before. A quick revisit helps them stay fresh.'},
  {key:'not_enough_evidence', title:'Still learning about this', description:'Keep practising so MathQuest can understand how this skill is going.'},
];

function friendlySkill(value:string|null){return value ? value.replaceAll('_',' ') : ''}

export function StudentProgress(){
  const[data,setData]=useState<ProgressPayload|null>(null);
  const[error,setError]=useState('');
  const[showAllAreas,setShowAllAreas]=useState(false);
  const load=()=>{setError('');apiRequest<ProgressPayload>('/learning/student-progress-v0410').then(value=>setData(value && !Array.isArray(value) ? value : {})).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  const learningRows=Array.isArray(data?.learning_now)?data.learning_now:[];
  const summary=data?.summary??{getting_stronger:0,building_confidence:0,review_due:0};
  const visibleRows=useMemo(()=>showAllAreas?learningRows:learningRows.filter(row=>row.state.key!=='not_enough_evidence').slice(0,8),[learningRows,showAllAreas]);
  const grouped=useMemo(()=>GROUPS.map(group=>({...group,rows:visibleRows.filter(row=>row.state.key===group.key)})).filter(group=>group.rows.length),[visibleRows]);

  return <section id="mq-student-progress" className="panel student-progress" aria-labelledby="student-progress-title">
    <div className="student-progress-head"><div><p className="eyebrow">YOUR LEARNING NOW</p><h2 id="student-progress-title"><Brain size={22}/> What MathQuest is noticing</h2><p>See what you are practising, what is getting stronger and what is ready to revisit.</p></div></div>
    {error&&<div className="mq-error-notice" role="alert"><div><b>Progress could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div>} {!data&&!error&&<p>Loading your learning progress…</p>}
    {data&&<>
      <div className="student-progress-summary" aria-label="Learning summary">
        {summary.getting_stronger>0&&<article><Sparkles size={18}/><span><b>{summary.getting_stronger}</b> ready for a challenge or getting stronger</span></article>}
        {summary.building_confidence>0&&<article><Brain size={18}/><span><b>{summary.building_confidence}</b> building confidence</span></article>}
        {summary.review_due>0&&<article><RefreshCw size={18}/><span><b>{summary.review_due}</b> ready to review</span></article>}
      </div>
      {data.recommendation&&data.recommendation_explanation&&<article className="student-progress-why"><p className="eyebrow">{data.recommendation_explanation.label}</p><h3>{data.recommendation.title}</h3><p>{data.recommendation_explanation.text}</p></article>}
      <div className="student-progress-groups">{grouped.map(group=><section key={group.key} className={`student-progress-group state-${group.key}`}><div className="student-progress-group-heading"><h3>{group.title}</h3><p>{group.description}</p></div><div className="student-progress-list">{group.rows.map(row=><article key={row.code} className="student-progress-row"><div><small>{row.strand}</small><h4>{row.title}</h4>{row.state.target_skill&&<span className="student-progress-skill">{friendlySkill(row.state.target_skill)}</span>}</div></article>)}</div></section>)}</div>
      {learningRows.length>visibleRows.length&&<button type="button" className="student-progress-detail-toggle" aria-expanded={showAllAreas} onClick={()=>setShowAllAreas(!showAllAreas)}>{showAllAreas?'Show priority learning only':'View all learning areas'}</button>}
    </>}
  </section>;
}
