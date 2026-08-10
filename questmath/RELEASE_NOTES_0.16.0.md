# MathQuest 0.16.0

## Worksheet history and resume

- Incomplete worksheets now show answered/total progress, elapsed learning time and a dedicated **Continue worksheet** action.
- Continuing a worksheet pins that exact worksheet ID as the active worksheet so page reloads do not silently switch to a different unfinished worksheet.
- Starting a new worksheet pins the newly created worksheet immediately and opens it after reload.
- The student hero now supplements current-worksheet progress with separate totals for all learning completed today.

## Weekly Learning Activity

- Replaces the old 28-day completion grid with a seven-day learning activity view.
- Defaults to the current Monday-Sunday calendar week.
- Includes previous day, previous week, next day and next week controls.
- Forward controls are disabled on the current week to avoid browsing into future periods with no learning data.
- Each day shows questions, accuracy, correct/incorrect totals, hints, XP, learning duration and the worksheets associated with the day.
- Worksheet entries in the calendar are actionable: incomplete work can be continued and completed work can be reviewed.
- Past weeks and sliding seven-day windows can be explored without changing the underlying worksheet dates.

## Analogue clocks

- Teaching clocks now display all twelve hour numbers.
- Added minute tick marks with stronger five-minute markers.
- Existing hour/minute hand positioning is retained.

## API

- Added `GET /api/worksheets/history-v0160` with dashboard-friendly worksheet progress and elapsed time.
- Added `GET /api/learning/week-v0160?start=YYYY-MM-DD` for seven-day learning activity summaries.
- Added `GET /api/v0160/capabilities`.

## Compatibility

- Preserves visual questions, visual hints, multiple worksheets per day, parent reporting, Home Assistant statistics, completed worksheet review, adaptive learning and existing worksheet data.
