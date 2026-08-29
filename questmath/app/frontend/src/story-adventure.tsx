import React from 'react';

export type AdventureProgress = {
  version?: number;
  theme: string;
  title: string;
  mission?: string;
  objective?: string;
  outcome?: string;
  chapter?: string;
  chapter_number?: number;
  chapters?: string[];
  stage?: string;
  stage_number?: number;
  stages?: string[];
  question: number;
  total: number;
  learning_goal?: string;
  learning_goals?: string[];
  learning_purpose?: string;
  learning_purpose_label?: string;
  adaptive_reason?: string;
  context?: {
    lead_in?: string;
    challenge_label?: string;
    success_text?: string;
  };
};

export function StoryMissionProgress({adventure}: {adventure: AdventureProgress}) {
  const steps = adventure.stages?.length ? adventure.stages : (adventure.chapters || []);
  const currentName = adventure.stage || adventure.chapter || steps[0] || 'Challenge';
  const current = Math.max(
    1,
    adventure.stage_number || adventure.chapter_number || steps.indexOf(currentName) + 1 || 1,
  );
  const totalSteps = Math.max(1, steps.length || 5);
  const progress = Math.max(0, Math.min(100, Math.round((adventure.question / Math.max(1, adventure.total)) * 100)));

  return <section className="story-mission-progress" aria-label={`${adventure.title} mission progress`}>
    <div className="story-mission-copy">
      <p className="eyebrow">STORY ADVENTURE · STAGE {current} OF {totalSteps}</p>
      <h2>{adventure.mission || adventure.title}</h2>
      <p>{adventure.context?.lead_in || adventure.objective}</p>
      <div className="story-purpose-row">
        <span>{adventure.learning_purpose_label || 'Practising this skill'}</span>
        <small>{adventure.context?.challenge_label || (adventure.learning_goal || 'mixed').replaceAll('_', ' ')}</small>
      </div>
    </div>
    <div className="story-progress-wrap" aria-label="Adventure progress">
      <div className="story-progress-track" aria-hidden="true"><i style={{width: `${progress}%`}}/></div>
      <small>{adventure.question} of {adventure.total} challenges · {progress}% complete</small>
    </div>
    <div className="story-chapters" aria-label="Mission stages">
      {(steps.length ? steps : [currentName]).map((name, index) =>
        <span key={`${name}-${index}`} className={index + 1 < current ? 'complete' : index + 1 === current ? 'current' : ''} title={name}>
          {index + 1 < current ? '✓' : index + 1}
        </span>)}
    </div>
    <small className="story-stage-label">{currentName} · Focus: {(adventure.learning_goal || 'mixed').replaceAll('_', ' ')}</small>
  </section>;
}

export function MissionOutcome({adventure}: {adventure: any}) {
  if (!adventure) return null;
  return <section className="mission-outcome">
    <span>🏁</span>
    <div>
      <p className="eyebrow">MISSION COMPLETE</p>
      <h2>{adventure.mission || adventure.title}</h2>
      <p>{adventure.outcome}</p>
      <small>Adventure completion celebrates the session. Learning progress still comes from the maths evidence collected during each challenge.</small>
      {adventure.status === 'complete_with_review' && <small>Some challenges were skipped. You can restart them from worksheet history.</small>}
    </div>
  </section>;
}
