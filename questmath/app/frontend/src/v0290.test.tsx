import React from 'react';
import {afterEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {Worksheet} from './main';
import './test-setup';

const question: any = {id: 1, topic: 'number', skill: 'VC2M4N06:efficient_multiply', level: 4, prompt: 'Calculate 37 × 6.', summary: 'Calculate 37 × 6.', answer_type: 'number', payload: {}, position: 0, status: 'current', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []};
const worksheet: any = {id: 10, date: '2026-08-19', completed_at: null, score: 0, total: 1, xp_earned: 0, current_question_id: 1, current_phase: 'main', elapsed_seconds: 0, status: 'in_progress', selected_topic: 'number', session_kind: 'practice', test_mode: false, counts: {correct: 0, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [question]};

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('v0.29 optional tutoring', () => {
  it('keeps Check answer available after an incorrect answer', async () => {
    let attempts = 0;
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input);
      if (url.includes('/questions/1/answer')) {
        attempts += 1;
        return Promise.resolve(new Response(JSON.stringify(attempts === 1 ? {correct: false, retry_allowed: true, mentor_required: false, message: 'Have another look.'} : {correct: true, retry_allowed: false, message: 'Great job!'}), {status: 200, headers: {'content-type': 'application/json'}}));
      }
      if (url.includes('/math-mentor?action=guide')) return Promise.resolve(new Response(JSON.stringify({action: 'guide', title: 'Try this first', body: 'What operation is being used?', guiding_question: 'What operation is being used?'}), {status: 200, headers: {'content-type': 'application/json'}}));
      return Promise.resolve(new Response(JSON.stringify({detail: 'unexpected'}), {status: 404}));
    });
    render(<Worksheet ws={worksheet} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByPlaceholderText('Type your answer');
    fireEvent.change(input, {target: {value: '216'}});
    fireEvent.click(screen.getByRole('button', {name: 'Check answer'}));
    await waitFor(() => expect(screen.getByText(/You can try another answer now/)).toBeInTheDocument());
    expect(screen.getByRole('button', {name: 'Check answer'})).toBeEnabled();
    fireEvent.change(input, {target: {value: '222'}});
    fireEvent.click(screen.getByRole('button', {name: 'Check answer'}));
    await waitFor(() => expect(screen.getByText('✅ Great job!')).toBeInTheDocument());
    expect(attempts).toBe(2);
  });
});
