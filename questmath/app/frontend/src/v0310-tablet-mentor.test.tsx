import {describe, expect, it} from 'vitest';
import fs from 'node:fs';
import path from 'node:path';

const ROOT = path.resolve(__dirname);

function source(name:string){
  return fs.readFileSync(path.join(ROOT,name),'utf8');
}

describe('v0.31.0 tablet and Math Mentor presentation',()=>{
  it('uses the v0.31.0 question-specific mentor endpoint',()=>{
    const main=source('main.tsx');
    expect(main).toContain('math-mentor-v0310');
    expect(main).toContain('support.teach_steps');
    expect(main).toContain('mentor-math');
  });

  it('does not render the old duplicate strategy card after hint two',()=>{
    const main=source('main.tsx');
    expect(main).not.toContain("q.hint_count>=2&&<StrategyCard");
  });

  it('keeps answer entry available while tutoring is open',()=>{
    const main=source('main.tsx');
    const answerIndex=main.indexOf('<Answer q={q}');
    const mentorIndex=main.indexOf('<MathMentor support={support}');
    expect(answerIndex).toBeGreaterThan(-1);
    expect(mentorIndex).toBeGreaterThan(answerIndex);
  });

  it('contains deliberate tablet breakpoints and touch targets',()=>{
    const css=source('styles.css');
    expect(css).toContain('@media(max-width:1100px)');
    expect(css).toContain('min-height:44px');
    expect(css).toContain('position:sticky;bottom:8px');
    expect(css).toContain('.mentor-lesson');
  });

  it('preserves mathematical line breaks for progressive hints',()=>{
    const css=source('styles.css');
    expect(css).toContain('.hint-box p');
    expect(css).toContain('white-space:pre-line');
  });
});
