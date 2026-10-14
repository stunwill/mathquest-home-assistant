import React, {useState} from 'react';
import {afterEach,beforeEach,expect,test,vi} from 'vitest';
import {cleanup,fireEvent,render,screen,waitFor} from '@testing-library/react';
import {Worksheet} from './main';
import {isFinalQuestion} from './worksheet-navigation';
import './test-setup';

const response=(data:unknown)=>Promise.resolve(new Response(JSON.stringify(data),{headers:{'content-type':'application/json'}}));
beforeEach(()=>{localStorage.clear();localStorage.setItem('token','token');vi.restoreAllMocks()});
afterEach(cleanup);

function makeWorksheet(count:number,current:number,total=count){
  const questions=Array.from({length:count},(_,position)=>({id:position+1,position,topic:'number',skill:'VC2M4N06:written_subtraction',level:4,prompt:`Calculate ${600+position} − 137.`,summary:'Subtraction',answer_type:'number',payload:{},status:position<current?'correct':position===current?'current':'not_started',skipped_count:0,hint_count:0,last_hint:null,attempts:position<current?[{answer:'463',correct:true,attempt_number:1}]:[]}));
  return {id:10,date:'2026-10-14',completed_at:null,score:0,total,xp_earned:0,current_question_id:current+1,current_phase:'main',elapsed_seconds:0,status:'in_progress',selected_topic:'number',session_kind:'practice',test_mode:false,counts:{correct:current,incorrect:0,skipped:0,remaining:count-current,hints:0},questions};
}

function Harness({initial,onDone}:{initial:any;onDone:()=>void}){
  const [ws,setWs]=useState(initial);
  return <Worksheet ws={ws} onUpdate={setWs} onExit={()=>{}} onDone={onDone}/>;
}

async function answerCurrent(initial:any,overrides:any={}){
  const q=initial.questions.find((item:any)=>item.id===initial.current_question_id);
  const answered={...initial,counts:{...initial.counts,correct:initial.counts.correct+1,remaining:initial.counts.remaining-1},questions:initial.questions.map((item:any)=>item.id===q.id?{...item,status:'correct',attempts:[{answer:'463',correct:true,attempt_number:1}]}:item),...overrides};
  const fetchMock=vi.spyOn(globalThis,'fetch').mockImplementation(input=>{
    const url=String(input);
    if(url===`api/questions/${q.id}/answer`)return response({correct:true,retry_allowed:false,message:'Correct',working:'Check by addition.'});
    if(url==='api/worksheets/10/view')return response(answered);
    if(url.includes('/navigate/')){const id=Number(url.split('/').at(-1));return response({...answered,current_question_id:id})}
    if(url.endsWith('/complete'))return response({worksheet_id:10,xp_earned:100});
    return response({});
  });
  const onDone=vi.fn();render(<Harness initial={initial} onDone={onDone}/>);
  fireEvent.change(screen.getByRole('textbox',{name:'Your answer'}),{target:{value:'463'}});
  fireEvent.click(screen.getByRole('button',{name:'Check answer'}));
  await screen.findByRole('dialog',{name:'Correct answer'});
  return {fetchMock,onDone};
}

test.each([5,10,15])('second-last question of %i uses Next question and navigates without completing',async count=>{
  const {fetchMock,onDone}=await answerCurrent(makeWorksheet(count,count-2));
  expect(screen.queryByRole('button',{name:'Finish worksheet'})).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button',{name:'Next question'}));
  await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>String(url).endsWith(`/navigate/${count}`))).toBe(true));
  expect(fetchMock.mock.calls.some(([url])=>String(url).endsWith('/complete'))).toBe(false);
  expect(onDone).not.toHaveBeenCalled();
});

test.each([1,5,10,15])('actual final question of %i offers Finish worksheet',async count=>{
  const {onDone}=await answerCurrent(makeWorksheet(count,count-1));
  fireEvent.click(screen.getByRole('button',{name:'Finish worksheet'}));
  await waitFor(()=>expect(onDone).toHaveBeenCalledTimes(1));
});

test('an unanswered final question cannot be finished',()=>{
  render(<Harness initial={makeWorksheet(5,4)} onDone={vi.fn()}/>);
  expect(screen.queryByRole('button',{name:/Finish worksheet/})).not.toBeInTheDocument();
});

test('final question retains skipped review and does not silently complete it',async()=>{
  const initial=makeWorksheet(5,4);
  initial.questions[1].status='skipped';initial.questions[1].skipped_count=1;initial.questions[1].attempts=[];
  initial.counts.skipped=1;initial.counts.remaining=2;
  const {fetchMock,onDone}=await answerCurrent(initial);
  fireEvent.click(screen.getByRole('button',{name:'Next question'}));
  await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>String(url).endsWith('/navigate/2'))).toBe(true));
  expect(onDone).not.toHaveBeenCalled();
  expect(screen.queryByRole('button',{name:/Finish worksheet/})).not.toBeInTheDocument();
});

test('out-of-sequence answers cannot finish from an earlier question',async()=>{
  const initial=makeWorksheet(5,3);
  initial.questions[4].status='correct';initial.questions[4].attempts=[{answer:'467',correct:true,attempt_number:1}];initial.counts.remaining=1;
  const {fetchMock,onDone}=await answerCurrent(initial);
  fireEvent.click(screen.getByRole('button',{name:'Next question'}));
  await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>String(url).endsWith('/navigate/5'))).toBe(true));
  expect(onDone).not.toHaveBeenCalled();
});

test('resume, shorter collections and question-map positions use the actual ordered sequence',()=>{
  const questions=[{id:30,position:7},{id:10,position:0},{id:20,position:4}];
  expect(isFinalQuestion(questions,20)).toBe(false);
  expect(isFinalQuestion(questions,30)).toBe(true);
  expect(isFinalQuestion(questions,10)).toBe(false);
  expect(isFinalQuestion([],30)).toBe(false);
});

test('final detection uses the actual collection when stored total is larger',async()=>{
  await answerCurrent(makeWorksheet(3,2,10));
  expect(screen.getByRole('button',{name:'Finish worksheet'})).toBeInTheDocument();
});
