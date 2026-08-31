# MathQuest v0.36.0 Manual Acceptance

Use this checklist against the installed Home Assistant add-on after automated CI is green.

## Login

1. Open MathQuest from the Home Assistant sidebar.
2. Confirm the username field contains `sienna`.
3. Confirm the password field is empty and focused.
4. Sign in as the student.
5. Sign out and confirm the normal login form returns with `sienna` prefilled.
6. Replace `sienna` with the configured parent username and confirm parent login still works.

## Session recovery

1. Sign in with a valid MathQuest account.
2. Simulate token expiry or use a deliberately expired MathQuest token.
3. Reopen MathQuest and confirm it returns directly to the normal login form.
4. Confirm the generic `Something went wrong - Invalid session` state is not used for normal MathQuest authentication expiry.
5. Confirm `sienna` is prefilled and the password is blank.
6. Verify a plain-text/non-JSON Home Assistant ingress 401 remains a distinct recovery message and does not automatically clear a valid MathQuest token.
7. Repeat from Home Assistant mobile, desktop, a new tab/window and after a normal page refresh.
8. Restart the add-on and verify valid persistent signing-secret behaviour remains unchanged.

## Interactive number lines

1. Start Number or Number & Algebra practice and locate several number-line location questions.
2. Confirm the answer is selected directly by tapping/clicking a tick on the line.
3. Confirm no separate numerical multiple-choice buttons reveal the requested answer.
4. Confirm the requested internal value is not already labelled on its target tick.
5. Confirm selected-state feedback is clear before pressing Check answer.
6. Submit a correct position and an incorrect position and confirm normal scoring/retry/evidence behaviour.
7. Check the same interaction with a desktop pointer and Home Assistant mobile touch input.
8. Confirm the line remains mathematically aligned on narrow screens and can scroll safely if needed.

## Adaptive Number and Algebra difficulty

1. Generate multiple Number & Algebra worksheets for the established learner profile.
2. Confirm simple additions comparable to `20 + 28` are uncommon when the existing evidence supports progression.
3. Confirm richer structures such as regrouping, missing numbers, patterns, inverse operations and other existing Grade 5 question families remain present.
4. Confirm foundational questions can still appear when their payload shows review, consolidation or retrieval purpose.
5. Confirm Parent Tests are unchanged by this quality policy.

## Regression

Confirm Parent Dashboard, Parent Learning Intelligence, Story Adventure, Math Mentor, hints, worked examples, Visual Mathematics, worksheet resume, Parent Tests, backup/restore and Home Assistant learning endpoints continue to operate normally.
