## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

Status: In release validation

### Student information architecture
- [x] Turn Home, Adventure, Worksheets and Progress into meaningful student destinations rather than scroll anchors in one long dashboard.
- [x] Keep Home focused on the next learning action with concise Adventure and Progress previews.
- [x] Make Adventure own the complete Story Adventure catalogue and duration controls.
- [x] Make Worksheets own full worksheet history, resume and review actions.
- [x] Make Progress own learner-state detail and Weekly Activity.

### Learner language and guidance
- [x] Replace student-facing intervention terminology with Extra Practice-style language while preserving the backend support-session model.
- [x] Present spaced retrieval as Ready to review rather than overdue work.
- [x] Group learner states under concise explanations and hide unnecessary zero-value summaries.
- [x] Remove raw mastery/support percentages and internal analytics from the primary student Progress display.
- [x] Preserve evidence-grounded recommendation explanations and existing adaptive thresholds.

### Worksheet lifecycle and regression protection
- [x] Distinguish untouched Ready to Start worksheets from genuinely started Continue Learning worksheets using existing progress evidence.
- [x] Preserve worksheet history and learning evidence without automatically deleting or archiving older incomplete work.
- [x] Preserve the established worksheet, Math Mentor, hint, worked-example, visual-mathematics, keyboard and post-answer feedback contracts.
- [ ] Defer automatic abandonment/archive decisions until the repository has a reliable inactivity signal that cannot corrupt learning evidence.
- [ ] Defer scroll-collapsing header behaviour until it can be proven stable under Home Assistant ingress, focus and dynamic viewport changes.

### Testing and acceptance
- [x] Add/update student-observable regression coverage for destination ownership, learner language, Ready to Start semantics and Progress density.
- [ ] Complete backend, frontend, metadata and aarch64 startup/health validation.
- [ ] Complete the real-device checklist in `questmath/MANUAL_ACCEPTANCE_0.42.0.md` on iPhone and iPad 10th-generation hardware.

## v0.41.0 - Student Learning Progress & Guidance

Status: In release validation

### Student learning guidance
- [x] Derive learner-facing states from existing outcome mastery and Adaptive Daily Learning evidence without creating a parallel mastery score.
- [x] Distinguish insufficient evidence from poor performance.
- [x] Distinguish supported eventual success from repeated independent success.
- [x] Reuse existing ready-to-progress thresholds for Ready for a challenge.
- [x] Reuse the existing spaced-retrieval schedule for Review due.
- [x] Replace technical student Best Next Step reasons with evidence-grounded learner explanations.
- [x] Keep historical-improvement claims conservative unless trustworthy trend evidence exists.
- [x] Keep internal misconception codes out of student language.

### Student Progress UX
- [x] Add a persistent Student Progress destination organised by learner meaning rather than raw level/accuracy rows.
- [x] Keep detailed evidence behind optional disclosure.
- [x] Point mobile Progress navigation to the learner-guidance section.
- [x] Preserve Continue Learning priority and avoid a competing recommended-session action inside Progress.
- [x] Keep Parent Learning Intelligence and Parent Tests separate from student navigation.

### Learning architecture
- [x] Preserve worksheet generation, mastery thresholds, adaptive composition, prerequisites, recent exposure and difficulty adaptation.
- [x] Preserve Math Mentor, hints, worked examples, confidence evidence and retry-first behaviour.
- [x] Preserve Story Adventure as a presentation layer over the normal adaptive session path.
- [x] Preserve the v0.38 Answer → Feedback → Understand → Reflect → Continue worksheet interaction.

### Testing and acceptance
- [x] Add backend regression coverage for insufficient evidence, supported success, challenge readiness, review due and recommendation explanations.
- [x] Add frontend regression coverage for learner-state rendering, optional evidence disclosure and Progress action hierarchy.
- [ ] Complete backend, frontend, metadata and real aarch64 startup/health validation.
- [ ] Complete the real-device checklist in `questmath/MANUAL_ACCEPTANCE_0.41.0.md` on iPhone and iPad hardware.

## v0.40.0 - Student Mobile Home, Navigation & Responsive UX

Status: Completed

