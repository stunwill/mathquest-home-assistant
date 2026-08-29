# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.35.0, Home Assistant Parent Integration and Actionable Learning Insights

This release makes MathQuest's existing learning intelligence genuinely useful to a parent through Home Assistant without creating a second mastery system.

### One learning-intelligence source

- Keep MathQuest backend-authoritative for mastery, progression, prerequisites, retention, review, misconceptions and recommendations.
- Reuse Parent Learning Intelligence, Adaptive Daily Learning and Story Adventure evidence rather than reimplementing those algorithms for Home Assistant.
- Keep Parent Dashboard and Home Assistant learning state aligned through shared backend helpers.

### Actionable parent learning state

- Expose a compact Home Assistant learning summary covering daily completion, current focus, review due, persistent support needs, repeated misconceptions, meaningful progress and a weekly summary.
- Use stable conceptual identifiers suitable for dashboards and automations.
- Avoid exposing every internal statistic as a separate entity.
- Preserve evidence confidence and use parent-readable learning-purpose labels.

### Daily learning and timing

- Count completed Daily Practice and Story Adventure sessions with answered-question evidence as legitimate daily learning.
- Do not count opening the app, starting a worksheet, abandoned no-evidence work or Parent Tests as completed daily learning.
- Distinguish actual elapsed learning time from configured 5, 10 or 15-minute session targets to avoid false precision.

### Conservative alerts

- Surface review-due state from existing spaced-retrieval and retention evidence.
- Surface persistent support dependence only after accumulated evidence, not a single difficult question.
- Surface repeated misconception evidence only after existing misconception thresholds are met.
- Surface meaningful progress from secure learning evidence or strong trend changes, not XP or Story Adventure completion.
- Provide notification-ready state without hard-coding reminder schedules or creating notification spam.

### Privacy and performance

- Keep learning data local and use the existing persistent Home Assistant service token.
- Add no cloud telemetry, analytics or third-party learner tracking.
- Use compact summary queries and reuse existing learning-intelligence calculations rather than continuous full-history recomputation.

### Release acceptance criteria

- `/api/ha/learning` returns stable parent-readable learning state.
- `/api/ha/weekly-summary` returns a concise educationally useful seven-day summary.
- Daily Practice and Story Adventure contribute legitimate activity.
- Parent Tests remain isolated.
- No-data and insufficient-evidence states are meaningful rather than misleadingly unavailable.
- Stable Home Assistant identifiers do not include worksheet, question, date, adventure or skill IDs.
- Frontend validation continues to use the committed dependency lockfile with `npm ci`, tests and production build.
- Full backend, frontend, production build, version and release-validation checks pass before merge.

## Recently completed release, 0.34.0, Story Adventure Expansion and Purposeful Daily Learning

- Made Story Adventure a presentation layer over the same adaptive learning plan as Daily Practice.
- Preserved skill, difficulty, learning purpose, prerequisite routing, spaced retrieval, misconception repair and challenge decisions.
- Preserved retry-first answers and optional tutoring.
- Kept Story Adventure evidence inside the existing learning model while ensuring story completion itself is not mastery evidence.

## Recently completed release, 0.33.0, Adaptive Daily Learning

- Classified practice questions as current learning, consolidation, spaced review or limited challenge from learner evidence.
- Added controlled progression requiring repeated independent success before challenge increases.
- Made progression support-aware and misconception-aware.
- Reused spaced-review evidence and preserved Parent Test isolation.

## Recently completed release, 0.32.3, Grade 5 Method-First Math Mentor

- Improved written multiplication, partition division, decimal hundredths, perimeter and area tutoring.
- Preserved progressive hints and different-number worked examples.
- Connected formulas and written methods back to mathematical meaning and place value.

## Recently completed release, 0.32.2, Grade 5 Algebra Variety

- Added numerical pattern continuation, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown-start problems and reverse multiplication/doubling.
- Mixed new structures into the existing Algebra pool instead of replacing established practice.
- Preserved adaptive difficulty, learning evidence, Math Mentor and worksheet-quality safeguards.

## Recently completed release, 0.32.1, Worksheet Learning Quality Corrective Release

- Preserved immediate retry after an incorrect answer with Math Mentor remaining optional.
- Tightened worked-example alignment.
- Limited very simple arithmetic to purposeful retrieval once learner evidence supports progression.
- Preserved fraction number-line and visual safeguards.

## Recently completed release, 0.32.0, Parent Learning Intelligence

- Added plain-language parent learning summaries generated from learner evidence.
- Distinguished first-attempt, eventual, independent and supported success.
- Added Secure, Developing, Needs Support, Review Due and Not Enough Evidence skill states.
- Added evidence confidence, recommendations, misconception grouping, prerequisite visibility, retention and spaced-review status.
- Added 7, 30 and 90-day learning comparisons.

## Further learner experience improvements

- Expand adventure themes and context where real usage shows it improves engagement without weakening mathematical clarity.
- Improve continuity between learner recommendations, Daily Practice and Story Adventure.
- Continue refining Grade 5 question variety and appropriate difficulty based on evidence from real sessions.
- Add richer visual models where they improve understanding rather than decoration.

## Later opportunities

- Deeper Parent Learning Intelligence and learning-goal planning.
- Additional verified Victorian Curriculum coverage.
- Richer Visual Mathematics models and manipulatives.
- Dependency/security maintenance without unsafe forced upgrades.
- Performance and Home Assistant operational improvements where real usage demonstrates a need.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
