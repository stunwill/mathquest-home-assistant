# MathQuest 0.35.0 - Home Assistant Parent Integration and Actionable Learning Insights

MathQuest now provides a compact, parent-readable Home Assistant learning state built from the same learning intelligence that drives the Parent Dashboard and adaptive learner experience.

## Highlights

- Home Assistant can see whether meaningful learner practice was completed today, including Daily Practice and Story Adventure.
- Parent Tests and abandoned sessions without answered-question evidence do not count as completed daily learning.
- Current focus includes the relevant skill, curriculum area, learning purpose, evidence confidence and MathQuest recommendation.
- Review due, persistent support dependence and repeated misconception signals use accumulated MathQuest evidence rather than isolated mistakes.
- A seven-day learning summary prioritises days practised, learning time, skills becoming secure, skills needing support, review status, misconception patterns and the recommended next focus.
- Notification-ready alerts are conservative and state-based. MathQuest does not send a notification for every incorrect answer and does not hard-code a daily reminder time.
- The integration remains local-first and uses the existing persistent Home Assistant service token. No cloud analytics or learner telemetry were added.
- Stable Home Assistant concept identifiers avoid transient worksheet, question, date, adventure and skill IDs.

## Compatibility

Existing `/api/ha/stats` and `/api/ha/summary` endpoints remain available. The new parent-learning endpoints are `/api/ha/learning` and `/api/ha/weekly-summary`.

Daily Practice, Story Adventure, adaptive question selection, prerequisite learning, spaced retrieval, retry-first answering, optional Math Mentor support, Visual Mathematics, worksheet resume/history and Parent Tests are preserved.
