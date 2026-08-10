# MathQuest v0.14.1

## Required question visuals hotfix

- Fixes inherently visual questions, including analogue clocks, angles, number lines, grids, fraction comparisons and charts, rendering without their required diagram.
- The backend was already generating structured visual payloads, but the v0.8 frontend could miss the initial worksheet response because its fetch wrapper loaded after React.
- Adds an early visual guard that independently retrieves the current date-scoped active worksheet and renders the active question visual from its real payload.
- Keeps the existing v0.8 renderer as compatibility fallback while avoiding duplicate visual panels.
- If an inherently visual question genuinely lacks a visual payload, MathQuest now shows a clear Visual unavailable warning instead of silently presenting an unanswerable question.
- Preserves v0.14 daily quest-state fixes, visual hints, multiple worksheets, worksheet review and Home Assistant statistics.
- Bumps add-on, frontend and runtime metadata to 0.14.1.
