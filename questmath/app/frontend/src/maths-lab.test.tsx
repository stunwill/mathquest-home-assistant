import React from 'react';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {afterEach, describe, expect, it, vi} from 'vitest';
import {MathsLab, recommendedLabTool} from './maths-lab';

afterEach(cleanup);

describe('interactive Maths Lab',()=>{
  it('recommends a model from the current question without limiting the other tools',()=>{
    expect(recommendedLabTool({topic:'number',skill:'VC2M4N03:equivalent_fractions'})).toBe('fractions');
    expect(recommendedLabTool({topic:'algebra',skill:'VC2M4A02:fact_recall_multiplication'})).toBe('arrays');
    expect(recommendedLabTool({topic:'measurement',skill:'VC2M4M03:duration'})).toBe('clock');
    render(<MathsLab question={{topic:'number',skill:'VC2M4N03:equivalent_fractions'}} onClose={()=>{}}/>);
    expect(screen.getAllByRole('button',{name:/Fractions/})[0].getAttribute('aria-pressed')).toBe('true');
    expect(screen.getByRole('button',{name:/Percentages/})).toBeTruthy();
    expect(screen.getByRole('button',{name:/Measurement/})).toBeTruthy();
  });

  it('links percentage, decimal, fraction and quantity representations',()=>{
    render(<MathsLab question={{topic:'number',skill:'percentage'}} onClose={()=>{}}/>);
    fireEvent.change(screen.getByLabelText('Percentage'),{target:{value:'40'}});
    fireEvent.change(screen.getByLabelText('Whole quantity'),{target:{value:'250'}});
    expect(screen.getByText('2/5')).toBeTruthy();
    expect(screen.getByText('0.40')).toBeTruthy();
    expect(screen.getByText('100')).toBeTruthy();
  });

  it('builds an array and resets the current model',()=>{
    render(<MathsLab question={{topic:'algebra',skill:'fact_recall_multiplication'}} onClose={()=>{}}/>);
    fireEvent.change(screen.getByLabelText('Array rows'),{target:{value:'5'}});
    fireEvent.change(screen.getByLabelText('Array columns'),{target:{value:'6'}});
    expect(screen.getByText('5 rows × 6 in each row = 30 counters')).toBeTruthy();
    fireEvent.click(screen.getByRole('button',{name:'Start over'}));
    expect(screen.getByText('3 rows × 4 in each row = 12 counters')).toBeTruthy();
  });

  it('links ruler and rectangle dimensions to perimeter and area',()=>{
    render(<MathsLab question={{topic:'measurement',skill:'area'}} onClose={()=>{}}/>);
    fireEvent.change(screen.getByLabelText('Ruler marker'),{target:{value:'10'}});
    fireEvent.change(screen.getByLabelText('Rectangle width'),{target:{value:'4'}});
    expect(screen.getByText('28 cm')).toBeTruthy();
    expect(screen.getByText('40 cm²')).toBeTruthy();
  });

  it('closes through the accessible close control',()=>{
    const close=vi.fn();
    render(<MathsLab question={{topic:'space',skill:'grid_references'}} onClose={close}/>);
    fireEvent.click(screen.getByRole('button',{name:'Close maths lab'}));
    expect(close).toHaveBeenCalledOnce();
  });
});
