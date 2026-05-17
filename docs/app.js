// Client-side filter/search/sort + interactive charts for the GenAI
// Security Incidents dataset. Pure vanilla JS, no build, no deps.

const PAGE_SIZE_DEFAULT = 250;
const PAGE_SIZE_OPTIONS = [50, 100, 250, 500, 1000];
let PAGE_SIZE = PAGE_SIZE_DEFAULT;
const SEV_RANK = { Critical: 4, High: 3, Medium: 2, Low: 1, Info: 0 };
const SEV_VARS = {
  Critical: "var(--critical)",
  High: "var(--high)",
  Medium: "var(--medium)",
  Low: "var(--low)",
  Info: "var(--info)",
};
const LLM_NAMES = {
  LLM01: "Prompt Injection", LLM02: "Sensitive Info Disclosure",
  LLM03: "Supply Chain", LLM04: "Data & Model Poisoning",
  LLM05: "Improper Output Handling", LLM06: "Excessive Agency",
  LLM07: "System Prompt Leakage", LLM08: "Vector & Embedding",
  LLM09: "Misinformation", LLM10: "Unbounded Consumption",
};
const ASI_NAMES = {
  ASI01: "Agent Goal Hijack", ASI02: "Tool Misuse & Exploit",
  ASI03: "Identity & Privilege Abuse", ASI04: "Agentic Supply Chain",
  ASI05: "Unexpected RCE", ASI06: "Memory & Context Poisoning",
  ASI07: "Insecure Inter-Agent Comm", ASI08: "Cascading Failures",
  ASI09: "Human-Agent Trust Exploit", ASI10: "Rogue Agents",
};

const els = {
  q: document.getElementById('q'),
  year: document.getElementById('year'),
  severity: document.getElementById('severity'),
  llm: document.getElementById('llm'),
  asi: document.getElementById('asi'),
  vector: document.getElementById('vector'),
  corpus: document.getElementById('corpus'),
  quality: document.getElementById('quality'),
  cveOnly: document.getElementById('cve_only'),
  pageSize: document.getElementById('page_size'),
  status: document.getElementById('result-status'),
  body: document.querySelector('#incidents tbody'),
  pager: document.getElementById('pager'),
  chips: document.getElementById('filter-chips'),
  stats: document.getElementById('stats'),
  meta: document.getElementById('dataset-meta'),
  table: document.getElementById('incidents'),
  backToTop: document.getElementById('back-to-top'),
};

const FILTER_KEYS = ['q','year','severity','llm','asi','vector','corpus','quality','cveOnly'];
const FILTER_LABEL = {
  q: 'Search', year: 'Year', severity: 'Severity',
  llm: 'OWASP LLM', asi: 'OWASP ASI', vector: 'Vector',
  corpus: 'Corpus', quality: 'Quality', cveOnly: 'CVE',
};

let DATA = [];
let FILTERED = [];
let PAGE = 1;
let SORT_BY = 'date';
let SORT_DIR = 'desc';
let EXPANDED = new Set();

// ----------------------------- Utilities ---------------------------------

