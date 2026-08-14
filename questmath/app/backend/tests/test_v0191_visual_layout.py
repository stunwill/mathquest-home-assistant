from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]


def test_fraction_comparison_rows_share_an_equal_whole_column():
    styles = (ROOT / 'questmath/app/frontend/src/v080.css').read_text(encoding='utf-8')
    assert '.fraction-compare{display:grid;grid-template-columns:minmax(0,1fr)' in styles
    assert '.fraction-row{display:grid;grid-template-columns:minmax(90px,auto) minmax(0,1fr) auto' in styles
    assert '.fraction-bar{display:flex;gap:4px;width:100%}' in styles


def test_grid_uses_external_axis_labels_and_blank_cells():
    source = (ROOT / 'questmath/app/frontend/src/visual-markup.ts').read_text(encoding='utf-8')
    assert 'grid-row-label' in source
    assert 'grid-column-label' in source
    assert 'aria-label="Highlighted square"' in source
    assert 'data-visual-answer' not in source
    assert '${reference}' not in source
