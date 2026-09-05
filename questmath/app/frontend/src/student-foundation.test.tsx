import React from 'react';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor} from '@testing-library/react';
import {createWorksheet} from './api';
import {ErrorNotice, LearningCalendar, StoryAdventures, StudentDestination, StudentMobileNavigation, WorksheetHistory} from './student-foundation';
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
});
afterEach(cleanup);

describe('student learning foundation', () => {
  it('creates every standard worksheet through the single new-worksheet endpoint and remembers it', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({id: 42, selected_topic: 'number'}));
    await createWorksheet('number');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe('api/worksheets/new');
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
    expect(fetchMock.mock.calls.map(call => String(call[0]))).toEqual(['api/adventures-v0340', 'api/sessions/new', 'api/worksheets/9/adventure-v0340', 'api/worksheets/9/view']);
  });

  it('renders navigation as controlled destinations rather than scroll anchors', () => {
    const onSelect = vi.fn();
    render(<StudentMobileNavigation selected="home" onSelect={onSelect}/>);
    expect(screen.getByRole('button', {name: 'Home'})).toHaveAttribute('aria-current', 'page');
    fireEvent.click(screen.getByRole('button', {name: 'Progress'}));
    expect(onSelect).toHaveBeenCalledWith('progress');
  });

  it('renders the complete Story Adventure experience only in Adventure', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([{id:'space',icon:'🚀',title:'Space Mission',intro:'Launch',objective:'Bring the crew home'}]));
    const {rerender} = render(<StudentDestination section="home" onOpen={vi.fn()} onCreate={vi.fn()} onSelect={vi.fn()}/>);
    expect(await screen.findByRole('region', {name:'Adventure preview'})).toBeInTheDocument();
    expect(screen.queryByRole('group', {name:'Story Adventure session length'})).not.toBeInTheDocument();
    cleanup();
    render(<StudentDestination section="adventure" onOpen={vi.fn()} onCreate={vi.fn()} onSelect={vi.fn()}/>);
    expect(await screen.findByRole('group', {name:'Story Adventure session length'})).toBeInTheDocument();
  });

  it('shows Ready to Start for an untouched worksheet', async () => {
    const untouched = {id:90,date:'2026-09-05',completed_at:null,display_title:'Space Mission',answered:0,total:20,score:0,skipped:0,hints:0,xp_earned:0,elapsed_seconds:0,progress:0,restartable_skipped:false};
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([untouched]));
    render(<WorksheetHistory compact onCreate={vi.fn()} onOpen={vi.fn()}/>);
    expect(await screen.findByRole('article', {name:'Ready to start'})).toHaveTextContent('READY TO START');
    expect(screen.getByRole('button', {name:'Start'})).toBeInTheDocument();
    expect(screen.queryByText(/progress is saved/i)).not.toBeInTheDocument();
  });

  it('shows Continue Learning only after meaningful progress exists', async () => {
    const inProgress = {id: 90, date: '2026-09-05', completed_at: null, display_title: 'Space Mission', answered: 4, total: 20, score: 4, skipped: 1, hints: 1, xp_earned: 0, elapsed_seconds: 180, progress: 20, restartable_skipped: false};
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([completedRow(1), inProgress]));
    render(<WorksheetHistory compact onCreate={vi.fn()} onOpen={vi.fn()}/>);
    const continueRegion = await screen.findByRole('article', {name: 'Continue learning'});
    expect(continueRegion).toHaveTextContent('4 of 20 answered');
    expect(screen.getByRole('button', {name: 'Continue'})).toBeInTheDocument();
  });

  it('shows skipped-question recovery when there is no active worksheet', async () => {
    const recovery = {...completedRow(8, 'Fractions'), skipped: 2, restartable_skipped: true};
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response([recovery]));
    render(<WorksheetHistory compact onCreate={vi.fn()} onOpen={vi.fn()}/>);
    expect(await screen.findByRole('article', {name: 'Continue learning'})).toHaveTextContent('2 questions need another try');
  });

  it('uses learner-friendly weekly activity language', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({start:'2026-08-31',end:'2026-09-06',days:[{date:'2026-09-01',is_today:false,is_future:false,questions:8,correct:6,incorrect:2,hints:1,elapsed_seconds:300,worksheets:[]}]}));
    render(<LearningCalendar onOpen={vi.fn()}/>);
    expect(await screen.findByText('8 questions practised')).toBeInTheDocument();
    expect(screen.getByText('6 correct · 2 to revisit')).toBeInTheDocument();
  });

  it('provides an accessible in-page retry instead of a browser alert', () => {
    const retry = vi.fn();
    render(<ErrorNotice message="Try the request again" retry={retry}/>);
    fireEvent.click(screen.getByRole('button', {name: /Try again/i}));
    expect(retry).toHaveBeenCalledOnce();
  });
});
