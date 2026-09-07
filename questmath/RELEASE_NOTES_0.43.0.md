# MathQuest 0.43.0 — Diagnostic Interpretation, Placement & Learning Path

MathQuest 0.43.0 turns the six-question Level 5/6 diagnostic into conservative learning evidence instead of a grade or pass/fail result.

## What changed

- Diagnostic responses now contribute through the existing outcome-mastery architecture rather than a separate diagnostic mastery model.
- Level 5 diagnostic operations evidence maps into the established efficient-calculation outcome; Level 6 fraction/decimal evidence maps into the established fraction/decimal outcome.
- Diagnostic interpretation distinguishes independent first-attempt success, eventual success with support, and areas that need more evidence.
- The diagnostic no longer produces an overall estimated curriculum level.
- Best Next Step continues to come from the existing adaptive recommendation, prerequisite and review systems.
- Three diagnostic questions cannot bypass the existing challenge-readiness threshold of six recent questions, at least 82% independent success and no more than 25% support dependency.
- Older diagnostic retakes remain in parent-visible history but do not accumulate toward current readiness; the latest diagnostic is the active placement signal.
- Diagnostic attempts do not manufacture spaced-retention evidence.
- Student Progress now includes a learner-safe Your Starting Point summary after diagnostic completion.
- Diagnostic completion avoids pass/fail, overall grade, raw mastery percentages and curriculum codes.
- Parent Dashboard receives a detailed Level 5/6 diagnostic evidence summary including independent/eventual success, support use, sampled outcomes and recommended next focus.
- Historical normal worksheet evidence remains preserved and continues to influence the same learning model.

## Deliberate limits

The diagnostic remains six questions: three Level 5 and three Level 6. It is a placement signal, not a comprehensive curriculum assessment. MathQuest deliberately does not claim that the learner has mastered a whole level, is a Grade 5 or Grade 6 learner, or should globally move all mathematics to one level.

Subsequent normal learning remains responsible for gathering enough evidence for stronger progression decisions.

## Compatibility

This release preserves Math Mentor, hints, worked examples, Visual Mathematics, Interactive Maths Lab, retry-first feedback, confidence evidence, worksheet history/resume, prerequisite routing, spaced review, learner states, Story Adventure, Parent Tests and Home Assistant ingress.

## Device acceptance

Physical iPhone and iPad 10th-generation checks are documented in `MANUAL_ACCEPTANCE_0.43.0.md` and remain **PENDING PHYSICAL DEVICE VALIDATION** until run on real hardware.
