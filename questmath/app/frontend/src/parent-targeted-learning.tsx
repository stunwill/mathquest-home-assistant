import React, {useEffect, useState} from 'react';
import {apiRequest} from './api';

type Plan = {
  kind:string;minutes:number;purpose:string;student_title:string;student_reason:string;
  primary_target?:{outcome_code?:string|null;title?:string;skill?:string|null;prerequisite_for?:string|null;evidence_questions?:number;status?:string|null;review_due?:boolean};
  stages?:string[];
};

export function ParentTargetedLearningInsight(){
  const[data,setData]=useState<Plan|null>(null);
  useEffect(()=>{apiRequest<Plan>('/learning/session-plan-v0440').then(setData).catch(()=>setData(null))},[]);
  if(!data||data.kind==='diagnostic'||!data.primary_target)return null;
  const target=data.primary_target;
  const counts=(data.stages||[]).reduce((acc:any,stage)=>{acc[stage]=(acc[stage]||0)+1;return acc},{});
  return <section className="panel" aria-label="Targeted learning plan">
    <p className="eyebrow">NEXT TARGETED LEARNING PLAN</p>
    <h2>{target.title}</h2>
    <p>{data.student_reason}</p>
    <div className="curriculum-table">
      <div className="curriculum-row"><span><b>Purpose</b><small>{data.purpose}</small></span><span>{data.minutes} minutes</span><span>{target.evidence_questions ?? 0} evidence questions</span><span>{target.status?.replaceAll('_',' ')||'Not assessed'}</span></div>
      <div className="curriculum-row"><span><b>Outcome</b><small>{target.outcome_code||'—'}</small></span><span>{target.skill?.replaceAll('_',' ')||'—'}</span><span>{target.review_due?'Review due':'Current learning'}</span><span>{target.prerequisite_for?`Prerequisite for ${target.prerequisite_for}`:'Primary target'}</span></div>
    </div>
    <p><strong>Planned sequence:</strong> {Object.entries(counts).map(([stage,count])=>`${stage.replaceAll('_',' ')} × ${count}`).join(' · ')}</p>
  </section>;
}
