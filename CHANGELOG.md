## v0.38.0 - iPad Landscape Feedback and Worksheet UX

- Replaced below-question post-answer results with a reusable feedback dialog designed around the iPad 10th-generation landscape worksheet workflow.
- Made correct/incorrect status, concise explanation, confidence reflection and the primary next action visible independently of page scroll.
- Preserved retry-first incorrect-answer behaviour, terminal-answer hiding during retry, existing misconception/mastery evidence, optional Math Mentor and Parent Test isolation.
- Added keyboard-first continuation and retry, focus restoration, dialog focus containment and rapid-Enter protection.
- Added restrained success motion, explicit non-colour result semantics and reduced-motion support.
- Tightened landscape tablet spacing so the mathematics question receives more of the viewport without shrinking core text or regressing portrait/mobile layouts.
- Reused the same result experience for typed, choice, interactive mathematics and Story Adventure questions.
- Added regression coverage for the result-dialog state machine, keyboard/touch operation, reflection evidence, responsive layout contracts and shared Story Adventure/interactive paths.

## v0.37.1 - Duplicate-Safe Reasoning Mix
- Prevent the richer interactive-question mix from replacing a question with an identity already present in the worksheet.
- Preserve duplicate-safe worksheet generation and add regression coverage for repeated reasoning candidates.

# MathQuest Changelog

This is the authoritative project and GitHub changelog consumed by repository tooling and DevHub. Home Assistant user-facing release notes are maintained separately in `questmath/CHANGELOG.md`.

## v0.37.0 - Richer Interactive Mathematics and Mathematical Reasoning

- Extended first-class interactive mathematics beyond whole-number number lines with fraction-bar selection, fraction number-line location, scaled ruler reading and selectable grid-reference questions.
- Kept every new interaction backend-authoritative by submitting a mathematical value or grid reference through the existing worksheet answer, attempt and learning-evidence path.
- Added target-hiding safeguards for fraction number lines and scaled rulers so the requested answer must be inferred from equal partitions or scale rather than read directly from the visual.
- Added structured Grade 5 mathematical reasoning including operation selection, reasonableness, perimeter-versus-area concepts, symmetry statements and age-appropriate error analysis.
- Reused the existing misconception-evidence architecture for regrouping/place-value error analysis instead of introducing a separate reasoning taxonomy.
- Added a controlled reasoning mix to learner worksheets while preserving purposeful review, consolidation, spaced retrieval and Parent Test isolation.
- Extended Math Mentor with representation-specific guidance and different-number worked examples for the new interactive models while preserving retry-first answers and optional tutoring.
- Kept Story Adventure on the same adaptive worksheet, answer-validation and evidence architecture so compatible interactive questions work without Story Adventure-only mathematics.
- Added reusable accessible touch/mouse/keyboard-focus answer components with selected-state feedback and responsive tablet/mobile layouts.
- Updated the product roadmap, DevHub metadata, release documentation and runtime validation for v0.37.0 while preserving all v0.36.0 session, login and interactive-number-line behaviour.

## v0.36.0 - Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Added first-class interactive number-line location questions so learners answer by selecting a tick on the line instead of choosing a button that repeats the requested value.
- Kept number-line correctness backend-authoritative by submitting the selected numeric position through the existing answer-validation and learning-evidence path.
- Added child-friendly mouse, keyboard-focus and touch targets, responsive number-line rendering and non-revealing unlabelled target positions.
- Extended worksheet-quality logic to recognise straightforward two-digit additions such as `20 + 28` that previously escaped the `≤12` trivial-arithmetic safeguard.
- Made suppression evidence-aware: learners ready for progression receive richer replacement questions, while purposeful review, consolidation and retrieval remain available.
- Changed new-install student username defaults and the login form convenience value to `sienna`; passwords remain blank and parent usernames remain editable.
- Retained the existing 24-hour MathQuest token lifetime while treating expired/invalid MathQuest authentication as a normal transition back to login rather than a generic `Invalid session` failure screen.
- Preserved the v0.35.1 distinction between MathQuest JSON authentication failures and Home Assistant ingress/proxy authentication failures so ingress problems do not automatically destroy valid MathQuest credentials.
- Preserved Parent Dashboard reliability, Story Adventure's adaptive-learning integration, Math Mentor, Parent Test isolation, Home Assistant learning APIs and local-first operation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

