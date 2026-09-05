# MathQuest v0.41.0 Student Learning State

## Purpose

The Student Learning State is a presentation layer over MathQuest's existing learning intelligence. It does not store or calculate a second mastery score.

Its purpose is to translate existing evidence into language a Grade 5 learner can understand without exposing internal scoring formulas or making claims that the evidence cannot support.

## Evidence sources

The student state reuses two existing systems.

### Outcome mastery, v0.23

`v0230.outcome_mastery()` already derives curriculum-outcome evidence from recent answered learner questions. It includes:

- independent accuracy;
- supported accuracy;
- fluency;
- confidence calibration;
- retention checks;
- evidence count;
- last-practised date;
- spaced-review due date;
- prerequisite relationships.

The existing mastery status and review schedule remain unchanged.

### Adaptive Daily Learning, v0.33

`v0330._question_evidence()` and `_progression_state()` already distinguish repeated skill evidence using:

- recent question count;
- first-attempt independent success;
- eventual success;
- support dependency;
- recent failures.

The existing progression thresholds remain authoritative. In particular, `ready_to_progress` still requires at least six recent questions, at least 82% independent success and no more than 25% support dependency.

## Student states

The states below are deterministic interpretations of those existing decisions.

### Not enough evidence yet

Used when the target skill has fewer than the existing minimum six recent questions and no spaced review is already due.

This is deliberately not treated as poor performance.

### Practising

Used when sufficient evidence exists but the skill does not yet meet the existing consolidating, secure or ready-to-progress conditions.

### Building confidence

Used when eventual success is at least 72% but the recent evidence still shows substantial support use or insufficient independent success for the existing consolidating threshold.

This recognises successful learning with help without treating supported work as equivalent to independent success.

### Getting stronger

Used when the existing adaptive progression state is `secure`.

The learner explanation describes strong recent independent evidence. It does not claim that a measured historical trend exists.

### Ready for a challenge

Used only when the existing adaptive progression state is `ready_to_progress`.

No new progression threshold is introduced by v0.41.0.

### Review due

Used when the existing outcome mastery evidence has at least three questions and its current spaced-retrieval schedule says review is due.

Review due takes precedence over the other presentation states because the educational action is retrieval, not remediation.

## Recommendation explanations

The existing adaptive recommendation remains authoritative. v0.41.0 maps the recommendation's actual mode and routing evidence into student language:

- missing diagnostic baseline: explains that the short check helps MathQuest find a useful starting point;
- prerequisite routing: explains that the selected skill supports the next maths idea;
- spaced review: explains that previously learned material is returning to help it stick;
- secure/mastered recommended outcome: explains that recent evidence is strong enough to keep moving forward carefully;
- other practice: explains that the skill is one of the most useful next areas based on recent work.

For students, the existing `/api/learning/adaptive-v0230` contract remains in place but its `reason` is replaced with this learner-safe explanation. Parent-facing evidence remains detailed.

## Deliberately conservative omissions

v0.41.0 does not create a student-facing historical trend such as "you improved by X" because the existing Student endpoint does not provide a trustworthy before/after comparison for every skill.

It also does not expose internal misconception codes or claim that a learner "has a misconception". Existing misconception evidence continues to influence tutoring and adaptive learning, but a dedicated learner-facing misconception explanation is deferred until the recommendation contract can identify a safe, specific misconception reason without fabricating causality.

## Parent separation

Parent Learning Intelligence remains the appropriate place for detailed evidence, confidence, support dependency, misconceptions, retention and technical learning history.

Student language is intentionally concise and actionable. The underlying educational decisions remain shared and backend-authoritative.
