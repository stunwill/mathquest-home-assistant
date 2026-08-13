import './v0170.css';

const API='api';
function headers():Record<string,string>{const token=localStorage.getItem('token');return token?{Authorization:`Bearer ${token}`}:{}}
async function focus(){const response=await fetch(`${API}/learning/focus-v0170`,{headers:headers()});return response.ok?response.json():null}
function label(value:string){return value.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase())}

let loading=false;
async function enhance(){
  const page=document.querySelector('.page');
  if(loading||!page||page.querySelector('.mq-v0170-focus'))return;
  loading=true;
  try{
    const data=await focus();
    if(!data||page.querySelector('.mq-v0170-focus'))return;
    const assessed=(data.operations||[]).filter((item:any)=>item.questions>0);
    const section=document.createElement('section');
    section.className='panel mq-v0170-focus';
    section.innerHTML=`<div class="mq-v0170-head"><div><p class="eyebrow">NUMBER & ALGEBRA SUPPORT</p><h2>Building fluent facts and efficient strategies</h2><p>MathQuest revisits facts answered incorrectly or with hints, while teaching strategies that replace finger counting.</p></div><span>v0.17</span></div>${assessed.length?`<div class="mq-v0170-grid">${assessed.map((item:any)=>`<article><div><b>${label(item.label)}</b><small>${item.status}${item.review_due?' · review due':''}</small></div><strong>${item.independent_accuracy??'—'}${item.independent_accuracy===null?'':'%'}</strong><p>${item.questions} questions · ${item.hints} hints${item.average_seconds?` · ${item.average_seconds}s avg`:''}</p></article>`).join('')}</div>`:'<p class="mq-v0170-empty">Complete a Number & Algebra Focus quest to start tracking fact recall and retention.</p>'}`;
    const anchor=page.querySelector('.mq-v070-student')||page.querySelector('.parent-title')||page.querySelector('.hero');
    anchor?.insertAdjacentElement('afterend',section);
  }finally{loading=false}
}
let scheduled=false;const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;void enhance()})});observer.observe(document.documentElement,{childList:true,subtree:true});void enhance();
