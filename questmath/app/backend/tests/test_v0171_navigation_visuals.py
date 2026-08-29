from __future__ import annotations

import random
from pathlib import Path

from app import v080, v0170


ROOT = Path(__file__).resolve().parents[4]


def test_question_card_is_keyed_and_previous_navigation_is_available():
    source = (ROOT / 'questmath/app/frontend/src/main.tsx').read_text(encoding='utf-8')
    assert "key={`${q.id}:${q.payload?.visual_key||''}`}" in source
    assert 'data-visual-key={q.payload?.visual_key}' in source
    assert 'Previous question' in source
    assert 'function previousEligible' in source
    assert "'skipped','retry_available'" in source
    assert 'Finish worksheet with skipped questions' in source
    assert '<h2>Badges</h2>' not in source
    foundation = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'completion-calendar' in foundation


def test_visual_guard_rejects_a_visual_from_another_question():
    source = (ROOT / 'questmath/app/frontend/src/question-visual.tsx').read_text(encoding='utf-8')
    main = (ROOT / 'questmath/app/frontend/src/main.tsx').read_text(encoding='utf-8')
    assert 'question?.payload?.visual_key' in source
    assert '<QuestionVisual question={q}/>' in main
    assert "key={`${q.id}:${q.payload?.visual_key||''}`}" in main


def test_calendar_navigation_keeps_a_stable_calendar_target():
    source = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'function LearningCalendar' in source
    assert 'setRangeStart' in source
    assert 'mq-v0160-calendar' in source
    assert 'MutationObserver' not in source


def test_story_adventure_uses_timed_adaptive_session_and_opens_it_in_place():
    source = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert "createSession('practice', minutes, 'mixed')" in source
    assert '/adventure-v0340' in source
    assert 'onOpen(await apiRequest' in source
    assert 'location.reload' not in source


def test_grid_question_payload_identifies_the_highlighted_square():
    item = v080._visual_grid(random.Random(7))
    payload = item[3]
    assert payload['visual']['type'] == 'grid'
    assert payload['visual']['target'] == item[4]
    assert item[4] in payload['choices']
    assert len(payload['choices']) == 16


def test_make_ten_never_splits_more_than_the_second_addend():
    for seed in range(300):
        item = v0170._addition_fact(random.Random(seed))
        payload = item[3]
        if payload.get('strategy_card', {}).get('strategy') != 'Make a ten':
            continue
        left, right = payload['numbers']
        needed = 10 - (left % 10)
        assert 0 < needed <= right
