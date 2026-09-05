import React from 'react';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import {StudentProgress} from './student-progress';

const apiRequest = vi.fn();
vi.mock('./api', () => ({apiRequest: (...args:any[]) => apiRequest(...args)}));

const progress = {
  recommendation: {title:'Review Fractions', mode:'review', minutes:10},
  recommendation_explanation: {label:'QUICK REVIEW', text:'You did this before. It is back today to help you remember it.'},
  summary: {getting_stronger:1, building_confidence:1, review_due:1},
  learning_now: [
    {code:'A',strand:'Number',title:'Fractions',questions:8,last_practised:null,review_due:true,state:{key:'review_due',label:'Review due',message:'You have done this before. A quick review will help keep it fresh.',target_skill:'equivalent_fractions',evidence:{questions:8,independent_accuracy:75,eventual_accuracy:88,support_dependency:25}}},
    {code:'B',strand:'Algebra',title:'Patterns',questions:9,last_practised:null,review_due:false,state:{key:'getting_stronger',label:'Getting stronger',message:'Your recent answers show strong independent work.',target_skill:'number_sequences',evidence:{questions:9,independent_accuracy:78,eventual_accuracy:89,support_dependency:11}}},
    {code:'C',strand:'Measurement',title:'Area',questions:6,last_practised:null,review_due:false,state:{key:'building_confidence',label:'Building confidence',message:'You can solve these with some help. We will keep practising them.',target_skill:'area',evidence:{questions:6,independent_accuracy:50,eventual_accuracy:83,support_dependency:50}}},
  ],
  this_week: [],
};

describe('student progress guidance', () => {
  beforeEach(()=>{apiRequest.mockReset();apiRequest.mockResolvedValue(progress)});

  it('renders learner states and the evidence-grounded why-this explanation', async () => {
    render(<StudentProgress/>);
    expect(await screen.findByRole('heading',{name:/what mathquest is noticing/i})).toBeInTheDocument();
    expect(screen.getAllByText('Getting stronger').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Building confidence').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Review due').length).toBeGreaterThan(0);
    expect(screen.getByText('QUICK REVIEW')).toBeInTheDocument();
  });

  it('keeps technical evidence behind optional disclosure', async () => {
    render(<StudentProgress/>);
    await screen.findByText('Patterns');
    expect(screen.queryByText('Independent success')).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Show learning detail'}));
    expect(screen.getAllByText('Independent success').length).toBeGreaterThan(0);
    expect(screen.getByText(/does not use a separate student score/i)).toBeInTheDocument();
  });

  it('does not create a competing start action when embedded in Progress', async () => {
    render(<StudentProgress/>);
    await screen.findByText('Review Fractions');
    expect(screen.queryByRole('button',{name:/start best next step/i})).not.toBeInTheDocument();
  });

  it('uses one learner-progress request rather than recomputing evidence in React', async () => {
    render(<StudentProgress/>);
    await waitFor(()=>expect(apiRequest).toHaveBeenCalledWith('/learning/student-progress-v0410'));
    expect(apiRequest).toHaveBeenCalledTimes(1);
  });
});
