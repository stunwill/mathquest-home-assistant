# MathQuest v0.38.0 Manual Acceptance

Status: **Not yet performed on Sienna's real iPad.**

Primary device: iPad 10th generation, landscape orientation, physical keyboard attached where available.

The release must not be described as having passed real-device acceptance until these checks have actually been completed and reported.

## Required iPad acceptance checklist

- [ ] 1. Open MathQuest on an iPad 10th generation in landscape orientation.
- [ ] 2. Start a normal Daily Practice worksheet.
- [ ] 3. Answer a typed question using the physical keyboard.
- [ ] 4. Press Enter.
- [ ] 5. Confirm the correct/incorrect result is immediately visible without scrolling the worksheet page.
- [ ] 6. Confirm the feedback dialog is visually engaging, readable and clearly distinguishes the result without relying only on colour.
- [ ] 7. Confirm the mathematical explanation is relevant to the actual question and does not expose an answer prematurely when a retry is expected.
- [ ] 8. Complete the optional self-reflection/confidence interaction and confirm it feels quick rather than form-like.
- [ ] 9. For a correct answer, press Enter again.
- [ ] 10. Confirm the next question loads and an ordinary typed-answer field is ready for keyboard input.
- [ ] 11. Submit an incorrect answer that permits another attempt.
- [ ] 12. Confirm the incorrect-answer experience supports retry without punitive motion or forced tutoring.
- [ ] 13. Press Enter/Retry and confirm the previous answer is cleared and focus returns to the answer field.
- [ ] 14. Test Math Mentor from the feedback experience and confirm it remains optional unless backend learning logic explicitly requires support.
- [ ] 15. Test an interactive mathematics question using touch, including at least one fraction/ruler/number-line/grid interaction when available.
- [ ] 16. Test a Story Adventure question and confirm it uses the same result experience.
- [ ] 17. Confirm no important question, answer or primary-action controls fall below the visible landscape viewport during the ordinary workflow.
- [ ] 18. Rotate to portrait and confirm the worksheet remains usable and readable.
- [ ] 19. Exit and resume an interrupted worksheet, confirming the expected question and saved state are restored.
- [ ] 20. Complete a worksheet and confirm scoring, skipped-question handling and completion behaviour remain correct.

## Additional regression checks

- [ ] Check an iPhone/mobile-width layout for modal fit, readable content and touch targets.
- [ ] Check a normal desktop browser layout for unintended spacing or modal regressions.
- [ ] With Reduce Motion enabled in iPad accessibility settings, confirm correct-answer feedback remains clear without celebratory animation.
- [ ] With rapid Enter presses, confirm the same answer is not submitted twice and a question is not skipped.
- [ ] Confirm multiple-choice and structured reasoning questions show the same result dialog.
- [ ] Confirm Parent Test question notes still appear in the post-answer flow and do not record learner confidence/mastery evidence.
