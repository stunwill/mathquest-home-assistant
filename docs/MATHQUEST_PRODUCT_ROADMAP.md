# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet or an analytics dashboard for a child. Each session should diagnose, explain, let Sienna work with meaningful mathematical representations, provide progressively stronger help only when needed, and revisit skills later to confirm retention.

## Current release scope, 0.42.0, Student UX, Navigation & Learning Guidance Refinement

Real iPhone use of v0.41.0 confirmed that the responsive foundation and learner-facing Progress work were useful, but also showed that Home still contained too much of Adventure, Worksheets and Progress. v0.42.0 makes the four student destinations own distinct responsibilities and translates more internal learning analytics into learner-safe language.

### Student information architecture

- Home is the concise learning launchpad for current work, Best Next Step and compact destination previews.
- Adventure owns the full Story Adventure selector while retaining the existing adaptive timed-session path.
- Worksheets owns resume, review and worksheet history.
- Progress owns learner states and Weekly Activity.
- Student Home no longer gives streak, raw accuracy, question volume, highest level or the technical Skill Map equal prominence with the next learning action.

### Learner-safe guidance

- Untouched worksheets are presented as Ready to Start; Continue Learning is reserved for genuinely started work.
- Student-facing intervention language becomes Extra Practice while the backend intervention service remains unchanged.
- Student-facing Review due becomes Ready to review.
- Raw independent/support percentages, adaptive mode labels and curriculum outcome codes are removed from the primary student experience.
- Progress groups skills under learner-state explanations instead of repeating the same explanation on every row.
- Zero-value learner-state summary cards are hidden.

### Learning continuity

- v0.41 learning-state derivation remains authoritative.
- Adaptive progression thresholds, prerequisite routing, spaced retrieval, recent exposure and difficulty adaptation do not change.
- Story Adventure remains a presentation layer over the same adaptive worksheet and evidence path.
- Math Mentor, hints, worked examples, confidence evidence, retry-first behaviour, worksheet scoring/completion, Parent Learning Intelligence and Parent Test isolation are preserved.

### Conservative worksheet lifecycle

- Ready to Start versus Continue Learning is derived from existing worksheet progress evidence.
- Historical learning evidence is not deleted.
- Automatic abandoned/archived classification is deferred until the repository has reliable lifecycle evidence to support it without inventing state.

### Responsive and accessibility

- Preserve iPhone safe-area navigation and the compact MathQuest header beneath Home Assistant ingress.
- Preserve the responsive Weekly Activity controls introduced in v0.40.0.
- Preserve the iPad 10th-generation landscape worksheet and physical-keyboard flow introduced in v0.38.0.
- Keep explicit current-page navigation semantics, visible focus, touch-size controls and reduced-motion behaviour.
- A scroll-collapsing MathQuest header is deliberately deferred unless it can be introduced without layout shift, focus or ingress regressions.

### Acceptance criteria

- Home, Adventure, Worksheets and Progress behave as distinct student destinations rather than scroll anchors.
- Untouched worksheets are not described as resumed/saved progress.
- Student-facing Extra Practice and Progress do not expose raw support percentages or intervention terminology.
- Ready to review is used for student-facing spaced-review language.
- Story Adventure continues to create the same adaptive practice session and theme framing as before.
- Full backend, frontend, metadata and aarch64 startup/health validation pass before merge.
- Physical iPhone and iPad checks remain explicitly unverified until performed on hardware.

## Recently completed release, 0.41.0, Student Learning Progress & Guidance

v0.41.0 translated existing outcome mastery, Adaptive Daily Learning progression, independent versus supported success and spaced-retrieval evidence into learner-facing states without creating another mastery score. Ready for a challenge remained tied to the existing `ready_to_progress` decision and review scheduling remained tied to existing spaced-retrieval evidence.

The release also added evidence-grounded Best Next Step explanations and kept unsupported historical-improvement claims and internal misconception codes out of the student experience. Parent Learning Intelligence remained the detailed technical evidence surface.

## Recently completed release, 0.40.0, Student Mobile Home, Navigation & Responsive UX

v0.40.0 introduced the action-first mobile Home, compact Story Adventure selection, progressive worksheet history, student navigation, safe-area handling and responsive Weekly Activity controls. v0.42.0 completes that information-architecture direction by making those navigation destinations distinct views.

## Ongoing product direction

MathQuest should continue expanding Grade 5 question variety and curriculum depth only where the mathematics and learner evidence justify it. Engagement features should remain subordinate to teaching quality, and technical analytics should be translated into useful learner guidance rather than exposed because they exist.
