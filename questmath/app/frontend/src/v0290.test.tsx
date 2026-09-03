import React from 'react';
import {afterEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {Worksheet} from './main';
import './test-setup';

const question: any = {id: 1, topic: 'number', skill: 'VC2M4N06:efficient_multiply', level: 4, prompt: 'Calculate 37 × 6.', summary: 'Calculate 37 × 6.', answer_type: 'number', payload: {}, position: 0, status: 'current', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []};
const worksheet: any = {id: 10, date: '2026-08-19', completed_at: null, score: 0, total: 1, xp_earned: 0, current_question_id: 1, current_phase: 'main', elapsed_seconds: 0, status: 'in_progress', selected_topic: 'number', session_kind: 'practice', test_mode: false, counts: {correct: 0, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [question]};

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

afterEach(() => { cleanup(); vi.restoreAllMocks(); });

describe('v0.29 optional tutoring', () => {
  it('keeps retry available after an incorrect answer without requiring Math Mentor', async () => {
    let attempts = 0;
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = typeof input === 'string' ? input : input instanceof Request ? input.url : String(input);
      if (url.includes('/questions/1/answer')) {
        attempts += 1;
        return response(attempts === 1 ? {correct: false, retry_allowed: true, mentor_required: false, message: 'Have another look.'} : {correct: true, retry_allowed: false, message: 'Great job!'});
      }
      if (url.includes('/worksheets/10/view')) return response({...worksheet, counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 0, hints: 0}, questions: [{...question, status: 'correct'}]});
      return response({detail: 'unexpected'}, false, 404);
    });
    render(<Worksheet ws={worksheet} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    let input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '216'}});
    fireEvent.click(screen.getByRole('button', {name: 'Check answer'}));
    expect(await screen.findByRole('dialog', {name: 'Incorrect answer'})).toBeInTheDocument();
    expect(screen.getByText('Have another look.')).toBeInTheDocument();
    expect(screen.getByRole('button', {name: /Try again/i})).toBeEnabled();
    fireEvent.click(screen.getByRole('button', {name: /Try again/i}));
    input = screen.getByRole('textbox', {name: 'Your answer'});
    await waitFor(() => expect(input).toHaveFocus());
    fireEvent.change(input, {target: {value: '222'}});
    fireEvent.click(screen.getByRole('button', {name: 'Check answer'}));
    expect(await screen.findByRole('dialog', {name: 'Correct answer'})).toBeInTheDocument();
    expect(screen.getByText('Great job!')).toBeInTheDocument();
    expect(attempts).toBe(2);
  });
});
