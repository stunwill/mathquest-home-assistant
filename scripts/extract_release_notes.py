#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path


def extract_release_notes(changelog: str, version: str) -> str:
    heading = re.compile(
        rf'^#{{1,2}}[ \t]+(?:MathQuest[ \t]+)?(?:v)?{re.escape(version)}(?:[ \t]+[^\n]*)?$',
        re.MULTILINE | re.IGNORECASE,
    )
    match = heading.search(changelog)
    if not match:
        raise ValueError(f'No changelog section found for {version}')
    following_heading = re.compile(r'^#{1,2}\s+', re.MULTILINE)
    next_match = following_heading.search(changelog, match.end())
    notes = changelog[match.end():next_match.start() if next_match else None].strip()
    if not notes:
        raise ValueError(f'Changelog section for {version} is empty')
    return notes


def release_notes_for(version: str, changelog_path: Path = Path('questmath/CHANGELOG.md')) -> str:
    changelog = changelog_path.read_text(encoding='utf-8')
    try:
        return extract_release_notes(changelog, version)
    except ValueError:
        corrective = changelog_path.parent / f'RELEASE_NOTES_{version}.md'
        if not corrective.exists():
            raise
        text = corrective.read_text(encoding='utf-8').strip()
        first_heading_end = text.find('\n')
        notes = text[first_heading_end + 1:].strip() if first_heading_end >= 0 else text
        if not notes:
            raise ValueError(f'Release notes for {version} are empty')
        return notes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('version')
    parser.add_argument('--changelog', type=Path, default=Path('questmath/CHANGELOG.md'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    notes = release_notes_for(args.version, args.changelog)
    if args.output:
        args.output.write_text(notes + '\n', encoding='utf-8')
    else:
        print(notes)


if __name__ == '__main__':
    main()
