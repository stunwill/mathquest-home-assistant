# MathQuest v0.40.0 Manual Acceptance

These checks require a real browser/device session. Do not mark them complete from unit tests, CSS inspection, emulation or CI alone.

## iPhone portrait

- [ ] Home loads without horizontal overflow.
- [ ] MathQuest header does not waste excessive vertical space beneath Home Assistant ingress.
- [ ] Primary learning action is visible quickly after load.
- [ ] Unfinished learning appears prominently as Continue Learning when relevant.
- [ ] A worksheet with skipped questions can be resumed for another attempt.
- [ ] Story Adventure selection is compact, readable and swipeable.
- [ ] Story Adventure cards do not become a long stack of oversized panels.
- [ ] Recent worksheet history is limited by default and does not dominate the Home feed.
- [ ] View all worksheets expands older history and Show recent only collapses it again.
- [ ] Student bottom navigation is visible, readable and usable.
- [ ] Home, Adventure, Worksheets and Progress destinations move to the expected student sections.
- [ ] Student navigation contains no Parent Dashboard or Parent Test entry.
- [ ] Bottom navigation respects the iPhone safe area and does not cover page content.
- [ ] Calendar controls remain readable with no compressed five-column layout.
- [ ] Calendar date range does not collapse into a vertical character stack.
- [ ] Previous week works.
- [ ] Next week works when a later week is available.
- [ ] Today returns to the current week.
- [ ] Weekly activity is readable without horizontal scrolling of the page.
- [ ] Sign out remains accessible.
- [ ] Rotating portrait to landscape and back does not corrupt worksheet or navigation state.
- [ ] Browser/Home Assistant chrome changes do not cover the bottom navigation or current action.

## Narrower iPhone portrait

- [ ] No horizontal page overflow at the narrower portrait width.
- [ ] Header controls remain usable and do not collide.
- [ ] Adventure selector still exposes the next card without clipping primary content.
- [ ] Bottom navigation labels remain legible.
- [ ] Calendar navigation remains usable with adequate touch targets.

## iPhone landscape

- [ ] Student navigation does not cover critical content.
- [ ] Page does not create nested horizontal scrolling.
- [ ] Header and primary action remain usable with reduced vertical height.

## iPad 10th generation landscape

- [ ] Existing worksheet layout remains correct.
- [ ] Physical keyboard Enter submits typed answers.
- [ ] Feedback modal remains viewport-fixed and readable.
- [ ] Enter continues after terminal feedback.
- [ ] Retry clears the previous response and restores input focus.
- [ ] Rapid Enter protection still prevents duplicate submit/skip behaviour.
- [ ] Math Mentor remains optional.
- [ ] Story Adventure feedback remains on the shared worksheet path.
- [ ] Home remains usable and does not show the phone bottom navigation at the landscape breakpoint.
- [ ] Calendar retains richer tablet controls without overflow.

## iPad 10th generation portrait

- [ ] Home remains appropriately responsive.
- [ ] Continue Learning remains prominent when relevant.
- [ ] Story Adventure cards remain usable.
- [ ] Calendar remains readable and navigable.
- [ ] No horizontal page overflow.

## Desktop

- [ ] No desktop regression in Student Home.
- [ ] Phone bottom navigation is not rendered visually on desktop.
- [ ] Richer calendar controls remain usable.
- [ ] Seven-day calendar presentation remains available.
- [ ] Worksheet history review remains available.
- [ ] Parent Dashboard remains separate and unchanged in scope.

## Accessibility

- [ ] Student navigation is understandable with text labels and icons.
- [ ] Keyboard focus is visible on student navigation, calendar and history controls.
- [ ] Touch targets are comfortable on iPhone.
- [ ] Continue Learning can be understood without colour alone.
- [ ] Calendar controls have understandable accessible names.
- [ ] VoiceOver reading order is logical for current action, Adventure, recent work and progress.
- [ ] Reduced-motion device preference avoids unnecessary transitions/animations.

## Recording-specific confirmation

Recheck the exact problems demonstrated in the 5 September 2026 iPhone recording:

- [ ] stacked Home Assistant and MathQuest headers now leave materially more useful first-viewport space;
- [ ] Story Adventure no longer requires scrolling through multiple oversized vertical cards;
- [ ] completed worksheet history no longer dominates many screen heights;
- [ ] technical progress does not visually outrank current learning;
- [ ] the weekly calendar no longer compresses five navigation columns into an unreadable control row.

## Sign-off

Device(s) used: ______________________________________

Home Assistant version/build: ________________________

MathQuest build/commit: ______________________________

Tester: _____________________________________________

Date: _______________________________________________

Notes: ______________________________________________
