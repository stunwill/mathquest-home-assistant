import React, {useEffect, useState} from 'react';
import {Brain, Clock3, RefreshCw} from 'lucide-react';
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

type Plan = {kind:string;minutes:number;purpose:string;title:string;reason:string;target_skill?:string|null};
const friendly=(value?:string|null)=>value?value.replaceAll('_',' '):'';

export function AdaptiveRecommendation({data, busy, onStart}: {data: any; busy: boolean; onStart: () => void}) {
  const recommendation: Recommendation | undefined = data?.recommendation;
  const[plan,setPlan]=useState<Plan|null>(null);
  useEffect(()=>{apiRequest<Plan>('/learning/session-plan-v0440').then(setPlan).catch(()=>setPlan(null))},[recommendation?.outcome_code,recommendation?.mode]);
  if (!recommendation) return null;
  const reviewCount = Number(data?.summary?.review_due || 0);
  const targeted=plan?.kind==='targeted';
  return <section className="panel adaptive-recommendation" aria-label="Recommended next session">
    <div className="adaptive-recommendation-copy">
      <p className="eyebrow">YOUR BEST NEXT STEP</p>
      {targeted&&<div className="adaptive-target-focus"><Brain size={18}/><span><small>TODAY’S FOCUS</small><b>{plan.title}</b></span></div>}
      <h2>{recommendation.title}</h2>
      <p>{targeted?plan.reason:recommendation.reason}</p>
      {targeted&&plan.target_skill&&<small className="adaptive-target-skill">Practising: {friendly(plan.target_skill)}</small>}
      <div className="adaptive-signals">
        <span><Clock3 size={16}/>{targeted?plan.minutes:recommendation.minutes} minutes</span>
        {reviewCount > 0 && <span><RefreshCw size={16}/>{reviewCount} ready to review</span>}
      </div>
    </div>
    <button type="button" className="primary" disabled={busy} onClick={onStart}>
      {busy ? 'Building your session…' : `Start ${targeted?plan.minutes:recommendation.minutes}-minute session`}
    </button>
  </section>;
}
