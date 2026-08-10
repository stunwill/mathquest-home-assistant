import './v0140.css';

const API='api';
const token=()=>localStorage.getItem('token');

async function api(path:string){
  const r=await fetch(API+path,{headers:{...(token()?{Authorization:`Bearer ${token()}`}:{})}});
  const type=r.headers.get('content-type')||'';
  if(!r.ok||!type.includes('json')) return null;
  return r.json();
}

function updateVersion(){
  document.querySelectorAll('.version').forEach(n=>n.textContent='Version 0.14.0');
  document.querySelectorAll('.header-version').forEach(n=>n.textContent='v0.14.0');
}

let loading=false;
async function addPreviousNotice(){
  if(loading||!token()||document.querySelector('.mq-v0140-previous')) return;
  const history=document.querySelector('.mq-v0120-history');
  if(!history) return;
  loading=true;
  try{
    const rows=await api('/worksheets/unfinished/previous');
    if(!rows?.length||document.querySelector('.mq-v0140-previous')) return;
    const box=document.createElement('div');
    box.className='mq-v0140-previous';
    box.innerHTML=`<div><b>Previous unfinished worksheets</b><span>${rows.length} older worksheet${rows.length===1?' is':'s are'} still in progress. They stay in history and do not count as today’s quest.</span></div>`;
    history.querySelector('.mq-v0120-head')?.insertAdjacentElement('afterend',box);
  } finally { loading=false; }
}

function run(){updateVersion();void addPreviousNotice()}
let scheduled=false;
const observer=new MutationObserver(()=>{
  if(scheduled)return;
  scheduled=true;
  requestAnimationFrame(()=>{scheduled=false;run()});
});
observer.observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('pagehide',(event:PageTransitionEvent)=>{if(!event.persisted)observer.disconnect()});
window.addEventListener('pageshow',run);
run();