- Fixed a React hook-order crash in Parent Learning Intelligence that could leave the parent experience blank or apparently stuck even while all parent API requests returned successfully.
- Made Parent Dashboard bootstrap failures visible and retryable instead of allowing required request failures to leave an indefinite MathQuest splash screen.
- Limited blocking Parent Dashboard startup data to the dashboard and worksheet settings, while backups and learning-intelligence enhancements now degrade independently.
- Added a regression test covering the real loading transition from no Parent Learning Intelligence data to populated data.
- Confirmed MathQuest Home Assistant ingress remains configured through the standard add-on ingress contract. The observed Home Assistant `/ingress/validate_session` 401 is not produced by a MathQuest route and is therefore not treated as the application root cause.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

- Added a compact backend-authoritative Home Assistant parent-learning summary using existing Parent Learning Intelligence, adaptive-learning purposes, retention, support dependency and misconception evidence.
- Added `/api/ha/learning` and `/api/ha/weekly-summary` while retaining existing `/api/ha/stats` and `/api/ha/summary` compatibility endpoints.
- Added stable Home Assistant concept identifiers for daily learning, current focus, review status, support status and weekly summary without worksheet/question/date-specific IDs.
- Daily Practice and Story Adventure can satisfy daily learning only when a learner worksheet is completed with answered-question evidence.
- Parent Tests, opening MathQuest, starting a worksheet and abandoned no-evidence sessions do not satisfy daily learning completion.
- Separated actual active minutes from configured timed-session target minutes to avoid false precision.
- Added current-focus details including skill, curriculum area, outcome, learning purpose, recommendation reason and evidence confidence.
- Added conservative review-due, persistent-support, repeated-misconception and meaningful-progress signals driven by accumulated learning evidence.
- Added notification-ready alert payloads without introducing hard-coded reminder schedules or noisy per-question notifications.
- Added a seven-day parent summary prioritising learning days, learning time, secure/support-needed skills, review state, misconceptions, support dependency and recommended focus.
- Preserved local-first privacy, Parent Dashboard alignment, Story Adventure evidence integrity and Parent Test isolation.

## v0.34.0 - Story Adventure Expansion and Purposeful Daily Learning

- Rebuilt Story Adventure as a presentation layer over MathQuest's backend-authoritative adaptive learning engine instead of replacing selected questions with a separate story generator.
- Preserved each selected question's skill, prompt, answer, difficulty band, learning purpose and Visual Mathematics payload while adding adventure mission, stage, context and progress metadata.
- Added reusable mission stages and 5, 10 and 15-minute Story Adventure entry points using the same timed adaptive session service as normal learner practice.
- Preserved prerequisite routing, consolidation, misconception repair, spaced retrieval, current practice and controlled challenge decisions inside Story Adventure.
- Kept incorrect answers retry-first, with Hint, Teach me, Worked example and Math Mentor remaining optional support.
- Kept Story Adventure answers in the existing learning-evidence and mastery architecture while ensuring adventure completion itself is not mastery evidence.
- Preserved Parent Test isolation.

## v0.33.0 - Adaptive Daily Learning

- Added Adaptive Daily Learning using accumulated learner evidence to balance current learning, consolidation, spaced review and limited challenge.
- Added controlled progression requiring repeated independent success before challenge increases.
- Made progression support-aware and misconception-aware.
- Integrated spaced-retrieval evidence and preserved Parent Test isolation.

## v0.32.3 - Grade 5 Method-First Math Mentor

- Expanded method-first tutoring for written multiplication, partition division, decimal hundredths, perimeter and area.
- Added dynamically generated worked examples using different values while preserving the same method.
- Preserved progressive hints and Grade 5 difficulty safeguards.

## v0.32.2 - Grade 5 Algebra Variety

- Added patterns, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- Mixed new structures into the existing Algebra pool and added structural-diversity safeguards.

## v0.32.1 - Worksheet Learning Quality Corrective Release

- Preserved immediate retry after incorrect answers while keeping tutoring optional.
- Improved worked-example alignment and reduced unnecessary trivial arithmetic once learner evidence supports progression.
- Preserved fraction number-line and visual-quality safeguards.

## v0.32.0 - Parent Learning Intelligence

- Added plain-language parent learning summaries, independent versus supported success, evidence confidence, prioritised recommendations, misconception grouping, prerequisite visibility and retention reporting.
- Added 7, 30 and 90-day learning comparisons while preserving Parent Test isolation.

## v0.31.0 - Tablet Learning and Math Mentor Refinement

- Improved tablet worksheet UX, question-specific tutoring, progressive hints and higher-value Number practice.
- Preserved Visual Mathematics, retry-first behaviour and keyboard autofocus.

For earlier release history, see repository tags/releases and the retained detailed add-on changelog history in `questmath/CHANGELOG.md`.
