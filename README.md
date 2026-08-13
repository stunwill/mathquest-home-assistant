# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.19.0`

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

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`, separate from the application image and the existing `/data/questmath.db`. An explicitly configured `SECRET_KEY` of at least 32 characters is honoured. The public legacy value `development-only-change-me` is never used.

Upgrading to `0.16.2` rotates installations that previously used the legacy secret. Existing JWTs may stop working and users may need to sign in again. No worksheet, progress, account or database data is reset or removed.

## Home Assistant Dashboard Integration

MathQuest exposes current learner statistics without duplicating the adaptive/mastery calculation logic.

### API endpoints

- `GET /api/ha/summary` is the lightweight polling endpoint recommended for dashboard headline values.
- `GET /api/ha/stats` includes headline values, weekly values and category statistics.
- Both endpoints require the same Bearer token used by the MathQuest web application.
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
  "app_path": "/"
}
```

The full endpoint additionally returns `correct_today`, `incorrect_today`, weekly totals and `categories` for Number, Measurement, Space, Algebra and Probability. Category values contain `progress`, `accuracy`, `questions` and hint-aware `mastery`. Values are `null` where MathQuest genuinely has no data yet.

### Recommended Home Assistant REST sensors

MathQuest is an ingress add-on rather than a Home Assistant integration, so v0.11 deliberately does not register entities directly. Use REST sensors against a network-reachable MathQuest URL. Store the MathQuest Bearer token in `secrets.yaml` as `mathquest_token`.

```yaml
rest:
  - resource: "http://HOME_ASSISTANT_HOST:8080/api/ha/stats"
    scan_interval: 30
    headers:
      Authorization: !secret mathquest_token
    sensor:
      - name: MathQuest Summary
        unique_id: mathquest_summary
        value_template: "{{ 'online' if value_json.available else 'unavailable' }}"
        attributes:
          - questions_today
          - correct_today
          - incorrect_today
          - accuracy_today
          - hints_used_today
          - activities_completed_today
          - streak_days
          - xp_today
          - xp_total
          - recommended_topic
          - last_activity
          - categories
      - name: MathQuest Questions Today
        unique_id: mathquest_questions_today
        value_template: "{{ value_json.questions_today }}"
      - name: MathQuest Accuracy Today
        unique_id: mathquest_accuracy_today
        unit_of_measurement: "%"
        value_template: "{{ value_json.accuracy_today }}"
      - name: MathQuest Hints Today
        unique_id: mathquest_hints_today
        value_template: "{{ value_json.hints_used_today }}"
      - name: MathQuest Activities Completed Today
        unique_id: mathquest_activities_completed_today
        value_template: "{{ value_json.activities_completed_today }}"
      - name: MathQuest Streak
        unique_id: mathquest_streak
        unit_of_measurement: "days"
        value_template: "{{ value_json.streak_days }}"
      - name: MathQuest XP Today
        unique_id: mathquest_xp_today
        unit_of_measurement: "XP"
        value_template: "{{ value_json.xp_today }}"
      - name: MathQuest XP Total
        unique_id: mathquest_xp_total
        unit_of_measurement: "XP"
        value_template: "{{ value_json.xp_total }}"
      - name: MathQuest Recommended Topic
        unique_id: mathquest_recommended_topic
        value_template: "{{ value_json.recommended_topic or 'None' }}"
      - name: MathQuest Last Activity
        unique_id: mathquest_last_activity
        device_class: timestamp
        value_template: "{{ value_json.last_activity }}"
```

Category sensors can use the same REST response. For example:

```yaml
      - name: MathQuest Number Progress
        unique_id: mathquest_number_progress
        unit_of_measurement: "%"
        value_template: "{{ value_json.categories.number.progress }}"
      - name: MathQuest Number Accuracy
        unique_id: mathquest_number_accuracy
        unit_of_measurement: "%"
        value_template: "{{ value_json.categories.number.accuracy }}"
```

Repeat that pair for `measurement`, `space`, `algebra` and `probability` if separate dashboard entities are desired. If the add-on port is not exposed, use a suitable internal/reverse-proxy route instead. Do not copy an ingress token URL into configuration because Home Assistant ingress URLs are session-specific.

### Example dashboard card

```yaml
type: entities
title: MathQuest
entities:
  - entity: sensor.mathquest_questions_today
    name: Questions Today
  - entity: sensor.mathquest_accuracy_today
    name: Accuracy
  - entity: sensor.mathquest_hints_today
    name: Hints Used
  - entity: sensor.mathquest_activities_completed_today
    name: Activities Completed
  - entity: sensor.mathquest_streak
    name: Current Streak
  - entity: sensor.mathquest_xp_total
    name: XP
  - entity: sensor.mathquest_recommended_topic
    name: Recommended Topic
```

If MathQuest cannot be reached, Home Assistant's REST integration marks the REST-backed sensors unavailable. A missing optional statistic inside a valid response is returned as `null` and does not fail the other statistics.

## Repository layout

```text
.
├── repository.yaml
├── README.md
├── LICENSE
├── .gitignore
├── .github/workflows/validate.yml
└── questmath/
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── CHANGELOG.md
    ├── README.md
    ├── app/
    └── rootfs/
```

## Install in Home Assistant

1. Open **Settings → Apps → App store**.
2. Open the three-dot menu and select **Repositories**.
3. Add the repository URL shown on this GitHub project.
4. Refresh the app store.
5. Install MathQuest.

## Development workflow

Changes are developed on branches and proposed to `main` using pull requests. Version changes must update every location checked by `python scripts/validate_versions.py` and add matching notes to `questmath/CHANGELOG.md`.
