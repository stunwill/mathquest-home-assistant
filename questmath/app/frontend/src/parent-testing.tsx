import React, {useEffect, useState} from 'react';
import {apiRequest} from './api';
import {ErrorNotice} from './student-foundation';

const TOPICS = ['mixed', 'number_algebra', 'number', 'algebra', 'measurement', 'space', 'statistics', 'probability'];

function topicLabel(value: string) {
  return value.replaceAll('_', ' ').replace(/\b\w/g, letter => letter.toUpperCase());
}

export function TestQuestionFeedback({worksheetId, question}: {worksheetId: number; question: any}) {
  const [note, setNote] = useState('');
  const [feedbackType, setFeedbackType] = useState('note');
  const [saved, setSaved] = useState<any[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  async function save() {
    if (!note.trim()) return;
    setBusy(true); setError('');
    try {
      const item = await apiRequest(`/testing/worksheets/${worksheetId}/feedback`, {
        method: 'POST', body: JSON.stringify({question_id: question.id, feedback_type: feedbackType, note: note.trim()}),
      });
      setSaved(items => [...items, item]); setNote('');
    } catch (reason: any) { setError(reason.message); }
    finally { setBusy(false); }
  }
  return <section className="test-question-note" aria-label="Question test notes">
    <div><small>PARENT TEST NOTE</small><b>Record anything to fix or improve</b></div>
    {saved.map(item => <p className="saved-test-note" key={item.id}><strong>{topicLabel(item.feedback_type)}</strong> {item.note}</p>)}
    {error && <ErrorNotice message={error} dismiss={() => setError('')}/>}<label>Feedback type<select value={feedbackType} onChange={event => setFeedbackType(event.target.value)}><option value="bug">Bug</option><option value="enhancement">Enhancement</option><option value="note">General note</option></select></label>
    <label>Note<textarea value={note} onChange={event => setNote(event.target.value)} placeholder="What happened, what did you expect, or what would make this question better?"/></label>
    <button type="button" disabled={busy || !note.trim()} onClick={save}>{busy ? 'Saving…' : 'Save question note'}</button>
  </section>;
}

export function TestWorksheetResult({data, onDone}: {data: any; onDone: () => void}) {
  const [note, setNote] = useState('');
  const [feedbackType, setFeedbackType] = useState('note');
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  async function save() {
    setError('');
    try {
      await apiRequest(`/testing/worksheets/${data.worksheet_id}/feedback`, {
        method: 'POST', body: JSON.stringify({question_id: null, feedback_type: feedbackType, note: note.trim()}),
      });
      setSaved(true); setNote('');
    } catch (reason: any) { setError(reason.message); }
  }
  return <main className="result test-result"><section><div className="result-score">{data.score}/{data.total}</div><h1>Test worksheet complete</h1><p>This attempt did not change Sienna’s progress, mastery, XP or learning recommendations.</p>
    <div className="overall-test-note"><h2>Overall test notes</h2><p>Record feedback that relates to the worksheet as a whole.</p>{error && <ErrorNotice message={error} dismiss={() => setError('')}/>} {saved && <p className="mq-success-notice" role="status">Overall note saved.</p>}
      <label>Feedback type<select value={feedbackType} onChange={event => setFeedbackType(event.target.value)}><option value="bug">Bug</option><option value="enhancement">Enhancement</option><option value="note">General note</option></select></label>
      <label>Overall note<textarea value={note} onChange={event => setNote(event.target.value)} placeholder="Summarise the test, recurring problems or wider improvements."/></label>
      <button type="button" disabled={!note.trim()} onClick={save}>Save overall note</button>
    </div><button className="primary" onClick={onDone}>Return to parent dashboard</button></section></main>;
}

function FeedbackEditor({item, onSaved}: {item: any; onSaved: () => void}) {
  const [draft, setDraft] = useState(item);
  const [error, setError] = useState('');
  async function save() {
    setError('');
    try {
      await apiRequest(`/testing/feedback/${item.id}`, {
        method: 'PUT', body: JSON.stringify({
          feedback_type: draft.feedback_type, note: draft.note, status: draft.status,
          addressed_release: draft.status === 'addressed' ? draft.addressed_release : null,
        }),
      });
      onSaved();
    } catch (reason: any) { setError(reason.message); }
  }
  return <article className="test-feedback-editor">
    <div className="test-feedback-location"><b>{item.question_position ? `Question ${item.question_position}` : 'Overall worksheet'}</b><small>{item.question_prompt}</small></div>
    <div className="test-feedback-fields"><select aria-label="Feedback type" value={draft.feedback_type} onChange={event => setDraft({...draft, feedback_type: event.target.value})}><option value="bug">Bug</option><option value="enhancement">Enhancement</option><option value="note">Note</option></select><select aria-label="Feedback status" value={draft.status} onChange={event => setDraft({...draft, status: event.target.value, addressed_release: event.target.value === 'addressed' ? draft.addressed_release : ''})}><option value="open">Open</option><option value="planned">Planned</option><option value="addressed">Addressed</option><option value="deferred">Deferred</option></select>{draft.status === 'addressed' && <input aria-label="Addressed release" value={draft.addressed_release || ''} onChange={event => setDraft({...draft, addressed_release: event.target.value})} placeholder="0.25.0"/>}</div>
    <textarea aria-label="Feedback note" value={draft.note} onChange={event => setDraft({...draft, note: event.target.value})}/>{error && <ErrorNotice message={error} dismiss={() => setError('')}/>}<button type="button" onClick={save}>Save feedback</button>
  </article>;
}

export function ParentTestWorksheets({onOpen}: {onOpen: (worksheet: any) => void}) {
  const [items, setItems] = useState<any[]>([]);
  const [topic, setTopic] = useState('mixed');
  const [count, setCount] = useState(10);
  const [busy, setBusy] = useState(false);
  const [review, setReview] = useState<any>(null);
  const [error, setError] = useState('');
  const load = () => { setError(''); apiRequest<any[]>('/testing/worksheets').then(setItems).catch((reason: Error) => setError(reason.message)); };
  useEffect(load, []);
  async function create() {
    setBusy(true); setError('');
    try { onOpen(await apiRequest('/testing/worksheets', {method: 'POST', body: JSON.stringify({topic, question_count: count})})); }
    catch (reason: any) { setError(reason.message); }
    finally { setBusy(false); }
  }
  async function continueTest(item: any) {
    setError('');
    try {
      const detail: any = await apiRequest(`/testing/worksheets/${item.id}`);
      onOpen(detail.worksheet);
    } catch (reason: any) { setError(reason.message); }
  }
  async function openReview(item: any) {
    setError('');
    try { setReview(await apiRequest(`/testing/worksheets/${item.id}`)); }
    catch (reason: any) { setError(reason.message); }
  }
  async function reloadReview() {
    if (!review) return;
    setReview(await apiRequest(`/testing/worksheets/${review.id}`)); load();
  }
  return <section className="panel parent-test-worksheets"><div className="panel-heading"><div><p className="eyebrow">PARENT QUALITY TESTING</p><h2>Test worksheets and record feedback</h2><p>Run the same worksheet experience as Sienna, add notes after questions, and trace each bug or enhancement to the release that addressed it. Test activity is excluded from all learner evidence.</p></div><span className="test-isolation-badge">Does not affect learning data</span></div>
    {error && <ErrorNotice message={error} retry={load} dismiss={() => setError('')}/>}<div className="test-create-controls"><label>Learning area<select value={topic} onChange={event => setTopic(event.target.value)}>{TOPICS.map(value => <option value={value} key={value}>{topicLabel(value)}</option>)}</select></label><label>Questions<input type="number" min="5" max="50" value={count} onChange={event => setCount(Math.max(5, Math.min(50, Number(event.target.value))))}/></label><button type="button" className="primary" disabled={busy} onClick={create}>{busy ? 'Building test…' : 'Start test worksheet'}</button></div>
    <div className="test-worksheet-list">{items.length === 0 ? <p>No test worksheets yet.</p> : items.map(item => <article key={item.id}><div><b>{topicLabel(item.selected_topic)} test</b><small>{new Date(item.started_at).toLocaleString()} · {item.answered}/{item.total} answered · {item.feedback_count} notes</small></div><span className={`status-pill ${item.completed_at ? 'secure' : 'developing'}`}>{item.completed_at ? 'Completed' : 'In progress'}</span><span>{item.open_feedback} open · {item.addressed_feedback} addressed{item.addressed_releases.length ? ` · ${item.addressed_releases.join(', ')}` : ''}</span><div className="test-list-actions">{!item.completed_at&&<button type="button" onClick={() => continueTest(item)}>Continue test</button>}<button type="button" onClick={() => openReview(item)}>View test and notes</button></div></article>)}</div>
    {review && <div className="modal-backdrop"><section className="test-review-modal"><button className="close" aria-label="Close review" onClick={() => setReview(null)}>×</button><p className="eyebrow">TEST WORKSHEET REVIEW</p><h2>{topicLabel(review.selected_topic)} · {review.score}/{review.total}</h2><p>{review.feedback_count} notes · {review.open_feedback} open · {review.addressed_feedback} addressed</p><div className="test-question-review">{review.questions.map((question: any) => <details key={question.id}><summary>{question.position + 1}. {question.prompt}</summary><p>Test answers: <strong>{question.attempts.map((answer: any) => answer.answer).join(' → ') || 'Skipped'}</strong></p><p>Correct answer: <strong>{question.correct_answer}</strong></p><p>{question.working}</p></details>)}</div><h3>Feedback and release traceability</h3>{review.feedback.length ? review.feedback.map((item: any) => <FeedbackEditor item={item} onSaved={reloadReview} key={item.id}/>) : <p>No feedback was recorded for this test.</p>}</section></div>}
  </section>;
}
