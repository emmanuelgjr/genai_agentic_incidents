# D8 marking half — source-freshness application: full field-level delta

**Date:** 2026-07-29
**Author:** pipeline-engineer (WS4)
**Spec:** `docs/specs/D8-source-freshness-2026-07-29.md` (schema-architect)
**Branch:** `ws3/airi-hold-marking`, on top of `88b12352` (schema-architect's two
commits: `b9e261fd` shape, `88b12352` provenance check). Neither touches
`data/incidents.json` — confirmed (`git show 88b12352:data/incidents.json` is
byte-identical to `git show 378bf9b3:data/incidents.json`, SHA-256
`a519963ee56e66d47cc304ca83f97ea01ef7ad2cc894fa7353a1e8c18bdab01e` both), so
"before" below is unambiguous.
**Scope:** the marking half only — deriving and applying `source_freshness`
per the spec's algorithm, plus the two required code changes (validator
completeness gate, §6a) and an assessment of the reconciliation workflow
change (§6b, judged out of scope for this task — see §5).

---

## 1. What was applied, and to what rows

Implemented the spec's rule verbatim in `scripts/merge_and_dedupe.py` step 6g
(`scripts/merge_and_dedupe.py:1541-1596`), immediately after the existing
`tier`/`source_count`/`confidence`/`capec_ids`/`purl` provenance block, reading
the registry via a new loader `_load_source_freshness_registry()`
(`scripts/merge_and_dedupe.py:965-985`, same shape/pattern as
`_load_curation_overrides()`):

```python
e.pop("source_freshness", None)          # re-derive, never setdefault
entry_tags = set(e.get("tags") or [])
stale = sorted(
    key for key, src in freshness_sources.items()
    if src.get("status") == "stale"
    and src.get("row_marker") is not None
    and src["row_marker"].get("value") in entry_tags
)
if stale:
    e["source_freshness"] = {
        "status": "stale",
        "as_of": min(freshness_sources[k]["last_success"] for k in stale),
        "sources": stale,
    }
```

- Runs on every entry in `deduped`, retained rows included (they pass through
  this loop identically to any other row — see §3 for why that matters).
- `data/incidents.min.json` carries the marker conditionally — added only when
  present, mirroring the `content_license` precedent
  (`scripts/merge_and_dedupe.py:1670-1701`).
- Ran `scripts/render_markdown.py` to refresh the two min.json mirrors
  (`docs/data/incidents.min.json`, `src/genai_incidents/data/incidents.min.json`)
  and the rendered Markdown; both mirrors confirmed byte-identical to
  `data/incidents.min.json` (same SHA-256). `INCIDENTS.md` and every
  `docs/incidents/*.md` year shard show **zero diff** — the field is not
  rendered into Markdown (no template exists, per spec §4), so nothing there
  moved. `data/stats.json` shows **zero diff** — no new key, invariant 6 intact,
  `check_stats_drift.py` exits 0.
- Added the required completeness gate to `scripts/validate.py`
  (`check_freshness_completeness()`), wired into `main()` alongside the
  existing `check_registry_provenance()` / `check_source_freshness()` calls.
- Did **not** touch `data/source_freshness.json`, `schema/`, or `PROGRESS.md`,
  per the brief. (`data/source_freshness.json` shows as modified in `git
  status` on this machine purely from CRLF/LF checkout normalization —
  confirmed empty under `git diff --ignore-space-at-eol`, i.e. zero content
  change; not staged by me.)

**Rows marked: 1,380** — verified to be **exactly** the set carrying the
`airi-navigator` tag (`marked == airi_navigator_tagged`, set equality checked
directly, not just count equality).

## 2. Every spec §5 assertion, re-derived independently against the rebuild

