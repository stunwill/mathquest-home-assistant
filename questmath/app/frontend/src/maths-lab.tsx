import React, {useMemo, useState} from 'react';
import {RotateCcw, X} from 'lucide-react';
import './maths-lab.css';

export type LabTool = 'fractions'|'percentages'|'number-line'|'place-value'|'arrays'|'clock'|'grid'|'measurement';

const TOOLS:{id:LabTool;label:string;icon:string}[]=[
  {id:'fractions',label:'Fractions',icon:'◒'},
  {id:'percentages',label:'Percentages',icon:'%'},
  {id:'number-line',label:'Number line',icon:'↔'},
  {id:'place-value',label:'Place value',icon:'123'},
  {id:'arrays',label:'Arrays',icon:'⠿'},
  {id:'clock',label:'Clock',icon:'◷'},
  {id:'grid',label:'Grid',icon:'▦'},
  {id:'measurement',label:'Measurement',icon:'⌇'},
];

export function recommendedLabTool(question:any):LabTool{
  const skill=String(question?.skill||'').toLowerCase(),topic=String(question?.topic||'').toLowerCase(),prompt=String(question?.prompt||'').toLowerCase();
  if(skill.includes('fraction'))return'fractions';
  if(skill.includes('percent'))return'percentages';
  if(skill.includes('clock')||skill.includes('duration')||prompt.includes('time'))return'clock';
  if(skill.includes('grid')||skill.includes('coordinate')||topic==='space')return'grid';
  if(skill.includes('place')||skill.includes('written_'))return'place-value';
  if(skill.includes('multiplication')||skill.includes('division')||skill.includes('fact_recall'))return'arrays';
  if(topic==='measurement')return'measurement';
  return'number-line';
}

export function MathsLab({question,onClose}:{question:any;onClose:()=>void}){
  const suggested=useMemo(()=>recommendedLabTool(question),[question]);
  const[tool,setTool]=useState<LabTool>(suggested);
  const[resetKey,setResetKey]=useState(0);
  return <div className="lab-backdrop" role="presentation" onMouseDown={event=>{if(event.target===event.currentTarget)onClose()}}>
    <section className="maths-lab" role="dialog" aria-modal="true" aria-labelledby="maths-lab-title">
      <header className="lab-header"><div><small>INTERACTIVE MATHS LAB</small><h2 id="maths-lab-title">Build it, move it, explain it</h2><p>Use a model to test your thinking. The lab does not submit an answer.</p></div><button type="button" aria-label="Close maths lab" onClick={onClose}><X/></button></header>
      <div className="lab-layout"><nav className="lab-tabs" aria-label="Maths lab tools">{TOOLS.map(item=><button type="button" key={item.id} className={tool===item.id?'selected':''} aria-pressed={tool===item.id} onClick={()=>{setTool(item.id);setResetKey(value=>value+1)}}><span>{item.icon}</span>{item.label}{item.id===suggested&&<small>Suggested</small>}</button>)}</nav>
        <div className="lab-workspace"><div className="lab-workspace-head"><div><small>CURRENT MODEL</small><b>{TOOLS.find(item=>item.id===tool)?.label}</b></div><button type="button" onClick={()=>setResetKey(value=>value+1)}><RotateCcw size={17}/> Start over</button></div><LabModel key={`${tool}-${resetKey}`} tool={tool}/></div>
      </div>
    </section>
  </div>;
}

function LabModel({tool}:{tool:LabTool}){
  if(tool==='fractions')return <FractionLab/>;
  if(tool==='percentages')return <PercentageLab/>;
  if(tool==='number-line')return <NumberLineLab/>;
  if(tool==='place-value')return <PlaceValueLab/>;
  if(tool==='arrays')return <ArrayLab/>;
  if(tool==='clock')return <ClockLab/>;
  if(tool==='grid')return <GridLab/>;
  return <MeasurementLab/>;
}

