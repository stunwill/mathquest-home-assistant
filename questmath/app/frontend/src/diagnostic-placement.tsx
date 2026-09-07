import React, {useEffect, useState} from 'react';
import {Brain, RefreshCw, Sparkles} from 'lucide-react';
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

export function DiagnosticPlacementSummary(){
  const[data,setData]=useState<PlacementPayload|null>(null);
  const[error,setError]=useState('');
  const load=()=>{setError('');apiRequest<PlacementPayload>('/learning/diagnostic-placement-v0430').then(setData).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  if(error)return <section className="panel diagnostic-placement"><div className="mq-error-notice" role="alert"><div><b>Starting point could not load</b><p>{error}</p></div><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></div></section>;
  if(!data||data.status!=='complete')return null;
  const demonstrated=data.demonstrated||[];
  const supported=data.supported||[];
  const needsMore=data.needs_more_evidence||[];
  return <section className="panel diagnostic-placement" aria-labelledby="diagnostic-placement-title">
    <div className="diagnostic-placement-head"><p className="eyebrow">YOUR STARTING POINT</p><h2 id="diagnostic-placement-title"><Brain size={22}/> What MathQuest learned</h2><p>{data.student_message}</p></div>
    <div className="diagnostic-placement-grid">
      {demonstrated.length>0&&<article><Sparkles size={18}/><div><small>YOU SHOWED CONFIDENCE WITH</small>{demonstrated.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
      {supported.length>0&&<article><Brain size={18}/><div><small>WE’LL KEEP PRACTISING</small>{supported.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
      {needsMore.length>0&&<article><RefreshCw size={18}/><div><small>WE NEED A LITTLE MORE EVIDENCE</small>{needsMore.map(item=><p key={`${item.strand}-${item.title}`}><b>{item.title}</b>{item.target_skill&&<span>{friendly(item.target_skill)}</span>}</p>)}</div></article>}
    </div>
    {data.recommended_focus?.title&&<article className="diagnostic-next-step"><p className="eyebrow">NEXT, MATHQUEST RECOMMENDS</p><h3>{data.recommended_focus.title}</h3>{data.recommended_focus.explanation&&<p>{data.recommended_focus.explanation}</p>}</article>}
  </section>;
}