| # | Assertion | Result |
|---|---|---|
| 1 | Marked set == entries carrying `airi-navigator` | **1,380 == 1,380**, set-equal |
| 2 | Marked set == entries carrying an `eu-ai-act-*` (hyphenated family) tag, symmetric difference 0 | **0** — confirmed once I excluded the *bare* `eu-ai-act` tag from the `-*` family match (see #3); with the bare tag included the naive symmetric difference is 1, which is #3 exactly, not a discrepancy |
| 3 | `INC-02549` NOT marked | Confirmed: carries `["eu-ai-act", "regulation", "enforcement", "prohibited-practices", "compliance"]` — the **bare** `eu-ai-act` tag, no `airi-navigator` — and is absent from the 1,380 |
| 4 | The 109 entries with both `airi-navigator` and `oecd-aim` list `["airi_navigator"]` only | **109/109** confirmed, zero exceptions |
| 5 | Every marked row has `as_of == "2026-05-31"` | **1,380/1,380**, zero exceptions |
| 6 | No `retained` entry marked | **0/9** retained entries carry the marker |
| 7 | Build byte-identical across two consecutive runs | Confirmed, see §4 |

## 3. Why retained rows needed explicit attention (and are covered)

Retained priors (step 6e, `scripts/merge_and_dedupe.py:1505`) are carried
**verbatim** from the previous `data/incidents.json` and bypass dedupe — so a
retained row can arrive at step 6g already holding a `source_freshness` marker
from an earlier build. The loop `pop`s the field first and re-derives from the
*current* registry rather than `setdefault`-ing, specifically so a source that
later recovers sheds the marker even on a row that no longer appears in any
fresh ingest input. Added a dedicated test for exactly this
(`test_source_freshness_dropped_on_retained_row_when_source_recovers`,
`tests/test_merge_and_dedupe.py`): mark a row stale, then rebuild with the row
absent from ingest (so it retains) **and** the registry flipped to `ok` in the
same build — the retained row's marker is gone. On the present corpus this is
moot in practice (assertion 6: 0 of 9 retained rows are AIRI-derived), but the
mechanism is tested, not just asserted.

## 4. Build determinism (two consecutive full runs)

Ran the full recipe twice (`make build`'s constituent commands — no `make`
binary on this Windows box): `parse_existing.py`, `merge_and_dedupe.py`,
`render_markdown.py`, `render_docs_stats.py`, `validate.py`. No network or
model call in this path.

```
[freshness] source_freshness marker on 1380 entr(ies)
[total]  18736 input -> 13119 unique
...
13119/13119 entries valid; 0 with errors.
source freshness: registry valid (4 source(s), observed_at 2026-07-12); 1 stale (airi_navigator); 1380 entr(ies) carry a source_freshness marker.
integrity: no duplicate CVE/source keys; all deprecations resolve.
```

`check_stats_drift.py`: `clean: 5 doc surfaces match data/stats.json, no
unmarked hardcoded totals`. `pytest tests -q`: **239 passed** (226 pre-existing
+ 13 new).

SHA-256 of every affected output, identical across both runs:

| File | SHA-256 (both runs) |
|---|---|
| `data/incidents.json` | `88bfc3357c469870fc85289ae4f19cef7807004b15a3eaf459a0267a58474d05` |
| `data/incidents.min.json` | `60fefbb8c98807925f3ab02596cf1be6f7fba0e0d4edc1050b2f937b3c9b03a4` |
| `docs/data/incidents.min.json` | `60fefbb8c98807925f3ab02596cf1be6f7fba0e0d4edc1050b2f937b3c9b03a4` (mirror in sync) |
| `src/genai_incidents/data/incidents.min.json` | `60fefbb8c98807925f3ab02596cf1be6f7fba0e0d4edc1050b2f937b3c9b03a4` (mirror in sync) |
| `INCIDENTS.md` | `1885c39597d593bb52f74c8575af43b978acc08b52a829ed4e257325ea54c8a4` |
| `data/id_deprecations.json` | `975d94c7922b41b3dadf7a2be776e516f4571eac417487ba04d87b15f04c5027` (**byte-identical to the pre-change committed version** — 0 new deprecations) |
| `data/legacy_consolidated.json` | `4c8e3f7a1123715e7c79bb940d7b949e62226b3ad736aa050e80661807cbd0e4` |

`git status --porcelain --untracked-files=all` after the second run is
identical to after the first run (checked via diff of the two captures) — the
second run introduced **zero** further changes, and no stray untracked files
(the zero-byte post-redirect artifact class from the retired reprocessing
hook) appeared at any point.

Pre-change (`HEAD` = `88b12352`) blob hash, for reference:

| File | SHA-256 (HEAD, pre-change) |
|---|---|
| `data/incidents.json` | `a519963ee56e66d47cc304ca83f97ea01ef7ad2cc894fa7353a1e8c18bdab01e` |

## 5. Full field-level delta — before = HEAD (`88b12352`) `data/incidents.json`
(13,119 entries), after = this rebuild (13,119 entries)

**Entry count: 13,119 → 13,119 (unchanged). ID set: IDENTICAL** — checked as
sets, zero additions, zero removals.

**Fields with any changed value, across the whole 13,119-entry corpus,
computed by diffing every field key present on any entry, before vs after —
every field not listed here is byte-for-byte identical on every single
entry:**

| Field | Rows changed |
|---|---|
| `source_freshness` | **1,380** (all `absent` → the marker object; 0 removed, 0 modified-in-place) |

That is the **entire** diff at the entry level. Nothing else moved — in
particular, confirmed identical corpus-wide and not merely by aggregate count:
`source_status` (13,110 `active` / 9 `retained`, both before and after,
identical distribution), `tags` (identical on every row — **no `eu-ai-act-*`
tag added, removed, or annotated in place**; the as-of annotation D8 asked for
lives entirely in the new `source_freshness.as_of` field, per spec §4's
"no render target" finding), `updated` / `last_seen` / `added` (identical on
every row), `attack_vector`, `severity`, `corpus`, `tier`, `quality_tier`,
`capec_ids`, `purl`, every taxonomy mapping (`owasp_llm`, `owasp_asi`,
`owasp_dsgai`, `nist_ai_rmf`, `mitre_atlas`, `mitre_atlas_tactics`), and
`content_license` (still exactly **1,517**). `landmark_count`
(`data/stats.json`, an aggregate, not a per-entry field) is unchanged at
**1,905** — `data/stats.json` itself shows **zero diff** (`git diff --stat`
empty), so this is not merely "the number happens to match", the file was
never touched.

## 6. Invariant 4 — is a freshness marker a content change? Declared: NO

`source_freshness` is **excluded** from `_CONTENT_FIELDS`
(`scripts/merge_and_dedupe.py:1074-1082` — the allowlist `_content_snapshot()`
diffs to decide whether to bump `updated`), by omission, exactly like
`content_license`'s E16 precedent
(`docs/audits/E16-marker-retitle-delta-2026-07-29.md` §5). Verified directly,
not just declared: `updated` and `last_seen` are **byte-identical, before and
after, on every one of the 1,380 newly-marked rows** (0 bumped) — confirmed as
part of the full-field diff in §5 (`updated`/`last_seen` do not appear in the
changed-fields table at all).

**Reasoning:** a source going stale (or later recovering) describes
*something that has not changed* — the row's content is exactly what it was
when the source last succeeded; only the reader's confidence in its currency
changes. Bumping `updated` would assert new content where there is none, which
is both an unintended delta and, per the spec's framing, a false claim in the
opposite direction from the one D8 exists to fix (D8 fixes an
under-claim — rows silently reading fresher than they are; a bumped `updated`
would be an over-claim — rows reading as edited when they were not). This
mirrors `content_license`'s established treatment exactly: attribution/
provenance/freshness metadata is not "content" for `_apply_history`'s purposes,
and I did not create a new exception — I extended the existing convention to a
new field, the same way E16 did.

## 7. §6b (registry/counter reconciliation) — assessed, NOT built here

**Judgment: defer to a follow-up task.** Reasoning:

- The brief itself flagged this as "likely NOT build here," and the spec's own
  framing (§6b: "If the foreman splits (b) into a follow-up task...") treats
  the split as an expected, legitimate outcome, not a shortfall.
- It is a materially separate piece of engineering from the marking: a new
  `--registry` flag on `scripts/check_source_health.py`, a new
  `auto-refresh.yml` step placed in the one window where the authoritative
  counter is in the tree (between the restore and persist steps,
  `.github/workflows/auto-refresh.yml:109-145`), and a failure-mode design
  (compare source keys / `status` / `last_success` only, never
  `consecutive_failures` / `last_attempt`, per the spec's explicit
  anti-flakiness reasoning). None of it is exercisable by the deterministic,
  network-free test suite this task is gated on — it can only be meaningfully
  validated in a live Actions run with the `refresh-state` branch populated,
  which is its own review surface.
- It has no dependency in either direction on the marking itself: the 1,380-row
  delta, the completeness gate, and the registry's own offline provenance
  check (`check_registry_provenance()`, already landed, already passing) are
  all independent of whether the weekly CI reconciliation exists.
- Combining them would also mean the zero-unintended-delta gate on this PR
  covers a CI-workflow behavior change that cannot be demonstrated via
  `git diff` output the way the data delta can — a worse review surface for
  both pieces, not a better one.

**Consequence, handled in this PR per the spec's own requirement:** since §6b
is deferred, the DATA_DICTIONARY.md sentence claiming the weekly reconciliation
exists and fails loudly on divergence would be describing a mechanism that
does not exist. Softened it (`docs/DATA_DICTIONARY.md`, "Source freshness"
section, the paragraph beginning "Three copies of the health state exist..."):
it now states plainly that the reconciliation is *meant to* exist, cites the
spec section that specifies it, names `check_registry_provenance()` as the
weaker check that *does* exist today, and says explicitly that until the
reconciliation lands, registry staleness is caught only by a human noticing —
not by CI. No other prose in that section changed.

**Recommendation for the follow-up task's acceptance criterion:** a synthetic
test harness for `check_source_health.py --registry <path>` (mock
`source_health.json` + mock registry, assert divergence on each of the three
compared fields raises, agreement passes) plus one manual dry run of the
`auto-refresh.yml` step ordering (confirmed by inspection here, not yet
exercised live) before it's trusted in production.

## 8. What I found and did not act on

- **`references[0].title` / STIX / HuggingFace / MISP:** per spec §4, no
  action needed (HuggingFace dumps rows verbatim; STIX and MISP are
  out-of-scope calls for distribution-engineer). Not touched.
- **The `conflicts`-field question** the E16 delta raised is unrelated to this
  task; not revisited here.
- Confirmed (grep) that no site template, README, or docs surface renders the
  `eu-ai-act` tag family — matches spec §4's "no render target" finding
  exactly; did not build one.

## 9. Reviewer verification recipe

```
git status --porcelain --untracked-files=all   # expect: only the files this task touched
python scripts/parse_existing.py
python scripts/merge_and_dedupe.py
python scripts/render_markdown.py
python scripts/render_docs_stats.py
python scripts/validate.py
python scripts/check_stats_drift.py
python -m pytest tests -q

python -c "
import json, subprocess
before = json.loads(subprocess.run(['git','show','88b12352:data/incidents.json'], capture_output=True).stdout)['incidents']
after = json.load(open('data/incidents.json', encoding='utf-8'))['incidents']
bmap, amap = {e['id']: e for e in before}, {e['id']: e for e in after}
print('entries:', len(before), '->', len(after))
print('ID set identical:', set(bmap) == set(amap))
fields = set()
for e in list(before) + list(after):
    fields.update(e.keys())
changed = {f: sum(1 for i in bmap if bmap[i].get(f) != amap[i].get(f)) for f in fields}
print('changed fields (nonzero only):', {f: n for f, n in changed.items() if n})
marked = {i for i in amap if amap[i].get('source_freshness')}
airi = {i for i in amap if 'airi-navigator' in (amap[i].get('tags') or [])}
print('marked == airi_navigator tagged:', marked == airi, len(marked))
print('INC-02549 marked:', 'INC-02549' in marked)
"
```

Expect: no further diff after re-running the build (determinism); `13119/13119
entries valid; 0 with errors`; source-freshness line `... 1380 entr(ies) carry
a source_freshness marker`; stats-drift clean; `239 passed`; the Python block's
`changed fields (nonzero only)` printing exactly `{'source_freshness': 1380}`;
`marked == airi_navigator tagged: True 1380`; `INC-02549 marked: False`.
