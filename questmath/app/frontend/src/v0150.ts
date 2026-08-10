import './v080.css';

const API='api';
const token=()=>localStorage.getItem('token');
let loading=false;
let scheduled=false;
let lastQuestionId:number|null=null;

async function activeWorksheet(){
  const t=token();
  if(!t)return null;
  const r=await fetch(`${API}/worksheets/active/latest`,{headers:{Authorization:`Bearer ${t}`}});
  const type=r.headers.get('content-type')||'';
  if(!r.ok||!type.includes('json'))return null;
  return r.json();
}

function visualMarkup(v:any){
  if(!v)return'';
  if(v.type==='fraction_compare')return `<div class="mq-visual fraction-compare">${v.items.map((x:any)=>`<div><b>${x.label}</b><div class="fraction-bar">${Array.from({length:x.denominator},(_:unknown,i:number)=>`<span class="${i<x.numerator?'on':''}"></span>`).join('')}</div><small>${x.numerator}/${x.denominator}</small></div>`).join('')}</div>`;
  if(v.type==='number_line')return `<div class="mq-visual number-line"><div class="line-track">${Array.from({length:v.steps+1},(_:unknown,i:number)=>`<button type="button" data-visual-answer="${i}"><i></i><span>${i===0?'0':i===v.steps?'1':''}</span></button>`).join('')}</div></div>`;
  if(v.type==='clock'){
    const minute=Number(v.minute)||0;
    const hour=Number(v.hour)||0;
    const mh=minute*6;
    const hh=(hour%12)*30+minute*.5;
    return `<div class="mq-visual clock" role="img" aria-label="Analogue clock showing the time for this question"><div class="clock-face"><i class="hour" style="transform:rotate(${hh}deg)"></i><i class="minute" style="transform:rotate(${mh}deg)"></i><b>12</b><b>3</b><b>6</b><b>9</b></div></div>`;
  }
  if(v.type==='angle'){
    const degrees=Math.max(0,Math.min(180,Number(v.degrees)||0));
    const x=60+110*Math.cos(degrees*Math.PI/180);
    const y=120-110*Math.sin(degrees*Math.PI/180);
    const ax=60+30*Math.cos(degrees*Math.PI/180);
    const ay=120-30*Math.sin(degrees*Math.PI/180);
    return `<div class="mq-visual angle"><svg viewBox="0 0 240 150" role="img" aria-label="Angle diagram for this question"><line x1="60" y1="120" x2="195" y2="120"/><line x1="60" y1="120" x2="${x}" y2="${y}"/><path d="M90 120 A30 30 0 0 0 ${ax} ${ay}"/></svg></div>`;
  }
  if(v.type==='bar_chart'){
    const m=Math.max(...v.values);
    return `<div class="mq-visual bar-chart" role="img" aria-label="Bar chart for this question">${v.labels.map((x:string,i:number)=>`<div><span style="height:${Math.max(12,v.values[i]/m*120)}px"></span><b>${v.values[i]}</b><small>${x}</small></div>`).join('')}</div>`;
  }
  if(v.type==='grid')return `<div class="mq-visual grid-vis">${v.columns.map((c:string)=>Array.from({length:v.rows},(_:unknown,idx:number)=>{const r=idx+1,k=`${c}${r}`;return `<button type="button" data-visual-answer="${k}" class="${k===v.target?'target':''}"><small>${k}</small></button>`}).join('')).join('')}</div>`;
  return'';
}

function attachChoiceHandlers(holder:HTMLElement,card:Element){
  holder.querySelectorAll('[data-visual-answer]').forEach((el:any)=>el.addEventListener('click',()=>{
    const value=el.dataset.visualAnswer;
    const choices=Array.from(card.querySelectorAll('button.choice')) as HTMLButtonElement[];
    choices.find(b=>(b.textContent||'').trim()===value)?.click();
  }));
}

async function ensureRequiredVisual(){
  const card=document.querySelector('.question-card');
  if(!card||loading)return;
  loading=true;
  try{
    const ws=await activeWorksheet();
    if(!ws)return;
    (window as any).__mq_ws=ws;
    const q=ws.questions?.find((x:any)=>x.id===ws.current_question_id);
    if(!q)return;
    lastQuestionId=q.id;
    const v=q.payload?.visual;
    const existing=card.querySelector('.mq-v080-visual') as HTMLElement|null;
    if(v){
      if(existing?.dataset.qid===String(q.id))return;
      existing?.remove();
      const holder=document.createElement('div');
      holder.className='mq-v080-visual';
      holder.dataset.qid=String(q.id);
      holder.dataset.requiredVisual='true';
      holder.innerHTML=visualMarkup(v);
      const answer=card.querySelector('.answer');
      (answer||card.querySelector('h1'))?.insertAdjacentElement('beforebegin',holder);
      attachChoiceHandlers(holder,card);
      return;
    }
    existing?.remove();
    const prompt=String(q.prompt||'').toLowerCase();
    const inherentlyVisual=q.skill?.includes('visual_')||/shown|chart|grid|clock|angle|diagram|number line/.test(prompt);
    if(inherentlyVisual){
      const warning=document.createElement('div');
      warning.className='mq-v080-visual mq-visual';
      warning.dataset.qid=String(q.id);
      warning.innerHTML='<strong>Visual unavailable</strong><p>This question needs a diagram that is missing. Please skip this question for now.</p>';
      card.querySelector('h1')?.insertAdjacentElement('afterend',warning);
    }
  } finally { loading=false; }
}

function run(){
  const card=document.querySelector('.question-card');
  if(!card){lastQuestionId=null;return}
  const existing=card.querySelector('.mq-v080-visual') as HTMLElement|null;
  if(existing&&existing.dataset.qid===String(lastQuestionId))return;
  void ensureRequiredVisual();
}

const observer=new MutationObserver(()=>{
  if(scheduled)return;
  scheduled=true;
  requestAnimationFrame(()=>{scheduled=false;run()});
});
observer.observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('pagehide',(event:PageTransitionEvent)=>{if(!event.persisted)observer.disconnect()});
window.addEventListener('pageshow',run);
run();
