import React from 'react';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {afterEach, describe, expect, it, vi} from 'vitest';

import {HomeAssistantConnection, ParentLearningInsight} from './parent-insight';

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

const insight = {
  estimated_level: {baseline: 3, current: 4, target: 5, growth: 1},
  summary: {review_due: 2},
  weekly: {current: {independent_accuracy: 70, supported_accuracy: 90, average_seconds: 31}, narrative: 'Sienna is becoming more independent.'},
  recommendation: {title: 'Review efficient calculation strategies', reason: 'This skill is due for retrieval practice.', minutes: 10},
  gains: [{code: 'VC2M4N06', title: 'Efficient calculation strategies', growth_points: 30}],
  persistent_gaps: [{code: 'VC2M4A01', title: 'Unknown values in equations', mastery: 45}],
  strategies_used: [{strategy: 'Written subtraction with regrouping', questions: 4}],
  outcomes: [{code: 'VC2M4N06', title: 'Efficient calculation strategies', questions: 8, independent_accuracy: 70, supported_accuracy: 90, mastery: 72, retention_accuracy: 67, review_due: true, next_review_due: '2026-08-14'}],
};

describe('parent and Home Assistant insight', () => {
  it('separates independent and supported performance and shows the next step', () => {
    render(<ParentLearningInsight data={insight}/>);
    expect(screen.getAllByText('70%').length).toBeGreaterThan(0);
    expect(screen.getAllByText('90%').length).toBeGreaterThan(0);
    expect(screen.getByText(/\+1 level growth from 3/)).toBeTruthy();
    expect(screen.getByText('Review efficient calculation strategies')).toBeTruthy();
    expect(screen.getByText('Due now')).toBeTruthy();
  });

  it('reveals the parent-protected long-lived Home Assistant token on demand', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true,
      headers: {get: () => 'application/json'},
      json: async () => ({token: 'stable-service-token', stats_endpoint: '/api/ha/stats', summary_endpoint: '/api/ha/summary'}),
    }));
    render(<HomeAssistantConnection/>);
    fireEvent.click(screen.getByRole('button', {name: 'Show Home Assistant token'}));
    await waitFor(() => expect(screen.getByDisplayValue('Bearer stable-service-token')).toBeTruthy());
    expect(screen.getByText('/api/ha/stats')).toBeTruthy();
  });
});
