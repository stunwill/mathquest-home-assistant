# MathQuest 0.3.1

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to Victorian Curriculum F–10 Version 2.0 Level 4.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Daily generated worksheet
- Save and exit, resume, skip-for-now and skipped-question round
- Question overview and navigation status panel
- Immediate feedback and one retry
- Six Level 4 strands and VCAA content-description codes
- Adaptive strand weighting and difficulty
- Parent curriculum tracker, support flags and incorrect-answer review
- CSV and PDF reports
- SQLite backup and restore API
- Home Assistant ingress and persistent `/data` storage

## Upgrade compatibility

The app slug and database path remain `questmath`, preserving the existing Home Assistant app identity and `/data/questmath.db`. The visible product name is MathQuest.
