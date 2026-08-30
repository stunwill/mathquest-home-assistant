# MathQuest Product Roadmap

MathQuest is a Victorian Curriculum aligned, adaptive mathematics learning application for short, purposeful daily practice. This file is the authoritative development roadmap for repository tooling and DevHub.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

Status: Completed

### Reliability
- [x] Fix Parent Learning Intelligence rendering when data transitions from initial loading to loaded state.
- [x] Prevent required Parent Dashboard bootstrap failures from leaving an indefinite splash screen.
- [x] Let backups and optional learning-intelligence sections degrade independently without blocking the core parent experience.
- [x] Preserve Home Assistant ingress, authentication, Parent Tests and learner functionality.

### Testing
- [x] Add regression coverage for the Parent Learning Intelligence null-to-loaded render lifecycle.
- [x] Keep release metadata and runtime-version validation aligned with the corrective release.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

Status: Completed

### Learning
- [x] Expose parent-readable learning state derived from MathQuest's existing Learning Intelligence rather than duplicating mastery logic in Home Assistant.
- [x] Surface meaningful daily-practice completion, current learning focus, review-due state, persistent support needs, repeated misconceptions and meaningful progress.
- [x] Keep Story Adventure activity inside the same evidence model as Daily Practice.
- [x] Preserve Parent Test isolation from ordinary daily learning and Home Assistant learner-state calculations.
- [x] Keep Home Assistant educational decisions backend-authoritative inside MathQuest.

### UX
- [x] Provide a compact stable Home Assistant entity/API contract instead of an entity for every internal metric.
- [x] Add concise parent-facing seven-day learning summaries and notification-ready learning signals without per-question notification noise.
- [x] Distinguish actual elapsed learning time from configured timed-session targets.
- [x] Document standard Home Assistant REST sensor and reminder automation examples without requiring HACS.
- [x] Preserve local-first privacy, Home Assistant ingress compatibility and existing learner/parent experiences.

### Testing
- [x] Verify Home Assistant learning state consumes Parent Learning Intelligence and adaptive-purpose evidence.
- [x] Verify Daily Practice and Story Adventure completion behaviour and Parent Test isolation.
- [x] Verify stable identifiers, no-data behaviour, restart-safe state derivation, review due, support dependence, misconception and meaningful-progress signals.
- [x] Preserve complete backend/frontend regression coverage, npm ci, frontend tests and production build validation.

## v0.34.0 - Story Adventure Expansion and Purposeful Daily Learning

Status: Completed

### Learning
- [x] Make Story Adventure a presentation layer over the same adaptive learning engine used by Daily Practice.
- [x] Preserve skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- [x] Record Story Adventure answers through the existing worksheet, attempt, support and mastery evidence architecture.
- [x] Keep Story Adventure completion and progression separate from mastery evidence.
- [x] Keep Parent Tests isolated from Story Adventure framing and adaptive recomposition.

### UX
- [x] Add short staged adventures using existing 5, 10 and 15-minute session lengths.
- [x] Preserve current worksheet navigation, tutoring, Visual Mathematics and review behaviour.

### Testing
- [x] Verify Story Adventure questions preserve backend-selected learning purpose and difficulty.
- [x] Verify adventure framing does not create separate mastery evidence.

## Future - Learner Experience and Curriculum Depth

Status: Planned

### Learning
- [ ] Continue improving adaptive learning quality across Victorian Curriculum Level 5 content.
- [ ] Continue improving misconception repair and spaced retrieval coverage.
- [ ] Continue expanding purposeful question variety without reducing educational quality.

### UX
- [ ] Continue improving Story Adventure presentation and motivation while preserving the existing learning engine.
- [ ] Continue improving parent progress visibility and learning-goal planning.

### Platform
- [ ] Continue improving Home Assistant integration, release observability and operational reliability.
