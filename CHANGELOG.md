# MathQuest Changelog

This is the authoritative project and GitHub changelog consumed by repository tooling and DevHub. Home Assistant user-facing release notes are maintained separately in `questmath/CHANGELOG.md`.

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
