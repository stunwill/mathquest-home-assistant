# MathQuest v0.44.0 — Targeted Learning Sessions & Skill-Level Progression

MathQuest now turns Best Next Step into a deliberate learning session rather than relying only on broad-topic adaptive selection.

## What changed

- Added an explicit session plan built from the existing outcome mastery, prerequisite, review and recommendation evidence.
- Recommended worksheets now prioritise the selected target skill where an established generator exists and retain existing duplicate/adaptive safeguards.
- Added purposeful question roles: reconnect, supported practice, core practice, transfer and independent check.
- Added learner-safe Today’s Focus guidance before a recommended session.
- Added targeted-session completion interpretation that can recognise support earlier followed by later independent work.
- Added parent visibility into the next plan, including purpose, target outcome/skill, prerequisite relation and planned question sequence.
- Preserved learner-state Progress, Story Adventure evidence continuity, Math Mentor, hints, worked examples, Parent Tests and Home Assistant integration.

## Progression safeguards

No global Grade 5 or Grade 6 state is introduced. Challenge readiness remains skill-specific and still requires at least six relevant recent questions, at least 82% independent success and no more than 25% support dependency.

The six-question Level 5/6 diagnostic remains a short starting signal. When evidence is uncertain, normal targeted learning is the preferred next source of evidence rather than repeated diagnostic testing.

## Compatibility

Existing worksheet history and evidence remain readable because targeted-session metadata is additive inside the existing question payload. Existing APIs and manually chosen worksheet flows remain available.

## Validation

Automated backend, frontend, metadata and aarch64 validation is performed by the repository Validate MathQuest workflow. Physical iPhone and iPad acceptance is tracked separately.

## Deferred

- Broader skill-specific generator coverage where the repository does not yet have an established targeted generator.
- Global curriculum-level placement or mastery classification.
- Large Vite/Vitest toolchain migration if the current audit findings cannot be safely resolved without unrelated release risk.
