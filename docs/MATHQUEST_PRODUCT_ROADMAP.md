# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current implemented release, 0.30.0, Visual Mathematics

This release builds on v0.29.1 Learning Intelligence and its corrective safeguards. It turns the existing worksheet visuals, Interactive Maths Lab, Math Mentor and learning evidence into one reusable Visual Mathematics system.

### Equal-whole fraction comparison

- Compare fractions against equal-sized wholes, vertically aligned to the same origin.
- Preserve visible denominator partitions, numerator shading and written fraction notation.
- Support fraction-bar, equivalent-fraction and shared number-line representations.
- Keep mathematical proportions accurate across desktop, tablet, mobile and Home Assistant ingress.

### Interactive fraction models

- Let the learner change numerator and denominator values while the written fraction and visual model remain synchronised.
- Show equivalent forms such as 1/2 and 2/4 without filling the assessed answer.
- Place fractions on a common number line and support improper fractions using repeated equal-sized wholes.
- Keep manipulatives learner-controlled and optional.

### Reusable visual systems

- Share reusable fraction, number-line, array, place-value and measurement components between worksheet visuals and the Maths Lab.
- Continue existing clock, grid, angle, chart and symmetry visuals without creating a third parallel rendering system.
- Keep question data responsible for describing the mathematics while components render it.

### Multiple solution strategies

- Provide suitable questions with more than one valid strategy, including partitioning, compensation, place value, arrays, inverse relationships, equivalent fractions and number lines.
- Show one alternative strategy at a time through **Show another way**.
- Preserve the current answer, worksheet position, Math Mentor state and Maths Lab state when another strategy is viewed.

### Math Mentor and learning evidence

- Recommend a question-appropriate visual model and explain how the representation matches the calculation.
- Use repeated v0.29 misconception evidence to suggest optional visual support when practical.
- Prefer recommendations such as “Try comparing these with equal-whole fraction bars” instead of opening tools automatically.
- Keep retry-first behaviour unchanged after incorrect answers.

### Assessment integrity and accessibility

- Use different values for teaching examples and never generate a teaching payload that deliberately reuses the assessed values.
- Suppress the new teaching strategies, visual recommendations and evidence-driven recommendations in parent tests.
- Preserve v0.29.1 grid answer-leakage protections, grouped-unit wording, duplicate-question repair and keyboard autofocus.
- Provide accessible names and mathematical descriptions for new visual models, keyboard-operable controls and reduced-motion-safe styling.

### Architecture

- Add v0.30 endpoints through an explicit FastAPI `APIRouter` rather than adding another route-list mutation workaround.
- Keep the existing version-layer architecture intact for compatibility during this focused release.
- Defer a broader version-wrapper and route-composition consolidation until it can be isolated behind comprehensive endpoint regression coverage.

### Release acceptance criteria

- Fraction comparison uses equal-sized wholes and clear partitions.
- Fraction manipulatives remain synchronised with written values and support equivalent and number-line representations.
- Major visual families reuse shared components.
- Suitable questions expose multiple strategies one at a time without losing learner state.
- Math Mentor and learning evidence can recommend appropriate optional visual support.
- Parent tests do not receive the new teaching aids automatically.
- Retry-first, keyboard-first and v0.29.1 corrective behaviour remain intact.
- Complete backend, frontend, build, release and validation suites pass before merge.

## Recently completed release, 0.29.1, Learning Intelligence corrective release

- Preserved the v0.29.0 optional tutoring, prerequisite graph, misconception evidence and difficulty balancing.
- Restored labelled grid visuals for grid-reference questions.
- Added keyboard autofocus when a new typed-answer question becomes active.
- Added final semantic duplicate-question prevention after worksheet transformations.
- Clarified grouped word-problem units, including the reviewed meal-portion wording.

## Recently completed release, 0.29.0, Learning Intelligence

