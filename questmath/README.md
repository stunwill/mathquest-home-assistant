# MathQuest 0.31.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to Victorian Curriculum F–10 Version 2.0 Level 4, with learning progression targeted toward upper Grade 5 mathematics.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Duplicate-safe question generation with visual question guardrails
- Question overview and navigation status panel
- Immediate retry-first feedback with optional Math Mentor support
- Tablet-first learner worksheet optimisation for portrait and landscape use
- Six Level 4 strands and VCAA content-description codes
- Adaptive strand weighting and progressive difficulty
- More instructional-level Number practice with hundreds, regrouping and decomposition when learner evidence supports it
- Parent curriculum tracker, support flags and incorrect-answer review
- CSV and PDF reports
- SQLite backup and restore API
- Home Assistant ingress and persistent `/data` storage
- Number & Algebra Focus quests for targeted fact recall and equation practice
- Question-specific Teach me mini-lessons using the actual problem structure
- Three distinct hint stages: nudge, strategy and worked next step
- Question-aligned worked examples using different values from the assessed question
- Interactive Maths Lab and shared Visual Mathematics components
- Outcome mastery, deterministic spaced reviews, prerequisite routing and personalised next-session recommendations
- Parent reporting for diagnostic and outcome growth, independent and supported accuracy, weekly progress, retention and review-due learning
- Parent-only test worksheets with isolated test evidence and feedback
- React-owned worksheet visuals and support tools with per-question visual identity and saved answer drafts
- Reconciled worksheet, calendar, parent and Home Assistant evidence counts
- Accessible review dialogs and keyboard-first answer and continuation flow
- v0.30.1 corrective guards for learner-wide completion recommendations, semantic question-family diversity, fraction number lines and Probability visual relevance

## Upgrade compatibility

The app slug and database path remain `questmath`, preserving the existing Home Assistant app identity and `/data/questmath.db`. v0.31.0 adds no destructive database migration and preserves existing worksheets, answers, attempts, learning evidence, progress and user IDs.

MathQuest persists its JWT signing secret separately at `/data/jwt-signing-secret` and its Home Assistant service token at `/data/ha-service-token`. Existing secrets and service tokens remain valid across this upgrade.
