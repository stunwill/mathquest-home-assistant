import React from 'react';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, describe, expect, it, vi} from 'vitest';

import {AdaptiveRecommendation} from './adaptive-recommendation';

afterEach(cleanup);

describe('adaptive next-session recommendation', () => {
  it('explains a prerequisite recommendation without exposing technical codes or modes', () => {
    const start = vi.fn();
    render(<AdaptiveRecommendation busy={false} onStart={start} data={{
      summary: {review_due: 3},
      recommendation: {
        mode: 'guided', minutes: 15, topic: 'number', outcome_code: 'VC2M4N06',
        title: 'Guided Efficient calculation strategies',
        reason: 'Build efficient calculation strategies first because it supports unknown values in equations.',
        prerequisite_for: 'VC2M4A01',
      },
    }}/>);
    expect(screen.getByText(/supports unknown values/i)).toBeTruthy();
    expect(screen.getByText('3 ready to review')).toBeTruthy();
    expect(screen.queryByText('VC2M4N06')).toBeNull();
    expect(screen.queryByText('guided')).toBeNull();
    fireEvent.click(screen.getByRole('button', {name: 'Start 15-minute session'}));
    expect(start).toHaveBeenCalledOnce();
  });

  it('shows diagnostic recommendation without an implementation label', () => {
    render(<AdaptiveRecommendation busy={false} onStart={vi.fn()} data={{
      summary: {review_due: 0},
      recommendation: {
        mode: 'diagnostic', minutes: 15, topic: 'number_algebra', outcome_code: null,
        title: 'Find the best starting point', reason: 'Complete the Levels 2–6 diagnostic.', prerequisite_for: null,
      },
    }}/>);
    expect(screen.getByText('Find the best starting point')).toBeTruthy();
    expect(screen.queryByText('diagnostic')).toBeNull();
  });
});
