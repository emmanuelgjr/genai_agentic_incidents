# E21 OECD narrative reduction — independent field-level delta

**Written 2026-07-30 by the foreman during session-recovery state reconstruction.**
**Status: evidence for a restore-vs-gate ruling. This is NOT a gate verdict.**

The previous session died with `ws4-e21-reduction` in flight. The batch had
already executed and committed to `ws4/oecd-narrative-reduction` (`3c1e3e9e`,
pushed), but it was **never gated, never merged, and never recorded on the
board** — `grep ws4/oecd-narrative-reduction PROGRESS.md` returns zero hits.
Per working agreement 2 and the WS0-T3 crash precedent, the delta is measured
and committed **before** any ruling on whether the batch is kept or restored.

## Why this file exists separately from the commit message

`3c1e3e9e`'s message contains a self-reported delta. This file records a
**foreman re-derivation from the two committed revisions**, not a transcription
of that claim. Where the two disagree, both readings are recorded below.

Method — for every field, compare `data/incidents.json` at `804cb6ee`
(pre-batch, `main`) against `3c1e3e9e` (post-batch), keyed by `id`:

```
git show 804cb6ee:data/incidents.json   # 13,119 rows
git show 3c1e3e9e:data/incidents.json   # 13,060 rows
```

## 1. Entry count and ID set

| Measure | Value | Verdict |
|---|---|---|
| Rows pre | 13,119 | — |
| Rows post | 13,060 | −59 |
| IDs **added** | **0** | ✅ none |
| IDs **removed** | **59** | all tombstoned, see §4 |

## 2. Field-level delta (rows present in both revisions)

| Field | Rows changed | Confined to the 27 orphan-merged rows? |
|---|---|---|
| `description` | **3,667** | — (this is the reduction itself) |
| `updated` | 3,682 | — (see §3) |
| `last_seen` | 3,682 | — (see §3) |
| `source_ids` | 27 | ✅ defines the set |
| `source_count` | 27 | ✅ 0 outside |
| `tags` | 26 | ✅ 0 outside |
| `nist_ai_rmf` | 21 | ✅ 0 outside |
| `mitre_atlas` | 16 | ✅ 0 outside |
| `owasp_llm` | **11** | ✅ 0 outside — **but undeclared, see §5.1** |
| `owasp_asi` | 10 | ✅ 0 outside |
| `mitre_atlas_tactics` | 10 | ✅ 0 outside |
| `severity` | 5 | ✅ 0 outside |
| `corpus` | **1** | ✅ 0 outside — INC-08170, explained §6 |
| **`attack_vector`** | **0** | ✅ **cascade fully closed** |

Every field that moved outside `description`/`updated`/`last_seen` is **100%
contained in the 27 rows whose `source_ids` changed** — i.e. the rows that were
cross-covered by AIID/OECD-AIM and lost the retired orphan file's contributed
fields. Measured as set difference, not asserted: `changed[f] − orphan27` is
empty for all ten fields.

`attack_vector` at **0** is the load-bearing number. It is the field that
silently regressed 178/4,160 rows to `other` in the specialist's own dry-run,
via `merge_and_dedupe.py`'s reclassify-from-description fallback — a *different*
keyword system from OECD's `map_taxonomy`. This is the same coupling class that
made the WS0-T3 field-cut relabel 372 AIAAIC entries (`WS0-T3-cascade-2026-07-18.md`).
It is closed here, and the downstream framework fields that `fill_taxonomy()`
would have rippled into (`owasp_llm`/`owasp_asi`/`mitre_atlas`/`nist_ai_rmf`)
show movement **only** inside the orphan-27, never in the 3,667 reduced rows.

## 3. `updated`/`last_seen` reconciliation — the commit message is off by one

`3c1e3e9e` claims: *"updated/last_seen: 3,682 = exactly description-changed
union orphan-merged-27, 0 unexplained."*

Re-derived: `description`-changed (3,667) ∪ orphan-27 (27) = **3,683**, with an
overlap of 11. Only **3,682** rows had `updated`/`last_seen` move. The union is
one larger than the set that actually changed.

