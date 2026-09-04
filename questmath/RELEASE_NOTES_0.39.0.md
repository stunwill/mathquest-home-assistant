# MathQuest v0.39.0 — Session Learning Quality and Adaptive Continuity

MathQuest v0.39.0 focuses on the quality of the complete learning session rather than adding another headline feature.

## What changes for the learner

- The final worksheet is checked for repeated mathematical structures even when the numbers are different.
- Similar direct calculations are compared using operation, operand digit lengths and regrouping demand, so genuinely different Grade 5 calculations remain useful rather than being removed simply because they use the same operation.
- Recently answered Daily Practice and Story Adventure structures influence variety when a suitable alternative is available.
- Purposeful review, consolidation and spaced retrieval are preserved.
- Accidental low-complexity arithmetic is limited when learner evidence supports richer practice.

## Adaptive continuity

The existing Adaptive Daily Learning engine remains authoritative. If the final quality pass replaces a question, MathQuest refreshes its learning purpose and evidence annotation afterwards. Parent Learning Intelligence and subsequent adaptive decisions therefore refer to the final mathematics actually shown to Sienna.

The existing one-question challenge budget is preserved, as are misconception evidence, support dependence, prerequisite routing and retention.

## Difficulty information

Direct arithmetic now records reliable lightweight dimensions where available:

- operation;
- digits in each operand;
- regrouping/borrowing demand;
- answer representation.

This supplements the existing retrieval/instructional/challenge bands rather than replacing them with a second difficulty engine.

## Release reliability

The release validator now derives the active backend module from the Home Assistant runtime startup script and checks the frontend package manifest alongside the add-on, frontend display, backend, README and changelog versions. This closes the gap that allowed the frontend package manifest to remain on an old release number.

## Preserved systems

v0.39.0 deliberately preserves:

- Victorian Curriculum-aligned adaptive learning;
- prerequisite and spaced-review logic;
- misconception, confidence and support evidence;
- Math Mentor, hints and worked examples;
- interactive mathematics and Visual Mathematics;
- Story Adventure as presentation over the same learning engine;
- Parent Tests isolation;
- scoring, completion, skip and resume;
- Parent Learning Intelligence;
- Home Assistant ingress, authentication, persistence, backup/restore and parent-learning APIs;
- the v0.38 iPad feedback dialog and keyboard-first flow.

## Validation and manual acceptance

Automated validation must pass backend tests, frontend tests/build, metadata validation and a real aarch64 add-on build/startup `/api/health` check before merge.

The dependency audit is recorded separately; breaking upgrades are not force-applied as part of this learning-quality release.

Real learner-session and physical-device acceptance is not claimed by automated tests. Review representative sessions after deployment to confirm that variety improves without suppressing deliberate review.
