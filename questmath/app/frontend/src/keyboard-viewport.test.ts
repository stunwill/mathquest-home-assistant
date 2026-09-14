import {afterEach,describe,expect,it,vi} from 'vitest';
import {answerContextScrollDelta,keyboardVisible,setupKeyboardViewport} from './keyboard-viewport';

afterEach(()=>{vi.useRealTimers();vi.restoreAllMocks();document.body.innerHTML='';});

describe('keyboard viewport detection',()=>{
  it('activates only for a substantially reduced viewport and answer control',()=>{
    const input=document.createElement('input');
    expect(keyboardVisible(768,500,input)).toBeTruthy();
    expect(keyboardVisible(768,700,input)).toBeFalsy();
    expect(keyboardVisible(768,500,document.createElement('button'))).toBeFalsy();
  });
});

describe('return to answering with a software keyboard',()=>{
  const rect=(top:number,bottom:number)=>({top,bottom} as DOMRect);
  it('keeps the question and answer together when they fit, and prioritises answer when they do not',()=>{
    expect(answerContextScrollDelta(rect(120,170),rect(430,530),0,400)).toBe(142);
    expect(answerContextScrollDelta(rect(210,240),rect(430,530),0,400)).toBe(142);
    expect(answerContextScrollDelta(rect(-50,10),rect(170,280),0,400)).toBe(-104);
    expect(answerContextScrollDelta(rect(100,140),rect(180,280),0,400)).toBe(0);
    expect(answerContextScrollDelta(rect(150,190),rect(340,410),20,400)).toBe(2);
  });

  it('restores on answer focus and re-tap, but not while reading support or using a physical keyboard',()=>{
    vi.useFakeTimers();
    const input=document.createElement('input');
    const card=document.createElement('section');card.className='question-card';
    const heading=document.createElement('h1');
    const group=document.createElement('div');group.className='answer-action-group';
    const row=document.createElement('div');row.className='answer-row';
    row.append(input);group.append(row);card.append(heading,group);
    const support=document.createElement('button');support.textContent='Math Mentor';
    card.append(support);document.body.append(card);
    vi.spyOn(heading,'getBoundingClientRect').mockReturnValue(rect(80,120));
    vi.spyOn(group,'getBoundingClientRect').mockReturnValue(rect(400,500));
    const scroll=vi.spyOn(window,'scrollBy').mockImplementation(()=>{});
    const originalHeight=window.innerHeight;
    Object.defineProperty(window,'innerHeight',{configurable:true,value:700});
    const viewport={height:400,offsetTop:0,addEventListener:vi.fn(),removeEventListener:vi.fn()};
    Object.defineProperty(window,'visualViewport',{configurable:true,value:viewport});
    const cleanup=setupKeyboardViewport();
    input.focus();vi.advanceTimersByTime(100);
    expect(scroll).toHaveBeenCalledWith({top:112,behavior:'auto'});
    scroll.mockClear();
    support.dispatchEvent(new Event('pointerdown',{bubbles:true}));
    vi.advanceTimersByTime(300);
    expect(scroll).not.toHaveBeenCalled();
    input.dispatchEvent(new Event('pointerdown',{bubbles:true}));
    vi.advanceTimersByTime(100);
    expect(scroll).toHaveBeenCalledTimes(1);
    scroll.mockClear();
    const nextInput=document.createElement('input');
    row.replaceChild(nextInput,input);
    nextInput.focus();vi.advanceTimersByTime(100);
    expect(scroll).toHaveBeenCalledTimes(1);
    scroll.mockClear();
    viewport.height=650;
    nextInput.blur();nextInput.focus();vi.advanceTimersByTime(100);
    expect(scroll).not.toHaveBeenCalled();
    cleanup();
    Object.defineProperty(window,'innerHeight',{configurable:true,value:originalHeight});
    Object.defineProperty(window,'visualViewport',{configurable:true,value:undefined});
  });
});
