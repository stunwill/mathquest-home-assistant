import React, {useEffect, useId, useRef} from 'react';
import {CheckCircle2, ChevronRight, Lightbulb, RotateCcw, Sparkles} from 'lucide-react';

type PostAnswerFeedbackModalProps = {
  feedback: any;
  working?: string | null;
  reflection?: React.ReactNode;
  testFeedback?: React.ReactNode;
  primaryLabel: string;
  onPrimary: () => void;
  onOpenMentor?: () => void;
  primaryBusy?: boolean;
};

export function PostAnswerFeedbackModal({feedback, working, reflection, testFeedback, primaryLabel, onPrimary, onOpenMentor, primaryBusy=false}: PostAnswerFeedbackModalProps) {
  const titleId = useId();
  const descriptionId = useId();
  const primaryRef = useRef<HTMLButtonElement>(null);
  const dialogRef = useRef<HTMLElement>(null);
  const correct = Boolean(feedback?.correct);
  const retry = Boolean(feedback?.retry_allowed);

  useEffect(() => {
    primaryRef.current?.focus({preventScroll: true});
  }, [feedback]);

  useEffect(() => {
    const keydown = (event: KeyboardEvent) => {
      if (event.key !== 'Tab' || !dialogRef.current) return;
      const focusable = Array.from(dialogRef.current.querySelectorAll<HTMLElement>('button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'));
      if (!focusable.length) return;
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    document.addEventListener('keydown', keydown);
    return () => document.removeEventListener('keydown', keydown);
  }, []);

  return <div className="post-answer-backdrop" data-post-answer-feedback="true">
    <section
      ref={dialogRef}
      className={'post-answer-modal '+(correct?'is-correct':'is-incorrect')}
      role="dialog"
      aria-modal="true"
      aria-labelledby={titleId}
      aria-describedby={descriptionId}
    >
      <header className="post-answer-result">
        <div className="post-answer-icon" aria-hidden="true">
          {correct?<CheckCircle2 size={34}/>:<Lightbulb size={34}/>} 
          {correct&&<span className="post-answer-sparkle"><Sparkles size={20}/></span>}
        </div>
        <div>
          <p className="eyebrow">{correct?'NICE WORK':'LEARNING MOMENT'}</p>
          <h2 id={titleId}>{correct?'Correct answer':'Incorrect answer'}</h2>
          <p id={descriptionId}>{correct?'You got it. Take a moment to notice the method, then keep going.':retry?'That answer did not match yet. Use the idea below, then have another go.':'That answer did not match. Review the explanation before continuing.'}</p>
        </div>
      </header>

      <div className="post-answer-scroll">
        {feedback?.message&&<section className="post-answer-message" aria-label="Result message"><b>{correct?'What went well':'What to notice'}</b><p>{feedback.message}</p></section>}
        {!retry&&working&&<section className="post-answer-explanation" aria-label="Mathematical explanation"><b>Why</b><p>{working}</p></section>}
        {retry&&onOpenMentor&&<section className="post-answer-mentor"><div><b>Want another way to think about it?</b><span>Math Mentor can guide you without making help a required step.</span></div><button type="button" onClick={onOpenMentor}>Math Mentor</button></section>}
        {testFeedback}
        {reflection&&<section className="post-answer-reflection" aria-label="Self reflection">{reflection}</section>}
      </div>

      <footer className="post-answer-actions">
        <span className="post-answer-keyboard-hint">Press Enter to {retry?'try again':'continue'}</span>
        <button ref={primaryRef} type="button" className="primary" disabled={primaryBusy} onClick={onPrimary}>
          {retry?<RotateCcw size={19}/>:<ChevronRight size={19}/>} {primaryLabel}
        </button>
      </footer>
    </section>
  </div>;
}
