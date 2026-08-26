import {describe, expect, it} from 'vitest';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';

const mainSource=readFileSync(resolve(process.cwd(),'src/main.tsx'),'utf8');

describe('v0.32.1 worksheet retry and tutoring safeguards',()=>{
  it('keeps Math Mentor optional after an incorrect retryable answer',()=>{
    expect(mainSource).toContain('if(result.mentor_required)');
    expect(mainSource).toContain('!feedback||feedback.retry_allowed');
    expect(mainSource).toContain('You can try another answer now');
  });

  it('keeps the answer input accessible and keyboard ready',()=>{
    expect(mainSource).toContain('aria-label="Your answer"');
    expect(mainSource).toContain('autoFocus');
    expect(mainSource).toContain("feedback.retry_allowed");
    expect(mainSource).toContain('void safe(submit)');
  });

  it('does not make tutoring a prerequisite for Check answer',()=>{
    const answerIndex=mainSource.indexOf('<Answer q={q}');
    const checkIndex=mainSource.indexOf('>Check answer</button>');
    expect(answerIndex).toBeGreaterThan(-1);
    expect(checkIndex).toBeGreaterThan(answerIndex);
  });
});
