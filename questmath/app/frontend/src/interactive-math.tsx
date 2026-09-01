import React from 'react';

type Setter=(value:string)=>void;

export function FractionBarAnswer({q,value,setValue}:{q:any;value:string;setValue:Setter}){
  const visual=q?.payload?.visual||{};
  const denominator=Math.max(1,Number(visual.denominator)||1);
  const selected=Math.max(0,Math.min(denominator,Number(value)||0));
  return <div className="interactive-fraction-bar" role="group" aria-label={`Fraction bar split into ${denominator} equal parts`}>
    <div className="interactive-fraction-segments">{Array.from({length:denominator},(_,index)=>{
      const on=index<selected;
      return <button key={index} type="button" aria-label={`Select ${index+1} of ${denominator} equal parts`} aria-pressed={on} className={on?'selected':''} onClick={()=>setValue(String(index+1))}><span aria-hidden="true"/></button>;
    })}</div>
    <p>{selected?`${selected} of ${denominator} parts selected`:'Select the equal parts that make the fraction.'}</p>
  </div>;
}

export function FractionNumberLineAnswer({q,value,setValue}:{q:any;value:string;setValue:Setter}){
  const visual=q?.payload?.visual||{};
  const denominator=Math.max(1,Number(visual.denominator)||1);
  const selected=Number(value);
  const labels=new Set<number>(Array.isArray(visual.label_indices)?visual.label_indices.map(Number):[0,denominator]);
  return <div className="interactive-fraction-line" role="group" aria-label={`Fraction number line from zero to one split into ${denominator} equal intervals`}>
    <div className="interactive-fraction-line-track">{Array.from({length:denominator+1},(_,index)=>{
      const labelled=labels.has(index);
      const label=index===0?'0':index===denominator?'1':'';
      const aria=labelled&&label?`Tick ${label}`:`Unlabelled fraction tick ${index+1}`;
      return <button key={index} type="button" aria-label={aria} aria-pressed={selected===index} className={selected===index?'selected':''} onClick={()=>setValue(String(index))}><i/><span>{label}</span></button>;
    })}</div>
    <p>Use the equal intervals between 0 and 1.</p>
  </div>;
}

export function RulerAnswer({q,value,setValue}:{q:any;value:string;setValue:Setter}){
  const visual=q?.payload?.visual||{};
  const steps=Math.max(1,Number(visual.steps)||1);
  const interval=Math.max(1,Number(visual.interval)||1);
  const unit=String(visual.unit||'cm');
  const selected=Number(value);
  const labels=new Set<number>(Array.isArray(visual.label_indices)?visual.label_indices.map(Number):[0,steps]);
  return <div className="interactive-ruler" role="group" aria-label={`Ruler with ${steps} equal intervals of ${interval} ${unit}`}>
    <div className="interactive-ruler-track">{Array.from({length:steps+1},(_,index)=>{
      const amount=index*interval;
      const labelled=labels.has(index);
      return <button key={index} type="button" aria-label={labelled?`${amount} ${unit}`:`Unlabelled ruler mark ${index+1}`} aria-pressed={selected===amount} className={selected===amount?'selected':''} onClick={()=>setValue(String(amount))}><i/><span>{labelled?amount:''}</span></button>;
    })}</div>
    <p>Each mark is equally spaced. Work out the scale before choosing a mark.</p>
  </div>;
}

export function GridSelectAnswer({q,value,setValue}:{q:any;value:string;setValue:Setter}){
  const visual=q?.payload?.visual||{};
  const columns:string[]=Array.isArray(visual.columns)?visual.columns.map(String):['A','B','C','D','E'];
  const rows=Math.max(1,Number(visual.rows)||5);
  return <div className="interactive-grid-select" role="group" aria-label="Selectable coordinate grid">
    <div className="interactive-grid-table" style={{'--mq-select-grid-columns':columns.length} as React.CSSProperties}>
      <span className="grid-select-corner"/>{columns.map(column=><b key={`column-${column}`}>{column}</b>)}
      {Array.from({length:rows},(_,rowIndex)=>{const row=rowIndex+1;return <React.Fragment key={row}><b>{row}</b>{columns.map(column=>{const reference=`${column}${row}`;return <button key={reference} type="button" aria-label={`Square ${reference}`} aria-pressed={value===reference} className={value===reference?'selected':''} onClick={()=>setValue(reference)}><span aria-hidden="true"/></button>})}</React.Fragment>})}
    </div>
    <p>Read the column letter first, then the row number.</p>
  </div>;
}
