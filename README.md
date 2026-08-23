# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.30.0`

## Features

- Student and parent logins
- Responsive student dashboard
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
- Question-specific strategy cards for addition, subtraction, multiplication, division and unknown equations
- Three-stage guided hints with Why?, Teach me this, Show another way and Start over support
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

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`, separate from the application image and the existing `/data/questmath.db`. It also generates a dedicated Home Assistant service token at `/data/ha-service-token`. Both values persist through restart and upgrade with restrictive permissions where supported. Explicit `SECRET_KEY` and `HA_SERVICE_TOKEN` values of at least 32 characters are honoured.

Parent and student usernames and passwords are managed from the Home Assistant add-on Configuration page. Save any credential change and restart the MathQuest add-on to apply it to the existing account. The account ID, worksheets, progress and feedback remain unchanged.

Upgrading to `0.16.2` rotates installations that previously used the legacy secret. Existing JWTs may stop working and users may need to sign in again. No worksheet, progress, account or database data is reset or removed.

## Home Assistant Dashboard Integration

MathQuest exposes current learner statistics without duplicating the adaptive/mastery calculation logic.

### API endpoints

- `GET /api/ha/summary` is the lightweight polling endpoint recommended for dashboard headline values.
- `GET /api/ha/stats` includes headline values, weekly values and category statistics.
- Both endpoints accept a normal MathQuest login token or the dedicated Home Assistant service token.
- The service token does not have the normal 24-hour login expiry and only authorises these Home Assistant statistics endpoints.
- A parent can reveal and copy it from **Parent View → Home Assistant Connection**.
- Recommended polling interval: **30–60 seconds**.
- `app_path` is returned as `/`, which is relative to MathQuest itself. Home Assistant should use the add-on's configured ingress/sidebar route rather than inventing a hard-coded ingress URL.

Example summary response:

```json
{
  "available": true,
  "questions_today": 18,
  "accuracy_today": 88.9,
  "hints_used_today": 3,
  "activities_completed_today": 2,
  "streak_days": 7,
  "xp_today": 120,
  "xp_total": 2450,
  "recommended_topic": "Fractions",
  "last_activity": "2026-08-09T14:30:00",
  "app_path": "/",
  "learning": {
    "baseline_level": 4,
    "current_level": 4.4,
    "weekly_independent_accuracy": 82,
    "weekly_supported_accuracy": 91,
    "review_due_count": 2,
    "recommended_session_minutes": 10
  }
}
```

## Development

See `CONTRIBUTING.md` and `docs/GITHUB-ACTIONS-SETUP.md` for local validation and repository automation guidance.
