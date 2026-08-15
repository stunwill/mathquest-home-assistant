import React from 'react';

function FractionComparison({items}: {items: any[]}) {
  return <div className="mq-visual fraction-compare" role="group" aria-label="Fraction comparison using equal-sized wholes">
    {(items || []).map((item, row) => { const numerator = Math.max(0, Number(item.numerator) || 0), denominator = Math.max(1, Number(item.denominator) || 1); return <div className="fraction-row" key={`${row}-${numerator}-${denominator}`}><b>{item.label}</b><div className="fraction-bar" role="img" aria-label={`${numerator} of ${denominator} equal parts shaded`}>{Array.from({length: denominator}, (_, index) => <span className={index < numerator ? 'on' : ''} key={index}/>)}</div><small>{numerator}/{denominator}</small></div>; })}
  </div>;
}

function GridReference({visual}: {visual: any}) {
  const rows: string[] = Array.isArray(visual?.columns) ? visual.columns.map(String) : [];
  const columnCount = Math.max(1, Number(visual?.rows) || 1);
  const columns = Array.from({length: columnCount}, (_, index) => index + 1);
  const target = String(visual?.target || '');
  return <div className="mq-visual grid-reference-visual" role="group" aria-label="Grid reference diagram with labelled rows and columns"><div className="grid-vis" style={{'--mq-grid-columns': columnCount} as React.CSSProperties}><span className="grid-corner"/>{columns.map(column => <span className="grid-axis grid-column-label" key={`column-${column}`}>{column}</span>)}{rows.flatMap(row => [<span className="grid-axis grid-row-label" key={`${row}-label`}>{row}</span>, ...columns.map(column => { const reference = `${row}${column}`; return <span className={`grid-cell ${reference === target ? 'target' : ''}`} aria-label={reference === target ? 'Highlighted square' : undefined} aria-hidden={reference === target ? undefined : true} key={reference}/>; })])}</div></div>;
}

function Clock({visual}: {visual: any}) {
  const minute = Number(visual.minute) || 0, hour = Number(visual.hour) || 0;
  return <div className="mq-visual clock" role="img" aria-label="Analogue clock for this question"><div className="clock-face"><i className="hour" style={{transform: `rotate(${(hour % 12) * 30 + minute * .5}deg)`}}/><i className="minute" style={{transform: `rotate(${minute * 6}deg)`}}/><b>12</b><b>3</b><b>6</b><b>9</b></div></div>;
}

function Angle({visual}: {visual: any}) {
  const degrees = Math.max(0, Math.min(180, Number(visual.degrees) || 0));
  const x = 60 + 110 * Math.cos(degrees * Math.PI / 180), y = 120 - 110 * Math.sin(degrees * Math.PI / 180);
  const ax = 60 + 30 * Math.cos(degrees * Math.PI / 180), ay = 120 - 30 * Math.sin(degrees * Math.PI / 180);
  return <div className="mq-visual angle"><svg viewBox="0 0 240 150" role="img" aria-label="Angle diagram for this question"><line x1="60" y1="120" x2="195" y2="120"/><line x1="60" y1="120" x2={x} y2={y}/><path d={`M90 120 A30 30 0 0 0 ${ax} ${ay}`}/></svg></div>;
}

function BarChart({visual}: {visual: any}) {
  const values = Array.isArray(visual.values) ? visual.values.map(Number) : [];
  const maximum = Math.max(1, ...values);
  return <div className="mq-visual bar-chart" role="img" aria-label="Bar chart for this question">{(visual.labels || []).map((label: string, index: number) => <div key={`${label}-${index}`}><span style={{height: `${Math.max(12, values[index] / maximum * 120)}px`}}/><b>{values[index]}</b><small>{label}</small></div>)}</div>;
}

function NumberLine({visual}: {visual: any}) {
  const steps = Math.max(1, Number(visual.steps) || 1);
  return <div className="mq-visual number-line" role="img" aria-label="Number line for this question"><div className="line-track">{Array.from({length: steps + 1}, (_, index) => <span key={index}><i/><b>{index === 0 ? '0' : index === steps ? '1' : ''}</b></span>)}</div></div>;
}

export function QuestionVisual({question}: {question: any}) {
  const visual = question?.payload?.visual;
  if (!visual) return null;
  const key = question?.payload?.visual_key || question?.id;
  if (visual.type === 'fraction_compare') return <FractionComparison key={key} items={visual.items}/>;
  if (visual.type === 'grid') return <GridReference key={key} visual={visual}/>;
  if (visual.type === 'clock') return <Clock key={key} visual={visual}/>;
  if (visual.type === 'angle') return <Angle key={key} visual={visual}/>;
  if (visual.type === 'bar_chart') return <BarChart key={key} visual={visual}/>;
  if (visual.type === 'number_line') return <NumberLine key={key} visual={visual}/>;
  return <div className="mq-visual visual-unavailable" role="status"><b>Visual unavailable</b><p>Skip this question and ask a parent to add a test note.</p></div>;
}
