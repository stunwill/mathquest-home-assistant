# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.32.1, Worksheet Learning Quality Corrective Release

This corrective release preserves v0.32.0 Parent Learning Intelligence while tightening real-session worksheet quality before moving to the next feature release.

### Optional wrong-answer support

- Preserve immediate retry after an incorrect answer.
- Keep Math Mentor, hints and worked examples optional at every retry point.
- Preserve misconception and adaptive-learning evidence from incorrect attempts.
- Keep keyboard-first answer entry and autofocus behaviour.

### Worked-example alignment

- Match worked examples to the current operation, skill, question family or mathematical representation.
- Use different values from the assessed question and avoid revealing its answer.
- Cover Probability, fraction number lines, Measurement, Space and Statistics in addition to the existing operation-specific arithmetic examples.
- Expose alignment metadata so automated tests can verify the relationship between the assessed question and its teaching example.

### Purposeful easy-question retrieval

- Retain simple arithmetic for warm-up, confidence, prerequisite checks, recovery and spaced retrieval.
- Once recent learner evidence supports progression, limit trivial arithmetic to a small retrieval allowance rather than allowing it to dominate the worksheet.
- Tag questions as retrieval, instructional or challenge work so future adaptive logic can reason about worksheet composition explicitly.

### Question-family diversity after adaptive transforms

- Re-check structural family diversity after later difficulty and worksheet transformations.
- Avoid parameter-only or effectively identical repeated question families when a suitable alternative exists.
- Preserve intentional repeated practice when the available pool is constrained or learning evidence justifies retrieval.

### Visual and Probability safeguards

- Preserve denominator-accurate fraction number lines.
- Preserve Probability visual relevance safeguards.
- Preserve existing visual question state isolation and visual-key behaviour.

### Release acceptance criteria

- A wrong answer can be retried immediately without opening Math Mentor.
- Worked examples use the same solving structure or representation but different values.
- Very easy questions remain possible but do not dominate a normal evidence-supported worksheet.
- Question-family diversity remains intact after final worksheet transformations.
- Existing scoring, completion, visuals, Story Adventures, Parent Learning Intelligence and Parent Test isolation remain unchanged.
- Complete backend, frontend, TypeScript/Vite build, version and release-validation suites pass before merge.

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

## Recently completed release, 0.30.1, Worksheet Quality corrective release

- Changed completion **Strongest** and **Practise next** recommendations to use broader persisted learner evidence.
- Added neutral completion wording when cross-category evidence is insufficient.
- Added question-family diversity so parameter-only variants are treated as repeats within short worksheets.
- Corrected denominator-based fraction number-line subdivisions and misleading rounded tick labels.
- Prevented unrelated number-line teaching recommendations on Probability questions.

## Recently completed release, 0.30.0, Visual Mathematics

- Added reusable Visual Mathematics components for equal-whole fraction comparison, number lines, arrays, place value and measurement.
- Added Interactive Maths Lab fraction manipulatives, equivalent-fraction and shared number-line representations.
- Added optional alternate solution strategies without changing learner answer state.
- Connected Math Mentor and misconception evidence to relevant optional visual support.
- Preserved parent-test assessment integrity and v0.29.1 corrective safeguards.

## Recently completed release, 0.29.1, Learning Intelligence corrective release

- Restored labelled grid-reference visuals after final question transformations.
- Preserved typed-answer autofocus for each new question.
- Added final semantic duplicate prevention after worksheet transformations.
- Clarified grouped-unit wording, including meal portions versus packs.
- Preserved the v0.29.0 learning-intelligence model and retry-first behaviour.

## Recently completed release, 0.29.0, Learning Intelligence

- Made Math Mentor optional after an incorrect answer.
- Added aligned worked examples with different values.
- Reduced very-easy arithmetic and increased moderate/challenging practice.
- Added persisted attempt, support and misconception evidence.
- Added prerequisite skill links and early parent recommendations.

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
