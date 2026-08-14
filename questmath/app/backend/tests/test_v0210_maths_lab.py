from pathlib import Path

from app import v0210


ROOT = Path(__file__).resolve().parents[4]


def test_v0210_capability_route_is_before_spa_fallback():
    paths = [getattr(route, 'path', None) for route in v0210.app.router.routes]
    assert '/api/v0210/capabilities' in paths
    if '/{path:path}' in paths:
        assert paths.index('/api/v0210/capabilities') < paths.index('/{path:path}')


def test_frontend_lab_covers_the_release_models_and_replaces_legacy_button():
    source = (ROOT / 'questmath/app/frontend/src/maths-lab.tsx').read_text(encoding='utf-8')
    styles = (ROOT / 'questmath/app/frontend/src/styles.css').read_text(encoding='utf-8')
    for model in ('fractions', 'percentages', 'number-line', 'place-value', 'arrays', 'clock', 'grid', 'measurement'):
        assert f"id:'{model}'" in source
    assert '[data-manip]{display:none}' in styles
    main = (ROOT / 'questmath/app/frontend/src/main.tsx').read_text(encoding='utf-8')
    assert 'Open Maths Lab' in main
    assert 'if(feedback&&!feedback.retry_allowed)return' in main
    assert 'canStartOver={!feedback||feedback.retry_allowed}' in main
