# MathQuest 0.33.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing daily adaptive mathematics practice, worksheet navigation, progress tracking and a parent dashboard aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Student and parent authentication
- Student dashboard, streak, XP, levels, calendar and badges
- Multiple generated worksheets per day
- Save and exit, resume, skip-for-now and skipped-question round
- Exact worksheet resume, completed worksheet review and weekly learning history
- Duplicate-safe question generation with visual question guardrails
- Question overview and navigation status panel
- Immediate retry-first feedback with optional Math Mentor support
- Tablet-optimised worksheet and tutoring layouts for portrait and landscape use
- Adaptive strand weighting and progressive difficulty
- Adaptive daily session composition using current learning, consolidation, spaced review and limited challenge purposes
- Controlled skill progression that requires enough independent evidence before challenge increases
- Support-aware consolidation so eventual success after substantial tutoring does not trigger premature progression
- Expanded Grade 5 Algebra variety with numerical patterns, symbolic unknowns, substitution, mystery-number reasoning, contextual unknown starts and reverse multiplication
- New Algebra structures supplement the existing equation, multiplication and division fact-family generators
- Structural-family diversity prevents a run of effectively identical Algebra equations with only different values
- Method-first Grade 5 Math Mentor guidance for written multiplication, partition division, decimal fractions out of 100, perimeter and area
- Different-number worked examples that show the complete method and reasoning without solving the active question
- More instructional-level Number practice with hundreds, regrouping and decomposition when learner evidence supports it
- Purposeful retrieval limits so very simple arithmetic remains available without dominating normal sessions
- Worked examples aligned to the current operation, question family or mathematical representation using different values
- Parent Learning Intelligence with plain-language learning summaries
- Independent versus supported success and evidence confidence at skill level
- Secure, Developing, Needs Support, Review Due and Not Enough Evidence mastery states
- Prioritised practice recommendations with evidence-based reasons
- Repeated misconception grouping and prerequisite-aware explanations
- Retention and spaced-review visibility
- Difficulty calibration that considers support dependency as well as accuracy
- 7, 30 and 90-day progress comparisons
- Parent curriculum tracker, support flags and incorrect-answer review
- CSV and PDF reports
- SQLite backup and restore API
- Home Assistant ingress and persistent `/data` storage
- Installation-specific JWT signing and failed-login throttling
- Number & Algebra Focus quests for targeted fact recall and equation practice
- Contextual strategy cards, written subtraction regrouping and retention review indicators
- Three-stage guided tutoring across arithmetic, fractions, measurement, grids, time, data and equations
- Distinct nudge, strategy and worked-next-step hint stages
- Question-specific Teach me mini-lessons using the current problem structure without revealing the final answer
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
- Persistent Home Assistant service authentication and dashboard-ready category, outcome and recommendation metrics
- Parent-only test worksheets with isolated test evidence, question and overall notes, feedback status and addressed-release traceability
- Number and Algebra interventions that select the weakest prerequisite, teach with linked models and report independent understanding separately

## Adaptive daily learning

v0.33.0 uses the learning evidence already collected by MathQuest to explain and shape the purpose of daily worksheet questions. Questions can be marked as current learning, consolidation, quick review or a limited challenge. Progression is conservative: a learner needs enough repeated independent success before MathQuest increases challenge, while high support dependency or repeated misconception evidence keeps a skill in consolidation. Parent Tests remain excluded from this adaptive composition layer.

## Grade 5 method-first Math Mentor

v0.32.3 improves Hints and Worked Examples so they teach a Grade 5 method rather than merely naming an operation or formula. Written multiplication works from the ones column through tens and hundreds and connects carrying to place-value partitioning. Division uses convenient partitions and an inverse multiplication check. Decimal-to-fraction questions explain tenths and hundredths and retain denominator 100 when the question asks for “out of 100”. Perimeter is introduced as distance around the outside before the rectangle shortcut, while area is explained as counting rows and columns of square units and explicitly uses cm² rather than cm.

## Parent Learning Intelligence

The parent dashboard is designed to answer quickly what is improving, what needs support, whether success is independent, what to practise next, why MathQuest recommends it, whether previously learned skills are being retained, and whether current difficulty is appropriate.

MathQuest avoids strong conclusions when there is insufficient evidence. Parent tests remain excluded from learner mastery, misconceptions, adaptive difficulty, spaced retrieval and recommendations.
