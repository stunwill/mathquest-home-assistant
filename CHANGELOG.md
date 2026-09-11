## v0.47.0 - Grade 5 Curriculum Depth, Question Families & Representation

MathQuest now expands the mathematical content available to its adaptive engine. High-value Level 5 targets use reusable question families with meaningful variation, including equivalent fractions, multiplication and division relationships, number patterns, and perimeter and area.

- Targeted sessions can route these skills to dedicated generators rather than loosely related generic practice.
- Family metadata records representation and evidence characteristics on the existing question payload without creating a second mastery model.
- A Level 5 coverage matrix records strong, adequate and limited areas and names deferred gaps.
- Diagnostic integrity, Level 5/6 progression, Story Adventure, Extra Practice, hints, worked examples, Parent Tests and existing worksheet history remain preserved.
- Physical iPhone/iPad acceptance remains pending until tested on real devices.

## v0.46.0 - Adaptive Learning Loop & Next-Session Intelligence

MathQuest now interprets what happened during a targeted learning session and uses that evidence to shape the next learning experience. Existing outcome mastery, support evidence, challenge thresholds, prerequisite routing and spaced review remain authoritative.

- Recent targeted sessions produce explicit internal follow-through decisions such as reteach, check independence, transfer, review later and challenge.
- Supported success is distinguished from later independent success, with learner-safe next-action language.
- Best Next Step and targeted session planning reuse recent evidence without introducing a global grade or second mastery model.
- Parent Learning Intelligence can inspect the evidence and resulting next action.
- Physical iPhone/iPad acceptance remains pending until tested on real devices.

## v0.45.0 - Targeted Session Evidence & Adaptive Follow-through

- Best Next Step now has live student and parent follow-through from the targeted worksheet it creates.\n- Targeted worksheets now retain purpose, target skill, planned stages and a pre-session evidence snapshot using the existing worksheet payload contract.
- Completion summaries derive support-to-independence messages and independent-check counts from actual attempts.
- Parent Dashboard can inspect the latest targeted session's purpose, target, support use, independent checks and before/after evidence.
- Student Home and completion now use the targeted learning components in the live application path.
- Existing mastery, progression, diagnostic, review, prerequisite, Story Adventure and Home Assistant contracts remain authoritative.
- Physical iPhone/iPad acceptance remains pending until tested on real devices.

## v0.44.0 - Targeted Learning Sessions & Skill-Level Progression

- Added an explicit targeted-learning session plan derived from the existing outcome mastery, Best Next Step, prerequisite and review evidence rather than introducing a second mastery model.
- Made recommended sessions deliberately compose around the recommended target skill or prerequisite instead of relying on a generic topic worksheet to contain useful practice by chance.
- Added purposeful session roles for reconnecting prior knowledge, supported practice, core practice, transfer and independent checking while keeping help available throughout the session.
- Preserved skill-sensitive progression and the existing challenge-readiness thresholds: at least six relevant recent questions, at least 82% independent success and no more than 25% support dependency.
- Added learner-safe Today’s Focus and targeted completion interpretation that can recognise support earlier in a session followed by later independent success.
- Added parent visibility into the next targeted learning plan, including purpose, target outcome/skill, prerequisite relationship and planned question sequence.
- Kept diagnostic uncertainty as a signal for subsequent targeted learning rather than expanding or repeatedly requiring the six-question diagnostic.
- Preserved Story Adventure as presentation over the same learning evidence path, Math Mentor, hints, worked examples, learner states, Progress, Parent Tests, worksheet history/resume and Home Assistant ingress.
- Added focused backend/frontend regression coverage and real-device acceptance criteria; physical device validation remains pending.

## v0.43.0 - Diagnostic Interpretation, Placement & Learning Path

- Turned the six-question Level 5/6 diagnostic into conservative placement evidence that feeds the existing outcome-mastery and adaptive-learning architecture.
- Mapped Level 5 operations and Level 6 fraction/decimal diagnostic evidence into existing curriculum outcome evidence without a second mastery score or table.
- Replaced overall estimated-level classification with learner-safe stronger-evidence, supported-practice and more-evidence-needed interpretation.
- Kept Best Next Step, prerequisite routing, review scheduling and challenge readiness authoritative; three diagnostic questions cannot bypass the existing six-question, 82% independent-success and 25% support-dependency progression thresholds.
- Preserved ordinary historical worksheet evidence while using only the latest diagnostic as current diagnostic evidence; older retakes remain in parent history without accumulating readiness or retention.
- Added learner-safe Your Starting Point after diagnostic completion and in Progress, without pass/fail, overall Grade 5/6 classification, mastery percentages or curriculum codes.
- Added parent diagnostic insight with Level 5/6 independent/eventual success, support use, sampled outcomes, prior evidence and recommended next focus.
- Preserved Story Adventure, Math Mentor, hints, worked examples, confidence evidence, Parent Tests, worksheet history/resume and Home Assistant ingress.
- Added focused backend/frontend regression coverage and real-device acceptance criteria; physical device checks remain pending.

## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

- Replaced the student mobile scroll-to-anchor navigation model with real Home, Adventure, Worksheets and Progress destinations.
- Simplified Home so current learning, Best Next Step, learner-safe extra practice and compact destination previews no longer compete with the complete Adventure, worksheet-history and Progress experiences.
- Distinguished untouched worksheets as Ready to Start from genuinely resumed Continue Learning work.
- Removed student-facing intervention terminology, raw independent/support percentages, adaptive mode labels and curriculum outcome codes while preserving the underlying learning evidence and session services.
- Changed learner-facing Review due wording to Ready to review and hid zero-value Progress summaries.
- Grouped Progress skills under one concise learner-state explanation and removed raw success/support percentages from the student Progress surface.
- Moved full Story Adventure ownership to Adventure, full worksheet history to Worksheets, and Weekly Activity to Progress while preserving Story Adventure's existing adaptive session contract.
- Replaced the old student Home streak/accuracy/question-count/highest-level and Skill Map emphasis with concise learning guidance and destination previews.
- Kept the existing v0.41 learning-state derivation, adaptive thresholds, recommendation logic, review scheduling, prerequisites, Math Mentor, hints, worked examples and Parent Learning Intelligence unchanged.
- Added regression coverage for destination navigation, Ready to Start semantics, learner-safe extra-practice wording, Ready to review language, grouped Progress and learner-friendly weekly activity.
