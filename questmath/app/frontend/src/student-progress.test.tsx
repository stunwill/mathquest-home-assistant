import React from 'react';
import '@testing-library/jest-dom/vitest';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, render, screen, waitFor} from '@testing-library/react';
import {StudentProgress} from './student-progress';

const apiRequest = vi.fn();
vi.mock('./api', () => ({apiRequest: (...args:any[]) => apiRequest(...args)}));

const progress = {
  recommendation: {title:'Review Fractions', mode:'review', minutes:10},
  recommendation_explanation: {label:'QUICK REVIEW', text:'You did this before. It is back today to help you remember it.'},
  summary: {getting_stronger:1, building_confidence:0, review_due:1},
  learning_now: [
    {code:'A',strand:'Number',title:'Fractions',questions:8,last_practised:null,review_due:true,state:{key:'review_due',label:'Review due',message:'You have done this before. A quick review will help keep it fresh.',target_skill:'equivalent_fractions'}},
    {code:'B',strand:'Algebra',title:'Patterns',questions:9,last_practised:null,review_due:false,state:{key:'getting_stronger',label:'Getting stronger',message:'Your recent answers show strong independent work.',target_skill:'number_sequences'}},
  ],
};

describe('student progress guidance', () => {
  beforeEach(()=>{apiRequest.mockReset();apiRequest.mockResolvedValue(progress)});
  afterEach(()=>cleanup());

  it('uses learner-safe Ready to review language', async () => {
    render(<StudentProgress/>);
    expect(await screen.findByRole('heading',{name:/what mathquest is noticing/i})).toBeInTheDocument();
    expect(screen.getAllByText('Ready to review').length).toBeGreaterThan(0);
    expect(screen.queryByText('Review due')).not.toBeInTheDocument();
  });

  it('hides zero-value learning summaries', async () => {
    render(<StudentProgress/>);
    await screen.findByText('Fractions');
    expect(screen.queryByText(/0 building confidence/i)).not.toBeInTheDocument();
  });

  it('groups skills under one state explanation rather than repeating row messages', async () => {
    render(<StudentProgress/>);
    await screen.findByText('Patterns');
    expect(screen.getByText(/skills are looking strong/i)).toBeInTheDocument();
    expect(screen.queryByText(/strong independent work/i)).not.toBeInTheDocument();
  });

  it('does not expose technical success percentages in student progress', async () => {
    render(<StudentProgress/>);
    await screen.findByText('Patterns');
    expect(screen.queryByText(/Independent success/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Eventually correct/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Support used/i)).not.toBeInTheDocument();
  });

  it('uses one learner-progress request rather than recomputing evidence in React', async () => {
    render(<StudentProgress/>);
    await waitFor(()=>expect(apiRequest).toHaveBeenCalledWith('/learning/student-progress-v0410'));
    expect(apiRequest).toHaveBeenCalledTimes(1);
  });
});
