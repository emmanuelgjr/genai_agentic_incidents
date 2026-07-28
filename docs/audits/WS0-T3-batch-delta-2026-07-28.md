# WS0-T3 Phase B — Full-Corpus Field-Level Delta (the real batch)

**Date:** 2026-07-28
**Author:** pipeline-engineer
**Authorizing decision:** PROGRESS.md D16 (2026-07-28, user) — batch approved after
review of `docs/audits/WS0-T3-validation-sample-2026-07-27.md` §3/§4/§7.
**Governing specs:** `docs/specs/WS0-T3-rescoped-2026-07-18.md` §2(c)/§5/§6.2,
`docs/specs/WS0-T3-marker-shape-2026-07-27.md`.
**Status:** this is the real batch. Unlike the 2026-07-27 dry run, nothing here
is reverted — `data/incidents.json`, `data/incidents.min.json`,
`ingest/aiaaic_sheet_incidents.json`, and every generated surface are committed
as part of this change.
**Code changed:** none. Phase A's code (`ws0/t3-impl` → merged to `main` at
`3f0af267`) is run as-is; this branch (`ws0/t3-batch`) contains only data/build
output and this audit doc.

---

## 1. Fetch

| | |
|---|---|
| Command | `python scripts/ingest_aiaaic_sheet.py` (`make ingest-aiaaic`) |
| Fetch time | 2026-07-28T23:26:32Z |
| Bytes downloaded | 961,119 (vs. the 2026-07-17 dry-run cache's 958,849 — legitimate upstream growth, not re-measured against that cache) |
| Raw sheet rows | 2,258 |
| Security-relevant entries written | 1,504 (skipped 751 out-of-scope) → `ingest/aiaaic_sheet_incidents.json` |

No `.etag` sidecar existed before this run (confirmed absent in the pre-batch
tree), so — exactly as the validation-sample document's §5 note anticipated —
`conditional_fetch` never sent `If-None-Match`/`If-Modified-Since`, the
304-Not-Modified branch was unreachable, and this is a **full, live re-fetch**,
not a replay of the gitignored 2026-07-17 snapshot. The dry run's numbers are a
**preview to reconcile against**, not a baseline this run reproduces
byte-for-byte; §5 below does that reconciliation.

## 2. Rebuild

`make build` (`parse_existing.py` → `merge_and_dedupe.py` → `render_markdown.py`
→ `render_docs_stats.py` → `validate.py`) run in full, no network or model call
anywhere in the path (the only network-shaped step is the ingest above, which
is outside `make build` by design — see `Makefile`'s `build: merge render
render-docs-stats validate` target).

```
[total]  18736 input -> 13119 unique
13119/13119 entries valid; 0 with errors.
integrity: no duplicate CVE/source keys; all deprecations resolve.
[check-stats-drift] clean: 5 doc surfaces match data/stats.json, no unmarked hardcoded totals
227 passed in 1.93s
```

**Determinism.** The full build (`parse_existing.py` + `merge_and_dedupe.py` +
`render_markdown.py` + `render_docs_stats.py` + `validate.py`) was run twice
against the same fetched `ingest/aiaaic_sheet_incidents.json` (i.e. without
re-fetching between runs, isolating the build step's own determinism from
network variance). SHA-256 of every generated artifact was identical across
both runs:

| File | SHA-256 |
|---|---|
| `data/incidents.json` | `b5fa3ae1257c6ac7db4816925a98dda72179d77531843302108e20298de028b` |
| `data/incidents.min.json` | `e4c126627aa56055efdaba26f281fbac51c60c7f939ed7bf0fe3cfec347e504` |
| `INCIDENTS.md` | `c74dff2c8f554124efdcd1cdcaec09aa195151ea4163eb3f9e28d17b89547bb` |
| `data/stats.json` | `fdac9162dd4265d5f3cda78f2b525b4ab76152abe68c439aa087a4e0d748a96` |
| `data/id_deprecations.json` | `975d94c7922b41b3dadf7a2be776e516f4571eac417487ba04d87b15f04c502` |
| `ingest/aiaaic_sheet_incidents.json` | `0f878558f6784fdce78dd9f555db475b64cb1bb272f140fdc828d6b204bc374` |

(Second-run `render_docs_stats.py` reported "all doc surfaces already match
`data/stats.json` (no-op)" — confirming the first run's template pass was
already idempotent.) `python -m pytest -q` and `check_stats_drift.py` were also
re-run clean after the second build. **`data/id_deprecations.json` is
byte-identical to the pre-batch committed version** (992 entries, no diff) —
expected, since this batch adds 0 removed/deprecated IDs.

## 3. Full-corpus field-level delta (before = pre-batch committed
`data/incidents.json`, after = this rebuild)

### 3.1 Entry count / ID set — checked in both directions

| | Before | After |
|---|---|---|
| Entry count | 13,115 | 13,119 |
| Corpus total (incl. this run's dedup pass) | — | `18,736 input -> 13,119 unique` |

- `{ids in before} - {ids in after}` (removed) = **∅ (0)**
- `{ids in after} - {ids in before}` (added) = **{INC-14601, INC-14602,
  INC-14603, INC-14604} (4)**
- `{ids in before} ∩ {ids in after}` (common) = **13,115** — exact set equality
  on this subset, verified by direct set difference, not just a count match.

**All 4 added IDs are attributable to upstream AIAAIC growth, not to any
merge/dedupe behavior change:** each carries `source_ids` = a single, previously
unseen `AIAAIC22xx` slug (`AIAAIC2265`–`AIAAIC2268`), `description_source ==
"aiaaic"`, a populated `content_license`, and `quality_tier: "auto"` /
`tier: "feed"` (none is `landmark`). They are new rows in AIAAIC's live sheet
that did not exist in the 2026-07-17 cache the dry run measured. The §5
relative criterion ("the reduction itself adds or removes ZERO entries") is
satisfied: the reduction/decoupling code added or removed nothing; the four
new entries come from new upstream source rows, the same class of change any
non-WS0-T3 AIAAIC refresh would have produced.

| ID | Title | source_ids |
|---|---|---|
| INC-14601 | WebinarTV secretly records and turns meetings into podcasts | AIAAIC2268 |
| INC-14602 | Hackers use Meta AI support chatbot to takeover Instagram accounts | AIAAIC2267 |
| INC-14603 | OpenAI models escape test, hack Hugging Face for answers | AIAAIC2266 |
| INC-14604 | Kimberlee Williams wrongly arrested by police using facial recognition | AIAAIC2265 |

### 3.2 landmark_count (derived: count of `tier=="landmark"`)

| Before | After | Changed |
|---|---|---|
| 1,905 | 1,905 | **0** |

Unchanged even though the corpus grew by 4 — none of the 4 new entries is
landmark-tier (confirmed directly, all four are `tier: "feed"`).

### 3.3 Per-field changed-entry counts — full 45-field sweep, common IDs only
(13,115 entries present in both before and after; the 4 newly-added IDs are
covered separately in §3.1/§3.6, not counted as "changed" here since they have
no "before" state to diff against)

| Field | Entries changed | | Field | Entries changed |
|---|---|---|---|---|
| `added` | 0 | | `mitigations` | 0 |
| `affected` | **1** — see §3.5 | | `mitre_atlas` | 0 |
| `aiid_id` | 0 | | `mitre_atlas_tactics` | 0 |
| `attack_vector` | **2** — see §3.4 | | `nist_ai_rmf` | 0 |
| `capec_ids` | 0 | | `owasp_asi` | 0 |
| `category` | 0 | | `owasp_dsgai` | 0 |
| `confidence` | 0 | | `owasp_llm` | 0 |
| `content_license` | **1,418** — see §3.6 | | `purl` | 0 |
| `corpus` | 0 | | `quality_tier` | 0 |
| `cve_ids` | 0 | | `references` | 0 |
| `cvss_score` | 0 | | `reversibility_class` | 0 |
| `cvss_vector` | 0 | | `severity` | 0 |
| `cwe_ids` | 0 | | `source_count` | 0 |
| `date` | 0 | | `source_ids` | 0 |
| `description` | **1,418** — see §3.6 | | `source_status` | 0 |
| `description_provenance` | **1,418** — see §3.6 | | `tags` | 0 |
| `description_source` | **1,418** — see §3.6 | | `tier` | 0 |
| `discovery_method` | 0 | | `title` | 0 |
| `exploited_in_wild` | 0 | | `updated` | **1,418** — see §3.6 |
| `first_seen` | 0 | | `year` | 0 |
| `id` | 0 | | | |
| `impact` | 0 | | | |
| `kev_date_added` | 0 | | | |
| `last_seen` | **1,418** — see §3.6 | | | |
| `maestro_layers` | 0 | | | |

**37 of 45 fields: exactly 0 changes** — includes every OWASP/ATLAS/NIST
taxonomy field, `severity`, `corpus`, `quality_tier`/`tier`, and the structural
fields (`id`, `title`, `tags`, `source_ids`, `references`, `added`,
`first_seen`, etc.). **8 fields non-zero:** `attack_vector` (2, both
pre-justified — §3.4), the six description/marker/timestamp fields sticky to
the D9/D11(b) reduction (1,418 each, all the **same** 1,418-entry set — §3.6),
and `affected` (1, a genuine new finding — §3.5).

### 3.4 `attack_vector` — the two residual deltas, identical to the approved preview

| ID | Before | After |
|---|---|---|
| INC-02406 | `unsafe-advice` | `other` |
| INC-04316 | `algorithmic-bias` | `other` |

Same two IDs, same before/after values as
`docs/audits/WS0-T3-validation-sample-2026-07-27.md` §3.3/§4 rows 3–4. No new
root-causing needed — the preview's ablation (dropped `purpose` prose for
INC-02406; a spurious title/description regex-boundary artifact for INC-04316,
now genuinely eliminated by the new `title + seed` classify-text shape) applies
unchanged, since these are the same two upstream rows with the same raw cells.
Neither entry's `owasp_llm`/`owasp_asi`/`mitre_atlas`/`mitre_atlas_tactics`/
`nist_ai_rmf`/`corpus`/`tier` changed (all captured as 0 in §3.3's sweep).

### 3.5 `affected` — one new divergence not predicted by the preview, root-caused

`INC-07735` ("Meta captures employee mouse movements to train AI models",
`source_ids: ["AIAAIC2264"]`) is the sole entry where `affected` changed:
`"Meta"` → `"Meta Platforms"`.

**Root cause: legitimate upstream content edit, not a code defect.** Every
other field on this entry that the description reduction could plausibly touch
is unchanged — `attack_vector: other` (before and after), `corpus: security`,
`tier: feed`, `owasp_llm: [LLM07]`, `mitre_atlas: [AML.T0056]`,
`nist_ai_rmf: [MEASURE-2.7]`, `severity: Medium`, all identical. This entry
**is** part of the 1,418-entry re-described set (its `description`,
`description_provenance`, `description_source`, `content_license`, `updated`,
`last_seen` all changed exactly as expected for an AIAAIC-dedup-target row —
confirmed by direct lookup, see the full before/after field dump below).
`affected` is derived at ingest time from
`(row["developer"] or row["deployer"] or row["system"]).strip()`
(`scripts/ingest_aiaaic_sheet.py`) — a raw-cell fact, not something the WS0-T3
reduction or seed-decoupling touches at all. The only way this field's *value*
changes between the 2026-07-17 cache and this live fetch is if AIAAIC itself
edited the `developer`/`deployer`/`system` cell for row `AIAAIC2264` in the
eleven days between snapshots (e.g. correcting "Meta" to the more formal "Meta
Platforms"). This is upstream drift on a live-fetched row — precisely the class
of divergence D16 designates as legitimate and requires attributing, not a
defect in the reduction or the label-seed decoupling. It is also a useful
confirmation of correctness: taxonomy fields correctly did **not** move even
though a non-taxonomy fact on the same row changed, showing the decoupled
classifiers are keyed off the fields they claim to be keyed off, not
indiscriminately off row identity.

Full before/after field dump for `INC-07735` (every field, not just the
changed ones):

```
added                   : 2026-06-10                          (same)
affected                : Meta                => Meta Platforms   <-- CHANGED
attack_vector           : other                                (same)
category                : real-world                           (same)
confidence              : low                                  (same)
content_license         : (absent) => {source: aiaaic, license: CC-BY-SA-4.0, ...}  <-- CHANGED (expected, part of the 1,418)
corpus                  : security                              (same)
date                    : 2026                                  (same)
description             : "AIAAIC report: Meta captures..." => "AIAAIC-tracked incident. Technology: Agentic AI; Generative AI. Sector: Technology. Jurisdiction: USA."  <-- CHANGED (expected)
description_provenance  : (absent) => original                  <-- CHANGED (expected)
description_source      : (absent) => aiaaic                     <-- CHANGED (expected)
first_seen              : 2026-06-10                            (same)
id                      : INC-07735                              (same)
last_seen               : 2026-06-10 => 2026-07-28               <-- CHANGED (expected)
mitre_atlas             : [AML.T0056]                            (same)
mitre_atlas_tactics     : [AML.TA0010]                           (same)
nist_ai_rmf             : [MEASURE-2.7]                          (same)
owasp_asi               : []                                     (same)
owasp_llm               : [LLM07]                                (same)
quality_tier            : auto                                   (same)
references              : [AIAAIC entry, .../meta-...]           (same)
severity                : Medium                                 (same)
source_count            : 1                                      (same)
source_ids              : [AIAAIC2264]                            (same)
source_status           : active                                 (same)
tags                    : [aiaaic, aiaaic-sheet, sector-technology, juris-usa]  (same)
tier                    : feed                                   (same)
title                   : Meta captures employee mouse movements to train AI models  (same)
updated                 : 2026-06-10 => 2026-07-28               <-- CHANGED (expected)
year                    : 2026                                   (same)
```

### 3.6 The intended (D9/D11(b)) deltas — 1,418 entries, one exact set

| Field | Entries changed |
|---|---|
| `description` | 1,418 |
| `description_provenance` | 1,418 |
| `description_source` | 1,418 |
| `content_license` | 1,418 |
| `updated` | 1,418 |
| `last_seen` | 1,418 |

**Verified programmatically that all six are the exact same 1,418-ID set**
(not merely the same count) — direct set-equality check, all six pairwise
comparisons `True`. `generated` (top-level, single value): `2026-07-19` →
`2026-07-28` (this run's build date), following the same
`_CONTENT_FIELDS`/`_apply_history` mechanism the validation-sample document's
§3.4 describes (`description` is one of the content fields that decides
`updated`; `last_seen` follows `updated`; `generated` moves once any entry
changed). This is invariant-4 **compliant**: the description content genuinely
changed for these 1,418 rows.

### 3.7 D11(b) marker coverage (spec §6.2)

| Check | Result |
|---|---|
| `description_source=="aiaaic"` entries (full corpus, incl. the 4 new rows) | **1,422** |
| ...of which carry `content_license` | **1,422 / 1,422 (100%)** |
| Non-AIAAIC entries carrying `content_license` | **0** |
| Distinct `content_license` object shapes among marked rows | **1** (single literal object, `source: aiaaic`, `license: CC-BY-SA-4.0`, `obligations: [attribution, share-alike]` — identical across all 1,422, per the schema doc's corpus-wide-not-per-row design) |
| `data/incidents.min.json` entries carrying `content_license` | **1,422 / 13,119** — matches the full record exactly (D12(a): marker included in the slim projection) |
| `data/incidents.min.json` entries carrying `description_source` at all | **0** — confirms the slim schema still excludes this field entirely (unrelated to the marker; verified so the two aren't conflated) |
| Internal seed fields (`aiaaic_ethical_tags`, `aiaaic_seed_facts`) leaking into `data/incidents.json` or `data/incidents.min.json` | **0** |
| `python scripts/validate.py` | 13,119/13,119 valid, 0 errors |

1,422 = the 1,418 re-described existing rows (§3.6) + the 4 newly-added rows
(§3.1), all four of which are AIAAIC-origin and ship with the marker from
first ingest.

### 3.8 D10 prose-marker grep — committed `ingest/*.json` + `data/*.json`

Acceptance per spec §2(a): grep the five cell markers (`AIAAIC report:` /
`Purpose:` / `Ethical issues:` / `Reported consequences:` / `Response:`) across
every committed `ingest/*.json` and `data/*.json`; requires 0.

Raw `grep -rl` file-level hit count:

| Marker | Files with ≥1 hit |
|---|---|
| `AIAAIC report:` | 0 |
| `Purpose:` | 0 |
| `Ethical issues:` | 0 |
| `Reported consequences:` | 0 |
| `Response:` | 3 (`data/incidents.json`, `ingest/cve_nvd_expanded.json`, `ingest/atlas_full.json`) |

**The 3 `Response:` file hits, and the 8 corpus-wide `description`-field hits
they resolve to, are all false positives unrelated to AIAAIC** — a naive
substring grep across a 13,119-entry, 20-source corpus will always collide
with generic English words. Verified directly: every one of the 8 hits is a
CVE/vulnerability write-up (Kimai, pyload, dagu, PraisonAI, LXD, Cadwyn,
Directus/Refit — `INC-08651`, `INC-08666`, `INC-09388`, `INC-09531`,
`INC-10187`, `INC-10356`, `INC-10725`, `INC-10774`) whose proof-of-concept
prose contains "Response:" as an HTTP-response label, e.g. `"Response: HTTP 200
— returns full timesheet record..."`. None has `description_source == "aiaaic"`
or any AIAAIC `source_ids`. A precise, per-entry check —
scanning only `description` fields where `description_source == "aiaaic"`,
and separately the two committed AIAAIC ingest files
(`ingest/aiaaic_sheet_incidents.json`, `ingest/aiaaic_incidents.json`) for any
of the five markers — returns **0 hits in every case**. D10 holds.

## 4. Preview vs. actual — explicit reconciliation

The approved preview (`docs/audits/WS0-T3-validation-sample-2026-07-27.md`
§3, dry run against a 2026-07-17 cache) predicted the following; this section
states the actual measured result and attributes every difference.

| Metric | Preview (2026-07-17 cache) | Actual (2026-07-28 live) | Match? | Attribution |
|---|---|---|---|---|
| Entry count | 13,115 → 13,115 | 13,115 → 13,119 | **Diverges (+4)** | 4 new AIAAIC rows added to the live sheet since 2026-07-17 (§3.1). Legitimate upstream drift, foreseen and pre-approved by D16: "entry counts may legitimately move; any movement must be enumerated and attributed to upstream drift." |
| IDs removed | 0 | 0 | **Matches** | — |
| IDs added | 0 | 4 | **Diverges** | Same 4 rows as above; not a merge/dedupe behavior change (§3.1). |
| `landmark_count` | 1,905 → 1,905 (0 changed) | 1,905 → 1,905 (0 changed) | **Matches** | The 4 new rows are all `tier: feed`, not `landmark`, so the count is unaffected even though corpus size grew. |
| `owasp_llm`/`owasp_asi`/`mitre_atlas`/`mitre_atlas_tactics`/`nist_ai_rmf`/`owasp_dsgai`/`severity`/`corpus`/`quality_tier`/`tier` | 0 changed, all 10 fields | 0 changed, all 10 fields (common IDs) | **Matches exactly** | — |
| `attack_vector` | 2 changed (INC-02406, INC-04316), both →`other` | 2 changed, same 2 IDs, same before/after values | **Matches exactly** | Same upstream rows, same root cause as the preview's §3.3 ablation. |
| `description`/`description_provenance`/`description_source`/`content_license` | 1,418 each, same set | 1,418 each, same set (verified set-identical across all 4 fields) | **Matches exactly** | — |
| `updated`/`last_seen` | 1,418, same set | 1,418, same set | **Matches exactly** | — |
| top-level `generated` | moves | `2026-07-19` → `2026-07-28` | **Matches (mechanism)** | Expected consequence of the 1,418 content changes. |
| `affected` | not enumerated (preview's §3.2 table did not name it as a changed field; its §3 scope claims all 45 fields swept, 38 unnamed = unchanged) | **1 changed** — INC-07735, `Meta`→`Meta Platforms` | **New divergence** | Root-caused in §3.5: AIAAIC edited the underlying `developer`/`deployer` cell for `AIAAIC2264` between the two fetches. Not a reduction/decoupling defect — confirmed by this same entry's taxonomy fields staying unchanged. This is exactly the "new/changed AIAAIC rows upstream" case D16 anticipated, on a field the preview's dry run had no opportunity to observe changing (its cache was frozen, so no upstream edits could show up in it). |
| D10 marker grep | 0 (against the 2026-07-17-cache-derived files) | 0 (against AIAAIC-derived content specifically); 3 files / 8 entries raise false positives from unrelated CVE content that did not exist in the smaller 2026-07-17-era corpus | **Matches (AIAAIC scope); explained (raw grep noise)** | The corpus has grown with new CVE/NVD ingests since the preview was written; a literal `Response:` substring match was always going to pick up incidental hits outside AIAAIC content as the corpus grows. Confirmed none are AIAAIC-sourced. |

**Summary verdict: no defect found.** Every divergence from the preview
resolves to legitimate upstream AIAAIC content drift over the eleven days
between the 2026-07-17 cache and this live 2026-07-28 fetch (4 new rows, 1
edited cell on an existing row), plus one grep-noise artifact from the
corpus's unrelated growth in other sources. Nothing indicates the reduction
itself moved a taxonomy label, added/removed an entry through its own logic,
or leaked AIAAIC prose. The §2(c) zero-unintended-taxonomy-delta bar and the §5
relative entry-count criterion both hold.

## 5. What is NOT touched by this batch

Confirmed via `git status --porcelain -- schema/ scripts/export_stix.py
NOTICE-DATA .reuse/dep5 .zenodo.json docs/DATA_DICTIONARY.md` returning empty:

- `scripts/export_stix.py` — the `x_content_license` heuristic-retirement work
  is sequenced after this batch per D15, not touched here.
- `schema/` and its packaged copy — no schema change; the D11(b) conditional
  landed with Phase A and is unmodified.
- `NOTICE-DATA`, `.reuse/dep5`, README's licensing-status text — unmodified.
  (README's only diff is the `stats:incident_count` marker, `13,115`→`13,119`,
  the standard invariant-6 render_docs_stats.py mechanism — not a licensing
  text change.)
- `.zenodo.json` — unmodified.
- `docs/DATA_DICTIONARY.md` — unmodified (Phase A's `ab3e7cf4` already covered
  `content_license`/`description_provenance`/`description_source`).

## 6. Files changed by this batch (build outputs only)

```
 M INCIDENTS.md
 M README.md                          (stats marker only)
 M data/incidents.json
 M data/incidents.min.json
 M data/stats.json
 M docs/DATASHEET.md                  (stats marker only)
 M docs/charts/owasp_asi.svg
 M docs/charts/owasp_llm.svg
 M docs/charts/severity_stack.svg
 M docs/charts/year_bar.svg
 M docs/data/incidents.min.json
 M docs/incidents/2008.md .. 2026.md  (19 year-shard files — the 1,418
                                        re-described + 4 new entries span
                                        this full year range)
 M docs/index.html                    (stats marker only)
 M ingest/aiaaic_sheet_incidents.json
 M src/genai_incidents/data/incidents.min.json
```

`data/id_deprecations.json` is unchanged (byte-identical, 992 entries) — no
diff, not listed above.

## 7. Open item flagged, not fixed (out of this batch's scope)

Spec `docs/specs/WS0-T3-rescoped-2026-07-18.md` §5 carries an unchecked
acceptance line: *"Committed AIAAIC live-total-row-count logging present
(denominator for any substantiality re-check)"* (§2(e)). Today
`ingest_aiaaic_sheet.py` only prints the raw-row and retained-row counts to
stdout (`print(f"[aiaaic] {len(rows)} raw rows")` and the "wrote N... (skipped
M)" line); nothing persists them to a committed file. This predates Phase B and
is not something the team-lead's brief for this batch asked me to build —
flagging it here rather than implementing it mid-batch (scope discipline per
the brief's explicit file list). This run's own numbers for the record: 2,258
raw rows, 1,504 retained, 751 skipped, fetched 2026-07-28T23:26:32Z.

## 8. Verification recipe

```
python scripts/ingest_aiaaic_sheet.py    # live fetch, ~2258 raw rows -> ~1504 retained
python scripts/parse_existing.py
python scripts/merge_and_dedupe.py       # 13119 unique
python scripts/render_markdown.py
python scripts/render_docs_stats.py
python scripts/validate.py               # 13119/13119 valid, 0 errors
python scripts/check_stats_drift.py      # clean
python -m pytest -q                      # 227 passed
```

Re-running `parse_existing.py` → `merge_and_dedupe.py` → `render_markdown.py` →
`render_docs_stats.py` → `validate.py` a second time (without re-fetching)
against the already-fetched `ingest/aiaaic_sheet_incidents.json` reproduces
`data/incidents.json`, `data/incidents.min.json`, `INCIDENTS.md`,
`data/stats.json`, and `data/id_deprecations.json` byte-for-byte (SHA-256
listed in §2). Re-fetching (`make ingest-aiaaic`) again will legitimately move
the entry count further if AIAAIC's live sheet has changed again — that is
expected behavior per D16, not a determinism failure; determinism is a
property of the build steps downstream of a given ingest snapshot, not of the
live fetch itself.
