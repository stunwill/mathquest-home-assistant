# MathQuest 0.12.1

- Fixes production GET API routes being shadowed by the single-page-app fallback route.
- Prevents newer MathQuest endpoints from returning `index.html` where JSON is expected.
- Hardens v0.12 frontend API parsing so unexpected non-JSON responses are reported cleanly rather than repeatedly throwing JSON parser errors.
- Adds a regression test that ensures worksheet history, parent dashboard, Home Assistant statistics and weekly-report routes are registered before the SPA fallback.
- Preserves v0.12 multiple daily worksheets, completed worksheet review and parent learner resolution.
