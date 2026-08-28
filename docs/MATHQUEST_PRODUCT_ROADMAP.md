# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.33.0, Adaptive Daily Learning

This release makes daily 5, 10 and 15-minute sessions use the learning evidence MathQuest already collects when deciding the purpose and progression of worksheet questions.

### Adaptive daily session composition

- Classify practice questions as current learning, consolidation, review or challenge.
- Use learner evidence rather than rigid fixed percentages.
- Keep challenge deliberately limited so a short session remains balanced.
- Preserve deliberate easy retrieval when it has a learning purpose.

### Controlled progression

- Require enough repeated independent evidence before marking a skill ready to progress.
- Treat high support dependency as evidence that more consolidation is appropriate even when eventual accuracy is high.
- Avoid advancing from one or two successful questions.
- Avoid dropping difficulty permanently after one isolated mistake.
- Centralise progression thresholds so future adjustments are explainable and testable.

### Retention and misconception integration

- Use existing spaced-review evidence to identify quick-review opportunities.
- Use repeated misconception evidence to hold a skill in consolidation before increasing difficulty.
- Keep prerequisite intervention targeted rather than turning the whole worksheet into low-level practice.

### Learner and parent explainability

- Attach a short learning-purpose label such as Quick review, Practising this skill or Today’s challenge.
- Store a parent-readable reason explaining why the adaptive engine selected that purpose.
- Do not expose raw mastery scores or algorithm internals to the learner.

### Release acceptance criteria

- Insufficient evidence cannot trigger progression.
- Strong repeated independent performance can trigger a limited challenge opportunity.
- Heavy hint or Math Mentor use slows progression.
- A single wrong answer does not destroy an otherwise secure trend.
- Repeated misconception evidence triggers consolidation.
- Parent Tests remain isolated from adaptive recomposition.
- Existing post-transform family diversity, fraction visuals, method-first tutoring, Grade 5 Algebra variety and Parent Learning Intelligence remain intact.
- Full backend, frontend, production build, version and release-validation checks pass before merge.

## Recently completed release, 0.32.3, Grade 5 Method-First Math Mentor

- Improved written multiplication, partition division, decimal hundredths, perimeter and area tutoring.
- Preserved progressive hints and different-number worked examples.
- Connected formulas and written methods back to mathematical meaning and place value.

## Recently completed release, 0.32.2, Grade 5 Algebra Variety

- Added numerical pattern continuation, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- Mixed new structures into the existing Algebra pool instead of replacing established practice.
- Added semantic structural-family diversity so numeric variants do not disguise repetitive templates.
- Preserved adaptive difficulty, learning evidence, Math Mentor and worksheet-quality safeguards.

## Recently completed release, 0.32.1, Worksheet Learning Quality Corrective Release

- Preserved immediate retry after an incorrect answer with Math Mentor remaining optional.
- Tightened worked-example alignment across Probability, fractions, Measurement, Space and Statistics.
- Limited very simple arithmetic to purposeful retrieval once learner evidence supports progression.
- Re-checked question-family diversity after final adaptive transforms.
- Preserved denominator-accurate fraction number lines and visual state isolation.

## Recently completed release, 0.32.0, Parent Learning Intelligence

- Added plain-language parent learning summaries generated from learner evidence.
- Distinguished first-attempt, eventual, independent and supported success.
- Added Secure, Developing, Needs Support, Review Due and Not Enough Evidence skill states.
- Added evidence confidence, prioritised practice recommendations, misconception grouping, prerequisite visibility, retention and spaced-review status.
- Added difficulty calibration using independent accuracy, eventual accuracy and support dependency together.
- Added 7, 30 and 90-day learning comparisons.
- Preserved Parent Test isolation and existing learner-facing adaptive behaviour.

## Recently completed release, 0.31.0, Tablet Learning and Math Mentor Refinement

- Optimised the live worksheet for tablet portrait and landscape use.
- Raised appropriate Number practice toward hundreds-based addition and subtraction when learner evidence supports progression.
- Made Teach me question-specific and based on the actual operands and mathematical structure.
- Split hints into distinct nudge, strategy and worked-next-step stages.
- Removed duplicated tutoring presentation and improved mathematical formatting.
- Preserved retry-first behaviour, keyboard autofocus, Visual Mathematics and v0.30.1 corrective safeguards.

## Upcoming release sequence

### 0.34.0, Home Assistant Parent Integration

- Parent notifications and weekly learning summaries.
- Home Assistant entities/sensors for key learning states and recommendations.
- Useful parent alerts for review due, persistent support needs and notable progress.
- Preserve local-first privacy and avoid notification overload.

### 0.35.0, Story Adventure Expansion

- Use the stronger learner model to drive adaptive Story Adventure missions.
- Make story challenges respond to mastery, prerequisites and retrieval needs rather than simply wrapping generic worksheets.
- Expand continuity, progression and themed mathematical models.

## Later opportunities

- Richer visual mathematics models and manipulatives.
- Longer-term learning trend reporting.
- Teacher/tutor reporting views.
- Additional curriculum coverage.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
