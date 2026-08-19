# MathQuest 0.29.0

- Made Math Mentor support optional after an incorrect answer. Sienna can immediately edit and resubmit an answer without opening a hint or completing a tutoring step.
- Added question-specific, operation-aligned worked examples that use different values and the same reasoning strategy as the displayed question.
- Reduced very-easy arithmetic items outside occasional confidence-building positions and increased moderate, challenging and application generation.
- Added persisted learning evidence for attempts, first-attempt success, hints, worked examples, retries and misconception evidence signals.
- Added prerequisite skill links for core Number, Algebra, Measurement and fraction outcomes.
- Added parent-only early recommendations for recurring misconceptions and spaced retrieval.
- Added backend and frontend regression coverage for optional tutoring, aligned examples, misconception detection, prerequisite graphs, recommendations and worksheet difficulty balance.
- Updated the canonical roadmap and release metadata to v0.29.0.

# MathQuest 0.28.0

- Added the Math Mentor, a lightweight collapsible tutoring panel on every worksheet question.
- Added ask-before-tell guided recovery after an incorrect learner answer, keeping the question retryable before an answer is revealed.
- Added progressive, question-family-specific support for arithmetic, equations, fractions, measurement, grids, time and data.
- Added Math Mentor **Hint**, **Why?**, **Teach me**, **Worked example**, **Start over** and **Read aloud** actions.
- Added distinct-number worked examples, common-mistake cues and family-specific memory tips without exposing the assessed answer.
- Added browser read aloud fallback messaging so unsupported browsers retain the complete worksheet flow.
- Kept parent test assessment behaviour unchanged while allowing parent test questions to inspect Math Mentor content.
- Added backend, interaction and accessibility regression coverage for mentor progression, restart and read-aloud fallback.
- Updated the canonical roadmap with the approved v0.28.0 to v0.33.0 release sequence.

# MathQuest 0.27.0

- Fixed Home Assistant parent and student credential changes so existing managed accounts are updated on restart without changing their IDs or losing worksheet data.
- Fixed parent test worksheets returning **Worksheet not found** after a correctly accepted answer.
- Made question-level and overall parent test notes explicitly optional without blocking navigation, completion or return to the dashboard.
- Corrected duplicated wording such as **Use use a known double** in addition feedback.
- Added shared worksheet lifecycle authorisation for learner worksheets and parent-owned test worksheets.
- Made session type, duration and learning-area choices visibly selectable with persistent, accessible selected states.
- Added regular-polygon visuals and before-and-after rotation hints for rotational-symmetry questions, including reduced-motion support.
- Removed Story Adventure chapter and challenge prefixes from maths prompts while retaining mission context separately.
- Added recent learner-history duplicate protection and more statistical-survey question variants while excluding parent tests from learner history.
- Added stored question visuals to completed learner and parent-test worksheet reviews.
- Added Escape-key, backdrop-click and focus-return behaviour to worksheet review dialogs.
- Added Enter-key support for both submitting typed answers and moving to the next question or finishing a worksheet.
- Added backend and React regression coverage for credential upgrades, parent-test completion, optional notes, session choices, symmetry hints, duplicate avoidance, review fidelity and keyboard flow.

# MathQuest 0.26.0

- Added targeted 5, 10 and 15-minute Number and Algebra intervention sessions.
- Added intervention coverage for addition, subtraction, multiplication, division, fact families, written methods and unknown-value equations.
- Added check, teach, practice and retrieval phases with progressively supported learning goals.
- Added question-specific model recommendations for number lines, place value, arrays and fraction comparisons.
- Added **Why?**, **Show another way** and **Start over** support without revealing the assessed answer.
- Moved question visuals, read-aloud, scratchpad, confidence checks and guided support into the React worksheet experience.
- Added stable per-question visual identities so images cannot carry over from a previous question.
- Added saved per-question answer drafts across previous, next, exit and resume actions.
- Added vertically stacked fraction comparison models aligned to equal-sized wholes.
- Corrected grid visuals so row and column labels are shown on the axes without printing the answer inside the highlighted square.
- Reconciled answered, completed, correct, incorrect, skipped, remaining and hinted counts from one evidence calculation.
- Separated independent accuracy from supported accuracy in intervention and Home Assistant reporting.
- Kept parent test evidence excluded from Sienna's progress, mastery, XP, streak, calendar, recommendations and Home Assistant metrics.
- Reduced legacy worksheet DOM enhancement layers and replaced browser-alert failures with in-page recovery messages.
- Added backend and React regression coverage for interventions, visual ownership, answer drafts, evidence isolation and reporting reconciliation.

