# Datasheet — GenAI & Agentic AI Security Incidents

Following *Datasheets for Datasets* (Gebru et al.). For per-field definitions see
[`DATA_DICTIONARY.md`](DATA_DICTIONARY.md); for the formal schema see
[`schema/incident.schema.json`](../schema/incident.schema.json).

## Motivation
A single, machine-readable source of truth for GenAI and agentic-AI security
incidents, normalized and mapped to OWASP LLM/ASI, NIST AI RMF, and MITRE
ATLAS — so developers, AppSec/threat-intel teams, and researchers can query,
pivot, and cite incidents instead of re-scraping scattered trackers.

## Composition
- **Instances:** consolidated incidents (currently 7,720), each an alleged
  real-world harm, disclosed vulnerability, threat report, or research/red-team
  demonstration involving an AI system.
- **Split:** `corpus` = `security` vs `ai-harm`; `category` distinguishes
  real-world from research/red-team/regulatory entries.
- **Labels:** severity, attack_vector, and OWASP/NIST/ATLAS mappings — assigned
  by deterministic heuristics and, for a growing subset, human/assisted review
  (see `quality_tier`).
- **Provenance:** every entry records its upstream `source_ids`.

## Collection
Aggregated from public, credible sources: AI Incident Database (AIID), AIAAIC,
OECD AI Incidents Monitor, MIT AI Risk Repository, MITRE ATLAS, AVID, NVD +
GitHub Security Advisories + OSV.dev (AI/ML packages), OWASP, vendor threat
reports, and peer-reviewed venues (arXiv/USENIX/CCS/NDSS). Ingestion scripts
live in [`scripts/`](../scripts); each source is re-pulled, normalized, then
deduplicated by CVE / canonical URL / fuzzy title.

## Preprocessing & quality
- **Dedup:** union of taxonomy/refs, highest severity, most specific date;
  merged ids tombstoned in `id_deprecations.json`.
- **Classification:** `attack_vector` and framework mappings are filled by
  precision-first heuristics; `quality_tier` records vetting level.
- **Curation overrides:** explicit human/assisted decisions are recorded in
  [`data/curation_overrides.json`](../data/curation_overrides.json) and survive rebuilds.
- **Reproducibility:** the full build is deterministic and idempotent across
  calendar days (CI re-derives all outputs and fails on any drift).

## Uses
- AppSec triage and dependency/CVE lookup; threat-intel (STIX 2.1 export,
  ATLAS tactic/technique pivots); research on AI-incident trends and taxonomy.
- **Not** a complete census of all AI incidents, and not legal advice.

## Limitations & biases
- **Source & language bias:** English-language, Western-media-skewed; under-counts
  unreported or non-English incidents.
- **Heuristic labels:** `auto`-tier mappings are unreviewed; `attack_vector`
  `other` (~39%) reflects genuinely uncategorized harm incidents.
- **Recency lag:** very recent CVEs may lack CVSS until NVD scores them.
- **Scope drift:** broad sources (AIAAIC/OECD) include pre-LLM algorithmic harms.

## Distribution & licence
- **Data:** CC-BY-4.0. **Code:** MIT. DOI [10.5281/zenodo.20248676](https://doi.org/10.5281/zenodo.20248676).
- Distributed via GitHub, PyPI (`genai-incidents`), Hugging Face Datasets, and a STIX 2.1 bundle.

## Maintenance
Maintained at <https://github.com/emmanuelgjr/genai_incidents>; a weekly workflow
refreshes external sources via PR. Versioned with SemVer; see [`CHANGELOG.md`](../CHANGELOG.md).
Corrections welcome via issues/PRs and the curation-overrides file.
