import React, {useEffect, useMemo, useRef, useState} from 'react';
import {AlertCircle, BarChart3, BookOpen, Home, List, Play, RefreshCw, X} from 'lucide-react';
import {apiRequest, createSession, rememberActiveWorksheet} from './api';
import {QuestionVisual} from './question-visual';
import {StudentProgress} from './student-progress';
import './v0160.css';
import './v090.css';

type ErrorNoticeProps = {message: string; retry?: () => void; dismiss?: () => void};
type WorksheetSummary = {
  id: number; date: string; completed_at: string | null; display_title: string; display_time?: string;
  answered: number; total: number; score: number; skipped: number; hints: number; xp_earned: number;
  elapsed_seconds: number; progress: number; restartable_skipped: boolean;
};
export type StudentSection = 'home' | 'adventure' | 'worksheets' | 'progress';

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

export function StudentMobileNavigation({selected, onSelect}:{selected:StudentSection; onSelect:(section:StudentSection)=>void}) {
  return <nav className="student-mobile-nav" aria-label="Student navigation">
    <button type="button" aria-current={selected === 'home' ? 'page' : undefined} onClick={() => onSelect('home')}><Home size={20}/><span>Home</span></button>
    <button type="button" aria-current={selected === 'adventure' ? 'page' : undefined} onClick={() => onSelect('adventure')}><BookOpen size={20}/><span>Adventure</span></button>
    <button type="button" aria-current={selected === 'worksheets' ? 'page' : undefined} onClick={() => onSelect('worksheets')}><List size={20}/><span>Worksheets</span></button>
    <button type="button" aria-current={selected === 'progress' ? 'page' : undefined} onClick={() => onSelect('progress')}><BarChart3 size={20}/><span>Progress</span></button>
  </nav>;
}

export function WorksheetHistory({onCreate, onOpen, compact = false}:{onCreate: () => void; onOpen: (worksheet: any) => void; compact?: boolean}) {
  const [rows, setRows] = useState<WorksheetSummary[] | null>(null);
  const [error, setError] = useState('');
  const [review, setReview] = useState<any>(null);
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

  const orderedRows = useMemo(() => [...(rows || [])].sort((a,b) => Number(Boolean(a.completed_at)) - Number(Boolean(b.completed_at))), [rows]);
  const incomplete = orderedRows.find(row => !row.completed_at);
  const skippedRecovery = !incomplete ? orderedRows.find(row => row.restartable_skipped && row.skipped > 0) : undefined;
  const continuation = incomplete || skippedRecovery;
  const historyRows = continuation ? orderedRows.filter(row => row.id !== continuation.id) : orderedRows;
  const visibleRows = compact ? historyRows.slice(0, 1) : historyRows.slice(0, 20);
  const isUntouched = !!incomplete && incomplete.answered === 0 && incomplete.progress <= 0;

  return <section id="mq-worksheet-history" className={`panel mq-v0160-history${continuation ? ' mq-has-continue' : ''}${compact ? ' mq-history-compact' : ''}`} aria-label="Worksheet history">
    {continuation && <article className="mq-continue-learning" aria-label={isUntouched ? 'Ready to start' : 'Continue learning'}><div><p className="eyebrow">{isUntouched ? 'READY TO START' : 'CONTINUE LEARNING'}</p><h2>{incomplete ? continuation.display_title : `${continuation.skipped} questions need another try`}</h2><p>{incomplete ? (isUntouched ? 'Your worksheet is ready when you are.' : `${continuation.answered} of ${continuation.total} answered. Your progress is saved.`) : 'Finish the skipped questions when you are ready.'}</p></div><button type="button" className="primary" onClick={() => incomplete ? open(continuation.id) : restart(continuation.id)}><Play size={18}/>{incomplete ? (isUntouched ? 'Start' : 'Continue') : 'Finish worksheet'}</button></article>}
    {!compact && <div id="mq-worksheet-history-secondary" className="mq-history-secondary">
      <div className="mq-v0160-head"><div><p className="eyebrow">WORKSHEETS</p><h2>Your worksheets</h2><p>Resume recent work or revisit completed practice.</p></div><button className="primary" type="button" onClick={onCreate}>+ New worksheet</button></div>
      {error && <ErrorNotice message={error} retry={load} dismiss={() => setError('')}/>} {rows === null && !error ? <p>Loading worksheet history…</p> : <div className="mq-v0160-list">{visibleRows.map(row => <article className="mq-v0160-row" key={row.id}><div className="meta"><b>{row.display_title}{row.display_time ? ` · ${row.display_time}` : ''}</b><small>{dateLabel(row.date)} · {row.answered}/{row.total} answered · {row.skipped || 0} skipped · {minutes(row.elapsed_seconds)}</small></div><span className="status">{row.completed_at ? `Completed · ${row.score}/${row.total}` : row.answered === 0 ? 'Ready to start' : `In progress · ${Math.round(row.progress)}%`}</span><div className="mq-v0160-row-actions"><button type="button" onClick={() => row.completed_at ? view(row.id) : open(row.id)}>{row.completed_at ? 'Review' : row.answered === 0 ? 'Start' : 'Continue'}</button>{row.restartable_skipped && <button type="button" onClick={() => restart(row.id)}>Finish {row.skipped} skipped</button>}</div></article>)}</div>}
    </div>}
    {compact && !continuation && visibleRows.length > 0 && <div className="mq-home-recent"><p className="eyebrow">RECENT LEARNING</p><b>{visibleRows[0].display_title}</b><span>{visibleRows[0].completed_at ? 'Completed' : 'In progress'}</span></div>}
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

  return <section id="mq-learning-calendar" className="panel completion-calendar mq-v0160-calendar"><div className="mq-cal-head"><button type="button" aria-label="Previous week" onClick={() => shift(-7)}>‹ Week</button><button className="day-shift" type="button" onClick={() => shift(-1)}>‹ 1 day</button><h2>{data ? `${dateLabel(data.start)} – ${dateLabel(data.end)}` : 'This week'}</h2><button className="day-shift" type="button" disabled={rangeStart >= currentMonday} onClick={() => shift(1)}>1 day ›</button><button type="button" aria-label="Next week" disabled={rangeStart >= currentMonday} onClick={() => shift(7)}>Week ›</button><button className="mq-cal-today" type="button" disabled={rangeStart >= currentMonday} onClick={goToday}>Today</button></div>
    {error && <ErrorNotice message={error} retry={load}/>} {!data && !error ? <p>Loading learning activity…</p> : <div className="mq-cal-days">{data?.days.map((day: any) => { const any = day.worksheets.length > 0; const complete = any && day.worksheets.every((worksheet: any) => worksheet.completed_at); return <article key={day.date} className={`mq-cal-day${day.is_today ? ' today' : ''}${complete ? ' complete' : ''}${any && !complete ? ' in-progress' : ''}${day.is_future ? ' future' : ''}`}><h3>{dateLabel(day.date)}</h3><div className="mq-cal-stats">{day.questions ? <><span>{day.questions} questions practised</span><span>{day.correct} correct · {day.incorrect} to revisit</span><span>💡 {day.hints} hints · {minutes(day.elapsed_seconds)}</span></> : <span>No learning activity</span>}</div><div className="mq-cal-ws">{day.worksheets.map((worksheet: any) => <button type="button" key={worksheet.id} onClick={() => open(worksheet.id)} aria-label={`${worksheet.display_title}, ${worksheet.completed_at ? 'completed' : 'in progress'}`}>{worksheet.display_title} · {worksheet.answered}/{worksheet.total} {worksheet.completed_at ? '✓' : '→'}</button>)}</div></article>; })}</div>}
  </section>;
}

