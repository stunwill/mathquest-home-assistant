# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.39.0, Session Learning Quality and Adaptive Continuity

MathQuest already has strong per-question generation, adaptive purpose, tutoring, interactive mathematics and duplicate safeguards. Real learner sessions nevertheless showed that a collection of individually valid questions can still form a repetitive or weak worksheet. v0.39.0 therefore treats the final worksheet as a learning product in its own right.

### Session-level learning quality

- Run a final quality policy over normal learner worksheets after existing generators and adaptive composition.
- Detect meaningful near-duplicate mathematical structures rather than relying only on exact prompts or broad skill identities.
- For direct arithmetic, use operation, operand digit counts and regrouping demand as lightweight difficulty dimensions.
- Limit accidental low-complexity work when learner readiness supports richer practice while preserving deliberate review, consolidation and spaced retrieval.
- Use a bounded sample of recently answered Daily Practice and Story Adventure questions to deprioritise heavily repeated structures when a suitable alternative exists.
- Keep the mechanism lightweight and derived from existing persisted questions rather than creating a second mastery or exposure database.

### Adaptive continuity

- Preserve the existing Adaptive Daily Learning engine as authoritative for current learning, consolidation, spaced review and limited challenge.
- When the final quality pass replaces a question, refresh adaptive purpose and evidence annotations so Parent Learning Intelligence and future learning decisions refer to the final mathematics shown to the learner.
- Retain the established one-question challenge budget.
- Preserve prerequisite, misconception, support-dependency and retention evidence.
- Preserve Parent Test isolation.

### Release integrity

- Derive the active backend release module from the Home Assistant runtime startup script rather than pinning validation to the previous version wrapper.
- Include the frontend package manifest in release-version consistency validation so stale package metadata cannot silently persist across releases.
- Continue validating package-lock dependency metadata for `npm ci` compatibility.

### Acceptance criteria

- A normal learner worksheet cannot contain repeated structurally equivalent questions merely because the numeric values differ.
- Similar calculations are distinguished from genuinely different mathematical demand; all three-digit addition is not treated as one family.
- Purposeful review/consolidation/retrieval questions remain eligible even when easy.
- Recent exposure influences variety without overriding a genuine adaptive learning need.
- Final questions contain multidimensional difficulty metadata where it can be derived reliably.
- Adaptive purpose/evidence metadata still matches the final question after quality replacement.
- Challenge remains limited to the existing session budget.
- Parent Tests remain unchanged by session-quality recomposition.
- Story Adventure continues to use the same adaptive questions and evidence architecture.
- Full backend, frontend, metadata and real aarch64 startup/health validation passes.
- Current dependency-audit findings are recorded rather than hidden or force-fixed.

## Recently completed release, 0.38.1, Number & Algebra Quality and Melbourne Time

- Reduced repeated low-complexity direct addition/subtraction by upgrading smaller calculations to larger place-value work.
- Changed equal-groups operation-label questions into numerical-total questions.
- Corrected worksheet-history time to `Australia/Melbourne`, including AEST/AEDT handling.
- Preserved adaptive learning, Story Adventure, Parent Tests and the v0.38 feedback flow.

## Recently completed release, 0.38.0, iPad Landscape Feedback and Worksheet UX

This learner-experience release optimised the worksheet for Sienna's primary device and workflow: iPad 10th generation in landscape with a physical keyboard.

### Answer → immediate feedback → understand → reflect → continue

- Replaced below-question post-answer content with one shared accessible feedback dialog so result and next action are visible without page scrolling.
- Preserved a fast two-Enter typed-answer flow: Enter submits, feedback appears immediately, and Enter continues after a terminal answer or returns to a clean focused answer field for retry.
- Kept retry-first answers educational rather than punitive. Final working remains hidden while another attempt is expected and Math Mentor is not mandatory merely because an answer is wrong.
- Moved the existing optional confidence reflection into the dialog without changing the evidence it records or contaminating Parent Tests.
- Preserved typed, choice, interactive mathematics and Story Adventure on one answer/feedback architecture.

### iPad landscape layout and accessibility

