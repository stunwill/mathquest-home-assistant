# MathQuest Home Assistant Changelog

Concise user-facing release notes for the Home Assistant add-on. The detailed project/GitHub changelog is maintained at the repository root in `CHANGELOG.md`.

## v0.36.0 - Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Number-line location questions can now be answered by tapping or clicking the correct tick directly on the number line instead of selecting a separate number button.
- Number & Algebra practice now recognises overly simple two-digit additions such as `20 + 28` and reduces them when learning evidence shows the student is ready for richer work, while still allowing purposeful review and consolidation.
- New installs default the student username to `sienna`, and the login screen pre-fills `sienna` while leaving the password blank and editable parent login available.
- Expired MathQuest sessions now return automatically to the normal login screen instead of leaving the learner on a `Something went wrong - Invalid session` screen.
- Kept Home Assistant ingress failures separate from MathQuest token expiry so an ingress problem does not automatically remove otherwise valid MathQuest credentials.
- Preserved Story Adventure, Math Mentor, Parent Learning Intelligence, Parent Tests, Home Assistant learning APIs and local-first operation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

- Fixed a Parent Learning Intelligence frontend crash that could stop the Parent Dashboard rendering even though its API calls succeeded.
- Parent Dashboard startup failures now show a retryable error instead of remaining indefinitely on the MathQuest loading screen.
- Backups and optional learning-intelligence sections no longer block the core Parent Dashboard from loading.
- Preserved Home Assistant ingress, Daily Learning, Parent Tests, local-first operation, authentication and existing learner functionality.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

- Added a compact Home Assistant learning summary showing daily completion, current learning focus, review status, support needs and a weekly learning summary.
- Daily Practice and Story Adventure count as daily learning only after meaningful completed learner work with answered questions.
- Parent Tests and abandoned no-evidence sessions do not count as daily learning.
- Added parent-friendly signals for review due, persistent support dependence, repeated misconceptions and meaningful progress using MathQuest's existing learning evidence.
- Added stable read-only Home Assistant endpoints and identifiers designed for dashboards and automations.
- Added standard Home Assistant REST sensor and reminder automation examples without requiring HACS.
- Preserved local-first privacy and existing learner experiences.

## v0.34.0 - Story Adventure Expansion and Purposeful Daily Learning

- Story Adventure now uses the same adaptive learning engine as Daily Practice, so the maths remains purposeful and matched to current learning needs.
- Added short staged adventures for 5, 10 and 15-minute sessions with lightweight mission progress.
- Preserved retry-first answers, optional Hint, Teach me, Worked example and Math Mentor support.
- Story Adventure answers contribute to the existing learning evidence, while adventure completion itself does not count as mastery.
- Parent Tests remain isolated from Story Adventure and learner evidence.

## v0.33.0 - Adaptive Daily Learning

- Added adaptive daily practice that balances current learning, consolidation, spaced review and limited challenge from learner evidence.
- Progression now requires repeated independent success and slows when support use or misconceptions show more consolidation is needed.
- Parent Tests remain isolated from adaptive practice decisions.

## v0.32.3 - Grade 5 Method-First Math Mentor

- Improved Math Mentor teaching for written multiplication, partition division, decimal hundredths, perimeter and area.
- Worked examples now demonstrate the same method using different values from the active question.

## v0.32.2 - Grade 5 Algebra Variety

- Added more Grade 5 Algebra variety including patterns, unknowns, substitution, mystery numbers, unknown-start problems and reverse multiplication.
- Kept the new question styles mixed with existing Algebra practice rather than replacing it.

## v0.32.1 - Worksheet Learning Quality Corrective Release

- Kept incorrect answers retry-first, with tutoring support optional.
- Improved worked-example matching and reduced overly simple arithmetic once learner evidence supports harder work.
- Improved question-family and fraction number-line safeguards.

## v0.32.0 - Parent Learning Intelligence

- Added parent-friendly learning summaries, independent versus supported success, evidence confidence and prioritised recommendations.
- Added misconception, prerequisite, retention and review-due visibility while preserving Parent Test isolation.

## v0.31.0 - Tablet Learning and Math Mentor Refinement

- Improved tablet worksheet use, question-specific tutoring and progressive hints.
- Preserved retry-first behaviour, keyboard autofocus and Visual Mathematics.

Historical release details remain available through GitHub Releases and repository history.