export function StoryAdventures({onOpen, compact = false, onExplore}:{onOpen: (worksheet: any) => void; compact?: boolean; onExplore?:()=>void}) {
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

  if (compact) {
    const item = items?.[0];
    return <section className="panel mq-adventure-preview" aria-label="Adventure preview"><p className="eyebrow">ADVENTURE</p><h2><BookOpen size={22}/> Learn through a mission</h2><p>{item ? `${item.icon} ${item.title} is ready, with maths chosen by your adaptive learning plan.` : 'Choose a Story Adventure when you want your maths practice to feel like a mission.'}</p>{onExplore && <button type="button" onClick={onExplore}>Explore adventures →</button>}</section>;
  }

  return <section id="mq-story-adventures" className="panel mq-v090-adventures mq-v0340-adventures">
    <div className="mq-adventure-heading"><div><p className="eyebrow">STORY ADVENTURE</p><h2><BookOpen size={22}/> Learn through a mission</h2><p>The same adaptive learning engine chooses the maths. Story Adventure changes how the session feels, not what MathQuest decides you should learn.</p></div><div className="mq-adventure-duration" role="group" aria-label="Story Adventure session length">{([5,10,15] as const).map(value=><button type="button" key={value} aria-pressed={minutes===value} className={minutes===value?'selected':''} onClick={()=>setMinutes(value)}>{value} min</button>)}</div></div>
    {error && <ErrorNotice message={error} retry={load} dismiss={() => setError('')}/>}<div className="mq-adventure-grid">{items === null && !error ? <p>Loading adventures…</p> : items?.length === 0 ? <p>No Story Adventures are available right now.</p> : items?.map(item => <button type="button" data-theme={item.id} key={item.id} disabled={!!busy} onClick={() => start(item.id)}><span>{item.icon}</span><b>{item.title}</b><small>{busy === item.id ? 'Building your adaptive mission…' : item.intro}</small><em>{item.objective}</em><i>Practises: {(item.recommended_goals || item.topics || []).slice(0, 2).join(' + ')}</i>{busy === item.id && <Play size={16}/>}</button>)}</div>
  </section>;
}

export function StudentDestination({section,onOpen,onCreate,onSelect}:{section:StudentSection;onOpen:(worksheet:any)=>void;onCreate:()=>void;onSelect:(section:StudentSection)=>void}) {
  if (section === 'adventure') return <StoryAdventures onOpen={onOpen}/>;
  if (section === 'worksheets') return <WorksheetHistory onCreate={onCreate} onOpen={onOpen}/>;
  if (section === 'progress') return <><StudentProgress/><LearningCalendar onOpen={onOpen}/></>;
  return <StoryAdventures compact onOpen={onOpen} onExplore={()=>onSelect('adventure')}/>;
}
