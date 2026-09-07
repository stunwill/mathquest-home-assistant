import React, {useEffect, useState} from 'react';
import {Brain, CheckCircle2, RefreshCw, Sparkles} from 'lucide-react';
import {apiRequest} from './api';
import './diagnostic-placement.css';

type PlacementItem = {strand?:string;title?:string;target_skill?:string|null};
type PlacementPayload = {
  status:string;
  completed_at?:string|null;
  student_message?:string;
  demonstrated?:PlacementItem[];
  supported?:PlacementItem[];
  needs_more_evidence?:PlacementItem[];
  recommended_focus?:{title?:string|null;target_skill?:string|null;explanation?:string|null};
};

function friendly(value?:string|null){return value ? value.replaceAll('_',' ') : ''}

function PlacementContent({data}:{data:PlacementPayload}){
  const demonstrated=data.demonstrated||[];
  const supported=data.supported||[];
  const needsMore=data.needs_more_evidence||[];
  return <>
    <div className="diagnostic-placement-head"><p className="eyebrow">YOUR STARTING POINT</p><h2 id="diagnostic-placement-title"><Brain size={22}/> What MathQuest learned</h2><p>{data.student_message}</p></div>
    <div className="diagnostic-placement-grid">
      {demonstrated.length>0&&<article><Sparkles size={18}/><div><small>YOU SHOWED CONFIDENCE WITH</small>{demonstrated.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
      {supported.length>0&&<article><Brain size={18}/><div><small>WE’LL KEEP PRACTISING</small>{supported.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
      {needsMore.length>0&&<article><RefreshCw size={18}/><div><small>WE NEED A LITTLE MORE EVIDENCE</small>{needsMore.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
    </div>
    {data.recommended_focus?.title&&<article className="diagnostic-next-step"><p className="eyebrow">NEXT, MATHQUEST RECOMMENDS</p><h3>{data.recommended_focus.title}</h3>{data.recommended_focus.explanation&&<p>{data.recommended_focus.explanation}</p>}</article>}
  </>;
}

function usePlacement(){
  const[data,setData]=useState<PlacementPayload|null>(null);
  const[error,setError]=useState('');
  const load=()=>{setError('');apiRequest<PlacementPayload>('/learning/diagnostic-placement-v0430').then(setData).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  return {data,error,load};
}

export function DiagnosticPlacementSummary(){
  const{data,error,load}=usePlacement();
  if(error)return <section className="panel diagnostic-placement"><div className="mq-error-notice" role="alert"><div><b>Starting point could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div></section>;
  if(!data||data.status!=='complete')return null;
  return <section className="panel diagnostic-placement" aria-labelledby="diagnostic-placement-title"><PlacementContent data={data}/></section>;
}

export function DiagnosticCompletion({back}:{back:()=>void}){
  const{data,error,load}=usePlacement();
  return <main className="result diagnostic-completion"><section className="diagnostic-completion-card">
    <CheckCircle2 size={42}/><p className="eyebrow">DIAGNOSTIC COMPLETE</p><h1>You completed all six questions</h1><p>This short check gives MathQuest a starting signal. It is not a pass, fail or overall grade.</p>
    {error&&<div className="mq-error-notice" role="alert"><div><b>Your starting point could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div>}
    {!data&&!error&&<p>Working out your best next step…</p>}
    {data?.status==='complete'&&<section className="diagnostic-placement" aria-labelledby="diagnostic-placement-title"><PlacementContent data={data}/></section>}
    <button type="button" className="primary" onClick={back}>Continue to MathQuest</button>
  </section></main>;
}
