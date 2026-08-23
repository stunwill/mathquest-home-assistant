import React from 'react';
import {afterEach, describe, expect, it} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import {QuestionVisual} from './question-visual';
import './test-setup';

afterEach(cleanup);

describe('React-owned question visuals', () => {
  it('stacks fractions against equal-width wholes', () => {
    const {container} = render(<QuestionVisual question={{id: 1, payload: {visual_key: '1:1', visual: {type: 'fraction_compare', items: [
      {label: 'Jack', numerator: 4, denominator: 5}, {label: 'Margaret', numerator: 2, denominator: 3},
    ]}}}}/>);
    expect(screen.getByRole('group', {name: /equal-sized wholes/i})).toBeInTheDocument();
    expect(container.querySelectorAll('.vm-fraction-row')).toHaveLength(2);
    expect(container.querySelectorAll('.vm-fraction-bar')).toHaveLength(2);
  });

  it('labels grid axes but does not print the answer inside the highlighted square', () => {
    const {container} = render(<QuestionVisual question={{id: 2, payload: {visual_key: '2:2', visual: {
      type: 'grid', columns: ['A', 'B', 'C', 'D'], rows: 4, target: 'C3',
    }}}}/>);
    expect(screen.getByLabelText('Highlighted square')).toBeInTheDocument();
    expect(container.querySelector('.grid-cell.target')?.textContent).toBe('');
    expect(container.querySelectorAll('.grid-row-label')).toHaveLength(4);
    expect(container.querySelectorAll('.grid-column-label')).toHaveLength(4);
  });

  it('renders only the visual attached to the current question payload', () => {
    const {rerender} = render(<QuestionVisual question={{id: 3, payload: {visual_key: '3:3', visual: {type: 'clock', hour: 3, minute: 15}}}}/>);
    expect(screen.getByRole('img', {name: /analogue clock/i})).toBeInTheDocument();
    rerender(<QuestionVisual question={{id: 4, payload: {visual_key: '4:4', visual: {type: 'angle', degrees: 90}}}}/>);
    expect(screen.queryByRole('img', {name: /analogue clock/i})).not.toBeInTheDocument();
    expect(screen.getByRole('img', {name: /angle diagram/i})).toBeInTheDocument();
  });
});
