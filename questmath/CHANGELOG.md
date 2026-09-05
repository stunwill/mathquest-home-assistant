## v0.42.0 - Student UX, Navigation & Learning Guidance Refinement

- Home, Adventure, Worksheets and Progress now behave as distinct student destinations instead of scroll targets within one long page.
- Home is shorter and focused on what to do next, while Adventure owns Story Adventure, Worksheets owns history and Progress owns learning states plus Weekly Activity.
- Untouched worksheets are labelled Ready to Start; Continue Learning is reserved for genuinely started work.
- Student-facing intervention terminology and raw independent/support percentages have been replaced by learner-safe Extra Practice language without changing the underlying learning service.
- Review due is presented to the learner as Ready to review, zero-value state summaries are hidden, and repeated Progress explanations are grouped for faster scanning.
- Student Best Next Step no longer exposes adaptive mode labels or curriculum outcome codes.
- The old student Home streak/accuracy/question-count/highest-level cards and technical Skill Map no longer dominate the learner experience.
- Story Adventure keeps the existing adaptive session and evidence path, and Parent Learning Intelligence remains the detailed technical evidence surface.
- Preserved Math Mentor, hints, worked examples, adaptive learning, review scheduling, prerequisite routing, worksheet scoring/completion, Parent Tests and Home Assistant integration.

## v0.41.0 - Student Learning Progress & Guidance

- Student Progress now translates existing learning evidence into understandable states: Not enough evidence yet, Practising, Building confidence, Getting stronger, Ready for a challenge and Review due.
- Best Next Step now explains why the adaptive engine selected the recommendation without exposing raw mastery percentages to the student.
- Review due is explained as purposeful retrieval practice so previously successful material does not look like a failure.
- Supported success is recognised as Building confidence while remaining distinct from repeated independent success.
- Ready for a challenge reuses the existing adaptive progression rules rather than adding a new mastery threshold.
- Student mobile Progress navigation opens the new learner-guidance section directly.
- Technical learning evidence remains available through optional detail while full Parent Learning Intelligence remains unchanged in purpose.
- Preserved worksheet generation, adaptive daily learning, Story Adventure selection, Math Mentor, Parent Test isolation and the v0.38 keyboard-first worksheet feedback flow.

## v0.40.0 - Student Mobile Home, Navigation & Responsive UX

- Reorganised the student mobile Home experience around current action rather than giving current learning, history and detailed progress equal visual priority.
- Added a dedicated Continue Learning treatment for active worksheets and skipped-question recovery so unfinished learning outranks completed history.
- Reduced mobile worksheet history to three recent items by default with explicit progressive disclosure for older work.
- Changed narrow-screen Story Adventure selection to compact horizontal cards while retaining title, purpose, likely learning focus and the existing adaptive session path.
- Added student-only Home, Adventure, Worksheets and Progress bottom navigation with text labels, accessible selected state, keyboard focus and iPhone safe-area padding.
- Reduced MathQuest mobile header height when the student navigation is present so Home Assistant ingress plus MathQuest branding consume less of the first viewport.
- Fixed the mobile weekly calendar navigation so previous/next week and Today remain readable instead of compressing five controls into unusable columns.
- Changed mobile weekly activity from a forced seven-column strip to a readable one-day-per-row activity list while retaining richer tablet and desktop controls.
- Added explicit regression coverage for Continue Learning, skipped-question recovery, three-item history disclosure, student-only navigation, Story Adventure continuity and week navigation.
- Preserved the v0.39 learning-quality engine, adaptive recommendations, Story Adventure question selection, Parent Test isolation and the v0.38 worksheet feedback/keyboard interaction.

## v0.39.0 - Session Learning Quality and Adaptive Continuity

- Session Learning Quality now checks the final learner worksheet as a whole for repeated mathematical structures, accidental low-complexity work and recently overused question patterns.
- Added multidimensional arithmetic difficulty metadata so direct calculations distinguish number size and regrouping demand rather than treating all addition or subtraction as equivalent.
- Preserved purposeful review, consolidation and retrieval while diversifying accidental near-duplicates.
- Recent answered Daily Practice and Story Adventure questions influence variety without creating a separate history or mastery system.
- Adaptive learning purpose and evidence annotations are refreshed after final worksheet-quality replacements so parent-facing learning information matches the mathematics actually shown.
- Parent Tests remain isolated and the existing one-question challenge limit is preserved.
- Release validation now derives the active backend module from the runtime configuration and checks the frontend package version alongside add-on, frontend display, backend, README and changelog versions.

## v0.38.1 - Number & Algebra Quality and Melbourne Time

- Reduced repeated low-complexity Number & Algebra addition/subtraction by upgrading smaller direct calculations to larger Grade 5-appropriate place-value work.
- Equal-groups questions now ask for the numerical total instead of only asking which operation should be used.
- Worksheet history now displays `Australia/Melbourne` local time and observes AEST/AEDT daylight-saving changes.
- Added regression tests for arithmetic difficulty, equal-groups answers and timezone conversion.

