# OWASP LLM Top 10: 2025 → 2026 migration delta

**Date:** 2026-08-17
**Scope:** renumber every `owasp_llm` code in the corpus from the OWASP Top 10 for
LLM Applications **2025** edition to the **2026** edition.
**Status:** applied and verified. Do not regenerate — this is the record of the
migration, not a live surface.

---

## 1. What the 2026 edition changed

Published **2026-08-03**.
Canonical text: <https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/tree/main/2026/final>
PDF: <https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/>

The 2026 revision is a **renumbering plus one rename**. No entry was added and none
removed, so the 2025 → 2026 mapping is a **bijection** over `LLM01`–`LLM10`.

| 2025 | Name (2025) | → | 2026 | Name (2026) | Move |
|---|---|---|---|---|---|
| LLM01 | Prompt Injection | → | LLM01 | Prompt Injection | — |
| LLM02 | Sensitive Information Disclosure | → | LLM02 | Sensitive Information Disclosure | — |
| LLM03 | Supply Chain | → | LLM04 | Supply Chain | −1 |
| LLM04 | Data and Model Poisoning | → | LLM05 | Data and Model Poisoning | −1 |
| LLM05 | Improper Output Handling | → | LLM10 | Improper Output Handling | **−5** |
| LLM06 | Excessive Agency | → | LLM03 | Excessive Agency | **+3** |
| LLM07 | System Prompt Leakage | → | LLM08 | **Hidden Context Exposure** | −1, renamed |
| LLM08 | Vector and Embedding Weaknesses | → | LLM09 | Vector and Embedding Weaknesses | −1 |
| LLM09 | Misinformation | → | LLM07 | Misinformation | +2 |
| LLM10 | Unbounded Consumption | → | LLM06 | Unbounded Consumption | **+4** |

Machine-readable: [`mappings/owasp_llm_2025_to_2026.json`](../../mappings/owasp_llm_2025_to_2026.json).

### Why this migration is unusually dangerous

The code space is **identical before and after** (`LLM01`–`LLM10`). `schema/incident.schema.json`
validates a correctly-migrated corpus and a doubly-migrated corpus equally happily,
and so does every downstream consumer. There is no natural tripwire: a wrong
permutation, a partial application, or a second application produces a corpus that
passes every existing check while meaning something different. Every safeguard in
this migration exists because of that.

---

## 2. Corpus delta (`data/incidents.json`)

13,060 entries · 11,556 carry at least one code · **17,498 code assignments**.

| 2026 code | Name | Count | (was, under 2025 numbering) |
|---|---|---:|---|
| LLM01 | Prompt Injection | 407 | LLM01 407 |
| LLM02 | Sensitive Information Disclosure | 984 | LLM02 984 |
| LLM03 | Excessive Agency | 783 | LLM06 783 |
| LLM04 | Supply Chain | 6,162 | LLM03 6,162 |
| LLM05 | Data and Model Poisoning | 157 | LLM04 157 |
| LLM06 | Unbounded Consumption | 44 | LLM10 44 |
| LLM07 | Misinformation | 2,416 | LLM09 2,416 |
| LLM08 | Hidden Context Exposure | 730 | LLM07 730 |
| LLM09 | Vector and Embedding Weaknesses | 24 | LLM08 24 |
| LLM10 | Improper Output Handling | 5,791 | LLM05 5,791 |
| | **Total** | **17,498** | **17,498** |

Inputs migrated ahead of the rebuild: 23,641 code assignments across 17 files
(`legacy/incidents.json` + 16 `ingest/*.json`), plus the retention source (§4).

---

## 3. Field-level delta (working agreement 2)

The migration was verified against a **control build**: a clean worktree at `HEAD`
(pre-migration code, pre-migration inputs) was built with the same pipeline, and its
output compared entry-by-entry with the migrated build.

```
git worktree add --detach <tmp> HEAD
cd <tmp> && python scripts/parse_existing.py && python scripts/merge_and_dedupe.py
```

Result:

| Check | Result |
|---|---|
| ID sets identical | **yes** — 13,060 = 13,060, symmetric difference 0 |
| Entries whose `owasp_llm` ≠ crosswalk image of the control | **0** |
| Entries with **any other field** changed | **0** |
| Total code assignments | 17,498 → 17,498 |

That is the whole claim of this migration, stated as one assertion: *for every
entry, the new code set is exactly the image of the old code set under the
crosswalk, and nothing else moved.*

Per-file input deltas (entry counts, ID sets, changed-field census) were also
checked by `scripts/migrate_owasp_llm_2026.py`, which fails closed and refuses to
write if any file shows a change outside `owasp_llm` / `owasp_entries`.

---

## 4. Finding: retain-on-drop rows are a second migration input

**An inputs-only migration is not sufficient for this corpus, and the first attempt
at one was wrong.**

`merge_and_dedupe.py`'s retain-on-drop step (`load_retained_priors()`, spec:
`docs/superpowers/specs/2026-06-01-retain-on-drop-design.md`) carries entries that
every source has dropped **verbatim out of the previous `data/incidents.json`**, so
the never-delete invariant holds. Those rows are not re-derived from any ingest
feed. An inputs-only migration therefore cannot reach them, and they would have
kept 2025 codes through every future rebuild.

