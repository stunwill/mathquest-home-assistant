# MathQuest v0.47.1 Manual Acceptance Checklist

## iPad 10th generation, landscape, software keyboard

- [ ] Open a normal worksheet and reach a numeric-answer question.
- [ ] Tap the answer field and confirm the software keyboard opens.
- [ ] Confirm the question remains understandable, the complete answer field remains visible, and **Check answer** remains visible above the keyboard without manual recovery scrolling.
- [ ] Type an answer and submit by touch; repeat with Return/Enter where supported.
- [ ] Confirm the Answer → Feedback → Understand → Reflect → Continue sequence remains stable.
- [ ] Use Hint, Worked example and Math Mentor while the keyboard is open.
- [ ] Repeat with fraction/decimal and visual questions, then through Story Adventure where applicable.

## Regression checks

- [ ] iPad landscape with a physical keyboard preserves the spacious worksheet layout, focus and Enter submission.
- [ ] iPhone portrait keeps answer and primary action stacked and usable with the software keyboard.
- [ ] Home Assistant ingress has no horizontal overflow, keyboard overlap or safe-area regression.
- [ ] Focus order, labels, touch targets, visible focus and reduced-motion behaviour remain accessible.

**PENDING PHYSICAL DEVICE VALIDATION**. Automated reduced-viewport tests do not replace real iPadOS, iPhone or ingress testing.