# MathQuest 0.25.0

- Added parent-only test worksheet creation for every standard MathQuest learning-area selection.
- Added test attempts that use Sienna's learning profile for question generation while remaining isolated from her progress, mastery, XP, streak, calendar and recommendations.
- Added structured bug, enhancement and general notes after each completed test question.
- Added overall feedback notes after a test worksheet is completed.
- Added parent test history with resume, completed review, question context, answers and saved feedback.
- Added open, planned, addressed and deferred feedback states.
- Added semantic release traceability for feedback marked as addressed.
- Corrected diagnostic growth reporting so a single diagnostic does not imply measured zero growth.
- Added backend and React regression coverage for parent access, learning-data isolation, feedback persistence and release traceability.

# MathQuest 0.24.0

- Added parent reporting for baseline, current estimated curriculum level and diagnostic growth.
- Added outcome growth using comparable early and recent independent-performance windows.
- Added weekly independent and supported accuracy, first-attempt time, hints, learning days and completed activity reporting.
- Added parent summaries of recent gains, persistent gaps, strategies practised and the recommended next 5, 10 or 15-minute session.
- Added outcome mastery, retention, review-due status and all six learning areas to the Home Assistant statistics response.
- Added the weekly learning summary and next-session recommendation to the compact Home Assistant summary response.
- Added a dedicated long-lived Home Assistant service token that persists through restart and upgrade and cannot access general MathQuest endpoints.
- Added a parent dashboard control for revealing and copying the Home Assistant service token.
- Added graceful unavailable responses so optional reporting failures do not break Home Assistant sensors.
- Added backend, security and React regression coverage for reporting, authentication persistence and responsive parent presentation.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant endpoint paths remain unchanged.

# MathQuest 0.23.0

- Added outcome-level mastery using independent and supported accuracy, hint use, fluency, confidence calibration and delayed retention evidence.
- Added deterministic spaced-review due dates and review-due prioritisation using existing persisted learning history.
- Added prerequisite routing that can teach an unsecured supporting outcome before repeating a weak target outcome.
- Added personalised diagnostic, guided, review and practice recommendations sized to 5, 10 or 15 minutes.
- Added direct dashboard creation of recommended sessions, including targeted Number and Algebra question generation.
- Included Story Adventure evidence in the corresponding Level 4 outcome mastery calculations.
- Fixed Space Adventure grid questions whose missing dimensions prevented the grid cells from rendering.
- Fixed Statistics Adventure mode questions so generated readings always have one unambiguous mode.
- Added backend and React regression coverage for adaptive mastery, review scheduling, prerequisite routing, session creation and Story Adventure payload correctness.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant data remain unchanged.

# MathQuest 0.22.0

- Upgraded Story Adventures from themed worksheets into coherent five-chapter missions with clear objectives and final outcomes.
- Added adaptive adventure recommendations that prioritise Sienna's weaker learning areas relevant to each theme.
- Replaced generic story-prefixed questions with theme-specific applied Number, Measurement, Space and Statistics challenges.
- Added shared mission data and multi-step calculations that remain connected across each adventure.
- Added in-question mission, chapter pathway and current learning-focus progress.
- Added a mission-completion outcome with skipped-question recovery guidance.
- Preserved guided tutoring, Interactive Maths Lab access, scoring, progress, duplicate protection and restart-skipped behaviour.
- Added backend and React regression coverage for adaptive goals, narrative continuity, mission progress and outcomes.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant data remain unchanged.

# MathQuest 0.21.0

