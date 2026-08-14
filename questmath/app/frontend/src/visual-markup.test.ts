import {describe, expect, it} from 'vitest';
import {fractionComparisonMarkup, gridReferenceMarkup} from './visual-markup';

describe('question visual markup', () => {
  it('keeps grid references out of the cells and labels the axes', () => {
    document.body.innerHTML = gridReferenceMarkup({columns: ['A', 'B', 'C', 'D'], rows: 4, target: 'C3'});

    expect(Array.from(document.querySelectorAll('.grid-row-label')).map(item => item.textContent)).toEqual(['A', 'B', 'C', 'D']);
    expect(Array.from(document.querySelectorAll('.grid-column-label')).map(item => item.textContent)).toEqual(['1', '2', '3', '4']);
    expect(document.querySelectorAll('.grid-cell')).toHaveLength(16);
    expect(document.querySelector('.grid-cell.target')?.textContent).toBe('');
    expect(document.body.textContent).not.toContain('C3');
    expect(document.querySelector('[data-visual-answer]')).toBeNull();
  });

  it('renders compared fractions as equal-whole stacked rows', () => {
    document.body.innerHTML = fractionComparisonMarkup([
      {label: 'Jack', numerator: 4, denominator: 5},
      {label: 'Margaret', numerator: 2, denominator: 3},
    ]);

    const rows = document.querySelectorAll('.fraction-row');
    expect(rows).toHaveLength(2);
    expect(rows[0].querySelectorAll('.fraction-bar span')).toHaveLength(5);
    expect(rows[1].querySelectorAll('.fraction-bar span')).toHaveLength(3);
    expect(rows[0].querySelectorAll('.fraction-bar .on')).toHaveLength(4);
    expect(rows[1].querySelectorAll('.fraction-bar .on')).toHaveLength(2);
    expect(Array.from(rows).every(row => row.classList.contains('fraction-row'))).toBe(true);
    expect(Array.from(rows).every(row => row.querySelector('.fraction-bar'))).toBe(true);
  });
});
