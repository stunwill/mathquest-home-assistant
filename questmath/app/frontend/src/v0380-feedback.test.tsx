import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {Worksheet} from './main';
import {PostAnswerFeedbackModal} from './post-answer-feedback';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

const q1 = {id: 1, topic: 'number', skill: 'VC2M5N06:addition', level: 5, prompt: 'Calculate 327 + 286.', summary: 'Calculate 327 + 286.', answer_type: 'number', payload: {}, position: 0, status: 'current', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []};
const q2 = {id: 2, topic: 'algebra', skill: 'VC2M5A01:unknown', level: 5, prompt: '□ + 18 = 43', summary: 'Solve the equation.', answer_type: 'number', payload: {}, position: 1, status: 'not_started', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []};
function worksheet(overrides: any = {}) {
  return {id: 10, date: '2026-09-02', completed_at: null, score: 0, total: 2, xp_earned: 0, current_question_id: 1, current_phase: 'main', elapsed_seconds: 0, status: 'in_progress', selected_topic: 'number', session_kind: 'practice', test_mode: false, counts: {correct: 0, incorrect: 0, skipped: 0, remaining: 2, hints: 0}, questions: [q1, q2], ...overrides};
}

beforeEach(() => { localStorage.clear(); localStorage.setItem('token', 'student-token'); vi.restoreAllMocks(); });
afterEach(cleanup);

