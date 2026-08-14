function esc(value: unknown) {
  return String(value ?? '').replace(/[&<>"']/g, character => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;',
  }[character] || character));
}

export function fractionComparisonMarkup(items: any[] = []) {
  return `<div class="mq-visual fraction-compare" role="group" aria-label="Fraction comparison using equal-sized wholes">${items.map(item => {
    const numerator = Math.max(0, Number(item.numerator) || 0);
    const denominator = Math.max(1, Number(item.denominator) || 1);
    return `<div class="fraction-row"><b>${esc(item.label)}</b><div class="fraction-bar" role="img" aria-label="${esc(numerator)} of ${esc(denominator)} equal parts shaded">${Array.from({length: denominator}, (_, index) => `<span class="${index < numerator ? 'on' : ''}"></span>`).join('')}</div><small>${esc(numerator)}/${esc(denominator)}</small></div>`;
  }).join('')}</div>`;
}

export function gridReferenceMarkup(visual: any) {
  const rows = Array.isArray(visual?.columns) ? visual.columns.map(String) : [];
  const columnCount = Math.max(1, Number(visual?.rows) || 1);
  const columnLabels = Array.from({length: columnCount}, (_, index) => index + 1);
  const target = String(visual?.target || '');
  const cells = rows.map((row: string) => `<span class="grid-axis grid-row-label">${esc(row)}</span>${columnLabels.map(column => {
    const reference = `${row}${column}`;
    return `<span class="grid-cell ${reference === target ? 'target' : ''}"${reference === target ? ' aria-label="Highlighted square"' : ' aria-hidden="true"'}></span>`;
  }).join('')}`).join('');
  return `<div class="mq-visual grid-reference-visual" role="group" aria-label="Grid reference diagram with labelled rows and columns"><div class="grid-vis" style="--mq-grid-columns:${columnCount}"><span class="grid-corner" aria-hidden="true"></span>${columnLabels.map(column => `<span class="grid-axis grid-column-label">${column}</span>`).join('')}${cells}</div></div>`;
}
