# Contributing to MathQuest

MathQuest changes are developed on a branch and merged into `main` through a pull request.

## Branches

Use a short descriptive branch name, for example:

- `fix/worksheet-answer-button`
- `feature/curriculum-progress-dashboard`
- `chore/update-documentation`

## Pull requests

Every pull request should:

1. Explain what changed and why.
2. Include testing notes.
3. Pass the GitHub Actions validation checks.
4. Update `questmath/CHANGELOG.md` when the app behaviour changes.
5. Increase `version` in `questmath/config.yaml` when Home Assistant users need to receive an app update.

## Versioning

MathQuest uses semantic versions in the form `MAJOR.MINOR.PATCH`.

- **PATCH**, for example `0.3.1` to `0.3.2`: bug fixes and small improvements.
- **MINOR**, for example `0.3.2` to `0.4.0`: new backwards-compatible features.
- **MAJOR**, for example `0.9.0` to `1.0.0`: a major stable milestone or incompatible change.

Do not reuse a version that has already been released.

## Automated releases

After a pull request containing a new app version is merged into `main`, `.github/workflows/release.yml`:

1. Reads the version from `questmath/config.yaml`.
2. Validates its format.
3. Extracts the matching section from `questmath/CHANGELOG.md`.
4. Creates a Git tag such as `v0.3.2`.
5. Publishes a GitHub Release.

Home Assistant update detection still depends on the version in `questmath/config.yaml`. The GitHub Release provides traceability and release notes.

## Changelog format

Add the newest release near the top of `questmath/CHANGELOG.md` using this structure:

```markdown
## 0.3.2 - 2026-07-30

### Fixed

- Fixed the Check Answer button not enabling after typing an answer.
```

## Release checklist

Before merging an app release:

- [ ] The app builds successfully.
- [ ] The changed behaviour has been tested.
- [ ] `questmath/config.yaml` contains the new version.
- [ ] `questmath/CHANGELOG.md` contains a matching version heading.
- [ ] No passwords, tokens or private information are committed.
- [ ] All required pull-request checks pass.
