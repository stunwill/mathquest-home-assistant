import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {createIntervention, questionDraft, rememberQuestionDraft} from './api';
import {InterventionCard, InterventionGoal} from './intervention';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

beforeEach(() => { localStorage.clear(); localStorage.setItem('token', 'test-token'); vi.restoreAllMocks(); });
afterEach(cleanup);

describe('v0.26 Number and Algebra intervention', () => {
  it('shows independent and supported evidence and starts the selected session length', async () => {
    const onOpen = vi.fn();
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      if (String(input) === 'api/learning/intervention-v0260') return response({
        recommended_focus: 'subtraction', reason: 'Build the weakest area.',
        focuses: [{focus: 'subtraction', questions: 6, independent_accuracy: 40, supported_accuracy: 80, status: 'needs_support'}],
      });
      return response({id: 91, session_kind: 'intervention', target_minutes: 15});
    });
    render(<InterventionCard onOpen={onOpen}/>);
    expect(await screen.findByText(/Build subtraction/i)).toBeInTheDocument();
    expect(screen.getByText('Independent 40%')).toBeInTheDocument();
    expect(screen.getByText('With support 80%')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', {name: '15 min'}));
    fireEvent.click(screen.getByRole('button', {name: /Start 15-minute intervention/i}));
    await waitFor(() => expect(onOpen).toHaveBeenCalledWith({id: 91, session_kind: 'intervention', target_minutes: 15}));
    expect(fetchMock.mock.calls[1][0]).toBe('api/interventions/new');
    expect(fetchMock.mock.calls[1][1]).toMatchObject({method: 'POST', body: JSON.stringify({minutes: 15, focus: 'auto'})});
    expect(localStorage.getItem('mq_active_worksheet_id')).toBe('91');
  });

  it('persists answer drafts by worksheet and question without mixing questions', () => {
    rememberQuestionDraft(12, 31, 'working answer');
    rememberQuestionDraft(12, 32, 'different answer');
    expect(questionDraft(12, 31)).toBe('working answer');
    expect(questionDraft(12, 32)).toBe('different answer');
    rememberQuestionDraft(12, 31, '');
    expect(questionDraft(12, 31)).toBe('');
  });

  it('creates an intervention through the dedicated endpoint', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({id: 44}));
    await createIntervention(5, 'addition');
    expect(fetchMock.mock.calls[0][0]).toBe('api/interventions/new');
    expect(fetchMock.mock.calls[0][1]).toMatchObject({body: JSON.stringify({minutes: 5, focus: 'addition'})});
  });

  it('shows the intervention phase and explains evidence separation', () => {
    render(<InterventionGoal question={{payload: {intervention: {phase: 'teach', learning_goal: 'Use an efficient strategy.'}}}}/>);
    expect(screen.getByText('TEACH PHASE')).toBeInTheDocument();
    expect(screen.getByText(/independent result is recorded separately/i)).toBeInTheDocument();
  });
});
