// Client-side filter/search for the incident dataset.
// Loads data/incidents.min.json once, then filters/paginates in memory.

const PAGE_SIZE = 100;

const els = {
  q:        document.getElementById('q'),
  year:     document.getElementById('year'),
  severity: document.getElementById('severity'),
  llm:      document.getElementById('llm'),
  asi:      document.getElementById('asi'),
  vector:   document.getElementById('vector'),
  corpus:   document.getElementById('corpus'),
  quality:  document.getElementById('quality'),
  cveOnly:  document.getElementById('cve_only'),
  status:   document.getElementById('status'),
  body:     document.querySelector('#incidents tbody'),
  pager:    document.getElementById('pager'),
  meta:     document.getElementById('dataset-meta'),
};

let DATA = [];
let FILTERED = [];
let PAGE = 1;

function escapeHtml(s) {
  return (s || '').replace(/[&<>"']/g, c => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
  ));
}

function uniqSorted(arr) {
  return Array.from(new Set(arr)).sort();
}

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

function readFiltersFromUrl() {
  const p = new URLSearchParams(location.hash.slice(1) || location.search.slice(1));
  for (const [k, el] of Object.entries(els)) {
    if (!('value' in el)) continue;
    if (el.type === 'checkbox') {
      if (p.get(k) === '1') el.checked = true;
    } else if (p.has(k)) {
      el.value = p.get(k);
    }
  }
  if (p.has('page')) PAGE = Math.max(1, parseInt(p.get('page'), 10) || 1);
}

function writeFiltersToUrl() {
  const p = new URLSearchParams();
  if (els.q.value)        p.set('q', els.q.value);
  if (els.year.value)     p.set('year', els.year.value);
  if (els.severity.value) p.set('severity', els.severity.value);
  if (els.llm.value)      p.set('llm', els.llm.value);
  if (els.asi.value)      p.set('asi', els.asi.value);
  if (els.vector.value)   p.set('vector', els.vector.value);
  if (els.corpus.value)   p.set('corpus', els.corpus.value);
  if (els.quality.value)  p.set('quality', els.quality.value);
  if (els.cveOnly.checked) p.set('cve_only', '1');
  if (PAGE > 1)           p.set('page', String(PAGE));
  const qs = p.toString();
  history.replaceState(null, '', qs ? '#' + qs : location.pathname);
}

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
      (e.cve_ids || []).join(' ') + ' ' +
      (e.owasp_llm || []).join(' ') + ' ' + (e.owasp_asi || []).join(' ') + ' ' +
      (e.primary_reference || '')
    ).toLowerCase();
    if (!hay.includes(q)) return false;
  }
  return true;
}

function dateScore(e) {
  // Newest first; pad with -00 so YYYY-MM sorts after YYYY-MM-DD of same year.
  const d = (e.date || String(e.year || 0)).padEnd(10, '0');
  return d;
}

function rerender() {
  FILTERED = DATA.filter(matches);
  FILTERED.sort((a, b) => dateScore(b).localeCompare(dateScore(a)));
  if (PAGE > Math.ceil(FILTERED.length / PAGE_SIZE)) PAGE = 1;

  const start = (PAGE - 1) * PAGE_SIZE;
  const slice = FILTERED.slice(start, start + PAGE_SIZE);

  const rows = slice.map(e => {
    const cves = (e.cve_ids || []);
    const cveCell = cves.length === 0 ? '' :
      cves.length <= 2 ? cves.map(c => `<code>${escapeHtml(c)}</code>`).join(', ') :
      `<code>${escapeHtml(cves[0])}</code> (+${cves.length - 1})`;
    const yearShard = e.year ? `incidents/${e.year}.html#${e.id.toLowerCase()}` : '';
    const idCell = yearShard
      ? `<a href="${yearShard}"><code>${escapeHtml(e.id)}</code></a>`
      : `<code>${escapeHtml(e.id)}</code>`;
    const llm = (e.owasp_llm || []).join(', ');
    const asi = (e.owasp_asi || []).join(', ');
    const link = e.primary_reference
      ? `<a href="${escapeHtml(e.primary_reference)}" rel="noopener" target="_blank">${escapeHtml(e.title)}</a>`
      : escapeHtml(e.title);
    return `<tr>
      <td class="date">${escapeHtml(e.date || String(e.year || ''))}</td>
      <td class="id">${idCell}</td>
      <td>${link}</td>
      <td><span class="sev sev-${escapeHtml(e.severity || '')}">${escapeHtml(e.severity || '')}</span></td>
      <td class="llm">${escapeHtml(llm)}</td>
      <td class="asi">${escapeHtml(asi)}</td>
      <td class="cves">${cveCell}</td>
    </tr>`;
  }).join('');

  els.body.innerHTML = rows || '<tr><td colspan="7" class="status">No matches.</td></tr>';

  const total = FILTERED.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const shown = slice.length;
  els.status.textContent = total === 0
    ? '0 incidents match.'
    : `${total.toLocaleString()} incidents match — showing ${start + 1}–${start + shown}.`;
  els.pager.innerHTML =
    `<button id="prev" ${PAGE === 1 ? 'disabled' : ''}>← prev</button> ` +
    `page ${PAGE} of ${totalPages.toLocaleString()} ` +
    `<button id="next" ${PAGE >= totalPages ? 'disabled' : ''}>next →</button>`;
  document.getElementById('prev').onclick = () => { PAGE = Math.max(1, PAGE - 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0}); };
  document.getElementById('next').onclick = () => { PAGE = Math.min(totalPages, PAGE + 1); writeFiltersToUrl(); rerender(); window.scrollTo({top: 0}); };

  writeFiltersToUrl();
}

async function init() {
  try {
    const r = await fetch('data/incidents.min.json');
    if (!r.ok) throw new Error('HTTP ' + r.status);
    const payload = await r.json();
    DATA = payload.incidents || [];
    els.meta.textContent =
      `${DATA.length.toLocaleString()} incidents · v${payload.version || '?'} · generated ${payload.generated || '?'}`;

    populateOptions(els.year,
      uniqSorted(DATA.map(e => String(e.year))).reverse());
    populateOptions(els.llm,
      uniqSorted(DATA.flatMap(e => e.owasp_llm || [])));
    populateOptions(els.asi,
      uniqSorted(DATA.flatMap(e => e.owasp_asi || [])));
    populateOptions(els.vector,
      uniqSorted(DATA.map(e => e.attack_vector).filter(Boolean)));

    readFiltersFromUrl();

    for (const el of Object.values(els)) {
      if (el && ('addEventListener' in el) && el.tagName) {
        const ev = (el.type === 'checkbox' || el.tagName === 'SELECT') ? 'change' : 'input';
        el.addEventListener(ev, () => { PAGE = 1; rerender(); });
      }
    }

    rerender();
  } catch (err) {
    els.status.textContent = 'Failed to load dataset: ' + err.message;
    els.meta.textContent = '';
    console.error(err);
  }
}

init();
