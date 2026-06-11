# GenAI & Agentic AI Security Incidents

[![Incidents](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fraw.githubusercontent.com%2Femmanuelgjr%2Fgenai_incidents%2Fmain%2Fdata%2Fstats.json&query=%24.incident_count&label=incidents&color=ffb000&logo=databricks&logoColor=white)](https://emmanuelgjr.github.io/genai_incidents/)
[![Validate dataset](https://github.com/emmanuelgjr/genai_incidents/actions/workflows/validate.yml/badge.svg)](https://github.com/emmanuelgjr/genai_incidents/actions/workflows/validate.yml)
[![PyPI version](https://img.shields.io/pypi/v/genai-incidents?logo=pypi&logoColor=white&label=pypi)](https://pypi.org/project/genai-incidents/)
[![Python versions](https://img.shields.io/pypi/pyversions/genai-incidents?logo=python&logoColor=white)](https://pypi.org/project/genai-incidents/)
[![Hugging Face dataset](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-dataset-yellow)](https://huggingface.co/datasets/emmanuelgjr/genai-incidents)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20248676.svg)](https://doi.org/10.5281/zenodo.20248676)
[![License: MIT (code)](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![License: CC-BY-4.0 (data)](https://img.shields.io/badge/data-CC--BY--4.0-lightgrey.svg)](LICENSE-DATA)

- 🔎 **Searchable site:** <https://emmanuelgjr.github.io/genai_incidents/>
- 📦 **Python:** `pip install genai-incidents`
- 🤗 **Hugging Face:** [`emmanuelgjr/genai-incidents`](https://huggingface.co/datasets/emmanuelgjr/genai-incidents) — `load_dataset("emmanuelgjr/genai-incidents")` (built with `make huggingface`)
- 🛰️ **STIX 2.1 bundle** (for OpenCTI / MISP / TAXII): <https://emmanuelgjr.github.io/genai_incidents/data/incidents.stix.json> — incidents as `x-genai-incident` SDOs linked to MITRE ATLAS `attack-pattern`s and CVE `vulnerability`s. Build locally with `make stix`.
- 📡 **TAXII 2.1 (static):** discovery at <https://emmanuelgjr.github.io/genai_incidents/taxii2/discovery.json> — a read-only static mirror of the STIX collection ([usage + caveats](https://emmanuelgjr.github.io/genai_incidents/taxii2/README.md)). Build locally with `make taxii`.
- 🛡️ **MISP feed:** subscribe a MISP instance to <https://emmanuelgjr.github.io/genai_incidents/misp/> (Format: *MISP Feed*) — incidents grouped into year-events with `genai-incidents:*` / `mitre-atlas:*` tags. Build locally with `make misp`.
- 📖 **Field reference:** [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) · **Provenance & limitations:** [`docs/DATASHEET.md`](docs/DATASHEET.md)
- 🎯 **Scope — what's in/out:** [`INCLUSION.md`](INCLUSION.md) (the inclusion policy every entry must satisfy)
- 🛠️ **Spot an error?** Open a [data correction](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=data_correction.yml) or [scope dispute](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=scope_dispute.yml) — accepted changes are logged in [`CORRECTIONS.md`](CORRECTIONS.md)
- 🪪 **DOI:** [`10.5281/zenodo.20248676`](https://doi.org/10.5281/zenodo.20248676) — see [`CITATION.cff`](CITATION.cff)
- 📄 **Methodology:** [`docs/paper/genai-incidents-methods.md`](docs/paper/genai-incidents-methods.md) — how the dataset is built, mapped, and governed
- 📜 **Changelog:** [`CHANGELOG.md`](CHANGELOG.md)

A single source of truth of **[11,500+ GenAI and agentic AI security incidents](https://emmanuelgjr.github.io/genai_incidents/)** (see the live count in the badge above), each mapped to:

- **OWASP Top 10 for LLM Applications (2025)** — `LLM01`–`LLM10`
- **OWASP Agentic Top 10 (ASI)** — `ASI01`–`ASI10`
- **NIST AI Risk Management Framework (AI 100-1)** — `GOVERN` / `MAP` / `MEASURE` / `MANAGE` subcategories
- **MITRE ATLAS** — tactics (`AML.TA00xx`) and techniques (`AML.T00xx`)
- _(Companion)_ **MAESTRO** architectural layers (`L1`–`L7`)

The dataset is published as both a machine-readable JSON (`data/incidents.json`) and a human-readable Markdown index (`INCIDENTS.md`).

---

## Layout

```
.
├── data/
│   ├── incidents.json          ← full single source of truth (use this)
│   ├── incidents.min.json      ← slim variant: id, title, taxonomy mappings, primary reference
│   └── legacy_consolidated.json ← intermediate output from the legacy parser
├── schema/
│   └── incident.schema.json    ← JSON Schema for one incident
├── mappings/
│   ├── owasp_llm_top10_2025.json
│   ├── owasp_asi_top10.json
│   ├── nist_ai_rmf.json
│   ├── mitre_atlas.json
│   └── maestro_layers.json
├── legacy/                     ← original source files (preserved verbatim)
├── ingest/                     ← per-source aggregator outputs (CVE, AIID, ATLAS, etc.)
├── scripts/
│   ├── parse_existing.py             ← parse legacy/ → data/legacy_consolidated.json
│   ├── ingest_external.py            ← parse cloned source repos under ../_external/ → ingest/*.json
│   ├── scrape_aiid.py                ← fetch all AIID incident pages (OG metadata) → ingest/aiid_full.json
│   ├── ingest_airi_navigator.py      ← MIT FutureTech AI Risk Navigator CSV → ingest/airi_navigator_incidents.json
│   ├── ingest_aiaaic_sheet.py        ← AIAAIC Repository public Google Sheet → ingest/aiaaic_sheet_incidents.json
│   ├── ingest_oecd_aim.py            ← OECD AI Incidents Monitor (10k pages) → ingest/oecd_aim_full_incidents.json
│   ├── ingest_cve_nvd_expanded.py    ← pull AI-relevant CVEs from NVD/GHSA/OSV → ingest/cve_nvd_expanded.json
│   ├── merge_and_dedupe.py           ← merge legacy + ingest/* → data/incidents.json
│   ├── render_markdown.py            ← data/incidents.json → INCIDENTS.md
│   └── validate.py                   ← validate JSON against schema
├── INCIDENTS.md                ← rendered index: unified table, newest-first
├── docs/incidents/<year>.md    ← per-year detail shards linked from INCIDENTS.md
├── tests/                      ← pytest suite for merge/render helpers
├── LICENSE                     ← MIT (covers code in scripts/)
├── LICENSE-DATA                ← CC-BY-4.0 (covers the dataset under data/)
└── README.md
```

---

## What counts as an incident?

Anything that is one or more of:

1. A **real-world** exploitation, breach, or misuse involving GenAI or agentic AI systems.
2. A **publicly disclosed vulnerability** (CVE or vendor advisory) affecting an AI/ML/LLM/agent stack.
3. A **research-demonstrated attack** with a credible PoC and public write-up.
4. A **red-team finding** released by a security researcher with sufficient detail to reproduce or replicate.

Each entry must have **at least one verifiable external URL**. Entries without sources are excluded.

This repository does **not** include broad fairness/bias-only AI harms unless they involve a security primitive (data exfiltration, integrity attack, account compromise, etc.).

---

## Schema (summary)

See [`schema/incident.schema.json`](schema/incident.schema.json) for the canonical version.

```jsonc
{
  "id": "INC-00001",                 // stable 5-digit ID
  "source_ids": ["AIID-123", "CVE-2025-..."],
  "cve_ids": ["CVE-2025-..."],
  "cwe_ids": ["CWE-918"],
  "cvss_score": 9.8,
  "cvss_vector": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
  "aiid_id": 1234,                   // canonical AIID numeric ID when applicable
  "title": "...",
  "date": "2025-09",
  "disclosure_date": "2025-10-02",   // separate from incident date when known
  "year": 2025,
  "category": "real-world | research | red-team | vulnerability-disclosure | threat-report | policy",
  "description": "...",
  "attack_vector": "prompt-injection | rce | supply-chain | data-exfiltration | ...",
  "affected": "vendor/product",
  "impact": "...",
  "severity": "Critical | High | Medium | Low | Info",
  "owasp_llm": ["LLM01", "LLM06"],
  "owasp_asi": ["ASI01", "ASI02"],
  "nist_ai_rmf": ["MEASURE-2.7", "MAP-3.5"],
  "mitre_atlas": ["AML.T0051", "AML.T0051.001"],
  "mitre_atlas_tactics": ["AML.TA0004"],
  "maestro_layers": [{"layer":"L3","label":"Agent Frameworks & Tooling","role":"origin"}],
  "mitigations": ["..."],
  "references": [
    {"title":"Vendor advisory","url":"https://...","type":"vendor"}
  ],
  "tags": ["mcp","supply-chain"],
  "added": "2026-05-16",             // stable across re-runs
  "updated": "2026-05-16"            // only bumped when content actually changes
}
```

---

## Using the dataset

### As a Python library

```bash
pip install genai-incidents
```

```python
from genai_incidents import query, by_cve, resolve_id

for inc in query(severity="Critical", attack_vector="prompt-injection", year=2026):
    print(inc["id"], "-", inc["title"])

print(by_cve("CVE-2026-21520"))   # all incidents that list this CVE
print(resolve_id("INC-00139"))    # follow merge history to the current canonical INC
```

### As JSON

- Full: [`data/incidents.json`](data/incidents.json)
- Slim (for UIs): [`data/incidents.min.json`](data/incidents.min.json)
- Schema: [`schema/incident.schema.json`](schema/incident.schema.json)
- ID deprecations: [`data/id_deprecations.json`](data/id_deprecations.json) — for resolving citations of merged-away IDs

### As a website

Filterable, searchable, deep-linkable table at
<https://emmanuelgjr.github.io/genai_incidents/>.

## Regenerating the dataset

```bash
pip install -r requirements.txt
make build      # parse legacy, merge + dedupe, render, validate
make test       # pytest tests/
make ingest-all # (heavy: refresh AIID/AIRI/AIAAIC/OECD AIM/NVD from network)
```

Or run the steps individually:

```bash
python scripts/parse_existing.py     # legacy/ -> data/legacy_consolidated.json
python scripts/merge_and_dedupe.py   # legacy + ingest/* -> data/incidents.json
python scripts/render_markdown.py    # data/incidents.json -> INCIDENTS.md + docs/incidents/<year>.md
python scripts/validate.py           # schema check
```

Dedupe keys (first hit wins): (a) matching `cve_ids`, (b) matching `source_ids` (with `AIID-N-OECD` canonicalised to `AIID-N`), (c) matching normalized reference URL, (d) fuzzy title match within ±1 year. After each merge the indices are reindexed so transitive dupes (entry A absorbs CVE-3, then entry B with CVE-3 already exists → B is merged into A as well) all collapse. Merges union taxonomy mappings, references, tags, CVE/CWE IDs, and source IDs; take the highest severity; prefer the more-specific date (YYYY-MM-DD beats year-only) and reject future-year dates.

`added` and `updated` are preserved from the previous output; `updated` only bumps when an entry's content actually changes. That keeps `make build` deterministic for CI drift checks.

---

## Adding entries

Two paths:

1. **Manual**: append a properly-shaped object to `data/incidents.json` and run `scripts/render_markdown.py`. Ensure `references` has at least one resolvable URL.
2. **Automated**: drop a JSON array of raw entries into `ingest/<your_source>.json` (any reasonable shape — see `scripts/merge_and_dedupe.py` `normalize_entry` for the field tolerance), then re-run merge + render.

Always run `scripts/validate.py` before committing.

---

## Taxonomy mappings

The mapping files in `mappings/` document the controlled vocabulary used in this dataset. They are derived from the original sources:

- OWASP LLM Top 10 (2025): <https://genai.owasp.org/llm-top-10/>
- OWASP Agentic Top 10 (ASI / "Agentic AI – Threats and Mitigations"): <https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/>
- NIST AI Risk Management Framework (AI 100-1): <https://www.nist.gov/itl/ai-risk-management-framework>
- NIST AI 600-1 Generative AI Profile: <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>
- MITRE ATLAS: <https://atlas.mitre.org/>
- MAESTRO (companion): <https://genai.owasp.org/resource/genai-security-project-maestro/>

When a framework releases a new version, update the mapping JSON in `mappings/` and re-run merge + validate.

---

## Sources aggregated

The current dataset draws from the following public sources. Each entry retains links back to the originating advisory, post, or paper:

- **OWASP GenAI Security Project** — incident roundups + Top 10 references
- **AI Incident Database (AIID)** ([incidentdatabase.ai](https://incidentdatabase.ai/), [github.com/responsible-ai-collaborative/aiid](https://github.com/responsible-ai-collaborative/aiid)) — security-relevant subset of the full corpus, scraped via OG metadata
- **OECD AI Incidents Monitor (AIM)** ([oecd.ai/en/incidents](https://oecd.ai/en/incidents)) — cross-listed against AIID via the official AIID-OECD bridge file
- **AIAAIC** ([aiaaic.org](https://www.aiaaic.org/aiaaic-repository)) — AI, Algorithmic, and Automation Incidents and Controversies
- **MITRE ATLAS** ([atlas.mitre.org](https://atlas.mitre.org/), [github.com/mitre-atlas/atlas-data](https://github.com/mitre-atlas/atlas-data)) — all case studies parsed from the YAML corpus
- **AVID** — AI Vulnerability Database ([avidml.org](https://avidml.org/))
- **CSET-AIID Harm Taxonomy** ([github.com/georgetown-cset/CSET-AIID-harm-taxonomy](https://github.com/georgetown-cset/CSET-AIID-harm-taxonomy)) — controlled vocabulary reference
- **NVD / CVE.org / GitHub Security Advisories / OSV.dev / CISA KEV** — AI/ML/LLM/agent CVEs pulled via REST API across 56 keywords
- **NVIDIA garak** ([github.com/NVIDIA/garak](https://github.com/NVIDIA/garak)) — one entry per LLM vulnerability scanner probe (canonical attack classes)
- **promptfoo** ([github.com/promptfoo/promptfoo](https://github.com/promptfoo/promptfoo)) — one entry per red-team plugin/strategy
- **ModelOriented/CVE-AI** ([github.com/ModelOriented/CVE-AI](https://github.com/ModelOriented/CVE-AI)) — XAI-based AI model validation findings
- **Researcher and vendor blogs** — Embrace The Red, Tenable, Palo Alto Unit 42, Trail of Bits, Aim Security, Noma Security, Wiz Research, Lakera, Invariant Labs, PromptArmor, Pillar Security, Token Security, HiddenLayer, Robust Intelligence, Protect AI, Cato Networks CTRL, Endor Labs, Sysdig, Zenity Labs, JFrog, Datadog Security Labs, Reco, AppOmni, BeyondTrust, Oasis Security, Mindgard, Koi Security, Imperva, Sonar, Oligo Security, OX Security, SentinelOne, Check Point Research, Trend Micro, Tinfoil Security, ZeroPath, Cymulate, MaccariTA, and others.
- **Vendor threat reports** — Anthropic, OpenAI, Google Threat Intelligence (GTIG/TAG/Mandiant), Microsoft Threat Intelligence (MTAC/MSRC), AWS Security Bulletins, CrowdStrike, Recorded Future.
- **Academic papers** — selected USENIX Security / NDSS / S&P / CCS / arXiv entries with concrete adversarial PoCs.

If a source is missing or mis-attributed, open an issue or PR.

---

## Contributing

PRs welcome. Please:

- Add at least one verifiable URL per entry.
- Map to all four taxonomies where applicable. If unsure, leave the field empty rather than guess.
- Run `scripts/validate.py` and `scripts/render_markdown.py` before opening a PR.
- For incidents you authored or first reported, that's totally fine — but please link the canonical writeup.

---

## License

- **Code** (`scripts/`, `schema/`): [MIT](LICENSE)
- **Data and documentation** (`data/`, `INCIDENTS.md`, `mappings/`): [Creative Commons Attribution 4.0 International](LICENSE-DATA)

If you use this dataset in research or tooling, please cite this repository.
