import React from 'react';
import {describe, expect, it, vi} from 'vitest';
import {render, screen} from '@testing-library/react';
import {PostAnswerFeedbackModal, meaningfulFeedback} from './post-answer-feedback';
import './test-setup';

describe('v0.47.3 feedback quality', () => {
  it('does not render a generic praise block when no specific insight exists', () => {
    render(<PostAnswerFeedbackModal feedback={{correct:true,retry_allowed:false,message:'Great job!'}} primaryLabel="Next question" onPrimary={vi.fn()} />);
    expect(screen.queryByText('What went well')).not.toBeInTheDocument();
  });
  it('keeps specific mathematical feedback when supplied by the learning engine', () => {
    render(<PostAnswerFeedbackModal feedback={{correct:true,retry_allowed:false,message:'You recognised the inverse relationship.'}} working="Multiplication and division undo each other." primaryLabel="Next question" onPrimary={vi.fn()} />);
    expect(screen.getByText('What went well')).toBeInTheDocument();
    expect(screen.getByText('You recognised the inverse relationship.')).toBeInTheDocument();
    expect(screen.getByText('Multiplication and division undo each other.')).toBeInTheDocument();
  });
  it('classifies only generic praise as unsupported feedback', () => {
    expect(meaningfulFeedback('Correct!')).toBe(false);
    expect(meaningfulFeedback('You used the number pattern correctly.')).toBe(true);
  });
});
