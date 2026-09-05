import React from 'react';
import {Clock3, RefreshCw} from 'lucide-react';

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
  const reviewCount = Number(data?.summary?.review_due || 0);
  return <section className="panel adaptive-recommendation" aria-label="Recommended next session">
    <div className="adaptive-recommendation-copy">
      <p className="eyebrow">YOUR BEST NEXT STEP</p>
      <h2>{recommendation.title}</h2>
      <p>{recommendation.reason}</p>
      <div className="adaptive-signals">
        <span><Clock3 size={16}/>{recommendation.minutes} minutes</span>
        {reviewCount > 0 && <span><RefreshCw size={16}/>{reviewCount} ready to review</span>}
      </div>
    </div>
    <button type="button" className="primary" disabled={busy} onClick={onStart}>
      {busy ? 'Building your session…' : `Start ${recommendation.minutes}-minute session`}
    </button>
  </section>;
}
