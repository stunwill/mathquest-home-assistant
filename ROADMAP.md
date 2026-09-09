## v0.45.0 - Targeted Session Evidence & Adaptive Follow-through

Status: In release validation

### Learning continuity
- [x] Persist targeted-session intent alongside the existing worksheet so the session can be interpreted after completion.
- [x] Capture pre-session outcome evidence and compare it with post-session evidence from the existing mastery service.
- [x] Make learner completion language reflect actual support use and independent checks without exposing technical analytics.
- [x] Add parent visibility into the latest targeted session's purpose, evidence and before/after question counts.
- [x] Integrate the existing targeted preview and completion components into the real student and parent application flows.

### Testing and acceptance
- [x] Add backend regression coverage for follow-through metadata, session evidence and learner-safe summaries.
- [ ] Complete backend, frontend, metadata and aarch64 startup/health validation for the final release head.
- [ ] Complete the physical-device checklist in `questmath/MANUAL_ACCEPTANCE_0.45.0.md` on iPhone and iPad 10th-generation hardware.

## v0.44.0 - Targeted Learning Sessions & Skill-Level Progression

Status: In release validation

### Targeted learning architecture
- [x] Add an explicit session-learning plan derived from existing outcome mastery, Best Next Step, prerequisite and review evidence rather than a parallel mastery model.
- [x] Make recommended sessions deliberately compose around the recommended instructional skill or prerequisite.
- [x] Add purposeful reconnect, supported-practice, core-practice, transfer and independent-check roles without disabling learner support.
- [x] Preserve skill-sensitive progression and the existing six-question / 82% independent-success / 25% support-dependency challenge thresholds.
- [x] Prefer targeted follow-up learning to repeated diagnostic retesting when evidence is uncertain.

### Learner and parent guidance
- [x] Add a concise learner-safe Today’s Focus preview for the next targeted session.
- [x] Add evidence-based targeted completion interpretation, including support-earlier/later-independent patterns where genuinely observed.
- [x] Keep the existing learner-state Progress model authoritative.
- [x] Add parent visibility into session purpose, target outcome/skill, prerequisite relationship and planned sequence.
- [x] Preserve Story Adventure as a presentation layer over the shared learning/evidence path.

### Testing and acceptance
- [x] Preserve existing backend and frontend regression suites while adding focused v0.44 targeting coverage.
- [ ] Complete backend, frontend, metadata and aarch64 startup/health validation for the final release head.
- [ ] Complete the physical-device checklist in `questmath/MANUAL_ACCEPTANCE_0.44.0.md` on iPhone and iPad 10th-generation hardware.

## v0.43.0 - Diagnostic Interpretation, Placement & Learning Path

Status: Completed

### Diagnostic interpretation and evidence
- [x] Feed the six-question Level 5/6 diagnostic into the existing outcome-mastery architecture without a parallel mastery score or table.
- [x] Treat three Level 5 and three Level 6 questions as placement evidence rather than whole-level mastery or a global grade classification.
- [x] Distinguish independent first-attempt success, eventual supported success and insufficient evidence.
- [x] Preserve ordinary historical worksheet evidence while using the latest diagnostic as the active diagnostic placement signal.
- [x] Preserve earlier diagnostic attempts in parent-visible history without allowing retakes to accumulate challenge-readiness or retention evidence.
- [x] Preserve existing challenge-readiness thresholds, prerequisite routing and spaced-review behaviour.

### Learner and parent guidance
- [x] Replace overall estimated-level interpretation with learner-safe Your Starting Point guidance.
- [x] Keep Best Next Step authoritative and explain the next focus without exposing curriculum codes, mastery percentages or internal adaptive modes.
- [x] Add the Starting Point summary to student Progress without expanding Home back into a long dashboard.
- [x] Add detailed parent diagnostic insight covering Level 5/6 independent/eventual success, support use, sampled outcomes, prior evidence and recommended next focus.
- [x] Preserve Story Adventure as a presentation layer over the normal adaptive learning and evidence path.

### Testing and acceptance
- [x] Add backend regression coverage for mastery integration, conservative uncertainty, historical evidence, retakes, prerequisites and unchanged challenge thresholds.
- [x] Add frontend regression coverage for learner-safe diagnostic selection, completion and placement guidance.
- [x] Complete backend, frontend, metadata and aarch64 startup/health validation for the final release head.
- [ ] Complete the physical-device checklist in `questmath/MANUAL_ACCEPTANCE_0.43.0.md` on iPhone and iPad 10th-generation hardware.

## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

Status: In release validation

### Student information architecture
- [x] Turn Home, Adventure, Worksheets and Progress into meaningful student destinations rather than scroll anchors in one long dashboard.
- [x] Keep Home focused on the next learning action with concise Adventure and Progress previews.
- [x] Make Adventure own the complete Story Adventure catalogue and duration controls.
- [x] Make Worksheets own full worksheet history, resume and review actions.
- [x] Make Progress own learner-state detail and Weekly Activity.

### Learner language and guidance
- [x] Replace student-facing intervention terminology with Extra Practice-style language while preserving the backend support-session model.
- [x] Present spaced retrieval as Ready to review rather than overdue work.
- [x] Group learner states under concise explanations and hide unnecessary zero-value summaries.
- [x] Remove raw mastery/support percentages and internal analytics from the primary student Progress display.
- [x] Preserve evidence-grounded recommendation explanations and existing adaptive thresholds.

### Testing and acceptance
- [x] Add/update student-observable regression coverage for destination ownership, learner language, Ready to Start semantics and Progress density.
- [ ] Complete backend, frontend, metadata and aarch64 startup/health validation.
- [ ] Complete the real-device checklist in `questmath/MANUAL_ACCEPTANCE_0.42.0.md` on iPhone and iPad 10th-generation hardware.

## Future - Learner Experience and Curriculum Depth

Status: Planned

### Learning
- [ ] Continue expanding Grade 5 question variety and appropriate difficulty using real learner evidence.
- [ ] Expand skill-specific targeted generators beyond the strongest currently supported outcomes while preserving verified curriculum mapping.
- [ ] Expand Victorian Curriculum coverage while preserving verified outcome mapping.
- [ ] Add richer Visual Mathematics only where representations improve understanding.

### UX
- [ ] Continue improving parent and student reporting from real evidence rather than adding generic game mechanics.
- [ ] Complete physical-device acceptance for releases that currently carry pending iPhone/iPad checks.

### Platform
- [ ] Consolidate historical backend version wrappers in a dedicated compatibility release when justified by maintenance cost and regression coverage.
- [ ] Review and remediate Vite/Vitest audit findings in a dedicated toolchain change if a safe compatible upgrade cannot be kept inside a focused product release.
