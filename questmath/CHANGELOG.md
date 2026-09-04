## v0.39.0 - Session Learning Quality and Adaptive Continuity

- MathQuest now checks the final learner worksheet as a whole for repeated mathematical structures, accidental low-complexity work and recently overused question patterns.
- Added multidimensional arithmetic difficulty metadata so direct calculations distinguish number size and regrouping demand rather than treating all addition or subtraction as equivalent.
- Preserved purposeful review, consolidation and retrieval while diversifying accidental near-duplicates.
- Recent answered Daily Practice and Story Adventure questions influence variety without creating a separate history or mastery system.
- Adaptive learning purpose and evidence annotations are refreshed after final worksheet-quality replacements so parent-facing learning information matches the mathematics actually shown.
- Parent Tests remain isolated and the existing one-question challenge limit is preserved.
- Release validation now derives the active backend module from the runtime configuration and checks the frontend package version alongside add-on, frontend display, backend, README and changelog versions.

## v0.38.1 - Number & Algebra Quality and Melbourne Time

- Reduced repeated low-complexity Number & Algebra addition/subtraction by upgrading smaller direct calculations to larger Grade 5-appropriate place-value work.
- Equal-groups questions now ask for the numerical total instead of only asking which operation should be used.
- Worksheet history now displays `Australia/Melbourne` local time and observes AEST/AEDT daylight-saving changes.
- Added regression tests for arithmetic difficulty, equal-groups answers and timezone conversion.

## v0.38.0 - iPad Landscape Feedback and Worksheet UX

- Replaced below-question answer results with an accessible post-answer feedback dialog so correct/incorrect status, concise mathematical support, reflection and the next action are immediately visible without page scrolling.
- Preserved retry-first learning: retryable incorrect answers do not reveal terminal working, Math Mentor remains optional, and Retry clears the previous response and returns focus to the typed-answer field.
- Made the physical-keyboard flow explicit: Enter submits a typed answer, the feedback primary action receives focus, and Enter continues or retries without requiring touch.
- Added rapid-Enter protection so a fast second key press cannot submit the same answer twice or skip a question.
- Moved learner confidence reflection into the feedback dialog while preserving the existing confidence-evidence endpoint and Parent Test isolation.
- Added restrained, non-blocking correct-answer celebration with explicit text/icon state and `prefers-reduced-motion` support.
- Added an iPad 10th-generation landscape layout band that reduces unnecessary header/card/side-panel space while preserving readable question typography and existing portrait/mobile behaviour.
- Kept whole-number number lines, fraction bars, fraction number lines, rulers, grid references, choices, structured reasoning and Story Adventure on the shared worksheet answer and feedback architecture.
- Added frontend regression coverage for keyboard submission/continuation, retry focus, optional Math Mentor, confidence evidence, focus trapping, rapid Enter, touch-first interactive answers, Story Adventure and viewport-fixed feedback.

# MathQuest Home Assistant Changelog

Concise user-facing release notes for the Home Assistant add-on. The detailed project/GitHub changelog is maintained at the repository root in `CHANGELOG.md`.

## v0.37.1 - Duplicate-Safe Reasoning Mix
- Prevent duplicate question identities when the v0.37.0 reasoning mix replaces a worksheet question.
- Preserve existing worksheet variety and retry the replacement generator before leaving the original question unchanged.

## v0.37.0 - Richer Interactive Mathematics and Mathematical Reasoning

- Interactive fractions now include selecting parts of a fraction bar and locating fractions directly on a 0-to-1 number line.
- Measurement practice can include interactive scaled rulers where the learner must work out the value of each interval before selecting the requested mark.
- Space practice can include selectable grid references so the learner chooses the actual square rather than typing a coordinate from the prompt.
- Added more mathematical reasoning, including operation selection, reasonableness, perimeter-versus-area understanding, symmetry statements and age-appropriate find-the-mistake questions.
- New interactive questions remain backend-authoritative and feed the same attempts, learning evidence, adaptive difficulty and misconception evidence as conventional questions.
- Math Mentor now gives representation-specific guidance and different-number worked examples for the new interactive models while keeping retry-first answers and optional tutoring.
- Story Adventure continues to use the same adaptive worksheet and evidence path, so compatible interactive mathematics works there without a separate story question engine.
- Preserved interactive whole-number number lines, adaptive suppression of unnecessarily basic arithmetic, session-expiry recovery, Parent Dashboard reliability, Parent Tests and Home Assistant learning APIs.

## v0.36.0 - Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Number-line location questions can now be answered by tapping or clicking the correct tick directly on the number line instead of selecting a separate number button that repeats the requested value.
- Adaptive Number & Algebra practice now recognises overly simple two-digit additions such as `20 + 28` and reduces them when learning evidence shows the student is ready for richer work, while still allowing purposeful review and consolidation.
- New installs default the student username to `sienna`, and the login screen pre-fills `sienna` while leaving the password blank and editable parent login available.
- Expired MathQuest sessions now return automatically to the normal login screen instead of leaving the learner on a `Something went wrong - Invalid session` screen.
- Kept Home Assistant ingress failures separate from MathQuest token expiry so an ingress problem does not automatically remove otherwise valid MathQuest credentials.
- Preserved Story Adventure, Math Mentor, Parent Learning Intelligence, Parent Tests, Home Assistant learning APIs and local-first operation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

- Fixed a Parent Learning Intelligence frontend crash that could stop the Parent Dashboard rendering even though its API calls succeeded.
- Parent Dashboard startup failures now show a retryable error instead of remaining indefinitely on a MathQuest splash screen.
- Backups and optional learning-intelligence sections no longer block the core Parent Dashboard from loading.
- Preserved Home Assistant ingress, authentication, Parent Tests and learner functionality.

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
