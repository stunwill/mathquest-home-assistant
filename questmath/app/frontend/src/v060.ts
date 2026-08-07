import './v060.css';

const API = 'api';
const VERSION = '0.6.0';

function tokenHeaders(extra: Record<string,string> = {}) {
  const token = localStorage.getItem('token');
  return {
    ...(token ? {Authorization:`Bearer ${token}`} : {}),
    ...extra,
  };
}

function selectedTopic(): string {
  const selected = document.querySelector('.category-option.selected b')?.textContent?.trim().toLowerCase() || 'mixed adventure';
  const map: Record<string,string> = {
    'measurement':'measurement',
    'algebra':'algebra',
    'probability':'probability',
    'number':'number',
    'space':'space',
    'statistics':'statistics',
    'mixed adventure':'mixed',
  };
  return map[selected] || 'mixed';
}

async function printWorksheet(topic: string) {
  const response = await fetch(`${API}/worksheets/today/print`, {
    method:'POST',
    headers: tokenHeaders({'Content-Type':'application/json'}),
    body: JSON.stringify({topic}),
  });
  if (!response.ok) {
    const data = await response.json().catch(()=>({detail:'Unable to print worksheet'}));
    throw new Error(data.detail || 'Unable to print worksheet');
  }
  const blob = await response.blob();
  const disposition = response.headers.get('content-disposition') || '';
  const match = disposition.match(/filename="?([^";]+)"?/i);
  const filename = match?.[1] || 'mathquest-worksheet.pdf';
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(link.href);
}

function makePrintButton(label: string, topicProvider: ()=>string) {
  const button = document.createElement('button');
  button.type = 'button';
  button.className = 'mq-print-button';
  button.innerHTML = `🖨️ <span>${label}</span>`;
  button.addEventListener('click', async () => {
    if (button.dataset.busy === 'true') return;
    button.dataset.busy = 'true';
    const old = button.innerHTML;
    button.innerHTML = '🖨️ <span>Preparing…</span>';
    try {
      await printWorksheet(topicProvider());
      window.setTimeout(()=>window.location.reload(), 250);
    } catch (error:any) {
      alert(error?.message || 'Unable to print worksheet');
      button.innerHTML = old;
      button.dataset.busy = 'false';
    }
  });
  return button;
}

function enhanceCategoryPicker() {
  const actions = document.querySelector('.category-actions');
  if (!actions || actions.querySelector('.mq-print-button')) return;
  const print = makePrintButton('Print worksheet', selectedTopic);
  actions.insertBefore(print, actions.lastElementChild);
}

function enhanceStudentHero() {
  const hero = document.querySelector('.hero');
  if (!hero || hero.querySelector('.mq-print-button')) return;
  const primary = Array.from(hero.querySelectorAll('button')).find(button =>
    /Continue Today|Today complete/i.test(button.textContent || '')
  );
  if (!primary || /Today complete/i.test(primary.textContent || '')) return;
  const print = makePrintButton('Print current worksheet', ()=> 'mixed');
  primary.insertAdjacentElement('afterend', print);
}

function patchVersionLabels() {
  document.querySelectorAll('.version').forEach(node => {
    node.textContent = `Version ${VERSION}`;
  });
  document.querySelectorAll('header b small').forEach(node => {
    node.textContent = `v${VERSION}`;
  });
}

function enhance() {
  patchVersionLabels();
  enhanceCategoryPicker();
  enhanceStudentHero();
}

const observer = new MutationObserver(enhance);
observer.observe(document.documentElement, {childList:true, subtree:true});
enhance();
