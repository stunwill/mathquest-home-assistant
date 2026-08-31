# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.36.0`

## Development Metadata

Repository and release tooling, including DevHub, should use these canonical sources:

- **Authoritative roadmap:** `ROADMAP.md`
- **Project/GitHub changelog:** `CHANGELOG.md`
- **Home Assistant add-on changelog:** `questmath/CHANGELOG.md`
- **Home Assistant manifest version:** `questmath/config.yaml`
- **Frontend package version:** `questmath/app/frontend/package.json`
- **Frontend display version:** `questmath/app/frontend/src/version.ts`
- **Backend/runtime version:** the active backend version module used by `questmath/rootfs/etc/services.d/questmath/run`
- **Runtime health version:** `/api/health`, sourced from the active backend application version
- **GitHub release/tag format:** `vX.Y.Z`

The release metadata validator derives the expected version from the repository version sources and checks that the root roadmap, project changelog and Home Assistant changelog contain matching release metadata.

## Features

- Student and parent logins, with `sienna` prefilled for the normal student login flow and automatic recovery from expired MathQuest sessions
- Responsive student dashboard
- Tablet-optimised worksheet and tutoring flow for portrait and landscape use
- Multiple daily worksheets with save, exact resume, review and skip support
- Interactive number-line location questions answered directly on the line rather than through answer-choice buttons
- Duplicate-safe adaptive question generation and visual learning guardrails
- Evidence-aware suppression of unnecessarily basic arithmetic while preserving purposeful review and consolidation
- Victorian Curriculum F–10 Version 2.0 Level 5 pathway, adapting across Levels 2–6 from diagnostic evidence
- Parent Learning Intelligence with independent versus supported success, evidence confidence, recommendations, misconception grouping, retention and difficulty calibration
- Adaptive Daily Learning with current learning, consolidation, spaced review and limited challenge purposes
- Story Adventure as a presentation layer over the same adaptive learning plan as Daily Practice
- Method-first Math Mentor, aligned worked examples, Visual Mathematics and Interactive Maths Lab
- Parent-only tests isolated from learner mastery and adaptive evidence
- Home Assistant ingress and a persistent local service token
- Compact Home Assistant parent-learning summary for daily completion, current focus, review due, persistent support needs, recurring misconceptions, meaningful progress and weekly learning
- Stable Home Assistant learning entity contract using a small number of long-lived identifiers rather than worksheet/question-specific IDs
- Notification-ready learning alerts based on meaningful accumulated evidence rather than individual wrong answers
- Parent Dashboard bootstrap that surfaces required-data failures and lets optional backups and intelligence sections degrade independently
- Local-first operation with no third-party learner analytics or telemetry

## Home Assistant Parent Learning Integration

MathQuest remains authoritative for all educational decisions. Home Assistant consumes the same Parent Learning Intelligence, adaptive-learning purpose, retention, support-dependency and misconception evidence used by MathQuest itself.

Use the existing Home Assistant service token from the parent dashboard with these read-only endpoints:

- `/api/ha/learning` for the complete compact parent-learning state
- `/api/ha/weekly-summary` for the current seven-day learning summary
- `/api/ha/stats` and `/api/ha/summary` remain available for compatibility

The learning response uses stable conceptual entities:

- `mathquest_daily_learning`
- `mathquest_learning_focus`
- `mathquest_review_status`
- `mathquest_support_status`
- `mathquest_weekly_summary`

These are stable unique-ID contracts for Home Assistant dashboards and automations. They do not contain transient worksheet, question, date, skill or adventure IDs.

### Daily learning state

Daily Practice and Story Adventure can satisfy daily learning only when a legitimate learner worksheet is completed with answered question evidence. Simply opening MathQuest, starting a worksheet, abandoning a worksheet without meaningful work, or completing a Parent Test does not satisfy daily learning.

Where MathQuest has actual elapsed session time, `active_minutes` is exposed. Where a completed timed session has a configured 5, 10 or 15-minute target, `planned_minutes_completed` is exposed separately so planned duration is not misrepresented as exact engagement time.

### Example REST sensor

A standard Home Assistant REST sensor can read the daily state without HACS:

```yaml
rest:
  - resource: http://YOUR_MATHQUEST_HOST:8080/api/ha/learning
    headers:
      Authorization: "Bearer YOUR_MATHQUEST_SERVICE_TOKEN"
    scan_interval: 60
    sensor:
      - name: MathQuest Daily Learning
        unique_id: mathquest_daily_learning
        value_template: "{{ value_json.daily_learning.state }}"
        json_attributes_path: "$.daily_learning"
        json_attributes:
          - completed
          - questions_attempted
          - independent_accuracy
          - eventual_accuracy
          - active_minutes
          - planned_minutes_completed
          - latest_session_type
          - latest_focus
```

The same endpoint can provide current focus, review, support and weekly-summary attributes to additional REST sensors if desired. A single REST fetch can therefore populate a small number of useful entities without exposing every internal metric.

### Example reminder automation

MathQuest deliberately does not hard-code a reminder time. Home Assistant can decide when a reminder is appropriate:

```yaml
automation:
  - alias: MathQuest learning reminder
    triggers:
      - trigger: time
        at: "18:00:00"
    conditions:
      - condition: template
        value_template: "{{ states('sensor.mathquest_daily_learning') != 'Completed' }}"
    actions:
      - action: notify.mobile_app_parent_phone
        data:
          message: "MathQuest learning has not been completed today."
```

Review, support and misconception states are intentionally conservative. One difficult question does not create a persistent-support alert, and isolated incorrect answers do not create misconception alerts.

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`. It also generates a dedicated Home Assistant service token at `/data/ha-service-token`. Both values persist through restart and upgrade with restrictive permissions where supported.

MathQuest login tokens currently retain the existing 24-hour lifetime. When a MathQuest token expires, the learner is returned to the normal login form instead of being left on an `Invalid session` error. Home Assistant ingress authentication failures remain separate and do not automatically clear an otherwise valid MathQuest token.

Parent and student usernames and passwords are managed from the Home Assistant add-on Configuration page. New installs default the student username to `sienna`. Save credential changes and restart the MathQuest add-on to apply them to the existing accounts. Learner evidence and worksheet history are preserved.
