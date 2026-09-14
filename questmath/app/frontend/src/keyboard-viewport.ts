const ANSWER_INPUT = '.question-card .answer-action-group .answer-row input';

export function keyboardVisible(layoutHeight:number, visualHeight:number, activeElement:Element|null):boolean{
  const activeTag=activeElement?.tagName.toLowerCase();
  return visualHeight>0 && layoutHeight-visualHeight>160 && (activeTag==='input'||activeTag==='textarea');
}

// The visual viewport may be offset within the layout viewport on iOS ingress.
export function answerContextScrollDelta(heading:DOMRect, group:DOMRect, viewportTop:number, viewportHeight:number):number{
  const top=viewportTop+54;
  const bottom=viewportTop+viewportHeight-12;
  const needed=group.bottom>bottom ? group.bottom-bottom : group.top<top ? group.top-top :
    heading.top<top ? Math.max(heading.top-top,group.bottom-bottom) : 0;
  if(!needed)return 0;
  // Keep the question visible if both fit. Large essential diagrams instead
  // yield space to the answer and Check answer interaction.
  if(needed>0 && group.bottom-heading.top<=bottom-top)return Math.min(needed,Math.max(0,heading.top-top));
  return needed;
}

export function setupKeyboardViewport():()=>void{
  const root=document.documentElement;
  const visualViewport=window.visualViewport;
  let pending:HTMLInputElement|null=null;
  let settleTimer:number|undefined;
  let expiryTimer:number|undefined;
  const update=()=>{
    const visualHeight=visualViewport?.height||window.innerHeight;
    root.style.setProperty('--mq-visual-viewport-height',`${visualHeight}px`);
    root.dataset.mqKeyboard=keyboardVisible(window.innerHeight,visualHeight,document.activeElement)?'open':'closed';
  };
  const restore=()=>{
    if(!pending||!pending.isConnected||document.activeElement!==pending)return;
    const height=visualViewport?.height||window.innerHeight;
    if(!keyboardVisible(window.innerHeight,height,pending))return;
    const card=pending.closest('.question-card');
    const heading=card?.querySelector('h1');
    const group=pending.closest('.answer-action-group');
    if(heading&&group){
      const delta=answerContextScrollDelta(heading.getBoundingClientRect(),group.getBoundingClientRect(),visualViewport?.offsetTop||0,height);
      if(Math.abs(delta)>2)window.scrollBy({top:delta,behavior:'auto'});
    }
    pending=null;
  };
  const schedule=()=>{
    if(settleTimer!==undefined)window.clearTimeout(settleTimer);
    settleTimer=window.setTimeout(restore,90);
  };
  const request=(target:EventTarget|null)=>{
    if(!(target instanceof HTMLInputElement)||!target.matches(ANSWER_INPUT))return;
    pending=target;
    schedule();
    if(expiryTimer!==undefined)window.clearTimeout(expiryTimer);
    expiryTimer=window.setTimeout(()=>{pending=null},1200);
  };
  const focus=(event:FocusEvent)=>{update();request(event.target)};
  const pointer=(event:PointerEvent)=>{if(event.target===document.activeElement)request(event.target)};
  const resize=()=>{update();if(pending)schedule()};
  update();
  window.addEventListener('resize',resize,{passive:true});
  document.addEventListener('focusin',focus);
  document.addEventListener('pointerdown',pointer);
  visualViewport?.addEventListener('resize',resize);
  return()=>{
    window.removeEventListener('resize',resize);
    document.removeEventListener('focusin',focus);
    document.removeEventListener('pointerdown',pointer);
    visualViewport?.removeEventListener('resize',resize);
    if(settleTimer!==undefined)window.clearTimeout(settleTimer);
    if(expiryTimer!==undefined)window.clearTimeout(expiryTimer);
  };
}
