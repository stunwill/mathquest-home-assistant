import React from 'react';
import {render, screen, waitFor} from '@testing-library/react';
import '@testing-library/jest-dom';
import {vi} from 'vitest';
import {DiagnosticPlacementSummary} from './diagnostic-placement';

vi.mock('./api', () => ({
  apiRequest: vi.fn(async () => ({
    status: 'complete',
    student_message: 'MathQuest has a useful starting point, but needs a little more evidence before making stronger claims.',
    demonstrated: [{strand:'Number', title:'Efficient calculation strategies', target_skill:'diagnostic_operations'}],
    supported: [],
    needs_more_evidence: [{strand:'Number', title:'Equivalent fractions and decimals', target_skill:'diagnostic_fraction_decimal'}],
    recommended_focus: {title:'Practice Equivalent fractions and decimals', target_skill:'diagnostic_fraction_decimal', explanation:'MathQuest needs a little more evidence before increasing difficulty.'},
  })),
}));

test('shows learner-safe diagnostic placement without grade or mastery claims', async () => {
  render(<DiagnosticPlacementSummary/>);
  await waitFor(() => expect(screen.getByText('What MathQuest learned')).toBeInTheDocument());
  expect(screen.getByText('YOU SHOWED CONFIDENCE WITH')).toBeInTheDocument();
  expect(screen.getByText('WE NEED A LITTLE MORE EVIDENCE')).toBeInTheDocument();
  expect(screen.getByText('NEXT, MATHQUEST RECOMMENDS')).toBeInTheDocument();
  const text=document.body.textContent||'';
  expect(text).not.toMatch(/mastered level 5|grade 6 student|pass|fail|% mastery/i);
  expect(text).not.toMatch(/VC2M\d/i);
});
