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


def version_locations() -> dict[str, str]:
    config = yaml.safe_load((ROOT / 'questmath/config.yaml').read_text(encoding='utf-8'))
    package = json.loads((ROOT / 'questmath/app/frontend/package.json').read_text(encoding='utf-8'))
    return {
        'questmath/config.yaml': str(config['version']),
        'frontend/package.json': str(package['version']),
        'frontend/src/version.ts': _match(ROOT / 'questmath/app/frontend/src/version.ts', r"APP_VERSION\s*=\s*['\"]([^'\"]+)"),
        'backend/app/v0320.py': _match(ROOT / 'questmath/app/backend/app/v0320.py', r"app\.version\s*=\s*['\"]([^'\"]+)"),
        'rootfs startup message': _match(ROOT / 'questmath/rootfs/etc/services.d/questmath/run', r'Starting MathQuest v([^ ]+)'),
        'README.md': _match(ROOT / 'README.md', r'Current release\s+\n\s*Version `([^`]+)`'),
        'questmath/README.md': _match(ROOT / 'questmath/README.md', r'^# MathQuest ([^\s]+)'),
    }


def main() -> None:
    versions = version_locations()
    unique = set(versions.values())
    if len(unique) != 1:
        details = '\n'.join(f'- {path}: {version}' for path, version in versions.items())
        raise SystemExit(f'MathQuest version mismatch:\n{details}')
    print(f'MathQuest version {unique.pop()} is consistent across {len(versions)} required locations.')


if __name__ == '__main__':
    main()
