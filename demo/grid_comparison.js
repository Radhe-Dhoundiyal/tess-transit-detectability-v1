'use strict';
(() => {
  const $ = id => document.getElementById(id);
  const labels = {
    DIRECT_RECOVERY: 'Direct', HALF_PERIOD_HARMONIC_RECOVERY: 'Half-period harmonic',
    DOUBLE_PERIOD_HARMONIC_RECOVERY: 'Double-period harmonic',
    OTHER_INTEGER_HARMONIC_RECOVERY: 'Other integer harmonic',
    ALIAS_RECOVERY: 'Alias', NOT_RECOVERED: 'Not recovered'
  };
  let records = null, loading = false;
  function change(row) {
    return row.baseline_direct_top10 === row.alternative_direct_top10 ? 'unchanged' :
      row.alternative_direct_top10 ? 'gain' : 'loss';
  }
  function renderRows() {
    const query = $('comparison-search').value.trim().toLowerCase();
    const cohort = $('comparison-cohort').value, outcome = $('comparison-change').value;
    const selected = records.filter(row =>
      (!query || `${row.trial_id} ${row.host_name}`.toLowerCase().includes(query)) &&
      (cohort === 'all' || row.cohort === cohort) && (outcome === 'all' || change(row) === outcome));
    $('comparison-count').textContent = `${selected.length} of ${records.length} paired trials · summary above uses all 320`;
    $('comparison-rows').replaceChildren();
    for (const row of selected) {
      const tr = document.createElement('tr');
      const values = [row.trial_id, row.host_name,
        row.cohort === 'original_exploratory' ? 'Exploratory' : 'Extension',
        labels[row.baseline_recovery_class], labels[row.alternative_recovery_class],
        row.baseline_direct_top1_literal ? 'Yes' : 'No', row.alternative_direct_top1_literal ? 'Yes' : 'No',
        change(row)];
      for (const value of values) {
        const td = document.createElement('td');
        td.textContent = value;
        tr.append(td);
      }
      tr.lastChild.className = change(row) === 'gain' ? 'direct' : change(row) === 'loss' ? 'alias' : 'nonrecovery';
      $('comparison-rows').append(tr);
    }
    if (!selected.length) {
      const tr = document.createElement('tr'), td = document.createElement('td');
      td.colSpan = 8;
      td.textContent = 'No matching paired trials.';
      tr.append(td);
      $('comparison-rows').append(tr);
    }
  }
  function showSummary(summary) {
    const box = $('comparison-scores');
    for (const [label, value] of [
      ['Primary direct top-10', `${summary.baseline_direct}/320 → ${summary.alternative_direct}/320`],
      ['Literal direct rank-1', `${summary.baseline_direct_top1_literal}/320 → ${summary.alternative_direct_top1_literal}/320`],
      ['Primary paired change', `${summary.paired_gains} gains · ${summary.paired_losses} loss · ${summary.unchanged_primary} unchanged`]
    ]) {
      const group = document.createElement('div'), name = document.createElement('span'), number = document.createElement('strong');
      name.textContent = label;
      number.textContent = value;
      group.append(name, number);
      box.append(group);
    }
    const note = document.createElement('p');
    const interval = summary.difference_percentile_95_ci.map(value => `+${(100 * value).toFixed(4)}`).join(' to ');
    note.textContent = `Paired change +${(100 * summary.absolute_difference).toFixed(4)} percentage points. Descriptive 95% host-bootstrap interval: ${interval} points.`;
    box.append(note);
  }
  window.loadGridComparison = async () => {
    if (records || loading || location.protocol === 'file:') return;
    loading = true;
    $('comparison-status').textContent = 'Reading saved paired records…';
    try {
      const response = await fetch('/api/grid-comparison', {cache: 'no-store'});
      if (!response.ok) throw Error('Saved records unavailable');
      const data = await response.json();
      if (data.rows.length !== 320 || data.summary.trials !== 320) throw Error('Incomplete paired records');
      records = data.rows;
      showSummary(data.summary);
      renderRows();
      $('comparison-live').hidden = false;
      $('comparison-status').textContent = 'Saved period-and-epoch matches · 32 exploratory trials / 4 hosts + 288 extension trials / 36 hosts';
    } catch {
      $('comparison-status').textContent = 'Paired table unavailable. The figures remain available; start the included local Python server to inspect the records.';
    } finally {
      loading = false;
    }
  };
  for (const id of ['comparison-search', 'comparison-cohort', 'comparison-change']) {
    $(id).addEventListener(id === 'comparison-search' ? 'input' : 'change', () => { if (records) renderRows(); });
  }
})();
