# MathQuest 0.30.1

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to Victorian Curriculum F–10 Version 2.0 Level 4, with learning progression targeted toward upper Grade 5 mathematics.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Duplicate-safe question generation with visual question guardrails
- Question overview and navigation status panel
- Immediate retry-first feedback with optional Math Mentor support
- Six Level 4 strands and VCAA content-description codes
- Adaptive strand weighting and progressive difficulty
- Parent curriculum tracker, support flags and incorrect-answer review
- CSV and PDF reports
- SQLite backup and restore API
- Home Assistant ingress and persistent `/data` storage
- Installation-specific JWT signing and failed-login throttling
- Number & Algebra Focus quests for targeted fact recall and equation practice
- Contextual strategy cards, written subtraction regrouping and retention review indicators
- Three-stage guided tutoring across arithmetic, fractions, measurement, grids, time, data and equations
- A responsive Interactive Maths Lab available from learner questions
- Shared Visual Mathematics components used by worksheet visuals and Maths Lab manipulatives
- Equal-sized whole fraction comparisons with clear denominator partitions and numerator shading
- Interactive fraction bars, equivalent-fraction models and fraction number-line representations
- Reusable number-line, array, place-value and measurement models
- Question-specific visual recommendations that connect the diagram to the calculation
- Multiple solution strategies presented one at a time through Show another way
- Learning-evidence-driven visual suggestions that remain optional and never auto-open the Maths Lab
- Assessment-integrity safeguards that suppress new teaching strategies and recommendations in parent tests
- Coherent Story Adventures with adaptive learning goals, shared mission data, chapter progress and final outcomes
- Outcome mastery, deterministic spaced reviews, prerequisite routing and personalised next-session recommendations
- Parent reporting for diagnostic and outcome growth, independent and supported accuracy, weekly progress, retention and review-due learning
- Persistent Home Assistant service authentication and dashboard-ready category, outcome and recommendation metrics
- Parent-only test worksheets with isolated test evidence, question and overall notes, feedback status and addressed-release traceability
- Number and Algebra interventions that select the weakest prerequisite, teach with linked models and report independent understanding separately
- React-owned question visuals and support tools with per-question visual identity and saved answer drafts
- Reconciled worksheet, calendar, parent and Home Assistant evidence counts
- Configuration-managed parent and student credentials that safely update existing accounts on restart
- Visual rotational-symmetry hints, recent-question duplicate protection and faithful worksheet-review visuals
- Accessible review dialogs and keyboard-first answer and continuation flow
- Collapsible Math Mentor panels with question-specific guided recovery, worked examples and browser text-to-speech support
- v0.29.1 corrective guards for grid visuals, keyboard autofocus, semantic duplicate prevention and explicit grouped-unit wording
- v0.30.1 completion recommendations based on broader persisted learner evidence rather than only the just-finished worksheet
- v0.30.1 question-family diversity guard that treats parameter-only variants as the same family and avoids consecutive repeats when alternatives exist
- v0.30.1 denominator-accurate fraction number lines with equal subdivisions and endpoint-safe labels
- v0.30.1 Probability visual relevance guard that prevents unrelated number-line teaching prompts

## Upgrade compatibility

The app slug and database path remain `questmath`, preserving the existing Home Assistant app identity and `/data/questmath.db`. This corrective release adds no destructive database migration and does not replace existing worksheets, answers, attempts, learning evidence, progress or user IDs.

MathQuest persists its JWT signing secret separately at `/data/jwt-signing-secret` and its Home Assistant service token at `/data/ha-service-token`. Existing secrets and service tokens remain valid across this upgrade.

Change parent and student usernames or passwords in the Home Assistant add-on Configuration page, save, then restart MathQuest. Startup reconciles those values with the existing managed accounts without replacing their IDs or learning data.
