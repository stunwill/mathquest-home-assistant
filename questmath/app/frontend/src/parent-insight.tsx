import React, {useState} from 'react';
import {Activity, Brain, Clock3, Copy, RefreshCw, Route, TrendingUp} from 'lucide-react';

import {apiRequest} from './api';

const value = (number: number | null | undefined, suffix = '') => number == null ? 'Not available' : `${number}${suffix}`;

export function ParentLearningInsight({data}: {data: any}) {
  if (!data) return null;
  const week = data.weekly?.current || {};
  const level = data.estimated_level || {};
  return <>
    <section className="panel parent-learning-insight">
      <div className="panel-heading">
        <div><p className="eyebrow">ADAPTIVE LEARNING INSIGHT</p><h2><Brain size={23}/> What the evidence shows</h2><p>{data.weekly?.narrative}</p></div>
        <div className="level-growth" aria-label="Estimated curriculum level">
          <small>Estimated level</small><strong>{value(level.current)}</strong>
          <span>{level.growth == null ? 'Complete another diagnostic to measure growth' : `${level.growth >= 0 ? '+' : ''}${level.growth} level growth from ${level.baseline}`}</span>
        </div>
      </div>
      <div className="insight-metrics">
        <article><TrendingUp/><small>Independent accuracy</small><strong>{value(week.independent_accuracy, '%')}</strong></article>
        <article><Activity/><small>Supported accuracy</small><strong>{value(week.supported_accuracy, '%')}</strong></article>
        <article><Clock3/><small>First-attempt time</small><strong>{value(week.average_seconds, 's')}</strong></article>
        <article><RefreshCw/><small>Reviews due</small><strong>{data.summary?.review_due || 0}</strong></article>
      </div>
      {data.recommendation&&<div className="parent-next-step"><Route/><div><small>RECOMMENDED NEXT SESSION</small><b>{data.recommendation.title}</b><p>{data.recommendation.reason}</p></div><strong>{data.recommendation.minutes} min</strong></div>}
      <div className="insight-columns">
        <div><h3>Recent gains</h3>{data.gains?.length ? data.gains.map((item:any)=><p key={item.code}><span>{item.title}</span><b>+{item.growth_points} points</b></p>) : <p>No comparable growth window yet.</p>}</div>
        <div><h3>Persistent gaps</h3>{data.persistent_gaps?.length ? data.persistent_gaps.map((item:any)=><p key={item.code}><span>{item.title}</span><b>{item.mastery}% mastery</b></p>) : <p>No persistent gaps currently identified.</p>}</div>
        <div><h3>Strategies practised</h3>{data.strategies_used?.length ? data.strategies_used.map((item:any)=><p key={item.strategy}><span>{item.strategy}</span><b>{item.questions}</b></p>) : <p>No strategy-card practice recorded this week.</p>}</div>
      </div>
    </section>
    <section className="panel outcome-insight"><h2>Outcome mastery and retention</h2><p>Independent accuracy excludes hinted answers. Supported accuracy includes questions completed after help.</p><div className="outcome-insight-table"><div className="outcome-insight-head"><b>Outcome</b><b>Independent</b><b>Supported</b><b>Mastery</b><b>Retention</b><b>Review</b></div>{data.outcomes.map((item:any)=><div className="outcome-insight-row" key={item.code}><span><b>{item.code}</b><small>{item.title}</small></span><span>{value(item.independent_accuracy, '%')}</span><span>{value(item.supported_accuracy, '%')}</span><span>{item.questions ? `${item.mastery}%` : 'Not assessed'}</span><span>{value(item.retention_accuracy, '%')}</span><span className={item.review_due?'review-due':''}>{item.review_due ? 'Due now' : item.questions ? item.next_review_due : 'Not scheduled'}</span></div>)}</div></section>
  </>;
}

export function HomeAssistantConnection() {
  const [details, setDetails] = useState<any>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  async function reveal() {
    setError('');
    try { setDetails(await apiRequest('/ha/service-token')); }
    catch (caught: any) { setError(caught.message); }
  }
  async function copy() {
    if (!details?.token) return;
    const header = details.authorization_header || `Bearer ${details.token}`;
    try { await navigator.clipboard.writeText(header); setMessage('Authorization value copied.'); }
    catch { setMessage('Select and copy the authorization value below.'); }
  }
  return <section className="panel ha-connection"><p className="eyebrow">HOME ASSISTANT CONNECTION</p><h2>Long-lived dashboard access</h2><p>This dedicated token does not expire after 24 hours and only authorises the MathQuest Home Assistant statistics endpoints.</p>
    {!details&&<button type="button" onClick={reveal}>Show Home Assistant token</button>}
    {error&&<p role="alert">{error}</p>}
    {details&&<><label>Authorization header value<input readOnly value={details.authorization_header || `Bearer ${details.token}`}/></label><button type="button" onClick={copy}><Copy size={17}/> Copy authorization value</button><small>Use <code>{details.stats_endpoint}</code> for complete metrics or <code>{details.summary_endpoint}</code> for headline sensors.</small>{message&&<span role="status">{message}</span>}</>}
  </section>;
}
