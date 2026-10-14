import React from 'react';
import {afterEach, expect, test, vi} from 'vitest';
import {cleanup, render, screen} from '@testing-library/react';
import {LearnerRewards} from './learner-rewards';
import {Student} from './main';
import {apiRequest} from './api';
import './test-setup';

vi.mock('./api',()=>({apiRequest:vi.fn(),ApiError:class extends Error{},loadActiveWorksheet:vi.fn(async()=>null),createSession:vi.fn(),rememberActiveWorksheet:vi.fn(),questionDraft:vi.fn(()=>''),rememberQuestionDraft:vi.fn()}));
vi.mock('./student-foundation',()=>({ErrorNotice:()=>null,StudentDestination:()=>null,StudentMobileNavigation:()=>null,WorksheetHistory:()=>null}));
vi.mock('./adaptive-recommendation',()=>({AdaptiveRecommendation:()=>null}));
vi.mock('./targeted-learning',()=>({TargetedCompletion:()=>null,TargetedLearningPreview:()=>null}));
vi.mock('./intervention',()=>({InterventionCard:()=>null,InterventionGoal:()=>null}));
afterEach(()=>{cleanup();vi.clearAllMocks()});

const rewards={id:1,xp:2450,level:10,xp_per_level:250,level_progress:200,next_level:11,xp_until_next_level:50};
const learner=(id:number)=>({id,username:`learner${id}`,display_name:'Learner',role:'student',xp:0,level:1,highest_level:1});

test('shows persisted total XP and the existing threshold progression accessibly',()=>{
  render(<LearnerRewards learnerId={1} user={rewards}/>);
  expect(screen.getByText('Level 10')).toBeInTheDocument();
  expect(screen.getByText('2,450 XP')).toBeInTheDocument();
  expect(screen.getByText('50 XP until Level 11')).toBeInTheDocument();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow','200');
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuemax','250');
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuetext','80 percent, 50 XP until Level 11');
});

test.each([null,{}, {...rewards,id:2},{...rewards,xp:undefined},{...rewards,xp:-1}])('does not invent rewards for missing or mismatched data',user=>{
  render(<LearnerRewards learnerId={1} user={user}/>);
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  expect(screen.queryByText('Level 1')).not.toBeInTheDocument();
  expect(screen.getByRole('status')).toHaveTextContent('unavailable');
});

test('handles an exact level boundary without implying the next level is complete',()=>{
  render(<LearnerRewards learnerId={1} user={{...rewards,xp:2500,level:11,level_progress:0,next_level:12,xp_until_next_level:250}}/>);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow','0');
  expect(screen.getByText('250 XP until Level 12')).toBeInTheDocument();
});

test('the home dashboard uses refreshed rewards and never leaks the previous learner while switching',async()=>{
  let resolveNext!:(value:unknown)=>void;
  vi.mocked(apiRequest).mockImplementation(async path=>path==='/dashboard/student'?{user:rewards}:null);
  const {rerender}=render(<Student key={1} user={learner(1)} logout={()=>{}}/>);
  expect(await screen.findByText('2,450 XP')).toBeInTheDocument();
  vi.mocked(apiRequest).mockImplementation(path=>path==='/dashboard/student'?new Promise(resolve=>{resolveNext=resolve}):Promise.resolve(null));
  rerender(<Student key={2} user={learner(2)} logout={()=>{}}/>);
  expect(screen.queryByText('2,450 XP')).not.toBeInTheDocument();
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  resolveNext({user:{...rewards,id:2,xp:2000,level:9,level_progress:0,next_level:10,xp_until_next_level:250}});
  expect(await screen.findByText('2,000 XP')).toBeInTheDocument();
  expect(screen.queryByText('2,450 XP')).not.toBeInTheDocument();
});
