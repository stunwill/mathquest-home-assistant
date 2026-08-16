# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.27.0

This release addresses the worksheet usability and review problems reported during v0.26.0 testing. It is a focused learner-experience release and does not change the completed v0.26.0 intervention or reporting scope.

### Session selection clarity

- Restyle **Targeted practice**, **Levels 2–6 diagnostic**, session-length choices and learning-area choices as unmistakably interactive controls.
- Use the current MathQuest design tokens instead of undefined legacy CSS variables.
- Give the selected option a persistent border, background and accessible selected state that remains clear with keyboard focus and on mobile.
- Add interaction tests proving each choice updates the session configuration used when the worksheet starts.

### Visual hints for symmetry

- Add a reusable regular-polygon visual to rotational-symmetry questions.
- When a hint is requested, show the original and rotated positions or an accessible rotation animation so Sienna can compare whether the shape matches itself.
- Respect reduced-motion preferences and provide an equivalent static before-and-after representation.
- Keep the hint progressive and avoid stating the assessed answer before the permitted reveal stage.

### Question naming and repetition

- Display Story Adventure chapter and challenge context as a separate label instead of embedding phrases such as a chapter name and **challenge 1** in the mathematical question prompt.
- Keep the core question wording concise in live worksheets and completed worksheet reviews while preserving existing historical records.
- Extend duplicate protection beyond a single worksheet so an identical prompt and choice set is not selected again from Sienna's recent learner history.
- Apply recent-history duplicate protection to standard, timed, recommended, intervention and Story Adventure creation without including parent tests in learner history.
- Add more than one statistical-investigation survey variant so the fixed favourite-fruit question is not repeatedly selected.
- Use a bounded recent-history window and a safe fallback so small question banks can still create a complete worksheet.

### Worksheet review and modal accessibility

- Render each question's stored visual payload in **View worksheet**, using the same React visual component as the live worksheet.
- Preserve the exact historical visual rather than generating a new one during review.
- Close worksheet-review and parent-test-review modals with the close button, the Escape key or a click on the backdrop outside the dialog.
- Keep clicks inside the dialog from closing it, restore focus to the opener and expose an accessible dialog label.

### Keyboard worksheet flow

- Let Enter submit the current typed answer when **Check answer** is available.
- After final feedback is displayed, let Enter activate **Next question** or **Finish worksheet**.
- Do not trigger worksheet actions while focus is in the scratchpad, a multiline note, another modal or an unrelated control.
- Prevent repeated keydown events or a held key from submitting twice or skipping past feedback.
- Add React interaction coverage for typed, choice, retry, final-answer and final-question keyboard paths.

## Recently completed release, 0.26.0

- Targeted Number and Algebra interventions with 5, 10 and 15-minute sessions.
- Interactive fraction, number-line, place-value, array and grid models with question-specific visual identity.
- React-owned worksheet tools, saved answer drafts and reduced legacy DOM enhancement layers.
- Reconciled learner evidence with independent and supported results separated and parent tests excluded.

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
- Clear selected and keyboard-focus states for session, duration and learning-area controls.
- Keyboard submission and continuation across the full worksheet feedback flow.
- Dismissible, focus-managed worksheet review dialogs with original question visuals.

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
- Prevent exact recent-history repeats across consecutive learner worksheets while retaining a bounded fallback.
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
| Completed | 0.26.0 | Number and Algebra intervention, interactive learning, platform reliability and reporting corrections | Merged and released |
| Current | 0.27.0 | Worksheet usability, visual symmetry hints, review fidelity and keyboard flow | Session choices are visibly selectable, repeated prompts are avoided, reviews reproduce stored visuals, modals dismiss accessibly and Enter supports the complete answer-to-next-question flow |

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

The 0.27.0 release groups the seven findings reported after v0.26.0 because they affect one end-to-end path: choosing a session, understanding a question, using a hint, completing it efficiently and reviewing the original result accurately.

## Recommended priority

The current release should deliver and validate the v0.27.0 worksheet usability and review corrections. The key gate is that Sienna can clearly choose a session, receive an appropriate visual symmetry hint, avoid an immediate repeat, use Enter through the answer and continuation flow, then review the exact original question and visual in a modal that dismisses by button, Escape or backdrop click. No release after 0.27.0 is sufficiently defined yet, so the following release requires a product decision after this release is reviewed and merged.
