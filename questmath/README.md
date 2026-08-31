# MathQuest 0.36.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Student and parent authentication, with `sienna` prefilled for the normal student login flow
- Automatic recovery from expired MathQuest sessions back to the login screen while keeping Home Assistant ingress failures distinct
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Interactive number-line location questions answered directly on the visual number line
- Duplicate-safe question generation with visual question guardrails
- Evidence-aware reduction of unnecessarily basic two-digit arithmetic while preserving purposeful review, consolidation and retrieval
- Immediate retry-first feedback with optional Math Mentor support
- Tablet-optimised worksheet and tutoring layouts
- Adaptive strand weighting and progressive difficulty
- Adaptive Daily Learning using current learning, consolidation, spaced review and challenge purposes
- Controlled skill progression requiring independent evidence before challenge increases
- Story Adventure over the same backend-authoritative adaptive learning plan as Daily Practice
- Story Adventure evidence recorded through the same worksheet, attempt, misconception and mastery architecture
- Parent Tests isolated from learner mastery and normal daily-learning completion
- Parent Learning Intelligence with plain-language summaries, independent versus supported success, evidence confidence, recommendations, misconception grouping and retention
- Home Assistant parent-learning integration with daily completion, learning focus, review due, support dependence, misconceptions, meaningful progress and weekly summary
- Persistent local Home Assistant service token and stable read-only learning endpoints
- Method-first Math Mentor, aligned worked examples, Visual Mathematics and Interactive Maths Lab
- Parent Dashboard reliability safeguards for loading, retry and optional-section failure
- SQLite persistence and Home Assistant backup support

## Interactive number lines

Number-line location questions now use a first-class `number_line` answer type. The learner taps or clicks a tick on the number line itself, and the selected numeric position is submitted through the normal backend-authoritative answer route. The requested internal value is intentionally not labelled on the line, so the question assesses scale interpretation rather than recognition of an answer button.

## Adaptive Number and Algebra quality

v0.36.0 extends the existing worksheet-quality safeguards beyond the previous `≤12` trivial-arithmetic check. Straightforward two-digit additions such as `20 + 28` are now recognised as low-complexity practice and are suppressed once learner readiness supports progression, unless the question is deliberately present for review, consolidation or retrieval. Foundational practice remains available when learning evidence gives it a purpose.

## Student login and session recovery

The login form now defaults the editable username to `sienna`, leaves the password blank and focuses the password field. The existing 24-hour MathQuest token lifetime is retained. A JSON `401` from MathQuest authentication is treated as normal session expiry and returns the learner directly to the login screen. A non-JSON/plain-text `401` from Home Assistant ingress remains a separate recovery state and does not automatically clear the MathQuest token.

## Parent Dashboard reliability

The v0.35.1 Parent Learning Intelligence and Parent Dashboard reliability corrections remain in place. Required bootstrap failures are visible and retryable, while backups and optional learning-intelligence data degrade independently.

## Home Assistant parent learning

MathQuest remains authoritative for educational decisions and exposes compact read-only learning state through the existing Home Assistant endpoints. Daily Practice and Story Adventure count as daily learning only after meaningful completed learner work with answered questions. Parent Tests and abandoned no-evidence sessions do not count as daily learning.

## Adaptive Story Adventures

Story Adventure remains a presentation layer over MathQuest's adaptive learning engine. Story progression never counts as mastery. Correctness, attempts, support use, misconception evidence and retention continue to determine learning progress through the same evidence model used by Daily Practice.

## Adaptive daily learning

Questions can be marked as current learning, consolidation, quick review or a limited challenge. Progression is conservative: the learner needs repeated independent success before MathQuest increases challenge, while high support dependency or repeated misconception evidence keeps a skill in consolidation. Parent Tests remain excluded.

## Parent Learning Intelligence

The parent dashboard is designed to answer what is improving, what needs support, whether success is independent, what to practise next, why MathQuest recommends it, whether previously learned skills are being retained, and whether current difficulty is appropriate.

MathQuest avoids strong conclusions when there is insufficient evidence. Home Assistant preserves that behaviour and exposes states such as Building evidence and No review due rather than fabricating conclusions.
