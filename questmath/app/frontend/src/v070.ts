import './v070.css';

const API='api';

function headers(): Record<string,string> {
  const result: Record<string,string> = {};
  const token=localStorage.getItem('token');
  if(token) result.Authorization=`Bearer ${token}`;
  return result;
}

async function get(path:string){
  const r=await fetch(API+path,{headers:headers()});
  return r.ok?r.json():null;
}

function updateBrand(){
  document.querySelectorAll('.mq-brand').forEach(el=>{
    if(el.querySelector('.mq-v070-logo'))return;
    el.innerHTML='<img class="mq-v070-logo" src="./mathquest-logo.svg" alt="MathQuest by Stu">';
  });
  document.querySelectorAll('.version').forEach(n=>n.textContent='Version 0.7.0');
  document.querySelectorAll('.header-version').forEach(n=>n.textContent='v0.7.0');
}

function trendSvg(points:any[]){
  const vals=points.filter(x=>x.accuracy!==null);
  if(vals.length<2)return '<p class="mq-muted">Complete more worksheets to build the progress chart.</p>';
  const w=520,h=150,p=18;
  const coords=vals.map((x,i)=>`${p+i*(w-p*2)/Math.max(1,vals.length-1)},${h-p-(x.accuracy/100)*(h-p*2)}`).join(' ');
  return `<svg viewBox="0 0 ${w} ${h}" class="mq-trend"><line x1="18" y1="132" x2="502" y2="132"/><polyline points="${coords}"/><text x="18" y="16">100%</text><text x="18" y="128">0%</text></svg>`;
}

async function parentEnhance(){
  const page=document.querySelector('.page');
  if(!page||document.querySelector('.mq-v070-parent'))return;
  const d=await get('/dashboard/parent');
  if(!d?.parent_insights)return;
  const section=document.createElement('section');
  section.className='panel mq-v070-parent';
  section.innerHTML=`<div class="mq-v070-title"><div><p class="eyebrow">LEARNING INTELLIGENCE</p><h2>What MathQuest is noticing</h2></div><span class="mq-pill">v0.7</span></div><div class="mq-insights">${d.parent_insights.map((x:string)=>`<article>💡 <span>${x}</span></article>`).join('')}</div><h3>30-day accuracy</h3>${trendSvg(d.progress_trends?.['30d']?.points||[])}<div class="mq-rewards"><div><h3>Rewards</h3>${(d.rewards||[]).map((x:any)=>`<span>🏆 <b>${x.name}</b><small>${x.detail}</small></span>`).join('')||'<p class="mq-muted">New rewards will unlock as independent mastery grows.</p>'}</div><div><h3>Mastery moments</h3>${(d.mastery_moments||[]).map((x:any)=>`<span>⭐ ${x.message}</span>`).join('')||'<p class="mq-muted">Breakthroughs will appear here.</p>'}</div></div><div class="mq-ha"><b>Home Assistant status API</b><code>/api/home-assistant/status</code><small>Exposes completion, streak, accuracy, XP, hints, recommended topic and revision status for HA dashboards and automations.</small></div>`;
  page.prepend(section);
}

async function studentEnhance(){
  const page=document.querySelector('.page');
  if(!page||document.querySelector('.mq-v070-student'))return;
  const [d,a]=await Promise.all([get('/dashboard/student'),get('/assignments')]);
  if(!d)return;
  const section=document.createElement('section');
  section.className='panel mq-v070-student';
  const moments=d.mastery_moments||[], rewards=d.rewards||[];
  section.innerHTML=`<div class="mq-v070-title"><div><p class="eyebrow">YOUR PROGRESS</p><h2>Growing stronger</h2></div><span class="mq-pill">${d.adaptive_learning?.recommended_topic?`Next: ${d.adaptive_learning.recommended_topic}`:'Keep exploring'}</span></div>${a?.length?`<div class="mq-assignment"><b>📚 Parent Practice Quest</b>${a.map((x:any)=>`<span>${x.title} · ${x.question_count} questions · ${x.topics.join(', ')}</span>`).join('')}</div>`:''}<div class="mq-rewards">${rewards.map((x:any)=>`<span>🏆 <b>${x.name}</b><small>${x.detail}</small></span>`).join('')}${moments.map((x:any)=>`<span>⭐ ${x.message}</span>`).join('')}</div>`;
  page.querySelector('.hero')?.insertAdjacentElement('afterend',section);
}

function isParentPage(): boolean {
  return Boolean(
    document.querySelector('.parent-title') ||
    document.body.textContent?.includes('PARENT VIEW') ||
    document.body.textContent?.includes('learning overview')
  );
}

function enhance(){
  updateBrand();
  if(isParentPage()) parentEnhance();
  else studentEnhance();
}

new MutationObserver(enhance).observe(document.documentElement,{childList:true,subtree:true});
enhance();