const escapeHtml = s => (s || '').replace(/[&<>"']/g,
  c => ({ '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;' }[c]));

const uniqSorted = arr => Array.from(new Set(arr)).sort();

const dateScore = e => (e.date || String(e.year || 0)).padEnd(10, '0');

const fmtNum = n => Number(n).toLocaleString();

const isFilterActive = key => {
  const v = filterValue(key);
  return v !== '' && v !== false && v != null;
};

function filterValue(key) {
  const el = els[key === 'cveOnly' ? 'cveOnly' : key];
  if (!el) return '';
  return el.type === 'checkbox' ? el.checked : el.value;
}

function setFilter(key, value) {
  const el = els[key === 'cveOnly' ? 'cveOnly' : key];
  if (!el) return;
  if (el.type === 'checkbox') el.checked = !!value;
  else el.value = value || '';
}

function activeFiltersCount() {
  return FILTER_KEYS.filter(isFilterActive).length;
}

// ----------------------------- URL state ---------------------------------

function readFiltersFromUrl() {
  const raw = location.hash.slice(1) || location.search.slice(1);
  if (!raw) return;
  const p = new URLSearchParams(raw);
  for (const k of FILTER_KEYS) {
    if (k === 'cveOnly') {
      if (p.get('cve_only') === '1') els.cveOnly.checked = true;
    } else if (p.has(k)) {
      setFilter(k, p.get(k));
    }
  }
  if (p.has('sort')) SORT_BY = p.get('sort');
  if (p.has('dir'))  SORT_DIR = p.get('dir') === 'asc' ? 'asc' : 'desc';
  if (p.has('page')) PAGE = Math.max(1, parseInt(p.get('page'), 10) || 1);
  if (p.has('ps')) {
    const n = parseInt(p.get('ps'), 10);
    if (PAGE_SIZE_OPTIONS.includes(n)) PAGE_SIZE = n;
  }
}

function writeFiltersToUrl() {
  const p = new URLSearchParams();
  for (const k of FILTER_KEYS) {
    const v = filterValue(k);
    if (k === 'cveOnly') { if (v) p.set('cve_only', '1'); }
    else if (v) p.set(k, v);
  }
  if (SORT_BY !== 'date' || SORT_DIR !== 'desc') {
    p.set('sort', SORT_BY); p.set('dir', SORT_DIR);
  }
  if (PAGE > 1) p.set('page', String(PAGE));
  if (PAGE_SIZE !== PAGE_SIZE_DEFAULT) p.set('ps', String(PAGE_SIZE));
  const qs = p.toString();
  history.replaceState(null, '', qs ? '#' + qs : location.pathname);
}

// ----------------------------- Filtering / sorting -----------------------

function matches(e) {
  if (els.year.value     && String(e.year) !== els.year.value) return false;
  if (els.severity.value && e.severity !== els.severity.value)  return false;
  if (els.llm.value      && !(e.owasp_llm || []).includes(els.llm.value)) return false;
  if (els.asi.value      && !(e.owasp_asi || []).includes(els.asi.value)) return false;
  if (els.vector.value   && e.attack_vector !== els.vector.value) return false;
  if (els.corpus.value   && e.corpus !== els.corpus.value)      return false;
  if (els.quality.value  && e.quality_tier !== els.quality.value) return false;
  if (els.cveOnly.checked && !(e.cve_ids || []).length)         return false;
  const q = els.q.value.trim().toLowerCase();
  if (q) {
    const hay = (
      e.id + ' ' + e.title + ' ' + (e.attack_vector || '') + ' ' +
      (e.affected || '') + ' ' +
      (e.cve_ids || []).join(' ') + ' ' +
      (e.owasp_llm || []).join(' ') + ' ' + (e.owasp_asi || []).join(' ') + ' ' +
      (e.primary_reference || '')
    ).toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function comparator() {
  const dir = SORT_DIR === 'asc' ? 1 : -1;
  if (SORT_BY === 'date') return (a, b) => dateScore(a).localeCompare(dateScore(b)) * dir;
  if (SORT_BY === 'severity') return (a, b) => ((SEV_RANK[a.severity] ?? -1) - (SEV_RANK[b.severity] ?? -1)) * dir;
  return (a, b) => 0;
}

// ----------------------------- Stats hero --------------------------------

function renderStats(allRows) {
  const total = allRows.length;
  const crit = allRows.filter(r => r.severity === 'Critical').length;
  const withCve = allRows.filter(r => (r.cve_ids || []).length).length;
  const curated = allRows.filter(r => r.quality_tier === 'curated').length;
  const reviewed = allRows.filter(r => r.quality_tier === 'reviewed').length;
  const years = uniqSorted(allRows.map(r => r.year).filter(Boolean));
  const latest = years[years.length - 1];
  const earliest = years[0];

  els.stats.innerHTML = `
    <div class="stat"><span class="num">${fmtNum(total)}</span><span class="label">Incidents</span><span class="sub">${earliest}–${latest}</span></div>
    <div class="stat"><span class="num sev-Critical" style="color: var(--critical)">${fmtNum(crit)}</span><span class="label">Critical</span><span class="sub">${(100*crit/total).toFixed(1)}% of total</span></div>
    <div class="stat"><span class="num">${fmtNum(withCve)}</span><span class="label">With CVE</span><span class="sub">${(100*withCve/total).toFixed(1)}% of total</span></div>
    <div class="stat"><span class="num">${fmtNum(curated + reviewed)}</span><span class="label">Curated + Reviewed</span><span class="sub">${fmtNum(curated)} curated</span></div>
    <div class="stat"><span class="num">${fmtNum(years.length)}</span><span class="label">Years</span><span class="sub">unbroken since ${earliest}</span></div>
  `;
}

// ----------------------------- Filter chips ------------------------------

function renderChips() {
  const parts = [];
  for (const k of FILTER_KEYS) {
    if (!isFilterActive(k)) continue;
    const v = filterValue(k);
    const display = v === true ? 'present' : String(v);
    parts.push(
      `<span class="chip" data-key="${k}">
        <span class="chip-key">${escapeHtml(FILTER_LABEL[k])}</span>
        ${escapeHtml(display)}
        <button type="button" aria-label="remove">×</button>
      </span>`
    );
  }
  if (parts.length) {
    parts.push('<button type="button" class="chip chip-clear" id="clear-filters">Clear all</button>');
  }
  els.chips.innerHTML = parts.join('');
  els.chips.querySelectorAll('.chip[data-key] button').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.parentElement.dataset.key;
      setFilter(key, key === 'cveOnly' ? false : '');
      PAGE = 1;
      EXPANDED.clear();
      rerender();
    });
  });
  const clear = document.getElementById('clear-filters');
  if (clear) {
    clear.addEventListener('click', () => {
      for (const k of FILTER_KEYS) setFilter(k, k === 'cveOnly' ? false : '');
      PAGE = 1;
      EXPANDED.clear();
      rerender();
    });
  }
}