- Added a tablet-specific landscape band around the typical iPad 10th-generation viewport.
- Reduced unnecessary header, card, progress, support and sidebar space while retaining readable question typography and useful working area.
- Kept result and primary action visible inside the dialog, with only long supporting content scrolling internally.
- Added explicit Correct answer and Incorrect answer semantics, focus movement/containment, touch-size controls, announcements and reduced-motion support.
- Preserved iPad portrait, iPhone/mobile and desktop behaviour outside the landscape-specific optimisation.

## Previous release scope, 0.37.1, Duplicate-Safe Reasoning Mix

The v0.37.1 corrective release preserves the v0.37.0 interactive mathematics scope and prevents structured reasoning augmentation from introducing duplicate worksheet question identities.

## Previous release scope, 0.37.0, Richer Interactive Mathematics and Mathematical Reasoning

This release extends MathQuest's first-class interactive answer architecture beyond whole-number number lines into a small set of representations where direct manipulation improves understanding rather than adding decoration.

### Interactive mathematics with one learning engine

- Keep MathQuest backend-authoritative for correctness, adaptive selection, progression, prerequisites, retention, misconceptions and learning evidence.
- Add interactive fraction-bar selection, fraction number-line location, scaled ruler reading and grid-reference selection through the existing worksheet answer route.
- Hide requested internal targets when labels would reveal the answer, including internal fraction-number-line ticks and ruler marks.
- Keep the interaction layer reusable and responsive rather than building unrelated one-off visual widgets.

### Mathematical reasoning

- Add structured reasonableness, conceptual comparison and age-appropriate error-analysis questions.
- Prefer assessable mathematical work over vocabulary recognition where calculation itself demonstrates the intended understanding.
- Reuse the existing misconception-evidence architecture for regrouping/place-value error analysis.
- Keep arithmetic fluency and purposeful foundational retrieval available rather than replacing calculation practice with reasoning-only sessions.

### Tutoring and Story Adventure

- Extend Math Mentor with representation-specific hints and different-number worked examples without revealing the active answer.
- Preserve immediate retry after an incorrect answer with tutoring remaining optional.
- Keep Story Adventure as presentation over the same adaptive worksheet, answer and evidence architecture.
- Preserve Parent Test isolation from learner mastery and adaptive evidence.

## Recently completed release, 0.36.0, Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Made whole-number number-line location a first-class interactive answer selected directly on the line.
- Reduced unnecessarily basic two-digit addition when learner evidence supports progression while preserving purposeful review, consolidation and retrieval.
- Defaulted the editable student username to `sienna` and made normal MathQuest token expiry return automatically to login.
- Preserved Home Assistant ingress distinction, Parent Dashboard reliability and the existing adaptive-learning architecture.

## Recently completed release, 0.35.1, Parent Dashboard Reliability

- Fixed Parent Learning Intelligence rendering and Parent Dashboard bootstrap recovery.
- Kept backups and optional learning-intelligence failures from blocking the core parent experience.

## Recently completed release, 0.35.0, Home Assistant Parent Integration and Actionable Learning Insights

- Exposed compact parent-readable Home Assistant learning state derived from MathQuest's existing Learning Intelligence.
- Added daily completion, current focus, review, support, misconception, progress and weekly-summary signals without duplicating mastery logic.
- Preserved Parent Test isolation and local-first operation.

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

- Expand Grade 5 curriculum depth only after verifying mappings and identifying genuinely shallow outcomes.
- Audit Math Mentor and worked-example quality systematically across less-used question families based on real learner evidence.
- Improve continuity between parent recommendations, Daily Practice and Story Adventure where persisted evidence shows a gap.
- Expand adventure themes only where real usage shows engagement improves without weakening mathematical clarity.
- Add further visual models only where they materially improve mathematical understanding.

## Later opportunities

- Deeper Parent Learning Intelligence and learning-goal planning.
- Additional verified Victorian Curriculum coverage.
- Focused dependency/security maintenance without unsafe forced upgrades.
- Performance and Home Assistant operational improvements where measurement identifies a real issue.
- Consolidation of historical backend version-wrapper architecture as a dedicated platform release with explicit compatibility and migration testing.
