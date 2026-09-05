# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.42.0`

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
- Real student destinations for Home, Adventure, Worksheets and Progress rather than scroll-to-section navigation
- Learner-safe Progress and Best Next Step language backed by the existing adaptive and mastery evidence
- Ready to Start for untouched worksheets and Continue Learning only after meaningful worksheet progress
- Extra Practice presentation that keeps intervention/support analytics internal while retaining the existing learning session service
- Story Adventure owned by the Adventure destination while preserving the same adaptive learning and evidence path
- Worksheet history owned by Worksheets and Weekly Activity owned by Progress
- iPhone safe-area navigation and compact Home Assistant ingress header treatment
- iPad 10th-generation landscape worksheet optimisation with viewport-fixed post-answer feedback and keyboard-first continuation/retry
- Multiple daily worksheets with save, exact resume, review and skip support
- First-class interactive mathematics including whole-number number lines, fraction bars, fraction number lines, scaled rulers and selectable grid references
- Structured mathematical reasoning including reasonableness, conceptual statements and age-appropriate error analysis
- Session-level learning quality that evaluates the final worksheet for near-duplicate structures, accidental low-complexity work and recent overexposure
- Victorian Curriculum F–10 Version 2.0 Level 5 pathway, adapting across Levels 2–6 from diagnostic evidence
- Parent Learning Intelligence with independent versus supported success, evidence confidence, recommendations, misconception grouping, retention and difficulty calibration
- Adaptive Daily Learning with current learning, consolidation, spaced review and limited challenge purposes
- Method-first Math Mentor with representation-specific support, aligned worked examples, Visual Mathematics and Interactive Maths Lab
- Parent-only tests isolated from learner mastery and adaptive evidence
- Home Assistant ingress and stable parent-learning APIs
- Local-first operation with no third-party learner analytics or telemetry

## Student destinations and learner-safe guidance

MathQuest v0.42.0 turns the student navigation into real information architecture. **Home** is a concise launchpad for current learning and the Best Next Step. **Adventure** owns Story Adventure. **Worksheets** owns worksheet history and resume/review actions. **Progress** owns learner states and Weekly Activity.

Untouched worksheets are shown as **Ready to Start** rather than falsely implying saved progress. Once answers exist, the same work becomes **Continue Learning**. Historical learning evidence is preserved; v0.42.0 does not automatically delete or archive old learner evidence.

Student-facing language now translates rather than exposes internal analytics. The learner sees **Extra Practice** instead of intervention, **Ready to review** instead of review due, and no raw independent/support percentages or curriculum outcome codes in the primary student experience. Parent Learning Intelligence remains the detailed technical evidence surface.

Progress groups skills under learner-state explanations rather than repeating the same explanation on every row. Zero-value state summaries are hidden. The underlying v0.41 learning-state derivation, adaptive thresholds, prerequisite routing, review scheduling and recommendation logic remain authoritative and unchanged.

## Student Learning Progress and Guidance

MathQuest v0.41.0 added a learner-facing interpretation layer over the existing Learning Intelligence system. It does not create another mastery score and does not change adaptive thresholds.

Student Progress can derive **Not enough evidence yet**, **Practising**, **Building confidence**, **Getting stronger**, **Ready for a challenge** and the internal review-due state from existing outcome mastery and Adaptive Daily Learning evidence. v0.42.0 presents the latter to students as **Ready to review**.

**Ready for a challenge** is only derived when the existing adaptive progression state is already `ready_to_progress`. Review scheduling comes from the existing spaced-retrieval evidence. Building confidence recognises successful work with support without treating it as equivalent to repeated independent success. Limited evidence is explicitly treated as limited evidence rather than failure.

The student's Best Next Step receives an evidence-grounded explanation. Diagnostic, prerequisite and spaced-review recommendations are explained according to the reason the adaptive engine actually selected them. Progress deliberately avoids unsupported historical improvement claims and internal misconception codes.

## Student mobile Home and navigation

MathQuest v0.40.0 introduced the mobile navigation and responsive foundation. v0.42.0 completes that direction by making the destinations own distinct views instead of acting as anchors in one large Home page.

The MathQuest header remains compact under Home Assistant ingress on mobile, and safe-area padding prevents bottom navigation from covering content. Weekly Activity retains readable mobile week controls and a vertical activity layout.

## Session learning quality

MathQuest v0.39.0 added a final learning-quality pass after the existing generators and adaptive composition have done their work. This is deliberately not another learning engine. It checks whether the resulting worksheet is educationally balanced as a session.

The policy groups questions by meaningful mathematical structure rather than exact wording. Recent answered Daily Practice and Story Adventure questions contribute a small recent-exposure signal. Parent Tests are excluded, and deliberate review, consolidation and retrieval are preserved rather than removed for the sake of variety.

## Number & Algebra question quality

MathQuest v0.38.1 reduced low-value direct arithmetic in Number & Algebra while preserving useful calculation fluency. Equal-groups modelling asks for the mathematical result so the learner chooses multiplication as part of solving the problem. Worksheet-history clock times use `Australia/Melbourne`.

## iPad landscape worksheet feedback

MathQuest v0.38.0 established the `Answer → Immediate feedback → Understand → Reflect → Continue` interaction without requiring page scrolling. Typed answers submit with Enter and keyboard-first continuation/retry remains part of the worksheet contract.

The same shared feedback architecture is used by ordinary typed answers, choices, first-class interactive mathematics and Story Adventure questions. Learner confidence reflection remains optional and Parent Tests remain isolated.

## Interactive mathematics and reasoning

Interactive questions stay inside the same backend-authoritative worksheet architecture as conventional questions. Current models include whole-number number-line positions, fraction-bar part selection, fraction locations, scaled ruler marks and grid-reference squares.

## Home Assistant Parent Learning Integration

MathQuest remains authoritative for educational decisions. Home Assistant consumes the same Parent Learning Intelligence, adaptive-learning purpose, retention, support-dependency and misconception evidence used by MathQuest itself through the existing stable learning APIs.

## Security and upgrades

MathQuest generates persistent local JWT and Home Assistant service tokens. Parent and student credentials are managed from the Home Assistant add-on Configuration page. Learner evidence and worksheet history are preserved through normal upgrades.
