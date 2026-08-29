# MathQuest Product Roadmap

MathQuest is a Victorian Curriculum aligned, adaptive mathematics learning application for short, purposeful daily practice. This file is the authoritative development roadmap for repository tooling and DevHub.

## v0.34.0 - Story Adventure Expansion and Purposeful Daily Learning

Status: Completed

### Learning
- [x] Make Story Adventure a presentation layer over the same adaptive learning engine used by Daily Practice.
- [x] Preserve skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- [x] Record Story Adventure answers through the existing worksheet, attempt, support and mastery evidence architecture.
- [x] Keep Story Adventure completion and progression separate from mastery evidence.
- [x] Keep Parent Tests isolated from Story Adventure framing and adaptive recomposition.

### UX
- [x] Add reusable short adventure themes with setting, objective, stages and an ending.
- [x] Support 5, 10 and 15-minute Story Adventure sessions.
- [x] Add lightweight stage and mission progress without introducing a game engine.
- [x] Preserve immediate retry after an incorrect answer.
- [x] Keep Hint, Teach me, Worked example and Math Mentor optional and question-specific.
- [x] Reuse Visual Mathematics only where it supports understanding.

### Testing
- [x] Verify Story Adventure preserves adaptive questions, learning purpose and difficulty metadata.
- [x] Verify prerequisite, consolidation, misconception repair, spaced review and controlled challenge remain available.
- [x] Verify Story Adventure evidence feeds the existing learning model without creating mastery from story completion.
- [x] Verify Parent Test isolation and session resume behaviour.
- [x] Validate frontend dependencies with npm ci, tests and production build.

## v0.33.0 - Adaptive Daily Learning

Status: Completed

### Learning
- [x] Classify daily practice as current learning, consolidation, spaced review or limited challenge from learner evidence.
- [x] Require repeated independent success before progression.
- [x] Make progression support-aware and misconception-aware.
- [x] Reuse spaced-review evidence for purposeful retrieval.
- [x] Keep Parent Tests isolated from adaptive session composition.

### Testing
- [x] Cover insufficient evidence, independent progression, support-heavy success, isolated mistakes and misconception-triggered consolidation.

## v0.32.3 - Grade 5 Method-First Math Mentor

Status: Completed

### Learning
- [x] Improve written multiplication, partition division, decimal hundredths, perimeter and area tutoring.
- [x] Preserve progressive hints and worked examples using different numbers from the active question.
- [x] Connect formulas and written methods back to mathematical meaning and place value.

### Testing
- [x] Add regression coverage for method-first tutoring and Grade 5 difficulty boundaries.

## v0.32.2 - Grade 5 Algebra Variety

Status: Completed

### Learning
- [x] Add numerical pattern continuation, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- [x] Mix new structures into the existing Algebra pool rather than replacing established practice.
- [x] Preserve adaptive difficulty, learning evidence, Math Mentor and worksheet-quality safeguards.

### Testing
- [x] Add large-sample generation and structural-diversity tests.

## v0.32.1 - Worksheet Learning Quality Corrective Release

Status: Completed

### Learning
- [x] Preserve retry-first incorrect-answer behaviour with tutoring support remaining optional.
- [x] Tighten worked-example alignment across Probability, fractions, Measurement, Space and Statistics.
- [x] Limit overly simple arithmetic to purposeful retrieval once learner evidence supports progression.
- [x] Preserve denominator-accurate fraction number lines and visual-state isolation.

### Testing
- [x] Recheck post-transform question-family diversity and worked-example alignment.

## v0.32.0 - Parent Learning Intelligence

Status: Completed

### Learning
- [x] Add parent-facing Secure, Developing, Needs Support, Review Due and Not Enough Evidence states.
- [x] Distinguish first-attempt, eventual, independent and supported success.
- [x] Add evidence confidence, prioritised recommendations, misconception grouping, prerequisite visibility and retention status.
- [x] Add 7, 30 and 90-day learning comparisons.

### UX
- [x] Present learning evidence in plain language without exposing internal mastery scores as false precision.

## v0.31.0 - Tablet Learning and Math Mentor Refinement

Status: Completed

### Learning
- [x] Raise appropriate Number practice toward hundreds-based addition and subtraction when evidence supports progression.
- [x] Make Teach me and hints question-specific.

### UX
- [x] Improve tablet portrait and landscape worksheet use.
- [x] Preserve retry-first behaviour, keyboard autofocus and Visual Mathematics.

## v0.35.0 - Home Assistant Parent Integration

Status: Planned

### Learning
- [ ] Expose parent-readable learning state derived from MathQuest's existing Learning Intelligence rather than duplicating mastery logic in Home Assistant.
- [ ] Surface purposeful daily-practice completion, current learning focus, review-due state, persistent support needs and meaningful progress.
- [ ] Keep Story Adventure activity inside the same evidence model as Daily Practice.
- [ ] Preserve Parent Test isolation.

### UX
- [ ] Provide a compact, stable Home Assistant entity/API model rather than an entity for every internal metric.
- [ ] Add concise parent-facing weekly learning summaries and notification-ready learning signals without notification overload.
- [ ] Preserve local-first privacy, Home Assistant ingress compatibility and responsive learner/parent experiences.

### Testing
- [ ] Verify Home Assistant learning state agrees with the Parent Dashboard and existing backend Learning Intelligence.
- [ ] Verify stable identifiers, no-data behaviour, restart recovery and Parent Test isolation.
- [ ] Preserve complete backend/frontend regression coverage, npm ci, frontend tests and production build validation.

## Future - Learner Experience and Curriculum Depth

Status: Planned

### Learning
- [ ] Continue expanding Grade 5 question variety and appropriate difficulty using real learner evidence.
- [ ] Improve continuity between learner recommendations, Daily Practice and Story Adventure.
- [ ] Expand Victorian Curriculum coverage while preserving verified outcome mapping.
- [ ] Add richer Visual Mathematics only where representations improve understanding.
- [ ] Continue improving hints, Math Mentor and worked examples when real usage identifies teaching gaps.

### UX
- [ ] Expand Story Adventure themes and context where engagement improves without weakening mathematical clarity.
- [ ] Continue improving parent progress visibility and learning-goal planning.

### Platform
- [ ] Consider consolidation of historical backend version-wrapper architecture as a focused platform release.
- [ ] Continue dependency, security, performance and Home Assistant operational maintenance.
