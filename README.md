# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.32.2`

## Features

- Student and parent logins
- Responsive student dashboard
- Tablet-optimised worksheet and tutoring flow for portrait and landscape use
- Multiple daily worksheets with save, exact resume, review and skip support
- Duplicate-safe adaptive question generation and visual learning guardrails
- Victorian Curriculum F–10 Version 2.0 Level 5 pathway, adapting across Levels 2–6 from diagnostic evidence
- Curriculum outcome tracking and parent review tools
- Parent Learning Intelligence with plain-language summaries, independent versus supported mastery, evidence confidence, prioritised practice recommendations, misconception grouping, retention status and difficulty calibration
- Visual questions, visual hints, story adventures and teaching tools
- Weekly learning activity and complete worksheet history
- XP, levels, streaks and badges
- SQLite persistence and Home Assistant backup support
- Home Assistant ingress and sidebar integration
- Dashboard-friendly Home Assistant statistics API
- Installation-specific JWT signing and failed-login throttling
- Recommended Number & Algebra Focus quests with fact-recall, efficient-strategy and retention support
- Expanded Grade 5 Algebra variety including number patterns, unknowns, substitution, mystery numbers, contextual unknown starts and reverse multiplication
- New Algebra structures mixed into the existing question pool rather than replacing established equations and fact-family practice
- Structural Algebra-family diversity so different numbers alone do not make repetitive questions count as varied
- Adaptive arithmetic that favours purposeful hundreds, regrouping and decomposition when learner evidence supports it
- Evidence-driven retrieval limits so very simple arithmetic remains purposeful without dominating normal worksheets
- Question-specific strategy cards for addition, subtraction, multiplication, division and unknown equations
- Three-stage guided hints with distinct nudge, strategy and worked-next-step roles
- Question-specific Teach me mini-lessons that use the current problem structure without revealing the assessed answer
- Worked examples aligned to the current question family, operation or representation while using different values
- Interactive Maths Lab with linked fractions, percentages, number lines, place value, arrays, clocks, grids and measurement models
- Shared Visual Mathematics components for equal-whole fraction comparison, number lines, arrays, place value and measurement
- Interactive fraction bars with number-line and equivalent-fraction representations that remain mathematically synchronised
- Optional question-specific visual recommendations and multiple solution strategies without changing the learner's answer
- Math Mentor visual-model recommendations connected to the calculation and informed by repeated learning-evidence signals
- Story Adventures 2.0 with adaptive learning goals, connected mission chapters, shared themed data and final outcomes
- Outcome-level mastery, spaced-review scheduling, prerequisite routing and personalised 5, 10 or 15-minute next-session recommendations
- Parent insight showing level and outcome growth, independent versus supported performance, retention, review dates and weekly recommendations
- Long-lived Home Assistant service authentication plus complete category and outcome learning metrics
- Parent-only test worksheets with question notes, overall feedback and addressed-release traceability
- Targeted Number and Algebra interventions with React-owned visuals, reliable resume state and reconciled reporting
- Configuration-managed credentials, reliable parent test completion and optional testing notes
- Visual symmetry hints, recent-question duplicate protection and original visuals in worksheet reviews
- Accessible review dialogs and Enter-key answer-to-next-question flow
- Math Mentor panels on every worksheet question with ask-before-tell tutoring, progressive hints, Why?, Teach me, worked examples, Start over and browser read aloud
- Optional retry-first tutoring, operation-aligned worked examples, prerequisite skill links, misconception evidence and parent-only learning recommendations
- v0.29.1 corrective safeguards for grid visuals, keyboard autofocus, semantic duplicate prevention and explicit grouped-unit wording
- v0.30.1 corrective safeguards for learner-history completion recommendations, question-family diversity, denominator-accurate fraction number lines and relevant Probability visual guidance
- v0.32.1 corrective safeguards for post-transformation family diversity, purposeful retrieval-question budgets and broader worked-example alignment

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`, separate from the application image and the existing `/data/questmath.db`. It also generates a dedicated Home Assistant service token at `/data/ha-service-token`. Both values persist through restart and upgrade with restrictive permissions where supported. Explicit `SECRET_KEY` and `HA_SERVICE_TOKEN` values of at least 32 characters are honoured.

Parent and student usernames and passwords are managed from the Home Assistant add-on Configuration page. Save any credential change and restart the MathQuest add-on to apply it to the existing account. The account ID, worksheets, progress and feedback remain unchanged.

Upgrading to `0.16.2` rotates installations that previously used the legacy secret. Existing JWTs may stop working and users may need to sign in again. No worksheet, progress, account or database data is reset or removed.

## Home Assistant Dashboard Integration

Use the dedicated service-token endpoints from the parent dashboard for long-lived read-only dashboard statistics API.