### Student mobile experience
- [x] Reorganise mobile Home around current learning action rather than equal-weight dashboard sections.
- [x] Promote active worksheets and skipped-question recovery through Continue Learning.
- [x] Limit recent worksheet history to three items by default with progressive disclosure.
- [x] Make Story Adventure selection compact and horizontally swipeable on narrow screens while preserving adaptive question selection.
- [x] Add student-only Home, Adventure, Worksheets and Progress navigation with safe-area support.
- [x] Reduce MathQuest mobile header height beneath Home Assistant ingress while preserving sign-out.
- [x] Flatten mobile history presentation and reduce unnecessary nested-card density.

### Calendar and responsive UX
- [x] Replace the broken five-column phone calendar controls with readable previous-week, date-range, next-week and Today navigation.
- [x] Preserve richer one-day navigation on tablet and desktop.
- [x] Present mobile weekly activity as a one-column activity list instead of a compressed desktop calendar.
- [x] Prevent horizontal page overflow and reserve bottom-navigation safe-area space through responsive CSS.
- [x] Respect reduced-motion preferences and preserve visible keyboard focus.

### Learning architecture
- [x] Preserve v0.39 session learning quality and adaptive continuity without changing generation or mastery behaviour.
- [x] Preserve prerequisite routing, spaced retrieval, misconception evidence and confidence evidence.
- [x] Preserve Story Adventure as a presentation layer over the normal adaptive session path.
- [x] Preserve Parent Learning Intelligence and Parent Test isolation.
- [x] Preserve the v0.38 Answer → Feedback → Understand → Reflect → Continue worksheet interaction.

### Testing and acceptance
- [x] Add frontend regression coverage for Continue Learning, skipped recovery, recent-history disclosure, student navigation, Story Adventure continuity and mobile week navigation.
- [x] Complete backend, frontend, metadata and real aarch64 startup/health validation.
- [ ] Complete the real-device checklist in `questmath/MANUAL_ACCEPTANCE_0.40.0.md` on iPhone and iPad hardware.

## v0.39.0 - Session Learning Quality and Adaptive Continuity

Status: Completed

### Learning quality
- [x] Add a final session-level quality policy after existing generation and adaptive composition.
- [x] Detect meaningful near-duplicate structures rather than only exact prompt or skill duplicates.
- [x] Add lightweight recent-exposure awareness across answered Daily Practice and Story Adventure work.
- [x] Preserve deliberate review, consolidation and retrieval while reducing accidental repetition.
- [x] Record multidimensional direct-arithmetic difficulty metadata including operation, digit size and regrouping demand.
- [x] Refresh adaptive purpose/evidence metadata after final question replacements so later learning decisions describe the final worksheet.
- [x] Preserve the established challenge limit and Parent Test isolation.

### Release integrity
- [x] Derive the release-authoritative backend module from the runtime startup script instead of hard-coding the previous wrapper.
- [x] Bring the frontend `package.json` version into the release consistency contract.
- [x] Reconcile v0.38.1 roadmap status with its completed merge/release state.

### Testing
- [x] Add deterministic tests for near-duplicate structure, difficulty dimensions, recent exposure, purposeful retrieval, Parent Test isolation, final annotations and challenge limits.
- [x] Complete backend, frontend, metadata and real aarch64 startup/health validation.
- [x] Record the current npm dependency audit and remaining findings.
- [ ] Complete manual real-session acceptance on representative iPad landscape and mobile/desktop views.

## v0.38.1 - Number & Algebra Quality and Melbourne Time

Status: Completed

### Learning quality
- [x] Reduce low-complexity direct addition/subtraction in normal Number & Algebra worksheets.
- [x] Upgrade small direct calculations to larger Grade 5-appropriate place-value values rather than removing calculation fluency entirely.
- [x] Replace equal-groups operation-label questions with numerical total questions so operation choice is part of solving the problem.
- [x] Preserve adaptive learning, purposeful retrieval, Story Adventure and Parent Test isolation.

### Home Assistant / history
- [x] Display worksheet-history timestamps using `Australia/Melbourne` rather than raw stored UTC.
- [x] Use timezone-aware conversion so AEST/AEDT daylight-saving transitions are correct.

### Testing
- [x] Add regression coverage for arithmetic upgrading, equal-groups numerical answers and Melbourne timezone conversion.
- [x] Complete repository CI including backend pytest, frontend Vitest/build, metadata validation and aarch64 startup/health check.

## v0.38.0 - iPad Landscape Feedback and Worksheet UX

