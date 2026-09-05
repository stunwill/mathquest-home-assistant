import React, {useEffect, useState} from 'react';
import {Clock3, RefreshCw, Route} from 'lucide-react';
import {apiRequest} from './api';

type Recommendation = {
  mode: 'diagnostic' | 'guided' | 'review' | 'practice';
  minutes: 5 | 10 | 15;
  topic: string;
  outcome_code: string | null;
  title: string;
  reason: string;
  prerequisite_for: string | null;
};

function StudentProgress({onStart}:{onStart:()=>void}) {
  const [data,setData]=useState<any>(null);
  const [error,setError]=useState('');
  const [showDetail,setShowDetail]=useState(false);
  useEffect(()=>{apiRequest('/learning/student-progress-v0410').then(setData).catch((e:Error)=>setError(e.message))},[]);
  if(error)return <section id="mq-student-progress" className="panel student-progress" aria-label="Student progress"><p role="alert">{error}</p></section>;
  if(!data)return <section id="mq-student-progress" className="panel student-progress" aria-label="Student progress"><p>Loading your learning progress…</p></section>;
  const groups=[
    ['ready_for_challenge','Ready for a challenge'],['getting_stronger','Getting stronger'],['building_confidence','Building confidence'],['practising','Practising now'],['review_due','Coming back for review'],['not_enough_evidence','Still learning about this']
  ];
  return <section id="mq-student-progress" className="panel student-progress" aria-labelledby="student-progress-title">
    <div className="student-progress-head"><div><p className="eyebrow">YOUR LEARNING NOW</p><h2 id="student-progress-title">What MathQuest is noticing</h2><p>Progress explains what you are practising, what is getting stronger and what is coming back for review.</p></div><button type="button" className="primary" onClick={onStart}>Start best next step</button></div>
    <div className="student-progress-summary" aria-label="Learning summary"><span><b>{data.summary.getting_stronger}</b> getting stronger</span><span><b>{data.summary.building_confidence}</b> building confidence</span><span><b>{data.summary.review_due}</b> review due</span></div>
    <article className="student-progress-why"><p className="eyebrow">{data.recommendation_explanation.label}</p><h3>{data.recommendation.title}</h3><p>{data.recommendation_explanation.text}</p></article>
    <div className="student-progress-groups">{groups.map(([key,title])=>{const rows=data.learning_now.filter((row:any)=>row.state.key===key);if(!rows.length)return null;return <section key={key} className={`student-progress-group state-${key}`}><h3>{title}</h3>{rows.map((row:any)=><article key={row.code} className="student-progress-row"><div><small>{row.strand}</small><h4>{row.title}</h4>{row.state.target_skill&&<span>{String(row.state.target_skill).replaceAll('_',' ')}</span>}</div><div><strong>{row.state.label}</strong><p>{row.state.message}</p></div></article>)}</section>})}</div>
    <button type="button" className="student-progress-detail-toggle" aria-expanded={showDetail} onClick={()=>setShowDetail(!showDetail)}>{showDetail?'Hide learning detail':'Show learning detail'}</button>
    {showDetail&&<div className="student-progress-detail"><p>MathQuest uses repeated answers, independent versus supported success, retention and current adaptive evidence. It does not use a separate student score.</p>{data.learning_now.map((row:any)=><details key={row.code}><summary>{row.title} · {row.state.label}</summary><p>{row.state.evidence.questions} recent skill questions · {row.state.evidence.independent_accuracy}% independent success · {row.state.evidence.eventual_accuracy}% eventually correct · {row.state.evidence.support_dependency}% support used</p></details>)}</div>}
  </section>;
}

export function AdaptiveRecommendation({data, busy, onStart}: {data: any; busy: boolean; onStart: () => void}) {
  const recommendation: Recommendation | undefined = data?.recommendation;
  if (!recommendation) return null;
  return <>
    <section className="panel adaptive-recommendation" aria-label="Recommended next session">
      <div className="adaptive-recommendation-copy">
        <p className="eyebrow">YOUR BEST NEXT STEP</p>
        <h2>{recommendation.title}</h2>
        <p>{recommendation.reason}</p>
        <div className="adaptive-signals">
          <span><Clock3 size={16}/>{recommendation.minutes} minutes</span>
          <span><Route size={16}/>{recommendation.mode.replace('_', ' ')}</span>
          {recommendation.outcome_code && <span>{recommendation.outcome_code}</span>}
          {!!data.summary?.review_due && <span><RefreshCw size={16}/>{data.summary.review_due} review due</span>}
        </div>
      </div>
      <button type="button" className="primary" disabled={busy} onClick={onStart}>
        {busy ? 'Building your session…' : `Start ${recommendation.minutes}-minute session`}
      </button>
    </section>
    <StudentProgress onStart={onStart}/>
  </>;
}
