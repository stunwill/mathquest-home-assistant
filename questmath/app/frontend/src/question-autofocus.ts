let activeQuestionId: string | null = null;

function modalIsOpen(): boolean {
  return Boolean(document.querySelector('.modal-backdrop, .lab-backdrop'));
}

function focusCurrentAnswer(): void {
  if (modalIsOpen()) return;
  const card = document.querySelector<HTMLElement>('.question-card[data-question-id]');
  if (!card) return;
  const questionId = card.dataset.questionId || null;
  if (!questionId || questionId === activeQuestionId) return;
  activeQuestionId = questionId;
  const input = card.querySelector<HTMLInputElement>('.answer-row input:not([disabled])');
  if (!input) return;
  window.requestAnimationFrame(() => {
    if (!modalIsOpen() && document.body.contains(input)) {
      input.focus({preventScroll: true});
      input.select();
    }
  });
}

export function setupQuestionAutofocus(): () => void {
  focusCurrentAnswer();
  const observer = new MutationObserver(focusCurrentAnswer);
  observer.observe(document.body, {childList: true, subtree: true});
  return () => observer.disconnect();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => setupQuestionAutofocus(), {once: true});
} else {
  setupQuestionAutofocus();
}
