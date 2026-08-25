# MathQuest Product Roadmap

## Product objective

MathQuest should help Sienna, a Grade 5 learner currently needing targeted Number and Algebra support, improve through short daily tutoring sessions. It should align to Victorian Curriculum Level 5 while adapting across Levels 2–6 from a diagnostic baseline.

The target experience is not a digital worksheet. Each session should diagnose, explain, let Sienna manipulate a mathematical model, ask her to reason, provide progressively stronger help only when needed, and revisit the skill later to confirm retention.

## Current release scope, 0.32.0, Parent Learning Intelligence

This release turns MathQuest's accumulated learner evidence into a parent-facing learning intelligence system that explains progress, support dependence, retention, misconceptions and next learning priorities without overstating certainty.

### Parent learning summary

- Surface a concise plain-language summary near the top of the Parent Dashboard.
- Explain current strengths, developing skills, areas needing support and the most valuable next practice.
- Avoid generic positive language when evidence is weak.
- Use Not Enough Evidence when a reliable judgement cannot yet be made.

### Independent versus supported success

- Distinguish first-attempt success, eventual success and tutoring-supported success.
- Treat hint, Math Mentor and worked-example use as support evidence without discouraging help-seeking.
- Prevent high eventual accuracy with heavy support from being reported as equivalent to independent mastery.

### Skill-level mastery and evidence confidence

- Report skill-level states where the underlying curriculum and question metadata permit it.
- Use Secure, Developing, Needs Support, Review Due and Not Enough Evidence states.
- Use evidence volume to qualify conclusions as limited, moderate or strong.
- Centralise mastery thresholds in backend learning-intelligence logic.

### Prioritised practice plan

- Combine mastery, misconceptions, prerequisite relationships and spaced-retrieval needs into a short ordered recommendation list.
- Use High Priority, Practise, Review and Keep Going labels.
- Explain why each recommendation is being made from real learner evidence.

### Misconceptions, prerequisites and retention

- Group recurring misconception patterns only after repeated evidence.
- Explain relevant prerequisite relationships without exposing the full internal graph by default.
- Surface retained skills, Review Due skills and skills needing another check.

### Difficulty and progress reporting

- Use first-attempt accuracy, eventual accuracy and support dependency together to describe whether work is at an appropriate instructional level.
- Provide 7, 30 and 90-day comparisons while avoiding conclusions from tiny samples.
- Keep the focus on learning value rather than maximising screen time.

### Responsive parent experience

- Keep Learning summary, Needs attention, Practise next, Strengths and Progress near the top on tablet and mobile.
- Support 1920 × 1080 desktop, 1180 × 820 tablet landscape, 820 × 1180 tablet portrait, mobile and Home Assistant ingress.
- Preserve touch-friendly controls and avoid horizontal overflow.

### Data integrity and architecture

- Build reporting from existing authoritative learner evidence rather than duplicating mastery calculations in React.
- Keep Parent Test evidence completely isolated from XP, streak, mastery, misconceptions, prerequisites, recommendations, spaced retrieval and learning intelligence.
- Preserve existing learner history and upgrade compatibility.

### CI and release hardening

- Keep frontend Node/Vite typings explicit and retain `moduleResolution: Bundler`.
- Require frontend tests and the production TypeScript/Vite build as separate release gates.
- Keep package metadata and lockfiles synchronised before release.

### Release acceptance criteria

- A parent can identify current strengths, areas needing support, independence, next practice, reasons for recommendations, retention and difficulty appropriateness within roughly 30 seconds.
- Strong mastery conclusions require sufficient independent evidence.
- Repeated misconception reporting requires more than one isolated error.
- Parent Test evidence remains excluded from all learner intelligence.
- Responsive parent layouts remain usable on desktop, tablet, mobile and Home Assistant ingress.
- Complete backend, frontend, TypeScript/Vite build, version and release-validation suites pass before merge.

## Recently completed release, 0.31.0, Tablet Learning and Math Mentor Refinement

- Optimised the live worksheet for tablet portrait and landscape use.
- Raised appropriate Number practice toward hundreds-based addition and subtraction when learner evidence supports progression.
- Made Teach me question-specific and based on the actual operands and mathematical structure.
- Split hints into distinct nudge, strategy and worked-next-step stages.
- Removed duplicated tutoring presentation and improved mathematical formatting.
- Preserved retry-first behaviour, keyboard autofocus, Visual Mathematics and v0.30.1 corrective safeguards.

## Recently completed release, 0.30.1, Worksheet Quality corrective release

- Changed completion **Strongest** and **Practise next** recommendations to use broader persisted learner evidence.
- Added neutral completion wording when cross-category evidence is insufficient.
- Added question-family diversity so parameter-only variants are treated as repeats within short worksheets.
- Corrected denominator-based fraction number-line subdivisions and misleading rounded tick labels.
- Prevented unrelated number-line teaching recommendations on Probability questions.

## Recently completed release, 0.30.0, Visual Mathematics

- Added reusable Visual Mathematics components for equal-whole fraction comparison, number lines, arrays, place value and measurement.
- Added Interactive Maths Lab fraction manipulatives, equivalent-fraction and shared number-line representations.
- Added optional alternate solution strategies without changing learner answer state.
- Connected Math Mentor and misconception evidence to relevant optional visual support.
- Preserved parent-test assessment integrity and v0.29.1 corrective safeguards.

## Recently completed release, 0.29.1, Learning Intelligence corrective release

- Restored labelled grid-reference visuals after final question transformations.
- Preserved typed-answer autofocus for each new question.
- Added final semantic duplicate prevention after worksheet transformations.
- Clarified grouped-unit wording, including meal portions versus packs.
- Preserved the v0.29.0 learning-intelligence model and retry-first behaviour.

## Recently completed release, 0.29.0, Learning Intelligence

- Made Math Mentor optional after an incorrect answer.
- Added aligned worked examples with different values.
- Reduced very-easy arithmetic and increased moderate/challenging practice.
- Added persisted attempt, support and misconception evidence.
- Added prerequisite skill links and early parent recommendations.

## Upcoming release sequence

### 0.33.0, Home Assistant Parent Integration

- Parent notifications and weekly learning summaries.
- Home Assistant entities/sensors for key learning states and recommendations.
- Useful parent alerts for review due, persistent support needs and notable progress.
- Preserve local-first privacy and avoid notification overload.

### 0.34.0, Story Adventure Expansion

- Use the stronger learner model to drive adaptive Story Adventure missions.
- Make story challenges respond to mastery, prerequisites and retrieval needs rather than simply wrapping generic worksheets.
- Expand continuity, progression and themed mathematical models.

## Later opportunities

- Deeper adaptive curriculum sequencing.
- Richer visual mathematics models and manipulatives.
- Longer-term learning trend reporting.
- Teacher/tutor reporting views.
- Additional curriculum coverage.
- Consolidation of historical backend version-wrapper architecture as a focused platform release.
