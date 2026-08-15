# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.25.0

This release gives the parent account a persistent quality-testing workflow for validating worksheets and tracing feedback into later releases.

- Let a parent create and complete Number, Algebra, Measurement, Space, Statistics, Probability, Number and Algebra, or mixed test worksheets.
- Generate parent test questions from Sienna's enabled learning areas and adaptive profile while storing the attempt under the parent account.
- Keep all parent test answers, hints, time, completion and scores out of Sienna's progress, mastery, XP, streak, calendar and recommendations.
- Let the parent add structured bug, enhancement or general notes after completing each test question.
- Let the parent add overall notes after completing a test worksheet.
- Provide a parent test history with in-progress resume, completed test review, question context, answers and saved notes.
- Track feedback as open, planned, addressed or deferred.
- Require addressed feedback to identify the semantic release number that delivered the correction or enhancement.
- Show open and addressed feedback counts and addressed release numbers for every completed test worksheet.
- Preserve all existing learner worksheets and data while adding a compatible feedback table.
- Correct parent reporting so one diagnostic does not claim zero measured growth before a repeat diagnostic exists.
- Add backend and React regression coverage for parent-only access, feedback lifecycle, release traceability, learning-data isolation and responsive presentation.

## Recently completed release, 0.24.0

- Parent reporting for diagnostic and outcome growth, independent and supported accuracy, fluency, retention and review dates.
- Seven-day learning summaries, recent gains, persistent gaps, practised strategies and recommended sessions.
- Complete Home Assistant category and outcome learning metrics.
- Persistent, narrowly scoped Home Assistant service authentication and graceful unavailable states.

## Feature findings from the supplied recordings

### Dynamic visual learning, inspired by the percentage demonstration

- Interactive percentage bars with draggable endpoints and linked numeric values.
- Multiple representations of the same concept, such as percentage, fraction, bar length and quantity.
- Immediate visual feedback when a model is changed.
- A visible learning pathway with small lessons and mastery checkpoints.
- A **Why?** explanation that can be opened without leaving the problem.
- **Start over** for resetting a model and trying a different strategy.
- Progressive examples that move from simple benchmark percentages to less obvious values.
- Correctness feedback attached to the model, not only to a text answer.

### Guided tutoring and manipulatives, inspired by the fraction demonstration

- Brief concept explanation followed immediately by a comprehension check.
- Tutor dialogue that asks Sienna to reason instead of revealing the answer.
- Virtual fraction tiles and area models that can be copied, split, moved and compared.
- On-demand manipulatives selected for the current misconception.
- A sequence of explain, try, inspect, prompt, retry and reflect.
- Optional read-aloud narration with synchronised visual steps.
- Positive feedback and small moments of celebration without distracting from the maths.
- Mixed response modes, including manipulation, multiple choice, typed values and spoken reasoning later.

## Consolidated feature backlog

### Learning foundation

- Diagnostic baseline mapped to Victorian Curriculum outcomes across Levels 2–6.
- Level 5 target pathway with prerequisite links to earlier concepts.
- Time-based 5, 10 and 15-minute sessions instead of relying only on fixed 20-question worksheets.
- Outcome-level mastery based on accuracy, independence, hint use, fluency and retention.
- Real spaced-retrieval scheduling with due dates for each skill.
- Automatic selection of prerequisite teaching when a misconception is detected.
- Number and Algebra intervention pathway covering all four operations, fact families, written methods and unknown-value equations.

### Teaching and hints

- Three-stage hints: a conceptual cue, a strategy or visual prompt, then a worked next step.
- Question-type-specific hints for arithmetic, fractions, measurement, grids, time, data and equations.
- Guided tutor mode that asks one question at a time and does not expose the final answer prematurely.
- Short worked examples using different numbers from the assessed question.
- **Why?**, **Teach me this**, **Show another way** and **Start over** actions.
- Read-aloud for prompts, hints and explanations.
- Confidence and misconception checks that influence the current session.

### Interactive mathematical models

