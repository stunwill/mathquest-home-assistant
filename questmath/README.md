# MathQuest 0.43.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, interactive mathematical models, reasoning, worksheet navigation, learner guidance and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway. A focused Level 5/6 diagnostic now supplies conservative placement evidence to the same adaptive learning system rather than assigning the learner an overall grade.

## Included

- Student and parent authentication, with `sienna` prefilled for the normal student login flow
- Automatic recovery from expired MathQuest sessions back to the login screen while keeping Home Assistant ingress failures distinct
- Distinct Home, Adventure, Worksheets and Progress student destinations rather than scroll-to-section navigation
- Concise Home focused on current learning, Best Next Step and destination previews
- Ready to Start for untouched worksheets and Continue Learning only after meaningful progress
- Learner-safe Extra Practice and Ready to review language backed by the existing adaptive evidence
- Student Learning Progress derived from existing mastery, adaptive progression, support and spaced-retrieval evidence
- Learner-readable states for Not enough evidence yet, Practising, Building confidence, Getting stronger, Ready for a challenge and Ready to review presentation
- Evidence-grounded Best Next Step explanations without raw mastery percentages, curriculum codes or adaptive mode labels
- Focused Level 5/6 diagnostic with three questions at each level used as placement evidence rather than a pass/fail or overall grade classification
- Diagnostic evidence mapped into the existing outcome mastery and adaptive recommendation model
- Conservative diagnostic retake handling: prior attempts remain in history but only the latest diagnostic contributes diagnostic evidence to current readiness
- Diagnostic attempts excluded from spaced-retention checks so repeated testing cannot manufacture retention evidence
- Diagnostic-only skill identifiers kept out of instructional targets so subsequent practice uses established generators and prerequisite routing
- Learner-safe Starting Point summary after diagnostic completion and in Progress
- Parent diagnostic insight with Level 5/6 sample evidence, independent/eventual success, support use, prior evidence and recommended next learning focus
- Story Adventure owned by Adventure while preserving adaptive learning selection
- Worksheet history owned by Worksheets and Weekly Activity owned by Progress
- Student navigation with iPhone safe-area support
- Responsive mobile weekly learning navigation with readable previous/next week controls and Today
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- iPad 10th-generation landscape worksheet optimisation with immediate post-answer feedback and a keyboard-first two-Enter flow
- First-class interactive whole-number number lines, fraction bars, fraction number lines, scaled rulers and grid-reference selection
- Grade 5 reasoning including reasonableness, conceptual comparison and find-the-mistake questions
- Session-level learning quality covering near-duplicate structures, recent exposure and accidental low-complexity work
- Multidimensional arithmetic difficulty metadata including digit size and regrouping demand
- Direct Number & Algebra addition/subtraction biased toward larger Grade 5-appropriate values rather than repeated low-complexity sums
- Equal-groups questions ask for the numerical total instead of only asking the learner to name the operation
- Worksheet history uses Melbourne local time with AEST/AEDT daylight-saving handling
- Duplicate-safe question generation with visual question guardrails
- Evidence-aware reduction of unnecessarily basic arithmetic while preserving purposeful review, consolidation and retrieval
- Immediate retry-first feedback with optional Math Mentor support
- Representation-specific Math Mentor guidance and different-number worked examples for interactive models
- Tablet-optimised worksheet and tutoring layouts
- Adaptive strand weighting and progressive difficulty
- Adaptive Daily Learning using current learning, consolidation, spaced review and challenge purposes
- Controlled skill progression requiring independent evidence before challenge increases
- Story Adventure over the same backend-authoritative adaptive learning, answer and evidence path as Daily Practice
- Parent Tests isolated from learner mastery and normal daily-learning completion
- Parent Learning Intelligence with plain-language summaries, independent versus supported success, evidence confidence, recommendations, misconception grouping and retention
- Home Assistant parent-learning integration with daily completion, learning focus, review due, support dependence, misconceptions, meaningful progress and weekly summary
- Persistent local Home Assistant service token and stable read-only learning endpoints
- Visual Mathematics and Interactive Maths Lab
- Parent Dashboard reliability safeguards for loading, retry and optional-section failure
- SQLite persistence and Home Assistant backup support

## Diagnostic interpretation, placement and learning path

v0.43.0 turns the six-question diagnostic into a starting signal for the existing learning model. It does not add another mastery score, a placement table or a global `current_grade` field.

The latest completed diagnostic contributes Level 5/6 evidence through existing outcome mastery. Ordinary historical practice remains part of the model. Earlier diagnostic attempts remain visible in history but are excluded from current mastery/progression evidence so repeated retakes cannot accumulate until they satisfy readiness thresholds. Diagnostic questions are also excluded from retention checks.

