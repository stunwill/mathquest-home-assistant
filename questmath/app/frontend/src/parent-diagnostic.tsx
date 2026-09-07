import React, {useEffect, useState} from 'react';
import {Brain, RefreshCw} from 'lucide-react';
import {apiRequest} from './api';
import './diagnostic-placement.css';

function friendly(value?:string|null){return value ? value.replaceAll('_',' ') : ''}

export function ParentDiagnosticInsight(){
  const[data,setData]=useState<any>(null);
  const[error,setError]=useState('');
  const load=()=>{setError('');apiRequest('/learning/parent-diagnostic-v0430').then(setData).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  if(error)return <section className="panel"><div className="mq-error-notice" role="alert"><div><b>Diagnostic insight could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div></section>;
  if(!data||data.status!=='complete')return null;
  return <section className="panel diagnostic-placement" aria-labelledby="parent-diagnostic-title">
    <div className="diagnostic-placement-head"><p className="eyebrow">DIAGNOSTIC PLACEMENT</p><h2 id="parent-diagnostic-title"><Brain size={22}/> Level 5/6 evidence summary</h2><p>{data.limitations}</p></div>
    <div className="diagnostic-placement-grid">{(data.levels||[]).map((level:any)=><article key={level.level}><div><small>LEVEL {level.level}</small><p><b>{level.attempted} attempted</b><span>{level.independent_correct} independent · {level.eventual_correct} eventual · {level.support_used} with support</span></p></div></article>)}</div>
    <div className="diagnostic-placement-grid">
      <article><div><small>STRONGER DIAGNOSTIC EVIDENCE</small>{(data.demonstrated||[]).length?(data.demonstrated||[]).map((item:any)=><p key={item.code}><b>{item.code} · {item.title}</b><span>{friendly(item.target_skill)} · {item.prior_evidence_questions} prior evidence question(s)</span></p>):<p>No sampled area has enough independent diagnostic evidence to describe as stronger yet.</p>}</div></article>
      <article><div><small>SUPPORTED DURING DIAGNOSTIC</small>{(data.supported||[]).length?(data.supported||[]).map((item:any)=><p key={item.code}><b>{item.code} · {item.title}</b><span>{item.eventual_correct}/{item.diagnostic_questions} eventual correct · support used {item.support_used} time(s) · {item.prior_evidence_questions} prior evidence question(s)</span></p>):<p>No sampled area required recorded support.</p>}</div></article>
      <article><div><small>MORE EVIDENCE NEEDED</small>{(data.needs_more_evidence||[]).length?(data.needs_more_evidence||[]).map((item:any)=><p key={item.code}><b>{item.code} · {item.title}</b><span>{item.independent_correct}/{item.diagnostic_questions} independent correct · {item.prior_evidence_questions} prior evidence question(s)</span></p>):<p>No sampled area is currently flagged here.</p>}</div></article>
    </div>
    {data.recommended_focus&&<article className="diagnostic-next-step"><p className="eyebrow">RECOMMENDED NEXT LEARNING FOCUS</p><h3>{data.recommended_focus.title}</h3><p>{data.recommended_focus.explanation}</p>{data.recommended_focus.target_skill&&<small>Target skill: {friendly(data.recommended_focus.target_skill)}</small>}</article>}
  </section>;
}
