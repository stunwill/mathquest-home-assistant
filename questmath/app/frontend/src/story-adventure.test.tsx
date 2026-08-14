import React from 'react';
import {render, screen} from '@testing-library/react';
import {describe, expect, it} from 'vitest';

import {MissionOutcome, StoryMissionProgress} from './story-adventure';

const adventure = {
  version: 2,
  theme: 'space',
  title: 'Space Mission',
  mission: 'Bring the research crew home',
  objective: 'Navigate the grid and prepare re-entry.',
  outcome: 'The research crew lands safely.',
  chapter: 'Navigate the asteroid field',
  chapter_number: 3,
  chapters: ['Prepare for launch', 'Reach orbit', 'Navigate the asteroid field', 'Prepare re-entry', 'Land safely'],
  question: 5,
  total: 10,
  learning_goal: 'space',
};

describe('Story Adventures 2.0', () => {
  it('shows the mission, current chapter and learning focus', () => {
    render(<StoryMissionProgress adventure={adventure}/>);
    expect(screen.getByText('Bring the research crew home')).toBeTruthy();
    expect(screen.getByText(/CHAPTER 3 OF 5/)).toBeTruthy();
    expect(screen.getByText(/Focus: space/)).toBeTruthy();
    const steps = screen.getByLabelText('Mission chapters').querySelectorAll('span');
    expect(steps).toHaveLength(5);
    expect(steps[0].textContent).toBe('✓');
    expect(steps[2].className).toContain('current');
  });

  it('shows the final story outcome and skipped-question recovery', () => {
    render(<MissionOutcome adventure={{...adventure, status: 'complete_with_review'}}/>);
    expect(screen.getByText('MISSION COMPLETE')).toBeTruthy();
    expect(screen.getByText('The research crew lands safely.')).toBeTruthy();
    expect(screen.getByText(/restart them from worksheet history/i)).toBeTruthy();
  });
});