- Added a React-owned Interactive Maths Lab available from every worksheet question.
- Added adjustable equal-whole fraction comparisons and linked percentage, fraction, decimal and quantity representations.
- Added interactive number lines, place-value columns, multiplication arrays, analogue clocks, labelled grids, rectangles, rulers and angle models.
- Added question-aware model recommendations while keeping every maths tool available for learner choice.
- Added responsive desktop, mobile and Home Assistant layouts plus a model-level **Start over** control.
- Fixed Algebra multiplication and division facts receiving unknown-equation tutor guidance.
- Prevented worked examples from reusing the assessed inputs or exposing a colliding final answer.
- Prevented tutor **Start over** from clearing a final question result and blocking normal worksheet navigation.
- Added backend and frontend regression coverage for the Maths Lab, model interactions and guided-tutor follow-up defects.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant data remain unchanged.

# MathQuest 0.20.0

- Added an ask-before-tell guided tutor with three progressively stronger hint stages: conceptual cue, strategy prompt and worked next step.
- Added question-specific guidance for arithmetic, fractions, measurement, grids, time, data and unknown-value equations.
- Added **Why?**, **Teach me this**, **Show another way** and **Start over** actions within the worksheet.
- Added different-number worked examples that demonstrate a method without revealing the assessed question's final answer.
- Routed detected misconceptions into the tutor panel after an incorrect attempt.
- Added read-aloud support for guided hints and explanations while retaining existing prompt narration.
- Added regression coverage for all representative question families, three-stage progression, tutor actions, answer protection and route ordering.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant data remain unchanged.

# MathQuest 0.19.1

- Fixed grid-reference questions so row letters and column numbers appear outside the grid instead of printing complete references inside every cell.
- Removed the highlighted square's visible and interactive answer value so the visual no longer gives away the correct response.
- Changed fraction comparisons to vertically stacked, left-aligned rows whose bars use the same whole width for direct visual comparison.
- Preserved each fraction's denominator partitions, shaded numerator, learner label and written value across desktop, mobile and Home Assistant layouts.
- Added frontend and source-level regression coverage for grid answer leakage, external axis labels, fraction partitions and equal-whole stacked layout.
- Corrected the roadmap patch version after v0.19.0 diagnostic and timed tutoring had already been released.
- Existing users, worksheets, answers, diagnostic results, progress and Home Assistant data remain unchanged.

# MathQuest 0.19.0

- Added a short Number and Algebra diagnostic with three questions at each Victorian Curriculum level from 2–6 and an explicit Level 5 learning target.
- Added selectable 5, 10 and 15-minute targeted practice sessions with question counts sized to the chosen duration.
- Added persisted session type and target duration metadata using additive database migration columns that preserve existing worksheets and answers.
- Added a latest-diagnostic summary API reporting evidence and accuracy at each assessed level.
- Added learner session planning controls and backend regression coverage for timed sessions, diagnostic coverage and database upgrades.

# MathQuest 0.18.0

- Consolidated all new worksheet requests onto the authoritative duplicate-safe backend creation service, removing the later route-replacement layer.
- Rebuilt student worksheet history, weekly completion calendar and Story Adventures as React-owned components rather than DOM-rewriting enhancement scripts.
- Replaced global active-worksheet `fetch` interception with explicit worksheet-ID loading and resume state.
- Added reusable in-page connection and action errors with retry and dismissal controls for authentication, dashboard, worksheet, history, calendar and adventure flows.
- Added frontend component and interaction tests covering the creation service, Story Adventure start flow, history controls, calendar recovery and accessible error feedback.
- Removed the legacy v0.16 calendar and worksheet-picker scripts from the production page while retaining existing worksheet data and API compatibility.
- Updated all authoritative release locations and startup messaging to `0.18.0`.
- Existing users, worksheets, answers, progress, XP, database data and persisted secrets remain unchanged.

# MathQuest 0.17.2

