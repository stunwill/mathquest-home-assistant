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
