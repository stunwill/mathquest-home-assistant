# MathQuest 0.30.0: Visual Mathematics

MathQuest v0.30.0 turns the existing question visuals, Interactive Maths Lab, Math Mentor and v0.29 learning evidence into a more coherent visual teaching system.

## Highlights

- Fraction comparison now uses reusable equal-whole models with aligned bars, denominator partitions and numerator shading.
- The Interactive Maths Lab adds synchronised fraction bars, fraction number lines and equivalent-fraction representations.
- Worksheet visuals and Maths Lab tools share reusable fraction, number-line, array, place-value and measurement components.
- Suitable questions expose multiple valid solution strategies one at a time through **Show another way**.
- Visual recommendations explain how a model connects to the calculation instead of giving generic diagram advice.
- Repeated misconception evidence can recommend optional visual support without opening the Maths Lab automatically.
- Parent-test payloads suppress the new teaching strategies and recommendations to preserve assessment integrity.
- Teaching examples use different values from the assessed question and do not fill the assessed answer field.
- New visual controls include accessible mathematical labels, keyboard-operable inputs and reduced-motion-safe styling.
- v0.29.1 grid visual, autofocus, semantic duplicate and grouped-unit corrective safeguards remain in the release path.

## Compatibility

The Home Assistant app slug, database path, users, worksheets, attempts, progress, learning evidence, credentials and service tokens are unchanged. No destructive database migration is introduced.

## Review gate

This release must be tested in Home Assistant before merge, especially fraction comparison, Maths Lab manipulation, keyboard retry flow, parent tests and mobile/ingress layouts.
