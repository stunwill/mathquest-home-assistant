# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.17.2

- Working completion-calendar navigation in one full-width section.
- No duplicate Badges panel beside the calendar.
- Previous-question navigation for unfinished questions.
- Correct visual identity when moving between questions.
- Finish a worksheet after every unresolved question has been explicitly skipped.
- Restart skipped questions as a separate focused follow-up worksheet.
- Story Adventure cards create, contextualise and immediately open a dedicated themed worksheet.
- Number and Algebra fact recall, written methods, missing-number equations and question-specific strategy hints.

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

## Expected release plan

| Release | Focus | Expected outcome | Indicative effort |
| --- | --- | --- | --- |
| 0.17.2 | Current reliability release | Calendar, worksheet completion/restart, Story Adventures and roadmap | Current draft PR |
| 0.18.0 | Frontend and worksheet foundation | One worksheet creation service, React-owned calendar/adventures, frontend tests and reliable error states | 1–2 weeks |
| 0.19.0 | Diagnostic and timed tutoring | Levels 2–6 diagnostic, Level 5 pathway and 5/10/15-minute sessions | 2–3 weeks |
| 0.20.0 | Guided tutor and scaffolded hints | Ask-before-tell tutor flow, three-stage hints, Why/another-way/start-over actions and misconception routing | 2–3 weeks |
| 0.21.0 | Interactive maths lab | Fractions, percentages, number lines, place value, arrays, clocks, grids and measurement manipulatives | 3–5 weeks |
| 0.22.0 | Story Adventures 2.0 | Coherent missions driven by learning goals, themed data and applied multi-step problems | 2–3 weeks |
| 0.23.0 | Adaptive mastery and retention | Outcome-level mastery, prerequisite graph, due-date scheduling and confidence/fluency feedback loops | 2–3 weeks |
| 0.24.0 | Parent and Home Assistant insight | Growth reporting, next-session recommendations, stable HA service token and dashboard metrics | 1–2 weeks |

The indicative total is 13–21 weeks if releases are completed sequentially. The interactive maths lab is the largest item and should not begin until the frontend architecture and automated interaction tests are in place.

## Recommended priority

The next major release should be 0.18.0, not the visual maths lab. The current layered frontend is already causing cross-question visuals, broken links and rerendering defects. Consolidating worksheet creation, calendar behaviour and Story Adventures into tested React components will make every later teaching feature faster and safer to build.