**The odd row is `INC-04496`.** It is in the orphan-27 (lost source_id
`OECD-2023-02-10-4440-bing-sydney`, leaving `AIID-473`) but its `description` is
AIID-derived and did not change, so the pipeline correctly did not bump its
clocks. `updated`/`last_seen` stay `2026-07-18`.

**Direction is benign** — one *fewer* timestamp touched than the union, not one
more. There is no row whose clock moved without an explanation
(`updated − union` is empty). The defect is in the message's arithmetic, not in
the data.

## 4. Tombstones — invariant 3

| Measure | Value |
|---|---|
| `data/id_deprecations.json` pre | 992 |
| `data/id_deprecations.json` post | 1,051 |
| New entries | **59** |
| Reason (all 59) | `orphaned-ingest-source-retired` |
| `into` (all 59) | `null` |
| **removed-from-corpus set == tombstoned set** | **✅ exactly equal** |

No silent deletion. Every row that left the corpus has a tombstone, and no
tombstone was written for a row that did not leave.

## 5. Discrepancies against the batch's own declared delta

Both are prose-level. Neither is an out-of-scope data move.

### 5.1 `owasp_llm` is undeclared

The commit message enumerates the orphan-confined fields as
"`source_ids`/`source_count`/`tags`/`nist_ai_rmf`/`mitre_atlas`/
`mitre_atlas_tactics`/`owasp_asi`/`severity`". **`owasp_llm` (11 rows) is
missing from that list.** Measurement puts all 11 inside the orphan-27, so the
scope claim survives — but under working agreement 2 an operation that moves a
field it did not declare is exactly what the delta rule exists to catch, and a
gate reading only the message would not have known to look.

### 5.2 The `updated`/`last_seen` identity is off by one

See §3. Claimed "exactly = union"; actually union − 1, explained by `INC-04496`.

## 6. The single `corpus` move, verified

`INC-08170`: `security` → `ai-harm`. The retired orphan row contributed
`deepfake`, `gdpr`, `training-data` and `xai` tags plus source_id
`OECD-2024-08-12-212f-grok-privacy`; with the orphan gone the row keeps
`AIID-762`/`AIID-763` and its remaining tags
(`mit-risk-domain:1-discrimination-and-toxicity`,
`mit-risk-domain:3-misinformation`, …). Losing `deepfake` is what stops the
security classifier firing on an AIID-content discrimination incident. The move
is a *consequence of the orphan retirement*, not of the narrative reduction, and
it corrects the classification rather than degrading it.

## 7. Test state — re-run, not quoted

```
python -m pytest -q   →   299 passed in 21.16s
```

Matches the batch's claim (283 baseline + 16 new). Includes
`tests/test_e23_aiid_dead_letter_tripwire.py` (215 lines), which converts E23's
hand-measured dormant-population finding into an enforced regression test.

## 8. What this file does NOT establish

- **It is not a gate.** Acceptance criteria, invariant sweep, scope-change hunt
  and stray check are red-reviewer's job, not measured here.
- **It does not verify the reduction's *content*** — that the replacement
  descriptions are genuinely structural-facts-only and carry no OECD narrative.
  That is a licensing judgement (E21 outcome (B)) and belongs to the gate.
- **It does not re-verify determinism.** The batch claims a double rebuild is
  structurally identical; that claim is untested here.
- **Part A's measurement has no standalone committed artifact.** The
  provenance-null figure (11,697/13,119) and the join-and-search establishing
  the 3,726 population exist **only in `3c1e3e9e`'s commit message**. They are
  re-derivable but were never written to an audit file, contrary to the
  committed-artifact rule.

## 9. Bottom line for the ruling

The measured delta **matches the authorized scope**: 3,667 reduced descriptions,
59 tombstoned orphan rows, 27 cross-covered rows losing only orphan-contributed
fields, zero `attack_vector` movement, zero unexplained rows, zero additions.
The two discrepancies found are both in the commit message's description of the
delta, not in the delta itself.