Status: Completed

### Student worksheet UX
- [x] Replace below-question post-answer feedback with a reusable accessible feedback dialog.
- [x] Keep correct/incorrect status and the primary next action visible independently of worksheet page scroll.
- [x] Move the existing optional confidence reflection into the feedback dialog without changing its evidence endpoint.
- [x] Preserve retry-first incorrect-answer behaviour and keep Math Mentor optional unless backend learning logic requires support.
- [x] Make the normal physical-keyboard flow Answer → Enter → Feedback → Enter → Continue or Retry explicit and predictable.
- [x] Restore a cleared, focused typed-answer field after retry.
- [x] Protect against rapid repeated Enter presses causing duplicate submission or question skipping.
- [x] Add restrained non-blocking success motion and reduced-motion support.

### iPad landscape layout
- [x] Add an iPad 10th-generation landscape layout band around the typical 1180 × 820 CSS viewport.
- [x] Reduce unnecessary header, progress, card, sidebar and support spacing while retaining readable question typography.
- [x] Keep portrait/mobile and desktop layouts outside the landscape-specific optimisation.
- [x] Keep long dialog support content internally scrollable while result and action remain visible.

### Shared learning architecture
- [x] Reuse the same result experience for typed, choice, whole-number number-line, fraction, ruler, grid, reasoning and Story Adventure questions through the shared Worksheet answer path.
- [x] Preserve adaptive selection, prerequisite graph, spaced retrieval, misconception evidence, confidence evidence, scoring, completion, resume and skipped-question handling.
- [x] Preserve Parent Test isolation from learner mastery and evidence.

### Accessibility and testing
- [x] Add dialog semantics, explicit result text/icons, screen-reader result announcement, focus movement, focus containment, visible focus styling and touch-size controls.
- [x] Add frontend coverage for keyboard submit/continue/retry, retry focus, rapid Enter, confidence evidence, optional Math Mentor, touch interaction, Story Adventure and viewport-fixed feedback.
- [x] Complete repository CI including backend pytest, frontend Vitest/build, metadata validation and real aarch64 startup/health check.
- [ ] Complete the real-device iPad 10th-generation manual acceptance checklist in `questmath/MANUAL_ACCEPTANCE_0.38.0.md`.

## v0.37.1 - Duplicate-Safe Reasoning Mix

Status: Completed

### Reliability and learning quality
- [x] Preserve worksheet question-identity uniqueness when adding structured reasoning questions.
- [x] Leave the original question unchanged when no unique reasoning replacement can be generated.

### Testing
- [x] Add regression coverage for duplicate reasoning candidates and preserve existing worksheet duplicate-safety tests.

# MathQuest Product Roadmap

MathQuest is a Victorian Curriculum aligned, adaptive mathematics learning application for short, purposeful daily practice. This file is the authoritative development roadmap for repository tooling and DevHub.

## v0.37.0 - Richer Interactive Mathematics and Mathematical Reasoning

Status: Completed

### Learning
- [x] Extend first-class interactive answers beyond whole-number number lines into fraction bars, fraction number lines, scaled ruler reading and grid-reference selection.
- [x] Keep every new interaction inside the existing backend-authoritative worksheet, attempt, evidence, misconception and adaptive-learning architecture.
- [x] Add structured mathematical reasoning including operation selection, reasonableness, conceptual comparison and age-appropriate error analysis.
- [x] Reuse existing misconception evidence for regrouping/place-value reasoning instead of creating a parallel taxonomy.
- [x] Preserve purposeful review, consolidation, spaced retrieval and existing adaptive-difficulty decisions.
- [x] Keep Story Adventure on the same question, validation and evidence path as Daily Practice.

### Tutoring and UX
- [x] Add child-friendly touch, mouse and keyboard-focus interactions with clear selected states and responsive layouts.
- [x] Hide requested internal targets where revealing a ruler or fraction-number-line label would undermine the learning objective.
- [x] Extend Math Mentor with representation-specific guidance and different-number worked examples for the new interactive models.
- [x] Preserve immediate retry after an incorrect answer without requiring Math Mentor.

### Testing
- [x] Add deterministic backend generator, scale/partition, target-hiding, reasoning and misconception tests.
- [x] Add frontend interaction and accessibility coverage for each new first-class answer model.
- [x] Preserve Parent Test isolation, Story Adventure compatibility and existing regression coverage.
- [x] Preserve backend, frontend, metadata and real aarch64 add-on startup validation.

