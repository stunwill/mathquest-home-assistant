import './v0160.css';

const API='api';
const ACTIVE_KEY='mq_active_worksheet_id';
const priorFetch=window.fetch.bind(window);

function token(){return localStorage.getItem('token')}
function activeId(){const v=localStorage.getItem(ACTIVE_KEY);return v&&/^\d+$/.test(v)?Number(v):null}
function setActive(id:number|null){if(id)localStorage.setItem(ACTIVE_KEY,String(id));else localStorage.removeItem(ACTIVE_KEY)}

window.fetch=async(input:RequestInfo|URL,init?:RequestInit)=>{
  let target=String(input);
  const method=(init?.method||'GET').toUpperCase();
  const id=activeId();
  if(id&&method==='GET'&&(target.endsWith('api/worksheets/today')||target.endsWith('api/worksheets/active/latest'))){
    target=target.replace(/api\/worksheets\/(today|active\/latest)$/i,`api/worksheets/${id}/view`);
  }
  const response=await priorFetch(target,init);
  if(method==='POST'&&target.endsWith('api/worksheets/new')&&response.ok){
    try{const data=await response.clone().json();if(data?.id)setActive(Number(data.id))}catch{}
  }
  const complete=target.match(/api\/worksheets\/(\d+)\/complete$/);
  if(method==='POST'&&complete&&response.ok&&Number(complete[1])===activeId())setActive(null);
  return response;
};

async function api(path:string,opts:RequestInit={}){
  const t=token();
  const r=await fetch(API+path,{...opts,headers:{'Content-Type':'application/json',...(t?{Authorization:`Bearer ${t}`}:{}) ,...(opts.headers||{})}});
  const type=r.headers.get('content-type')||'';
  if(!r.ok)throw new Error(type.includes('json')?(await r.json().catch(()=>({detail:'Request failed'}))).detail:'Request failed');
  if(!type.includes('json'))throw new Error('MathQuest returned non-JSON content');
  return r.json();
}

