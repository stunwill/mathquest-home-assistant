# MathQuest v0.37.0 Manual Acceptance

Use this checklist against the installed Home Assistant add-on after automated CI is green.

## Core learner flow

1. Start a normal learner session.
2. Confirm conventional number, algebra, measurement and space questions still render and submit normally.
3. Submit an incorrect answer and confirm another answer can be entered immediately without opening Math Mentor.
4. Save and exit, then resume the worksheet and confirm the current question and draft answer are preserved where applicable.

## Interactive fraction bar

1. Encounter a fraction-bar question.
2. Confirm the bar is divided into the stated number of equal parts.
3. Confirm parts can be selected using touch or mouse.
4. Confirm selected parts have a visible state that is not colour-only.
5. Submit a correct and incorrect selection and confirm backend scoring is correct.

## Interactive fraction number line

1. Encounter a fraction number-line question.
2. Confirm 0 and 1 are clear landmarks and internal intervals are equally spaced.
3. Confirm the requested internal fraction is not directly labelled.
4. Select an internal tick and submit it.
5. Confirm the selected-state position remains mathematically accurate in portrait and landscape layouts.

## Interactive ruler

1. Encounter a scaled ruler question.
2. Confirm labels and interval spacing agree mathematically.
3. Confirm the requested internal measurement is not directly labelled.
4. Select a ruler mark using touch and mouse.
5. Confirm correct and incorrect selections are scored correctly.

## Interactive grid references

1. Encounter a grid-reference selection question.
2. Confirm column letters and row numbers remain aligned with their cells.
3. Select the requested square directly on the grid.
4. Confirm selection remains usable on tablet portrait, tablet landscape and a reasonable mobile width.

## Mathematical reasoning

1. Encounter structured reasoning questions including operation selection, reasonableness or a conceptual statement.
2. Confirm distractors are plausible but only one answer is mathematically correct.
3. Encounter a find-the-mistake question and confirm it assesses the stated misconception rather than using trick wording.
4. Confirm conventional fluency questions still occur and reasoning has not replaced calculation practice.

## Math Mentor

1. Open Hint on each new interactive model.
2. Confirm the hint refers to the relevant representation, such as equal parts, intervals, ruler scale or grid coordinates.
3. Confirm the hint does not reveal the active answer.
4. Open Teach me and Worked example.
5. Confirm the worked example uses different values or references while teaching the same structure.
6. Confirm Math Mentor remains optional after an incorrect answer.

## Story Adventure

1. Start a Story Adventure.
2. Continue until a compatible interactive or reasoning question appears, or use a controlled test session if required.
3. Confirm story framing does not alter the underlying mathematical answer interaction.
4. Confirm the question still scores through the normal backend route.
5. Confirm Story Adventure completion itself does not create mastery evidence.

## Parent and regression checks

1. Confirm Parent Dashboard loads.
2. Confirm Parent Learning Intelligence loads or degrades independently if optional data is unavailable.
3. Confirm Parent Tests remain isolated from learner mastery and adaptive evidence.
4. Confirm interactive whole-number number lines from v0.36.0 still work.
5. Confirm the login screen still defaults to `sienna` with a blank password.
6. Confirm normal expired MathQuest authentication returns to login rather than a dead-end Invalid session screen.
7. Restart the Home Assistant add-on and confirm worksheet history, learning evidence and settings persist.
