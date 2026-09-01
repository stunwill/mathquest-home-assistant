# MathQuest 0.37.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, interactive mathematical models, reasoning, worksheet navigation, progress tracking and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Student and parent authentication, with `sienna` prefilled for the normal student login flow
- Automatic recovery from expired MathQuest sessions back to the login screen while keeping Home Assistant ingress failures distinct
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- First-class interactive whole-number number lines, fraction bars, fraction number lines, scaled rulers and grid-reference selection
- Structured Grade 5 reasoning including operation choice, reasonableness, conceptual comparison and find-the-mistake questions
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

## Richer interactive mathematics

v0.37.0 extends the first-class interactive answer architecture introduced for whole-number number lines. Learners can now interact directly with selected high-value mathematical representations:

- shade a requested number of equal parts on a fraction bar;
- locate a fraction between 0 and 1 using equal intervals;
- read a scaled ruler by selecting the correct mark;
- select a grid square using a column-and-row reference.

The frontend interaction does not decide correctness. The selected mathematical value or grid reference is submitted through the normal backend answer route so attempts, learning evidence, adaptive difficulty and misconception handling remain consistent.

Internal targets are deliberately left unlabelled where a visible label would reveal the answer.

## Mathematical reasoning

Learner sessions can now include a controlled amount of structured reasoning alongside calculation practice. Question families include selecting an appropriate operation, choosing a reasonable estimate, identifying true statements about perimeter, area and symmetry, and analysing a plausible regrouping or place-value mistake.

This is not a separate reasoning engine. The questions use the same curriculum mappings, worksheet selection, answer validation and learning-evidence architecture as other MathQuest practice.

## Math Mentor

Math Mentor remains optional and retry-first behaviour is preserved. New interactive questions receive representation-specific support. Hints refer to equal parts, scale, landmarks or grid coordinates without revealing the active answer. Worked examples demonstrate the same method with different numbers or references.

## Interactive number lines and adaptive Number quality

The v0.36.0 whole-number number-line interaction remains available. Straightforward two-digit additions can still be reduced when learner evidence supports progression, while purposeful review, consolidation and retrieval remain available.

## Student login and session recovery

The login form defaults the editable username to `sienna`, leaves the password blank and focuses the password field. The existing 24-hour MathQuest token lifetime is retained. A JSON `401` from MathQuest authentication is treated as normal session expiry and returns the learner directly to the login screen. A non-JSON/plain-text `401` from Home Assistant ingress remains a separate recovery state and does not automatically clear the MathQuest token.

## Parent Dashboard and Home Assistant learning

Parent Dashboard reliability corrections remain in place. MathQuest remains authoritative for educational decisions and exposes compact read-only learning state through the existing Home Assistant endpoints. Daily Practice and Story Adventure count as daily learning only after meaningful completed learner work with answered questions. Parent Tests and abandoned no-evidence sessions do not count as daily learning.

## Adaptive Story Adventures

Story Adventure remains a presentation layer over MathQuest's adaptive learning engine. Compatible interactive questions use the same answer components and backend validation as Daily Practice. Story progression never counts as mastery. Correctness, attempts, support use, misconception evidence and retention continue to determine learning progress.

## Parent Learning Intelligence

The parent dashboard is designed to answer what is improving, what needs support, whether success is independent, what to practise next, why MathQuest recommends it, whether previously learned skills are being retained, and whether current difficulty is appropriate.

MathQuest avoids strong conclusions when there is insufficient evidence. Home Assistant preserves that behaviour and exposes states such as Building evidence and No review due rather than fabricating conclusions.
