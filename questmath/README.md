# MathQuest 0.35.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Duplicate-safe question generation with visual question guardrails
- Immediate retry-first feedback with optional Math Mentor support
- Tablet-optimised worksheet and tutoring layouts
- Adaptive strand weighting and progressive difficulty
- Adaptive Daily Learning using current learning, consolidation, spaced review and challenge purposes
- Controlled skill progression requiring independent evidence before challenge increases
- Story Adventure over the same backend-authoritative adaptive learning plan as Daily Practice
- Story Adventure evidence recorded through the same worksheet, attempt, misconception and mastery architecture
- Parent Tests isolated from learner mastery and normal daily-learning completion
- Parent Learning Intelligence with plain-language summaries, independent versus supported success, evidence confidence, recommendations, misconception grouping and retention
- Home Assistant parent-learning integration with daily completion, learning focus, review due, support dependence, misconceptions, meaningful progress and weekly summary
- Persistent local Home Assistant service token and stable read-only learning endpoints
- Method-first Math Mentor, aligned worked examples, Visual Mathematics and Interactive Maths Lab
- SQLite persistence and Home Assistant backup support

## Home Assistant parent learning

v0.35.0 makes the existing learning intelligence useful outside the MathQuest UI without creating a second mastery system. Home Assistant reads a compact backend-generated learning state from `/api/ha/learning` and `/api/ha/weekly-summary` using the existing local service token.

Daily Practice and Story Adventure count as daily learning only when a learner session is completed with answered-question evidence. Parent Tests, opening the app, starting a worksheet and abandoned no-evidence sessions do not satisfy daily learning.

The Home Assistant contract exposes a small number of stable concepts rather than dozens of internal metrics. It includes current learning purpose, evidence confidence, review-due state, persistent support dependency, repeated misconception evidence, meaningful progress and a seven-day parent summary. Parent Dashboard and Home Assistant derive from the same Parent Learning Intelligence helpers.

## Adaptive Story Adventures

Story Adventure remains a presentation layer over MathQuest's adaptive learning engine. Story progression never counts as mastery. Correctness, attempts, support use, misconception evidence and retention continue to determine learning progress through the same evidence model used by Daily Practice.

## Adaptive daily learning

Questions can be marked as current learning, consolidation, quick review or a limited challenge. Progression is conservative: the learner needs repeated independent success before MathQuest increases challenge, while high support dependency or repeated misconception evidence keeps a skill in consolidation. Parent Tests remain excluded.

## Parent Learning Intelligence

The parent dashboard is designed to answer what is improving, what needs support, whether success is independent, what to practise next, why MathQuest recommends it, whether previously learned skills are being retained, and whether current difficulty is appropriate.

MathQuest avoids strong conclusions when there is insufficient evidence. Home Assistant preserves that behaviour and exposes states such as Building evidence and No review due rather than fabricating conclusions.