function FractionBar({numerator,denominator}:{numerator:number;denominator:number}){return <div className="lab-fraction-bar" role="img" aria-label={`${numerator} of ${denominator} equal parts shaded`}>{Array.from({length:denominator},(_,index)=><i className={index<numerator?'on':''} key={index}/>)}</div>}
function FractionLab(){const[d1,setD1]=useState(4),[n1,setN1]=useState(3),[d2,setD2]=useState(3),[n2,setN2]=useState(2);const updateD1=(value:number)=>{setD1(value);setN1(Math.min(n1,value))},updateD2=(value:number)=>{setD2(value);setN2(Math.min(n2,value))};return <div className="lab-model"><p>Keep both wholes the same width, then compare the shaded amount.</p><div className="lab-fraction-controls"><label>First numerator<input aria-label="First numerator" type="number" min="0" max={d1} value={n1} onChange={e=>setN1(Math.max(0,Math.min(d1,+e.target.value)))}/></label><label>First denominator<input aria-label="First denominator" type="number" min="1" max="12" value={d1} onChange={e=>updateD1(Math.max(1,Math.min(12,+e.target.value)))}/></label></div><div className="lab-fraction-row"><b>{n1}/{d1}</b><FractionBar numerator={n1} denominator={d1}/></div><div className="lab-fraction-controls"><label>Second numerator<input aria-label="Second numerator" type="number" min="0" max={d2} value={n2} onChange={e=>setN2(Math.max(0,Math.min(d2,+e.target.value)))}/></label><label>Second denominator<input aria-label="Second denominator" type="number" min="1" max="12" value={d2} onChange={e=>updateD2(Math.max(1,Math.min(12,+e.target.value)))}/></label></div><div className="lab-fraction-row"><b>{n2}/{d2}</b><FractionBar numerator={n2} denominator={d2}/></div><output>{n1/d1===n2/d2?'The shaded amounts are equal.':n1/d1>n2/d2?'The first shaded amount is larger.':'The second shaded amount is larger.'}</output></div>}

function PercentageLab(){const[value,setValue]=useState(25),[quantity,setQuantity]=useState(100);const divisor=gcd(value,100);return <div className="lab-model"><p>Move the percentage and watch every representation change together.</p><label>Percentage: <b>{value}%</b><input aria-label="Percentage" type="range" min="0" max="100" step="1" value={value} onChange={e=>setValue(+e.target.value)}/></label><div className="lab-percent-bar" aria-label={`${value} percent shaded`}><i style={{width:`${value}%`}}/></div><div className="lab-linked-values"><span><small>Fraction</small><b>{value/divisor}/{100/divisor}</b></span><span><small>Decimal</small><b>{(value/100).toFixed(2)}</b></span><span><small>Of quantity</small><b>{format(value/100*quantity)}</b></span></div><label>Whole quantity<input aria-label="Whole quantity" type="number" min="1" max="1000" value={quantity} onChange={e=>setQuantity(Math.max(1,+e.target.value))}/></label></div>}

function NumberLineLab(){const[min,setMin]=useState(0),[max,setMax]=useState(100),[value,setValue]=useState(30);const bounded=Math.max(min,Math.min(max,value));return <div className="lab-model"><p>Move the marker or make jumps. Explain the size and direction of each jump.</p><div className="lab-range-inputs"><label>Start<input aria-label="Number line start" type="number" value={min} onChange={e=>{const next=+e.target.value;setMin(next);if(value<next)setValue(next)}}/></label><label>End<input aria-label="Number line end" type="number" value={max} onChange={e=>{const next=Math.max(min+1,+e.target.value);setMax(next);if(value>next)setValue(next)}}/></label></div><div className="lab-number-line"><input aria-label="Number line marker" type="range" min={min} max={max} value={bounded} onChange={e=>setValue(+e.target.value)}/><div><b>{min}</b><output>{bounded}</output><b>{max}</b></div></div><div className="lab-jumps">{[-10,-1,1,10].map(jump=><button type="button" key={jump} onClick={()=>setValue(Math.max(min,Math.min(max,bounded+jump)))}>{jump>0?'+':''}{jump}</button>)}</div></div>}

function PlaceValueLab(){const[value,setValue]=useState(243),digits=String(Math.max(0,Math.min(9999,value))).padStart(4,'0').split('');return <div className="lab-model"><p>Change the number, then inspect how many thousands, hundreds, tens and ones it contains.</p><label>Number<input aria-label="Place value number" type="number" min="0" max="9999" value={value} onChange={e=>setValue(Math.max(0,Math.min(9999,+e.target.value)))}/></label><div className="lab-place-columns">{['thousands','hundreds','tens','ones'].map((place,index)=><div key={place}><small>{place}</small><strong>{digits[index]}</strong><span>{Array.from({length:+digits[index]},(_,i)=><i key={i}/>)}</span></div>)}</div><div className="lab-jumps"><button type="button" onClick={()=>setValue(Math.max(0,value-10))}>− 1 ten</button><button type="button" onClick={()=>setValue(Math.min(9999,value+10))}>+ 1 ten</button><button type="button" onClick={()=>setValue(Math.max(0,value-100))}>− 1 hundred</button><button type="button" onClick={()=>setValue(Math.min(9999,value+100))}>+ 1 hundred</button></div></div>}

