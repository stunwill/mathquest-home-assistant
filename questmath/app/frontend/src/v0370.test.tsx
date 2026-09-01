import React from 'react';
import {fireEvent, render, screen} from '@testing-library/react';
import {describe, expect, it, vi} from 'vitest';
import {Answer} from './main';
import {FractionBarAnswer, FractionNumberLineAnswer, GridSelectAnswer, RulerAnswer} from './interactive-math';

describe('v0.37 interactive mathematics',()=>{
  it('selects fraction-bar parts directly on the representation',()=>{
    const setValue=vi.fn();
    const q={payload:{visual:{denominator:5}}};
    render(<FractionBarAnswer q={q} value="" setValue={setValue}/>);
    const third=screen.getByRole('button',{name:'Select 3 of 5 equal parts'});
    fireEvent.click(third);
    expect(setValue).toHaveBeenCalledWith('3');
  });

  it('keeps an internal fraction target unlabelled while making ticks selectable',()=>{
    const setValue=vi.fn();
    const q={payload:{visual:{denominator:4,label_indices:[0,4]}}};
    render(<FractionNumberLineAnswer q={q} value="" setValue={setValue}/>);
    const target=screen.getByRole('button',{name:'Unlabelled fraction tick 4'});
    fireEvent.click(target);
    expect(setValue).toHaveBeenCalledWith('3');
    expect(target.textContent).toBe('');
  });

  it('selects a mathematically scaled ruler mark without showing an unlabelled value',()=>{
    const setValue=vi.fn();
    const q={payload:{visual:{steps:6,interval:2,unit:'cm',label_indices:[0,3,6]}}};
    render(<RulerAnswer q={q} value="" setValue={setValue}/>);
    const target=screen.getByRole('button',{name:'Unlabelled ruler mark 3'});
    fireEvent.click(target);
    expect(setValue).toHaveBeenCalledWith('4');
    expect(target.textContent).toBe('');
  });

  it('uses accessible grid-square buttons and records the selected reference',()=>{
    const setValue=vi.fn();
    const q={payload:{visual:{columns:['A','B','C'],rows:3}}};
    render(<GridSelectAnswer q={q} value="" setValue={setValue}/>);
    const square=screen.getByRole('button',{name:'Square B2'});
    fireEvent.click(square);
    expect(setValue).toHaveBeenCalledWith('B2');
  });

  it('routes first-class interactive answer types instead of generic text inputs',()=>{
    const setValue=vi.fn();
    render(<Answer q={{answer_type:'fraction_bar',payload:{visual:{denominator:4}}}} value="" setValue={setValue}/>);
    expect(screen.queryByLabelText('Your answer')).toBeNull();
    expect(screen.getByRole('group',{name:'Fraction bar split into 4 equal parts'})).toBeTruthy();
  });

  it('preserves structured choice reasoning questions',()=>{
    const setValue=vi.fn();
    render(<Answer q={{answer_type:'choice',payload:{choices:['addition','multiplication','division']}}} value="" setValue={setValue}/>);
    fireEvent.click(screen.getByRole('button',{name:'multiplication'}));
    expect(setValue).toHaveBeenCalledWith('multiplication');
  });
});
