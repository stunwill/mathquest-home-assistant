import React, {useState} from 'react';
import {apiRequest} from './api';

export function QuestionTools({question, onOpenLab}: {question: any; onOpenLab: () => void}) {
  const [scratchOpen, setScratchOpen] = useState(false);
  const [scratch, setScratch] = useState('');
  const [scratchLoaded, setScratchLoaded] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  async function readAloud() {
    setError('');
    try {
      const data: any = await apiRequest(`/questions/${question.id}/read-aloud`);
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance([data.text, data.visual_description].filter(Boolean).join('. '));
        utterance.lang = 'en-AU'; utterance.rate = .92; window.speechSynthesis.speak(utterance);
      }
    } catch (reason: any) { setError(reason.message); }
  }
  async function toggleScratch() {
    setSaved(false); setError('');
    if (!scratchOpen && !scratchLoaded) {
      try { const data: any = await apiRequest(`/questions/${question.id}/scratchpad`); setScratch(data.content || ''); setScratchLoaded(true); }
      catch (reason: any) { setError(reason.message); return; }
    }
    setScratchOpen(value => !value);
  }
  async function saveScratch() {
    setError(''); setSaved(false);
    try { await apiRequest(`/questions/${question.id}/scratchpad`, {method: 'PUT', body: JSON.stringify({content: scratch})}); setSaved(true); }
    catch (reason: any) { setError(reason.message); }
  }
  return <div className="react-question-tools"><div><button type="button" onClick={readAloud}>🔊 Read aloud</button><button type="button" onClick={toggleScratch}>✏️ Scratchpad</button><button type="button" onClick={onOpenLab}>🧩 Maths tools</button></div>{error && <p role="alert">{error}</p>}{scratchOpen && <section className="react-scratchpad"><div><b>Scratchpad</b><small>Your working is saved for this question and does not affect your score.</small></div><textarea aria-label="Scratchpad working" value={scratch} onChange={event => { setScratch(event.target.value); setSaved(false); }} placeholder="Write your working here…"/><button type="button" onClick={saveScratch}>{saved ? 'Saved ✓' : 'Save working'}</button></section>}</div>;
}

export function ConfidenceCheck({questionId}: {questionId: number}) {
  const [saved, setSaved] = useState('');
  const [error, setError] = useState('');
  async function choose(confidence: string) {
    setError('');
    try { await apiRequest(`/questions/${questionId}/confidence`, {method: 'POST', body: JSON.stringify({confidence})}); setSaved(confidence); }
    catch (reason: any) { setError(reason.message); }
  }
  if (saved) return <div className="confidence-check saved"><b>Thanks!</b><span>Your confidence helps MathQuest choose the next intervention.</span></div>;
  return <div className="confidence-check"><b>How sure were you?</b><span>This helps separate secure understanding from a lucky answer.</span><div><button type="button" onClick={() => choose('guessed')}>😕 I guessed</button><button type="button" onClick={() => choose('pretty_sure')}>🙂 Pretty sure</button><button type="button" onClick={() => choose('knew_it')}>😎 I knew it</button></div>{error && <p role="alert">{error}</p>}</div>;
}
