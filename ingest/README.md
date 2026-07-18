# `ingest/`

Each `*.json` file here is a per-source aggregator output — a top-level JSON array of incident-shaped objects in a tolerant input schema (it doesn't need to match `schema/incident.schema.json` exactly; `scripts/merge_and_dedupe.py` normalizes on the way in).

## Adding a new source

1. Create `ingest/<source>.json` containing a JSON array of raw entries. Minimum per entry:

   ```jsonc
   {
     "source_id": "<unique-id-from-the-source>",
     "title": "...",
     "date": "YYYY-MM",
     "year": YYYY,
     "description": "...",
     "references": [{"url": "https://..."}]  // at least one URL required
   }
   ```

   All other fields (taxonomies, severity, etc.) are optional but encouraged.

2. Run `python scripts/merge_and_dedupe.py` — the normalizer will:
   - Coerce to the canonical schema
   - Backfill MITRE ATLAS / NIST AI RMF from OWASP codes if you didn't provide them
   - Dedupe by CVE → reference URL → fuzzy title match
   - Assign stable `INC-NNNNN` IDs

3. Run `python scripts/validate.py` and `python scripts/render_markdown.py`.

## Current source files

| File | Source | Notes |
|---|---|---|
| `aiid_incidents.json` | AI Incident Database security-relevant subset | Some entries also reference vendor/research writeups for verification |
| `aiid_full.json` | AI Incident Database, via AIID's official weekly snapshot channel (`scripts/ingest_aiid_snapshot.py`, `make ingest-aiid`) | Facts + link only — title + structured facts (date/entities/MIT taxonomy); AIID's own narrative `description` is used only as an ephemeral classification signal, never persisted. See `docs/audits/WS0-T4-aiid-snapshot-swap-2026-07-18.md`. |
| `atlas_incidents.json` | MITRE ATLAS case studies + adversarial-ML research cited in ATLAS | All entries map at least one ATLAS technique |
| `avid_owasp_incidents.json` | AVID + OWASP GenAI Project incident roundups | AVID taxonomy codes (`S/E/P-####`) preserved in `avid_categories` |
| `cve_incidents.json` | NVD-verified CVEs affecting AI/ML/LLM/agent stacks (2022-2026) | Every entry has a verified CVE ID and NVD URL |
| `research_incidents.json` | Researcher and vendor security blog disclosures | Embrace The Red, Tenable, Unit 42, etc. |
| `bounty_incidents.json` | HackerOne / huntr.dev / Bugcrowd disclosed AI bounties | _(may be present)_ |
| `arxiv_incidents.json` | arXiv + venue papers demonstrating concrete AI attacks | _(may be present)_ |
| `threat_reports_incidents.json` | Vendor TI reports (Anthropic, OpenAI, GTI, MSTIC, etc.) | Each named operation/actor is split into its own entry |

## Don't

- Don't paste full HTML scrapes here. Summarize.
- Don't include entries without a verifiable URL.
- Don't worry about deduping against the rest of the dataset — the merger handles that.
