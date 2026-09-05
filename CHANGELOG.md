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
- Changed narrow-screen weekly activity to a readable vertical list rather than forcing a desktop-style seven-column calendar into the phone viewport.
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
- Preserved the existing one-question challenge budget, Parent Test isolation, Story Adventure presentation architecture and v0.38 keyboard-first feedback experience.
- Made the active backend module release-authoritative in version validation and added the previously stale frontend `package.json` version to the consistency gate.
- Added deterministic learning-quality regression tests for near-duplicate structures, multidimensional difficulty, recent-exposure isolation, purposeful review, Parent Test isolation, final quality annotations and challenge limits.

## v0.38.1 - Number & Algebra Quality and Melbourne Time

- Reduced low-complexity Number & Algebra direct arithmetic by upgrading small addition/subtraction items such as `121 + 22`, `50 + 58`, `14 − 4` and `8 + 8` to larger Grade 5-appropriate place-value calculations.
- Preserved useful calculation fluency while preventing small direct sums from dominating normal learner worksheets.
- Replaced equal-groups “Which operation?” questions with numerical total questions so the learner chooses multiplication as part of solving the problem rather than naming the operation only.
- Converted worksheet-history timestamps from stored UTC to `Australia/Melbourne`, including AEST/AEDT daylight-saving transitions.
- Added backend regression coverage for arithmetic upgrading, equal-groups numerical answers and Melbourne time conversion.

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
- Preserved the v0.35.1 distinction between MathQuest JSON authentication failures and Home Assistant ingress/proxy authentication failures so ingress problems do not automatically destroy MathQuest credentials.
- Preserved Parent Dashboard reliability, Story Adventure's adaptive-learning integration, Math Mentor, Parent Test isolation, Home Assistant learning APIs and local-first operation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

- Fixed the Parent Learning Intelligence render lifecycle so the Parent Dashboard no longer crashes when intelligence changes from its initial null state to loaded data.
- Replaced indefinite parent-dashboard loading with explicit bootstrap success/failure handling and visible retry guidance for required dashboard data.
- Made backups and Parent Learning Intelligence independently degradable so one optional section cannot block the rest of the Parent Dashboard.
- Preserved Home Assistant ingress, MathQuest authentication, learner pages and Parent Tests.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

- Added compact Home Assistant learning APIs derived from Parent Learning Intelligence and existing adaptive evidence rather than introducing a second learning model.
- Added stable conceptual Home Assistant entities for daily learning, current focus, review status, support status and weekly summary.
- Added notification-ready learning signals for persistent support needs, repeated misconceptions, meaningful progress and review due.
- Separated actual active minutes from configured timed-session target minutes.
- Kept Daily Practice and Story Adventure inside the same learner evidence model and kept Parent Tests excluded.
- Added documented Home Assistant REST sensor and reminder examples while preserving local-first operation.
