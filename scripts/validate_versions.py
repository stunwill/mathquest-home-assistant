#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _match(path: Path, pattern: str) -> str:
    match = re.search(pattern, path.read_text(encoding='utf-8'), re.MULTILINE)
    if not match:
        raise ValueError(f'Unable to read version from {path.relative_to(ROOT)}')
    return match.group(1)


def _normalise(version: str) -> str:
    return version[1:] if version.startswith('v') else version


def version_locations() -> dict[str, str]:
    config = yaml.safe_load((ROOT / 'questmath/config.yaml').read_text(encoding='utf-8'))
    package = json.loads((ROOT / 'questmath/app/frontend/package.json').read_text(encoding='utf-8'))
    backend_path = ROOT / 'questmath/app/backend/app/v0360.py'
    return {
        'questmath/config.yaml': str(config['version']),
        'frontend/package.json': str(package['version']),
        'frontend/src/version.ts': _match(ROOT / 'questmath/app/frontend/src/version.ts', r"APP_VERSION\s*=\s*['\"]([^'\"]+)"),
        'backend/app/v0360.py app.version': _match(backend_path, r"app\.version\s*=\s*['\"]([^'\"]+)"),
        'backend/app/v0360.py health version': _match(backend_path, r"legacy\.APP_VERSION\s*=\s*['\"]([^'\"]+)"),
        'rootfs startup message': _match(ROOT / 'questmath/rootfs/etc/services.d/questmath/run', r'Starting MathQuest v([^ ]+)'),
        'README.md': _match(ROOT / 'README.md', r'Current release\s+\n\s*Version `([^`]+)`'),
        'questmath/README.md': _match(ROOT / 'questmath/README.md', r'^# MathQuest ([^\s]+)'),
        'root CHANGELOG.md': _normalise(_match(ROOT / 'CHANGELOG.md', r'^##\s+v?([0-9]+\.[0-9]+\.[0-9]+)\b')),
        'Home Assistant CHANGELOG.md': _normalise(_match(ROOT / 'questmath/CHANGELOG.md', r'^##\s+v?([0-9]+\.[0-9]+\.[0-9]+)\b')),
    }


def validate_metadata_files(expected_version: str) -> None:
    required = [ROOT / 'ROADMAP.md', ROOT / 'CHANGELOG.md', ROOT / 'questmath/CHANGELOG.md']
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        raise SystemExit('Missing required DevHub metadata files: ' + ', '.join(missing))
    roadmap = (ROOT / 'ROADMAP.md').read_text(encoding='utf-8')
    if f'## v{expected_version} - ' not in roadmap:
        raise SystemExit(f'ROADMAP.md does not contain current release v{expected_version}')
    if 'Status: Completed' not in roadmap or 'Status: Planned' not in roadmap:
        raise SystemExit('ROADMAP.md must expose completed and planned phase status for DevHub parsing')
    for relative in ['CHANGELOG.md', 'questmath/CHANGELOG.md']:
        text = (ROOT / relative).read_text(encoding='utf-8')
        if not re.search(rf'^##\s+v?{re.escape(expected_version)}\b', text, re.MULTILINE):
            raise SystemExit(f'{relative} does not contain release {expected_version}')


def main() -> None:
    versions = version_locations()
    unique = set(versions.values())
    if len(unique) != 1:
        details = '\n'.join(f'- {path}: {version}' for path, version in versions.items())
        raise SystemExit(f'MathQuest version mismatch:\n{details}')
    expected_version = unique.pop()
    validate_metadata_files(expected_version)
    print(f'MathQuest version {expected_version} is consistent across {len(versions)} required locations.')
    print('DevHub metadata files and roadmap phase markers are present.')


if __name__ == '__main__':
    main()