## v0.38.0 - iPad Landscape Feedback and Worksheet UX

- Replaced below-question answer results with an accessible post-answer feedback dialog so correct/incorrect status, concise mathematical support, reflection and the next action are immediately visible without page scrolling.
- Preserved retry-first learning: retryable incorrect answers do not reveal terminal working, Math Mentor remains optional, and Retry clears the previous response and returns focus to the typed-answer field.
- Made the physical-keyboard flow explicit: Enter submits a typed answer, the feedback primary action receives focus, and Enter continues or retries without requiring touch.
- Added rapid-Enter protection so a fast second key press cannot submit the same answer twice or skip a question.
- Moved learner confidence reflection into the feedback dialog while preserving the existing confidence-evidence endpoint and Parent Test isolation.
- Added restrained, non-blocking correct-answer celebration with explicit text/icon state and `prefers-reduced-motion` support.
- Added an iPad 10th-generation landscape layout band that reduces unnecessary header/card/side-panel space while preserving readable question typography and existing portrait/mobile behaviour.
- Kept whole-number number lines, fraction bars, fraction number lines, rulers, grid references, choices, structured reasoning and Story Adventure on the shared worksheet answer and feedback architecture.
- Added frontend regression coverage for keyboard submission/continuation, retry focus, optional Math Mentor, confidence evidence, focus trapping, rapid Enter, touch-first interactive answers, Story Adventure and viewport-fixed feedback.

# MathQuest Home Assistant Changelog

Concise user-facing release notes for the Home Assistant add-on. The detailed project/GitHub changelog is maintained at the repository root in `CHANGELOG.md`.

## v0.37.1 - Duplicate-Safe Reasoning Mix
- Prevent duplicate question identities when the v0.37.0 reasoning mix replaces a worksheet question.
- Preserve existing worksheet variety and retry the replacement generator before leaving the original question unchanged.

## v0.37.0 - Richer Interactive Mathematics and Mathematical Reasoning

- Interactive fractions now include selecting parts of a fraction bar and locating fractions directly on a 0-to-1 number line.
- Measurement practice can include interactive scaled rulers where the learner must work out the value of each interval before selecting the requested mark.
- Space practice can include selectable grid references so the learner chooses the actual square rather than typing a coordinate from the prompt.
- Added more mathematical reasoning, including operation selection, reasonableness, perimeter-versus-area understanding, symmetry statements and age-appropriate find-the-mistake questions.
- New interactive questions remain backend-authoritative and feed the same attempts, learning evidence, adaptive difficulty and misconception evidence as conventional questions.
- Math Mentor now gives representation-specific guidance and different-number worked examples for the new interactive models while keeping retry-first answers and optional tutoring.
- Story Adventure continues to use the same adaptive worksheet and evidence path, so compatible interactive mathematics works there without a separate story question engine.
- Preserved interactive whole-number number lines, adaptive suppression of unnecessarily basic arithmetic, session-expiry recovery, Parent Dashboard reliability, Parent Tests and Home Assistant learning APIs.

## v0.36.0 - Interactive Mathematics, Adaptive Difficulty and Seamless Student Access

- Number-line location questions can now be answered by tapping or clicking the correct tick directly on the number line instead of selecting a separate number button that repeats the requested value.
- Adaptive Number & Algebra practice now recognises overly simple two-digit additions such as `20 + 28` and reduces them when learning evidence shows the student is ready for richer work, while still allowing purposeful review and consolidation.
- New installs default the student username to `sienna`, and the login screen pre-fills `sienna` while leaving the password blank and editable parent login available.
- Expired MathQuest sessions now return automatically to the normal login screen instead of leaving the learner on a `Something went wrong - Invalid session` screen.
- Kept Home Assistant ingress failures separate from MathQuest token expiry so an ingress problem does not automatically remove otherwise valid MathQuest credentials.
- Preserved Story Adventure, Math Mentor, Parent Learning Intelligence, Parent Tests, Home Assistant learning APIs and local-first operation.

## v0.35.1 - Parent Dashboard Reliability Corrective Release

- Fixed a Parent Learning Intelligence frontend crash that could stop the Parent Dashboard rendering even though its API calls succeeded.
- Added explicit loading and error states to the Parent Dashboard bootstrap instead of leaving the screen on an indefinite spinner.
- Made backups and Parent Learning Intelligence optional sections fail independently so their API failures do not hide core parent controls, settings or learning summaries.
- Kept Parent Tests and Home Assistant ingress behaviour unchanged.

## v0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

- Added compact Home Assistant learning endpoints built from the same Parent Learning Intelligence, retention, support and misconception evidence used inside MathQuest.
- Added stable learning entities for daily learning state, current focus, review status, support status and weekly summary.
- Added notification-ready learning signals for persistent support needs, repeated misconceptions, meaningful progress and review due.
- Separated actual active minutes from configured timed-session target minutes.
- Kept Daily Practice and Story Adventure on the same learner evidence model and kept Parent Tests excluded.
- Added example Home Assistant REST sensors and reminder automations without adding any cloud dependency.
