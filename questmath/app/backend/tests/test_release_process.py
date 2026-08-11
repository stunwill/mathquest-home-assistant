from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def load_script(name: str):
    path = ROOT / 'scripts' / f'{name}.py'
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def test_release_notes_extract_v0162_section_only():
    module = load_script('extract_release_notes')
    changelog = (ROOT / 'questmath/CHANGELOG.md').read_text(encoding='utf-8')
    notes = module.extract_release_notes(changelog, '0.16.2')
    assert notes.startswith('- Replaced the public development JWT signing secret')
    assert 'JWT' in notes
    assert 'login' in notes.lower()
    assert '0.16.1' not in notes


def test_required_version_locations_agree():
    module = load_script('validate_versions')
    versions = module.version_locations()
    assert set(versions.values()) == {'0.16.2'}
