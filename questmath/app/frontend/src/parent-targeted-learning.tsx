import React, {useEffect, useState} from 'react';
import {apiRequest} from './api';

type Plan = {
  kind:string;minutes:number;purpose:string;student_title:string;student_reason:string;
  primary_target?:{outcome_code?:string|null;title?:string;skill?:string|null;prerequisite_for?:string|null;evidence_questions?:number;status?:string|null;review_due?:boolean};
  stages?:string[];
};

const stageLabels:Record<string,string>={
  reconnect:'reconnect',
  supported:'supported practice',
  core:'core practice',
  transfer:'transfer',
  check:'independent check',
};

export function ParentTargetedLearningInsight(){
  const[data,setData]=useState<Plan|null>(null);
  useEffect(()=>{apiRequest<Plan>('/learning/session-plan-v0440').then(setData).catch(()=>setData(null))},[]);
  if(!data||data.kind==='diagnostic'||!data.primary_target)return null;
  const target=data.primary_target;
  const counts=(data.stages||[]).reduce((acc:Record<string,number>,stage)=>{acc[stage]=(acc[stage]||0)+1;return acc},{});
  return <section className="panel" aria-label="Targeted learning plan">
    <p className="eyebrow">NEXT TARGETED LEARNING PLAN</p>
    <h2>{target.title}</h2>
    <p>{data.student_reason}</p>
    <div className="curriculum-table">
      <div className="curriculum-row"><span><b>Purpose</b><small>{data.purpose}</small></span><span>{data.minutes} minutes</span><span>{target.evidence_questions ?? 0} evidence questions</span><span>{target.status?.replaceAll('_',' ')||'Not assessed'}</span></div>
      <div className="curriculum-row"><span><b>Outcome</b><small>{target.outcome_code||'—'}</small></span><span>{target.skill?.replaceAll('_',' ')||'—'}</span><span>{target.review_due?'Review due':'Current learning'}</span><span>{target.prerequisite_for?`Prerequisite for ${target.prerequisite_for}`:'Primary target'}</span></div>
    </div>
    <p><strong>Planned sequence:</strong> {Object.entries(counts).map(([stage,count])=>`${stageLabels[stage]||stage.replaceAll('_',' ')} × ${count}`).join(' · ')}</p>{latest?.available&&<div className="targeted-parent-followthrough"><h3>Latest completed targeted session</h3><p>{latest.title} · {latest.purpose}</p><p><strong>Evidence:</strong> {latest.evidence.answered} answered, {latest.evidence.independent_successes} independent successes, {latest.evidence.support_used_questions} questions with support, {latest.evidence.independent_checks} independent checks.</p><p><strong>Before → after:</strong> {latest.before.questions} → {latest.after.questions} evidence questions.</p></div>}
  </section>;
}
