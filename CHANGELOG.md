## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

- Replaced the student mobile scroll-to-anchor navigation model with real Home, Adventure, Worksheets and Progress destinations.
- Simplified Home so current learning, Best Next Step, learner-safe extra practice and compact destination previews no longer compete with the complete Adventure, worksheet-history and Progress experiences.
- Distinguished untouched worksheets as Ready to Start from genuinely resumed Continue Learning work.
- Removed student-facing intervention terminology, raw independent/support percentages, adaptive mode labels and curriculum outcome codes while preserving the underlying learning evidence and session services.
- Changed learner-facing Review due wording to Ready to review and hid zero-value Progress summaries.
- Grouped Progress skills under one concise learner-state explanation and removed raw success/support percentages from the student Progress surface.
- Moved full Story Adventure ownership to Adventure, full worksheet history to Worksheets, and Weekly Activity to Progress while preserving Story Adventure's existing adaptive session contract.
- Replaced the old student Home streak/accuracy/question-count/highest-level and Skill Map emphasis with concise learning guidance and destination previews.
- Kept the existing v0.41 learning-state derivation, adaptive thresholds, recommendation logic, review scheduling, prerequisites, Math Mentor, hints, worked examples and Parent Learning Intelligence unchanged.
- Added regression coverage for destination navigation, Ready to Start semantics, learner-safe extra-practice wording, Ready to review language, grouped Progress and learner-friendly weekly activity.

## v0.41.0 - Student Learning Progress & Guidance

- Added a student-facing learning-state layer derived from existing outcome mastery, adaptive progression, support and spaced-retrieval evidence rather than creating a second mastery score.
- Added learner-readable states for Not enough evidence yet, Practising, Building confidence, Getting stronger, Ready for a challenge and Review due.
- Kept Ready for a challenge tied to the existing Adaptive Daily Learning `ready_to_progress` decision, including its repeated independent-success and support-dependency thresholds.
- Added a persistent Student Progress destination that groups learning by learner meaning instead of exposing raw levels and accuracy as the primary student experience.
- Replaced technical student Best Next Step reasons with backend-derived "Why this?" explanations for diagnostics, prerequisite routing, spaced review and current practice.
- Explained spaced retrieval as purposeful review rather than failure and recognised support-heavy eventual success without treating it as independent mastery.
- Kept detailed evidence optional for the student while preserving full Parent Learning Intelligence, misconception evidence and Parent Test isolation.
- Added deterministic backend and frontend regression coverage for insufficient evidence, supported success, progression readiness, review due, recommendation explanations and no parallel mastery score.
- Preserved worksheet generation, adaptive composition, mastery thresholds, Math Mentor, hints, worked examples, Story Adventure selection and the v0.38 keyboard-first feedback flow.

## v0.40.0 - Student Mobile Home, Navigation & Responsive UX

- Reorganised the student mobile experience around current learning action so unfinished work and recommended learning no longer compete equally with history and detailed progress.
- Added an explicit Continue Learning experience for active worksheets and completed worksheets with skipped-question recovery.
- Limited the default student Home history DOM to three recent completed worksheets, with View all worksheets progressive disclosure.
- Added student-only mobile navigation for Home, Adventure, Worksheets and Progress with text labels, accessible current-state semantics, keyboard focus and iPhone safe-area spacing.
- Converted Story Adventure on narrow screens from a long vertical stack into compact horizontally swipeable cards while preserving the same timed adaptive session and evidence path.
- Reduced the MathQuest student header beneath Home Assistant ingress on mobile without removing sign-out.
- Replaced the broken five-column phone calendar navigation with readable previous-week, date-range, next-week and Today controls; one-day controls remain available on wider layouts.
- Changed narrow-screen weekly activity to a readable vertical activity list rather than forcing a desktop-style seven-column calendar into the phone viewport.
- Flattened mobile worksheet-history presentation and reduced nested card density while retaining detailed review data after disclosure.
- Added frontend regression tests for unfinished-work priority, skipped recovery, recent-history limits, mobile student navigation, calendar controls and Story Adventure continuity.
- Added a v0.40.0 presentation-only backend wrapper so runtime/version metadata advances without changing the v0.39 learning-quality engine.
- Preserved adaptive daily learning, prerequisite routing, spaced retrieval, misconception evidence, confidence evidence, Math Mentor, Visual Mathematics, Story Adventure learning selection, Parent Learning Intelligence, Parent Test isolation and the v0.38 keyboard-first worksheet feedback flow.

## v0.39.0 - Session Learning Quality and Adaptive Continuity

- Added a final session-level learning-quality pass so MathQuest evaluates the generated worksheet as a whole rather than relying only on individual question safeguards.
- Added multidimensional direct-arithmetic difficulty metadata covering operation, operand digit counts, regrouping demand and representation.
- Added meaningful near-duplicate detection so structurally equivalent calculations can be diversified without treating all Grade 5 addition or subtraction as the same question.
- Added lightweight recent-exposure awareness across answered Daily Practice and Story Adventure questions so overused structures are deprioritised without introducing a new learner-history subsystem.
- Preserved deliberate review, consolidation and retrieval instead of globally banning easy questions.
- Reconciled adaptive purpose and evidence metadata after final question replacement so Parent Learning Intelligence and later adaptive decisions describe the question Sienna actually received.
