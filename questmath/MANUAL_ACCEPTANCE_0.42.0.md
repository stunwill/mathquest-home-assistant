# MathQuest v0.42.0 Manual Acceptance

Physical-device acceptance must remain unchecked until performed on actual hardware. Automated responsive tests do not satisfy this checklist.

## iPhone through Home Assistant ingress

- [ ] Home opens without horizontal overflow and shows a concise launchpad rather than the complete Adventure, Worksheets and Progress views.
- [ ] Untouched current work is labelled Ready to Start and does not claim progress is saved.
- [ ] A genuinely started worksheet is labelled Continue Learning and resumes exactly.
- [ ] Best Next Step is readable without mastery percentages, curriculum codes or adaptive mode labels.
- [ ] Extra Practice contains no student-facing intervention terminology or raw independent/support percentages.
- [ ] Adventure opens as a distinct destination and the complete Story Adventure selector is usable by touch.
- [ ] Worksheets opens as a distinct destination and current/completed worksheet states and actions are easy to scan.
- [ ] Progress opens as a distinct destination and shows grouped learner states plus Weekly Activity.
- [ ] Ready to review language is used in student-facing Progress and recommendation summaries.
- [ ] Bottom navigation remains visible, respects the iPhone safe area and identifies the active destination without relying on colour alone.
- [ ] Switching destinations returns predictably to the top and does not produce a long anchor-scroll effect.
- [ ] Home Assistant plus MathQuest header space remains usable and sign-out is accessible.
- [ ] Weekly Activity previous week, date range, next week and Today controls remain readable.

## iPad 10th generation landscape through Home Assistant ingress

- [ ] Home, Adventure, Worksheets and Progress destinations are usable in landscape without horizontal overflow.
- [ ] Student navigation remains keyboard-focusable with visible focus.
- [ ] Starting an untouched worksheet uses Ready to Start semantics.
- [ ] Typed answer field receives focus and Enter submits the answer.
- [ ] Post-answer feedback remains viewport-appropriate and Enter continues or retries as intended.
- [ ] Retry returns to a cleared, focused answer input.
- [ ] Hint, Why, Teach me and Worked example remain available and question-specific.
- [ ] Math Mentor remains optional unless the learning flow explicitly requires support.
- [ ] Interactive number lines, fractions, rulers and grids remain touch/mouse usable.
- [ ] Story Adventure questions use the same worksheet answer and feedback flow.
- [ ] Skipped-question recovery and worksheet completion continue to work.

## Desktop

- [ ] Home, Adventure, Worksheets and Progress destination controls are usable by mouse and keyboard.
- [ ] Destination content remains readable without mobile-only layout assumptions.
- [ ] Parent Dashboard and Parent Tests remain outside student navigation and function normally.

## Release validation evidence

- [ ] Complete backend test suite passes.
- [ ] Complete frontend test suite passes.
- [ ] Production frontend build passes.
- [ ] Version/DevHub metadata validation passes.
- [ ] aarch64 add-on image builds and starts successfully with health reporting v0.42.0.
