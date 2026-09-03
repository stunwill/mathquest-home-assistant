import {describe, expect, it} from 'vitest';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';

const mainSource=readFileSync(resolve(process.cwd(),'src/main.tsx'),'utf8');
const feedbackSource=readFileSync(resolve(process.cwd(),'src/post-answer-feedback.tsx'),'utf8');

describe('v0.32.1 worksheet retry and tutoring safeguards',()=>{
  it('keeps Math Mentor optional after an incorrect retryable answer',()=>{
    expect(mainSource).toContain('if(result.mentor_required)');
    expect(mainSource).toContain("feedback.retry_allowed?'Try again'");
    expect(mainSource).toContain('onOpenMentor={feedback.retry_allowed?');
    expect(feedbackSource).toContain('Math Mentor can guide you without making help a required step.');
  });

  it('keeps the answer input accessible and keyboard ready',()=>{
    expect(mainSource).toContain('aria-label="Your answer"');
    expect(mainSource).toContain('autoFocus');
    expect(mainSource).toContain('answerRef.current?.focus');
    expect(mainSource).toContain('void safe(submit)');
  });

  it('does not make tutoring a prerequisite for Check answer',()=>{
    const answerIndex=mainSource.indexOf('<Answer q={q}');
    const checkIndex=mainSource.indexOf('>Check answer</button>');
    expect(answerIndex).toBeGreaterThan(-1);
    expect(checkIndex).toBeGreaterThan(answerIndex);
  });
});