- Fixed completion-calendar navigation and expanded the calendar to the full dashboard width, with the duplicate Badges panel removed.
- Allowed worksheets to be finished once every unanswered question has been explicitly skipped.
- Added **Restart skipped questions**, which creates a focused follow-up worksheet without changing the completed worksheet's score, XP or history.
- Fixed Story Adventure cards so they create and immediately open a dedicated worksheet for the selected story.
- Regenerated Story Adventure questions from theme-appropriate learning areas and added chapter-based contextual prompts throughout each adventure.
- Fixed a visual-loading race so rapid question changes retry against the newly mounted question card instead of attaching to a detached card.
- Added a product roadmap combining the supplied learning-system recordings with previously identified MathQuest priorities.
- Updated all authoritative release locations and startup messaging to `0.17.2`.
- Existing users, worksheets, answers, progress and persisted secrets remain unchanged.

# MathQuest 0.17.1

- Added a **Previous question** control that returns to the nearest earlier unfinished, skipped or retryable question while keeping completed results read-only.
- Fixed grid-reference and other visual questions retaining the image from the previous question by keying question cards to their question ID and rejecting mismatched injected visuals.
- Ensured weak, hinted and due Number and Algebra focus skills influence the generated practice questions, not only the strand-level topic weights.
- Fixed make-ten addition questions so the second addend always contains enough to complete ten.
- Fixed direct-subtraction generation so equal ones digits use the dedicated equal-digits strategy instead of contradictory guidance.
- Added navigation, visual identity, grid payload and strategy edge-case regression coverage.
- Updated all authoritative release locations and startup messaging to `0.17.1`.
- Existing users, worksheets, answers, progress and persisted secrets remain unchanged.

# MathQuest 0.17.0

- Added a recommended **Number & Algebra Focus** quest containing only those two Victorian Curriculum strands.
- Added deliberate fact-recall practice for addition, subtraction, multiplication facts to `10 × 10`, and related division facts.
- Added efficient mental strategies including make-ten, doubles, near-doubles, inverse facts, multiplication patterns and fact families to reduce reliance on finger counting.
- Added written addition and subtraction practice with question-specific strategy cards.
- Added subtraction guidance for the three column cases: subtract directly when the top digit is larger, regroup from the next place when it is smaller, and write zero when the digits match.
- Added a worked place-value lesson for `81 − 8` that explains regrouping 8 tens and 1 one into 7 tens and 11 ones before subtracting.
- Expanded unknown-value Algebra questions across addition and subtraction equation forms, with inverse-operation hints and substitution checks.
- Added Number and Algebra focus reporting for independent accuracy, hint use, average response time, last practice and retention review status.
- Connected the new skills to MathQuest's existing hint-aware mastery and spaced-review weighting so weak, hinted and due outcomes receive further practice.
- Added HTTP, generation, hint, strategy, capability and teaching-lesson regression coverage.
- Updated all authoritative release locations and the production entrypoint to `0.17.0`.
- Existing users, worksheets, progress, `/data/questmath.db` and `/data/jwt-signing-secret` remain unchanged.

# MathQuest 0.16.3

- Added version-consistency validation directly to the release workflow before any existing-tag check or GitHub Release publication.
- Added an explicit Python 3.12 setup and pinned YAML parser dependency so release validation is reproducible on GitHub Actions.
- Changed pull-request release-note validation to extract notes for the version configured in `questmath/config.yaml` instead of the hard-coded `0.16.2` section.
- Added regression coverage for release validation order, configured-version note extraction and version agreement.
- Updated all required add-on, backend, frontend, startup and documentation version locations to `0.16.3`.
- No database, authentication, worksheet or learning-engine behaviour is changed by this patch.

# MathQuest 0.16.2

