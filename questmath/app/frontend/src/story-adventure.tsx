import React from 'react';

export type AdventureProgress = {
  version?: number;
  theme: string;
  title: string;
  mission?: string;
  objective?: string;
  outcome?: string;
  chapter: string;
  chapter_number?: number;
  chapters?: string[];
  question: number;
  total: number;
  learning_goal?: string;
  learning_goals?: string[];
};

export function StoryMissionProgress({adventure}: {adventure: AdventureProgress}) {
  const chapters = adventure.chapters || [];
  const chapter = Math.max(1, adventure.chapter_number || chapters.indexOf(adventure.chapter) + 1 || 1);
  return <section className="story-mission-progress" aria-label={`${adventure.title} mission progress`}>
    <div>
      <p className="eyebrow">STORY MISSION · CHAPTER {chapter} OF {chapters.length || 5}</p>
      <h2>{adventure.mission || adventure.title}</h2>
      <p>{adventure.objective}</p>
    </div>
    <div className="story-chapters" aria-label="Mission chapters">
      {(chapters.length ? chapters : [adventure.chapter]).map((name, index) =>
        <span key={`${name}-${index}`} className={index + 1 < chapter ? 'complete' : index + 1 === chapter ? 'current' : ''} title={name}>
          {index + 1 < chapter ? '✓' : index + 1}
        </span>)}
    </div>
    <small>{adventure.chapter} · Focus: {(adventure.learning_goal || 'mixed').replaceAll('_', ' ')}</small>
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
      {adventure.status === 'complete_with_review' && <small>Some challenges were skipped. You can restart them from worksheet history.</small>}
    </div>
  </section>;
}
