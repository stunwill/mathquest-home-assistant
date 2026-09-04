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


def test_release_notes_extract_current_version_section_only():
    module = load_script('extract_release_notes')
    versions = load_script('validate_versions').version_locations()
    current_version = versions['questmath/config.yaml']
    notes = module.release_notes_for(current_version, ROOT / 'questmath/CHANGELOG.md')
    lowered = notes.lower()
    assert 'session learning quality' in lowered
    assert 'recent' in lowered
    assert 'adaptive' in lowered
    assert 'melbourne' not in lowered
    assert 'ipad landscape' not in lowered


def test_required_version_locations_agree():
    module = load_script('validate_versions')
    versions = module.version_locations()
    expected_version = versions['questmath/config.yaml']
    assert set(versions.values()) == {expected_version}
    assert 'frontend/package.json' in versions
    assert any('v0390.py app.version' in key for key in versions)
    module.validate_frontend_lockfile()


def test_release_workflow_validates_versions_before_publishing():
    workflow = (ROOT / '.github/workflows/release.yml').read_text(encoding='utf-8')
    validation = workflow.index('python scripts/validate_versions.py')
    existing_tag_check = workflow.index('name: Check whether the tag already exists')
    publish = workflow.index('gh release create')
    assert validation < existing_tag_check < publish


def test_validation_workflow_does_not_hard_code_release_version_for_notes():
    workflow = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
    extraction_step = workflow.split('- name: Validate release-note extraction', 1)[1]
    assert "config['version']" in extraction_step
    assert 'extract_release_notes.py "$VERSION"' in extraction_step


def test_frontend_validation_uses_committed_lockfile():
    workflow = (ROOT / '.github/workflows/validate.yml').read_text(encoding='utf-8')
    assert 'run: npm ci' in workflow
    assert 'run: npm test' in workflow
    assert 'run: npm run build' in workflow
