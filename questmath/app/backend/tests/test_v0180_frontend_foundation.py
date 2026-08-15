from pathlib import Path

from app import v0170


ROOT = Path(__file__).resolve().parents[4]


def test_only_one_new_worksheet_post_route_is_registered():
    routes = [
        route for route in v0170.app.router.routes
        if getattr(route, 'path', None) == '/api/worksheets/new'
        and 'POST' in (getattr(route, 'methods', None) or set())
    ]
    assert len(routes) == 1
    assert routes[0].endpoint.__module__.endswith('v0120')


def test_student_foundation_owns_calendar_history_and_adventures():
    source = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'function WorksheetHistory' in source
    assert 'function LearningCalendar' in source
    assert 'function StoryAdventures' in source
    assert 'MutationObserver' not in source
    assert 'location.reload' not in source


def test_legacy_calendar_and_picker_layers_are_not_loaded():
    index = (ROOT / 'questmath/app/frontend/index.html').read_text(encoding='utf-8')
    assert '/src/v0160.ts' not in index
    assert '/src/v0160actions.ts' not in index


def test_core_frontend_uses_in_page_recovery_messages():
    api = (ROOT / 'questmath/app/frontend/src/api.ts').read_text(encoding='utf-8')
    foundation = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'Check Home Assistant and try again' in api
    assert 'role="alert"' in foundation
    assert 'alert(' not in foundation


def test_explicitly_resumed_worksheet_is_the_visual_source():
    main = (ROOT / 'questmath/app/frontend/src/main.tsx').read_text(encoding='utf-8')
    visual = (ROOT / 'questmath/app/frontend/src/question-visual.tsx').read_text(encoding='utf-8')
    assert '(window as any).__mq_ws=worksheet' in main
    assert '<QuestionVisual question={q}/>' in main
    assert 'const visual = question?.payload?.visual' in visual
