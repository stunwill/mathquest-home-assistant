# MathQuest 0.29.0

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
- Number & Algebra Focus quests for targeted fact recall and equation practice
- Contextual strategy cards, written subtraction regrouping and retention review indicators
- Three-stage guided tutoring across arithmetic, fractions, measurement, grids, time, data and equations
- A responsive Interactive Maths Lab available from every question
- Coherent Story Adventures with adaptive learning goals, shared mission data, chapter progress and final outcomes
- Outcome mastery, deterministic spaced reviews, prerequisite routing and personalised next-session recommendations
- Parent reporting for diagnostic and outcome growth, independent and supported accuracy, weekly progress, retention and review-due learning
- Persistent Home Assistant service authentication and dashboard-ready category, outcome and recommendation metrics
- Parent-only test worksheets with isolated test evidence, question and overall notes, feedback status and addressed-release traceability
- Number and Algebra interventions that select the weakest prerequisite, teach with linked models and report independent understanding separately
- React-owned question visuals and support tools with per-question visual identity and saved answer drafts
- Reconciled worksheet, calendar, parent and Home Assistant evidence counts
- Configuration-managed parent and student credentials that safely update existing accounts on restart
- Reliable parent test navigation with optional notes and isolated learner evidence
- Visual rotational-symmetry hints, recent-question duplicate protection and faithful worksheet-review visuals
- Accessible review dialogs and keyboard-first answer and continuation flow
- Collapsible Math Mentor panels with question-specific guided recovery, worked examples and browser text-to-speech support
- Optional retry-first tutoring, operation-aligned examples, prerequisite graph evidence, misconception signals and parent-only recommendations

## Upgrade compatibility

The app slug and database path remain `questmath`, preserving the existing Home Assistant app identity and `/data/questmath.db`. The visible product name is MathQuest.

MathQuest persists its JWT signing secret separately at `/data/jwt-signing-secret` and its Home Assistant service token at `/data/ha-service-token`. Upgrading from the public legacy JWT signing value can invalidate existing sessions, so users may need to sign in again. The database is not changed or replaced.

Change parent and student usernames or passwords in the Home Assistant add-on Configuration page, save, then restart MathQuest. Startup reconciles those values with the existing managed accounts without replacing their IDs or learning data.
