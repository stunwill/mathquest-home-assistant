# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.32.3, Grade 5 Method-First Math Mentor

This focused learning-quality update improves Grade 5 Hints and Worked Examples without changing the planned v0.33.0 feature release.

### Method-first tutoring

- Teach the mathematical idea before relying on a shortcut, formula or operation label.
- Preserve progressive Hint 1 concept, Hint 2 first-step and Hint 3 method support.
- Avoid revealing the active answer where practical.
- Use a complete worked example with different values so the learner must still apply the method independently.

### Written multiplication

- Work from the ones column through tens and hundreds.
- Explain carrying in place-value language.
- Connect the compact written algorithm to partial products and partitioning so the learner can see why it works.

### Division by partitioning

- Break dividends into convenient multiples of the divisor when appropriate.
- Divide each part and combine the partial quotients.
- Check the result using multiplication as the inverse operation.

### Decimal fractions

- Teach tenths and hundredths through decimal place value.
- Add age-appropriate questions asking for a decimal to be written as a fraction out of 100.
- Preserve denominator 100 when the question specifically requires “out of 100” rather than automatically simplifying.

### Perimeter and area

- Establish perimeter as the distance around the outside before introducing 2 × (length + width).
- Explain why the rectangle perimeter shortcut works from two equal lengths and two equal widths.
- Establish area as counting square units inside the rectangle.
- Connect length × width to rows and columns of square units rather than teaching it only as a formula.
- Reinforce cm for perimeter and cm² for area.

### Release acceptance criteria

- Multiplication hints teach written place-value calculation without revealing the current product.
- Division hints support useful partitioning and an inverse multiplication check.
- Decimal-fraction tutoring explains hundredths and preserves denominator 100 when requested.
- Perimeter tutoring explains around-the-outside meaning before the shortcut formula.
- Area tutoring explains square units and distinguishes area from perimeter.
- Worked examples use different values from the active question wherever possible and remain mathematically valid.
- Existing adaptive difficulty, Algebra variety, retry-first Math Mentor, Visual Mathematics, worksheet scoring, Story Adventures and parent reporting remain unchanged.
- Complete backend, frontend, TypeScript/Vite build, version and release-validation suites pass before merge.

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
