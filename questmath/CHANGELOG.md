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

## MathQuest 0.3.1

- Fixed typed answers not being recognised on iPhone and iPad.
- Check answer now activates as soon as a valid answer is entered.
- Added Return-key submission for typed answers.

# MathQuest 0.3.1

- Renamed QuestMath to MathQuest.
- Added the slogan “Sienna’s daily adventure in maths.”
- Replaced legacy topic generation with Victorian Curriculum F–10 Version 2.0 Level 4-aligned practice across Number, Algebra, Measurement, Space, Statistics and Probability.
- Added VCAA content-description codes to generated questions and tracking.
- Added a parent curriculum tracker, areas-to-review flags and recent incorrect-answer review.
- Updated reports and displayed version to 0.3.1.
