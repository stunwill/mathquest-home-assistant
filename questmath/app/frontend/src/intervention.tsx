import React, {useEffect, useState} from 'react';
import {Brain, Clock3, Play, Route} from 'lucide-react';
import {apiRequest, createIntervention} from './api';

type Focus = {
  focus: string;
  questions: number;
  independent_accuracy: number | null;
  supported_accuracy: number | null;
  support_gap: number | null;
  status: string;
};

function learnerStatus(status?: string) {
  if (!status) return 'Starting point';
  if (status === 'needs_support') return 'A little extra practice will help';
  if (status === 'developing') return 'Building confidence';
  if (status === 'secure') return 'Getting stronger';
  return 'Practice focus';
}

export function InterventionCard({onOpen}: {onOpen: (worksheet: any) => void}) {
  const [data, setData] = useState<any>(null);
  const [minutes, setMinutes] = useState<5 | 10 | 15>(10);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    apiRequest('/learning/intervention-v0260').then(setData).catch((reason: Error) => setError(reason.message));
  }, []);
  if (!data && !error) return null;
  const focus: Focus | undefined = data?.focuses?.find((item: Focus) => item.focus === data.recommended_focus);
  async function start() {
    setBusy(true); setError('');
    try { onOpen(await createIntervention(minutes)); }
    catch (reason: any) { setError(reason.message); }
    finally { setBusy(false); }
  }
  const focusName = String(data?.recommended_focus || 'efficient facts').replaceAll('_', ' ');
  return <section className="panel intervention-card" aria-label="Extra practice">
    <div className="intervention-copy"><p className="eyebrow">EXTRA PRACTICE</p><h2><Brain size={22}/> Build your {focusName} confidence</h2><p>A little extra practice here can help you solve these more confidently on your own.</p>
      <div className="adaptive-signals"><span><Route size={16}/>{learnerStatus(focus?.status)}</span></div>
    </div>
    <div className="intervention-start"><div role="group" aria-label="Practice length">{([5, 10, 15] as const).map(value => <button type="button" className={minutes === value ? 'selected' : ''} onClick={() => setMinutes(value)} key={value}><Clock3 size={15}/>{value} min</button>)}</div><button type="button" className="primary" disabled={busy} onClick={start}><Play size={18}/>{busy ? 'Building your practice…' : `Start ${minutes}-minute practice`}</button></div>
    {error && <p className="intervention-error" role="alert">{error}</p>}
  </section>;
}

export function InterventionGoal({question}: {question: any}) {
  const intervention = question?.payload?.intervention;
  if (!intervention) return null;
  return <div className="intervention-goal"><small>{String(intervention.phase).toUpperCase()} PHASE</small><b>{intervention.learning_goal}</b><span>MathQuest keeps track of when you solve a question on your own and when support helps.</span></div>;
}
