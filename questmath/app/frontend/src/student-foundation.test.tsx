import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {createWorksheet} from './api';
import {ErrorNotice, LearningCalendar, StoryAdventures, WorksheetHistory} from './student-foundation';
import './test-setup';

function response(data: any, ok = true, status = 200) {
  return Promise.resolve(new Response(JSON.stringify(data), {status, headers: {'content-type': 'application/json'}}));
}

const completedRow = (id: number, title = `Worksheet ${id}`) => ({id, date: '2026-09-03', completed_at: '2026-09-03T01:00:00', display_title: title, answered: 12, total: 12, score: 12, skipped: 0, hints: 0, xp_earned: 10, elapsed_seconds: 540, progress: 100, restartable_skipped: false});

beforeEach(() => {
  localStorage.clear();
  localStorage.setItem('token', 'test-token');
  vi.restoreAllMocks();
  Object.defineProperty(window, 'scrollTo', {value: vi.fn(), writable: true});
  Object.defineProperty(Element.prototype, 'scrollIntoView', {value: vi.fn(), writable: true});
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

  it('renders semantic student navigation without exposing parent functions', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([{id: 'space', icon: '🚀', title: 'Space Mission', intro: 'Launch', objective: 'Bring the crew home'}]));
    render(<StoryAdventures onOpen={vi.fn()}/>);
    const nav = await screen.findByRole('navigation', {name: 'Student navigation'});
    expect(nav).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Home'})).toHaveAttribute('aria-current', 'page');
    fireEvent.click(screen.getByRole('button', {name: 'Worksheets'}));
    expect(screen.getByRole('button', {name: 'Worksheets'})).toHaveAttribute('aria-current', 'page');
    expect(screen.queryByText(/Parent Dashboard/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Parent Tests/i)).not.toBeInTheDocument();
  });

  it('puts unfinished work in Continue Learning ahead of completed history', async () => {
    const inProgress = {id: 90, date: '2026-09-05', completed_at: null, display_title: 'Space Mission', answered: 4, total: 20, score: 4, skipped: 1, hints: 1, xp_earned: 0, elapsed_seconds: 180, progress: 20, restartable_skipped: false};
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([completedRow(1, 'Old completed'), inProgress, completedRow(2, 'Recent completed')]));
    render(<WorksheetHistory onCreate={vi.fn()} onOpen={vi.fn()}/>);
    const continueRegion = await screen.findByRole('article', {name: 'Continue learning'});
    expect(continueRegion).toHaveTextContent('Space Mission');
    expect(continueRegion).toHaveTextContent('4 of 20 answered');
    expect(screen.getAllByRole('button', {name: 'Review'})).toHaveLength(2);
    expect(screen.queryByText('In progress · 20%')).not.toBeInTheDocument();
  });

  it('shows skipped-question recovery when there is no active worksheet', async () => {
    const recovery = {...completedRow(8, 'Fractions'), skipped: 2, restartable_skipped: true};
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([recovery, completedRow(9)]));
    render(<WorksheetHistory onCreate={vi.fn()} onOpen={vi.fn()}/>);
    expect(await screen.findByRole('article', {name: 'Continue learning'})).toHaveTextContent('2 questions need another try');
    expect(screen.getByRole('button', {name: 'Finish worksheet'})).toBeInTheDocument();
  });

  it('limits recent history to three rows and provides progressive disclosure', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([completedRow(1), completedRow(2), completedRow(3), completedRow(4), completedRow(5)]));
    render(<WorksheetHistory onCreate={vi.fn()} onOpen={vi.fn()}/>);
    await screen.findByText('Worksheet 1');
    expect(screen.getAllByRole('button', {name: 'Review'})).toHaveLength(3);
    const viewAll = screen.getByRole('button', {name: 'View all worksheets →'});
    expect(viewAll).toHaveAttribute('aria-expanded', 'false');
    fireEvent.click(viewAll);
    expect(screen.getAllByRole('button', {name: 'Review'})).toHaveLength(5);
    expect(screen.getByRole('button', {name: 'Show recent only'})).toHaveAttribute('aria-expanded', 'true');
  });

  it('renders worksheet history in React and opens the shared new-worksheet picker', async () => {
    const onCreate = vi.fn();
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([]));
    render(<WorksheetHistory onCreate={onCreate} onOpen={vi.fn()}/>);
    fireEvent.click(await screen.findByRole('button', {name: '+ New worksheet'}));
    expect(onCreate).toHaveBeenCalledOnce();
    expect(screen.getByRole('region', {name: 'Worksheet history'})).toBeInTheDocument();
  });

  it('uses readable previous and next week controls and retains Today', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({start: '2026-08-31', end: '2026-09-06', days: []}));
    render(<LearningCalendar onOpen={vi.fn()}/>);
    expect(await screen.findByRole('button', {name: 'Previous week'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Next week'})).toBeInTheDocument();
    expect(screen.getByRole('button', {name: 'Today'})).toBeInTheDocument();
    expect(screen.getByText(/31 Aug/)).toBeInTheDocument();
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
    const open = await screen.findByRole('button', {name: 'Review'});
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
