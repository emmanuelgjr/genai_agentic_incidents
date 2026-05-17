# Changelog

All notable changes to the dataset and tooling are recorded here.
The dataset uses [SemVer](https://semver.org/) — major bumps for breaking
schema or ID changes, minor bumps for additive schema fields or large
ingest expansions, patch bumps for routine refreshes and bug fixes.

## [2.0.0] — 2026-05-16

### Breaking

- `INC-*` IDs are now **stable across rebuilds**. Previously they were
  reassigned on every merge based on year+title order; citing
  `INC-00139` was unsafe because tomorrow's `INC-00139` could refer to
  a different incident. New rule: once assigned, an ID never moves. If
  an entry is merged away, the old ID is recorded in
  `data/id_deprecations.json` pointing at the surviving entry.
- Schema field `version` in `data/incidents.json` bumped to `2.0.0`.

### Added

- New schema fields: `quality_tier` (`curated` / `reviewed` / `auto`),
  `corpus` (`security` / `ai-harm`), `cwe_ids`, `cvss_vector`,
  `aiid_id`, `disclosure_date`.
- `CITATION.cff` for academic citation; `.zenodo.json` for DOI minting
  on GitHub releases.
- New ingest sources: AIAAIC public spreadsheet (~1,500 net-new entries
  after dedupe), OECD AI Incidents Monitor full corpus (~2,900 net-new
  after dedupe + security filter), MIT FutureTech AI Risk Navigator
  (~400 net-new + authoritative AIID dates for 1,020 existing entries).
- `make ingest-all`, `make test` targets.
- `tests/` with 33 unit tests covering dedup, classifiers, renderer.
- `docs/incidents/<year>.md` shards so the top-level `INCIDENTS.md`
  stays under GitHub's render budget.

### Fixed

- **Dedupe correctness** — three independent bugs caused the same
  incident to live as multiple `INC-*` records: (a) the dedup indices
  weren't refreshed after a merge, so absorbed CVEs missed the target
  on subsequent passes; (b) when an absorbed key already mapped to a
  different entry, the two should have transitively merged but didn't;
  (c) `AIID-N-OECD` (from the legacy bridge file) and `AIID-N` (from
  the fresh AIID scrape and OECD AIM) referenced the same incident but
  never matched. All three fixed; **0 duplicate CVEs, source IDs, or
  reference URLs** across 7,714 entries.
- **AIID year-fallback bug** — pages without machine-readable dates
  were getting the *maximum* year mentioned in title/description, so
  references to "the 2027 election" produced incidents dated 2027.
  Now: minimum plausible year, capped at the current year. 1,020
  AIID entries got authoritative dates via the AIRI bridge.
- **Deterministic builds** — `updated`/`generated` no longer stamped
  with `today` on every run; CI drift checks now stable.
- **Severity normalisation** — NVD's literal string `"None"` no longer
  fails schema validation.
- **CVE title cleanup** — generic NVD descriptions like _"A flaw has
  been found in MLflow…"_ and _"Gradio is an open-source Python
  package…"_ are rewritten to _"\<Product\> — \<Vector\> (CVE-…)"_.

### Changed

- `INCIDENTS.md` restructured: single unified table, newest-first.
  Per-incident detail blocks moved to year shards.
- README documents the full toolchain, sources, and reproducibility
  contract.

## [1.0.0] — 2026-05-13

Initial public release. ~3,200 incidents covering 2015–2026, mapped
across OWASP LLM Top 10 (2025), OWASP Agentic Top 10, NIST AI RMF, and
MITRE ATLAS.
