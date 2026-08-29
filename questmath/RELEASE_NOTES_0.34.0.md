# MathQuest 0.34.0 Release Notes

## Story Adventure Expansion and Purposeful Daily Learning

MathQuest 0.34.0 makes Story Adventure a presentation layer over the same adaptive learning system used by Daily Practice.

Previously, the Story Adventure flow could create a normal worksheet and then replace its questions with a separate theme-specific generator. That meant the adaptive decisions introduced in recent releases could be lost after the worksheet had already been planned.

This release changes the architecture to:

Learner evidence → adaptive learning plan → selected maths question → Story Adventure presentation.

## What changes for the learner

- Story Adventure now preserves the maths selected by MathQuest's adaptive learning engine.
- The learner can choose a 5, 10 or 15-minute Story Adventure.
- Adventures use lightweight stages: Start, Challenge, Discovery, Harder Challenge, Final Challenge and Completion.
- Mission progress shows the current stage, overall question progress and the learning purpose of the current challenge.
- Adventure themes provide a setting, objective and ending without forcing every mathematical question into an awkward word problem.
- Incorrect answers remain retry-first. The learner can immediately try another answer without being forced to open a hint or Math Mentor.
- Hint, Teach me, Worked example and Math Mentor remain optional supports.
- Existing Visual Mathematics continues to appear where the selected question benefits from it.
- Existing XP and completion feedback remain lightweight reinforcement. Story progress itself is not treated as mathematical mastery.

## Adaptive learning integrity

Story Adventure retains the selected question's:

- curriculum skill;
- difficulty;
- learning purpose;
- prerequisite routing;
- misconception-repair intent;
- spaced-review intent;
- progression or challenge intent;
- Visual Mathematics payload.

Adventure answers continue to contribute to the existing learning evidence model. First-attempt independence, eventual success, support use, repeated errors, misconceptions and retention remain the evidence used to determine progress.

Completing an adventure does not directly increase mastery.

## Parent Tests

Parent Tests remain independent assessments. They cannot be converted into Story Adventures and do not receive story framing or adventure rewards. Their existing evidence-isolation rules remain unchanged.

## Resume and recovery

Story Adventure uses the existing worksheet identity and persistence model. Applying adventure presentation does not create a replacement session, and reopening or refreshing an unfinished adventure continues through the same worksheet state.

## Responsive and performance behaviour

The Story Adventure interface uses existing React components and lightweight CSS. No game engine, animation framework or large image dependency has been added.

Progress and session controls are designed to adapt to desktop, tablet, mobile and Home Assistant ingress layouts without introducing fixed-width adventure screens.

## Validation

GitHub Actions validation for the release branch completed successfully with:

- Backend: 210 tests passed.
- Frontend: 18 test files passed, 61 tests passed.
- Frontend dependency install: `npm ci` passed using the synchronized committed lockfile.
- TypeScript and production build: `tsc && vite build --base=./` passed.
- Vite production build: 1,598 modules transformed and build completed successfully.
- Release metadata and version consistency validation passed.

No real browser, iPad, mobile-device or Home Assistant ingress manual validation is claimed as part of these automated results.

## Roadmap

The roadmap has been reconciled so Story Adventure Expansion is the 0.34.0 release. The likely next focus returns to deeper Home Assistant parent integration and further learner-experience refinements, with the exact semantic version to be determined from the repository state when that work begins.