## v0.36.0 - Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

Status: Completed

### Learning
- [x] Make number-line location questions first-class interactive answers selected directly on the line.
- [x] Keep number-line scoring and evidence inside the existing backend-authoritative worksheet and attempt architecture.
- [x] Extend worksheet-quality safeguards so straightforward two-digit additions such as `20 + 28` are recognised as low-complexity practice when learner evidence supports progression.
- [x] Preserve purposeful foundational review, consolidation and spaced retrieval rather than globally removing easy arithmetic.
- [x] Keep Story Adventure on the same adaptive-learning and answer-validation path.

### UX
- [x] Add child-friendly mouse, touch and keyboard-focus targets for interactive number lines.
- [x] Default the editable student login username to `sienna` while leaving passwords blank and parent login available.
- [x] Treat normal MathQuest token expiry as a return-to-login state rather than a generic `Invalid session` application failure.
- [x] Keep Home Assistant ingress authentication failures distinct from MathQuest authentication expiry.

### Testing
- [x] Add deterministic number-line generation tests and frontend interaction coverage.
- [x] Add regression coverage for simple two-digit addition classification and purposeful-foundation preservation.
- [x] Add login and session-expiry recovery coverage.
- [x] Preserve backend, frontend, metadata and aarch64 add-on startup validation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

Status: Completed

### Reliability
- [x] Fix Parent Learning Intelligence rendering when data transitions from initial loading to loaded state.
- [x] Prevent required Parent Dashboard bootstrap failures from leaving an indefinite splash screen.
- [x] Let backups and optional learning-intelligence failures degrade independently without blocking the core parent experience.
- [x] Preserve Home Assistant ingress, authentication, Parent Tests and learner functionality.

### Testing
- [x] Add regression coverage for the Parent Learning Intelligence null-to-loaded render lifecycle.
- [x] Keep release metadata and runtime-version validation aligned with the corrective release.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

Status: Completed

### Learning
- [x] Expose parent-readable learning state derived from MathQuest's existing Learning Intelligence rather than duplicating mastery logic in Home Assistant.
- [x] Surface meaningful daily-practice completion, current learning focus, review-due state, persistent support needs, repeated misconceptions and meaningful progress.
- [x] Keep Story Adventure activity inside the same evidence model as Daily Practice.
- [x] Preserve Parent Test isolation from ordinary daily learning and Home Assistant learner-state calculations.
- [x] Keep Home Assistant educational decisions backend-authoritative inside MathQuest.

### UX
- [x] Provide a compact stable Home Assistant entity/API contract instead of an entity for every internal metric.
- [x] Add concise parent-facing seven-day learning summaries and notification-ready learning signals without per-question notification noise.
- [x] Distinguish actual active minutes from configured timed-session target minutes.
- [x] Document standard Home Assistant REST sensor and reminder automation examples without requiring HACS.
- [x] Preserve local-first privacy, Home Assistant ingress compatibility and existing learner/parent experiences.

### Testing
- [x] Verify Home Assistant learning state consumes Parent Learning Intelligence and adaptive-purpose evidence.
- [x] Verify Daily Practice and Story Adventure completion behaviour and Parent Test isolation.
- [x] Verify stable identifiers, no-data behaviour, restart-safe state derivation, review due, support dependence, misconception and meaningful-progress signals.
- [x] Preserve complete backend/frontend regression coverage, npm ci, frontend tests and production build validation.

## v0.34.0 - Story Adventure Expansion and Purposeful Daily Learning

Status: Completed

### Learning
- [x] Make Story Adventure a presentation layer over the same adaptive learning engine used by Daily Practice.
- [x] Preserve skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- [x] Record Story Adventure answers through the existing worksheet, attempt, support and mastery evidence architecture.
- [x] Keep Story Adventure completion and progression separate from mastery evidence.
- [x] Keep Parent Tests isolated from Story Adventure framing and adaptive recomposition.

### UX
- [x] Add reusable short adventure themes with setting, objective, stages and an ending.
- [x] Support 5, 10 and 15-minute Story Adventure sessions.
- [x] Add lightweight stage and mission progress without introducing a game engine.
- [x] Preserve immediate retry after an incorrect answer.
- [x] Keep Hint, Teach me, Worked example and Math Mentor optional and question-specific.
- [x] Reuse Visual Mathematics only where it supports understanding.

