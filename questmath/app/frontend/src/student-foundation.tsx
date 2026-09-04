import React, {useEffect, useMemo, useRef, useState} from 'react';
import {AlertCircle, BookOpen, Play, RefreshCw, X} from 'lucide-react';
import {apiRequest, createSession, rememberActiveWorksheet} from './api';
import {QuestionVisual} from './question-visual';
import './v0160.css';
import './v090.css';

type ErrorNoticeProps = {message: string; retry?: () => void; dismiss?: () => void};
type WorksheetSummary = {
  id: number; date: string; completed_at: string | null; display_title: string; display_time?: string;
  answered: number; total: number; score: number; skipped: number; hints: number; xp_earned: number;
  elapsed_seconds: number; progress: number; restartable_skipped: boolean;
};

export function ErrorNotice({message, retry, dismiss}: ErrorNoticeProps) {
  return <div className="mq-error-notice" role="alert">
    <AlertCircle size={22}/><div><b>Something went wrong</b><p>{message}</p></div>
    {retry && <button type="button" onClick={retry}><RefreshCw size={16}/> Try again</button>}
    {dismiss && <button type="button" className="icon-button" aria-label="Dismiss error" onClick={dismiss}><X size={18}/></button>}
  </div>;
}

function localDate(date = new Date()) {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
}
function fromISO(value: string) { const [y, m, d] = value.split('-').map(Number); return new Date(y, m - 1, d); }
function addDays(date: Date, days: number) { const next = new Date(date); next.setDate(next.getDate() + days); return next; }
function monday(date = new Date()) { const value = new Date(date); value.setDate(value.getDate() - ((value.getDay() + 6) % 7)); value.setHours(0, 0, 0, 0); return value; }
function dateLabel(value: string) { return fromISO(value).toLocaleDateString('en-AU', {weekday: 'short', day: 'numeric', month: 'short'}); }
function minutes(seconds: number) { const value = Math.round((seconds || 0) / 60); return value ? `${value} min` : '<1 min'; }