- Kept answer entry and **Check answer** available immediately after an incorrect response.
- Aligned worked examples to the same mathematical concept and strategy while using different values.
- Reduced very-easy arithmetic while retaining occasional confidence-building questions.
- Added prerequisite skill links, structured misconception evidence, learning events and parent recommendations.
- Kept parent-test activity excluded from Sienna’s adaptive profile.

## Recently completed release, 0.28.0, Math Mentor Foundation

- Added a consistent learner-facing Math Mentor panel.
- Added Hint, Why?, Teach me, Worked example, Start over and Read aloud actions.
- Added ask-before-tell support with progressive question-family-specific hints.
- Kept parent tests isolated from altered learner assessment behaviour.

## Feature findings from the supplied recordings

### Dynamic visual learning

- Interactive percentage bars with linked percentage, fraction, decimal and quantity values.
- Multiple representations of the same concept with immediate feedback when a model changes.
- A visible learning pathway with small lessons and mastery checkpoints.
- Why? explanations and Start over controls that do not leave the question.

### Guided tutoring and manipulatives

- Brief concept explanation followed by a comprehension check.
- Tutor dialogue that asks the learner to reason instead of revealing the answer.
- Virtual fraction, area, number-line, array and place-value models selected for the concept.
- A sequence of explain, try, inspect, prompt, retry and reflect.

## Consolidated feature backlog

### Learning foundation

- Continue strengthening diagnostic baselines and Level 5 prerequisite pathways.
- Expand spaced retrieval and retention evidence across more outcomes.
- Improve automatic prerequisite teaching selection where misconception evidence is strong.
- Continue upper Grade 5 difficulty calibration across all learning areas.

### Teaching and hints

- Expand visual recommendations to more question families with stronger misconception-to-model mapping.
- Add richer visual worked examples that animate or step through transformations without using assessed values.
- Improve explanation quality testing so written guidance must reference visible model elements.
- Add spoken reasoning only when privacy, browser support and assessment rules are clear.

### Interactive mathematical models

Implemented in v0.30.0:

- Equal-whole fraction comparison bars.
- Interactive numerator and denominator fraction models.
- Equivalent-fraction and common number-line representations.
- Reusable number-line, array, place-value and measurement components.
- Learner-selected multiple strategies and question-specific visual recommendations.

Follow-up candidates:

- Fraction tiles that can be copied, split and moved.
- Area models for multiplication and fraction multiplication when curriculum scope reaches them.
- Richer equal-sharing division manipulatives.
- Explicit base-ten regrouping animation using hundreds, tens and ones blocks.
- More interactive rulers, scaled number lines, data charts and geometry models.
- A visual explanation contract that validates diagram labels against written explanation references.

### Applied practice and engagement

- Continue Story Adventures with coherent multi-question narratives and real mathematical dependencies.
- Expand everyday applications involving money, time, recipes, travel, sport and data.
- Keep celebrations tied to mastery, persistence and independent improvement.

### Learner experience

- Keep session goals and durations clear before starting.
- Preserve previous, next, skip, finish-with-skipped and restart-skipped lifecycle.
- Resume the exact worksheet, question, answer draft and elapsed time.
- Continue accessibility improvements for mobile and Home Assistant ingress.
- Add stronger automated responsive-layout checks for mathematical diagrams.

### Parent insight and Home Assistant

- Baseline level, current estimated level and growth by outcome.
- Independent accuracy separated from hinted accuracy.
- Fluency, response time, retention and review-due reporting.
- Clear recommendations for the next 5, 10 or 15-minute session.
- Weekly summaries of gains, persistent gaps and strategies used.
- Stable `/api/ha/stats` and `/api/ha/summary` data with graceful unavailable states.

### Platform reliability

- Continue replacing legacy version-specific route mutation with explicit router composition when touched by feature work.
- Plan a separate endpoint-composition consolidation rather than rewriting the version stack inside a learner feature release.
- Add frontend component, interaction and end-to-end tests.
- Keep duplicate-question protection in every worksheet and adventure flow.
- Preserve existing database, worksheet history, answers, progress and Home Assistant upgrades.

