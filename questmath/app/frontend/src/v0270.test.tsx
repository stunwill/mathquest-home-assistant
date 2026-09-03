import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {QuestCategoryPicker, Worksheet} from './main';
import {QuestionVisual} from './question-visual';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

const questions = [
  {id: 1, topic: 'number', skill: 'VC2M4N06:fact_recall_addition', level: 3, prompt: 'Calculate 4 + 4.', summary: 'Calculate 4 + 4.', answer_type: 'number', payload: {}, position: 0, status: 'current', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []},
  {id: 2, topic: 'number', skill: 'VC2M4N06:fact_recall_addition', level: 3, prompt: 'Calculate 5 + 5.', summary: 'Calculate 5 + 5.', answer_type: 'number', payload: {}, position: 1, status: 'not_started', skipped_count: 0, hint_count: 0, last_hint: null, attempts: []},
];

function worksheet(overrides: any = {}) {
  return {id: 10, date: '2026-08-16', completed_at: null, score: 0, total: 2, xp_earned: 0, current_question_id: 1, current_phase: 'main', elapsed_seconds: 0, status: 'in_progress', selected_topic: 'number', session_kind: 'parent_test', test_mode: true, counts: {correct: 0, incorrect: 0, skipped: 0, remaining: 2, hints: 0}, questions, ...overrides};
}

beforeEach(() => { localStorage.clear(); localStorage.setItem('token', 'parent-token'); vi.restoreAllMocks(); });
afterEach(cleanup);

describe('MathQuest 0.27 learner and parent-test interactions', () => {
  it('makes session choices visibly selectable and submits the selected configuration', async () => {
    const start = vi.fn().mockResolvedValue(undefined);
    render(<QuestCategoryPicker start={start} cancel={vi.fn()}/>);
    const fifteen = screen.getByRole('button', {name: /15 minutes/i});
    const number = screen.getByRole('button', {name: /Number Place value/i});
    fireEvent.click(fifteen);
    fireEvent.click(number);
    expect(fifteen).toHaveAttribute('aria-pressed', 'true');
    expect(number).toHaveAttribute('aria-pressed', 'true');
    fireEvent.click(screen.getByRole('button', {name: 'Start 15-minute session'}));
    await waitFor(() => expect(start).toHaveBeenCalledWith('number', 15, 'practice'));
  });

  it('shows a visual before and after rotation once a symmetry hint is used', () => {
    render(<QuestionVisual question={{id: 9, hint_count: 1, payload: {visual_key: '9', visual: {type: 'rotational_symmetry', sides: 6}}}}/>);
    expect(screen.getByRole('img')).toHaveAccessibleName(/shown before and after a partial rotation/i);
    expect(screen.getByText('Starting position')).toBeInTheDocument();
    expect(screen.getByText('After one matching turn')).toBeInTheDocument();
  });

  it('answers and advances a parent test with the two-Enter feedback flow without requiring a note', async () => {
    const answered = worksheet({counts: {correct: 1, incorrect: 0, skipped: 0, remaining: 1, hints: 0}, questions: [{...questions[0], status: 'correct', attempts: [{answer: '8', correct: true, attempt_number: 1}]}, questions[1]]});
    const moved = {...answered, current_question_id: 2, questions: [answered.questions[0], {...questions[1], status: 'current'}]};
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input);
      if (url === 'api/questions/1/answer') return response({correct: true, retry_allowed: false, message: 'Correct!', working: 'Use a known double.'});
      if (url === 'api/worksheets/10/view') return response(answered);
      if (url === 'api/worksheets/10/navigate/2') return response(moved);
      return response({detail: 'missing'}, false, 404);
    });
    render(<Worksheet ws={worksheet() as any} onUpdate={vi.fn()} onExit={vi.fn()} onDone={vi.fn()}/>);
    const input = screen.getByRole('textbox', {name: 'Your answer'});
    fireEvent.change(input, {target: {value: '8'}});
    fireEvent.keyDown(input, {key: 'Enter'});
    expect(await screen.findByRole('dialog', {name: 'Correct answer'})).toBeInTheDocument();
    expect(screen.getByLabelText(/Note.*optional/i).closest('label')).toHaveTextContent('optional');
    const next = screen.getByRole('button', {name: /Next question/i});
    await waitFor(() => expect(next).toHaveFocus());
    fireEvent.keyDown(next, {key: 'Enter'});
    await waitFor(() => expect(fetchMock.mock.calls.some(call => String(call[0]) === 'api/worksheets/10/navigate/2')).toBe(true));
  });
});
