import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {Worksheet} from './main';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

const question = {id: 1, topic: 'algebra', skill: 'VC2M4A01:unknown_add_subtract', level: 4, prompt: '□ + 18 = 43', summary: 'Solve the equation', answer_type: 'number', payload: {}, position: 0, status: 'current', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []};
const worksheet: any = {id: 10, date: '2026-08-16', completed_at: null, score: 0, total: 1, xp_earned: 0, current_question_id: 1, current_phase: 'main', elapsed_seconds: 0, status: 'in_progress', selected_topic: 'algebra', session_kind: 'practice', test_mode: false, counts: {correct: 0, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [question]};
const mentor = {action: 'why', title: 'Keep the equation balanced', stage: 1, guiding_question: 'What has happened to the unknown number?', body: 'An equals sign says both sides have the same value.', why: 'Both sides must stay equal.', memory_tip: 'Use the inverse operation.', worked_example: 'For □ + 7 = 19, subtract 7 from 19.', final_answer_revealed: false, visual_recommendation: {model: 'number-line', message: 'Try the number line model. The jumps show the same changes as the calculation.', automatic_open: false}};

beforeEach(() => { localStorage.clear(); localStorage.setItem('token', 'student-token'); vi.restoreAllMocks(); });
afterEach(cleanup);

describe('Math Mentor', () => {
  it('is available as a collapsible, keyboard-accessible panel on every worksheet question', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input);
      if (url.includes('/math-mentor-v0310?action=why')) return response(mentor);
      return response({detail: 'unexpected'}, false, 404);
    });
    render(<Worksheet ws={worksheet} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const toggle = screen.getByRole('button', {name: /Math Mentor/i});
    expect(toggle).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(toggle);
    expect(toggle).toHaveAttribute('aria-expanded', 'true');
    fireEvent.click(screen.getByRole('button', {name: 'Why?'}));
    expect(await screen.findByText('Why this works')).toBeInTheDocument();
    expect(screen.getByText(/same changes as the calculation/i)).toBeInTheDocument();
    expect(fetchMock.mock.calls.some(call => String(call[0]).includes('/math-mentor-v0310?action=why'))).toBe(true);
  });

  it('uses a non-blocking fallback when browser read aloud is unavailable', () => {
    const original = (window as any).speechSynthesis;
    Object.defineProperty(window, 'speechSynthesis', {value: undefined, configurable: true});
    render(<Worksheet ws={worksheet} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', {name: /Math Mentor/i}));
    fireEvent.click(screen.getAllByRole('button', {name: /Read aloud/}).at(-1)!);
    expect(screen.getByRole('status')).toHaveTextContent(/not available in this browser/i);
    Object.defineProperty(window, 'speechSynthesis', {value: original, configurable: true});
  });

  it('restarts mentoring without clearing the active worksheet', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      if (String(input).includes('/math-mentor/start-over')) return response({...mentor, action: 'guide', reset: true});
      return response({detail: 'unexpected'}, false, 404);
    });
    render(<Worksheet ws={worksheet} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', {name: /Math Mentor/i}));
    fireEvent.click(screen.getByRole('button', {name: /Start over/i}));
    await waitFor(() => expect(screen.getByText('Try this first')).toBeInTheDocument());
    expect(screen.getByText(question.prompt)).toBeInTheDocument();
  });
});
