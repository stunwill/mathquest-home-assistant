# MathQuest 0.45.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, interactive mathematical models, reasoning, worksheet navigation, learner guidance and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway. The focused Level 5/6 diagnostic supplies conservative placement evidence, and v0.44.0 turns that evidence and Best Next Step into deliberately targeted learning sessions.

## v0.45.0 follow-through\n\n- Targeted worksheets retain their learning purpose and pre-session evidence, allowing completion and parent views to explain what changed after real practice.\n- Student completion remains learner-safe, while Parent Dashboard can inspect support use, independent checks and before/after evidence.\n\n## Included

- Student and parent authentication, with `sienna` prefilled for the normal student login flow
- Automatic recovery from expired MathQuest sessions back to the login screen while keeping Home Assistant ingress failures distinct
- Distinct Home, Adventure, Worksheets and Progress student destinations rather than scroll-to-section navigation
- Concise Home focused on current learning, Best Next Step and destination previews
- Ready to Start for untouched worksheets and Continue Learning only after meaningful progress
- Learner-safe Extra Practice and Ready to review language backed by the existing adaptive evidence
- Student Learning Progress derived from existing mastery, adaptive progression, support and spaced-retrieval evidence
- Learner-readable states for Not enough evidence yet, Practising, Building confidence, Getting stronger, Ready for a challenge and Ready to review presentation
- Evidence-grounded Best Next Step explanations without raw mastery percentages, curriculum codes or adaptive mode labels
- Explicit targeted-learning plans that turn the recommended skill or prerequisite into the actual worksheet composition
- Purposeful targeted-session stages for reconnect, supported practice, core practice, transfer and independent checking
- Focused Level 5/6 diagnostic with three questions at each level used as placement evidence rather than a pass/fail or overall grade classification
- Diagnostic evidence mapped into the existing outcome mastery and adaptive recommendation model
- Conservative diagnostic retake handling: prior attempts remain in history but only the latest diagnostic contributes diagnostic evidence to current readiness
- Diagnostic attempts excluded from spaced-retention checks so repeated testing cannot manufacture retention evidence
- Learner-safe Starting Point summary after diagnostic completion and in Progress
- Parent diagnostic insight with Level 5/6 sample evidence, independent/eventual success, support use, prior evidence and recommended next learning focus
- Story Adventure owned by Adventure while preserving the same backend-authoritative adaptive learning and evidence path
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
- Parent Tests isolated from learner mastery and normal daily-learning completion
- Parent Learning Intelligence with plain-language summaries, independent versus supported success, evidence confidence, recommendations, misconception grouping and retention
- Home Assistant parent-learning integration with daily completion, learning focus, review due, support dependence, misconceptions, meaningful progress and weekly summary
- Persistent local Home Assistant service token and stable read-only learning endpoints
- Visual Mathematics and Interactive Maths Lab
- Parent Dashboard reliability safeguards for loading, retry and optional-section failure
- SQLite persistence and Home Assistant backup support

## Targeted learning sessions and skill-level progression

v0.44.0 adds an explicit learning-plan layer between Best Next Step and worksheet composition. The plan is derived from the existing mastery, review and prerequisite evidence. It does not create another score, table or global grade assignment.

The plan identifies the primary curriculum outcome and instructional skill, a learner-safe reason, the session purpose and a sequence of question roles. Recommended sessions are then built around that target instead of opening a broad-topic worksheet and relying on chance. Where a skill-specific generator is available, the majority of the session is deliberately generated from it while duplicate identities are blocked and the existing adaptive/session-quality systems remain active.

Targeted sessions can reconnect prior knowledge, keep support readily available, provide repeated but varied core practice, ask for transfer and end with independent-check opportunities. Help is never disabled to manufacture independence. Instead, completion evidence can recognise the useful transition from needing support earlier to solving a later related question independently.

Progression remains skill-specific. MathQuest does not introduce `current_grade = 5` or `current_grade = 6`. The established challenge-readiness requirements remain unchanged: six relevant recent questions, at least 82% independent success and no more than 25% support dependency.

Diagnostic uncertainty is followed by normal targeted learning rather than a larger diagnostic. This allows MathQuest to replace uncertainty with authentic practice evidence while preserving the six-question diagnostic as a short starting signal.

## Diagnostic interpretation, placement and learning path

v0.43.0 turns the six-question diagnostic into a starting signal for the existing learning model. It does not add another mastery score, a placement table or a global `current_grade` field.

The latest completed diagnostic contributes Level 5/6 evidence through existing outcome mastery. Ordinary historical practice remains part of the model. Earlier diagnostic attempts remain visible in history but are excluded from current mastery/progression evidence so repeated retakes cannot accumulate until they satisfy readiness thresholds. Diagnostic questions are also excluded from retention checks.

The current diagnostic deliberately samples only two areas: Level 5 efficient calculation through multiplication and Level 6 fraction-to-decimal place-value conversion. MathQuest does not claim that this measures an entire curriculum level. When evidence remains uncertain, subsequent ordinary learning gathers more evidence rather than starting another long diagnostic.
