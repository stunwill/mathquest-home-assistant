# MathQuest v0.39.0 Evidence-Based Product Review

## Baseline

The review started from merged `main` at `995950497115ac33d96d86f8df9b9494821dc601`, released as MathQuest v0.38.1. v0.38.1 had green validation and release workflows and no open pull requests at the start of this review.

## Learning-system findings

MathQuest is strongest where learner evidence, adaptive purpose, support use, misconception evidence and retention are already connected. The iPad feedback path, interactive mathematics, Story Adventure presentation layer and Parent Test isolation also have substantial regression coverage.

The main weakness is final-session composition. Several historical layers independently improve questions—duplicate guards, trivial-arithmetic suppression, adaptive recomposition, reasoning augmentation and v0.38.1 arithmetic upgrades—but there was no final policy that assessed the worksheet as a complete learning session. As a result, individually valid questions could still be structurally repetitive, and late replacements could leave earlier adaptive annotations describing a question that was no longer present.

Exact duplicate prevention was stronger than near-duplicate prevention. Existing question-family logic generally groups by skill, but it does not remember recent structural exposure across completed learner sessions. Repeated calculations with changed numbers can therefore remain educationally similar while passing exact-identity checks.

Difficulty metadata was also mostly categorical. Existing retrieval/instructional/challenge bands are useful for session balance, but direct arithmetic can expose more reliable dimensions without creating a new difficulty engine: operation, operand digit counts, regrouping demand and representation.

## Prioritised opportunities

### P0 — Release metadata integrity

**Problem:** the merged v0.38.1 product had `questmath/app/frontend/package.json` still reporting `0.35.0`, while the add-on, frontend display, backend runtime and release were 0.38.1. The version validator did not inspect the package manifest and was hard-coded to `v0381.py`.

**Impact:** release tooling can report internally inconsistent versions and a future backend wrapper can be missed by validation.

**Selected response:** make the active runtime module discoverable from the startup script and validate `package.json` as a release-authoritative location. Keep lockfile dependency metadata validation focused on `npm ci` compatibility rather than treating npm's root lock metadata as a second product-version authority.

**Complexity/risk:** low.

### P1 — Session-level learning quality

**Problem:** final worksheets can pass multiple per-question guards yet still contain structurally repetitive work.

**Impact:** reduced information value from a short session and avoidable learner boredom.

**Selected response:** add a final quality policy for normal learner worksheets that checks meaningful structure, accidental low-complexity work and bounded recent exposure. Preserve purposeful review/consolidation/retrieval.

**Complexity/risk:** medium. The policy is implemented as a final wrapper rather than replacing the established adaptive engine.

### P1 — Adaptive annotation continuity

**Problem:** late question replacement can occur after adaptive learning-purpose annotations were generated.

**Impact:** parent-facing recommendations and later evidence can describe stale question metadata.

**Selected response:** refresh adaptive purpose/evidence annotations after final session-quality replacement while preserving the existing challenge budget.

**Complexity/risk:** medium; covered by deterministic tests.

### P1 — Learning-quality regression tests

**Problem:** existing tests are strong at generator and feature level but weaker at whole-session educational invariants.

**Impact:** future releases can regress worksheet balance without breaking individual generator tests.

**Selected response:** add deterministic tests for structural near-duplicates, multidimensional difficulty, recent-exposure scope, purposeful retrieval, Parent Test isolation, final annotations and challenge limits.

**Complexity/risk:** low to medium.

### P2 — Systematic tutoring audit

**Problem:** major Grade 5 families have aligned tutoring and different-number examples, but a complete family-by-family audit remains valuable as coverage expands.

**Evidence:** v0.32.1–v0.32.3 and v0.37 added substantial tutoring-specific coverage; no concrete new tutoring correctness defect was found in this review that justified expanding v0.39.0.

**Recommendation:** perform a dedicated audit driven by real support usage and misconception evidence rather than adding generic tutoring text now.

### P2 — Dependency/security maintenance

**Problem:** earlier releases recorded frontend audit findings. The current audit must be re-run because those historical counts may no longer be accurate.

**Recommendation:** record the v0.39.0 audit in CI/release review. Any breaking dependency upgrade should be a focused maintenance change, not forced into the learning-quality implementation.

### P2 — Curriculum depth audit

**Problem:** the repository has broad Level 5-aligned functionality and some adaptive use across Levels 2–6, but code presence alone does not prove equal depth across outcomes.

**Recommendation:** separately verify actual question-family depth, representations and teaching support against authoritative Victorian Curriculum mappings before adding new outcome codes. No unverified mapping is added in v0.39.0.

### P3 — Historical backend wrapper consolidation

**Problem:** sequential version wrappers increasingly make mutation order and release wiring harder to reason about.

**Impact:** maintenance and release risk.

**Recommendation:** a dedicated platform release should consolidate wrappers with compatibility tests. It is deliberately not combined with v0.39.0 learning changes.

### P3 — Story expansion and additional parent goal planning

The existing Story Adventure architecture correctly leaves mathematics selection to the adaptive engine, and Parent Learning Intelligence already answers the core parent questions. More themes or goal-planning UI are lower priority than proving session quality and curriculum depth.

## Selected v0.39.0 scope

1. Final session-level learning-quality policy.
2. Meaningful structural near-duplicate handling.
3. Lightweight recent-exposure awareness from existing answered learner questions.
4. Multidimensional direct-arithmetic difficulty metadata.
5. Adaptive annotation refresh after final replacement.
6. Parent Test and challenge-budget preservation.
7. Release-version validation hardening and stale frontend package-version correction.
8. Deterministic learning-quality regression coverage.

## Deliberately deferred

- broad generator expansion;
- new Story Adventure themes;
- native Home Assistant integration architecture changes;
- large backend wrapper consolidation;
- major dependency upgrades;
- unverified curriculum mapping changes;
- broad parent-dashboard redesign;
- visual changes unsupported by learner evidence.

## Manual acceptance still required

Automated tests cannot establish the subjective quality of real learner sessions or physical-device ergonomics. Review several generated Number & Algebra sessions on the real deployment, confirm useful variety without suppressing deliberate review, and retain the existing v0.38 iPad real-device checklist as outstanding unless it has actually been performed.
