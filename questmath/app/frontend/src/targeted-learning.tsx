import React, {useEffect, useState} from 'react';
import {Brain, RefreshCw, Sparkles} from 'lucide-react';
import {apiRequest} from './api';
import './targeted-learning.css';

type Plan = {kind:string;minutes:number;purpose:string;title:string;reason:string;target_skill?:string|null};
type Summary = {available:boolean;purpose?:string;target_skill?:string|null;message?:string;evidence_added?:number;independent_checks?:number};

function friendly(value?:string|null){return value ? value.replaceAll('_',' ') : ''}

export function TargetedLearningPreview(){
  const[data,setData]=useState<Plan|null>(null);
  const[error,setError]=useState('');
  const load=()=>{setError('');apiRequest<Plan>('/learning/session-plan-v0440').then(setData).catch((e:Error)=>setError(e.message))};
  useEffect(load,[]);
  if(error)return <section className="panel targeted-learning-preview" aria-label="Today's focus"><p className="eyebrow">TODAY’S FOCUS</p><p>MathQuest could not load your focus.</p><button type="button" onClick={load}><RefreshCw size={16}/> Try again</button></section>;
  if(!data||data.kind==='diagnostic')return null;
  return <section className="panel targeted-learning-preview" aria-label="Today's focus">
    <div><p className="eyebrow">TODAY’S FOCUS</p><h2><Brain size={20}/>{data.title}</h2><p>{data.reason}</p>{data.target_skill&&<small>Practising: {friendly(data.target_skill)}</small>}</div>
    <span>{data.minutes} min</span>
  </section>;
}

export function TargetedCompletion({worksheetId,back}:{worksheetId:number;back:()=>void}){
  const[data,setData]=useState<Summary|null>(null);
  useEffect(()=>{apiRequest<Summary>(`/worksheets/${worksheetId}/targeted-summary-v0450`).then(setData).catch(()=>setData({available:false}))},[worksheetId]);
  return <main className="result-page targeted-result"><section className="result-card">
    <p className="eyebrow">SESSION COMPLETE</p>
    <h1><Sparkles size={28}/> Nice work</h1>
    <h2>What this session added</h2>
    <p>{data?.available ? data.message : 'Your practice has been added to MathQuest’s learning evidence.'}</p>
    {data?.target_skill&&<p><strong>Focus:</strong> {friendly(data.target_skill)}</p>}\n    {data?.available&&<p className="targeted-evidence-note">{data.evidence_added ? `${data.evidence_added} new evidence question${data.evidence_added===1?'':'s'} added.` : 'This session added useful evidence.'} {data.independent_checks ? `${data.independent_checks} independent check${data.independent_checks===1?'':'s'} completed.` : 'MathQuest will keep gathering evidence.'}</p>}
    <button className="primary" type="button" onClick={back}>Continue to MathQuest</button>
  </section></main>;
}