function ArrayLab(){const[rows,setRows]=useState(3),[columns,setColumns]=useState(4);return <div className="lab-model"><p>Build equal rows and columns to model multiplication or division.</p><div className="lab-range-inputs"><label>Rows<input aria-label="Array rows" type="number" min="1" max="12" value={rows} onChange={e=>setRows(Math.max(1,Math.min(12,+e.target.value)))}/></label><label>Columns<input aria-label="Array columns" type="number" min="1" max="12" value={columns} onChange={e=>setColumns(Math.max(1,Math.min(12,+e.target.value)))}/></label></div><div className="lab-array" style={{gridTemplateColumns:`repeat(${columns},1fr)`}} aria-label={`${rows} rows of ${columns} counters`}>{Array.from({length:rows*columns},(_,i)=><i key={i}/>)}</div><output>{rows} rows × {columns} in each row = {rows*columns} counters</output></div>}

function ClockLab(){const[hour,setHour]=useState(3),[minute,setMinute]=useState(20),minuteAngle=minute*6,hourAngle=(hour%12)*30+minute*.5;return <div className="lab-model"><p>Move each hand using the controls and connect the analogue and digital times.</p><div className="lab-clock"><b className="n12">12</b><b className="n3">3</b><b className="n6">6</b><b className="n9">9</b><i className="hour" style={{transform:`rotate(${hourAngle}deg)`}}/><i className="minute" style={{transform:`rotate(${minuteAngle}deg)`}}/><span/></div><output>{hour}:{String(minute).padStart(2,'0')}</output><label>Hour<input aria-label="Clock hour" type="range" min="1" max="12" value={hour} onChange={e=>setHour(+e.target.value)}/></label><label>Minutes<input aria-label="Clock minutes" type="range" min="0" max="55" step="5" value={minute} onChange={e=>setMinute(+e.target.value)}/></label></div>}

function GridLab(){const[selected,setSelected]=useState('B3'),rows=['A','B','C','D'],columns=[1,2,3,4];return <div className="lab-model"><p>Select a square. Read the row letter first, then the column number.</p><div className="lab-grid" style={{gridTemplateColumns:`auto repeat(${columns.length},1fr)`}}><span/>{columns.map(column=><b key={column}>{column}</b>)}{rows.flatMap(row=>[<b key={`${row}-label`}>{row}</b>,...columns.map(column=>{const reference=`${row}${column}`;return <button aria-label={`Grid square ${reference}`} type="button" className={selected===reference?'selected':''} key={reference} onClick={()=>setSelected(reference)}/>})])}</div><output>Selected reference: {selected}</output></div>}

function MeasurementLab(){const[length,setLength]=useState(8),[width,setWidth]=useState(3),[angle,setAngle]=useState(60);const x=50+100*Math.cos(angle*Math.PI/180),y=125-100*Math.sin(angle*Math.PI/180);return <div className="lab-model"><p>Adjust the dimensions or angle, then describe what changes and what stays the same.</p><div className="lab-range-inputs"><label>Length (cm)<input aria-label="Rectangle length" type="number" min="1" max="20" value={length} onChange={e=>setLength(Math.max(1,Math.min(20,+e.target.value)))}/></label><label>Width (cm)<input aria-label="Rectangle width" type="number" min="1" max="20" value={width} onChange={e=>setWidth(Math.max(1,Math.min(20,+e.target.value)))}/></label></div><div className="lab-ruler"><div>{Array.from({length:21},(_,index)=><span key={index}><i/>{index}</span>)}</div><input aria-label="Ruler marker" type="range" min="1" max="20" value={length} onChange={e=>setLength(+e.target.value)}/></div><div className="lab-rectangle" style={{aspectRatio:`${length}/${width}`}}><span>{length} cm</span><b>{width} cm</b></div><div className="lab-linked-values"><span><small>Perimeter</small><b>{2*(length+width)} cm</b></span><span><small>Area</small><b>{length*width} cm²</b></span><span><small>Ruler marker</small><b>{length} cm</b></span></div><label>Angle: <b>{angle}°</b><input aria-label="Angle" type="range" min="0" max="180" value={angle} onChange={e=>setAngle(+e.target.value)}/></label><svg className="lab-angle" viewBox="0 0 180 150" aria-label={`${angle} degree angle`}><line x1="50" y1="125" x2="160" y2="125"/><line x1="50" y1="125" x2={x} y2={y}/></svg></div>}

function gcd(a:number,b:number):number{return b?gcd(b,a%b):Math.max(1,a)}
function format(value:number){return Number.isInteger(value)?String(value):value.toFixed(2)}
