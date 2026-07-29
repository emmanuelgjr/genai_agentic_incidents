# Data dictionary

Every incident in [`data/incidents.json`](../data/incidents.json) follows
[`schema/incident.schema.json`](../schema/incident.schema.json). Fields below; **R** = required.

## Identity & provenance
| Field | Type | Notes |
|---|---|---|
| `id` **R** | string | Stable incident id, `INC-#####`. Never reused; merged-away ids are recorded in [`data/id_deprecations.json`](../data/id_deprecations.json) and resolvable via the package's `resolve_id()`. |
| `source_ids` | string[] | Upstream ids this entry was consolidated from (e.g. `AIID-1234`, `CVE-2026-…`, `ATLAS-AML.CS0001`, `AIAAIC2257`). |
| `quality_tier` | enum | Vetting level: `curated` (hand-written/maintainer), `reviewed` (maintained catalogue, NVD-scored CVE, hand-picked, or human/assisted review), `auto` (bulk-ingested). Filter on this to control trust. |
| `tier` | enum | **landmark** (curated, AIID-linked real-world, ai-harm, or real-world-category — the notable headline set) vs **feed** (the comprehensive CVE/GHSA/OSV stream). Cite the landmark count for headlines. |
| `confidence` | enum | Rule-derived, not opinion: **high** = `curated`/`reviewed`, OR 2+ sources with a CVE; **medium** = 2+ sources, OR has a CVE/CVSS; **low** = a single `auto` source, no CVE. |
| `source_count` | int | Number of distinct upstream sources corroborating the entry. |
| `source_status` | enum | **Emission status, not liveness status.** `active` (still emitted by a source this build) or `retained` (carried from a prior build after all its sources dropped it — see retain-on-drop). **`active` does not mean the upstream source is still alive or still refreshing successfully** — it means only that the entry appeared in this build's inputs, and a committed ingest snapshot re-emits its rows every build whether or not the source that produced them still exists. Freshness is a separate axis: see `source_freshness` and [Source freshness](#source-freshness) below. The two are independent — an entry can be active-and-fresh, active-and-stale, retained-and-fresh, or retained-and-stale. |
| `source_freshness` | object | Present when at least one source that contributed to the entry has **stopped refreshing successfully**: `{status: "stale", as_of: YYYY-MM-DD, sources: [<source key>…]}`. Derived — inherited by reference from [`data/source_freshness.json`](../data/source_freshness.json), never authored per row; each `sources` element is a key into that registry, where the full source record lives. `as_of` is the earliest `last_success` among the listed sources: the entry's content **from those sources** is current only through that date. Only stale sources are listed, so a cross-listed entry with one dead and one healthy source names just the dead one. **Absence means no contributing source is registered stale — not that the entry is verified current, and not that its sources are tracked at all** (the registry's `coverage` names what nothing measures). |
| `corpus` | enum | `security` (exploit/vuln/misuse) or `ai-harm` (societal harm without a security primitive). |
| `added` / `updated` | date | First-added / last-content-change dates (content-gated, so unchanged entries don't churn). |
| `first_seen` / `last_seen` | date | Provenance aliases of `added` / `updated`. |

## Core description
| Field | Type | Notes |
|---|---|---|
| `title` **R** | string | ≥5 chars. |
| `description` **R** | string | ≥20 chars. |
| `description_provenance` | enum | `verbatim` \| `summary` \| `original` — how `description` was produced. `original` covers a mechanically composed, non-model, non-verbatim text (e.g. AIAAIC's facts-only categorical description). Set once by whichever entry survives dedup as the merge target; never overwritten by a later merge (excluded from `merge_into`'s union/absorb behaviour). |
| `description_source` | string | Slug naming which upstream source contributed the *current* `description` (e.g. `aiaaic`), meaningful only when `description_provenance` is set. Needed because `description`/provenance are sticky to the dedup target while `tags`/`source_ids` union across every absorbed duplicate — provenance alone can't say *which* source. |
| `date` **R** | string | `YYYY`, `YYYY-MM`, or `YYYY-MM-DD`. |
| `year` **R** | integer | 1980–2030. |
| `category` **R** | enum | `real-world`, `research`, `research-demonstrated`, `red-team`, `vulnerability-disclosure`, `threat-report`, `policy`, `regulatory`, `report`. |
| `severity` **R** | enum | `Critical`, `High`, `Medium`, `Low`, `Info`. |
| `attack_vector` | string | Controlled vocabulary (see schema `examples`): `prompt-injection`, `rce`, `data-exfiltration`, `deepfake`, `privacy-violation`, `algorithmic-bias`, `csam-generation`, `unsafe-advice`, `other`, … |
| `affected` | string | Vendor / product / organization / system affected (free text). |
| `impact` | string | Real-world consequence summary. |
| `reversibility_class` | enum | Reversibility of the incident's **closing action**, ordered least→most severe: `read-only` → `reversible` → `external-reversible` → `irreversible` (see [TAXONOMIES.md](TAXONOMIES.md#reversibility-class), #74). Landmark-tier only, assigned via `data/curation_overrides.json` where source evidence describes the closing action (evidence + review date in the override `_note`). **Absence means unassessed, not `read-only`.** |
| `discovery_method` | enum | How the incident was first surfaced: `security-researcher`, `actor-disclosure`, `customer-report`, `media-report`, `law-enforcement`, `internal-monitoring`, `internal-report`, `vendor-monitoring`, `other` (see [TAXONOMIES.md](TAXONOMIES.md#discovery-method); lineage: VERIS 1.4.1 `discovery_method`, flattened). Landmark-tier only, evidence-gated via `data/curation_overrides.json`. **Absence means unassessed, not internally detected.** |

## Framework mappings
| Field | Type | Notes |
|---|---|---|
| `owasp_llm` | enum[] | OWASP Top 10 for LLM Apps 2025 — `LLM01`–`LLM10`. |
| `owasp_asi` | enum[] | OWASP Agentic (ASI) Top 10 — `ASI01`–`ASI10`. |
| `owasp_dsgai` | string[] | OWASP Data Security for GenAI codes (`DSGAInn`, companion). |
| `nist_ai_rmf` | string[] | NIST AI RMF subcategories, e.g. `MEASURE-2.7`, `MAP-3.5`. |
| `mitre_atlas` | string[] | MITRE ATLAS technique ids, e.g. `AML.T0051`, `AML.T0048.003`. |
| `mitre_atlas_tactics` | string[] | ATLAS tactic ids, e.g. `AML.TA0011` (Impact). Derived from techniques (subtechniques inherit the parent's). |
| `maestro_layers` | object[] | MAESTRO architectural-layer mapping (companion; `{layer, label, role, notes}`). |

## Vulnerability metadata
| Field | Type | Notes |
|---|---|---|
| `cve_ids` | string[] | `CVE-YYYY-NNNN…`. |
| `cwe_ids` | string[] | `CWE-NNN`. |
| `capec_ids` | string[] | `CAPEC-NNN` attack patterns, **derived** from `cwe_ids` via the authoritative CWE→CAPEC map (`mappings/cwe_capec.json`, built by `scripts/build_cwe_capec.py` from MITRE's CAPEC corpus). The complete, uncapped union — a broad CWE legitimately implies many patterns — so high-CWE records carry many CAPECs by design. Fully reconstructable from `cwe_ids` + the map; denormalised here for convenience. |
| `purl` | string[] | Package-URLs (`pkg:type/namespace/name`) **derived** from structured GHSA/OSV `affected` identifiers (e.g. `pip/foo` → `pkg:pypi/foo`, `maven/g:a` → `pkg:maven/g/a`). Entity-resolution anchor for the affected package; absent when `affected` is free-text. Only ecosystems with an official purl type are emitted. |
| `cvss_score` | number | 0–10. |
| `cvss_vector` | string | Full CVSS vector string. |
| `aiid_id` | integer | AI Incident Database numeric id where cross-listed. |
| `disclosure_date` | string | Public disclosure date when distinct from `date`. |

## Evidence
| Field | Type | Notes |
|---|---|---|
| `references` **R** | object[] | ≥1 `{title, url, type}`; `type` ∈ news/advisory/research/vendor/blog/cve/report/paper/regulatory/disclosure/legal/… |
| `mitigations` | string[] | Defensive measures / remediation. |
| `tags` | string[] | Free-form, incl. `sector-*` and `juris-*` facets and source tags (`aiaaic`, `atlas`, …). Source tags double as the row selectors in the freshness registry (see [Source freshness](#source-freshness)), so a tag like `airi-navigator` or `oecd-aim` identifies which upstream emitted the row. Content a source supplied is only as current as that source: the EU AI Act risk-tier tags (`eu-ai-act-*`) are AIRI-derived, so on any entry carrying them their as-of date is that entry's `source_freshness.as_of`, not the build date. |

## Licensing
| Field | Type | Notes |
|---|---|---|
| `content_license` | object | Row-level license-obligation marker: this entry's content derives from an upstream source whose license imposes obligations (attribution, possibly share-alike) on the row itself, over and above the repository's own `LICENSE-DATA`. Present on every entry that cites an AIAAIC source: the rows whose description derives from AIAAIC's sheet (`description_source == "aiaaic"`) plus the hand-curated rows whose title and categorical facts derive from AIAAIC directly, not via that field (D11(b) row-level containment; see `docs/specs/WS0-T3-marker-shape-2026-07-27.md`; extended to the hand-curated set by E16/D18, 2026-07-29) — current count audited in `docs/SOURCE_LICENSES.md` §1.1, not restated here to avoid drift. Shape: `{source, license, license_url?, attribution, attribution_url?, obligations}` where `obligations` is a non-empty subset of `["attribution", "share-alike"]`. Source-generic by design — a future source with row-level obligations reuses the same field, keyed by its own `source` value. Set at ingest — historically in lockstep with `description_source` for sheet-derived rows, independently for the hand-curated set — and excluded from `merge_into`'s key lists, so it is sticky to the dedup target and never overwritten by a later merge. Carried in full on `data/incidents.json` and the HuggingFace export; carried on `data/incidents.min.json` — and its two mirrors, `docs/data/incidents.min.json` and `src/genai_incidents/data/incidents.min.json` — only on marked rows (never emitted as `null` on unmarked rows); mirrored per-row on the STIX bundle as `x_content_license`. STIX emits it on the exact same set of SDOs the field covers on `data/incidents.json` — an exact match, not a heuristic-inflated count. **Absence means no row-level obligation is known for this entry — not that the entry is unencumbered.** |

## Source freshness

**Freshness is a property of the source, not of the row.** Whether an entry is
*emitted* (`source_status`) and whether the source that fed it is still
*refreshing* are two independent facts, and conflating them is how a dataset
comes to describe itself falsely without any single field being wrong: a
committed ingest snapshot keeps re-emitting its rows long after the upstream
download disappears, so every one of those rows stays honestly `active` while
its content quietly ages.

[`data/source_freshness.json`](../data/source_freshness.json) is the published
registry of that second fact — one record per tracked source, validated against
[`schema/source_freshness.schema.json`](../schema/source_freshness.schema.json).
It is a **curated input**, like `data/curation_overrides.json`: hand-authored,
reviewed, and read by the build — not a generated artifact.

| Registry field | Notes |
|---|---|
| `observed_at` | Date of the source-health snapshot the registry was last reconciled against — **not** the build date and not today. An artifact dated by its input reads as visibly old when it is old, instead of reading as current and being wrong. |
| `observed_from` | Which copy of `ingest/_state/source_health.json` those values came from, named precisely enough to judge their strength (see the three-copies note below). |
| `coverage` | What the registry speaks for, and — the part that matters — what it does not. Only the four weekly-refreshed sources are tracked; the AIID snapshot, the CVE/GHSA/OSV enrichment caches, the ATLAS/AVID/garak imports and `legacy_consolidated.json` are static or manual, with no health tracking. **Absence from the registry means nothing is measured, not that a source is healthy.** |
| `sources.<key>.status` | `ok` \| `degraded` \| `stale`, the same vocabulary `scripts/check_source_health.py` assigns. Only `stale` propagates to rows: `degraded` is a below-threshold blip, and letting it mark rows would churn a field across thousands of entries on a flaky week. Retiring a source is a corpus action (status + tombstone, Invariant 3), not a freshness value — which is why the enum needs no fourth member for it. |
| `sources.<key>.last_success` | The as-of date for everything that source contributed. |
| `sources.<key>.stale_since` | The first *failed* refresh after `last_success` — when the source broke, as opposed to when it crossed the threshold or when anyone noticed. Set from run-log evidence; omitted rather than guessed. |
| `sources.<key>.paused` | CI alerting is muted for this source. **A pause silences the alert, never the freshness claim** — a paused stale source still reads `stale` and still marks its rows. |
| `sources.<key>.hold` | An open retire/replace/restore decision *with the date it becomes live* (`{decision, until, note}`). Dated by construction, so an open-ended hold cannot be expressed as a resolved one. |
| `sources.<key>.row_marker` | How rows the source contributed to are found: `{kind: "tag", value: "<tag>"}`, or an explicit `null` plus a `row_marker_note` saying why the source does not propagate. Enrichment-only sources take the `null` path: CISA KEV adds fields to rows other sources created, so if it went stale the damage would be missing flags on rows nobody can enumerate — marking the few rows that *do* carry KEV data would point at the wrong set. |

**Resolution.** A row is contributed to by source *S* when it carries *S*'s
`row_marker` tag. Its `source_freshness` marker is emitted when at least one
such *S* is `stale`, listing exactly those sources with `as_of` = the earliest
`last_success` among them. Everything on the row is reconstructable from the
registry plus the row's tags; nothing is authored per row. **Declaring the next
dead source is a status flip in the registry — no schema change, no new field,
no migration.**

**Three copies of the health state exist and only one of them is publishable.**
`refresh-state:ingest/_state/source_health.json` is the authoritative machine
counter (high-churn, unreviewed by design, per decision D5).
`main:ingest/_state/source_health.json` is a bootstrap fallback that goes stale
**by design** — also D5, an accepted consequence of keeping unattended writes
off `main`. `data/source_freshness.json` is the reviewed publication. **The
build reads the registry and must never read the counter**: a build reading a
`main` checkout's counter would republish a deliberately-stale file as current,
which is a fresh instance of the very failure this registry closes. The counter
is what keeps the registry honest — the weekly refresh reconciles the two while
the authoritative copy is in the tree and fails loudly on divergence — but it is
never the thing that ships.

## Access
- **Python:** `pip install genai-incidents` → `load_incidents()`, `query(...)`, `by_id()`, `by_cve()`, `resolve_id()`.
- **Hugging Face:** `load_dataset("emmanuelgjr/genai-incidents")` (JSONL projection).
- **STIX 2.1:** `…github.io/genai_incidents/data/incidents.stix.json`.
- **CSV / min JSON / per-year markdown:** see the [site](https://emmanuelgjr.github.io/genai_incidents/) and [`docs/`](.).
