# MathQuest for Home Assistant

MathQuest is a local, adaptive mathematics learning application designed for Sienna and packaged as a Home Assistant app.

> **Sienna's daily adventure in maths.**

## Current release

Version `0.3.1`

## Features

- Student and parent logins
- Responsive student dashboard
- Daily worksheets with save, resume and skip support
- Victorian Curriculum F–10 Version 2.0 Level 4 alignment
- Curriculum outcome tracking and parent review tools
- XP, levels, streaks and badges
- SQLite persistence and Home Assistant backup support
- Home Assistant ingress and sidebar integration

## Repository layout

```text
.
├── repository.yaml
├── README.md
├── LICENSE
├── .gitignore
├── .github/workflows/validate.yml
└── questmath/
    ├── config.yaml
    ├── build.yaml
    ├── Dockerfile
    ├── CHANGELOG.md
    ├── README.md
    ├── app/
    └── rootfs/
```

## Install in Home Assistant

1. Open **Settings → Apps → App store**.
2. Open the three-dot menu and select **Repositories**.
3. Add `https://github.com/stunwill/mathquest-home-assistant`.
4. Refresh the app store.
5. Install MathQuest.

## Development workflow

Changes are developed on branches and proposed to `main` using pull requests. Version changes must update `questmath/config.yaml`, frontend and backend version metadata, and `questmath/CHANGELOG.md`.
