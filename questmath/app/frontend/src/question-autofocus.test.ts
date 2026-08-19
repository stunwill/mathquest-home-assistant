import {afterEach, describe, expect, it, vi} from 'vitest';

import {setupQuestionAutofocus} from './question-autofocus';

afterEach(() => {
  document.body.innerHTML = '';
  vi.restoreAllMocks();
});

describe('question autofocus', () => {
  it('focuses the text input when a new question is rendered', async () => {
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(callback => {
      callback(0);
      return 1;
    });
    document.body.innerHTML = '<section class="question-card" data-question-id="1"><div class="answer-row"><input value="" /></div></section>';
    const stop = setupQuestionAutofocus();
    expect(document.activeElement).toBe(document.querySelector('input'));

    document.body.innerHTML = '<section class="question-card" data-question-id="2"><div class="answer-row"><input value="" /></div></section>';
    await Promise.resolve();
    expect(document.activeElement).toBe(document.querySelector('input'));
    stop();
  });

  it('does not steal focus while a modal is open', () => {
    vi.spyOn(window, 'requestAnimationFrame').mockImplementation(callback => {
      callback(0);
      return 1;
    });
    document.body.innerHTML = '<div class="modal-backdrop"><button id="modal-button">Close</button></div><section class="question-card" data-question-id="3"><div class="answer-row"><input /></div></section>';
    const button = document.querySelector<HTMLButtonElement>('#modal-button')!;
    button.focus();
    const stop = setupQuestionAutofocus();
    expect(document.activeElement).toBe(button);
    stop();
  });
});
