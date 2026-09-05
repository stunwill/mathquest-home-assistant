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
- [x] Preserve retry-first incorrect-answer behaviour and keep Math Mentor optional unless backend learning logic requires it.
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
