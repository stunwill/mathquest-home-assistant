import './v0120.css';

const API='api';
const nativeFetch=window.fetch.bind(window);

window.fetch=async(input:RequestInfo|URL,init?:RequestInit)=>{
  let target=String(input);
  const method=(init?.method||'GET').toUpperCase();
  if(target.endsWith('api/dashboard/parent')) target=target.replace(/api\/dashboard\/parent$/,'api/dashboard/parent-v0120');
  if(target.endsWith('api/reports/weekly')) target=target.replace(/api\/reports\/weekly$/,'api/reports/weekly-v0120');
  if(target.endsWith('api/worksheets/today')) target=target.replace(/api\/worksheets\/today$/,method==='POST'?'api/worksheets/new':'api/worksheets/active/latest');
  return nativeFetch(target,init);
};

const token=()=>localStorage.getItem('token');
async function api(path:string,opts:RequestInit={}){
  const r=await fetch(API+path,{...opts,headers:{'Content-Type':'application/json',...(token()?{Authorization:`Bearer ${token()}`}:{}) ,...(opts.headers||{})}});
  const type=r.headers.get('content-type')||'';
  if(!r.ok){const detail=type.includes('json')?(await r.json().catch(()=>({detail:'Request failed'}))).detail:`Request failed (${r.status})`;throw new Error(detail||'Request failed')}
  if(!type.includes('json'))throw new Error(`MathQuest API ${path} returned ${type||'non-JSON content'} instead of JSON`);
  return r.json();
}
const label=(t:string)=>t==='mixed'?'Mixed Adventure':t==='number_algebra'?'Number & Algebra Focus':t.charAt(0).toUpperCase()+t.slice(1);
const dateLabel=(s:string)=>new Date(`${s}T00:00:00`).toLocaleDateString('en-AU',{day:'numeric',month:'short',year:'numeric'});

function modal(html:string){document.querySelector('.mq-v0120-modal')?.remove();const wrap=document.createElement('div');wrap.className='mq-v0120-modal';wrap.innerHTML=`<section>${html}</section>`;wrap.addEventListener('click',e=>{if(e.target===wrap)wrap.remove()});document.body.append(wrap);return wrap}

async function chooseNew(){const m=modal(`<button class="mq-close">×</button><p class="eyebrow">ANOTHER QUEST</p><h2>Choose your next worksheet</h2><p>There is no one-worksheet-per-day limit. Each worksheet is saved separately and all of today's work contributes to progress.</p><div class="mq-v0120-topics">${['number_algebra','measurement','algebra','probability','number','space','statistics','mixed'].map(t=>`<button data-topic="${t}">${label(t)}</button>`).join('')}</div>`);m.querySelector('.mq-close')?.addEventListener('click',()=>m.remove());m.querySelectorAll('[data-topic]').forEach((b:any)=>b.addEventListener('click',async()=>{b.disabled=true;b.textContent='Building quest…';try{await api('/worksheets/new',{method:'POST',body:JSON.stringify({topic:b.dataset.topic})});location.reload()}catch(e:any){b.disabled=false;b.textContent=label(b.dataset.topic);alert(e.message)}}))}

async function review(id:number){const d=await api(`/worksheets/${id}/review`);const accuracy=d.total?Math.round(d.score/d.total*100):0;const m=modal(`<button class="mq-close">×</button><p class="eyebrow">COMPLETED WORKSHEET</p><h2>${label(d.selected_topic)} · ${dateLabel(d.date)}</h2><div class="mq-v0120-score"><strong>${d.score}/${d.total}</strong><span>${accuracy}% accuracy · ${d.counts.hints} hint${d.counts.hints===1?'':'s'}</span></div><div class="mq-v0120-questions">${d.questions.map((q:any)=>`<details><summary><b>${q.position+1}. ${q.prompt}</b><span class="${q.status}">${q.status}</span></summary><p>Your answer${q.student_answers?.length===1?'':'s'}: <strong>${q.student_answers?.map((a:any)=>a.answer).join(' → ')||'No answer'}</strong></p><p>Correct answer: <strong>${q.correct_answer}</strong></p><p>${q.working}</p>${q.hint_count?`<small>💡 ${q.hint_count} hint${q.hint_count===1?'':'s'} used</small>`:''}</details>`).join('')}</div>`);m.querySelector('.mq-close')?.addEventListener('click',()=>m.remove())}

function historyRows(history:any[],isParent:boolean){return history.slice(0,12).map((w:any)=>`<article><div><b>${label(w.selected_topic)}</b><small>${dateLabel(w.date)} · ${w.total} questions · ${w.hints} hints · +${w.xp_earned} XP</small></div><strong>${w.completed_at?`${w.score}/${w.total}`:'In progress'}</strong>${w.completed_at?`<button data-review="${w.id}">View worksheet</button>`:isParent?'<span class="mq-status">In progress</span>':''}</article>`).join('')}

let loading=false;
async function enhance(){if(loading||!token())return;const page=document.querySelector('.page');if(!page||document.querySelector('.mq-v0120-history'))return;const isParent=Boolean(document.querySelector('.parent-title'));loading=true;try{const history=await api('/worksheets/history');const todayKey=new Date().toLocaleDateString('en-CA');const today=history.filter((x:any)=>x.date===todayKey);const completed=today.filter((x:any)=>x.completed_at);const answered=today.reduce((n:number,x:any)=>n+(x.answered||0),0);const correct=today.reduce((n:number,x:any)=>n+(x.score||0),0);const hints=today.reduce((n:number,x:any)=>n+(x.hints||0),0);const xp=today.reduce((n:number,x:any)=>n+(x.xp_earned||0),0);const section=document.createElement('section');section.className='panel mq-v0120-history';section.innerHTML=`<div class="mq-v0120-head"><div><p class="eyebrow">${isParent?'TODAY’S LEARNING':'WORKSHEETS'}</p><h2>${isParent?'Worksheet activity':'Your worksheet history'}</h2><p>${completed.length?`${completed.length} worksheet${completed.length===1?'':'s'} completed today.`:'No worksheet has been completed today yet.'}</p></div>${isParent?'':'<button class="primary" data-new>+ New worksheet</button>'}</div>${isParent?`<div class="mq-v0120-metrics"><article><small>Completed</small><strong>${completed.length}</strong></article><article><small>Questions</small><strong>${answered}</strong></article><article><small>Accuracy</small><strong>${answered?Math.round(correct/answered*100)+'%':'—'}</strong></article><article><small>Hints</small><strong>${hints}</strong></article><article><small>XP today</small><strong>${xp}</strong></article></div>`:''}${history.length?`<div class="mq-v0120-list">${historyRows(history,isParent)}</div>`:'<p>No worksheets recorded yet.</p>'}`;const anchor=isParent?page.querySelector('.parent-title'):page.querySelector('.hero');anchor?.insertAdjacentElement('afterend',section);section.querySelector('[data-new]')?.addEventListener('click',chooseNew);section.querySelectorAll('[data-review]').forEach((b:any)=>b.addEventListener('click',()=>review(Number(b.dataset.review))))}catch(e){console.warn('MathQuest v0.12.1 history unavailable',e)}finally{loading=false}}

function run(){void enhance()}
let scheduled=false;const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;run()})});observer.observe(document.documentElement,{childList:true,subtree:true});window.addEventListener('pagehide',(event:PageTransitionEvent)=>{if(!event.persisted)observer.disconnect()});window.addEventListener('pageshow',()=>run());run();
