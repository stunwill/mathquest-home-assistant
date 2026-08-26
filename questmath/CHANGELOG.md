# MathQuest 0.32.2

- Expanded Grade 5 Algebra question variety with increasing/decreasing patterns, symbolic addition and subtraction unknowns, addition and multiplication substitution, mystery-number problems, contextual unknown-start problems and reverse multiplication/doubling.
- Mixed the new structures into the existing Algebra generator rather than replacing established equation, multiplication and division fact-family questions.
- Added structural diversity identifiers for each new Algebra question type so different generated values do not disguise repetitive question structures within the same worksheet.
- Added question-specific hints, strategy cards and worked examples that explain inverse operations, substitution and reverse reasoning without revealing the assessed answer.
- Kept Grade 5 bridging addition/subtraction unknown and substitution practice on the existing scaffold mapping, while mapping Level 5 multiplication/division reasoning to verified Victorian Curriculum Version 2.0 outcomes and avoiding invented curriculum codes.
- Added large-sample generation tests for answer correctness, whole-number constraints, difficulty boundaries, variation, structural diversity and Math Mentor compatibility.
- Preserved v0.32.1 worksheet quality, adaptive difficulty, scoring, visual mathematics, Story Adventures, parent reporting and retry-first tutoring behaviour.

# MathQuest 0.32.1

- Preserved immediate wrong-answer retry so Math Mentor, hints and worked examples remain optional support rather than required actions.
- Tightened worked-example alignment for Probability, fraction number lines, Measurement, Space and Statistics while retaining existing operation-specific arithmetic examples.
- Added explicit worked-example alignment metadata so regression tests can verify the topic, skill and question family used for tutoring.
- Added evidence-driven retrieval budgeting so very simple arithmetic remains available for confidence, prerequisite checks and spaced retrieval without dominating a normal worksheet once recent learner evidence supports progression.
- Added retrieval, instructional and challenge difficulty-band metadata to generated questions.
- Re-applied structural question-family diversity after the v0.31 adaptive difficulty transformations so later rewrites cannot reintroduce repetitive question families.
- Preserved denominator-accurate fraction number-line repair and existing visual mathematics annotations after quality transformations.
- Added backend regression coverage for trivial-question classification, hundreds-level progression and question-family-specific worked examples.
- Updated release metadata, runtime entrypoint, version validation and documentation for v0.32.1.

# MathQuest 0.32.0

- Redesigned the Parent Dashboard around learning decisions instead of raw administrative metrics.
- Added plain-language parent learning summaries generated from learner evidence.
- Added skill-level mastery states: Secure, Developing, Needs Support, Review Due and Not Enough Evidence.
- Distinguished first-attempt, eventual, independent and supported success so tutoring-assisted correctness does not overstate mastery.
- Added evidence-confidence labels based on the volume of recent attempts.
- Added prioritised practice recommendations with evidence-based reasons and clear High Priority, Practise, Review and Keep Going categories.
- Added recurring misconception grouping that requires repeated evidence before surfacing a parent-facing concern.
- Added prerequisite visibility, spaced-review status and retention reporting.
- Added difficulty calibration that considers independent accuracy, eventual accuracy and support dependency together.
- Added 7, 30 and 90-day progress comparisons and conservative handling for insufficient sample sizes.
- Updated curriculum wording to describe MathQuest evidence against the Victorian Curriculum Level 5 pathway rather than implying formal achievement certification.
- Added responsive parent-learning cards for desktop, tablet, mobile and Home Assistant ingress layouts.
- Preserved Parent Test isolation from learner XP, streak, mastery, misconceptions, recommendations, adaptive difficulty and retention evidence.
- Hardened frontend TypeScript configuration with explicit Node and Vite types while retaining Bundler module resolution.
- Updated release metadata, backend runtime entrypoint and documentation for v0.32.0 Parent Learning Intelligence.

# MathQuest 0.31.0

- Optimised the live worksheet layout for tablet portrait and landscape use, including more compact tutoring content, improved touch targets and better visibility of primary worksheet actions.
- Increased instructional-level Number practice for learners with sufficient evidence, favouring purposeful hundreds-based addition and subtraction with regrouping, decomposition and place-value reasoning while retaining occasional easier retrieval items.
- Added structured question context for Math Mentor, including operation, operands, skill, question family and expected strategy metadata.
- Redesigned **Teach me** as a question-specific mini-lesson that uses the actual problem structure and operands without revealing the final assessed answer.
- Split tutoring support into clearer roles: Hint provides the smallest useful nudge, Why explains the concept, Teach me provides a mini-lesson, Worked example uses different values, and Show worked next step exposes one additional current-question step.
- Made three-stage hints materially progressive: conceptual nudge, problem-specific strategy and worked next step.
- Improved mathematical formatting for tutoring steps so partitioned values and place-value working are visually distinct from prose.
- Preserved retry-first answer entry, keyboard autofocus, Math Mentor optionality, v0.30 Visual Mathematics and all v0.30.1 worksheet-quality safeguards.
- Added regression coverage for hundreds-based arithmetic, question-specific tutoring, distinct hint levels, answer protection, worked-example alignment and tablet-oriented presentation behaviour.

# MathQuest 0.30.1

- Changed worksheet completion **Strongest** and **Practise next** recommendations to use persisted learner-wide mastery evidence instead of only the category in the just-completed worksheet.
- Added neutral completion-summary wording when there is not enough cross-category evidence for a meaningful comparison.
- Strengthened duplicate prevention with question-family detection so numeric variants of the same underlying template are treated as repeats.
- Added worksheet-level family diversity that avoids consecutive and repeated families when an appropriate alternative is available, while retaining a safe fallback for constrained question pools.
- Corrected fraction number-line visuals so the denominator controls the number of equal intervals, including ten equal intervals for 8/10.
- Prevented fractional number-line tick values from being rounded into misleading integer labels such as 0, 0, 1.
- Removed unrelated number-line teaching prompts from Probability questions when no compatible interactive visual is available.
- Added backend and frontend regression coverage for learner-history summaries, semantic question families, fraction number-line subdivisions and Probability visual relevance.
- Preserved v0.30.0 Visual Mathematics, Math Mentor, retry-first keyboard flow and all v0.29.1 corrective safeguards.
