# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.41.0, Student Learning Progress & Guidance

MathQuest already holds useful evidence about independent success, support use, retention, adaptive progression, prerequisites and spaced review. v0.41.0 translates appropriate parts of that existing intelligence into language the learner can understand without creating another mastery score.

### Student learning state

- Derive learner-facing states centrally in the backend from existing v0.23 outcome mastery and v0.33 Adaptive Daily Learning evidence.
- Treat limited evidence as limited evidence rather than poor performance.
- Distinguish supported eventual success from repeated independent success.
- Reuse the existing `ready_to_progress` decision for Ready for a challenge rather than adding a new threshold.
- Reuse the existing spaced-retrieval schedule for Review due.
- Keep state derivation deterministic and documented.

### Student Progress experience

- Provide a persistent Progress destination that groups learning by learner meaning: challenge-ready/strong evidence, building confidence, current practice, review and insufficient evidence.
- Prefer concise explanations to raw Level and accuracy rows.
- Keep technical evidence behind optional disclosure instead of making the student page an analytics dashboard.
- Keep Parent Learning Intelligence as the detailed evidence surface.
- Keep Parent Tests outside student navigation.

### Why this?

- Keep the existing adaptive recommendation authoritative.
- Translate diagnostic, prerequisite, review and normal-practice recommendation reasons into age-appropriate student explanations in the backend.
- Do not expose raw mastery percentages in the student's Best Next Step explanation.
- Explain spaced retrieval as purposeful review so previously successful material does not look like failure.

### Conservative evidence language

- Do not claim a before/after improvement trend unless the current evidence actually provides one.
- Do not infer readiness from one successful worksheet.
- Do not equate support-heavy eventual success with repeated independent success.
- Do not expose internal misconception codes or tell the learner they "have a misconception".
- Defer dedicated learner-facing misconception explanations until the recommendation contract can identify a specific misconception cause safely.

### Learning continuity

- Preserve worksheet generation, adaptive composition, mastery thresholds, prerequisite routing, recent exposure and difficulty adaptation.
- Preserve Math Mentor, hints, worked examples, confidence evidence, Interactive Mathematics and Visual Mathematics.
- Preserve Story Adventure as presentation over the same adaptive worksheet path.
- Preserve Parent Learning Intelligence and Parent Test isolation.
- Preserve the v0.38 worksheet interaction: Answer → Immediate feedback → Understand → Reflect → Continue.
- Preserve the v0.40 action-first mobile Home, Continue Learning priority, compact Story Adventure selector, progressive history, safe-area navigation and responsive calendar.

### Acceptance criteria

- Student learning states are derived from existing evidence and no parallel mastery score is persisted.
- Fewer than the existing minimum skill-evidence questions cannot be labelled as failure.
- Supported eventual success can produce Building confidence without becoming Ready for a challenge.
- Ready for a challenge only follows the existing adaptive `ready_to_progress` state.
- Review due follows the existing spaced-retrieval evidence.
- Best Next Step reasons shown to students contain learner-safe explanations rather than raw mastery percentages.
- Progress is accessible from mobile navigation even when unfinished work exists, without competing with Continue Learning for the main action.
- Full backend, frontend, version metadata and real aarch64 startup/health validation passes before merge.
- Physical iPhone and iPad checks remain explicitly unverified until performed on hardware.

## Recently completed release, 0.40.0, Student Mobile Home, Navigation & Responsive UX

MathQuest's learning intelligence had become stronger, but real iPhone use showed that the student Home page had accumulated too many equal-weight dashboard sections. v0.40.0 changed the information architecture so current action, unfinished work and recommended learning are easier to find while history and detailed progress use progressive disclosure or navigation.

- Promoted active worksheets and skipped-question recovery through Continue Learning.
- Limited completed history to three recent items by default.
- Added compact horizontal Story Adventure selection on narrow screens.
- Added student-only Home, Adventure, Worksheets and Progress navigation with safe-area support.
- Reduced the MathQuest mobile header beneath Home Assistant ingress.
- Corrected mobile week navigation and replaced compressed phone calendar columns with a readable activity list.
- Preserved worksheet generation, adaptive learning, Parent Learning Intelligence, Parent Tests and the v0.38 worksheet interaction.

## Recently completed release, 0.39.0, Session Learning Quality and Adaptive Continuity

MathQuest already had strong per-question generation, adaptive purpose, tutoring, interactive mathematics and duplicate safeguards. Real learner sessions nevertheless showed that a collection of individually valid questions could still form a repetitive or weak worksheet. v0.39.0 therefore treats the final worksheet as a learning product in its own right.

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

## Further learner experience improvements

- Add learner-facing misconception guidance only when the recommendation/evidence contract can prove the specific reason safely.
- Add genuine progress-over-time language only where a trustworthy comparison exists, rather than deriving trends from one rolling evidence window.
- Expand Grade 5 curriculum depth only after verifying mappings and identifying genuinely shallow outcomes.
- Audit Math Mentor and worked-example quality systematically across less-used question families based on real learner evidence.
- Improve continuity between parent recommendations, Daily Practice and Story Adventure where persisted evidence shows a gap.
- Expand adventure themes only where real usage shows engagement improves without weakening mathematical clarity.

## Later opportunities

- Deeper Parent Learning Intelligence and learning-goal planning.
- Additional verified Victorian Curriculum coverage.
- Focused dependency/security maintenance without unsafe forced upgrades.
- Performance and Home Assistant operational improvements where measurement identifies a real issue.
- Consolidation of historical backend version-wrapper architecture as a dedicated platform release with explicit compatibility and migration testing.
