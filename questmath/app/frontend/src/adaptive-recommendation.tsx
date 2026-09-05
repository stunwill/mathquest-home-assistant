import React from 'react';
import {Clock3, RefreshCw, Route} from 'lucide-react';

type Recommendation = {
  mode: 'diagnostic' | 'guided' | 'review' | 'practice';
  minutes: 5 | 10 | 15;
  topic: string;
  outcome_code: string | null;
  title: string;
  reason: string;
  prerequisite_for: string | null;
};

export function AdaptiveRecommendation({data, busy, onStart}: {data: any; busy: boolean; onStart: () => void}) {
  const recommendation: Recommendation | undefined = data?.recommendation;
  if (!recommendation) return null;
  return <section className="panel adaptive-recommendation" aria-label="Recommended next session">
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
  </section>;
}