// ----------------------------- Table -------------------------------------

function renderTable(slice, start) {
  const rows = slice.map((e, i) => {
    const cves = (e.cve_ids || []);
    const cveCell = cves.length === 0 ? '' :
      cves.length === 1 ? `<code>${escapeHtml(cves[0])}</code>` :
      `<code>${escapeHtml(cves[0])}</code> +${cves.length - 1}`;
    const yearShard = e.year ? `incidents/${e.year}.html#${e.id.toLowerCase()}` : '';
    const idCell = yearShard
      ? `<a href="${yearShard}" onclick="event.stopPropagation()">${escapeHtml(e.id)}</a>`
      : escapeHtml(e.id);
    const llm = (e.owasp_llm || []).join(', ');
    const asi = (e.owasp_asi || []).join(', ');
    const expanded = EXPANDED.has(e.id);
    const cls = expanded ? ' class="expanded"' : '';
    const main = `<tr${cls} data-row="${e.id}">
      <td class="date">${escapeHtml(e.date || String(e.year || ''))}</td>
      <td class="id">${idCell}</td>
      <td class="title-cell">${escapeHtml(e.title)}</td>
      <td><span class="sev-badge sev-${escapeHtml(e.severity)}">${escapeHtml(e.severity || '')}</span></td>
      <td class="llm">${escapeHtml(llm)}</td>
      <td class="asi">${escapeHtml(asi)}</td>
      <td class="cves">${cveCell}</td>
    </tr>`;
    if (!expanded) return main;
    return main + renderDetail(e);
  }).join('');

  els.body.innerHTML = rows || '<tr><td colspan="7" class="status">No matches.</td></tr>';
  els.body.querySelectorAll('tr[data-row]').forEach(tr => {
    tr.addEventListener('click', () => {
      const id = tr.dataset.row;
      if (EXPANDED.has(id)) EXPANDED.delete(id); else EXPANDED.add(id);
      rerender();
    });
  });
}

function renderDetail(e) {
  const cves = (e.cve_ids || []).map(c => `<code>${escapeHtml(c)}</code>`).join(' ');
  const tags = (e.tags || []).map(t => `<span class="tag">${escapeHtml(t)}</span>`).join('');
  const refLink = e.primary_reference
    ? `<a href="${escapeHtml(e.primary_reference)}" rel="noopener" target="_blank">primary source ↗</a>`
    : '';
  const shardLink = e.year
    ? `<a href="incidents/${e.year}.html#${e.id.toLowerCase()}">full details ↗</a>`
    : '';
  return `<tr class="detail"><td colspan="7"><div class="detail-body">
    <p>${escapeHtml(e.description || 'No description.')}</p>
    <div class="detail-meta">
      ${e.affected ? `<span><strong>Affected:</strong> ${escapeHtml(e.affected)}</span>` : ''}
      ${e.attack_vector ? `<span><strong>Vector:</strong> <code>${escapeHtml(e.attack_vector)}</code></span>` : ''}
      ${e.corpus ? `<span><strong>Corpus:</strong> ${escapeHtml(e.corpus)}</span>` : ''}
      ${e.quality_tier ? `<span><strong>Quality:</strong> ${escapeHtml(e.quality_tier)}</span>` : ''}
      ${cves ? `<span><strong>CVEs:</strong> ${cves}</span>` : ''}
    </div>
    ${tags ? `<div class="detail-tags">${tags}</div>` : ''}
    <div class="detail-meta" style="margin-top:0.5rem">${refLink} ${shardLink}</div>
  </div></td></tr>`;
}

