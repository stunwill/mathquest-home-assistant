# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.34.0, Story Adventure Expansion and Purposeful Daily Learning

This release makes Story Adventure a meaningful presentation layer over the same adaptive learning decisions used by Daily Practice. MathQuest decides what Sienna should practise, consolidate, review or progress to before Story Adventure adds mission context and lightweight progression.

### One learning engine

- Create the adaptive learning plan and selected maths questions before Story Adventure presentation is applied.
- Preserve skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- Remove the runtime path that could independently replace adaptive worksheet questions with a separate Story Adventure generator.
- Keep learning decisions backend-authoritative.

### Short coherent adventures

- Use reusable adventure themes with a setting, objective, stages and clear ending.
- Support the existing 5, 10 and 15-minute session choices without requiring a long mission to be finished in a short session.
- Provide lightweight stage and mission progress without introducing a game engine or heavy animation dependency.
- Keep the maths clear when a selected skill is better presented directly rather than forced into an awkward story problem.

### Evidence integrity

- Record Story Adventure answers through the same worksheet, attempt, support, misconception and mastery evidence used by equivalent Daily Practice.
- Preserve first-attempt independence, eventual success, supported success, repeated errors and retention evidence.
- Do not treat Story Adventure completion, stage progress or rewards as mastery evidence.
- Keep Parent Tests isolated from Story Adventure framing, rewards and adaptive recomposition.

### Tutoring and learner experience

- Preserve immediate retry after an incorrect answer.
- Keep Hint, Teach me, Worked example and Math Mentor optional.
- Preserve question-specific teaching and operation-aligned worked examples.
- Reuse Visual Mathematics only where it supports understanding.
- Keep responsive controls usable on desktop, tablet, mobile and Home Assistant ingress.

### Release acceptance criteria

- Story Adventure preserves the adaptive questions selected for the session.
- Learning purpose and difficulty metadata survive Story Adventure presentation.
- Prerequisite, consolidation, misconception repair, spaced review and challenge decisions can be represented without a second selection engine.
- Insufficient or highly supported evidence cannot be promoted merely because the learner is in an adventure.
- Story Adventure evidence feeds the existing learning model and story completion alone does not increase mastery.
- Parent Tests remain isolated.
- Unfinished Story Adventures resume using the existing worksheet state instead of creating duplicates.
- 5, 10 and 15-minute Story Adventures use appropriately sized timed sessions.
- Frontend validation uses the committed dependency lockfile and `npm ci` before tests and production build.
- Full backend, frontend, production build, version and release-validation checks pass before merge.

## Recently completed release, 0.33.0, Adaptive Daily Learning

- Classified practice questions as current learning, consolidation, spaced review or limited challenge from learner evidence.
- Added controlled progression requiring repeated independent success before challenge increases.
- Made progression support-aware and misconception-aware.
- Reused spaced-review evidence and preserved deliberate easy retrieval when it has a learning purpose.
- Kept Parent Tests isolated from adaptive session composition.

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

### Likely next focus, Home Assistant Parent Integration

- Parent notifications and weekly learning summaries.
- Home Assistant entities/sensors for key learning states and recommendations.
- Useful parent alerts for review due, persistent support needs and notable progress.
- Preserve local-first privacy and avoid notification overload.
- Reconfirm the semantic version against the repository state when implementation begins rather than pre-allocating it here.

### Further learner experience improvements

- Expand adventure themes and context where real usage shows it improves engagement without weakening mathematical clarity.
- Improve continuity between learner recommendations, Daily Practice and Story Adventure.
- Continue refining Grade 5 question variety and appropriate difficulty based on evidence from real sessions.
- Add richer visual models where they improve understanding rather than decoration.

## Later opportunities

- Richer visual mathematics models and manipulatives.
- Longer-term learning trend reporting.
- Teacher/tutor reporting views.
- Additional curriculum coverage.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
