# MathQuest v0.40.0

## Student Mobile Home, Navigation & Responsive UX

MathQuest v0.40.0 is a focused student-experience release based on real iPhone use inside Home Assistant ingress.

The release changes the student mobile information hierarchy so current learning is easier to find and act on without weakening the adaptive learning system.

### What changed

- Unfinished worksheets and meaningful skipped-question recovery are promoted through **Continue Learning**.
- Completed worksheet history is reduced to three recent items by default, with **View all worksheets** for older work.
- Story Adventure uses compact horizontally swipeable cards on narrow screens instead of a long stack of large cards.
- Mobile student navigation provides Home, Adventure, Worksheets and Progress destinations with text labels and safe-area spacing.
- The MathQuest student header is reduced on mobile so the Home Assistant ingress header plus MathQuest identity consume less vertical space.
- The weekly calendar no longer compresses previous week, previous day, date range, next day and next week into unusable phone columns.
- Mobile week navigation uses previous week, date range, next week and Today, with day-by-day learning activity presented vertically.
- Mobile history and progress presentation use flatter visual grouping and stronger distinction between primary current actions and secondary historical actions.

### Learning behaviour preserved

This release does not change the mathematics selection or evidence model. It inherits the complete v0.39.0 backend learning-quality implementation and preserves:

- adaptive Daily Learning;
- prerequisite routing;
- spaced retrieval;
- recent-exposure logic;
- misconception evidence;
- independent versus supported success;
- confidence evidence;
- Math Mentor, hints and worked examples;
- Visual Mathematics and interactive answers;
- Story Adventure adaptive question selection;
- Parent Learning Intelligence;
- Parent Test isolation;
- the v0.38 keyboard-first post-answer feedback experience.

### Responsive intent

The narrow-screen presentation is designed around iPhone portrait while preserving the existing tablet and desktop architecture. Responsive CSS, not device-name detection, controls the layout. The mobile navigation reserves `safe-area-inset-bottom`, touch controls retain suitable targets, focus remains visible and reduced-motion preferences are respected.

### Validation status

Automated repository validation must pass before merge, including backend pytest, frontend Vitest and TypeScript/Vite build, version metadata, YAML/release-note checks and the real aarch64 add-on startup/health job.

Physical iPhone and iPad acceptance is documented separately in `MANUAL_ACCEPTANCE_0.40.0.md`. Those checks must not be marked complete unless they are performed on the actual devices.
