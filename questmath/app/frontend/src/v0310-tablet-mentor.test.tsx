/// <reference types="vite/client" />

import {describe, expect, it} from 'vitest';
import mainSource from './main.tsx?raw';
import stylesSource from './styles.css?raw';

describe('v0.31.0 tablet and Math Mentor presentation',()=>{
  it('uses the v0.31.0 question-specific mentor endpoint',()=>{
    expect(mainSource).toContain('math-mentor-v0310');
    expect(mainSource).toContain('support.teach_steps');
    expect(mainSource).toContain('mentor-math');
  });

  it('does not render the old duplicate strategy card after hint two',()=>{
    expect(mainSource).not.toContain("q.hint_count>=2&&<StrategyCard");
  });

  it('keeps answer entry available while tutoring is open',()=>{
    const answerIndex=mainSource.indexOf('<Answer q={q}');
    const mentorIndex=mainSource.indexOf('<MathMentor support={support}');
    expect(answerIndex).toBeGreaterThan(-1);
    expect(mentorIndex).toBeGreaterThan(answerIndex);
  });

  it('contains deliberate tablet breakpoints and touch targets',()=>{
    expect(stylesSource).toContain('@media(max-width:1100px)');
    expect(stylesSource).toContain('min-height:44px');
    expect(stylesSource).toContain('position:sticky;bottom:8px');
    expect(stylesSource).toContain('.mentor-lesson');
  });

  it('preserves mathematical line breaks for progressive hints',()=>{
    expect(stylesSource).toContain('.hint-box p');
    expect(stylesSource).toContain('white-space:pre-line');
  });
});
