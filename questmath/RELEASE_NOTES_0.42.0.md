# MathQuest v0.42.0 — Student UX, Navigation & Learning Guidance Refinement

v0.42.0 turns the student navigation into genuine Home, Adventure, Worksheets and Progress destinations based on real iPhone use of v0.41.0 through Home Assistant ingress.

## Student experience

- Home is now a concise learning launchpad rather than a long dashboard containing every major feature.
- Adventure owns the full Story Adventure selector and keeps the existing adaptive timed-session path.
- Worksheets owns worksheet history, resume and review actions.
- Progress owns learner-state guidance and Weekly Activity.
- Untouched worksheets are shown as Ready to Start. Continue Learning is reserved for work with meaningful progress.
- Extra Practice replaces student-facing intervention language, without changing the underlying intervention/support session service.
- Ready to review replaces Review due in student-facing presentation.
- Raw independent/support percentages, adaptive mode labels and curriculum outcome codes are removed from the primary student experience.
- Progress groups skills beneath a concise state explanation, hides zero-value summary cards and removes the optional technical percentage disclosure.

## Learning continuity

The release does not create a new mastery model or change adaptive thresholds. It inherits v0.41 learning-state derivation, Adaptive Daily Learning, prerequisite routing, spaced review, recommendation logic, recent exposure, difficulty adaptation and Parent Learning Intelligence.

Story Adventure remains a presentation layer over the normal adaptive worksheet path. Math Mentor, hints, worked examples, confidence evidence, retry-first behaviour, worksheet scoring/completion and Parent Test isolation remain part of the release contract.

## Conservative worksheet lifecycle

v0.42.0 improves presentation semantics for untouched versus started worksheets but does not automatically delete or archive old learner evidence. Reliable abandonment/archival rules are deferred until the repository has sufficient lifecycle evidence to make that distinction safely.

## Responsive and accessibility

The existing compact Home Assistant ingress header, iPhone safe-area navigation, responsive week controls, iPad landscape worksheet layout, physical-keyboard flow, visible focus and reduced-motion behaviour are preserved. Destination navigation uses explicit current-page semantics.

## Manual acceptance

Automated validation does not replace physical-device checks. iPhone Home Assistant ingress and iPad 10th-generation landscape acceptance remain explicitly unverified until performed on hardware using `MANUAL_ACCEPTANCE_0.42.0.md`.
