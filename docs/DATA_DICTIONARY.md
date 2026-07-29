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
| `source_status` | enum | `active` (still emitted by a source this build) or `retained` (carried from a prior build after all its sources dropped it — see retain-on-drop). |
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
| `tags` | string[] | Free-form, incl. `sector-*` and `juris-*` facets and source tags (`aiaaic`, `atlas`, …). |

## Licensing
| Field | Type | Notes |
|---|---|---|
| `content_license` | object | Row-level license-obligation marker: this entry's content derives from an upstream source whose license imposes obligations (attribution, possibly share-alike) on the row itself, over and above the repository's own `LICENSE-DATA`. Present on every entry that cites an AIAAIC source: the rows whose description derives from AIAAIC's sheet (`description_source == "aiaaic"`) plus the hand-curated rows whose title and categorical facts derive from AIAAIC directly, not via that field (D11(b) row-level containment; see `docs/specs/WS0-T3-marker-shape-2026-07-27.md`; extended to the hand-curated set by E16/D18, 2026-07-29) — current count audited in `docs/SOURCE_LICENSES.md` §1.1, not restated here to avoid drift. Shape: `{source, license, license_url?, attribution, attribution_url?, obligations}` where `obligations` is a non-empty subset of `["attribution", "share-alike"]`. Source-generic by design — a future source with row-level obligations reuses the same field, keyed by its own `source` value. Set at ingest — historically in lockstep with `description_source` for sheet-derived rows, independently for the hand-curated set — and excluded from `merge_into`'s key lists, so it is sticky to the dedup target and never overwritten by a later merge. Carried in full on `data/incidents.json` and the HuggingFace export; carried on `data/incidents.min.json` — and its two mirrors, `docs/data/incidents.min.json` and `src/genai_incidents/data/incidents.min.json` — only on marked rows (never emitted as `null` on unmarked rows); mirrored per-row on the STIX bundle as `x_content_license`. STIX emits it on the exact same set of SDOs the field covers on `data/incidents.json` — an exact match, not a heuristic-inflated count. **Absence means no row-level obligation is known for this entry — not that the entry is unencumbered.** |

## Access
- **Python:** `pip install genai-incidents` → `load_incidents()`, `query(...)`, `by_id()`, `by_cve()`, `resolve_id()`.
- **Hugging Face:** `load_dataset("emmanuelgjr/genai-incidents")` (JSONL projection).
- **STIX 2.1:** `…github.io/genai_incidents/data/incidents.stix.json`.
- **CSV / min JSON / per-year markdown:** see the [site](https://emmanuelgjr.github.io/genai_incidents/) and [`docs/`](.).
