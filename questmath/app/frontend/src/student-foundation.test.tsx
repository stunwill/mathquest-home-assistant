import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {createWorksheet} from './api';
import {ErrorNotice, LearningCalendar, StoryAdventures, WorksheetHistory} from './student-foundation';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('token', 'test-token');
  vi.restoreAllMocks();
});
afterEach(cleanup);

describe('student learning foundation', () => {
  it('creates every standard worksheet through the single new-worksheet endpoint and remembers it', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({id: 42, selected_topic: 'number'}));
    await createWorksheet('number');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe('api/worksheets/new');
    expect(fetchMock.mock.calls[0][1]).toMatchObject({method: 'POST', body: JSON.stringify({topic: 'number'})});
    expect(localStorage.getItem('mq_active_worksheet_id')).toBe('42');
  });

  it('starts Story Adventure from the same timed adaptive session service', async () => {
    const onOpen = vi.fn();
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input, init) => {
      const url = String(input);
      if (url === 'api/adventures-v0340') return response([{id: 'space', icon: '🚀', title: 'Space Mission', intro: 'Launch', objective: 'Bring the crew home', recommended_goals: ['number', 'measurement']}]);
      if (url === 'api/sessions/new') {
        expect(init).toMatchObject({method: 'POST', body: JSON.stringify({kind: 'practice', minutes: 5, topic: 'mixed'})});
        return response({id: 9});
      }
      if (url === 'api/worksheets/9/adventure-v0340') return response({theme: 'space'});
      if (url === 'api/worksheets/9/view') return response({id: 9, selected_topic: 'Space Mission', session_kind: 'adventure'});
      return response({detail: 'missing'}, false, 404);
    });
    render(<StoryAdventures onOpen={onOpen}/>);
    fireEvent.click(await screen.findByRole('button', {name: '5 min'}));
    fireEvent.click(screen.getByRole('button', {name: /Space Mission/i}));
    await waitFor(() => expect(onOpen).toHaveBeenCalledWith({id: 9, selected_topic: 'Space Mission', session_kind: 'adventure'}));
    expect(localStorage.getItem('mq_active_worksheet_id')).toBe('9');
    expect(fetchMock.mock.calls.map(call => String(call[0]))).toEqual([
      'api/adventures-v0340', 'api/sessions/new', 'api/worksheets/9/adventure-v0340', 'api/worksheets/9/view',
    ]);
  });

  it('offers only the existing 5, 10 and 15 minute Story Adventure choices', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([{id: 'space', icon: '🚀', title: 'Space Mission', intro: 'Launch', objective: 'Bring the crew home'}]));
    render(<StoryAdventures onOpen={vi.fn()}/>);
    expect(await screen.findByRole('group', {name: 'Story Adventure session length'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: '5 min'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: '10 min'})).toHaveAttribute('aria-pressed', 'true');
    expect(screen.getByRole('button', {name: '15 min'})).toBeInTheDocument();
  });

  it('renders worksheet history in React and opens the shared new-worksheet picker', async () => {
    const onCreate = vi.fn();
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([]));
    render(<WorksheetHistory onCreate={onCreate} onOpen={vi.fn()}/>);
    fireEvent.click(await screen.findByRole('button', {name: '+ New worksheet'}));
    expect(onCreate).toHaveBeenCalledOnce();
    expect(screen.getByRole('region', {name: 'Worksheet history'})).toBeInTheDocument();
  });

  it('navigates the React-owned calendar and shows recoverable request errors', async () => {
    let calls = 0;
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => {
      calls += 1;
      if (calls === 1) return Promise.reject(new TypeError('offline'));
      return response({start: '2026-08-03', end: '2026-08-09', days: []});
    });
    render(<LearningCalendar onOpen={vi.fn()}/>);
    expect(await screen.findByRole('alert')).toHaveTextContent('could not connect');
    fireEvent.click(screen.getByRole('button', {name: /Try again/i}));
    await waitFor(() => expect(screen.queryByRole('alert')).not.toBeInTheDocument());
    expect(screen.getByText(/3 Aug/)).toBeInTheDocument();
  });

  it('provides an accessible in-page retry instead of a browser alert', () => {
    const retry = vi.fn();
    render(<ErrorNotice message="Try the request again" retry={retry}/>);
    fireEvent.click(screen.getByRole('button', {name: /Try again/i}));
    expect(retry).toHaveBeenCalledOnce();
  });

  it('reviews the stored question visual and closes by Escape or backdrop click', async () => {
    const row = {id: 7, date: '2026-08-16', completed_at: '2026-08-16T01:00:00', display_title: 'Space', answered: 1, total: 1, score: 1, skipped: 0, hints: 0, xp_earned: 10, elapsed_seconds: 20, progress: 100, restartable_skipped: false};
    const review = {selected_topic: 'space', date: '2026-08-16', score: 1, total: 1, counts: {hints: 0}, questions: [{id: 3, position: 0, prompt: 'Which square?', payload: {visual_key: '7:3', visual: {type: 'grid', columns: ['A', 'B'], rows: 2, target: 'B2'}}, student_answers: [{answer: 'B2'}], correct_answer: 'B2', working: 'Read across then down.'}]};
    vi.spyOn(globalThis, 'fetch').mockImplementation(input => String(input).endsWith('/review') ? response(review) : response([row]));
    render(<WorksheetHistory onCreate={vi.fn()} onOpen={vi.fn()}/>);
    const open = await screen.findByRole('button', {name: 'View worksheet'});
    fireEvent.click(open);
    expect(await screen.findByRole('dialog', {name: /space/i})).toBeInTheDocument();
    expect(screen.getByRole('group', {name: /Grid reference diagram/i})).toBeInTheDocument();
    fireEvent.keyDown(window, {key: 'Escape'});
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
    fireEvent.click(open);
    const dialog = await screen.findByRole('dialog');
    const backdrop = dialog.parentElement as HTMLElement;
    fireEvent.mouseDown(backdrop, {target: backdrop});
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument());
  });
});
