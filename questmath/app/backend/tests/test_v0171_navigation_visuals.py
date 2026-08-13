from __future__ import annotations

import random
from pathlib import Path

from app import v080, v0170


ROOT = Path(__file__).resolve().parents[4]


def test_question_card_is_keyed_and_previous_navigation_is_available():
    source = (ROOT / 'questmath/app/frontend/src/main.tsx').read_text(encoding='utf-8')
    assert 'key={q.id} data-question-id={q.id}' in source
    assert 'Previous question' in source
    assert 'function previousEligible' in source
    assert "'skipped','retry_available'" in source
    assert 'Finish worksheet with skipped questions' in source
    assert '<h2>Badges</h2>' not in source
    foundation = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'completion-calendar' in foundation


def test_visual_guard_rejects_a_visual_from_another_question():
    source = (ROOT / 'questmath/app/frontend/src/v0150.ts').read_text(encoding='utf-8')
    assert 'dataset.questionId' in source
    assert 'existing.dataset.qid!==cardQuestionId' in source
    assert 'existing.remove()' in source
    assert '!card.isConnected' in source
    assert 'requestAnimationFrame(run)' in source


def test_calendar_navigation_keeps_a_stable_calendar_target():
    source = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert 'function LearningCalendar' in source
    assert 'setRangeStart' in source
    assert 'mq-v0160-calendar' in source
    assert 'MutationObserver' not in source


def test_story_adventure_creates_and_opens_a_new_worksheet():
    source = (ROOT / 'questmath/app/frontend/src/student-foundation.tsx').read_text(encoding='utf-8')
    assert "createWorksheet('mixed')" in source
    assert '/adventure' in source
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
        card = item[3]['strategy_card']
        if card['strategy'] != 'Make 10 first':
            continue
        first, second = [int(value) for value in item[1].replace('Calculate ', '').replace('.', '').split(' + ')]
        assert second >= 10 - first


def test_direct_subtraction_has_strictly_more_on_top():
    for seed in range(300):
        item = v0170._written_subtraction(random.Random(seed))
        if item[3]['subtraction_case'] != 'no_regroup':
            continue
        top, bottom = [int(value) for value in item[1].replace('Calculate ', '').replace('.', '').split(' − ')]
        assert top % 10 > bottom % 10


def test_focus_target_is_used_by_question_generation():
    token = v0170._focus_targets.set({'number': 'fact_recall_subtraction'})
    try:
        item = v0170.make_question_v0170('number', 1, random.Random(1))
    finally:
        v0170._focus_targets.reset(token)
    assert item[0].endswith(':fact_recall_subtraction')
