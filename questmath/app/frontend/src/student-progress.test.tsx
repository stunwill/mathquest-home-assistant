import React from 'react';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {fireEvent, render, screen, waitFor} from '@testing-library/react';
import {AdaptiveRecommendation} from './adaptive-recommendation';

const apiRequest = vi.fn();
vi.mock('./api', () => ({apiRequest: (...args:any[]) => apiRequest(...args)}));

const progress = {
  recommendation: {title:'Review Fractions', mode:'review', minutes:10},
  recommendation_explanation: {label:'QUICK REVIEW', text:'You did this before. It is back today to help you remember it.'},
  summary: {getting_stronger:1, building_confidence:1, review_due:1},
  learning_now: [
    {code:'A',strand:'Number',title:'Fractions',state:{key:'review_due',label:'Review due',message:'You have done this before. A quick review will help keep it fresh.',target_skill:'equivalent_fractions',evidence:{questions:8,independent_accuracy:75,eventual_accuracy:88,support_dependency:25}}},
    {code:'B',strand:'Algebra',title:'Patterns',state:{key:'getting_stronger',label:'Getting stronger',message:'You are solving these independently more often.',target_skill:'number_sequences',evidence:{questions:9,independent_accuracy:78,eventual_accuracy:89,support_dependency:11}}},
    {code:'C',strand:'Measurement',title:'Area',state:{key:'building_confidence',label:'Building confidence',message:'You can solve these with some help. We will keep practising them.',target_skill:'area',evidence:{questions:6,independent_accuracy:50,eventual_accuracy:83,support_dependency:50}}},
  ],
};

const adaptive = {summary:{review_due:1},recommendation:{mode:'review',minutes:10,topic:'number',outcome_code:'VC2M4N03',title:'Review Fractions',reason:'This skill is due for retrieval practice.',prerequisite_for:null}};

describe('student progress guidance', () => {
  beforeEach(()=>{apiRequest.mockReset();apiRequest.mockResolvedValue(progress)});

  it('renders learner states and the evidence-grounded why-this explanation', async () => {
    render(<AdaptiveRecommendation data={adaptive} busy={false} onStart={vi.fn()}/>);
    expect(await screen.findByRole('heading',{name:/what mathquest is noticing/i})).toBeInTheDocument();
    expect(screen.getAllByText('Getting stronger').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Building confidence').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Review due').length).toBeGreaterThan(0);
    expect(screen.getByText('QUICK REVIEW')).toBeInTheDocument();
  });

  it('keeps technical evidence behind optional disclosure', async () => {
    render(<AdaptiveRecommendation data={adaptive} busy={false} onStart={vi.fn()}/>);
    await screen.findByText('Patterns');
    expect(screen.queryByText(/78% independent success/i)).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole('button',{name:'Show learning detail'}));
    expect(screen.getByText(/does not use a separate student score/i)).toBeInTheDocument();
    expect(screen.getByText(/78% independent success/i)).toBeInTheDocument();
  });

  it('reuses the existing best-next-step action', async () => {
    const onStart=vi.fn();
    render(<AdaptiveRecommendation data={adaptive} busy={false} onStart={onStart}/>);
    await screen.findByRole('heading',{name:/what mathquest is noticing/i});
    fireEvent.click(screen.getByRole('button',{name:'Start best next step'}));
    expect(onStart).toHaveBeenCalledTimes(1);
  });

  it('uses one learner-progress request rather than recomputing evidence in React', async () => {
    render(<AdaptiveRecommendation data={adaptive} busy={false} onStart={vi.fn()}/>);
    await waitFor(()=>expect(apiRequest).toHaveBeenCalledWith('/learning/student-progress-v0410'));
    expect(apiRequest).toHaveBeenCalledTimes(1);
  });
});