function renderPager(total) {
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const start = (PAGE - 1) * PAGE_SIZE;
  els.pager.innerHTML = `
    <button id="prev" ${PAGE === 1 ? 'disabled' : ''}>← Previous</button>
    <button id="next" ${PAGE >= totalPages ? 'disabled' : ''}>Next →</button>
    <span class="pager-info">Page ${fmtNum(PAGE)} of ${fmtNum(totalPages)}</span>
  `;
  document.getElementById('prev').onclick = () => { PAGE = Math.max(1, PAGE - 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0, behavior:'smooth'}); };
  document.getElementById('next').onclick = () => { PAGE = Math.min(totalPages, PAGE + 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0, behavior:'smooth'}); };
}

function updateSortIndicators() {
  els.table.querySelectorAll('th.sortable').forEach(th => {
    th.classList.remove('sort-asc','sort-desc');
    if (th.dataset.sort === SORT_BY) th.classList.add(SORT_DIR === 'asc' ? 'sort-asc' : 'sort-desc');
  });
}

function rerender() {
  FILTERED = DATA.filter(matches).sort(comparator());
  const totalPages = Math.max(1, Math.ceil(FILTERED.length / PAGE_SIZE));
  if (PAGE > totalPages) PAGE = 1;
  const start = (PAGE - 1) * PAGE_SIZE;
  const slice = FILTERED.slice(start, start + PAGE_SIZE);

  renderTable(slice, start);
  renderPager(FILTERED.length);
  renderChips();
  updateSortIndicators();

  const total = FILTERED.length;
  els.status.textContent = total === 0
    ? 'No incidents match your filters.'
    : `${fmtNum(total)} of ${fmtNum(DATA.length)} incidents — showing ${fmtNum(start + 1)}–${fmtNum(start + slice.length)}.`;

  writeFiltersToUrl();
}

// ----------------------------- Charts ------------------------------------

const CHART_ID = {
  year: 'chart-year', severity: 'chart-severity-stack',
  llm: 'chart-owasp-llm', asi: 'chart-owasp-asi',
  vectors: 'chart-vectors', vendors: 'chart-vendors',
};

const tooltipEl = document.createElement('div');
tooltipEl.className = 'chart-tooltip';
document.body.appendChild(tooltipEl);

function showTip(html, x, y) {
  tooltipEl.innerHTML = html;
  tooltipEl.style.left = x + 'px';
  tooltipEl.style.top = y + 'px';
  tooltipEl.classList.add('visible');
}
function hideTip() { tooltipEl.classList.remove('visible'); }

function svg(width, height, content) {
  return `<svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMinYMin meet">${content}</svg>`;
}

function topN(counts, n) {
  return Object.entries(counts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, n);
}

function colorForSeverity(sev) { return SEV_VARS[sev] || 'var(--accent)'; }

function renderBarChart(containerId, items, onClick, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!items.length) { el.innerHTML = '<p class="hint">No data.</p>'; return; }

  const W = opts.width || 640;
  const ROW_H = opts.rowH || 20;
  const M_LEFT = opts.leftPad || 170;
  const M_RIGHT = 56;
  const M_TOP = 6;
  const M_BOTTOM = 6;
  const chartW = W - M_LEFT - M_RIGHT;
  const H = M_TOP + M_BOTTOM + items.length * ROW_H;
  const maxV = Math.max(...items.map(i => i.value));

  const bars = items.map((it, i) => {
    const y = M_TOP + i * ROW_H + 4;
    const bw = (it.value / maxV) * chartW;
    const labelTrunc = it.label.length > 32 ? it.label.slice(0, 31) + '…' : it.label;
    const color = it.color || 'var(--bar)';
    const filterPayload = JSON.stringify(it.filter || null).replace(/"/g, '&quot;');
    return `
      <text class="row-label" x="${M_LEFT - 8}" y="${y + 13}" text-anchor="end">${escapeHtml(labelTrunc)}</text>
      <rect class="bar" x="${M_LEFT}" y="${y}" width="${bw}" height="${ROW_H - 8}"
        rx="3" fill="${color}"
        data-filter="${filterPayload}"
        data-tip="${escapeHtml(it.label)}: ${fmtNum(it.value)}"/>
      <text class="value-label" x="${M_LEFT + bw + 6}" y="${y + 13}">${fmtNum(it.value)}</text>
    `;
  }).join('');

  el.innerHTML = svg(W, H, bars);
  wireChart(el, onClick);
}