- Replaced the public development JWT signing secret with a cryptographically secure, installation-specific secret persisted at `/data/jwt-signing-secret` with restrictive permissions where supported.
- Added support for a deliberately configured `SECRET_KEY` environment value and safe replacement of the legacy `development-only-change-me` value.
- Added fail-closed startup behaviour when a secure signing secret cannot be loaded or persisted.
- Added bounded, in-memory throttling for repeated failed logins, including `429 Too Many Requests`, `Retry-After`, recovery after the retry window and credential-safe structured security events.
- Stopped blindly trusting arbitrary forwarded client-address headers. Uvicorn now trusts only its configured proxy policy when determining the client used for rate limiting.
- Consolidated first and additional worksheet creation through one authoritative duplicate-safe service.
- Duplicate identity now includes the normalized prompt and normalized choices, where present.
- Added bounded generation retries and a shorter valid worksheet fallback when the enabled question pool cannot supply the requested number of unique questions.
- Added HTTP-level regression tests for the real `/api/worksheets/today` and `/api/worksheets/new` routes, category selection and insufficient unique pools.
- Fixed release-note extraction for the repository's existing changelog heading format and added automated release-note extraction validation.
- Added automated version-consistency validation across Home Assistant metadata, backend, frontend, startup messaging and documentation.
- Updated FastAPI, frontend, add-on and documentation release metadata to `0.16.2` and removed older enhancement scripts' competing visible-version mutations.
- Existing databases and `/data/questmath.db` remain unchanged. The JWT secret rotation invalidates tokens signed with the old public value, so users may need to sign in again after updating.

# MathQuest 0.16.1

- Fixed a frontend observer loop that repeatedly recreated the **Today overall** worksheet summary in the student hero.
- Marked the hero as enhanced before loading worksheet history, removed stale duplicate summaries and appended one stable summary after the data request completed.
- Updated Home Assistant, frontend and startup release metadata to `0.16.1`.

# MathQuest 0.16.0

- Added exact worksheet resume so an incomplete worksheet can be continued by ID without a reload switching to another worksheet.
- Added answered/total progress, elapsed learning time and dedicated continue/review actions to worksheet history.
- Replaced the old 28-day completion grid with a navigable seven-day learning activity view covering questions, accuracy, correct/incorrect totals, hints, XP, duration and linked worksheets.
- Added `GET /api/worksheets/history-v0160`, `GET /api/learning/week-v0160?start=YYYY-MM-DD` and `GET /api/v0160/capabilities`.
- Improved analogue teaching clocks with all twelve hour numbers and minute tick marks while preserving existing hand positioning.
- Preserved existing worksheet data, visual questions, visual hints, multiple worksheets per day, parent reporting, Home Assistant statistics, review and adaptive learning behaviour.

# MathQuest 0.15.0

- Fixed inherently visual questions rendering without the diagram required to answer them.
- Analogue-clock questions now reliably show a clock face with correctly positioned hour and minute hands.
- Angle-identification questions now show the angle itself and ask the learner to identify the type from the diagram.
- Added a pre-React visual guard so required visuals no longer depend on the earlier frontend fetch timing race.
- Added a clear visual-unavailable fallback so an unanswerable visual question is never silently presented.
- Fixed `+ New worksheet` so it always creates a genuinely new worksheet even when another worksheet from today remains incomplete.
- Existing unfinished worksheets remain safely available in worksheet history and do not get overwritten.
- Added worksheet-generation protection against repeated question prompts within the same worksheet.
- Added duplicate-choice protection so the correct answer appears only once in multiple-choice questions.
- Kept Level 1 Measurement practice focused on practical units, clocks and simple angle identification for now; area/perimeter and advanced reflex/revolution angle work is deferred to higher levels/later work.
- Added regression tests for visual clocks, visual angles, duplicate choices, repeated questions and starting a second same-day worksheet.
- Updated runtime, frontend and Home Assistant app metadata to 0.15.0.

# MathQuest 0.14.0

- Fixed the student hero incorrectly treating an unfinished worksheet from a previous date as today's active quest.
- Today's active worksheet is now strictly scoped to the current calendar date.
- Previous unfinished worksheets remain in worksheet history but no longer block creation of a new worksheet today.
- Added explicit previous-unfinished worksheet metadata so old work is visible without being confused with today's progress.
- Added `quest_today` to `/api/ha/stats` and `/api/ha/summary`, including exists/status/worksheet ID/topic/questions answered/questions total/started time.
- Added `unfinished_previous_worksheets` to Home Assistant statistics.
- Home Assistant daily totals continue to aggregate only worksheets belonging to today's date.
- Parent daily statistics now use the same authoritative date-scoped worksheet logic as the student experience and HA API.
- Improved worksheet history metadata with `is_today` and `is_previous_unfinished` flags.
- Added regression tests proving old unfinished worksheets cannot become today's quest or today's Home Assistant statistics.
- Preserved multiple worksheets per day, completed worksheet review, visual hints, adaptive learning, Teaching Mode, Story Adventures and existing dashboard statistics.
- Updated runtime, frontend and Home Assistant app metadata to 0.14.0.