export function WorksheetHistory({onCreate, onOpen, homeLimit}:{onCreate: () => void; onOpen: (worksheet: any) => void; homeLimit?: number}) {
  const [rows, setRows] = useState<WorksheetSummary[] | null>(null);
  const [error, setError] = useState('');
  const [review, setReview] = useState<any>(null);
  const [showAll, setShowAll] = useState(false);
  const reviewOpener = useRef<HTMLElement|null>(null);
  const load = () => { setError(''); apiRequest<WorksheetSummary[]>('/worksheets/history-v0160').then(setRows).catch((e: Error) => setError(e.message)); };
  useEffect(load, []);

  async function open(id: number) {
    setError('');
    try {
      const worksheet = await apiRequest(`/worksheets/${id}/view`);
      rememberActiveWorksheet(id);
      onOpen(worksheet);
    } catch (e: any) { setError(e.message); }
  }
  async function restart(id: number) {
    setError('');
    try {
      const worksheet: any = await apiRequest(`/worksheets/${id}/restart-skipped`, {method: 'POST'});
      rememberActiveWorksheet(worksheet.id);
      onOpen(worksheet);
    } catch (e: any) { setError(e.message); }
  }
  async function view(id: number) {
    setError('');
    reviewOpener.current = document.activeElement as HTMLElement|null;
    try { setReview(await apiRequest(`/worksheets/${id}/review`)); }
    catch (e: any) { setError(e.message); }
  }
  function closeReview() { setReview(null); setTimeout(() => reviewOpener.current?.focus(), 0); }
  useEffect(() => {
    if (!review) return;
    const keydown = (event: KeyboardEvent) => { if (event.key === 'Escape') closeReview(); };
    window.addEventListener('keydown', keydown);
    return () => window.removeEventListener('keydown', keydown);
  }, [review]);

  const today = (rows || []).filter(row => row.date === localDate());
  const totals = useMemo(() => ({
    answered: today.reduce((sum, row) => sum + row.answered, 0),
    score: today.reduce((sum, row) => sum + row.score, 0),
    hints: today.reduce((sum, row) => sum + row.hints, 0),
    xp: today.reduce((sum, row) => sum + row.xp_earned, 0),
  }), [rows]);
  const orderedRows = useMemo(() => [...(rows || [])].sort((a,b) => Number(Boolean(a.completed_at)) - Number(Boolean(b.completed_at))), [rows]);
  const visibleRows = homeLimit && !showAll ? orderedRows.slice(0, homeLimit) : orderedRows.slice(0, 20);

  return <section className="panel mq-v0160-history" aria-label="Worksheet history">
    <div className="mq-v0160-head"><div><p className="eyebrow">WORKSHEETS</p><h2>{homeLimit?'Recent worksheets':'Your worksheet history'}</h2><p>{today.filter(row => !row.completed_at).length || 'No'} worksheet{today.filter(row => !row.completed_at).length === 1 ? ' is' : 's are'} currently in progress.</p></div><button className="primary" type="button" onClick={onCreate}>+ New worksheet</button></div>
    {error && <ErrorNotice message={error} retry={load} dismiss={() => setError('')}/>} {rows === null && !error ? <p>Loading worksheet history…</p> : <>
      {!homeLimit&&<div className="mq-v0160-summary"><article><small>Worksheets today</small><strong>{today.length}</strong></article><article><small>Questions</small><strong>{totals.answered}</strong></article><article><small>Accuracy</small><strong>{totals.answered ? `${Math.round(totals.score / totals.answered * 100)}%` : '—'}</strong></article><article><small>Hints</small><strong>{totals.hints}</strong></article><article><small>XP</small><strong>{totals.xp}</strong></article></div>}
      <div className="mq-v0160-list">{visibleRows.map(row => <article className="mq-v0160-row" key={row.id}><div className="meta"><b>{row.display_title}{row.display_time ? ` · ${row.display_time}` : ''}</b><small>{dateLabel(row.date)} · {row.answered}/{row.total} answered · {row.skipped || 0} skipped · {row.hints} hints · {minutes(row.elapsed_seconds)}</small></div><span className="status">{row.completed_at ? `Completed · ${row.score}/${row.total}` : `In progress · ${Math.round(row.progress)}%`}</span><div className="mq-v0160-row-actions"><button type="button" onClick={() => row.completed_at ? view(row.id) : open(row.id)}>{row.completed_at ? 'Review' : 'Continue'}</button>{row.restartable_skipped && <button type="button" onClick={() => restart(row.id)}>Finish {row.skipped} skipped</button>}</div></article>)}</div>
      {homeLimit&&orderedRows.length>homeLimit&&<button className="student-compact-link" type="button" aria-expanded={showAll} onClick={()=>setShowAll(!showAll)}>{showAll?'Show recent only':'View all worksheets →'}</button>}
    </>}
    {review && <div className="mq-v0160-review" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) closeReview(); }}><section role="dialog" aria-modal="true" aria-labelledby="worksheet-review-title"><button className="close" type="button" aria-label="Close review" onClick={closeReview}>×</button><p className="eyebrow">WORKSHEET REVIEW</p><h2 id="worksheet-review-title">{review.selected_topic?.replaceAll('_', ' ')} · {dateLabel(review.date)}</h2><p><strong>{review.score}/{review.total}</strong> · {review.counts?.hints || 0} hints</p>{review.questions?.map((question: any) => <details key={question.id}><summary>{question.position + 1}. {question.prompt}</summary><div className="question-card review-question-visual"><QuestionVisual question={question}/></div><p>Your answer: <strong>{question.student_answers?.map((answer: any) => answer.answer).join(' → ') || 'No answer'}</strong></p><p>Correct answer: <strong>{question.correct_answer}</strong></p><p>{question.working}</p></details>)}</section></div>}
  </section>;
}

