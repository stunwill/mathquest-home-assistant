# MathQuest 0.30.0

- Added reusable Visual Mathematics components for equal-whole fraction comparison, number lines, arrays, place value and measurement.
- Expanded the Interactive Maths Lab with synchronised interactive fraction bars, shared fraction number lines and equivalent-fraction representations.
- Kept fraction comparison bars vertically aligned to equal-sized wholes with explicit denominator partitions and numerator shading.
- Added multiple valid solution strategies for suitable arithmetic, fraction, multiplication and division questions, presented one at a time through **Show another way**.
- Added question-specific visual recommendations that explain how each model connects to the calculation without automatically opening a teaching tool.
- Added learning-evidence-driven visual recommendations for repeated misconception patterns while keeping learner control.
- Suppressed new teaching strategies and visual recommendations in parent tests to preserve assessment integrity.
- Kept teaching examples on different values from assessed questions and prevented manipulatives from filling the assessed answer field.
- Added accessible mathematical descriptions, keyboard-operable visual controls, responsive layouts and reduced-motion-safe styling.
- Added v0.30 endpoints through explicit FastAPI `APIRouter` composition instead of another route-list mutation workaround.
- Preserved v0.29.1 grid visual, keyboard autofocus, semantic duplicate and grouped-unit corrective safeguards.
- Updated the canonical roadmap, release notes, Home Assistant metadata, backend entrypoint, frontend version and documentation to v0.30.0.

# MathQuest 0.29.1

- Restored grid-reference diagrams after final question-generation transformations so grid questions always retain their labelled visual.
- Preserved keyboard-first typed-answer autofocus when a new question becomes active.
- Added a final semantic duplicate-question guard across generated worksheets.
- Clarified grouped word-problem units, including specifying that hikers use meal portions rather than packs.
- Updated v0.29.1 release and version-validation metadata without changing the v0.29.0 learning-intelligence model.

# MathQuest 0.29.0

- Made Math Mentor support optional after an incorrect answer. Sienna can immediately edit and resubmit an answer without opening a hint or completing a tutoring step.
- Added question-specific, operation-aligned worked examples that use different values and the same reasoning strategy as the displayed question.
- Reduced very-easy arithmetic items outside occasional confidence-building positions and increased moderate, challenging and application generation.
- Added persisted learning evidence for attempts, first-attempt success, hints, worked examples, retries and misconception evidence signals.
- Added prerequisite skill links for core Number, Algebra, Measurement and fraction outcomes.
- Added parent-only early recommendations for recurring misconceptions and spaced retrieval.
- Added backend and frontend regression coverage for optional tutoring, aligned examples, misconception detection, prerequisite graphs, recommendations and worksheet difficulty balance.
- Updated the canonical roadmap and release metadata to v0.29.0.

# MathQuest 0.28.0

- Added the Math Mentor, a lightweight collapsible tutoring panel on every worksheet question.
- Added ask-before-tell guided recovery after an incorrect learner answer, keeping the question retryable before an answer is revealed.
- Added progressive, question-family-specific support for arithmetic, equations, fractions, measurement, grids, time and data.
- Added Math Mentor **Hint**, **Why?**, **Teach me**, **Worked example**, **Start over** and **Read aloud** actions.
- Added distinct-number worked examples, common-mistake cues and family-specific memory tips without exposing the assessed answer.
- Added browser read aloud fallback messaging so unsupported browsers retain the complete worksheet flow.
- Kept parent test assessment behaviour unchanged while allowing parent test questions to inspect Math Mentor content.
- Added backend, interaction and accessibility regression coverage for mentor progression, restart and read-aloud fallback.
- Updated the canonical roadmap with the approved v0.28.0 to v0.33.0 release sequence.

# MathQuest 0.27.0

- Fixed Home Assistant parent and student credential changes so existing managed accounts are updated on restart without changing their IDs or losing worksheet data.
- Fixed parent test worksheets returning **Worksheet not found** after a correctly accepted answer.
- Made question-level and overall parent test notes explicitly optional without blocking navigation, completion or return to the dashboard.
- Corrected duplicated wording such as **Use use a known double** in addition feedback.
- Added shared worksheet lifecycle authorisation for learner worksheets and parent-owned test worksheets.
- Made session type, duration and learning-area choices visibly selectable with persistent, accessible selected states.
- Added regular-polygon visuals and before-and-after rotation hints for rotational-symmetry questions, including reduced-motion support.
- Removed Story Adventure chapter and challenge prefixes from maths prompts while retaining mission context separately.
- Added recent learner-history duplicate protection and more statistical-survey question variants while excluding parent tests from learner history.
- Added stored question visuals to completed learner and parent-test worksheet reviews.
- Added Escape-key, backdrop-click and focus-return behaviour to worksheet review dialogs.
- Added Enter-key support for both submitting typed answers and moving to the next question or finishing a worksheet.
- Added backend and React regression coverage for credential upgrades, parent-test completion, optional notes, session choices, symmetry hints, duplicate avoidance, review fidelity and keyboard flow.

# MathQuest 0.26.0

- Added targeted 5, 10 and 15-minute Number and Algebra intervention sessions.
- Added intervention coverage for addition, subtraction, multiplication, division, fact families, written methods and unknown-value equations.
- Added check, teach, practice and retrieval phases with progressively supported learning goals.
- Added question-specific model recommendations for number lines, place value, arrays and fraction comparisons.
- Added **Why?**, **Show another way** and **Start over** support without revealing the assessed answer.
- Moved question visuals, read-aloud, scratchpad, confidence checks and guided support into the React worksheet experience.
- Added stable per-question visual identities so images cannot carry over from a previous question.
- Added saved per-question answer drafts across previous, next, exit and resume actions.
- Added vertically stacked fraction comparison models aligned to equal-sized wholes.
- Corrected grid visuals so row and column labels are shown on the axes without printing the answer inside the highlighted square.
- Reconciled answered, completed, correct, incorrect, skipped, remaining and hinted counts from one evidence calculation.
- Separated independent accuracy from supported accuracy in intervention and Home Assistant reporting.
- Kept parent test evidence excluded from Sienna's progress, mastery, XP, streak, calendar, recommendations and Home Assistant metrics.
- Reduced legacy worksheet DOM enhancement layers and replaced browser-alert failures with in-page recovery messages.
- Added backend and React regression coverage for interventions, visual ownership, answer drafts, evidence isolation and reporting reconciliation.
