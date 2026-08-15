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
    fireEvent.change(screen.getByLabelText('Feedback type'), {target: {value: 'bug'}});
    fireEvent.change(screen.getByLabelText('Note'), {target: {value: 'The image is stale.'}});
    fireEvent.click(screen.getByRole('button', {name: 'Save question note'}));
    expect(await screen.findByText('The image is stale.')).toBeInTheDocument();
  });
});
