# Changelog

All notable changes to the dataset and tooling are recorded here.
The dataset uses [SemVer](https://semver.org/) — major bumps for breaking
schema or ID changes, minor bumps for additive schema fields or large
ingest expansions, patch bumps for routine refreshes and bug fixes.

## [2.8.0] — 2026-07-13

Data-quality release. Net composition 12,770 → 12,986 (+241 from the weekly
source refresh, −25 from removing non-GenAI scope contamination); landmark
1,858 → 1,865.

### Removed (scope precision)
- **25 non-GenAI CVE-bridge buckets excluded** per INCLUSION.md — entries where
  a weak key (shared reference URL / templated title) had collapsed dozens to
  hundreds of *unrelated, non-GenAI* CVE advisories into one incident:
  `dexidp/dex` (708 CVEs, was landmark), Juju (93, was landmark), ~11 ×
  Magento/Adobe Commerce, KaiOS, Google Chrome, four Jenkins plugins, Liferay,
  Mattermost, MantisBT, jackson-dataformat-toml, Firefox. Decisions and
  per-bucket rationale in `data/issue88_remediation.json`; each removal carries
  an `out-of-scope` deprecation so citations still resolve. The excluded
  buckets' source keys are suppressed **before** dedupe (enumerated statically),
  so the removal is idempotent and cannot resurrect on rebuild. (#88, #95)

### Added (labels)
- **55 landmark-tier `reversibility_class` / `discovery_method` labels**
  populated across two evidence-gated curation batches, each label citing
  closing-action or discovery-channel evidence in `data/curation_overrides.json`.
  (#91, #92)

### Changed
- **Weekly source refresh** — AIRI Navigator, AIAAIC, OECD AI Incidents Monitor
  (+241 incidents net; routine dedupe deprecations recorded). (#93)

### Tooling
- **`scripts/audit_cve_bridge.py`** — reproducible precision audit of the
  grandfathered disjoint-CVE weak-key merges (#36), classifying each multi-CVE
  incident. It surfaced the scope-contamination removed above and characterises
  the remaining GenAI over-merges (a ~542-advisory recovery) as the v3.0 one-way
  split re-baseline tracked in #88. (#94)

## [2.7.0] — 2026-07-03

Data-quality and interoperability release. Incident composition is unchanged
from v2.6.0 (12,770 entries, 0 added / 0 removed) — the work is in
classification precision, threat-intel mapping freshness, and the first
populated landmark-tier label.

### Changed (interoperability)
- **MITRE ATLAS mapping refreshed to content v2026.06** (`mappings/mitre_atlas.json`;
  ATLAS froze the old `dist/ATLAS.yaml` at 5.6.0, so `scripts/ingest_external.py`
  now parses the pinned `dist/v6/ATLAS-2026.06.yaml`). Adds techniques
  `AML.T0113`, `AML.T0114`, `AML.T0091.001`; no renames or removals for existing
  IDs. (#86)

### Changed (classification precision)
- **844 `attack_vector: other` entries reclassified from unanimous CWE evidence**
  (`other` 4,589 → 3,745). A new `mappings/cwe_attack_vector.json` maps 35
  unambiguous CWE classes to 10 vectors, applied only when text classification
  left an entry at `other` **and** every mappable CWE on it agrees (unanimity
  rule — mixed signals stay `other`). A 50-entry random sample reviewed 50/50
  defensible. (#89)

### Added (first labels)
- **First `reversibility_class` label populated** — INC-03152 (the Replit
  agent production-database deletion) classified `external-reversible`, with
  closing-action evidence in the curation override. The boundary rubric
  (realized-outcome, "who had to act?") is now documented in `TAXONOMIES.md`.
  First community-contributed label (proposal #74). (#85)

### Fixed
- **Dedupe no longer over-merges distinct-CVE incidents** on a full CVE-feed
  refresh — weak keys (shared reference URL, templated title) can no longer
  bridge two entries with disjoint CVE sets, including transitive claims
  (the shape that collapsed six distinct MLflow CVEs into one). Historical
  merges are grandfathered so committed data is byte-stable. (#87, #36)

### Docs
- Datasheet/methods-paper truth-pass: incident count corrected, the two v2.6.0
  landmark labels and the VERIS crosswalk documented, TAXII/MISP distribution
  and `veris:*` machinetags surfaced; Hugging Face `size_categories` now
  derived from the record count. (#84)

## [2.6.0] — 2026-07-02

### Added (Schema — landmark-tier labels)
- **`reversibility_class`** — optional enum (`read-only` / `reversible` /
  `external-reversible` / `irreversible`) classifying the reversibility of the
  action that closed the incident. Landmark-tier only, evidence-gated via
  `data/curation_overrides.json`, enforced by a new validate.py integrity
  invariant. Community proposal #74 (lineage: OWASP AISVS C09-02). (#76)
- **`discovery_method`** — optional enum (`security-researcher`,
  `actor-disclosure`, `customer-report`, `media-report`, `law-enforcement`,
  `internal-monitoring`, `internal-report`, `vendor-monitoring`, `other`)
  recording how the incident was first surfaced; same landmark gate (the
  validate.py invariant now covers both label fields). Lineage: VERIS 1.4.1
  `discovery_method`, flattened and AI-adapted. (#81)

### Added (Integrations)
- **VERIS 1.4.1 crosswalk** — hand-curated `mappings/veris.json` (35
  attack_vectors → 48 enum entries, mechanically verified and adversarially
  reviewed against official VERIS definitions), emitted as `veris:*`
  machinetags in the MISP feed alongside `genai-incidents:*` /
  `mitre-atlas:*`. Opens the dataset to VERIS consumers (DBIR contributor
  pipeline, cyber insurers, FAIR-style risk quantification) with zero schema
  surface. (#79)

### Data
- 11,658 → **12,770 incidents**: weekly auto-refresh (#75), OpenClaw
  ingest-coverage fix (#77 — `openclaw` added to the NVD keyword list,
  AI-context tokens, npm ecosystem allowlist and strict malware gate after
  CVE-2026-44112 was missed on wording alone), and a CVE-enrichment run
  (#78: +788 incidents including 276 previously-invisible OpenClaw
  advisories and CVE-2026-44112 itself as INC-14014; +936 CVEs; all 42
  removals recorded as merge deprecations).

### Notes
- Both new fields are additive and optional — absence means **unassessed**,
  never a claim. No existing records were modified for the schema change.
- Hardcoded marketing lower bound updated "11,500+" → "12,500+" (canonical
  count remains `data/stats.json`).

## [2.5.0] — 2026-06-11

### Added (Coverage — linkage graph, #30)
- **`capec_ids`** on every CWE-bearing entry — MITRE CAPEC attack patterns
  derived from `cwe_ids` via an authoritative CWE→CAPEC map
  (`mappings/cwe_capec.json`, built by `scripts/build_cwe_capec.py` from MITRE's
  CAPEC corpus). The complete, uncapped union; ~4,433 entries.
- **`purl`** on every entry with a structured `affected` identifier — Package-URLs
  (`pkg:type/namespace/name`) for entity resolution of affected packages
  (`pip/foo`→`pkg:pypi/foo`, `maven/g:a`→`pkg:maven/g/a`, scoped npm `%40`-encoded);
  ~3,620 entries.

### Added (Adoption — integrations, #33)
- **Static TAXII 2.1 endpoint** at `docs/taxii2/` (discovery, API root,
  collections, objects + manifest envelopes) — a read-only mirror of the STIX
  collection, generated at Pages deploy. `make taxii`.
- **MISP feed** at `docs/misp/` (manifest + one Event per year + `hashes.csv`)
  with `genai-incidents:*` / `mitre-atlas:technique` attribute tags. Subscribe a
  MISP instance to the feed URL. `make misp`.

### Notes
- Schema gains `capec_ids` + `purl` (additive). Both fields are derived in the
  provenance pass, kept out of the content snapshot, and added to the full
  `data/incidents.json` only (the slim site payload is unchanged). Incident
  composition is identical to v2.4.0 (0 added / 0 removed).

## [2.4.0] — 2026-06-11

### Added (Trust foundation)
- **[INCLUSION.md](INCLUSION.md)** — explicit scope policy: every entry must
  satisfy AI-nexus + security/safety-relevance + evidence gates.
- **Provenance fields** on every entry: `confidence` (transparent
  high/medium/low rule), `source_count`, `source_status` (active/retained),
  `first_seen`/`last_seen`.
- **Corrections process** — `data_correction` / `scope_dispute` issue
  templates and a public [CORRECTIONS.md](CORRECTIONS.md) log.

### Changed (enforced quality)
- CI now enforces two cross-entry invariants on every build: every entry has
  a resolvable primary source, and no out-of-scope malicious-package entry
  may survive (the v2.3.1 scope-purge is now a hard gate).

## [2.3.1] — 2026-06-10

### Fixed
- **Data precision:** the v2.3.0 GHSA MALWARE pass matched generic npm
  malware on weak substrings (`ai` in `chai-mocks`, `prompt` in
  `sudo-prompt`, `nemo` in `nemo-reporter`) and a loose description-token
  fallback — ~71% of the 465 malicious-package entries were not AI-related.
  MALWARE advisories now require a **strong, segment-boundary** match
  against a curated AI package allowlist (no weak substrings, no
  description fallback); the noise entries are dropped.

### Security / docs
- Documented that `title`/`description`/`affected`/`impact`/`mitigations`
  are **untrusted verbatim free text** (may contain raw HTML/exploit
  payloads); consumers must escape before rendering (schema + DATASHEET).
- Light/dark theme now also applies to the year-shard and 404 pages.

## [2.3.0] — 2026-06-10

### Added

- **9,209 → 12,062 incidents.** Deeper GitHub Security Advisory ingest
  (paged back to the 2022 floor) plus a new **MALWARE-classification
  pass** that surfaced **465 malicious-package** advisories (AI-ecosystem
  typosquats / trojaned deps), and ~31 new NVD keywords + OSV packages
  for high-CVE-count AI products (Langflow, LiteLLM, LangGraph, NeMo,
  DeepSpeed, vLLM, llama.cpp, …).
- **CISA KEV enrichment**: `exploited_in_wild` + `kev_date_added` flag
  incidents whose CVEs are in the Known Exploited Vulnerabilities catalog
  (deterministic, from a committed snapshot refreshed by the workflows).
- New `exploited_in_wild` / `kev_date_added` schema fields. README now
  carries a live incident-count badge fed by `data/stats.json`.

### Security

- **Fixed a stored XSS** on the generated incident pages: advisory
  descriptions containing raw HTML (e.g. `<img src=x onerror=...>`)
  executed when rendered as Markdown. All incident free-text is now
  HTML-escaped and link schemes are restricted to http(s)/mailto; a CI
  guard fails the build if raw HTML reaches a shard.

### Changed

- **Site rebuilt to scale**: custom Jekyll build (the managed builder
  stopped finishing at 12k pages) and the per-incident standalone pages
  were retired in favour of self-anchored year shards + client-side
  detail. Added a **light/dark theme** toggle.
- CI hardened: cross-entry integrity invariants (no CVE/source held by
  two live entries; deprecations resolve) and UTC-stable date stamps.

## [2.2.0] — 2026-06-10

### Added

- **CVE enrichment**: `cwe_ids` populated on 2,411 and `cvss_vector` on
  2,094 of the 2,493 CVE-bearing incidents (previously 0). New
  manually-dispatched `CVE enrichment` workflow re-pulls NVD + GHSA +
  OSV on CI (supports the `NVD_API_KEY` secret).
- **+1,361 incidents** from the first working GHSA ingest — a Windows
  encoding bug (`text=True` decoding `gh api` output as cp1252) had
  silently yielded 0 advisories; now UTF-8. Plus the weekly refresh
  (+427) and 9 hand-curated crosswalk-watch CVEs. Total: 7,725 → 9,209.

### Fixed

- **Core dedupe tombstone bug**: stale index pointers could merge new
  content into already-absorbed (tombstoned) entries, silently dropping
  it. Dedupe now resolves every hit to the live absorber and reindexes
  until stable; recovered 24 previously-lost incidents (+39 CVEs,
  +210 source_ids). See
  `docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md`.
- **UTC date stamps**: `added`/`updated`/`generated` now derive from
  the UTC calendar (`utc_today()`), so local builds behind UTC can't
  drift against CI.
- Removed CNA-rejected `CVE-2026-35020`; removed the phantom MITRE
  ATLAS technique `AML.T0039`.

### CI

- Validate workflow runs a Python 3.12/3.13 matrix with least-privilege
  permissions; publish/PR actions pinned to release commit SHAs
  (`gh-action-pypi-publish` v1.14.0, `create-pull-request` v8.1.1);
  weekly refresh reports per-source ingest outcomes and aborts if all
  sources fail.

## [2.1.0] — 2026-06-03

### Added

- Hugging Face dataset publishing (`emmanuelgjr/genai-incidents`) with
  enriched dataset card; STIX 2.1 export; retain-on-drop (incidents are
  never silently lost when a source drops them); red-team benchmark
  catalogue; MITRE ATLAS tactic backfill; CWE/CVSS-vector capture in the
  CVE ingester; GitHub Pages site redesign ("amber threat console").

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
