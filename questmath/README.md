# MathQuest 0.35.1

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
- Parent Dashboard reliability safeguards for loading, retry and optional-section failure
- SQLite persistence and Home Assistant backup support

## v0.35.1 corrective release

This release fixes a Parent Learning Intelligence render crash caused by inconsistent React hook ordering during the initial null-to-loaded data transition. It also makes required Parent Dashboard startup failures visible and retryable, while backups and optional learning intelligence no longer block the core dashboard.

The Home Assistant add-on continues to use the standard ingress declaration in `config.yaml`. MathQuest does not define a `/ingress/validate_session` application route, so Home Assistant ingress validation remains outside the MathQuest API surface.

## Home Assistant parent learning

Use the dedicated parent-facing Home Assistant endpoints with the service token shown in the Parent Dashboard:

- `/api/ha/learning`
- `/api/ha/weekly-summary`
- `/api/ha/stats`
- `/api/ha/summary`

MathQuest remains the authoritative source for learning state and recommendations.
