# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.37.0, Richer Interactive Mathematics and Mathematical Reasoning

This release extends MathQuest's first-class interactive answer architecture beyond whole-number number lines into a small set of representations where direct manipulation improves understanding rather than adding decoration.

### Interactive mathematics with one learning engine

- Keep MathQuest backend-authoritative for correctness, adaptive selection, progression, prerequisites, retention, misconceptions and learning evidence.
- Add interactive fraction-bar selection, fraction number-line location, scaled ruler reading and grid-reference selection through the existing worksheet answer route.
- Hide requested internal targets when labels would reveal the answer, including internal fraction-number-line ticks and ruler marks.
- Keep the interaction layer reusable and responsive rather than building unrelated one-off visual widgets.

### Mathematical reasoning

- Add structured operation-selection, reasonableness, conceptual comparison and age-appropriate error-analysis questions.
- Prefer assessable structured choices over long free-text explanations that cannot be reliably validated.
- Reuse the existing misconception-evidence architecture for regrouping/place-value error analysis.
- Keep arithmetic fluency and purposeful foundational retrieval available rather than replacing calculation practice with reasoning-only sessions.

### Tutoring and Story Adventure

- Extend Math Mentor with representation-specific hints and different-number worked examples without revealing the active answer.
- Preserve immediate retry after an incorrect answer with tutoring remaining optional.
- Keep Story Adventure as presentation over the same adaptive worksheet, answer and evidence architecture.
- Preserve Parent Test isolation from learner mastery and adaptive evidence.

### Release acceptance criteria

- Each new interactive model submits through the normal backend-authoritative answer path.
- Fraction partitions, number-line intervals, ruler scales and grid references are mathematically consistent and responsive.
- Requested internal targets are not accidentally labelled.
- At least one structured reasoning family can appear in an appropriate learner session without imposing a rigid session sequence.
- Error-analysis questions use plausible distractors and existing misconception evidence where justified.
- Math Mentor support is aligned with the representation and worked examples use different values.
- Story Adventure automatically supports compatible interactive questions without a separate story question generator.
- Parent Tests remain isolated.
- Full backend, frontend, production build, metadata and aarch64 startup checks pass before merge.

## Recently completed release, 0.36.0, Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Made whole-number number-line location a first-class interactive answer selected directly on the line.
- Reduced unnecessarily basic two-digit addition when learner evidence supports progression while preserving purposeful review, consolidation and retrieval.
- Defaulted the editable student username to `sienna` and made normal MathQuest token expiry return automatically to login.
- Preserved Home Assistant ingress distinction, Parent Dashboard reliability and the existing adaptive-learning architecture.

## Recently completed release, 0.35.1, Parent Dashboard Reliability

- Fixed Parent Learning Intelligence rendering and Parent Dashboard bootstrap recovery.
- Kept backups and optional learning-intelligence failures from blocking the core parent experience.

## Recently completed release, 0.35.0, Home Assistant Parent Integration and Actionable Learning Insights

- Exposed compact parent-readable Home Assistant learning state derived from MathQuest's existing Learning Intelligence.
- Added daily completion, current focus, review, support, misconception, progress and weekly-summary signals without duplicating mastery logic.
- Preserved Parent Test isolation and local-first operation.

## Recently completed release, 0.34.0, Story Adventure Expansion and Purposeful Daily Learning

- Made Story Adventure a presentation layer over the same adaptive learning plan as Daily Practice.
- Preserved skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- Preserved retry-first answers and optional tutoring.
- Kept Story Adventure evidence inside the existing learning model while ensuring story completion itself is not mastery evidence.

## Recently completed release, 0.33.0, Adaptive Daily Learning

- Classified practice questions as current learning, consolidation, spaced review or limited challenge from learner evidence.
- Added controlled progression requiring repeated independent success before challenge increases.
- Made progression support-aware and misconception-aware.
- Reused spaced-review evidence and preserved Parent Test isolation.

## Recently completed release, 0.32.3, Grade 5 Method-First Math Mentor

- Improved written multiplication, partition division, decimal hundredths, perimeter and area tutoring.
- Preserved progressive hints and different-number worked examples.
- Connected formulas and written methods back to mathematical meaning and place value.

## Recently completed release, 0.32.2, Grade 5 Algebra Variety

- Added numerical pattern continuation, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- Mixed new structures into the existing Algebra pool instead of replacing established practice.
- Preserved adaptive difficulty, learning evidence, Math Mentor and worksheet-quality safeguards.

## Recently completed release, 0.32.1, Worksheet Learning Quality Corrective Release

- Preserved immediate retry after an incorrect answer with Math Mentor remaining optional.
- Tightened worked-example alignment.
- Limited very simple arithmetic to purposeful retrieval once learner evidence supports progression.
- Preserved fraction number-line and visual safeguards.

## Recently completed release, 0.32.0, Parent Learning Intelligence

- Added plain-language parent learning summaries generated from learner evidence.
- Distinguished first-attempt, eventual, independent and supported success.
- Added Secure, Developing, Needs Support, Review Due and Not Enough Evidence skill states.
- Added evidence confidence, recommendations, misconception grouping, prerequisite visibility, retention and spaced-review status.
- Added 7, 30 and 90-day learning comparisons.

## Further learner experience improvements

- Expand adventure themes and context where real usage shows it improves engagement without weakening mathematical clarity.
- Improve continuity between learner recommendations, Daily Practice and Story Adventure.
- Continue refining Grade 5 question variety and appropriate difficulty based on evidence from real sessions.
- Add further visual models only where they materially improve mathematical understanding.

## Later opportunities

- Deeper Parent Learning Intelligence and learning-goal planning.
- Additional verified Victorian Curriculum coverage.
- Richer Visual Mathematics models and manipulatives after evidence from real learner use.
- Dependency/security maintenance without unsafe forced upgrades.
- Performance and Home Assistant operational improvements where real usage demonstrates a need.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