function renderColumnChart(containerId, items, onClick, opts = {}) {
  const el = document.getElementById(containerId);
  if (!el) return;
  if (!items.length) { el.innerHTML = '<p class="hint">No data.</p>'; return; }
  const W = opts.width || 720;
  const H = opts.height || 200;
  const M_LEFT = 40, M_RIGHT = 10, M_TOP = 10, M_BOTTOM = 26;
  const chartW = W - M_LEFT - M_RIGHT;
  const chartH = H - M_TOP - M_BOTTOM;
  const maxV = Math.max(...items.map(i => i.value));
  const barW = chartW / items.length;

  const grid = [];
  for (let g = 0; g <= 4; g++) {
    const y = M_TOP + chartH * g / 4;
    const v = Math.round(maxV * (4 - g) / 4);
    grid.push(`<line class="gridline" x1="${M_LEFT}" y1="${y}" x2="${W - M_RIGHT}" y2="${y}"/>`);
    grid.push(`<text class="tick" x="${M_LEFT - 6}" y="${y + 3}" text-anchor="end">${fmtNum(v)}</text>`);
  }
  const bars = items.map((it, i) => {
    const bw = barW * 0.78;
    const x = M_LEFT + i * barW + (barW - bw) / 2;
    const bh = (it.value / maxV) * chartH;
    const y = M_TOP + chartH - bh;
    const filterPayload = JSON.stringify(it.filter || null).replace(/"/g, '&quot;');
    const labelEvery = items.length > 18 ? 2 : 1;
    const showLabel = (i === 0) || (i === items.length - 1) || (i % labelEvery === 0);
    return `
      <rect class="bar" x="${x}" y="${y}" width="${bw}" height="${bh}" rx="2"
        fill="${it.color || 'var(--bar)'}"
        data-filter="${filterPayload}"
        data-tip="${escapeHtml(it.label)}: ${fmtNum(it.value)}"/>
      ${showLabel ? `<text class="tick" x="${x + bw / 2}" y="${H - M_BOTTOM + 14}" text-anchor="middle">${escapeHtml(it.label)}</text>` : ''}
    `;
  }).join('');

  el.innerHTML = svg(W, H, grid.join('') + bars);
  wireChart(el, onClick);
}

function renderStackedColumnChart(containerId, years, byYearBySeverity, onClick) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const sevOrder = ['Critical','High','Medium','Low','Info'];
  const W = 720, H = 200;
  const M_LEFT = 40, M_RIGHT = 100, M_TOP = 10, M_BOTTOM = 26;
  const chartW = W - M_LEFT - M_RIGHT;
  const chartH = H - M_TOP - M_BOTTOM;
  const totals = years.map(y => sevOrder.reduce((a,s) => a + (byYearBySeverity[y][s] || 0), 0));
  const maxV = Math.max(...totals) || 1;
  const barW = chartW / years.length;

  const grid = [];
  for (let g = 0; g <= 4; g++) {
    const y = M_TOP + chartH * g / 4;
    const v = Math.round(maxV * (4 - g) / 4);
    grid.push(`<line class="gridline" x1="${M_LEFT}" y1="${y}" x2="${W - M_RIGHT}" y2="${y}"/>`);
    grid.push(`<text class="tick" x="${M_LEFT - 6}" y="${y + 3}" text-anchor="end">${fmtNum(v)}</text>`);
  }
  const bars = years.map((yr, i) => {
    const bw = barW * 0.78;
    const x = M_LEFT + i * barW + (barW - bw) / 2;
    let cumulative = 0;
    const segs = [];
    for (const sev of sevOrder) {
      const c = byYearBySeverity[yr][sev] || 0;
      if (!c) continue;
      const bh = (c / maxV) * chartH;
      const segY = M_TOP + chartH - cumulative - bh;
      segs.push(`<rect class="bar" x="${x}" y="${segY}" width="${bw}" height="${bh}"
        fill="${colorForSeverity(sev)}"
        data-filter='${JSON.stringify({ year: String(yr), severity: sev })}'
        data-tip="${escapeHtml(String(yr))} · ${sev}: ${fmtNum(c)}"/>`);
      cumulative += bh;
    }
    const labelEvery = years.length > 18 ? 2 : 1;
    const showLabel = (i === 0) || (i === years.length - 1) || (i % labelEvery === 0);
    return segs.join('') + (showLabel
      ? `<text class="tick" x="${x + bw / 2}" y="${H - M_BOTTOM + 14}" text-anchor="middle">${yr}</text>`
      : '');
  }).join('');
  // Legend
  const legend = sevOrder.map((sev, i) => {
    const ly = M_TOP + i * 18;
    const lx = W - M_RIGHT + 6;
    return `<rect x="${lx}" y="${ly}" width="11" height="11" fill="${colorForSeverity(sev)}"/>
      <text class="row-label" x="${lx + 16}" y="${ly + 9}">${sev}</text>`;
  }).join('');

  el.innerHTML = svg(W, H, grid.join('') + bars + legend);
  wireChart(el, onClick);
}

