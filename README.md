# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.46.0`

## v0.46.0 - Adaptive Learning Loop & Next-Session Intelligence

MathQuest now interprets what happened during a targeted session and uses that evidence to shape the next learning experience. Existing outcome mastery, support evidence, challenge thresholds, prerequisite routing and spaced review remain authoritative.

- Recent targeted sessions produce explicit internal follow-through decisions such as reteach, check independence, transfer, review later and challenge.
- Supported success is distinguished from later independent success, with learner-safe next-action language.
- Best Next Step and targeted session planning reuse recent evidence without introducing a global grade or second mastery model.
- Parent Learning Intelligence can inspect the evidence and resulting next action.
- Physical iPhone/iPad acceptance remains pending until tested on real devices.

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

- Targeted-session follow-through records the planned learning intent and compares evidence before and after completion without exposing parent analytics to the learner

- Student and parent logins, with `sienna` prefilled for the normal student login flow and automatic recovery from expired MathQuest sessions
- Distinct student Home, Adventure, Worksheets and Progress destinations rather than scroll-to-section navigation
- Concise student Home focused on current learning, Best Next Step and destination previews
- Ready to Start for untouched worksheets and Continue Learning only after meaningful progress
- Learner-safe Extra Practice and Ready to review language backed by the existing adaptive evidence
- Student Learning Progress that translates existing mastery, adaptive progression, support and spaced-retrieval evidence into age-appropriate learner guidance
- Evidence-grounded Best Next Step explanations that tell the learner why MathQuest selected the recommendation without exposing mastery percentages, curriculum codes or adaptive mode labels
- Explicit targeted-learning plans that turn Best Next Step into a purposefully composed session around the recommended skill or prerequisite
- Targeted session stages for reconnecting prior knowledge, supported practice, core practice, transfer and independent checking without introducing a second mastery system
- Focused Level 5/6 diagnostic placement using three Level 5 and three Level 6 questions as a starting signal rather than a pass/fail or overall grade classification
- Diagnostic evidence integrated into the existing outcome-mastery and adaptive learning model, with older retakes retained in history but prevented from inflating current readiness evidence
- Learner-safe diagnostic completion and Progress summaries explaining what MathQuest noticed, where more evidence is needed and what learning step comes next
- Parent diagnostic insight showing sampled Level 5/6 evidence, independent versus eventual success, support use, prior evidence and the recommended next learning focus
- Story Adventure owned by Adventure while retaining adaptive learning selection and theme purpose
- Worksheet history owned by Worksheets and Weekly Activity owned by Progress
- Student-only navigation with iPhone safe-area support
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
- Victorian Curriculum F–10 Version 2.0 Level 5 pathway with skill-sensitive progression informed by ongoing practice and focused Level 5/6 diagnostic evidence
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

## Adaptive Learning Loop and Next-Session Intelligence

MathQuest v0.45.0 connects the targeted plan to its learning result. Each targeted worksheet records the recommendation-derived purpose, target skill, planned stages and a pre-session evidence snapshot. Completion summaries then report only evidence grounded in the learner's actual session, while the parent view can inspect before/after outcome evidence, support use and independent checks. Existing outcome mastery remains authoritative, and repeated practice does not create a second evidence model.

## Targeted Learning Sessions and Skill-Level Progression

MathQuest v0.44.0 turns the existing Best Next Step recommendation into an explicit session-learning plan before worksheet composition. The plan reuses outcome mastery, prerequisites, review scheduling and the existing adaptive progression thresholds; it does not add a second mastery score, global grade or parallel learning history.

A targeted plan identifies the primary outcome and instructional skill, the reason it was selected, whether it is current learning, consolidation, review or prerequisite work, and a learner-safe purpose. Recommended worksheets are then composed around that target while keeping enough variation for useful transfer evidence. Short sessions use a purposeful sequence that can reconnect prior knowledge, make support readily available, provide repeated core practice, vary representation and finish with independent-check opportunities.

Support remains available throughout the worksheet. MathQuest does not punish hint, worked-example or Math Mentor use. Targeted completion evidence can instead recognise the more useful pattern where support was needed earlier and a similar later question was completed independently.

Progression remains skill-specific. The existing challenge-readiness contract is unchanged: at least six relevant recent questions, at least 82% independent success and no more than 25% support dependency. Strong evidence in one mathematical pathway does not promote every skill to Level 6, and diagnostic evidence remains a starting signal rather than a curriculum-wide grade judgement.

Targeted follow-up is the preferred way to replace diagnostic uncertainty with authentic learning evidence. The six-question Level 5/6 diagnostic remains deliberately short; MathQuest should gather the next evidence through normal learning rather than repeatedly retesting the learner.

## Diagnostic Interpretation, Placement and Learning Path

MathQuest v0.43.0 turns the focused Level 5/6 diagnostic into meaningful placement evidence without creating another mastery system.

The diagnostic remains intentionally short: three Level 5 questions and three Level 6 questions. It samples Level 5 efficient calculation through multiplication and Level 6 fraction-to-decimal place-value conversion. Those six questions are not treated as proof that a student has mastered an entire curriculum level, nor as evidence that the student is globally a Grade 5 or Grade 6 learner.

Diagnostic attempts contribute through the same outcome-mastery and adaptive evidence architecture used by normal learning. Level 5/6 diagnostic outcome identifiers are mapped into the existing outcome model, ordinary historical practice remains preserved, and the adaptive engine still owns Best Next Step, prerequisite routing, review scheduling and challenge decisions.

Only the latest diagnostic attempt contributes diagnostic evidence to current mastery and progression. Earlier attempts remain visible in diagnostic history but do not accumulate until they falsely satisfy evidence thresholds. Diagnostic attempts are also excluded from spaced-retention checks. The existing challenge-readiness threshold remains unchanged: at least six relevant recent questions, at least 82% independent success and no more than 25% support dependency.

The diagnostic completion screen answers three learner questions without turning the experience into an exam result: what MathQuest noticed, what still needs evidence and what to do next. It deliberately avoids pass/fail, raw mastery percentages, curriculum codes and global grade classification. The same Starting Point summary appears in Progress after completion.
