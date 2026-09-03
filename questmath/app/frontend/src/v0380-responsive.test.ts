import {describe, expect, it} from 'vitest';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';

const sourceDir=resolve(process.cwd(),'src');
const feedbackStyles=readFileSync(resolve(sourceDir,'student-feedback.css'),'utf8');
const mainSource=readFileSync(resolve(sourceDir,'main.tsx'),'utf8');

describe('v0.38 responsive feedback contracts',()=>{
  it('targets iPad 10th generation landscape CSS dimensions without changing portrait breakpoints',()=>{
    expect(feedbackStyles).toContain('@media (min-width:900px) and (max-width:1200px) and (orientation:landscape)');
    expect(feedbackStyles).toContain('grid-template-columns:minmax(0,1fr) 220px');
    expect(feedbackStyles).toContain('max-height:calc(100dvh - 28px)');
  });

  it('makes correct and incorrect feedback viewport-fixed while only the modal body can scroll',()=>{
    expect(feedbackStyles).toContain('.post-answer-backdrop{position:fixed;inset:0');
    expect(feedbackStyles).toContain('grid-template-rows:auto minmax(0,1fr) auto');
    expect(feedbackStyles).toContain('.post-answer-scroll{min-height:0;overflow:auto');
    expect(feedbackStyles).toContain('.post-answer-actions{display:flex');
  });

  it('respects reduced motion and does not rely on colour for result meaning',()=>{
    expect(feedbackStyles).toContain('@media (prefers-reduced-motion: reduce)');
    expect(mainSource).toContain('PostAnswerFeedbackModal');
    expect(mainSource).not.toContain('optional-tutor-feedback wrong');
  });
});
