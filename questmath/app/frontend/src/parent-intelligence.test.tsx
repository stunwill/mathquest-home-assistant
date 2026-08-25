import React from 'react';
import {render, screen} from '@testing-library/react';
import {describe, expect, it, vi} from 'vitest';
import {ParentLearningIntelligence} from './parent-intelligence';

const data={
  summary:['Addition with regrouping is becoming secure.'],
  trend:{days:30,current:{first_attempt_accuracy:80,eventual_accuracy:90,questions:12},previous:{first_attempt_accuracy:65,eventual_accuracy:82,questions:10}},
  difficulty:{state:'at_instructional_level',attempts:12},
  recommendations:[{priority:'practise',title:'Practise subtraction with decomposition',reason:'First-attempt accuracy remains low.',skill:'number:written_subtraction'}],
  misconceptions:[{skill:'number:written_subtraction',type:'regrouping_error',label:'Regrouping Error',skill_label:'Subtraction with decomposition',count:3,response:'MathQuest will prioritise subtraction practice.'}],
  retention:[{skill:'number:written_addition',label:'Addition with regrouping',review_due:false,status:'secure'}],
  skills:[
    {skill:'number:written_addition',label:'Addition with regrouping',attempts:12,confidence:'strong',status:'secure',first_attempt_accuracy:90,eventual_accuracy:100,support_dependency:10},
    {skill:'number:written_subtraction',label:'Subtraction with decomposition',attempts:8,confidence:'moderate',status:'needs_support',first_attempt_accuracy:45,eventual_accuracy:88,support_dependency:70},
  ],
};

describe('v0.32.0 parent learning intelligence',()=>{
  it('shows the learning summary and practice priority',()=>{
    render(<ParentLearningIntelligence data={data} onPeriod={vi.fn()}/>);
    expect(screen.getByText('Addition with regrouping is becoming secure.')).toBeTruthy();
    expect(screen.getByText('Practise subtraction with decomposition')).toBeTruthy();
  });

  it('distinguishes first-attempt, eventual and support evidence',()=>{
    render(<ParentLearningIntelligence data={data} onPeriod={vi.fn()}/>);
    expect(screen.getAllByText('First attempt').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Eventual').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Support used').length).toBeGreaterThan(0);
    expect(screen.getAllByText('70%').length).toBeGreaterThan(0);
  });

  it('shows conservative mastery states and misconception evidence',()=>{
    render(<ParentLearningIntelligence data={data} onPeriod={vi.fn()}/>);
    expect(screen.getAllByText('Secure').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Needs Support').length).toBeGreaterThan(0);
    expect(screen.getByText('Regrouping Error')).toBeTruthy();
    expect(screen.getByText('3 observations')).toBeTruthy();
  });
});
