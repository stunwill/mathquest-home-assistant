# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.31.0`

## Features

- Student and parent logins
- Responsive student dashboard
- Tablet-optimised worksheet and tutoring flow
- Multiple daily worksheets with save, exact resume, review and skip support
- Duplicate-safe adaptive question generation and visual learning guardrails
- Victorian Curriculum F–10 Version 2.0 Level 4 alignment
- Curriculum outcome tracking and parent review tools
- Visual questions, visual hints, story adventures and teaching tools
- Weekly learning activity and complete worksheet history
- XP, levels, streaks and badges
- SQLite persistence and Home Assistant backup support
- Home Assistant ingress and sidebar integration
- Dashboard-friendly Home Assistant statistics API
- Installation-specific JWT signing and failed-login throttling
- Recommended Number & Algebra Focus quests with fact-recall, efficient-strategy and retention support
- Adaptive arithmetic that increasingly uses hundreds, regrouping and decomposition when learner evidence supports it
- Question-specific strategy cards for addition, subtraction, multiplication, division and unknown equations
- Three-stage guided hints with distinct nudge, strategy and worked-next-step roles
- Question-specific Teach me mini-lessons that use the current operands without revealing the assessed answer
- Interactive Maths Lab with linked fractions, percentages, number lines, place value, arrays, clocks, grids and measurement models
- Shared Visual Mathematics components for equal-whole fraction comparison, number lines, arrays, place value and measurement
- Optional question-specific visual recommendations and multiple solution strategies without changing the learner's answer
- Story Adventures 2.0 with adaptive learning goals, connected mission chapters, shared themed data and final outcomes
- Outcome-level mastery, spaced-review scheduling, prerequisite routing and personalised 5, 10 or 15-minute next-session recommendations
- Parent insight showing level and outcome growth, independent versus supported performance, retention, review dates and weekly recommendations
- Parent-only test worksheets with question notes, overall feedback and addressed-release traceability
- Configuration-managed credentials, reliable parent test completion and optional testing notes
- Accessible review dialogs and Enter-key answer-to-next-question flow
- v0.30.1 learner-wide completion recommendations, semantic question-family diversity, corrected fraction number lines and Probability visual relevance safeguards

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`, separate from the application image and the existing `/data/questmath.db`. It also generates a dedicated Home Assistant service token at `/data/ha-service-token`. Both values persist through restart and upgrade with restrictive permissions where supported. Explicit `SECRET_KEY` and `HA_SERVICE_TOKEN` values of at least 32 characters are honoured.

Parent and student usernames and passwords are managed from the Home Assistant add-on Configuration page. Save any credential change and restart MathQuest to apply it to the existing account. Existing account IDs, worksheets, progress and feedback remain unchanged.

## Development workflow

Changes are developed on branches and proposed to `main` using pull requests. Version changes must update every location checked by `python scripts/validate_versions.py` and add matching notes to `questmath/CHANGELOG.md`.
