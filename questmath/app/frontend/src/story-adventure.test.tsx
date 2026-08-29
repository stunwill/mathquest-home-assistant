import React from 'react';
import {render, screen} from '@testing-library/react';
import {describe, expect, it} from 'vitest';

import {MissionOutcome, StoryMissionProgress} from './story-adventure';

const adventure = {
  version: 3,
  theme: 'space',
  title: 'Space Mission',
  mission: 'Bring the research crew home',
  objective: 'Navigate the grid and prepare re-entry.',
  outcome: 'The research crew lands safely.',
  stage: 'Discovery',
  stage_number: 3,
  stages: ['Start', 'Challenge', 'Discovery', 'Harder Challenge', 'Final Challenge', 'Completion'],
  question: 5,
  total: 10,
  learning_goal: 'space',
  learning_purpose: 'review',
  learning_purpose_label: 'Quick review',
  context: {
    lead_in: 'Mission control needs your space thinking before the crew can continue.',
    challenge_label: 'Grid Reference',
  },
};

describe('Story Adventure expansion', () => {
  it('shows adaptive learning purpose, stage and progress', () => {
    render(<StoryMissionProgress adventure={adventure}/>);
    expect(screen.getByText('Bring the research crew home')).toBeTruthy();
    expect(screen.getByText(/STAGE 3 OF 6/)).toBeTruthy();
    expect(screen.getByText('Quick review')).toBeTruthy();
    expect(screen.getByText('Grid Reference')).toBeTruthy();
    expect(screen.getByText(/5 of 10 challenges · 50% complete/)).toBeTruthy();
    const steps = screen.getByLabelText('Mission stages').querySelectorAll('span');
    expect(steps).toHaveLength(6);
    expect(steps[0].textContent).toBe('✓');
    expect(steps[2].className).toContain('current');
  });

  it('shows the final story outcome without treating completion as mastery', () => {
    render(<MissionOutcome adventure={{...adventure, status: 'complete_with_review'}}/>);
    expect(screen.getByText('MISSION COMPLETE')).toBeTruthy();
    expect(screen.getByText('The research crew lands safely.')).toBeTruthy();
    expect(screen.getByText(/Learning progress still comes from the maths evidence/i)).toBeTruthy();
    expect(screen.getByText(/restart them from worksheet history/i)).toBeTruthy();
  });
});
