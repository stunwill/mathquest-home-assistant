import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
import {describe, expect, it} from 'vitest';

const sourceDir = resolve(process.cwd(), 'src');
const mobileCss = readFileSync(resolve(sourceDir, 'student-mobile.css'), 'utf8');
const calendarCss = readFileSync(resolve(sourceDir, 'v0160.css'), 'utf8');
const worksheetCss = readFileSync(resolve(sourceDir, 'student-feedback.css'), 'utf8') + readFileSync(resolve(sourceDir, 'styles.css'), 'utf8');

describe('v0.40 student responsive layout contracts', () => {
  it('uses responsive breakpoints rather than device-name detection for phone navigation', () => {
    expect(mobileCss).toContain('@media(max-width:760px)');
    expect(mobileCss).toContain('@media(max-width:430px)');
    expect(mobileCss).toContain('.student-mobile-nav{display:grid');
    expect(mobileCss).not.toMatch(/iPhone|iPad 10th/i);
  });

  it('prevents known page-width overflow and reserves compact space for the fixed safe-area navigation', () => {
    expect(mobileCss).toContain('overflow-x:hidden');
    expect(mobileCss).toContain('overflow-x:clip');
    expect(mobileCss).toContain('env(safe-area-inset-bottom)');
    expect(mobileCss).toContain('padding:12px 14px calc(78px + min(env(safe-area-inset-bottom),16px))');
    expect(mobileCss).toContain('padding:4px 8px calc(2px + min(env(safe-area-inset-bottom),16px))');
  });

  it('keeps navigation touch targets and visible keyboard focus', () => {
    expect(mobileCss).toContain('min-height:48px');
    expect(mobileCss).toContain('.student-mobile-nav button:focus-visible');
    expect(mobileCss).toContain('outline:3px solid');
  });

  it('respects reduced motion', () => {
    expect(mobileCss).toContain('@media(prefers-reduced-motion:reduce)');
    expect(mobileCss).toContain('transition:none!important');
    expect(mobileCss).toContain('animation:none!important');
  });

  it('replaces the five-column phone calendar header with readable week navigation', () => {
    expect(calendarCss).toContain('.mq-cal-head{display:grid;grid-template-columns:auto auto minmax(0,1fr) auto auto');
    expect(calendarCss).toMatch(/@media\(max-width:760px\)[\s\S]*\.mq-cal-head\{grid-template-columns:auto minmax\(0,1fr\) auto\}/);
    expect(calendarCss).toMatch(/@media\(max-width:760px\)[\s\S]*\.mq-cal-head \.day-shift\{display:none\}/);
    expect(calendarCss).toMatch(/@media\(max-width:760px\)[\s\S]*\.mq-cal-days\{grid-template-columns:1fr;overflow:visible\}/);
  });

  it('keeps Story Adventure in one horizontal mobile selector without creating page overflow', () => {
    expect(mobileCss).toContain('.mq-adventure-grid{display:flex!important;overflow-x:auto');
    expect(mobileCss).toContain('scroll-snap-type:x proximity');
    expect(mobileCss).toContain('flex:0 0 82%');
  });

  it('does not replace the established tablet worksheet feedback rules', () => {
    expect(worksheetCss).toContain('.post-answer-backdrop{position:fixed;inset:0');
    expect(worksheetCss).toContain('.post-answer-scroll{min-height:0;overflow:auto');
    expect(worksheetCss).toContain('@media (min-width:900px) and (max-width:1200px) and (orientation:landscape)');
    expect(mobileCss).toContain('@media(min-width:761px)');
  });
});


describe('v0.47.1 keyboard-aware worksheet contracts', () => {
  it('groups the answer field and primary submit action for responsive layout', () => {
    const source = readFileSync(resolve(sourceDir, 'main.tsx'), 'utf8');
    expect(source).toContain('answer-action-group');
    expect(source).toContain('aria-label="Answer and submit"');
    expect(source).toContain('className="primary answer-submit"');
  });
  it('uses dynamic viewport sizing and a reduced-visual-viewport state', () => {
    expect(worksheetCss).toContain('100dvh');
    expect(worksheetCss).toContain('data-mq-keyboard=open');
    expect(worksheetCss).toContain('env(safe-area-inset-bottom)');
  });
  it('uses landscape width for the answer and submit group while stacking on phones', () => {
    expect(worksheetCss).toContain('@media (min-width:900px) and (max-width:1200px) and (orientation:landscape)');
    expect(worksheetCss).toContain('@media (max-width:760px)');
    expect(worksheetCss).toContain('grid-template-columns:1fr');
  });
});


describe('v0.47.2 mathematics-first worksheet contracts', () => {
  it('places the question before supporting tools and removes raw student difficulty metadata', () => {
    const source = readFileSync(resolve(sourceDir, 'main.tsx'), 'utf8');
    expect(source.indexOf('<h1>{q.prompt}</h1>')).toBeLessThan(source.indexOf('<QuestionTools question={q}'));
    expect(source).not.toContain('{q.topic} · level {q.level}');
  });
  it('keeps the answer and primary action grouped while treating skip as secondary', () => {
    const source = readFileSync(resolve(sourceDir, 'main.tsx'), 'utf8');
    expect(source).toContain('aria-label="Answer and submit"');
    expect(worksheetCss).toContain('.question-actions{display:flex;justify-content:flex-end');
    expect(worksheetCss).toContain('background:transparent;color:#7b5d16');
  });
  it('uses compact, labelled worksheet tools without removing support', () => {
    expect(worksheetCss).toContain('.react-question-tools>div:first-child button{min-height:44px');
    expect(worksheetCss).toContain('html[data-mq-keyboard=open] .react-question-tools');
    expect(readFileSync(resolve(sourceDir, 'question-tools.tsx'), 'utf8')).toContain('Read aloud');
    expect(readFileSync(resolve(sourceDir, 'question-tools.tsx'), 'utf8')).toContain('Scratchpad');
  });
  it('keeps diagnostic wording short and learner-safe', () => {
    const source = readFileSync(resolve(sourceDir, 'main.tsx'), 'utf8');
    expect(source).toContain('Six quick questions');
    expect(source).toContain('It is not an exam.');
    expect(source).not.toContain('placement evidence only');
  });
});