# MathQuest 0.13.0

- Added visual learning hints for fractions, number lines, place value, clocks, angles, grids, area/perimeter and sequences.
- Fraction comparisons can show equal-sized fraction circles and aligned fraction bars without revealing the final answer.
- Preserved written hints as a fallback when a reliable visual model cannot be derived.

# MathQuest 0.12.1

- Fixed API/SPА route ordering so JSON endpoints are matched before the frontend fallback.
- Hardened frontend API handling and retained the sidebar load/freeze fixes.

# MathQuest 0.12.0

- Added multiple worksheets per day and worksheet history.
- Added completed worksheet review for students and parents.
- Improved learner resolution for parent reporting.

# MathQuest 0.11.0

- Added stable authenticated `GET /api/ha/stats` and lightweight `GET /api/ha/summary` endpoints for Home Assistant dashboards.
- Exposes real current learner data for questions, correct/incorrect answers, accuracy, hints, completed activities, streak, daily/total XP, recommended topic and last activity.
- Added dashboard category statistics for Number, Measurement, Space, Algebra and Probability with progress, accuracy, question count and hint-aware mastery.
- Reuses the existing adaptive topic metrics and mastery calculations rather than maintaining a second learning-statistics implementation.
- Added optional rolling seven-day questions, accuracy, hints, activities and XP statistics.
- Added a stable relative `app_path` without hard-coding Home Assistant's session-specific ingress URL.
- Added defensive category aggregation so missing optional statistics return null/zero values without breaking the complete dashboard response.
- Documented Home Assistant REST sensor configuration, units, timestamp handling, refresh interval, authentication and a dashboard card example.
- Added backend regression tests for zero activity, accuracy, category statistics, hints, completion/last activity and compact summary output.
- Updated CI so backend tests run on every PR alongside compile, frontend TypeScript/Vite build and Home Assistant YAML validation.
- Updated runtime, frontend and Home Assistant app metadata to 0.11.0.

# MathQuest 0.10.0

- Added browser-based read-aloud support for questions using Australian English speech, including short descriptions of visual question content.
- Added an on-screen scratchpad so students can keep working notes beside a question without affecting assessment or mastery signals.
- Added interactive maths manipulatives selected for the current question, including fraction tiles, place-value blocks, rulers, grid tokens and grouping counters.
- Added drag-and-drop modelling for fraction pieces, counters and place-value blocks, with touch-friendly supporting layouts.
- Added a rolling seven-day parent learning report covering learning days, questions attempted, first-attempt accuracy, hints, XP, confidence and skill mastery.
- Added plain-English weekly parent summaries highlighting the strongest current evidence and the most useful next focus.
- Preserved v0.9 skill mastery, confidence-aware adaptation, Teaching Mode, misconception detection and Story Adventures.
- Updated runtime, frontend and Home Assistant app metadata to 0.10.0.

# MathQuest 0.9.0

- Added skill-level mastery tracking across individual Victorian Curriculum outcomes rather than only broad learning areas.
- Added student confidence tracking (I guessed, Pretty sure, I knew it) as an additional mastery signal.
- Added dynamic in-quest difficulty adjustment, allowing remaining questions to move up or down after strong independent confidence or demonstrated difficulty.
- Added Teaching Mode with short explanations, worked examples and step-by-step guidance when repeated difficulty is detected.
- Added misconception detection for common fraction, perimeter/area, grid-reference and analogue-clock errors.
- Added Story Adventures including Bakery Challenge, Camping Adventure, Space Mission and Animal Rescue, linking several questions into a shared narrative.
- Added a v0.9 capability API and student/parent skill-mastery view.
- Preserved v0.8 visual maths, parent Practice Quests, printable worksheet capture and adaptive spaced revision.
- Updated runtime, frontend and Home Assistant app metadata to 0.9.0.