## Release sequence and delivery gates

Calendar estimates are intentionally excluded. MathQuest releases can be developed quickly, while the meaningful delivery constraint is the review and real-world testing gate. The roadmap is therefore an ordered queue, not a dated schedule.

| Order | Release | Focus | Delivery gate |
| --- | --- | --- | --- |
| Completed | 0.17.2 | Calendar, worksheet completion/restart, Story Adventures and roadmap | Merged and released |
| Completed | 0.18.0 | Frontend and worksheet foundation | Merged and released |
| Completed | 0.19.0 | Diagnostic and timed tutoring | Merged and released |
| Completed | 0.19.1 | Grid and fraction visual correctness | Merged and released |
| Completed | 0.20.0 | Guided tutor and scaffolded hints | Merged and released |
| Completed | 0.21.0 | Interactive maths lab | Merged and released |
| Completed | 0.22.0 | Story Adventures 2.0 | Merged and released |
| Completed | 0.23.0 | Adaptive mastery and retention | Merged and released |
| Completed | 0.24.0 | Parent and Home Assistant insight | Merged and released |
| Completed | 0.25.0 | Parent test worksheets and feedback traceability | Merged and released |
| Completed | 0.26.0 | Number and Algebra intervention, interactive learning, platform reliability and reporting corrections | Merged and released |
| Completed | 0.27.0 | Credential and parent-test reliability, worksheet usability, visual symmetry hints, review fidelity and keyboard flow | Merged and released |
| Completed | 0.28.0 | Math Mentor Foundation | Merged and released |
| Completed | 0.29.0 | Learning Intelligence | Merged and released |
| Completed | 0.29.1 | Corrective grid, autofocus, duplicate and grouped-unit safeguards | Merged and released |
| Current | 0.30.0 | Visual Mathematics: equal-whole fractions, manipulatives, shared visual models, multiple strategies and visual recommendations | Review and Home Assistant test gate before merge |
| Planned | 0.31.0 | Parent Insights: growth reporting, retention analytics, mastery tracking, session recommendations, misconception reports and dashboard enhancements | Parent reporting clearly separates independent, supported and retained understanding |
| Planned | 0.32.0 | Home Assistant Expansion: dashboard improvements, notifications, automations, widgets and integration enhancements | Home Assistant data remains stable, privacy-preserving and non-blocking to local learning |
| Planned | 0.33.0 | Story Adventure Expansion: applied mathematics, curriculum adventures, quest progression, unlockables and challenge content | Story content maps to current curriculum goals and does not weaken adaptive learning evidence |

### Continuous delivery loop

1. Lock the next release to a small, independently testable scope.
2. Develop the complete scope, including version references, changelog and documentation.
3. Run backend tests, frontend type/build checks, release validation and the relevant regression tests.
4. Open a pull request and stop for Stu's testing and review.
5. Fix findings on that same release branch until it passes.
6. After Stu merges the pull request, detect the merge and begin the next release in the queue.

No release receives a promised date or week count. A release remains at its gate for as long as testing or correction requires.

### How new work enters the queue

- Critical security, data-loss or blocking reliability defects may interrupt the queue as a tightly scoped patch release.
- Ad-hoc bugs and enhancements reported during an active release are assessed and added to the next planned release rather than silently expanding the active release.
- Related ad-hoc items may be grouped into the upcoming release when this makes implementation and testing more coherent.
- The active release remains scope-locked unless explicitly expanded or required for release correctness.
- Every Home Assistant-delivered release must bump all required version references and changelog entries so the app detects the update.

## Recommended priority after v0.30.0

After Visual Mathematics passes the Home Assistant review gate, the next release remains v0.31.0 Parent Insights. It should turn the existing learning evidence into clearer growth, retention and misconception reporting without expanding v0.30.0 into unrelated parent-dashboard work.
