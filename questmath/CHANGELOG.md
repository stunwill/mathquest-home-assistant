# MathQuest 0.34.0

- Rebuilt Story Adventure as a presentation layer over MathQuest's backend-authoritative adaptive learning engine instead of replacing selected questions with a separate story generator.
- Preserved each selected question's skill, prompt, answer, difficulty band, learning purpose and Visual Mathematics payload while adding adventure mission, stage, context and progress metadata.
- Added reusable mission stages covering Start, Challenge, Discovery, Harder Challenge, Final Challenge and Completion.
- Added 5, 10 and 15-minute Story Adventure entry points using the same timed adaptive session service as normal learner practice.
- Preserved prerequisite routing, consolidation, misconception repair, spaced retrieval, current practice and controlled challenge decisions inside Story Adventure.
- Kept incorrect answers retry-first, with Hint, Teach me, Worked example and Math Mentor remaining optional support rather than required gates.
- Kept Story Adventure answers in the existing learning-evidence and mastery architecture while ensuring adventure completion itself is not mastery evidence.
- Explicitly prevented Parent Tests from receiving Story Adventure framing or rewards and retained Parent Test isolation from learner evidence.
- Added lightweight responsive mission progress that remains suitable for tablet, mobile and Home Assistant ingress without new game or animation dependencies.
- Updated legacy Story Adventure compatibility behaviour so the old endpoint now uses the same v0.34 presentation-only architecture instead of exposing a second question-selection system.
- Added backend and frontend regression coverage for adaptive Story Adventure selection, evidence integrity, Parent Test isolation, session sizing, resume behaviour and mission progress.
- Preserved v0.33.0 Adaptive Daily Learning, v0.32.3 method-first Math Mentor, Visual Mathematics, worksheet history, Parent Learning Intelligence and all existing retry-first tutoring safeguards.

# MathQuest 0.33.0

- Added Adaptive Daily Learning so practice worksheets use accumulated learner evidence to label and balance current learning, consolidation, spaced review and limited challenge work.
- Added controlled progression states so difficulty does not increase from one or two correct answers and does not collapse after a single mistake.
- Made progression support-aware: high hint or Math Mentor usage keeps a skill in consolidation even when eventual accuracy is high.
- Integrated existing spaced-retrieval evidence so previously strong outcomes can return as Quick review questions.
- Used repeated misconception evidence to favour consolidation before harder progression.
- Added learner-facing learning-purpose metadata and parent-facing adaptive reasons without exposing internal mastery scores.
- Preserved post-transform question-family diversity and existing fraction-number-line visual repairs.
- Kept Parent Tests isolated from adaptive session recomposition.
- Centralised progression thresholds in the v0.33.0 adaptive engine and added regression tests for insufficient evidence, strong independent progression, support-heavy success, isolated mistakes, misconception-triggered consolidation and Parent Test isolation.
- Preserved v0.32.3 method-first Math Mentor, Grade 5 Algebra variety, Visual Mathematics, retry-first tutoring and Parent Learning Intelligence.

# MathQuest 0.32.3

- Expanded Grade 5 Math Mentor hints and worked examples so they teach the method, not just the operation or formula.
- Added written multiplication guidance that works from ones to tens and hundreds, explains carrying, and connects the written algorithm back to place-value partitioning.
- Added division guidance that partitions the dividend into convenient multiples, combines partial quotients and checks the result with multiplication as the inverse operation.
- Added Grade 5 decimal-to-fraction-out-of-100 questions and tutoring that explains tenths and hundredths and preserves denominator 100 when the wording requires it.
- Improved perimeter tutoring to establish perimeter as distance around the outside before introducing the rectangle shortcut formula and to retain linear units such as cm.
- Improved area tutoring to explain rows and columns of square units, distinguish area from perimeter and reinforce square units such as cm².
- Added dynamically generated worked examples that use different values from the active question while demonstrating the same method and complete example answer.
- Preserved progressive Hint 1 concept, Hint 2 first-step and Hint 3 method behaviour without revealing the active answer where practical.
- Added regression tests covering method-first multiplication, partition division, inverse checks, hundredths fractions, perimeter/area concepts, units, different-number examples and Grade 5 difficulty boundaries.
- Preserved v0.32.2 Algebra variety, adaptive difficulty, retry-first Math Mentor behaviour, worksheet quality, visual mathematics, Story Adventures and parent reporting.

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
- Preserved denominator-accurate fraction-number-line repair and existing visual mathematics annotations after quality transformations.
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