# MathQuest 0.8.0

- Added a full parent Practice Quest builder with topic selection, question count and optional due dates.
- Added assignment lifecycle tracking so quests can move through Assigned, In Progress, Overdue and Completed states.
- Added support for creating targeted practice directly from MathQuest learning recommendations.
- Added richer visual question formats including fraction comparisons, number lines, analogue clocks, angles, bar charts and grids.
- Added story-based maths questions that place curriculum skills into everyday contexts such as sharing food, shopping, measurement and other real-world situations.
- Added support for entering answers from printed worksheets back into MathQuest so paper work can still contribute to mastery tracking.
- Added a question-format capability endpoint for validating which visual and storytelling formats are available.
- Updated runtime, frontend and Home Assistant app metadata to 0.8.0.

# MathQuest 0.7.0

- Added parent learning insights that translate mastery, hint dependence and spaced revision into plain-English recommendations.
- Added 7, 30 and 90 day progress datasets covering accuracy, independent mastery, hint usage and completion time.
- Added improved rewards for independent problem solving, streaks and learning breakthroughs.
- Added Mastery Moments that recognise concepts completed independently after previously needing hints or correction.
- Added parent-created Practice Quest assignments with selected learning areas, question counts and optional due dates.
- Added a Home Assistant status API exposing today's completion, score, streak, accuracy, XP, hints, recommended topic and revision-due areas.
- Updated the MathQuest by Stu visual identity to match the DinnerHub and MediaHub brand family, using a rounded emblem, bold wordmark and script-style by Stu treatment.
- Updated runtime, frontend and Home Assistant app metadata to 0.7.0.

# MathQuest 0.6.0

- Added hint-aware adaptive mastery so independent correct answers contribute 1.0 mastery, Hint 1 answers 0.7, Hint 2 answers 0.4 and incorrect answers 0.
- Added automatic targeted practice that increases the likelihood of questions from learning areas and curriculum outcomes needing more support.
- Added spaced revision using 1, 3, 7 and 14 day review intervals, with stronger emphasis on concepts that remain below mastery.
- Added more contextual two-stage hints tailored to common Level 4 question types without revealing the final answer.
- Added printable student worksheets from the quest selector and from an existing in-progress worksheet.
- Printing a worksheet now starts that day's worksheet, marks it In Progress, stores its current position and preserves it for later continuation in MathQuest.
- Printable worksheets include student name, date, selected quest, In Progress status, all questions and answer space, without answers or solution steps.
- Kept existing parent hint analytics and scoring unchanged while using hint dependence internally to improve future adaptive question selection.
- Updated runtime and application metadata to 0.6.0.

# MathQuest 0.5.0

- Added student-requested hints that guide the next step without revealing the answer.
- Added per-question hint tracking and repeat-safe hint delivery.
- Added parent hint analytics by learning area, including hint counts, questions using hints and hint rates.
- Added recent hint activity so parents can see where support is being requested most often.
- Added hint usage to worksheet summaries and progress reporting.
- Added a MathQuest by Stu brand treatment aligned with MediaHub and DinnerHub, with a dedicated maths emblem.
- Improved the parent dashboard with clearer learning-support signals alongside accuracy.
- Updated runtime and displayed version metadata to 0.5.0.

# MathQuest 0.4.0

- Added a student learning-area selector before a new daily worksheet begins.
- Added focused worksheets for Measurement, Algebra, Probability, Number, Space and Statistics.
- Added a Mixed Adventure option spanning all enabled Level 4 strands.
- Stored the selected learning area with each worksheet for future reporting.
- Preserved parent topic controls, adaptive difficulty and resume behaviour.

# MathQuest 0.3.1

- Fixed typed-answer input handling so Check answer activates reliably on iPhone and iPad.
- Added Return-key submission for typed answers.
- Updated displayed and runtime version metadata to 0.3.1.
