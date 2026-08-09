# MathQuest 0.13.0

## Visual hints

MathQuest hints can now include a visual learning aid alongside the existing written guidance. The visual is generated from the current question data and does not reveal the correct answer.

### Fraction comparison

For comparison questions such as `2/3` versus `4/5`, Hint 1 renders two equal-sized fraction circles. Each circle is divided into the denominator number of equal slices and the numerator number of slices is shaded.

Hint 2 keeps the fraction circles and adds aligned fraction bars to provide a second representation of the same quantities without stating which fraction is larger.

### Other supported visuals

The visual-hint framework also supports:

- single fraction circles and fraction bars
- number lines
- decimal place-value columns
- analogue clocks
- angle diagrams with 90° and 180° reference landmarks
- labelled grids
- rectangle area/perimeter diagrams
- number-sequence stepping diagrams

Visuals are only shown when MathQuest can derive a reliable representation from the current question. If no suitable visual exists, the normal written hint continues to work unchanged.

## Learning behaviour

- Visual hints use the existing MathQuest hint count, so the current hint-aware mastery weighting remains unchanged.
- Requesting a visual does not create an additional hint event.
- The correct answer is never included in the visual-hint payload.
- Existing written Hint 1 and Hint 2 strategies are preserved.
- Existing adaptive learning, spaced revision, teaching mode, storytelling, worksheets, assignments, manipulatives and Home Assistant statistics remain unchanged.

## API

Adds authenticated student endpoint:

`GET /api/questions/{question_id}/hint-visual`

The endpoint returns a structured visual model for the current hint level or `null` when no reliable visual is available.

Also adds:

`GET /api/v0130/capabilities`

## Validation

The release includes regression coverage for fraction comparisons, second-stage fraction bars, single-fraction visuals, number lines, decimal place value, angles, unknown/no-visual questions and API route ordering behind the Home Assistant ingress SPA fallback.
