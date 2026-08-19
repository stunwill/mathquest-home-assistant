# MathQuest v0.29.1

Corrective release following the August 2026 worksheet review.

## Fixes

- Grid-reference questions now receive a labelled grid visual with the target square highlighted before the worksheet is shown.
- Keyboard entry is smoother: text and number answer fields are focused automatically whenever a new question becomes active, without stealing focus from open modals.
- A final worksheet quality pass now detects repeated question concepts after adaptive, story and difficulty transformations and regenerates duplicates before the worksheet is returned.
- Grouped word problems now repeat the unit being removed or counted when wording could otherwise be ambiguous. The reviewed meal-pack question now explicitly says that meal portions are used and asks how many meal portions remain.

## Regression coverage

- Grid visual payload generation for `grid_references`.
- Explicit unit wording for grouped meal-portion questions.
- Duplicate-concept replacement after final worksheet transformations.
- Browser autofocus behaviour for newly rendered answer fields and modal focus protection.

## Compatibility

This release is intentionally corrective and builds directly on v0.29.0 Learning Intelligence. It does not change the learning model, scoring rules, Math Mentor behaviour, stored worksheet schema, or user data format.

Closes #45.
