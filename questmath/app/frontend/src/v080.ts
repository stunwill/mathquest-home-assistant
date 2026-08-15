import './v080.css';

const API='api';
function authHeaders():Record<string,string>{const headers:Record<string,string>={'Content-Type':'application/json'};const token=localStorage.getItem('token');if(token)headers.Authorization=`Bearer ${token}`;return headers}
async function get(path:string){const response=await fetch(API+path,{headers:authHeaders()});if(!response.ok)throw new Error((await response.json().catch(()=>({detail:'Request failed'}))).detail||'Request failed');return response.json()}
async function post(path:string,body:any){const response=await fetch(API+path,{method:'POST',headers:authHeaders(),body:JSON.stringify(body)});if(!response.ok)throw new Error((await response.json().catch(()=>({detail:'Request failed'}))).detail||'Request failed');return response.json()}

let parentLoading=false,studentLoading=false;
async function enhanceParentAssignments(){
  const page=document.querySelector('.page');
  if(parentLoading||!page||document.querySelector('.mq-v080-assignments'))return;
  parentLoading=true;
  try{
    const assignments=await get('/assignments/all');
    if(document.querySelector('.mq-v080-assignments'))return;
    const section=document.createElement('section');section.className='panel mq-v080-assignments';
    section.innerHTML=`<div class="mq-v080-head"><div><p class="eyebrow">PRACTICE QUESTS</p><h2>Assign targeted practice</h2></div></div><form class="mq-assignment-form"><input name="title" placeholder="Practice quest title" value="Targeted practice"><div class="mq-topic-picks">${['number','algebra','measurement','space','statistics','probability'].map(topic=>`<label><input type="checkbox" name="topics" value="${topic}">${topic}</label>`).join('')}</div><label>Questions <input name="count" type="number" min="5" max="50" value="10"></label><label>Due date <input name="due" type="date"></label><button class="primary" type="submit">Assign to Sienna</button><p class="mq-assignment-message" role="status"></p></form><div class="mq-assignment-list">${assignments.map((assignment:any)=>`<article><div><b>${assignment.title}</b><small>${assignment.topics.join(', ')} · ${assignment.question_count} questions${assignment.due_date?` · due ${assignment.due_date}`:''}</small></div><span class="status ${assignment.status}">${assignment.status.replace('_',' ')}</span></article>`).join('')||'<p class="mq-muted">No practice quests assigned yet.</p>'}</div>`;
    page.prepend(section);
    section.querySelector('form')?.addEventListener('submit',async(event:any)=>{event.preventDefault();const form=new FormData(event.target);const topics=form.getAll('topics').map(String);const message=section.querySelector('.mq-assignment-message') as HTMLElement;message.textContent='';if(!topics.length){message.textContent='Select at least one learning area.';return}try{await post('/assignments',{title:String(form.get('title')||'Practice Quest'),topics,question_count:Number(form.get('count')||10),due_date:String(form.get('due')||'')||null});message.textContent='Practice quest assigned. Refreshing the list…';window.setTimeout(()=>location.reload(),400)}catch(reason:any){message.textContent=reason.message}});
  }catch{}finally{parentLoading=false}
}

async function enhanceStudentAssignments(){
  const page=document.querySelector('.page');
  if(studentLoading||!page||document.querySelector('.mq-v080-student-assignments'))return;
  studentLoading=true;
  try{
    const assignments=await get('/assignments');
    if(!assignments?.length||document.querySelector('.mq-v080-student-assignments'))return;
    const section=document.createElement('section');section.className='panel mq-v080-student-assignments';
    section.innerHTML=`<p class="eyebrow">PARENT PRACTICE</p><h2>Your assigned quests</h2><p class="mq-assignment-message" role="status"></p>${assignments.map((assignment:any)=>`<article><div><b>${assignment.title}</b><small>${assignment.question_count} questions · ${assignment.topics.join(', ')}${assignment.due_date?` · due ${assignment.due_date}`:''}</small></div><button data-start-assignment="${assignment.id}" class="primary">Prepare practice quest</button></article>`).join('')}`;
    page.querySelector('.hero')?.insertAdjacentElement('afterend',section);
    section.querySelectorAll('[data-start-assignment]').forEach((button:any)=>button.addEventListener('click',async()=>{const message=section.querySelector('.mq-assignment-message') as HTMLElement;message.textContent='';try{const data=await post(`/assignments/${button.dataset.startAssignment}/start`,{});message.textContent=`Practice quest prepared. Choose ${data.topics.join(', ')} when starting your next worksheet.`}catch(reason:any){message.textContent=reason.message}}));
  }catch{}finally{studentLoading=false}
}

function enhance(){const text=document.body.textContent||'';if(text.includes('PARENT VIEW'))void enhanceParentAssignments();else void enhanceStudentAssignments()}
let scheduled=false;
const observer=new MutationObserver(()=>{if(scheduled)return;scheduled=true;requestAnimationFrame(()=>{scheduled=false;enhance()})});
observer.observe(document.documentElement,{childList:true,subtree:true});
window.addEventListener('pagehide',()=>observer.disconnect(),{once:true});
enhance();
