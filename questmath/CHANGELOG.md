## v0.47.5 - Parent Dashboard Crash Fix

This focused corrective release publishes the Parent Dashboard resilience fix already merged in PR #81 as an installable Home Assistant add-on update.

- Prevent Parent Learning Insight from crashing when a legacy or partial insight payload omits the `outcomes` collection.
- Render a clear no-evidence state instead of blanking the Parent Dashboard.
- Add regression coverage for the legacy payload shape that reproduced the production failure.
- Preserve Best Next Step, targeted learning session behaviour, skill-sensitive progression, worksheets, adaptive progression, diagnostics, Math Mentor and stored learner evidence unchanged.

## v0.47.4 - Return to Answer After Support

The latest installed v0.47.3 production recording confirms the keyboard-first answer layout, compact quest header, learner-safe worksheet map, mathematical feedback and active-work Home hierarchy. It also shows a typed-answer worksheet scrolled into Visual idea and Math Mentor while the software keyboard is open.

- Restore the question and answer group on actual answer focus or re-tap after support reading, using the visual viewport offset and height. Do not scroll on every render or while support is being read.
- Keep support disclosure unchanged because the expanded Visual idea is a small recommendation, the model is modal, and Scratchpad/Math Mentor content should not be automatically discarded or collapsed.
- Preserve Best Next Step, targeted learning session, skill-sensitive progression and diagnostic evidence architecture without backend learning changes.
- Physical iPhone, iPad and Home Assistant ingress validation remains pending.
