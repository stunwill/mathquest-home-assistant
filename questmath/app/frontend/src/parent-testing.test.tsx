import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {ParentTestWorksheets, TestQuestionFeedback} from './parent-testing';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

beforeEach(() => {
  localStorage.setItem('token', 'parent-token');
  vi.restoreAllMocks();
});
afterEach(cleanup);

describe('parent test worksheets', () => {
  it('creates a test worksheet from the parent dashboard without using learner worksheet storage', async () => {
    const onOpen = vi.fn();
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(input => {
      if (String(input) === 'api/testing/worksheets') {
        const method = fetchMock.mock.calls.at(-1)?.[1]?.method;
        return method === 'POST' ? response({id: 45, test_mode: true, session_kind: 'parent_test'}) : response([]);
      }
      return response({detail: 'missing'}, false, 404);
    });
    render(<ParentTestWorksheets onOpen={onOpen}/>);
    fireEvent.change(screen.getByLabelText('Learning area'), {target: {value: 'number'}});
    fireEvent.click(screen.getByRole('button', {name: 'Start test worksheet'}));
    await waitFor(() => expect(onOpen).toHaveBeenCalledWith({id: 45, test_mode: true, session_kind: 'parent_test'}));
    const createCall = fetchMock.mock.calls.find(call => call[1]?.method === 'POST');
    expect(createCall?.[0]).toBe('api/testing/worksheets');
    expect(createCall?.[1]?.body).toBe(JSON.stringify({topic: 'number', question_count: 10}));
  });

  it('records a structured note after a completed test question', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({
      id: 7, question_id: 3, feedback_type: 'bug', note: 'The image is stale.', status: 'open',
    }));
    render(<TestQuestionFeedback worksheetId={2} question={{id: 3}}/>);
    const noteField = screen.getByLabelText(/Note.*optional/i);
    expect(noteField.closest('label')).toHaveTextContent('optional');
    fireEvent.change(screen.getByLabelText('Feedback type'), {target: {value: 'bug'}});
    fireEvent.change(noteField, {target: {value: 'The image is stale.'}});
    fireEvent.click(screen.getByRole('button', {name: 'Save question note'}));
    expect(await screen.findByText('The image is stale.')).toBeInTheDocument();
  });

  it('shows stored visuals in the test review and closes accessibly', async () => {
    const item = {id: 8, selected_topic: 'space', started_at: '2026-08-16T01:00:00', answered: 1, total: 1, feedback_count: 0, open_feedback: 0, addressed_feedback: 0, addressed_releases: [], completed_at: '2026-08-16T01:01:00'};
    const detail = {...item, score: 1, feedback: [], questions: [{id: 4, position: 0, prompt: 'Which grid reference?', attempts: [{answer: 'A1'}], correct_answer: 'A1', working: 'Read the axes.', payload: {visual_key: '8:4', visual: {type: 'grid', columns: ['A', 'B'], rows: 2, target: 'A1'}}}]};
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => String(input) === 'api/testing/worksheets/8' ? response(detail) : response([item]));
    render(<ParentTestWorksheets onOpen={vi.fn()}/>);
    fireEvent.click(await screen.findByRole('button', {name: 'View test and notes'}));
    expect(await screen.findByRole('dialog', {name: /Space/i})).toBeInTheDocument();
    fireEvent.click(screen.getByText('1. Which grid reference?'));
    expect(screen.getByRole('group', {name: /Grid reference diagram/i})).toBeInTheDocument();
    fireEvent.keyDown(window, {key: 'Escape'});
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
