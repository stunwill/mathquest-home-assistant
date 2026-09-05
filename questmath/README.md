# MathQuest 0.42.0

**Sienna’s daily adventure in maths.**

MathQuest is a local Home Assistant app providing adaptive mathematics practice, interactive mathematical models, reasoning, worksheet navigation, learner guidance and parent reporting aligned to a Victorian Curriculum Level 5 pathway while adapting across Levels 2–6 from diagnostic evidence.

## Included

- Real student destinations for Home, Adventure, Worksheets and Progress rather than scroll-to-section navigation
- Concise student Home focused on current learning and the Best Next Step
- Ready to Start for untouched worksheets and Continue Learning only once work has genuinely begun
- Student Learning Progress derived from existing mastery, adaptive progression, support and spaced-retrieval evidence
- Learner-readable states including Practising, Building confidence, Getting stronger, Ready for a challenge and Ready to review presentation
- Evidence-grounded Best Next Step explanations without raw mastery percentages, curriculum codes or adaptive mode labels
- Learner-safe Extra Practice presentation while retaining the existing intervention/support session backend
- Story Adventure owned by the Adventure destination and preserved on the same adaptive session/evidence path
- Worksheet history owned by Worksheets and Weekly Activity owned by Progress
- iPhone safe-area navigation and compact Home Assistant ingress header treatment
- iPad 10th-generation landscape worksheet optimisation with immediate post-answer feedback and keyboard-first continuation/retry
- Multiple generated worksheets per day with save, exact resume, skip-for-now and skipped-question recovery
- First-class interactive whole-number number lines, fraction bars, fraction number lines, scaled rulers and grid-reference selection
- Grade 5 reasoning including reasonableness, conceptual comparison and find-the-mistake questions
- Session-level learning quality covering near-duplicate structures, recent exposure and accidental low-complexity work
- Adaptive Daily Learning using current learning, consolidation, spaced review and controlled challenge purposes
- Math Mentor, hints, worked examples, Visual Mathematics and Interactive Maths Lab
- Parent Learning Intelligence and Parent Tests isolated from ordinary learner evidence
- Home Assistant parent-learning integration and local SQLite persistence

## Student destinations and learning guidance

v0.42.0 completes the navigation direction started in v0.40.0 and informed by real iPhone use of v0.41.0. Home, Adventure, Worksheets and Progress are now distinct student destinations instead of anchor targets inside one long dashboard.

**Home** is the launchpad. **Adventure** owns the full Story Adventure selector. **Worksheets** owns resume, review and history. **Progress** owns learner-state detail and Weekly Activity. Student Home no longer gives streak, raw accuracy, total question volume, highest level or the technical Skill Map the same prominence as the next learning action.

Untouched worksheets are presented as **Ready to Start**. Once answers exist, they become **Continue Learning**. Existing worksheet and learning evidence is preserved; v0.42.0 does not invent automatic archival rules where the current data cannot reliably prove abandonment.

The learner sees **Extra Practice** rather than intervention and **Ready to review** rather than review due. Raw independent/support percentages are no longer displayed in student Progress or Extra Practice. The underlying v0.41 learning-state derivation and all adaptive thresholds remain unchanged.

Progress groups skills under a single state explanation and hides zero-value state summaries. Parent Learning Intelligence remains the detailed evidence surface for technical analytics.

## Learning continuity

v0.42.0 is a presentation and information-architecture release. It does not create a second mastery model, change progression thresholds, alter prerequisite routing, change spaced-retrieval scheduling or replace Story Adventure question selection. The existing adaptive engine remains authoritative.

Math Mentor, hints, worked examples, retry-first behaviour, worksheet scoring/completion, confidence evidence, Parent Test isolation and Home Assistant integration remain part of the release contract.

## iPad landscape feedback

The v0.38 worksheet flow remains `Answer → Immediate feedback → Understand → Reflect → Continue`. Typed answers retain keyboard-first submission and continuation/retry, and the iPad 10th-generation landscape layout remains protected by automated regression coverage and manual acceptance requirements.

## Parent Dashboard and Home Assistant learning

Parent Dashboard remains the detailed evidence and administration surface. MathQuest stays authoritative for educational decisions and exposes compact read-only learning state through the existing Home Assistant endpoints. Parent Tests remain isolated from learner mastery and ordinary daily-learning completion.
