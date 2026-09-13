export function keyboardVisible(layoutHeight:number, visualHeight:number, activeElement:Element|null):boolean{
  const activeTag=activeElement?.tagName.toLowerCase();
  return visualHeight>0 && layoutHeight-visualHeight>160 && (activeTag==='input'||activeTag==='textarea');
}

export function setupKeyboardViewport():()=>void{
  const root=document.documentElement;
  const visualViewport=window.visualViewport;
  const update=()=>{
    const visualHeight=visualViewport?.height||window.innerHeight;
    root.style.setProperty('--mq-visual-viewport-height',`${visualHeight}px`);
    root.dataset.mqKeyboard=keyboardVisible(window.innerHeight,visualHeight,document.activeElement)?'open':'closed';
  };
  update();
  window.addEventListener('resize',update,{passive:true});
  document.addEventListener('focusin',update);
  visualViewport?.addEventListener('resize',update);
  return()=>{window.removeEventListener('resize',update);document.removeEventListener('focusin',update);visualViewport?.removeEventListener('resize',update)};
}