The existing progression contract is unchanged: challenge readiness still requires at least six relevant recent questions, at least 82% independent success and no more than 25% support dependency. Three correct diagnostic responses therefore cannot independently make a skill Ready for a challenge.

The current diagnostic deliberately samples only two areas: Level 5 efficient calculation through multiplication and Level 6 fraction-to-decimal place-value conversion. MathQuest does not claim that this measures an entire curriculum level. When evidence remains uncertain, subsequent ordinary learning gathers more evidence rather than starting another long diagnostic.

After completion, the student sees **Your Starting Point** instead of the generic worksheet result. The screen explains what MathQuest noticed, what needs more evidence and the next recommended learning action without raw mastery percentages, curriculum codes, pass/fail or an overall grade label. Progress retains this starting-point interpretation alongside the existing learner states.

Parents receive a more detailed diagnostic evidence panel. It distinguishes the latest diagnostic sample from prior evidence and includes independent versus eventual success, recorded support, curriculum outcomes and the adaptive engine's recommended next focus.

Best Next Step remains owned by the existing adaptive engine. Diagnostic-only skills are not allowed to become the instructional target, so established practice generators, prerequisites, review scheduling and normal adaptive difficulty remain authoritative. Story Adventure continues to present the same adaptive learning path rather than creating a separate Level 5 or Level 6 adventure engine.

## Student UX, navigation and learning guidance refinement

v0.42.0 completes the information-architecture direction started in v0.40.0. Home, Adventure, Worksheets and Progress now behave as distinct destinations rather than four controls pointing into one long student dashboard.

**Home** is the concise learning launchpad. **Adventure** owns the complete Story Adventure selector. **Worksheets** owns worksheet history, resume and review actions. **Progress** owns learner-state guidance and Weekly Activity.

Untouched worksheets are shown as **Ready to Start** and do not claim saved progress. Once meaningful answers exist, the same work becomes **Continue Learning**. Historical learning evidence is preserved; v0.42.0 deliberately does not invent automatic abandonment or archival states where current data cannot prove them safely.

Student-facing learning language translates internal analytics. **Extra Practice** replaces intervention wording and **Ready to review** replaces Review due. Raw independent/support percentages, curriculum outcome codes and adaptive mode labels are removed from the primary student presentation. Parent Learning Intelligence remains the detailed evidence surface.

The underlying learning-state derivation, adaptive progression thresholds, prerequisite routing, spaced-review scheduling and recommendation logic remain authoritative. Progress groups skills under concise learner-state explanations instead of repeating the same explanation on every row, and zero-value state summaries are hidden.

## Student Learning Progress and Guidance

v0.41.0 translates MathQuest's existing Learning Intelligence into student language without creating a second mastery model or changing progression thresholds.

Student Progress can show **Not enough evidence yet**, **Practising**, **Building confidence**, **Getting stronger**, **Ready for a challenge** and the internal review-due state. These labels come from the existing outcome mastery, Adaptive Daily Learning progression, independent versus supported success and spaced-retrieval evidence. v0.42.0 presents review-due evidence to the student as **Ready to review**.

**Ready for a challenge** only follows the existing adaptive `ready_to_progress` decision. Review scheduling follows the existing spaced-review schedule. Supported success can be recognised as **Building confidence** without being treated as equivalent to repeated independent success. Limited evidence is explicitly not treated as failure.

Best Next Step continues to use the existing adaptive recommendation. For student requests, the technical recommendation reason is translated in the backend into a concise explanation of the actual reason, such as a diagnostic starting point, prerequisite support or purposeful review.

MathQuest deliberately does not claim a measured before/after improvement trend where the existing evidence cannot prove one. It also does not expose internal misconception codes or tell the learner they "have a misconception". Those signals continue to influence tutoring and adaptive learning. The complete v0.41 mapping is documented in `STUDENT_LEARNING_STATE_0.41.0.md`.

## Student mobile Home and navigation

v0.40.0 introduced the responsive student mobile foundation after real iPhone use showed that the Home page had become too long and dashboard-like. v0.42.0 completes that direction by making the navigation destinations own distinct views.

Story Adventure retains its adaptive learning path, the student navigation uses accessible current-page state and iPhone safe-area padding, and the mobile MathQuest header remains compressed beneath Home Assistant ingress while keeping sign-out accessible.

The weekly learning calendar keeps readable previous week, date range, next week and Today controls on mobile, with the week presented as a one-column activity list. Tablet and desktop retain richer day navigation and the seven-day layout.