function wireChart(el, onClick) {
  const rect = () => el.getBoundingClientRect();
  el.querySelectorAll('.bar').forEach(bar => {
    bar.addEventListener('mousemove', ev => {
      const r = rect();
      showTip(bar.dataset.tip, ev.clientX, ev.clientY);
    });
    bar.addEventListener('mouseleave', hideTip);
    bar.addEventListener('click', () => {
      hideTip();
      try {
        const filt = JSON.parse(bar.dataset.filter || 'null');
        if (filt && onClick) onClick(filt);
      } catch (_) { /* ignore */ }
    });
  });
}

function applyChartFilter(patch) {
  // Apply chart-click filters on top of whatever is already set.
  for (const [k, v] of Object.entries(patch)) {
    if (k === 'cveOnly') els.cveOnly.checked = !!v;
    else if (els[k]) els[k].value = v;
  }
  PAGE = 1;
  EXPANDED.clear();
  rerender();
  document.querySelector('.filters-section').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function renderAllCharts() {
  // Per-year column chart
  const yearCounts = {};
  for (const e of DATA) if (e.year) yearCounts[e.year] = (yearCounts[e.year] || 0) + 1;
  const years = Object.keys(yearCounts).map(Number).sort((a,b) => a - b);
  const yearItems = years.map(y => ({ label: String(y), value: yearCounts[y], filter: { year: String(y) } }));
  renderColumnChart(CHART_ID.year, yearItems, applyChartFilter);

  // Severity composition over time (last 16 years that have data)
  const sevYears = years.slice(-16);
  const byYearBySev = {};
  for (const y of sevYears) byYearBySev[y] = { Critical: 0, High: 0, Medium: 0, Low: 0, Info: 0 };
  for (const e of DATA) {
    if (byYearBySev[e.year]) byYearBySev[e.year][e.severity || 'Medium']++;
  }
  renderStackedColumnChart(CHART_ID.severity, sevYears, byYearBySev, applyChartFilter);

  // OWASP LLM bar chart
  const llmCounts = {};
  Object.keys(LLM_NAMES).forEach(k => llmCounts[k] = 0);
  for (const e of DATA) for (const c of e.owasp_llm || []) llmCounts[c] = (llmCounts[c] || 0) + 1;
  const llmItems = Object.keys(LLM_NAMES).map(k => ({
    label: `${k} · ${LLM_NAMES[k]}`, value: llmCounts[k] || 0, filter: { llm: k },
  })).sort((a,b) => b.value - a.value);
  renderBarChart(CHART_ID.llm, llmItems, applyChartFilter, { rowH: 24 });

  // OWASP ASI bar chart
  const asiCounts = {};
  Object.keys(ASI_NAMES).forEach(k => asiCounts[k] = 0);
  for (const e of DATA) for (const c of e.owasp_asi || []) asiCounts[c] = (asiCounts[c] || 0) + 1;
  const asiItems = Object.keys(ASI_NAMES).map(k => ({
    label: `${k} · ${ASI_NAMES[k]}`, value: asiCounts[k] || 0, filter: { asi: k },
  })).sort((a,b) => b.value - a.value);
  renderBarChart(CHART_ID.asi, asiItems, applyChartFilter, { rowH: 24 });

  // Top attack vectors
  const vecCounts = {};
  for (const e of DATA) {
    const v = e.attack_vector || 'other';
    vecCounts[v] = (vecCounts[v] || 0) + 1;
  }
  const vecItems = topN(vecCounts, 12).map(([k, v]) => ({
    label: k, value: v, filter: { vector: k },
  }));
  renderBarChart(CHART_ID.vectors, vecItems, applyChartFilter, { rowH: 22, leftPad: 170 });

  // Top affected vendors / products (extracted from the `affected` field)
  const vendorCounts = {};
  for (const e of DATA) {
    const text = (e.affected || '').trim();
    if (!text) continue;
    // Pull out the first comma-separated chunk and normalise common noise.
    const first = text.split(/[,;|]/)[0].trim();
    if (!first || first.length > 60) continue;
    const key = first.replace(/\s+v?\d+(\.\d+)*$/, '').trim();
    vendorCounts[key] = (vendorCounts[key] || 0) + 1;
  }
  const vendorItems = topN(vendorCounts, 12).map(([k, v]) => ({
    label: k, value: v, filter: { q: k },
  }));
  renderBarChart(CHART_ID.vendors, vendorItems, applyChartFilter, { rowH: 22, leftPad: 200 });
}

// ----------------------------- Bootstrap ---------------------------------

function populateOptions(select, values) {
  const frag = document.createDocumentFragment();
  for (const v of values) {
    const opt = document.createElement('option');
    opt.value = v;
    opt.textContent = v;
    frag.appendChild(opt);
  }
  select.appendChild(frag);
}

async function init() {
  try {
    const r = await fetch('data/incidents.min.json');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const payload = await r.json();
    DATA = payload.incidents || [];

    populateOptions(els.year,
      uniqSorted(DATA.map(e => String(e.year))).filter(Boolean).reverse());
    populateOptions(els.llm,
      uniqSorted(DATA.flatMap(e => e.owasp_llm || [])));
    populateOptions(els.asi,
      uniqSorted(DATA.flatMap(e => e.owasp_asi || [])));
    populateOptions(els.vector,
      uniqSorted(DATA.map(e => e.attack_vector).filter(Boolean)));

    // Populate page-size selector (URL state may already have set PAGE_SIZE)
    for (const n of PAGE_SIZE_OPTIONS) {
      const opt = document.createElement('option');
      opt.value = String(n);
      opt.textContent = n.toLocaleString();
      els.pageSize.appendChild(opt);
    }

    readFiltersFromUrl();
    els.pageSize.value = String(PAGE_SIZE);
    els.pageSize.addEventListener('change', () => {
      const n = parseInt(els.pageSize.value, 10);
      if (PAGE_SIZE_OPTIONS.includes(n)) {
        PAGE_SIZE = n;
        PAGE = 1;
        rerender();
      }
    });

    // Back-to-top FAB
    if (els.backToTop) {
      window.addEventListener('scroll', () => {
        els.backToTop.classList.toggle('visible', window.scrollY > 600);
      }, { passive: true });
      els.backToTop.addEventListener('click', (ev) => {
        ev.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
      });
    }

    renderStats(DATA);
    renderAllCharts();

    // Filter change handlers
    for (const k of FILTER_KEYS) {
      const el = els[k === 'cveOnly' ? 'cveOnly' : k];
      if (!el) continue;
      const ev = (el.type === 'checkbox' || el.tagName === 'SELECT') ? 'change' : 'input';
      el.addEventListener(ev, () => {
        PAGE = 1;
        EXPANDED.clear();
        rerender();
      });
    }
    // Sortable headers
    els.table.querySelectorAll('th.sortable').forEach(th => {
      th.addEventListener('click', () => {
        const next = th.dataset.sort;
        if (SORT_BY === next) SORT_DIR = SORT_DIR === 'asc' ? 'desc' : 'asc';
        else { SORT_BY = next; SORT_DIR = next === 'severity' ? 'desc' : 'desc'; }
        rerender();
      });
    });

    els.meta.textContent =
      `Dataset v${payload.version || '?'} · generated ${payload.generated || '?'} · ${fmtNum(DATA.length)} incidents`;

    rerender();
  } catch (err) {
    els.status.textContent = 'Failed to load dataset: ' + err.message;
    console.error(err);
  }
}

init();