function localDate(d=new Date()){const y=d.getFullYear(),m=String(d.getMonth()+1).padStart(2,'0'),day=String(d.getDate()).padStart(2,'0');return `${y}-${m}-${day}`}
function fromISO(s:string){const [y,m,d]=s.split('-').map(Number);return new Date(y,m-1,d)}
function addDays(d:Date,n:number){const x=new Date(d);x.setDate(x.getDate()+n);return x}
function monday(d=new Date()){const x=new Date(d);const day=(x.getDay()+6)%7;x.setDate(x.getDate()-day);x.setHours(0,0,0,0);return x}
function labelTopic(v:string){return (v||'mixed').replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
function mins(sec:number){const m=Math.round((sec||0)/60);return m?`${m} min`:'<1 min'}
function dateLabel(s:string){return fromISO(s).toLocaleDateString('en-AU',{weekday:'short',day:'numeric',month:'short'})}

function enhanceClock(){
  document.querySelectorAll('.clock-face').forEach((face:any)=>{
    if(face.dataset.v0160==='1')return;
    face.dataset.v0160='1';
    face.querySelectorAll('b').forEach((n:Element)=>n.remove());
    for(let h=1;h<=12;h++){
      const angle=h*30*Math.PI/180;
      const span=document.createElement('span');span.className='mq-clock-number';span.textContent=String(h);
      span.style.left=`${50+39*Math.sin(angle)}%`;span.style.top=`${50-39*Math.cos(angle)}%`;span.style.transform='translate(-50%,-50%)';face.append(span);
    }
    for(let i=0;i<60;i++){
      const tick=document.createElement('i');tick.className='mq-clock-tick'+(i%5===0?' major':'');tick.style.transform=`translateX(-50%) rotate(${i*6}deg)`;face.append(tick);
    }
  });
}

function reviewModal(data:any){
  document.querySelector('.mq-v0160-review')?.remove();
  const wrap=document.createElement('div');wrap.className='mq-v0160-review';
  wrap.innerHTML=`<section><button class="close">×</button><p class="eyebrow">WORKSHEET REVIEW</p><h2>${labelTopic(data.selected_topic)} · ${dateLabel(data.date)}</h2><p><strong>${data.score}/${data.total}</strong> · ${data.counts?.hints||0} hints</p>${(data.questions||[]).map((q:any)=>`<details><summary>${q.position+1}. ${q.prompt}</summary><p>Your answer: <strong>${q.student_answers?.map((a:any)=>a.answer).join(' → ')||'No answer'}</strong></p><p>Correct answer: <strong>${q.correct_answer}</strong></p><p>${q.working||''}</p></details>`).join('')}</section>`;
  wrap.querySelector('.close')?.addEventListener('click',()=>wrap.remove());wrap.addEventListener('click',e=>{if(e.target===wrap)wrap.remove()});document.body.append(wrap);
}
async function viewWorksheet(id:number){reviewModal(await api(`/worksheets/${id}/review`))}
function continueWorksheet(id:number){setActive(id);location.reload()}

let historyCache:any[]|null=null;
async function history():Promise<any[]>{if(historyCache===null)historyCache=await api('/worksheets/history-v0160');return historyCache||[]}

async function enhanceHistory(){
  const section=document.querySelector('.mq-v0120-history') as HTMLElement|null;
  if(!section||section.dataset.v0160==='1')return;
  const rows=await history();section.dataset.v0160='1';section.classList.add('mq-v0160-history');
  const today=rows.filter((w:any)=>w.date===localDate());
  const answered=today.reduce((n:number,w:any)=>n+(w.answered||0),0),correct=today.reduce((n:number,w:any)=>n+(w.score||0),0),hints=today.reduce((n:number,w:any)=>n+(w.hints||0),0),xp=today.reduce((n:number,w:any)=>n+(w.xp_earned||0),0),inProgress=today.filter((w:any)=>!w.completed_at).length;
  section.innerHTML=`<div class="mq-v0160-head"><div><p class="eyebrow">WORKSHEETS</p><h2>Your worksheet history</h2><p>${inProgress?`${inProgress} worksheet${inProgress===1?' is':'s are'} currently in progress.`:'No unfinished worksheet today.'}</p></div><button class="primary" data-new>+ New worksheet</button></div><div class="mq-v0160-summary"><article><small>Worksheets today</small><strong>${today.length}</strong></article><article><small>Questions</small><strong>${answered}</strong></article><article><small>Accuracy</small><strong>${answered?Math.round(correct/answered*100)+'%':'—'}</strong></article><article><small>Hints</small><strong>${hints}</strong></article><article><small>XP</small><strong>${xp}</strong></article></div><div class="mq-v0160-list">${rows.slice(0,20).map((w:any)=>`<article class="mq-v0160-row"><div class="meta"><b>${w.display_title}${w.display_time?` · ${w.display_time}`:''}</b><small>${dateLabel(w.date)} · ${w.answered}/${w.total} answered · ${w.hints} hints · ${mins(w.elapsed_seconds)}</small></div><span class="status">${w.completed_at?`Completed · ${w.score}/${w.total}`:`In progress · ${Math.round(w.progress)}%`}</span><button data-${w.completed_at?'view':'continue'}="${w.id}">${w.completed_at?'View worksheet':'Continue worksheet'}</button></article>`).join('')}</div>`;
  section.querySelectorAll('[data-continue]').forEach((b:any)=>b.addEventListener('click',()=>continueWorksheet(Number(b.dataset.continue))));
  section.querySelectorAll('[data-view]').forEach((b:any)=>b.addEventListener('click',()=>viewWorksheet(Number(b.dataset.view))));
}

async function enhanceHero(){
  const hero=document.querySelector('.hero');if(!hero||hero.querySelector('.mq-v0160-today'))return;
  const rows=await history();const today=rows.filter((w:any)=>w.date===localDate());const answered=today.reduce((n:number,w:any)=>n+(w.answered||0),0);const completed=today.filter((w:any)=>w.completed_at).length;const p=document.createElement('div');p.className='mq-v0160-today';p.textContent=`Today overall: ${answered} questions answered across ${today.length} worksheet${today.length===1?'':'s'} · ${completed} completed.`;hero.querySelector('div')?.append(p);
}

let rangeStart=monday();
async function renderCalendar(){
  const panels=[...document.querySelectorAll('.panel')];const target=panels.find(p=>p.querySelector('h2')?.textContent?.trim()==='Completion calendar') as HTMLElement|undefined;if(!target)return;
  target.classList.add('mq-v0160-calendar');
  const start=localDate(rangeStart);const data=await api(`/learning/week-v0160?start=${start}`);const currentMonday=monday();const canForward=rangeStart<currentMonday;
  target.innerHTML=`<div class="mq-cal-head"><button data-shift="-7">« 1 week</button><button data-shift="-1">‹ 1 day</button><h2>${dateLabel(data.start)} – ${dateLabel(data.end)}</h2><button data-shift="1" ${canForward?'':'disabled'}>1 day ›</button><button data-shift="7" ${canForward?'':'disabled'}>1 week »</button></div><div class="mq-cal-days">${data.days.map((d:any)=>{const any=d.worksheets.length>0,complete=any&&d.worksheets.every((w:any)=>!!w.completed_at),progress=any&&!complete;return `<article class="mq-cal-day${d.is_today?' today':''}${complete?' complete':''}${progress?' in-progress':''}${d.is_future?' future':''}"><h3>${dateLabel(d.date)}</h3><div class="mq-cal-stats">${d.questions?`<span>${d.questions} questions · ${d.accuracy??0}%</span><span>${d.correct} correct · ${d.incorrect} incorrect</span><span>💡 ${d.hints} · ⭐ ${d.xp} · ${mins(d.elapsed_seconds)}</span>`:'<span>No learning activity</span>'}</div><div class="mq-cal-ws">${d.worksheets.map((w:any)=>`<button data-${w.completed_at?'view':'continue'}="${w.id}">${w.display_title} · ${w.answered}/${w.total} ${w.completed_at?'✓':'→'}</button>`).join('')}</div></article>`}).join('')}</div>`;
  target.querySelectorAll('[data-shift]').forEach((b:any)=>b.addEventListener('click',()=>{const n=Number(b.dataset.shift);let next=addDays(rangeStart,n);if(next>currentMonday)next=currentMonday;rangeStart=next;void renderCalendar()}));
  target.querySelectorAll('[data-continue]').forEach((b:any)=>b.addEventListener('click',()=>continueWorksheet(Number(b.dataset.continue))));target.querySelectorAll('[data-view]').forEach((b:any)=>b.addEventListener('click',()=>viewWorksheet(Number(b.dataset.view))));
}

function updateVersion(){document.querySelectorAll('.header-version').forEach(n=>n.textContent='v0.16.0');document.querySelectorAll('.version').forEach(n=>n.textContent='Version 0.16.0')}
let scheduled=false;function run(){updateVersion();enhanceClock();if(token()){void enhanceHistory();void enhanceHero();void renderCalendar()}}
const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;run()})});observer.observe(document.documentElement,{childList:true,subtree:true});window.addEventListener('pageshow',run);run();