describe('v0.38 iPad landscape answer feedback', () => {
  it('submits with Enter, opens the result dialog immediately and advances with the next Enter', async () => {
    const answered = worksheet({counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [{...q1, status: 'correct', attempts: [{answer: '613', correct: true, attempt_number: 1}]}, q2]});
    const moved = {...answered, current_question_id: 2, questions: [answered.questions[0], {...q2, status: 'current'}]};
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(input => {
      const url = String(input);
      if (url === 'api/questions/1/answer') return response({correct: true, retry_allowed: false, message: 'Correct!', working: '327 + 286 = 613.'});
      if (url === 'api/worksheets/10/view') return response(answered);
      if (url === 'api/worksheets/10/navigate/2') return response(moved);
      return response({detail: 'missing'}, false, 404);
    });
    render(<Worksheet ws={worksheet() as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '613'}});
    fireEvent.keyDown(input, {key: 'Enter'});
    const dialog = await screen.findByRole('dialog', {name: 'Correct answer'});
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(screen.getByText('327 + 286 = 613.')).toBeInTheDocument();
    const next = screen.getByRole('button', {name: /Next question/i});
    await waitFor(() => expect(next).toHaveFocus());
    fireEvent.keyDown(next, {key: 'Enter'});
    fireEvent.click(next);
    await waitFor(() => expect(fetchMock.mock.calls.some(call => String(call[0]) === 'api/worksheets/10/navigate/2')).toBe(true));
  });

  it('keeps retry-first feedback supportive, does not reveal terminal working, and restores an empty focused input', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => {
      if (String(input) === 'api/questions/1/answer') return response({correct: false, retry_allowed: true, message: 'Check the hundreds regrouping.', working: 'The final answer is 613.'});
      return response({detail: 'missing'}, false, 404);
    });
    render(<Worksheet ws={worksheet() as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '513'}});
    fireEvent.keyDown(input, {key: 'Enter'});
    expect(await screen.findByRole('dialog', {name: 'Incorrect answer'})).toBeInTheDocument();
    expect(screen.getByText('Check the hundreds regrouping.')).toBeInTheDocument();
    expect(screen.queryByText('The final answer is 613.')).not.toBeInTheDocument();
    const retry = screen.getByRole('button', {name: /Try again/i});
    fireEvent.click(retry);
    await waitFor(() => expect(screen.getByRole('textbox', {name: 'Your answer'})).toHaveFocus());
    expect(screen.getByRole('textbox', {name: 'Your answer'})).toHaveValue('');
  });

  it('keeps Math Mentor optional from retry feedback', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => {
      if (String(input) === 'api/questions/1/answer') return response({correct: false, retry_allowed: true, message: 'Try another strategy.'});
      return response({detail: 'missing'}, false, 404);
    });
    render(<Worksheet ws={worksheet() as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '500'}});
    fireEvent.keyDown(input, {key: 'Enter'});
    await screen.findByRole('dialog', {name: 'Incorrect answer'});
    fireEvent.click(screen.getByRole('button', {name: 'Math Mentor'}));
    expect(screen.queryByRole('dialog', {name: 'Incorrect answer'})).not.toBeInTheDocument();
    expect(screen.getByRole('button', {name: /Math Mentor/i})).toHaveAttribute('aria-expanded', 'true');
  });

  it('records the existing confidence evidence from inside the modal', async () => {
    const answered = worksheet({counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [{...q1, status: 'correct'}, q2]});
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(input => {
      const url = String(input);
      if (url === 'api/questions/1/answer') return response({correct: true, retry_allowed: false, message: 'Correct!', working: 'Add by place value.'});
      if (url === 'api/worksheets/10/view') return response(answered);
      if (url === 'api/questions/1/confidence') return response({saved: true});
      return response({detail: 'missing'}, false, 404);
    });
    render(<Worksheet ws={worksheet() as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '613'}}); fireEvent.keyDown(input, {key: 'Enter'});
    await screen.findByRole('dialog', {name: 'Correct answer'});
    fireEvent.click(screen.getByRole('button', {name: '🙂 Pretty sure'}));
    await waitFor(() => expect(fetchMock.mock.calls.some(call => String(call[0]) === 'api/questions/1/confidence')).toBe(true));
    expect(await screen.findByText('Thanks!')).toBeInTheDocument();
  });

  it('traps keyboard focus within the accessible feedback dialog', () => {
    render(<PostAnswerFeedbackModal feedback={{correct: false, retry_allowed: true}} primaryLabel="Try again" onPrimary={vi.fn()} onOpenMentor={vi.fn()}/>);
    const mentor = screen.getByRole('button', {name: 'Math Mentor'});
    const retry = screen.getByRole('button', {name: /Try again/i});
    retry.focus();
    fireEvent.keyDown(document, {key: 'Tab'});
    expect(mentor).toHaveFocus();
    mentor.focus();
    fireEvent.keyDown(document, {key: 'Tab', shiftKey: true});
    expect(retry).toHaveFocus();
  });

  it('uses the shared result modal after a touch-first interactive answer', async () => {
    const interactive = {...q1, answer_type: 'fraction_bar', payload: {visual: {denominator: 4}}, prompt: 'Shade 3/4 of the bar.'};
    const ws = worksheet({questions: [interactive, q2]});
    const answered = worksheet({counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [{...interactive, status: 'correct'}, q2]});
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => String(input) === 'api/questions/1/answer' ? response({correct: true, retry_allowed: false, message: 'Correct!', working: 'Three of four equal parts is 3/4.'}) : response(answered));
    render(<Worksheet ws={ws as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    fireEvent.click(screen.getByRole('button', {name: 'Select 3 of 4 equal parts'}));
    fireEvent.click(screen.getByRole('button', {name: 'Check answer'}));
    expect(await screen.findByRole('dialog', {name: 'Correct answer'})).toBeInTheDocument();
  });

  it('uses the same feedback experience for Story Adventure questions', async () => {
    const story = {...q1, payload: {adventure: {title: 'Space Mission', mission: 'Repair the navigation', stage_name: 'Launch', stage_index: 0, stage_count: 3}}};
    const ws = worksheet({session_kind: 'adventure', selected_topic: 'Space Mission', questions: [story, q2]});
    const answered = worksheet({session_kind: 'adventure', selected_topic: 'Space Mission', counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [{...story, status: 'correct'}, q2]});
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => String(input) === 'api/questions/1/answer' ? response({correct: true, retry_allowed: false, message: 'Mission maths correct.', working: 'Use place value.'}) : response(answered));
    render(<Worksheet ws={ws as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'}); fireEvent.change(input, {target: {value: '613'}}); fireEvent.keyDown(input, {key: 'Enter'});
    expect(await screen.findByRole('dialog', {name: 'Correct answer'})).toBeInTheDocument();
  });
});
