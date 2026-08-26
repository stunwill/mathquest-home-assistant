# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.32.2, Grade 5 Algebra Variety

This focused update extends the Algebra question bank without replacing existing Algebra practice or changing the planned v0.33.0 feature release.

### Grade 5 Algebra variety

- Add numerical pattern continuation, including increasing, decreasing and simple multiplicative patterns.
- Add symbolic addition and subtraction unknowns with varied letters.
- Add basic substitution into addition and multiplication expressions.
- Add mystery-number and contextual unknown-start problems that bridge arithmetic and symbolic reasoning.
- Add reverse multiplication and doubling questions using division as the inverse operation.
- Keep generated values within age-appropriate whole-number ranges.

### Healthy question mixture

- Keep the existing Algebra generators active and authoritative.
- Introduce the new structures as a minority share of eligible Algebra generation rather than the entire question pool.
- Give each structure a semantic family so worksheet-level diversity can prevent runs of effectively identical equations with different values.
- Preserve intentional retrieval and prerequisite practice where adaptive evidence calls for it.

### Tutoring and evidence

- Give every new structure question-specific strategy guidance, progressive hints and a different-number worked example.
- Reinforce inverse-operation reasoning and the meaning of a supplied variable value rather than revealing answers.
- Preserve scoring, retry-first behaviour, misconception evidence, adaptive evidence and worksheet completion behaviour.

### Victorian Curriculum handling

- Use verified Victorian Curriculum Version 2.0 Level 5 Algebra outcomes for multiplication/division inverse reasoning and unknown multiplication/division equations.
- Treat addition/subtraction unknowns and simple substitution as scaffold/retrieval practice where they do not exactly match the Level 5 Algebra descriptors, rather than inventing or mislabelling curriculum codes.
- Preserve the existing broader Level 5 pathway and diagnostic adaptation architecture.

### Release acceptance criteria

- New Algebra structures appear naturally alongside existing Algebra questions.
- A normal Algebra worksheet avoids repeated structural forms where alternatives exist.
- Generated answers remain mathematically correct and whole-number appropriate.
- Hints and worked examples use the same structure with different values and do not reveal the assessed answer.
- Complete backend, frontend, TypeScript/Vite build, version and release-validation suites pass before merge.

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

### 0.33.0, Home Assistant Parent Integration

- Parent notifications and weekly learning summaries.
- Home Assistant entities/sensors for key learning states and recommendations.
- Useful parent alerts for review due, persistent support needs and notable progress.
- Preserve local-first privacy and avoid notification overload.

### 0.34.0, Story Adventure Expansion

- Use the stronger learner model to drive adaptive Story Adventure missions.
- Make story challenges respond to mastery, prerequisites and retrieval needs rather than simply wrapping generic worksheets.
- Expand continuity, progression and themed mathematical models.

## Later opportunities

- Deeper adaptive curriculum sequencing using explicit worksheet difficulty-band composition.
- Richer visual mathematics models and manipulatives.
- Longer-term learning trend reporting.
- Teacher/tutor reporting views.
- Additional curriculum coverage.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
