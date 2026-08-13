# MathQuest 0.16.3

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to Victorian Curriculum F–10 Version 2.0 Level 4.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Duplicate-safe question generation with visual question guardrails
- Question overview and navigation status panel
- Immediate feedback and one retry
- Six Level 4 strands and VCAA content-description codes
- Adaptive strand weighting and difficulty
- Parent curriculum tracker, support flags and incorrect-answer review
- CSV and PDF reports
- SQLite backup and restore API
- Home Assistant ingress and persistent `/data` storage
- Installation-specific JWT signing and failed-login throttling

## Upgrade compatibility

The app slug and database path remain `questmath`, preserving the existing Home Assistant app identity and `/data/questmath.db`. The visible product name is MathQuest.

Version 0.16.2 also persists its JWT signing secret separately at `/data/jwt-signing-secret`. Upgrading from the public legacy signing value can invalidate existing sessions, so users may need to sign in again. The database is not changed or replaced.
