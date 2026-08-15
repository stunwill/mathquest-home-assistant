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
  return <section className="panel intervention-card" aria-label="Number and Algebra intervention">
    <div className="intervention-copy"><p className="eyebrow">NUMBER &amp; ALGEBRA INTERVENTION</p><h2><Brain size={22}/> Build {String(data?.recommended_focus || 'efficient facts').replaceAll('_', ' ')}</h2><p>{data?.reason}</p>
      <div className="adaptive-signals"><span><Route size={16}/>{focus?.status?.replaceAll('_', ' ') || 'starting point'}</span>{focus?.independent_accuracy != null && <span>Independent {focus.independent_accuracy}%</span>}{focus?.supported_accuracy != null && <span>With support {focus.supported_accuracy}%</span>}</div>
    </div>
    <div className="intervention-start"><div role="group" aria-label="Intervention length">{([5, 10, 15] as const).map(value => <button type="button" className={minutes === value ? 'selected' : ''} onClick={() => setMinutes(value)} key={value}><Clock3 size={15}/>{value} min</button>)}</div><button type="button" className="primary" disabled={busy} onClick={start}><Play size={18}/>{busy ? 'Building intervention…' : `Start ${minutes}-minute intervention`}</button></div>
    {error && <p className="intervention-error" role="alert">{error}</p>}
  </section>;
}

export function InterventionGoal({question}: {question: any}) {
  const intervention = question?.payload?.intervention;
  if (!intervention) return null;
  return <div className="intervention-goal"><small>{String(intervention.phase).toUpperCase()} PHASE</small><b>{intervention.learning_goal}</b><span>Your independent result is recorded separately from work completed with support.</span></div>;
}
