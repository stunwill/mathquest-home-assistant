# GitHub Actions setup

MathQuest uses two workflows:

- `Validate MathQuest` checks the backend, frontend and Home Assistant YAML metadata.
- `Publish MathQuest release` creates a Git tag and GitHub Release when a new app version is merged into `main`.

## Repository Actions permissions

In GitHub, open:

**Settings → Actions → General**

Under **Actions permissions**:

- Select **Allow all actions and reusable workflows**.

Under **Workflow permissions**:

- Select **Read and write permissions**.
- Leave **Allow GitHub Actions to create and approve pull requests** disabled. MathQuest does not require it.
- Save the settings.

The release workflow also declares `contents: write`, limiting the requested permission to repository contents and releases.

## Recommended branch protection

Open:

**Settings → Branches → Add branch protection rule**

Use branch name pattern:

```text
main
```

Recommended settings:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Require branches to be up to date before merging.
- Select the validation checks after they have run at least once:
  - `backend`
  - `frontend`
  - `metadata`
- Do not allow force pushes.
- Do not allow deletions.

For a one-person project, required approvals can remain disabled unless an independent review is wanted.

## Repository secrets

No custom repository secrets are required for the current workflows.

GitHub automatically supplies `GITHUB_TOKEN`. The release workflow uses it to create tags and releases. Do not create or store a personal access token for this workflow.

## First run

After the automation pull request is merged:

1. Open the repository's **Actions** tab.
2. Select **Publish MathQuest release**.
3. Confirm that the workflow triggered and completed successfully.
4. Open **Releases** and confirm that `MathQuest 0.3.1` exists.

If the release already exists, the workflow exits without creating a duplicate.

## Future app releases

Every app update pull request must change both:

- `version` in `questmath/config.yaml`
- the matching release section in `questmath/CHANGELOG.md`

For example:

```yaml
version: "0.3.2"
```

and:

```markdown
## 0.3.2 - 2026-07-30

### Fixed

- Fixed typed answers not enabling the Check Answer button.
```

After the pull request is merged into `main`, GitHub Actions creates tag `v0.3.2` and publishes the release notes automatically.
