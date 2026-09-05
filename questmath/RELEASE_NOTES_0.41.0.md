# MathQuest v0.41.0

## Student Learning Progress & Guidance

MathQuest v0.41.0 makes the existing learning intelligence understandable to the student without creating a second mastery model.

### What changed

- Added learner-facing states derived from existing mastery, adaptive progression, support and spaced-retrieval evidence: Not enough evidence yet, Practising, Building confidence, Getting stronger, Ready for a challenge and Review due.
- Added a persistent Student Progress destination that groups mathematical outcomes by what the learner should understand about them rather than presenting raw levels and accuracy at equal priority.
- Added concise "Why this?" explanations for Best Next Step using the recommendation that the adaptive engine actually selected.
- Spaced retrieval is explained as purposeful review rather than failure.
- Supported success is recognised as learning with help and remains distinct from repeated independent success.
- Ready for a challenge reuses the existing Adaptive Daily Learning progression decision and does not introduce a new threshold.
- Technical evidence remains available through optional disclosure in Student Progress while Parent Learning Intelligence retains the full detailed evidence model.
- The mobile Progress navigation now targets the learner-guidance section directly.

### Learning architecture preserved

The release does not alter mastery thresholds, worksheet generation, adaptive composition, prerequisite routing, misconception evidence, Math Mentor, hints, worked examples, confidence evidence, Story Adventure selection or Parent Test isolation.

Student states are deterministic interpretations of existing `v0230` outcome mastery and `v0330` skill progression evidence. See `STUDENT_LEARNING_STATE_0.41.0.md` for the mapping.

### Conservative language

MathQuest does not claim a measured historical improvement trend unless the evidence supports one. It does not expose internal misconception codes or tell the learner they "have a misconception". A dedicated learner-facing misconception explanation is deferred until the recommendation contract can identify that cause safely and specifically.

### Validation status

Repository validation must pass before merge, including Python compilation, the complete backend pytest suite, npm ci, the complete frontend Vitest suite, TypeScript/Vite production build, YAML and version validation, release-note extraction, git diff checks and the real aarch64 add-on startup/health test.

Physical-device acceptance remains documented separately in `MANUAL_ACCEPTANCE_0.41.0.md` and must not be marked complete from automated testing alone.
