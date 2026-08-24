import React, {useEffect, useState} from 'react';
import {apiRequest} from './api';
import {speakText} from './speech';

export function QuestionTools({question, onOpenLab}: {question: any; onOpenLab: () => void}) {
  const [scratchOpen, setScratchOpen] = useState(false);
  const [scratch, setScratch] = useState('');
  const [scratchLoaded, setScratchLoaded] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [strategyIndex, setStrategyIndex] = useState(0);
  const strategies = Array.isArray(question?.payload?.solution_strategies) ? question.payload.solution_strategies : [];
  const visual = question?.payload?.visual_mathematics;
  const strategy = strategies[strategyIndex % Math.max(1, strategies.length)];

  useEffect(() => { setStrategyIndex(0); }, [question?.id]);

  async function readAloud() {
    setError('');
    try {
      const data: any = await apiRequest(`/questions/${question.id}/read-aloud`);
      const result = speakText([data.text, data.visual_description].filter(Boolean).join('. '), data.lang || 'en-AU');
      if (!result.supported) setError(result.message);
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
  function anotherWay() {
    if (!strategies.length) return;
    setStrategyIndex(value => (value + 1) % strategies.length);
  }
  return <div className="react-question-tools">
    <div><button type="button" onClick={readAloud}>🔊 Read aloud</button><button type="button" onClick={toggleScratch}>✏️ Scratchpad</button><button type="button" onClick={onOpenLab}>🧩 Maths tools</button>{strategies.length > 1 && <button type="button" onClick={anotherWay}>↻ Show another way</button>}</div>
    {visual?.teaching_visual_available && <aside className="visual-recommendation" aria-label="Visual mathematics recommendation"><b>Visual idea</b><p>{visual.visual_reason}</p><button type="button" onClick={onOpenLab}>Try the {String(visual.recommended_model || 'visual').replaceAll('-', ' ')} model</button></aside>}
    {strategy && strategyIndex > 0 && <aside className="strategy-alternative" role="status" aria-live="polite"><b>{strategy.title}</b><p>{strategy.explanation}</p><small>Try this strategy without changing your current answer.</small></aside>}
    {error && <p role="alert">{error}</p>}
    {scratchOpen && <section className="react-scratchpad"><div><b>Scratchpad</b><small>Your working is saved for this question and does not affect your score.</small></div><textarea aria-label="Scratchpad working" value={scratch} onChange={event => { setScratch(event.target.value); setSaved(false); }} placeholder="Write your working here…"/><button type="button" onClick={saveScratch}>{saved ? 'Saved ✓' : 'Save working'}</button></section>}
  </div>;
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