### Testing
- [x] Verify Story Adventure preserves adaptive questions, learning purpose and difficulty metadata.
- [x] Verify prerequisite, consolidation, misconception repair, spaced review and controlled challenge remain available.
- [x] Verify Story Adventure evidence feeds the existing learning model without creating mastery from story completion.
- [x] Verify Parent Test isolation and session resume behaviour.
- [x] Validate frontend dependencies with npm ci, tests and production build.

## v0.33.0 - Adaptive Daily Learning

Status: Completed

### Learning
- [x] Classify daily practice as current learning, consolidation, spaced review or limited challenge from learner evidence.
- [x] Require repeated independent success before progression.
- [x] Make progression support-aware and misconception-aware.
- [x] Reuse spaced-review evidence for purposeful retrieval.
- [x] Keep Parent Tests isolated from adaptive session composition.

### Testing
- [x] Cover insufficient evidence, independent progression, support-heavy success, isolated mistakes and misconception-triggered consolidation.

## v0.32.3 - Grade 5 Method-First Math Mentor

Status: Completed

### Learning
- [x] Improve written multiplication, partition division, decimal hundredths, perimeter and area tutoring.
- [x] Preserve progressive hints and worked examples using different numbers from the active question.
- [x] Connect formulas and written methods back to mathematical meaning and place value.

### Testing
- [x] Add regression coverage for method-first tutoring and Grade 5 difficulty boundaries.

## v0.32.2 - Grade 5 Algebra Variety

Status: Completed

### Learning
- [x] Add numerical pattern continuation, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- [x] Mix new structures into the existing Algebra pool rather than replacing established practice.
- [x] Preserve adaptive difficulty, learning evidence, Math Mentor and worksheet-quality safeguards.

### Testing
- [x] Add large-sample generation and structural-diversity tests.

## v0.32.1 - Worksheet Learning Quality Corrective Release

Status: Completed

### Learning
- [x] Preserve retry-first incorrect-answer behaviour with tutoring support remaining optional.
- [x] Tighten worked-example alignment across Probability, fractions, Measurement, Space and Statistics.
- [x] Limit overly simple arithmetic to purposeful retrieval once learner evidence supports progression.
- [x] Preserve denominator-accurate fraction number lines and visual-state isolation.

### Testing
- [x] Recheck post-transform question-family diversity and worked-example alignment.

## v0.32.0 - Parent Learning Intelligence

Status: Completed

### Learning
- [x] Add parent-facing Secure, Developing, Needs Support, Review Due and Not Enough Evidence states.
- [x] Distinguish first-attempt, eventual, independent and supported success.
- [x] Add evidence confidence, prioritised recommendations, misconception grouping, prerequisite visibility and retention status.
- [x] Add 7, 30 and 90-day learning comparisons.

### UX
- [x] Present learning evidence in plain language without exposing internal mastery scores as false precision.

## v0.31.0 - Tablet Learning and Math Mentor Refinement

Status: Completed

### Learning
- [x] Raise appropriate Number practice toward hundreds-based addition and subtraction when evidence supports progression.
- [x] Make Teach me and hints question-specific.

### UX
- [x] Improve tablet portrait and landscape worksheet use.
- [x] Preserve retry-first behaviour, keyboard autofocus and Visual Mathematics.

## Future - Learner Experience and Curriculum Depth

Status: Planned

### Learning
- [ ] Continue expanding Grade 5 question variety and appropriate difficulty using real learner evidence.
- [ ] Improve continuity between learner recommendations, Daily Practice and Story Adventure.
- [ ] Expand Victorian Curriculum coverage while preserving verified outcome mapping.
- [ ] Add richer Visual Mathematics only where representations improve understanding.
- [ ] Continue improving hints, Math Mentor and worked examples when real usage identifies teaching gaps.

### UX
- [ ] Expand Story Adventure themes and context where engagement improves without weakening mathematical clarity.
- [ ] Continue improving parent and student reporting from real evidence rather than adding generic game mechanics.

### Platform
- [ ] Consolidate historical backend version wrappers in a dedicated compatibility release when justified by maintenance cost and regression coverage.
