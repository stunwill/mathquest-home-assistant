import {readFileSync} from 'node:fs';
import {describe, expect, it} from 'vitest';

const mobileCss = readFileSync(new URL('./student-mobile.css', import.meta.url), 'utf8');
const calendarCss = readFileSync(new URL('./v0160.css', import.meta.url), 'utf8');
const worksheetCss = readFileSync(new URL('./student-feedback.css', import.meta.url), 'utf8') + readFileSync(new URL('./styles.css', import.meta.url), 'utf8');

describe('v0.40 student responsive layout contracts', () => {
  it('uses responsive breakpoints rather than device-name detection for phone navigation', () => {
    expect(mobileCss).toContain('@media(max-width:760px)');
    expect(mobileCss).toContain('@media(max-width:430px)');
    expect(mobileCss).toContain('.student-mobile-nav{display:grid');
    expect(mobileCss).not.toMatch(/iPhone|iPad 10th/i);
  });

  it('prevents known page-width overflow and reserves space for the fixed safe-area navigation', () => {
    expect(mobileCss).toContain('overflow-x:hidden');
    expect(mobileCss).toContain('overflow-x:clip');
    expect(mobileCss).toContain('env(safe-area-inset-bottom)');
    expect(mobileCss).toMatch(/padding:12px 14px calc\(94px \+ env\(safe-area-inset-bottom\)\)/);
  });

  it('keeps navigation touch targets and visible keyboard focus', () => {
    expect(mobileCss).toContain('min-height:50px');
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
    expect(worksheetCss).toContain('post-answer-feedback');
    expect(worksheetCss).toMatch(/orientation:\s*landscape|landscape/);
    expect(mobileCss).toContain('@media(min-width:761px)');
  });
});
