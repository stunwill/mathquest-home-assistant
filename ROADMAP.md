## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

Status: In release validation

### Student information architecture
- [x] Make Home, Adventure, Worksheets and Progress real student destinations rather than scroll anchors.
- [x] Keep Home focused on current learning, Best Next Step and concise destination previews.
- [x] Move the complete Story Adventure selector to Adventure.
- [x] Move full worksheet history to Worksheets.
- [x] Move learner-state detail and Weekly Activity to Progress.
- [x] Remove the old streak/accuracy/question-volume/highest-level and technical Skill Map emphasis from student Home.

### Learner guidance
- [x] Present untouched worksheets as Ready to Start and reserve Continue Learning for meaningful progress.
- [x] Replace student-facing intervention terminology with Extra Practice while retaining the existing backend service.
- [x] Replace Review due student wording with Ready to review.
- [x] Remove raw independent/support percentages, adaptive mode labels and curriculum outcome codes from the primary student experience.
- [x] Group Progress skills under concise learner-state explanations and hide zero-value state summaries.

### Learning continuity
- [x] Preserve v0.41 learner-state derivation and recommendation logic without creating a second mastery score.
- [x] Preserve adaptive thresholds, prerequisite routing, spaced retrieval, recent exposure and difficulty adaptation.
- [x] Preserve Story Adventure on the normal adaptive timed-session and evidence path.
- [x] Preserve Math Mentor, hints, worked examples, confidence evidence, worksheet scoring/completion and Parent Test isolation.

### Testing and acceptance
- [x] Add frontend regression coverage for destination ownership, Ready to Start semantics, learner-safe guidance, grouped Progress and Weekly Activity wording.
- [ ] Complete backend, frontend, metadata and aarch64 startup/health validation.
- [ ] Complete the real-device checklist in `questmath/MANUAL_ACCEPTANCE_0.42.0.md` on iPhone and iPad hardware.

### Deliberately deferred
- [ ] Define automatic archival/abandonment rules only when existing worksheet lifecycle evidence can support them safely.
- [ ] Consider scroll-collapsing MathQuest header only if it can be implemented without layout shift, focus or ingress regressions.

## v0.41.0 - Student Learning Progress & Guidance

Status: Completed

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
- [x] Complete backend, frontend, metadata and real aarch64 startup/health validation.
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
