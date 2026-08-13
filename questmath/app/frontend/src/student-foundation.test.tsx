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

describe('v0.18 worksheet foundation', () => {
  it('creates every worksheet through the single new-worksheet endpoint and remembers it', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(() => response({id: 42, selected_topic: 'number'}));
    await createWorksheet('number');
    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0][0]).toBe('api/worksheets/new');
    expect(fetchMock.mock.calls[0][1]).toMatchObject({method: 'POST', body: JSON.stringify({topic: 'number'})});
    expect(localStorage.getItem('mq_active_worksheet_id')).toBe('42');
  });

  it('starts a story through React without reloading the page', async () => {
    const onOpen = vi.fn();
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation((input) => {
      const url = String(input);
      if (url === 'api/adventures') return response([{id: 'space', icon: '🚀', title: 'Space Mission', intro: 'Launch'}]);
      if (url === 'api/worksheets/new') return response({id: 9});
      if (url === 'api/worksheets/9/adventure') return response({theme: 'space'});
      if (url === 'api/worksheets/9/view') return response({id: 9, selected_topic: 'Space Mission'});
      return response({detail: 'missing'}, false, 404);
    });
    render(<StoryAdventures onOpen={onOpen}/>);
    fireEvent.click(await screen.findByRole('button', {name: /Space Mission/i}));
    await waitFor(() => expect(onOpen).toHaveBeenCalledWith({id: 9, selected_topic: 'Space Mission'}));
    expect(fetchMock.mock.calls.map(call => String(call[0]))).toEqual([
      'api/adventures', 'api/worksheets/new', 'api/worksheets/9/adventure', 'api/worksheets/9/view',
    ]);
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
});
