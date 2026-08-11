import './v0130.css';

const API='api';
let visualLoading=false;
let lastSignature='';

function currentQuestion(){
  const ws=(window as any).__mq_ws;
  return ws?.questions?.find((q:any)=>q.id===ws.current_question_id)||null;
}

function authHeaders():Record<string,string>{
  const headers:Record<string,string>={};
  const token=localStorage.getItem('token');
  if(token)headers.Authorization=`Bearer ${token}`;
  return headers;
}

function esc(value:any){return String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'} as any)[c])}

function sectorPath(index:number,total:number){
  const cx=60,cy=60,r=50;
  const start=-Math.PI/2+(index/total)*Math.PI*2;
  const end=-Math.PI/2+((index+1)/total)*Math.PI*2;
  const x1=cx+r*Math.cos(start),y1=cy+r*Math.sin(start);
  const x2=cx+r*Math.cos(end),y2=cy+r*Math.sin(end);
  const large=end-start>Math.PI?1:0;
  return `M ${cx} ${cy} L ${x1.toFixed(3)} ${y1.toFixed(3)} A ${r} ${r} 0 ${large} 1 ${x2.toFixed(3)} ${y2.toFixed(3)} Z`;
}

function pie(item:any){
  const n=Math.max(0,Number(item.numerator)||0),d=Math.max(1,Number(item.denominator)||1);
  const slices=Array.from({length:d},(_,i)=>`<path d="${sectorPath(i,d)}" class="${i<n?'filled':'empty'}"></path>`).join('');
  return `<figure class="mq-hint-pie"><svg viewBox="0 0 120 120" role="img" aria-label="${esc(n)} of ${esc(d)} equal slices shaded">${slices}<circle cx="60" cy="60" r="50" class="outline"></circle></svg><figcaption>${esc(item.label||`${n}/${d}`)}</figcaption></figure>`;
}

function fractionBar(item:any){
  const n=Math.max(0,Number(item.numerator)||0),d=Math.max(1,Number(item.denominator)||1);
  return `<div class="mq-hint-fraction-bar" aria-label="${esc(n)} of ${esc(d)} equal parts shaded">${Array.from({length:d},(_,i)=>`<span class="${i<n?'filled':''}"></span>`).join('')}</div>`;
}

function renderFractionPies(v:any){
  const items=(v.items||[]).slice(0,2);
  return `<div class="mq-hint-pies">${items.map(pie).join('')}</div>${v.show_bars?`<div class="mq-hint-bars">${items.map((x:any)=>`<div><b>${esc(x.label)}</b>${fractionBar(x)}</div>`).join('')}</div>`:''}`;
}

function renderNumberLine(v:any){
  const steps=Math.max(1,Math.min(20,Number(v.steps)||1));
  return `<div class="mq-hint-number-line"><div class="track">${Array.from({length:steps+1},(_,i)=>`<span><i></i><b>${i===0?esc(v.min):i===steps?esc(v.max):''}</b></span>`).join('')}</div><small>${steps} equal spaces</small></div>`;
}

function renderPlaceValue(v:any){return `<div class="mq-hint-place-value">${(v.digits||[]).map((x:any)=>`<div><small>${esc(x.place)}</small><strong>${esc(x.digit)}</strong></div>`).join('')}<span class="decimal-label">Number: ${esc(v.value)}</span></div>`}

function renderClock(v:any){
  const minute=(Number(v.minute)||0)%60,hour=(Number(v.hour)||12)%12;
  const mh=minute*6,hh=hour*30+minute*.5;
  return `<div class="mq-hint-clock"><div class="face"><b class="n12">12</b><b class="n3">3</b><b class="n6">6</b><b class="n9">9</b><i class="hour" style="transform:rotate(${hh}deg)"></i><i class="minute" style="transform:rotate(${mh}deg)"></i><span></span></div></div>`;
}

function renderAngle(v:any){
  const degrees=Math.max(0,Math.min(360,Number(v.degrees)||0));
  const x=(60+100*Math.cos(degrees*Math.PI/180)).toFixed(2),y=(125-100*Math.sin(degrees*Math.PI/180)).toFixed(2);
  return `<div class="mq-hint-angle"><svg viewBox="0 0 230 150" role="img" aria-label="Angle measuring ${degrees} degrees"><line x1="60" y1="125" x2="200" y2="125"></line><line x1="60" y1="125" x2="${x}" y2="${y}"></line><path d="M92 125 A32 32 0 0 0 ${(60+32*Math.cos(degrees*Math.PI/180)).toFixed(2)} ${(125-32*Math.sin(degrees*Math.PI/180)).toFixed(2)}"></path><text x="105" y="108">${degrees}°</text></svg><div><span>90° right angle</span><span>180° straight angle</span></div></div>`;
}

function renderGrid(v:any){
  const cols=(v.columns||['A','B','C','D','E']).slice(0,8),rows=Math.max(1,Math.min(8,Number(v.rows)||6));
  return `<div class="mq-hint-grid" style="grid-template-columns:repeat(${cols.length},1fr)">${cols.flatMap((c:string)=>Array.from({length:rows},(_,i)=>{const key=`${c}${i+1}`;return `<span class="${key===v.target?'target':''}">${esc(key)}</span>`})).join('')}</div>`;
}

function renderRectangle(v:any){return `<div class="mq-hint-rectangle-wrap"><div class="mq-hint-rectangle"><span class="length">${esc(v.length)}</span><span class="width">${esc(v.width)}</span><div>${v.mode==='area'?'space inside':'distance around'}</div></div><small>${v.mode==='area'?'Think about the inside':'Trace all four outside edges'}</small></div>`}

function renderSequence(v:any){return `<div class="mq-hint-sequence">${(v.values||[]).map((x:any,i:number)=>`<span>${esc(x)}</span>${i<(v.values||[]).length-1?'<b>→</b>':''}`).join('')}</div>`}

function visualMarkup(v:any){
  if(!v)return'';
  if(v.type==='fraction_pies')return renderFractionPies(v);
  if(v.type==='fraction_pie')return `<div class="mq-hint-pies single">${pie(v.item)}</div>${v.show_bar?fractionBar(v.item):''}`;
  if(v.type==='number_line')return renderNumberLine(v);
  if(v.type==='place_value')return renderPlaceValue(v);
  if(v.type==='clock')return renderClock(v);
  if(v.type==='angle')return renderAngle(v);
  if(v.type==='grid')return renderGrid(v);
  if(v.type==='rectangle')return renderRectangle(v);
  if(v.type==='sequence')return renderSequence(v);
  return'';
}

async function addVisualHint(){
  const hintBox=document.querySelector('.hint-box');
  const q=currentQuestion();
  if(!hintBox||!q||(q.hint_count||0)<1||visualLoading)return;
  const signature=`${q.id}:${q.hint_count}`;
  if(lastSignature===signature&&document.querySelector(`.mq-visual-hint[data-signature="${signature}"]`))return;
  visualLoading=true;
  try{
    const response=await fetch(`${API}/questions/${q.id}/hint-visual`,{headers:authHeaders()});
    if(!response.ok)return;
    const data=await response.json();
    if(!data.visual)return;
    document.querySelectorAll('.mq-visual-hint').forEach(n=>n.remove());
    const panel=document.createElement('section');
    panel.className='mq-visual-hint';
    panel.dataset.signature=signature;
    panel.innerHTML=`<div class="mq-visual-hint-title"><span>👀</span><div><small>VISUAL HINT</small><b>Picture the maths</b></div><em>Hint ${Math.min(2,Math.max(1,data.visual.hint_level||q.hint_count))}</em></div><div class="mq-visual-hint-canvas">${visualMarkup(data.visual)}</div><p>${esc(data.visual.instruction||'Use the picture to help work out your next step.')}</p>${data.visual.accessibility_text?`<span class="sr-only">${esc(data.visual.accessibility_text)}</span>`:''}`;
    hintBox.insertAdjacentElement('afterend',panel);
    lastSignature=signature;
  }catch(error){console.warn('MathQuest visual hint unavailable',error)}finally{visualLoading=false}
}

function run(){void addVisualHint()}
let scheduled=false;
const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;run()})});
observer.observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('pagehide',(event:PageTransitionEvent)=>{if(!event.persisted)observer.disconnect()});
window.addEventListener('pageshow',()=>run());
run();
