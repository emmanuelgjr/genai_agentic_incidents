# GenAI & Agentic AI Security Incidents

A single source of truth for **GenAI and agentic AI security incidents**, mapped to:

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
│   ├── ingest_cve_nvd_expanded.py    ← pull AI-relevant CVEs from NVD/GHSA/OSV → ingest/cve_nvd_expanded.json
│   ├── merge_and_dedupe.py           ← merge legacy + ingest/* → data/incidents.json
│   ├── render_markdown.py            ← data/incidents.json → INCIDENTS.md
│   └── validate.py                   ← validate JSON against schema
├── INCIDENTS.md                ← rendered index of all incidents
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
  "cvss_score": 9.8,
  "title": "...",
  "date": "2025-09",
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
  "tags": ["mcp","supply-chain"]
}
```

---

## Regenerating the dataset

```bash
# 1) Parse legacy source files into the unified schema
python scripts/parse_existing.py

# 2) (Optional) Run any incremental ingestor that drops a JSON array into ingest/
#    e.g. ingest/aiid_incidents.json, ingest/cve_incidents.json, ingest/atlas_incidents.json

# 3) Merge + dedupe everything into the single source of truth
python scripts/merge_and_dedupe.py

# 4) Render the human-readable Markdown index
python scripts/render_markdown.py

# 5) Validate the JSON against the schema
python scripts/validate.py
```

Dedupe keys, in priority order: (a) matching `cve_ids`, (b) matching normalized reference URL, (c) fuzzy title match within ±1 year. Merges union taxonomy mappings, references, tags, and CVE IDs across duplicates; takes the highest severity.

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
