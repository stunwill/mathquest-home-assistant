import React from 'react';

export type FractionValue={numerator:number;denominator:number;label?:string};

function clampFraction(value:FractionValue):FractionValue{
  const denominator=Math.max(1,Math.min(24,Number(value.denominator)||1));
  const numerator=Math.max(0,Math.min(denominator*3,Number(value.numerator)||0));
  return {...value,numerator,denominator};
}

export function FractionModel({value,interactive=false,onChange}:{value:FractionValue;interactive?:boolean;onChange?:(value:FractionValue)=>void}){
  const item=clampFraction(value),whole=Math.floor(item.numerator/item.denominator),remainder=item.numerator%item.denominator;
  const wholes=Array.from({length:Math.max(1,whole+(remainder?1:0))});
  const update=(next:Partial<FractionValue>)=>onChange?.(clampFraction({...item,...next}));
  return <div className="vm-fraction-model">
    {interactive&&<div className="vm-fraction-inputs"><label>Numerator<input aria-label={`${item.label||'Fraction'} numerator`} type="number" min="0" max={item.denominator*3} value={item.numerator} onChange={e=>update({numerator:+e.target.value})}/></label><label>Denominator<input aria-label={`${item.label||'Fraction'} denominator`} type="number" min="1" max="24" value={item.denominator} onChange={e=>update({denominator:+e.target.value,numerator:Math.min(item.numerator,+e.target.value*3)})}/></label></div>}
    <div className="vm-fraction-wholes" role="img" aria-label={`${item.numerator} over ${item.denominator}, shown as equal-sized fraction bars`}>
      {wholes.map((_,wholeIndex)=>{const shaded=Math.max(0,Math.min(item.denominator,item.numerator-wholeIndex*item.denominator));return <div className="vm-fraction-bar" key={wholeIndex}>{Array.from({length:item.denominator},(_,index)=><span className={index<shaded?'on':''} key={index}/>)}</div>})}
    </div>
    <output aria-live="polite">{item.numerator}/{item.denominator}</output>
  </div>;
}

export function FractionComparison({items,interactive=false,onChange}:{items:FractionValue[];interactive?:boolean;onChange?:(items:FractionValue[])=>void}){
  const safe=(items||[]).slice(0,2).map(clampFraction);
  const change=(index:number,value:FractionValue)=>onChange?.(safe.map((item,i)=>i===index?value:item));
  return <div className="vm-fraction-comparison" role="group" aria-label="Fraction comparison using equal-sized wholes">
    {safe.map((item,index)=><div className="vm-fraction-row" key={index}><b>{item.label||`Fraction ${index+1}`}</b><FractionModel value={item} interactive={interactive} onChange={value=>change(index,value)}/></div>)}
  </div>;
}

export function FractionNumberLine({values,onChange}:{values:FractionValue[];onChange?:(index:number,value:FractionValue)=>void}){
  return <div className="vm-fraction-number-line" role="group" aria-label="Fractions positioned on a number line from zero to one">
    <div className="vm-number-line-track"><span>0</span><i/><span>1</span>{values.slice(0,2).map((value,index)=>{const item=clampFraction(value),position=Math.max(0,Math.min(100,item.numerator/item.denominator*100));return <button type="button" key={index} className="vm-number-line-marker" style={{left:`${position}%`}} aria-label={`${item.label||`Fraction ${index+1}`} is at ${item.numerator} over ${item.denominator}`} onClick={()=>onChange?.(index,item)}>{index+1}</button>})}</div>
  </div>;
}

export function EquivalentFractionModel({value}:{value:FractionValue}){
  const item=clampFraction(value),factor=2,equivalent={numerator:item.numerator*factor,denominator:item.denominator*factor};
  return <div className="vm-equivalent" role="group" aria-label={`${item.numerator} over ${item.denominator} is equivalent to ${equivalent.numerator} over ${equivalent.denominator}`}><FractionModel value={{...item,label:'Original'}}/><span aria-hidden="true">=</span><FractionModel value={{...equivalent,label:'Equivalent'}}/></div>;
}

export function NumberLineModel({min=0,max=100,value=30,onChange}:{min?:number;max?:number;value?:number;onChange?:(value:number)=>void}){
  const safeMax=Math.max(min+1,max),safe=Math.max(min,Math.min(safeMax,value));
  return <div className="vm-number-line" role="group" aria-label={`Number line from ${min} to ${safeMax}`}><input aria-label="Number line position" type="range" min={min} max={safeMax} value={safe} onChange={e=>onChange?.(+e.target.value)}/><div><b>{min}</b><output>{safe}</output><b>{safeMax}</b></div></div>;
}

export function ArrayModel({rows,columns}:{rows:number;columns:number}){
  const r=Math.max(1,Math.min(12,rows)),c=Math.max(1,Math.min(12,columns));
  return <div className="vm-array-wrap"><div className="vm-array" style={{gridTemplateColumns:`repeat(${c},1fr)`}} role="img" aria-label={`${r} equal rows with ${c} in each row`}>{Array.from({length:r*c},(_,index)=><i key={index}/>)}</div><output>{r} rows × {c} in each row = {r*c} counters</output></div>;
}

export function PlaceValueModel({value}:{value:number}){
  const safe=Math.max(0,Math.min(9999,Math.floor(value))),digits=String(safe).padStart(4,'0').split('');
  return <div className="vm-place-value" role="group" aria-label={`Place value representation of ${safe}`}>{['Thousands','Hundreds','Tens','Ones'].map((label,index)=><div key={label}><small>{label}</small><strong>{digits[index]}</strong><span>{Array.from({length:+digits[index]},(_,i)=><i key={i}/>)}</span></div>)}</div>;
}

export function MeasurementModel({length,width,unit='cm'}:{length:number;width:number;unit?:string}){
  const l=Math.max(1,length),w=Math.max(1,width);
  return <div className="vm-measurement" role="img" aria-label={`Rectangle ${l} ${unit} by ${w} ${unit}`}><div style={{aspectRatio:`${l}/${w}`}}><span>{l} {unit}</span><b>{w} {unit}</b></div></div>;
}