Measured here: **9 retained rows, 16 code assignments.** They surfaced as a 9-entry
drift between the migrated build and the crosswalk image of the control build —
LLM03 +9 / LLM04 −9 and LLM05 +7 / LLM10 −7 — while the *total* stayed exactly
17,498. **The totals matched while the distribution was wrong**, which is precisely
the failure a count-only check waves through.

Fix: `data/incidents.json` is a migration target as well as a build output. It was
restored to its pre-migration state, migrated, and only then rebuilt. This is not a
hand-edit of `data/*.json` — that invariant forbids editing the built corpus by
hand, and this is a deterministic, delta-verified script.

**Generalization for future taxonomy migrations in this repo:** the set of build
inputs is `legacy/` + `ingest/` **+ the previous `data/incidents.json`**. Any
migration that rewrites persisted field values must include the third, or it will
silently miss every retained row. Nothing in the schema or the validator detects
the omission.

---

## 5. Double-apply guards

A bijection applied twice is silently wrong and undetectable downstream, so
`scripts/migrate_owasp_llm_2026.py` fails closed on two independent guards:

1. **Hash stamp** — `data/.owasp_llm_migration.json` records SHA-256 before/after
   per file. A file whose current hash equals its recorded post-migration hash is
   skipped.
2. **Semantic guard** — the retention source is rewritten by every `make build`, so
   its hash will not match the stamp afterwards. It is instead skipped when it
   already declares `OWASP LLM Top 10 (2026)` in its dataset description.

The crosswalk itself is asserted to be a bijection at load time; the script hardcodes
no permutation of its own.

---

## 6. Scope limit — renumbering, NOT re-classification

Each entry kept the risk concept it was already assigned; only the identifier for
that concept changed.

Several 2026 entries **widened their scope**:

- **LLM08 Hidden Context Exposure** — from the system prompt specifically to *all*
  non-user-facing context (developer instructions, retrieved policy text, tool and
  function schemas).
- **LLM01 Prompt Injection** — now covers cross-modal attacks (instructions hidden
  in image or audio).
- **LLM04 Supply Chain** — now covers model-artifact provenance failures.
- **LLM05 Data and Model Poisoning** — absorbs fine-tuning subversion.
- **LLM10 Improper Output Handling** — now spans insecure code generated at scale.

Incidents that would **newly qualify** under a widened entry were **not** added.
Doing so means re-running classifiers over incident descriptions, and
description-coupled reclassification is a known hazard here — the WS0-T3 field cut
silently relabelled 372 AIAAIC entries through exactly that coupling
([`WS0-T3-cascade-2026-07-18.md`](WS0-T3-cascade-2026-07-18.md)).

**Consequence:** current 2026 mappings are *complete with respect to the 2025
labelling* and *conservative with respect to 2026 scope*. Closing that gap is
annotation work (WS2), not renumbering, and is not claimed anywhere as done.

---

## 7. Surfaces updated

**Data / inputs:** `legacy/incidents.json`, 16 × `ingest/*.json`,
`data/incidents.json` (retention source), then rebuilt: `data/incidents.min.json`,
`data/legacy_consolidated.json`, `data/incidents.stix.json`, `INCIDENTS.md`,
31 × `docs/incidents/<year>.md`, `docs/data/*`, `src/genai_incidents/data/*`,
`dist/hf/*`.

**Classifier tables** (so re-ingests emit 2026 codes): `ingest_aiaaic_sheet.py`,
`ingest_airi_navigator.py`, `ingest_cve_nvd_expanded.py`, `ingest_external.py`,
`ingest_oecd_aim.py`, `ingest_redteam_benchmarks.py`, `scrape_aiid.py`,
`parse_existing.py`, `merge_and_dedupe.py`, `render_markdown.py`.

**Catalogs:** added `mappings/owasp_llm_top10_2026.json` and
`mappings/owasp_llm_2025_to_2026.json`; `mappings/owasp_llm_top10_2025.json` kept
and marked superseded (releases ≤ v2.9.0 and their DOIs carry 2025 codes and cannot
be read without it).

**Docs / metadata:** `README.md`, `docs/TAXONOMIES.md`, `docs/DATA_DICTIONARY.md`,
`docs/paper/genai-incidents-methods.md`, `CONTRIBUTING.md`, `docs/index.html`,
`docs/app.js`, `schema/incident.schema.json` (+ packaged copy), `.zenodo.json`,
`CITATION.cff`.

**Also refreshed:** `data/incidents.stix.json`, `docs/data/incidents.stix.json` and
`dist/hf/incidents.jsonl` were regenerated. These were **separately stale** — built
from a July snapshot (e.g. LLM01 428 vs the corpus's 407) — so their regeneration
carries an unrelated content refresh in addition to the renumbering. Flagged here
rather than folded silently into the migration delta.

---

## 8. Verification commands

```bash
python scripts/migrate_owasp_llm_2026.py            # dry run + per-file delta
python scripts/migrate_owasp_llm_2026.py --verify data/incidents.json
python scripts/validate.py                          # 13060/13060 valid, 0 errors
python scripts/check_stats_drift.py                 # clean, 5 surfaces match
python -m pytest tests -q                           # 314 passed
```

Consumers reading data published before this date: see the compatibility note in
[`docs/TAXONOMIES.md`](../TAXONOMIES.md#owasp-top-10-for-llm-applications-2026).
