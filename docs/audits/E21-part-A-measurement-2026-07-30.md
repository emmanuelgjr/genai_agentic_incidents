# E21 Part A — standalone re-derivation of the pre-reduction measurement

**Written 2026-07-30 by pipeline-engineer, as Deliverable 2 of the E21
named-additions task** (brief: two things E21's original batch did not
deliver — the INC-00437 relabel, and this file). **Status: a re-derivation,
not a transcription.** Per the working agreement — *"a commit message is not
an artifact"* — `3c1e3e9e`'s commit message is the only place Part A's
numbers existed before this file. Every figure below was independently
re-derived from committed revisions with the commands/code shown; none is
copied from the commit message. Where a number is confirmed, that is stated
as a match, not assumed.

## Why this file exists separately from the commit message

`3c1e3e9e`'s message states, in full:

> Part A (measurement): description_provenance is null/absent on 11,697/13,119
> rows (structural -- AIAAIC-only mechanism). Join-and-search (E16/E23 method)
> against both OECD ingest files confirms the reduction population is 3,726
> (3,667 main file + 59 orphan file), matching E21's defect-2 correction
> exactly, and confirms INC-00437 is the ONLY row whose aiid_id/source_ids
> signal AIID while its shipped content is actually OECD-derived (re-run of
> E23's AIID-template check: still exactly 2 exceptions today, 898 and 1574).

Four separate claims are packed into that paragraph. Each is re-derived below
against the actual committed files, following the E16/E23 join-and-search
method those tasks established (join corpus rows back to the pinned upstream
artifact, search every field, count exact/near matches, report anything a
totals-only summary would miss).

**Bottom line up front, stated plainly per the committed-artifact rule's own
instruction to flag disagreements prominently rather than bury them: all four
claims re-derive to the exact same numbers the commit message reported. No
disagreement found.** This is unlike the foreman's independent field-level
delta (`docs/audits/E21-reduction-delta-2026-07-30.md`), which found two
prose-level discrepancies elsewhere in the same commit message (an undeclared
`owasp_llm` field, and an off-by-one in the `updated`/`last_seen`
reconciliation) — this file's four claims are not among those two, and none
of them re-derives to a different number.

---

## 1. `description_provenance` null/absent on 11,697/13,119 rows

**Claim:** null/absent on 11,697 of 13,119 rows, and this is structural — an
AIAAIC-only mechanism (no other ingest path sets the field at all).

**Why pre-batch (`804cb6ee`), not post-batch:** the denominator (13,119)
matches the corpus row count *before* the E21 batch ran (post-batch is
13,060, per `docs/audits/E21-reduction-delta-2026-07-30.md` §1) — this
measurement was taken against the corpus as it stood going into the batch,
before the reduction and orphan-retirement changed the row count.

```python
import subprocess, json
def show(rev, path):
    out = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True)
    return json.loads(out.stdout.decode("utf-8"))

pre = show("804cb6ee", "data/incidents.json")
pre_rows = pre["incidents"] if isinstance(pre, dict) else pre
print(len(pre_rows))  # 13119

present = sum(1 for r in pre_rows if r.get("description_provenance"))
absent = len(pre_rows) - present
print(present, absent)  # 1422 11697

from collections import Counter
print(Counter(r.get("description_source") for r in pre_rows
              if r.get("description_provenance")))
# Counter({'aiaaic': 1422})
```

**Result:**

| Measure | Value |
|---|---|
| Rows total (pre-batch, `804cb6ee`) | 13,119 |
| `description_provenance` present | 1,422 |
| `description_provenance` null/absent | **11,697** |
| `description_source` values among the 1,422 present | `aiaaic` — **100%**, 0 other values |

**Match: exact.** 11,697/13,119, confirmed absent everywhere except a single
source mechanism (`aiaaic`), confirming the "structural, AIAAIC-only
mechanism" characterization. Grep-level corroboration: `description_provenance`
is set in exactly one place in `scripts/` outside the pass-through added by
this same batch (`scripts/ingest_aiaaic_sheet.py:540`,
`"description_provenance": "original"`) — no OECD, AIID, CVE, ATLAS, or any
other ingest path calls anything equivalent before this batch's own
`description_source: "oecd-aim"` addition (see §4 below, which is scoped to
one row and does not change this section's population).

---

## 2. Join-and-search: the reduction population is 3,726 (3,667 + 59)

**Claim:** joining against both OECD ingest files gives a combined
narrative-reduction population of 3,726 — 3,667 rows in
`ingest/oecd_aim_full_incidents.json` plus 59 in the retired
`ingest/oecd_aim_incidents.json` — matching "E21's defect-2 correction."

**On "defect-2":** nothing recoverable in this session names what internal
defect-numbering scheme `3c1e3e9e`'s message refers to (the session that
produced it died before any board record survived — see
`docs/audits/E21-reduction-delta-2026-07-30.md`'s own account of the crash).
This file does not attempt to reconstruct that label; it re-derives the two
population numbers on their own terms and confirms they sum to the same
3,726 the message claims, independent of what "defect-2" originally named.

**Method — two separate joins, not one, because the two ingest files were
retired differently** (the main file was reduced in place; the orphan file
was retired wholesale, per `docs/audits/E21-reduction-delta-2026-07-30.md`
§4/§6):

### 2a. The 3,667 figure — corpus rows whose description changed, joined back to `oecd_aim_full_incidents.json` by `source_id`

A naive raw-file count is the wrong number here: every one of
`oecd_aim_full_incidents.json`'s 4,160 rows had its OWN description text
rewritten by the migration script (`scripts/migrate_oecd_description_reduction.py`),
not just 3,667. The 3,667 figure is a **corpus-level** count — how many of
those 4,160 rewritten ingest rows are also the row whose content actually won
the merge and became a corpus row's shipped description — established by a
real join, not asserted from the ingest-file total:

```python
pre_corpus = show("804cb6ee", "data/incidents.json")["incidents"]
post_corpus = show("3c1e3e9e", "data/incidents.json")["incidents"]
pre_by_id = {r["id"]: r for r in pre_corpus}
post_by_id = {r["id"]: r for r in post_corpus}

changed_desc_ids = [i for i in pre_by_id if i in post_by_id
                    and pre_by_id[i]["description"] != post_by_id[i]["description"]]
print(len(changed_desc_ids))  # 3667

oecd_full = show("804cb6ee", "ingest/oecd_aim_full_incidents.json")
oecd_full_ids = set(r["source_id"] for r in oecd_full)

joined = sum(1 for i in changed_desc_ids
             if set(pre_by_id[i].get("source_ids") or []) & oecd_full_ids)
print(joined)  # 3667 -- every changed-description row joins, 0 unjoined
```

| Measure | Value |
|---|---|
| `oecd_aim_full_incidents.json` rows whose OWN description text the migration script rewrote | 4,160 (100% of the file) |
| Corpus rows whose `description` field changed (`804cb6ee` → `3c1e3e9e`) | 3,667 |
| Of those, joined back to `oecd_aim_full_incidents.json` by `source_id` | **3,667 / 3,667 — 100%, 0 unjoined** |

The gap between 4,160 (every ingest row rewritten) and 3,667 (corpus rows
whose *shipped* description actually changed) is explained by ordinary
dedup/merge mechanics: not every raw OECD ingest row survives as its own
corpus row's merge target (some lose a dedup collision to a different
source's row, whose description field is untouched by this migration and
therefore doesn't move). This is expected, not a discrepancy — the 3,667
figure the commit message reports is explicitly the corpus-level number, and
that is exactly what this join reproduces.

### 2b. The 59 figure — orphan-file rows, all tombstoned, none partially retained

```python
orphan = show("804cb6ee", "ingest/oecd_aim_incidents.json")
orphan_ids = set(r["source_id"] for r in orphan)
print(len(orphan_ids))  # 86

removed_ids = set(pre_by_id) - set(post_by_id)
print(len(removed_ids))  # 59

removed_source_sets = [set(pre_by_id[i].get("source_ids") or []) for i in removed_ids]
print(all(s <= orphan_ids for s in removed_source_sets))       # True
print(set(len(s) for s in removed_source_sets))                # {1}
```

| Measure | Value |
|---|---|
| `ingest/oecd_aim_incidents.json` rows (orphan file, pre-retirement, `804cb6ee`) | 86 |
| Corpus rows removed (`804cb6ee` → `3c1e3e9e`) | 59 |
| Removed rows' `source_ids` — subset of the orphan file's IDs? | **Yes, 100%** |
| Removed rows' `source_ids` set size | **{1}** — every removed row had the orphan file as its ONLY source |
| Reconciliation: 86 orphan rows = 59 removed + 27 cross-covered-and-kept | 59 + 27 = 86 ✓ |

Every one of the 59 removed corpus rows had the (now-retired) orphan file as
its sole surviving source — confirming these are genuinely orphan-only rows,
not a coincidental count. The remaining 27 orphan rows are the
cross-covered-and-kept population `docs/audits/E21-reduction-delta-2026-07-30.md`
§2 already measured (present in both revisions, losing only orphan-contributed
fields) — 59 + 27 = 86, the orphan file's full row count, with no unaccounted
remainder.

### 2c. Sum and match

| Component | Value |
|---|---|
| Main file, corpus-level, real join | 3,667 |
| Orphan file, real join | 59 |
| **Sum** | **3,726** |

**Match: exact**, and — unlike a totals-only check — both halves are
independently confirmed by a real join against `source_id`/`source_ids`, not
by the two numbers merely summing to the claimed total.

---

## 3. INC-00437 is the ONLY row whose AIID signal disagrees with its OECD-derived content

**Claim:** INC-00437 (`aiid_id` 1574) is the one row in the corpus whose
`aiid_id`/`AIID-<n>` source-ID signal says "this has an AIID counterpart"
while the description that actually ships is OECD's own template, not
AIID's.

**Method:** a real in-process repro of the merge pipeline
(`scripts/merge_and_dedupe.py`'s own `normalize_entry()`/`dedupe_entries()`,
imported and run directly — the same read-only, no-network, no-`data/*.json`-write
method `tests/test_e21_partA_inc00437_provenance.py` and
`tests/test_e23_aiid_dead_letter_tripwire.py` both use), restricted to the two
ingest files that can jointly produce this disagreement class:
`ingest/aiid_full.json` (the only file that can supply real AIID content for
an `AIID-<n>` key) and `ingest/oecd_aim_full_incidents.json` (the only file
that attaches an `AIID-<n>` cross-reference to OECD's own content, via
`normalize_body()`'s `aiid_ids` → `extra_source_ids` mechanism).

```python
import sys; sys.path.insert(0, "scripts")
import merge_and_dedupe as m, json, re

raw = json.loads(open("ingest/aiid_full.json", encoding="utf-8").read())
raw += json.loads(open("ingest/oecd_aim_full_incidents.json", encoding="utf-8").read())
normalized = [n for n in (m.normalize_entry(r) for r in raw) if n is not None]
surviving, _ = m.dedupe_entries(normalized)

TEMPLATE = re.compile(r"^AI Incident Database \(AIID\) entry #\d+: ")
aiid_rows = [e for e in surviving if e.get("aiid_id")]
exceptions = [e for e in aiid_rows if not TEMPLATE.match(e.get("description", ""))]
print(len(surviving), len(aiid_rows), len(exceptions))
# 5195 1524 1
print([(e["aiid_id"], e["source_ids"]) for e in exceptions])
# [(1574, ['AIID-1574', 'OECD-AIM-2026-04-03-c16a'])]
```

**Result: exactly one row — `aiid_id` 1574 / INC-00437.**

**A wrinkle worth recording, because a naive version of this check
over-counts by 3×:** a *raw per-row* join (checking each OECD ingest row's
claimed `AIID-<n>` cross-reference against `aiid_full.json`'s ID set,
*without* running the actual dedup/merge) finds **four** OECD rows whose
claimed AIID ID isn't (yet) in `aiid_full.json`, not one:

```python
oecd = json.loads(open("ingest/oecd_aim_full_incidents.json", encoding="utf-8").read())
aiid = json.loads(open("ingest/aiid_full.json", encoding="utf-8").read())
aiid_ids_present = {int(r["source_id"].split("-",1)[1]) for r in aiid
                     if r.get("source_id","").startswith("AIID-")}
disagreements = [(r["source_id"], int(e.split("-",1)[1]))
                 for r in oecd for e in (r.get("extra_source_ids") or [])
                 if e.startswith("AIID-") and int(e.split("-",1)[1]) not in aiid_ids_present]
print(disagreements)
# [('OECD-AIM-2026-01-21-eb71', 1575), ('OECD-AIM-2026-03-24-d861', 1568),
#  ('OECD-AIM-2026-04-03-c16a', 1574), ('OECD-AIM-2026-07-06-b9aa', 1582)]
```

Three of those four (1575, 1568, 1582) are **not** corpus-level
disagreements: each merges, via title/URL/fuzzy-title dedup, into a *different*
corpus row that also carries a *different* `AIID-<n>` id that **does** exist
in `aiid_full.json` — e.g. `OECD-AIM-2026-01-21-eb71`'s claimed `AIID-1575`
lands on corpus row INC-05013, whose final `source_ids` also include
`AIID-1436` (which does exist in `aiid_full.json`), and whose `aiid_id`
resolves to 1436 with a description matching AIID's own template exactly —
no disagreement, because that row's `aiid_id` **is** backed by real AIID
content, even though it also carries a second, dangling `AIID-1575`
cross-reference that happens not to resolve to anything. Only
`OECD-AIM-2026-04-03-c16a` (1574 / INC-00437) has no other AIID-<n> id to
fall back on and genuinely surfaces as a corpus-level disagreement once
dedup runs. **This is why the join-and-search method requires running the
real merge, not a raw file-level join** — the same lesson E16 and E23 both
drew for their own populations, now confirmed a third time on a different
population.

**Match: exact** (one row, `aiid_id` 1574).

---

## 4. Re-run of E23's AIID-template check: still exactly 2 exceptions

**Claim:** re-running E23's own check (`docs/audits/E23-aiid-scope-measurement-2026-07-30.md`
§3(i)) against the post-batch corpus still finds exactly 2 exceptions to the
AIID-template match among all `aiid_id`-bearing rows: `aiid_id` 898 and 1574.

```python
post = show("3c1e3e9e", "data/incidents.json")
post_rows = post["incidents"] if isinstance(post, dict) else post
TEMPLATE = re.compile(r"^AI Incident Database \(AIID\) entry #\d+: ")
aiid_rows = [r for r in post_rows if r.get("aiid_id")]
exceptions = [r for r in aiid_rows if not TEMPLATE.match(r.get("description",""))]
print(len(aiid_rows), len(exceptions))         # 1465 2
print([(r["id"], r["aiid_id"]) for r in exceptions])
# [('INC-08183', 898), ('INC-00437', 1574)]
```

| `aiid_id` | corpus id | why it's an exception |
|---|---|---|
| 898 | INC-08183 | content is a research-blog-sourced entry (Embrace the Red / Bard exfiltration), not AIID's and not OECD's — a different exception class, unrelated to E21 |
| 1574 | INC-00437 | content is OECD AIM's own template — the row this task's Deliverable 1 relabels |
| — | — | **2 of 1,465, exact match to the commit message's claim** |

**Distinguishing the two exceptions, since only one is in E21's population:**
of the two, only `INC-00437` carries an `OECD-AIM-*` source_id
(`INC-08183`'s source_ids are `AIID-898`/`ATLAS-*`/`EXT-2024-HF-MALICIOUS-MODELS`/
`RES-etr-bard-exfil-2023` — no OECD reference at all). This is the same check
§3 above used to isolate INC-00437 as the unique OECD-content disagreement,
cross-referenced here against the full-corpus (not two-file-restricted)
population to confirm nothing else changed shape between the two methods.

**Match: exact.** Re-run after Deliverable 1's fix (`data/curation_overrides.json`'s
new `OECD-AIM-2026-04-03-c16a` entry) reproduces the identical 2/1,465 —
expected, since that fix only adds `description_provenance`/`description_source`
metadata and never touches `description` text itself.

---

## 5. Summary table

| # | Claim (from `3c1e3e9e`'s commit message) | Re-derived value | Match? |
|---|---|---|---|
| 1 | `description_provenance` null/absent on 11,697/13,119, AIAAIC-only mechanism | 11,697/13,119; 1,422 present, 100% `aiaaic` | ✅ exact |
| 2 | Reduction population 3,726 = 3,667 (main file) + 59 (orphan file) | 3,667 (real join, 0 unjoined) + 59 (real join, all singleton-orphan-sourced) = 3,726 | ✅ exact |
| 3 | INC-00437 is the ONLY row whose AIID signal disagrees with OECD-derived content | 1 row (`aiid_id` 1574) via real-pipeline repro; naive raw join over-counts to 4, explained | ✅ exact |
| 4 | Still exactly 2 AIID-template exceptions today (898, 1574) | 2/1,465 (898, 1574); only 1574 carries an OECD source | ✅ exact |

**No disagreement found in any of the four Part A claims.** This is a
different finding from `docs/audits/E21-reduction-delta-2026-07-30.md`, which
found two (unrelated, prose-level) discrepancies in the same commit message's
delta-reporting paragraph — those are about the field-level delta of Part
B/C, not about Part A, and are already recorded in that file.

## What this file does NOT establish

- It does not re-verify Part B's or Part C's own field-level delta — that is
  `docs/audits/E21-reduction-delta-2026-07-30.md`'s job and is already done
  there.
- It does not re-assess the licensing judgement behind the reduction
  (whether OECD's summary/evidences text is safely redistributable) — that
  was `docs/audits/E21-oecd-narrative-licence-2026-07-30.md`'s call, not
  re-opened here.
- It is not a gate verdict. Acceptance criteria, invariant sweep, and stray
  checks are red-reviewer's job.
