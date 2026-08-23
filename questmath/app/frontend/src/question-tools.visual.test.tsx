import React from 'react';
import {fireEvent, render, screen} from '@testing-library/react';
import '@testing-library/jest-dom';
import {QuestionTools} from './question-tools';

it('shows question-specific visual recommendation and opens the lab only when chosen',()=>{
  let opened=0;
  render(<QuestionTools question={{id:1,payload:{visual_mathematics:{teaching_visual_available:true,recommended_model:'fractions',visual_reason:'Equal-sized wholes make the compared amounts visible.'},solution_strategies:[]}}} onOpenLab={()=>opened++}/>);
  expect(screen.getByText('Equal-sized wholes make the compared amounts visible.')).toBeInTheDocument();
  expect(opened).toBe(0);
  fireEvent.click(screen.getByRole('button',{name:'Try the fractions model'}));
  expect(opened).toBe(1);
});

it('switches one alternate strategy at a time without touching the answer field',()=>{
  const answer=document.createElement('input');
  answer.value='75';
  document.body.appendChild(answer);
  render(<QuestionTools question={{id:2,payload:{solution_strategies:[{title:'Partition',explanation:'Add tens, then ones.'},{title:'Compensate',explanation:'Use a nearby ten, then undo the adjustment.'},{title:'Place value',explanation:'Combine matching places.'}]}}} onOpenLab={()=>{}}/>);
  fireEvent.click(screen.getByRole('button',{name:'↻ Show another way'}));
  expect(screen.getByText('Compensate')).toBeInTheDocument();
  expect(screen.queryByText('Place value')).not.toBeInTheDocument();
  expect(answer.value).toBe('75');
  answer.remove();
});

it('does not expose a new visual recommendation when assessment restrictions disable it',()=>{
  render(<QuestionTools question={{id:3,payload:{visual_mathematics:{teaching_visual_available:false,assessment_restricted:true,recommended_model:'fractions'},solution_strategies:[]}}} onOpenLab={()=>{}}/>);
  expect(screen.queryByLabelText('Visual mathematics recommendation')).not.toBeInTheDocument();
});
