# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.41.0`

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

The release metadata validator derives the active backend module from the runtime script and requires the add-on, frontend package/display, backend, README and changelog versions to agree. The committed frontend lockfile is also checked for dependency metadata compatibility with `package.json`.

## Features

- Student and parent logins, with `sienna` prefilled for the normal student login flow and automatic recovery from expired MathQuest sessions
- Student Learning Progress that translates existing mastery, adaptive progression, support and spaced-retrieval evidence into age-appropriate learner guidance
- Evidence-grounded Best Next Step explanations that tell the learner why MathQuest selected the recommendation without exposing mastery percentages
- Action-first student mobile Home with unfinished learning promoted ahead of completed history
- Student-only mobile navigation for Home, Adventure, Worksheets and Progress, with iPhone safe-area support
- Compact Story Adventure selection on narrow screens while retaining adaptive learning selection and theme purpose
- Progressive worksheet history with three recent items by default and explicit access to older work
- Responsive weekly learning navigation that replaces the compressed five-control phone layout with readable week navigation and Today
- Responsive student dashboard
- iPad 10th-generation landscape worksheet optimisation with viewport-fixed post-answer feedback and keyboard-first continuation/retry
- Tablet-optimised worksheet and tutoring flow for portrait and landscape use
- Multiple daily worksheets with save, exact resume, review and skip support
- First-class interactive mathematics including whole-number number lines, fraction bars, fraction number lines, scaled rulers and selectable grid references
- Structured mathematical reasoning including reasonableness, conceptual statements and age-appropriate error analysis
- Session-level learning quality that evaluates the final worksheet for near-duplicate structures, accidental low-complexity work and recent overexposure
- Multidimensional direct-arithmetic difficulty metadata including operation, operand digit counts and regrouping demand
- Number & Algebra direct addition/subtraction practice biased toward larger Grade 5-appropriate values instead of repeated low-complexity sums
- Equal-groups modelling questions require the learner to calculate the total rather than merely name the operation
- Worksheet history times are displayed in `Australia/Melbourne`, including daylight-saving transitions
- Duplicate-safe adaptive question generation and visual learning guardrails
- Evidence-aware suppression of unnecessarily basic arithmetic while preserving purposeful review and consolidation
- Victorian Curriculum F–10 Version 2.0 Level 5 pathway, adapting across Levels 2–6 from diagnostic evidence
- Parent Learning Intelligence with independent versus supported success, evidence confidence, recommendations, misconception grouping, retention and difficulty calibration
- Adaptive Daily Learning with current learning, consolidation, spaced review and limited challenge purposes
- Story Adventure as a presentation layer over the same adaptive learning plan, answer validation and evidence path as Daily Practice
- Method-first Math Mentor with representation-specific support, aligned worked examples, Visual Mathematics and Interactive Maths Lab
- Parent-only tests isolated from learner mastery and adaptive evidence
- Home Assistant ingress and a persistent local service token
- Compact Home Assistant parent-learning summary for daily completion, current focus, review due, persistent support needs, recurring misconceptions, meaningful progress and weekly learning
- Stable Home Assistant learning entity contract using a small number of long-lived identifiers rather than worksheet/question-specific IDs
- Notification-ready learning alerts based on meaningful accumulated evidence rather than individual wrong answers
- Parent Dashboard bootstrap that surfaces required-data failures and lets optional backups and intelligence sections degrade independently
- Local-first operation with no third-party learner analytics or telemetry

## Student Learning Progress and Guidance

MathQuest v0.41.0 adds a learner-facing interpretation layer over the existing Learning Intelligence system. It does not create another mastery score and does not change adaptive thresholds.

Student Progress can present **Not enough evidence yet**, **Practising**, **Building confidence**, **Getting stronger**, **Ready for a challenge** and **Review due**. These states reuse the existing outcome mastery and Adaptive Daily Learning evidence, including repeated question evidence, independent versus supported success and spaced-retrieval scheduling.

**Ready for a challenge** is only shown when the existing adaptive progression state is already `ready_to_progress`. **Review due** comes from the existing spaced-retrieval schedule. **Building confidence** recognises successful work with support without treating it as equivalent to repeated independent success. Limited evidence is explicitly treated as limited evidence rather than failure.

The student's Best Next Step also receives an evidence-grounded explanation. Diagnostic, prerequisite and spaced-review recommendations are explained according to the reason the adaptive engine actually selected them. Student-facing recommendation text no longer needs to expose technical mastery percentages.

Progress deliberately avoids unsupported historical claims. v0.41.0 does not say that a skill "improved by X" because the current learner evidence does not provide a trustworthy before/after comparison for every skill. It also does not expose internal misconception codes. The complete mapping and conservative omissions are documented in `questmath/STUDENT_LEARNING_STATE_0.41.0.md`.

Detailed technical evidence remains available to parents through Parent Learning Intelligence. Student Progress keeps a smaller optional evidence disclosure so the primary experience stays understandable rather than becoming an analytics dashboard.

## Student mobile Home and navigation

