# MathQuest 0.40.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, interactive mathematical models, reasoning, worksheet navigation, progress tracking and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Student and parent authentication, with `sienna` prefilled for the normal student login flow
- Automatic recovery from expired MathQuest sessions back to the login screen while keeping Home Assistant ingress failures distinct
- Action-first student mobile Home that promotes unfinished learning ahead of completed history
- Student-only mobile Home, Adventure, Worksheets and Progress navigation with iPhone safe-area support
- Compact horizontal Story Adventure selection on narrow screens while preserving adaptive learning selection
- Recent worksheet history limited to three rows by default with progressive disclosure for older work
- Responsive mobile weekly learning navigation with readable previous/next week controls and Today
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- iPad 10th-generation landscape worksheet optimisation with immediate post-answer feedback and a keyboard-first two-Enter flow
- First-class interactive whole-number number lines, fraction bars, fraction number lines, scaled rulers and grid-reference selection
- Grade 5 reasoning including reasonableness, conceptual comparison and find-the-mistake questions
- Session-level learning quality covering near-duplicate structures, recent exposure and accidental low-complexity work
- Multidimensional arithmetic difficulty metadata including digit size and regrouping demand
- Direct Number & Algebra addition/subtraction biased toward larger Grade 5-appropriate values rather than repeated low-complexity sums
- Equal-groups questions ask for the numerical total instead of only asking the learner to name the operation
- Worksheet history uses Melbourne local time with AEST/AEDT daylight-saving handling
- Duplicate-safe question generation with visual question guardrails
- Evidence-aware reduction of unnecessarily basic arithmetic while preserving purposeful review, consolidation and retrieval
- Immediate retry-first feedback with optional Math Mentor support
- Representation-specific Math Mentor guidance and different-number worked examples for interactive models
- Tablet-optimised worksheet and tutoring layouts
- Adaptive strand weighting and progressive difficulty
- Adaptive Daily Learning using current learning, consolidation, spaced review and challenge purposes
- Controlled skill progression requiring independent evidence before challenge increases
- Story Adventure over the same backend-authoritative adaptive learning, answer and evidence path as Daily Practice
- Parent Tests isolated from learner mastery and normal daily-learning completion
- Parent Learning Intelligence with plain-language summaries, independent versus supported success, evidence confidence, recommendations, misconception grouping and retention
- Home Assistant parent-learning integration with daily completion, learning focus, review due, support dependence, misconceptions, meaningful progress and weekly summary
- Persistent local Home Assistant service token and stable read-only learning endpoints
- Visual Mathematics and Interactive Maths Lab
- Parent Dashboard reliability safeguards for loading, retry and optional-section failure
- SQLite persistence and Home Assistant backup support

## Student mobile Home and navigation

v0.40.0 reorganises the student mobile experience around current learning action. Real iPhone use showed that the Home page had become too long and dashboard-like, with Story Adventure, large worksheet cards, technical skill evidence and the weekly calendar all competing for attention.

When unfinished learning exists, MathQuest now surfaces a **Continue Learning** card before historical content. An unfinished worksheet can be resumed directly, and completed work with skipped questions can be reopened for another attempt without inventing urgency. Completed history is reduced to three recent rows until the learner chooses to view more.

Story Adventure cards become horizontally swipeable on narrow screens so title, purpose and Start action stay visible without requiring a long stack of large cards. The underlying Story Adventure flow still creates a normal adaptive practice session first, then applies theme framing, so the mathematics remains selected by the same learning engine.

A student-only bottom navigation provides Home, Adventure, Worksheets and Progress destinations. It uses text and icons, has accessible current-state semantics, supports keyboard focus and reserves iPhone safe-area space so content is not covered. Parent Dashboard and Parent Tests remain outside student navigation.

The mobile MathQuest header is compressed when student navigation is present, reducing duplicated application identity beneath the Home Assistant ingress header while keeping sign-out accessible.

The weekly learning calendar now treats the previously compressed five-control iPhone layout as a responsive defect. Mobile shows readable previous week, date range, next week and Today controls, while the day content becomes a one-column weekly activity list. Tablet and desktop retain richer day navigation and the seven-day layout.

This release does not change worksheet generation, adaptive purpose selection, mastery calculations, learning evidence, Parent Tests or the v0.38 answer-feedback interaction.

## Session learning quality

v0.39.0 adds a final worksheet-quality pass after the existing adaptive generators. It checks the completed question set for educationally repetitive structures rather than only exact duplicate prompts.

For direct calculation, MathQuest distinguishes operation, operand digit lengths and regrouping demand. Recently answered Daily Practice and Story Adventure structures are also counted lightly so an overused structure can be replaced when a suitable alternative exists. This does not create a second learning model and does not remove deliberate review, consolidation or spaced retrieval.

