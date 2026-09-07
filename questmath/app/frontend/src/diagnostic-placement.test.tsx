import React from 'react';
import {render, screen, waitFor} from '@testing-library/react';
import '@testing-library/jest-dom/vitest';
import {expect, test, vi} from 'vitest';
import {DiagnosticCompletion, DiagnosticPlacementSummary} from './diagnostic-placement';

vi.mock('./api', () => ({
  apiRequest: vi.fn(async () => ({
    status: 'complete',
    student_message: 'MathQuest has a useful starting point, but needs a little more evidence before making stronger claims.',
    demonstrated: [{strand:'Number', title:'Efficient calculation strategies', target_skill:'written_subtraction'}],
    supported: [],
    needs_more_evidence: [{strand:'Number', title:'Equivalent fractions and decimals', target_skill:'equivalent_fractions'}],
    recommended_focus: {title:'Practice Equivalent fractions and decimals', target_skill:'equivalent_fractions', explanation:'MathQuest needs a little more evidence before increasing difficulty.'},
  })),
}));

test('shows learner-safe diagnostic placement without grade or mastery claims', async () => {
  render(<DiagnosticPlacementSummary/>);
  await waitFor(() => expect(screen.getByText('What MathQuest learned')).toBeInTheDocument());
  expect(screen.getByText('YOU SHOWED CONFIDENCE WITH')).toBeInTheDocument();
  expect(screen.getByText('WE NEED A LITTLE MORE EVIDENCE')).toBeInTheDocument();
  expect(screen.getByText('NEXT, MATHQUEST RECOMMENDS')).toBeInTheDocument();
  const text=document.body.textContent||'';
  expect(text).not.toMatch(/mastered level 5|grade 6 student|% mastery/i);
  expect(text).not.toMatch(/VC2M\d/i);
});

test('diagnostic completion explains the starting signal instead of showing an exam result', async () => {
  render(<DiagnosticCompletion back={()=>{}}/>);
  expect(screen.getByRole('heading',{name:'You completed all six questions'})).toBeInTheDocument();
  expect(screen.getByText(/not a pass, fail or overall grade/i)).toBeInTheDocument();
  await waitFor(() => expect(screen.getByText('NEXT, MATHQUEST RECOMMENDS')).toBeInTheDocument());
  const text=document.body.textContent||'';
  expect(text).not.toMatch(/accuracy|% mastery|working at grade/i);
  expect(screen.getByRole('button',{name:'Continue to MathQuest'})).toBeInTheDocument();
});
