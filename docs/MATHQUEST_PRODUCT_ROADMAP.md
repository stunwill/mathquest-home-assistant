# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.26.0

This release combines the next agreed educational and reliability work into one testable improvement to Number and Algebra tutoring, interactive models and trustworthy reporting.

### Number and Algebra intervention

- Deliver a targeted intervention pathway for addition, subtraction, multiplication and division.
- Build fluent recall through fact families, related facts, decomposition, bridging through tens and efficient mental strategies instead of finger counting.
- Teach and practise written methods, including place-value alignment, regrouping and exchanging, with question-specific subtraction support.
- Include unknown-value equations in different positions so Algebra practice tests inverse operations and relational understanding rather than answer recall.
- Use short diagnostic checks to identify prerequisite gaps and route the session to the appropriate intervention before returning to grade-level work.
- Support 5, 10 and 15-minute intervention sessions with clear goals, a small number of focused questions and later retrieval checks.
- Measure independent performance separately from performance completed with hints, tutor support or interactive models.

### Interactive learning expansion

- Stack fraction comparison models vertically, align them to the same origin and scale them to an equal whole so relative amounts are visually comparable.
- Add open number-line jump strategies for addition and subtraction.
- Add place-value and regrouping models for written addition and subtraction.
- Add arrays and equal-group models for multiplication and division.
- Select the model and progressively stronger hints from the operation, question structure and detected misconception.
- Provide **Why?**, **Show another way** and **Start over** controls without revealing the final answer prematurely.
- Keep labels, highlights and generated images tied to the current question so the visual never exposes the answer or carries over from a previous question.

### Platform reliability

- Consolidate worksheet creation behind one shared service for learner worksheets, timed sessions, recommendations, Story Adventures and parent tests.
- Replace remaining MutationObserver feature layers in the worksheet experience with React-owned components and state.
- Preserve exact question, image, answer draft, elapsed time, skip state and hint state across previous, next, exit and resume actions.
- Prevent duplicate questions and stale visual payloads across standard, intervention, adventure and parent-test flows.
- Replace silent failures and browser alerts with accessible in-page errors and recovery actions, including expired-authentication handling.
- Preserve the existing database, worksheet history, answers, progress, parent test feedback and Home Assistant add-on upgrade path.
- Add component, interaction, API and end-to-end regression coverage for the affected worksheet paths.

### Reporting corrections

- Reconcile worksheet totals, completed, correct, incorrect, hinted, skipped and remaining counts across the live worksheet, completion summary, calendar and parent reports.
- Keep parent test activity excluded from Sienna's learning history, mastery, XP, streak, calendar, recommendations and Home Assistant learner metrics.
- Report growth only when enough comparable evidence exists, and clearly distinguish insufficient evidence from no improvement.
- Keep independent, hinted and tutor-supported performance separate in parent and Home Assistant reporting.
- Ensure calendar navigation and worksheet links open the correct day and worksheet, with no duplicated badge panel in the calendar section.
- Add regression tests that compare the parent dashboard, calendar and Home Assistant statistics against the underlying learner worksheet evidence.

## Recently completed release, 0.25.0

- Parent-only test worksheets using Sienna's learning profile without changing her learning evidence.
- Structured question and overall notes with open, planned, addressed and deferred states.
- Completed test review with question context, attempts, correct answers, working, timing and feedback.
- Semantic release traceability for addressed bugs and enhancements.
- Corrected diagnostic reporting so a single result does not imply measured zero growth.

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
| Completed | 0.25.0 | Parent test worksheets and feedback traceability | Merged and released |
| Current | 0.26.0 | Number and Algebra intervention, interactive learning, platform reliability and reporting corrections | A focused intervention selects appropriate strategies and models, worksheet state remains reliable across navigation and resume, and learner reporting reconciles without parent-test contamination |

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

The 0.26.0 release builds on the adaptive mastery, guided tutoring, interactive lab and parent-testing foundations. Its four workstreams are delivered together because the intervention must use reliable worksheet state and trustworthy reporting to measure whether the new teaching support improves independent understanding.

## Recommended priority

The current release should deliver and validate the Number and Algebra intervention, its linked interactive models, the worksheet reliability work needed to support it and corrected reporting. The key gate is that Sienna can complete a focused short session using appropriate strategies and models, then the parent and Home Assistant views accurately distinguish independent understanding from supported completion. No release after 0.26.0 is sufficiently defined yet, so the following release requires a product decision after this release is reviewed and merged.