MathQuest v0.40.0 changed the student mobile information architecture because the existing Home page had become too long for iPhone portrait. The problem was not missing learning information, it was that current action, unfinished work, Story Adventure, history, technical skill evidence and the weekly calendar were all presented with similar visual weight.

On narrow screens, unfinished worksheets and skipped-question recovery are surfaced as **Continue Learning** before completed history. Story Adventure becomes a compact horizontal selector, completed worksheet history shows only the three most relevant recent items until expanded, and the student receives persistent Home, Adventure, Worksheets and Progress navigation. The Progress destination now leads to the v0.41 learner-guidance section. The navigation is student-only and does not expose Parent Dashboard or Parent Test functionality.

The MathQuest header is reduced when the student navigation is present so the Home Assistant ingress header and MathQuest identity do not consume most of the initial viewport. Safe-area padding prevents the bottom navigation covering content on iPhone.

The weekly learning calendar no longer tries to squeeze previous week, previous day, a date range, next day and next week into five narrow phone columns. Mobile keeps previous week, date range, next week and Today, then presents the week as a readable vertical activity list. Tablet and desktop retain the richer controls and seven-day presentation.

## Session learning quality

MathQuest v0.39.0 added a final learning-quality pass after the existing generators and adaptive composition have done their work. This is deliberately not another learning engine. It checks whether the resulting worksheet is educationally balanced as a session.

The policy groups questions by meaningful mathematical structure rather than exact wording. For direct arithmetic it considers the operation, operand digit counts and regrouping demand. This means near-duplicates such as similarly structured three-digit-plus-two-digit calculations can be diversified, while a substantially different three-digit regrouping problem is not treated as identical merely because it is also addition.

Recent answered Daily Practice and Story Adventure questions contribute a small recent-exposure signal. Structures that have appeared repeatedly are deprioritised when a suitable alternative is available. Parent Tests are excluded, and deliberate review, consolidation and retrieval are preserved rather than removed for the sake of variety.

If final session-quality work changes a question, MathQuest refreshes that question's adaptive purpose and evidence annotation so later learning decisions and parent-facing information refer to the mathematics Sienna actually received. The established one-question challenge limit remains in force.

## Number & Algebra question quality

MathQuest v0.38.1 reduced low-value direct arithmetic in Number & Algebra. Straight addition and subtraction questions remain useful for fluency, but examples such as `121 + 22`, `50 + 58`, `14 − 4` and `8 + 8` are no longer allowed to dominate normal learner worksheets. When direct addition or subtraction is selected, smaller examples are upgraded to larger place-value calculations suitable for Grade 5 practice.

Equal-groups modelling also asks for the mathematical result. Instead of asking which operation would find the total, MathQuest asks how many items there are altogether, so Sienna chooses multiplication as part of actually solving the problem.

Worksheet-history clock times are converted from stored UTC timestamps to `Australia/Melbourne` before display, using the correct AEST/AEDT offset for the date.

## iPad landscape worksheet feedback

MathQuest v0.38.0 changed the normal student flow to `Answer → Immediate feedback → Understand → Reflect → Continue` without requiring page scrolling between those steps. Typed answers still submit with Enter. The feedback dialog then receives focus so a second Enter continues after a terminal answer or returns to a clean, focused answer field when another attempt is expected.

The dialog keeps the result and primary action visible while allowing only genuinely long supporting content to scroll internally. Correct answers use restrained, non-blocking celebration and incorrect answers use supportive learning language. Retryable incorrect answers continue to hide terminal working, and Math Mentor remains optional unless the backend explicitly requires support.

The same shared feedback architecture is used by ordinary typed answers, choices, first-class interactive mathematics and Story Adventure questions. Learner confidence reflection remains optional and continues to record the existing learning evidence. Parent Tests remain isolated.

## Interactive mathematics and reasoning

MathQuest keeps interactive questions inside the same backend-authoritative worksheet architecture as conventional questions. The learner's selected mathematical value or grid reference is submitted through the normal answer endpoint, so correctness, attempts, support use and learning evidence remain consistent.

The current interactive models include:

- whole-number number-line positions;
- fraction-bar part selection;
- fraction locations between 0 and 1;
- scaled ruler marks;
- grid-reference squares.

Where revealing a label would give away the answer, internal targets are intentionally left unlabelled. Reasoning questions add controlled variety such as judging a reasonable estimate, distinguishing perimeter from area, recognising symmetry statements and analysing a plausible mathematical mistake.

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

## Security and upgrades

MathQuest generates a secure JWT signing secret on first start and stores it at `/data/jwt-signing-secret`. It also generates a dedicated Home Assistant service token at `/data/ha-service-token`. Both values persist through restart and upgrade with restrictive permissions where supported.

MathQuest login tokens currently retain the existing 24-hour lifetime. When a MathQuest token expires, the learner is returned to the normal login form instead of being left on an `Invalid session` error. Home Assistant ingress authentication failures remain separate and do not automatically clear an otherwise valid MathQuest token.

Parent and student usernames and passwords are managed from the Home Assistant add-on Configuration page. New installs default the student username to `sienna`. Save credential changes and restart the MathQuest add-on to apply them to the existing accounts. Learner evidence and worksheet history are preserved.
