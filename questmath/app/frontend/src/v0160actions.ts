const API='api';
const token=()=>localStorage.getItem('token');

async function createWorksheet(topic:string){
  const t=token();
  const r=await fetch(`${API}/worksheets/new`,{method:'POST',headers:{'Content-Type':'application/json',...(t?{Authorization:`Bearer ${t}`}:{})},body:JSON.stringify({topic})});
  const type=r.headers.get('content-type')||'';
  if(!r.ok)throw new Error(type.includes('json')?(await r.json()).detail:'Unable to create worksheet');
  return r.json();
}

function openPicker(){
  document.querySelector('.mq-v0160-review.mq-picker')?.remove();
  const topics=['number_algebra','measurement','algebra','probability','number','space','statistics','mixed'];
  const labels:Record<string,string>={number_algebra:'Number & Algebra Focus',measurement:'Measurement',algebra:'Algebra',probability:'Probability',number:'Number',space:'Space',statistics:'Statistics',mixed:'Mixed Adventure'};
  const wrap=document.createElement('div');wrap.className='mq-v0160-review mq-picker';
  wrap.innerHTML=`<section><button class="close">×</button><p class="eyebrow">ANOTHER QUEST</p><h2>Choose your next worksheet</h2><p>You can have more than one worksheet in progress. Each worksheet is saved separately.</p><div class="mq-v0120-topics">${topics.map(t=>`<button data-topic="${t}">${labels[t]}</button>`).join('')}</div></section>`;
  wrap.querySelector('.close')?.addEventListener('click',()=>wrap.remove());
  wrap.querySelectorAll('[data-topic]').forEach((button:any)=>button.addEventListener('click',async()=>{const original=button.textContent;button.disabled=true;button.textContent='Building quest…';try{await createWorksheet(button.dataset.topic);location.reload()}catch(e:any){button.disabled=false;button.textContent=original;alert(e.message)}}));
  wrap.addEventListener('click',e=>{if(e.target===wrap)wrap.remove()});document.body.append(wrap);
}

function bind(){
  const button=document.querySelector('.mq-v0160-history [data-new]') as HTMLButtonElement|null;
  if(!button||button.dataset.v0160Bound==='1')return;
  button.dataset.v0160Bound='1';
  button.addEventListener('click',e=>{e.preventDefault();e.stopImmediatePropagation();openPicker()},true);
}

let scheduled=false;const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;bind()})});observer.observe(document.documentElement,{childList:true,subtree:true});bind();
