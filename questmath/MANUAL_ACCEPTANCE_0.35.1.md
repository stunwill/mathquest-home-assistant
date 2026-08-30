# MathQuest v0.35.1 Home Assistant Acceptance Test

Use this checklist against the installed Home Assistant add-on before merging the corrective release.

## Parent Dashboard

1. Open MathQuest from the Home Assistant sidebar.
2. Sign in with the parent account.
3. Confirm the Parent Dashboard renders rather than remaining on the MathQuest splash screen.
4. Confirm Parent Learning Intelligence renders when its request completes.
5. Refresh the browser while on the Parent Dashboard.
6. Close and reopen the MathQuest sidebar panel.
7. Open MathQuest in a new browser tab or window from Home Assistant.
8. Restart the MathQuest add-on, reopen MathQuest and confirm the Parent Dashboard recovers.

## Failure handling

1. Confirm a required Parent Dashboard bootstrap failure shows a visible retryable error rather than an indefinite splash screen.
2. Confirm a backups failure does not prevent the main Parent Dashboard from rendering.
3. Confirm an optional Parent Learning Intelligence failure does not prevent the core Parent Dashboard from rendering.
4. Confirm Retry can recover after a transient failure.
5. Confirm an expired MathQuest JWT offers sign-in recovery.
6. If Home Assistant returns a plain-text 401 through ingress/proxy handling, confirm MathQuest reports that Home Assistant could not validate the session and advises reopening from the sidebar.

## Regression checks

1. Confirm Student Dashboard still loads.
2. Confirm Daily Practice still starts and resumes.
3. Confirm Story Adventure still starts and records learner evidence.
4. Confirm Parent Tests remain separate from ordinary learner evidence.
5. Confirm worksheet settings still load and save.
6. Confirm backups still list and create when the backups API is available.
7. Confirm Home Assistant learning endpoints remain available with the service token.

## Home Assistant logs

During normal sidebar use, review Home Assistant logs for `/ingress/validate_session` failures. MathQuest does not expose that route itself, so any remaining Home Assistant validation failure should be recorded separately with its exact timestamp and surrounding Supervisor/Home Assistant log context.
