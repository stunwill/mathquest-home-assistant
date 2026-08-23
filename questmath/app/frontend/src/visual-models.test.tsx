import React from 'react';
import {afterEach, expect, it} from 'vitest';
import {cleanup, fireEvent, render, screen} from '@testing-library/react';
import {ArrayModel, EquivalentFractionModel, FractionComparison, FractionNumberLine, NumberLineModel, PlaceValueModel, type FractionValue} from './visual-models';
import './test-setup';

afterEach(cleanup);

it('renders fraction comparison with equal whole rows and written notation',()=>{
  const {container}=render(<FractionComparison items={[{label:'First',numerator:3,denominator:4},{label:'Second',numerator:5,denominator:8}]}/>);
  expect(screen.getByLabelText('Fraction comparison using equal-sized wholes')).toBeInTheDocument();
  const bars=container.querySelectorAll('.vm-fraction-bar');
  expect(bars).toHaveLength(2);
  expect(bars[0].children).toHaveLength(4);
  expect(bars[1].children).toHaveLength(8);
  expect(screen.getByText('3/4')).toBeInTheDocument();
  expect(screen.getByText('5/8')).toBeInTheDocument();
});

it('keeps interactive numerator and denominator synchronised',()=>{
  let current:FractionValue[]=[{label:'First',numerator:1,denominator:2},{label:'Second',numerator:2,denominator:4}];
  const {rerender}=render(<FractionComparison items={current} interactive onChange={next=>{current=next;rerender(<FractionComparison items={current} interactive onChange={()=>{}}/>)}}/>);
  fireEvent.change(screen.getByLabelText('First numerator'),{target:{value:'2'}});
  expect(screen.getByText('2/2')).toBeInTheDocument();
});

it('shows equivalent fractions using a common whole relationship',()=>{
  render(<EquivalentFractionModel value={{numerator:1,denominator:2}}/>);
  expect(screen.getByLabelText('1 over 2 is equivalent to 2 over 4')).toBeInTheDocument();
  expect(screen.getByText('1/2')).toBeInTheDocument();
  expect(screen.getByText('2/4')).toBeInTheDocument();
});

it('places fractions on one number line',()=>{
  render(<FractionNumberLine values={[{label:'A',numerator:1,denominator:2},{label:'B',numerator:3,denominator:4}]}/>);
  expect(screen.getByLabelText('A is at 1 over 2')).toBeInTheDocument();
  expect(screen.getByLabelText('B is at 3 over 4')).toBeInTheDocument();
});

it('supports keyboard-operable range controls',()=>{
  const changed:number[]=[];
  render(<NumberLineModel min={0} max={20} value={5} onChange={value=>changed.push(value)}/>);
  fireEvent.change(screen.getByLabelText('Number line position'),{target:{value:'9'}});
  expect(changed).toEqual([9]);
});

it('renders array and place value models accessibly',()=>{
  const {rerender}=render(<ArrayModel rows={3} columns={4}/>);
  expect(screen.getByLabelText('3 equal rows with 4 in each row')).toBeInTheDocument();
  rerender(<PlaceValueModel value={243}/>);
  expect(screen.getByLabelText('Place value representation of 243')).toBeInTheDocument();
});