export function LearningCalendar({onOpen}:{onOpen: (worksheet: any) => void}) {
  const [rangeStart, setRangeStart] = useState(monday());
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');
  const start = localDate(rangeStart);
  const load = () => { setError(''); setData(null); apiRequest(`/learning/week-v0160?start=${start}`).then(setData).catch((e: Error) => setError(e.message)); };
  useEffect(load, [start]);
  const currentMonday = monday();
  const shift = (days: number) => { const next = addDays(rangeStart, days); setRangeStart(next > currentMonday ? currentMonday : next); };
  const goToday = () => setRangeStart(currentMonday);
  const open = async (id: number) => { try { const worksheet = await apiRequest(`/worksheets/${id}/view`); rememberActiveWorksheet(id); onOpen(worksheet); } catch (e: any) { setError(e.message); } };

  return <section className="panel completion-calendar mq-v0160-calendar"><div className="mq-cal-head"><button type="button" aria-label="Previous week" onClick={() => shift(-7)}>‹ Week</button><button className="day-shift" type="button" onClick={() => shift(-1)}>‹ 1 day</button><h2>{data ? `${dateLabel(data.start)} – ${dateLabel(data.end)}` : 'This week'}</h2><button className="day-shift" type="button" disabled={rangeStart >= currentMonday} onClick={() => shift(1)}>1 day ›</button><button type="button" aria-label="Next week" disabled={rangeStart >= currentMonday} onClick={() => shift(7)}>Week ›</button><button className="mq-cal-today" type="button" disabled={rangeStart >= currentMonday} onClick={goToday}>Today</button></div>
    {error && <ErrorNotice message={error} retry={load}/>} {!data && !error ? <p>Loading learning activity…</p> : <div className="mq-cal-days">{data?.days.map((day: any) => { const any = day.worksheets.length > 0; const complete = any && day.worksheets.every((worksheet: any) => worksheet.completed_at); return <article key={day.date} className={`mq-cal-day${day.is_today ? ' today' : ''}${complete ? ' complete' : ''}${any && !complete ? ' in-progress' : ''}${day.is_future ? ' future' : ''}`}><h3>{dateLabel(day.date)}</h3><div className="mq-cal-stats">{day.questions ? <><span>{day.questions} questions · {day.accuracy ?? 0}%</span><span>{day.correct} correct · {day.incorrect} incorrect</span><span>💡 {day.hints} · ⭐ {day.xp} · {minutes(day.elapsed_seconds)}</span></> : <span>No learning activity</span>}</div><div className="mq-cal-ws">{day.worksheets.map((worksheet: any) => <button type="button" key={worksheet.id} onClick={() => open(worksheet.id)}>{worksheet.display_title} · {worksheet.answered}/{worksheet.total} {worksheet.completed_at ? '✓' : '→'}</button>)}</div></article>; })}</div>}
  </section>;
}

export function StoryAdventures({onOpen}:{onOpen: (worksheet: any) => void}) {
  const [items, setItems] = useState<any[] | null>(null);
  const [busy, setBusy] = useState('');
  const [minutes, setMinutes] = useState<5|10|15>(10);
  const [error, setError] = useState('');
  const load = () => { setError(''); apiRequest<any[]>('/adventures-v0340').then(setItems).catch((e: Error) => setError(e.message)); };
  useEffect(load, []);

  async function start(theme: string) {
    setBusy(theme); setError('');
    try {
      const worksheet: any = await createSession('practice', minutes, 'mixed');
      await apiRequest(`/worksheets/${worksheet.id}/adventure-v0340`, {method: 'POST', body: JSON.stringify({theme})});
      rememberActiveWorksheet(worksheet.id);
      onOpen(await apiRequest(`/worksheets/${worksheet.id}/view`));
    } catch (e: any) { setError(e.message); }
    finally { setBusy(''); }
  }

  if (items?.length === 0) return null;
  return <section className="panel mq-v090-adventures mq-v0340-adventures">
    <div className="mq-adventure-heading"><div><p className="eyebrow">STORY ADVENTURE</p><h2><BookOpen size={22}/> Learn through a mission</h2><p>The same adaptive learning engine chooses the maths. Story Adventure changes how the session feels, not what MathQuest decides you should learn.</p></div><div className="mq-adventure-duration" role="group" aria-label="Story Adventure session length">{([5,10,15] as const).map(value=><button type="button" key={value} aria-pressed={minutes===value} className={minutes===value?'selected':''} onClick={()=>setMinutes(value)}>{value} min</button>)}</div></div>
    {error && <ErrorNotice message={error} retry={load} dismiss={() => setError('')}/>}<div className="mq-adventure-grid">{items === null && !error ? <p>Loading adventures…</p> : items?.map(item => <button type="button" data-theme={item.id} key={item.id} disabled={!!busy} onClick={() => start(item.id)}><span>{item.icon}</span><b>{item.title}</b><small>{busy === item.id ? 'Building your adaptive mission…' : item.intro}</small><em>{item.objective}</em><i>Likely focus: {(item.recommended_goals || item.topics || []).slice(0, 2).join(' + ')}</i>{busy === item.id && <Play size={16}/>}</button>)}</div>
  </section>;
}
