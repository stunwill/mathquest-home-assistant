import React from 'react';
import {render, screen} from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import {expect, test, vi} from 'vitest';
import {TargetedCompletion, TargetedLearningPreview} from './targeted-learning';
import {ParentTargetedLearningInsight} from './parent-targeted-learning';

vi.mock('./api', () => ({
  apiRequest: vi.fn(async (path:string) => {
    if(path.includes('targeted-summary')) return {available:true,purpose:'consolidate',target_skill:'equivalent_fractions',message:'You used support earlier, then solved a similar question independently.'};
    if(path.includes('targeted-session-detail')) return {
      available:true,title:'Equivalent fractions and decimals',purpose:'consolidate',
      evidence:{answered:6,independent_successes:4,support_used_questions:1,independent_checks:2},
      before:{questions:4},after:{questions:10},
    };
    return {
      kind:'targeted',minutes:10,purpose:'consolidate',title:'Equivalent fractions and decimals',reason:'Build confidence with equivalent fractions and decimals and work towards doing it independently.',target_skill:'equivalent_fractions',
      student_title:'Equivalent fractions and decimals',student_reason:'Build confidence with equivalent fractions and decimals and work towards doing it independently.',
      primary_target:{outcome_code:'VC2M4N03',title:'Equivalent fractions and decimals',skill:'equivalent_fractions',prerequisite_for:'VC2M4A02',evidence_questions:4,status:'developing',review_due:false},
      stages:['reconnect','supported','core','core','core','core','core','core','transfer','transfer','check','check']
    };
  }),
}));

test('student preview explains the focus without technical learning analytics', async () => {
  render(<TargetedLearningPreview/>);
  expect(await screen.findByRole('region',{name:"Today's focus"})).toBeInTheDocument();
  expect(screen.getByText('Equivalent fractions and decimals')).toBeInTheDocument();
  expect(screen.getByText(/work towards doing it independently/i)).toBeInTheDocument();
  const text=document.body.textContent||'';
  expect(text).not.toMatch(/VC2M|%|mastery|support dependency|below grade|failed/i);
});

test('targeted completion foregrounds learning evidence rather than a score', async () => {
  render(<TargetedCompletion worksheetId={42} back={()=>{}}/>);
  expect(screen.getByRole('heading',{name:'Nice work'})).toBeInTheDocument();
  expect(await screen.findByText(/used support earlier, then solved a similar question independently/i)).toBeInTheDocument();
  expect(screen.getByText(/Focus:/)).toBeInTheDocument();
  const text=document.body.textContent||'';
  expect(text).not.toMatch(/accuracy|\d+\s*\/\s*\d+|% mastery/i);
  expect(screen.getByRole('button',{name:'Continue to MathQuest'})).toBeInTheDocument();
});

test('parent insight exposes the evidence, prerequisite and latest targeted follow-through', async () => {
  render(<ParentTargetedLearningInsight/>);
  expect(await screen.findByRole('region',{name:'Targeted learning plan'})).toBeInTheDocument();
  expect(screen.getByText('VC2M4N03')).toBeInTheDocument();
  expect(screen.getByText(/Prerequisite for VC2M4A02/)).toBeInTheDocument();
  expect(screen.getByText(/independent check × 2/i)).toBeInTheDocument();
  expect(await screen.findByRole('heading',{name:'Latest completed targeted session'})).toBeInTheDocument();
  expect(screen.getByText(/6 answered, 4 independent successes, 1 questions with support, 2 independent checks/i)).toBeInTheDocument();
  expect(screen.getByText(/4 → 10 evidence questions/i)).toBeInTheDocument();
});
