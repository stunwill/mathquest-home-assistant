# MathQuest v0.39.0 Manual Acceptance

Status: **Not yet performed**

Do not mark these items complete from automated CI alone.

## Representative learner sessions

- [ ] Generate at least three normal Number & Algebra worksheets on the deployed Home Assistant add-on.
- [ ] Confirm the worksheet does not contain several mathematically near-identical calculations with only the numbers changed.
- [ ] Confirm direct addition/subtraction still appears when useful and uses appropriate Grade 5 number size/complexity.
- [ ] Confirm an intentionally easy review/retrieval item can still appear when the learning purpose justifies it.
- [ ] Confirm the session is not made artificially difficult merely to maximise variety.
- [ ] Confirm reasonableness, algebra, contextual, interactive and calculation work can coexist naturally where selected by the adaptive engine.
- [ ] Complete several answers and start another worksheet; confirm very recently repeated structures are reduced without preventing a genuine learning need from recurring.

## Adaptive continuity

- [ ] Inspect learner-facing learning-purpose labels after a generated worksheet and confirm they make sense for the final questions.
- [ ] Confirm no more than the established challenge allowance appears in a short session.
- [ ] Confirm review/consolidation work remains available after prior errors, support dependence or retention need.
- [ ] Confirm Story Adventure preserves the same mathematical difficulty and learning purpose rather than using an easier parallel generator.
- [ ] Confirm Parent Tests are unaffected by session-quality recomposition.

## Tutoring and feedback regression

- [ ] On iPad 10th generation landscape, answer a typed question with Enter and confirm the v0.38 feedback dialog appears immediately.
- [ ] Press Enter again and confirm Continue/Retry behaviour remains correct.
- [ ] Use Hint, Teach me/Math Mentor and a worked example on representative questions; confirm support matches the active method and does not reveal a retry answer prematurely.
- [ ] Complete at least one interactive fraction/number-line/ruler/grid question and confirm the shared feedback path still works.

## Responsive / Home Assistant

- [ ] Check iPad landscape.
- [ ] Check iPad portrait.
- [ ] Check a representative iPhone viewport.
- [ ] Check desktop/Home Assistant ingress.
- [ ] Confirm no horizontal overflow or blocked primary actions.
- [ ] Confirm worksheet history still displays Melbourne local time.
- [ ] Restart the add-on and confirm existing learner history/evidence is preserved.

## Parent experience

- [ ] Open Parent Learning Intelligence after learner practice.
- [ ] Confirm current focus/recommendation is plausible relative to the final worksheet questions.
- [ ] Confirm Parent Test activity has not contaminated learner mastery or daily-learning state.

## Notes

Record any repeated structure, tutoring mismatch, unexpectedly easy/hard session or responsive defect with the exact worksheet/question so it can become deterministic regression evidence in a later release.