- Fraction tiles, fraction walls, area models and equivalent-fraction builders.
- Fraction-comparison bars stacked vertically, aligned to the same origin and scaled to an equal whole so relative amounts can be compared directly.
- Percentage bars linked to fractions, decimals and quantities.
- Open number lines and jump strategies for addition and subtraction.
- Place-value blocks and regrouping models for written operations.
- Arrays and equal-group models for multiplication and division.
- Interactive analogue clocks, rulers, grids, coordinates, angles and data charts.
- Scratchpad, drawing and reusable manipulatives available from every question.

### Applied practice and engagement

- Story Adventures 2.0 with a coherent multi-question narrative, themed data and a final mission outcome.
- Story difficulty and learning outcomes selected from Sienna's current goals.
- Everyday word problems involving money, time, recipes, travel, sport and data.
- Choice of standard practice, guided lesson, Story Adventure or review session.
- Meaningful progress celebrations tied to mastery and persistence rather than only XP.

### Learner experience

- Clear session goal and estimated duration before starting.
- Previous, next, skip, finish-with-skipped and restart-skipped lifecycle.
- Resume the exact worksheet, question, answer draft and elapsed time.
- Accessible mobile and Home Assistant layouts.
- Reliable offline/local operation with clear recovery messages.
- Replace browser alerts with in-page error and recovery states.

### Parent insight and Home Assistant

- Baseline level, current estimated level and growth by outcome.
- Independent accuracy separated from hinted accuracy.
- Fluency, response time, retention and review-due reporting.
- Clear recommendations for the next 5, 10 or 15-minute session.
- Weekly summaries of gains, persistent gaps and strategies used.
- Stable `/api/ha/stats` and `/api/ha/summary` data with graceful unavailable states.
- Long-lived Home Assistant service authentication so dashboard entities do not expire daily.
- Category and outcome progress for Number, Algebra, Measurement, Space, Statistics and Probability.

### Platform reliability

- Consolidate the three worksheet-creation paths into one service.
- Replace MutationObserver feature layers with React-owned components and state.
- Add frontend component, interaction and end-to-end tests.
- Keep duplicate-question protection in every worksheet and adventure flow.
- Improve authentication expiry handling and eliminate silent or alert-only failures.
- Preserve existing database, worksheet history, answers, progress and Home Assistant add-on upgrades.
- Parent-only test worksheets with question and overall feedback, status tracking and addressed-release traceability.

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
| Current | 0.25.0 | Parent test worksheets and feedback traceability | Parent testing remains isolated from learning evidence, notes persist with question context, and addressed items show a valid release number |

### Continuous delivery loop

1. Lock the next release to a small, independently testable scope.
2. Develop the complete scope, including version references, changelog and documentation.
3. Run backend tests, frontend type/build checks, release validation and the relevant regression tests.
4. Open a draft pull request and stop for Stu's testing and review.
5. Fix findings on that same release branch until it passes.
6. After Stu merges the pull request, detect the merge and begin the next release in the queue.

No release receives a promised date or week count. The loop may complete several times in a day when development, automated checks and Stu's testing are all completed quickly. A release remains at its gate for as long as testing or correction requires.

### How new work enters the queue

- Critical security, data-loss or blocking reliability defects may interrupt the queue as a tightly scoped patch release.
- Ad-hoc bugs and enhancements reported during an active release are assessed and added to the next planned release development, rather than interrupting or reshuffling the release already underway.
- Related ad-hoc items may be grouped into that upcoming release when this makes implementation and testing more coherent.
- The active release remains scope-locked unless Stu explicitly asks to include an item, or the item is required for that release to function correctly.
- If a security, data-loss or application-blocking defect appears serious enough to interrupt the queue, raise it for Stu's decision before changing the release sequence.
- Every Home Assistant-delivered release must bump all required version references and changelog entries so the add-on detects the update.

Parent Test Worksheets and Feedback Traceability reuses the worksheet experience and question generator, but stores its evidence under the parent account and keeps it separate from Sienna's adaptive learning history.

## Recommended priority

The current release should deliver and validate Parent Test Worksheets and Feedback Traceability. The key gate is that Stu can test the real worksheet flow, record actionable question-level and overall feedback, review it later, and see which release addressed each item without changing any of Sienna's learning evidence. No release after 0.25.0 is sufficiently defined yet, so the next release requires a product decision after this release is reviewed and merged.