After a final replacement, MathQuest refreshes the adaptive learning-purpose and evidence annotation so Parent Learning Intelligence and subsequent adaptive decisions describe the final question Sienna actually received. Parent Tests remain isolated and the existing one-question challenge limit remains intact.

## Number & Algebra quality corrective release

v0.38.1 reduced low-value direct arithmetic such as `121 + 22`, `50 + 58`, `14 − 4` and `8 + 8` in normal Number & Algebra worksheets. When a small direct addition or subtraction is selected, MathQuest upgrades it to a larger place-value calculation instead of letting a worksheet become dominated by easy fluency items.

Equal-groups modelling questions require an answer to the actual problem. For example, rather than asking which operation would find the total for 5 groups of 8, MathQuest asks how many items there are altogether. The learner still has to recognise multiplication, but that decision is part of solving the calculation.

Worksheet-history clock times are converted from stored UTC timestamps to `Australia/Melbourne`, including the correct daylight-saving offset for the date.

## iPad landscape feedback

v0.38.0 made the post-answer experience viewport-fixed rather than placing the result beneath the question card. Sienna can type an ordinary answer, press Enter, immediately see the result and supporting explanation, optionally record confidence, then press Enter again to continue.

Retryable incorrect answers preserve the existing retry-first learning model. The final answer is not revealed, Math Mentor remains optional, and choosing Retry returns to a cleared, focused answer field. The feedback dialog contains keyboard focus while open, provides explicit Correct answer or Incorrect answer text and iconography, and respects reduced-motion preferences.

The iPad landscape breakpoint also reduces unnecessary header, card, progress and sidebar space without shrinking the mathematical question into a desktop layout. Portrait, iPhone/mobile and desktop layouts retain responsive behaviour.

## Richer interactive mathematics

v0.37.0 extended the first-class interactive answer architecture introduced for whole-number number lines. Learners can interact directly with selected high-value mathematical representations:

- shade a requested number of equal parts on a fraction bar;
- locate a fraction between 0 and 1 using equal intervals;
- read a scaled ruler by selecting the correct mark;
- select a grid square using a column-and-row reference.

The frontend interaction does not decide correctness. The selected mathematical value or grid reference is submitted through the normal backend answer route so attempts, learning evidence, adaptive difficulty and misconception handling remain consistent.

Internal targets are deliberately left unlabelled where a visible label would reveal the answer.

## Mathematical reasoning

Learner sessions can include a controlled amount of structured reasoning alongside calculation practice. Question families include choosing a reasonable estimate, identifying true statements about perimeter, area and symmetry, and analysing a plausible regrouping or place-value mistake. Equal-groups modelling asks for the numerical result rather than an operation label.

This is not a separate reasoning engine. The questions use the same curriculum mappings, worksheet selection, answer validation and learning-evidence architecture as other MathQuest practice.

## Math Mentor

Math Mentor remains optional and retry-first behaviour is preserved. Interactive questions receive representation-specific support. Hints refer to equal parts, scale, landmarks or grid coordinates without revealing the active answer. Worked examples demonstrate the same method with different numbers or references.

## Interactive number lines and adaptive Number quality

The v0.36.0 whole-number number-line interaction remains available. Straightforward addition/subtraction is retained only when it offers useful practice, with low-complexity items upgraded to larger values for normal Number & Algebra work.

## Student login and session recovery

The login form defaults the editable username to `sienna`, leaves the password blank and focuses the password field. The existing 24-hour MathQuest token lifetime is retained. A JSON `401` from MathQuest authentication is treated as normal session expiry and returns the learner directly to the login screen. A non-JSON/plain-text `401` from Home Assistant ingress remains a separate recovery state and does not automatically clear the MathQuest token.

## Parent Dashboard and Home Assistant learning

Parent Dashboard reliability corrections remain in place. MathQuest remains authoritative for educational decisions and exposes compact read-only learning state through the existing Home Assistant endpoints. Daily Practice and Story Adventure count as daily learning only after meaningful completed learner work with answered questions. Parent Tests and abandoned no-evidence sessions do not count as daily learning.

## Adaptive Story Adventures

Story Adventure remains a presentation layer over MathQuest's adaptive learning engine. Compatible interactive questions use the same answer components, post-answer feedback and backend validation as Daily Practice. Story progression never counts as mastery. Correctness, attempts, support use, misconception evidence and retention continue to determine learning progress.

## Parent Learning Intelligence

The parent dashboard is designed to answer what is improving, what needs support, whether success is independent, what to practise next, why MathQuest recommends it, whether previously learned skills are being retained, and whether current difficulty is appropriate.

MathQuest avoids strong conclusions when there is insufficient evidence. Home Assistant preserves that behaviour and exposes states such as Building evidence and No review due rather than fabricating conclusions.
