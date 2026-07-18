# WS0-T4 swap-half: field-level before/after delta (2026-07-18)

Per the standing field-level delta rule (CLAUDE.md working agreement #2):
this is a transformative data operation (AIID's ingest source swapped from
the prohibited scrape to the sanctioned snapshot). Every affected field is
enumerated below with a count and a justification. "Before" = committed
`data/incidents.json` prior to this branch's rebuild (12,986 entries).
"After" = `data/incidents.json` produced by `scripts/parse_existing.py` +
`scripts/merge_and_dedupe.py` + `scripts/render_markdown.py` +
`scripts/render_docs_stats.py` + `scripts/validate.py` (the `make build`
sequence) on this branch, from the regenerated `ingest/aiid_full.json`.

## Entry-count / ID-set delta

| | Before | After | Delta |
|---|---|---|---|
| Total corpus entries | 12,986 | 13,025 | **+39** |
| AIID-linked entries (`aiid_id` set or `AIID-<n>[-OECD]` source_id) | 1,426 | 1,465 | **+39** |
| Corpus `INC-*` ids removed | -- | -- | **0** |
| Corpus `INC-*` ids added | -- | -- | 39 (all AIID-linked, all new AIID incident_ids not previously covered by any source) |

**0 IDs removed** -- invariant 3 (never delete; status + tombstone instead)
is satisfied for this change: no previously-published entry disappeared.
Verified by set difference on the full `id` set between the before/after
`data/incidents.json`, not by sampling.

## `ingest/aiid_full.json` (the swapped file itself)

| | Count |
|---|---|
| AIID incidents in the sanctioned snapshot (`incidents.csv` rows) | 1,571 |
| AIID incident_ids already present in the corpus pre-swap (any source) | 1,509 |
| Written to the new `ingest/aiid_full.json` | 1,548 |
| &nbsp;&nbsp;-- security-relevant (keyword filter, `is_security_relevant()`) | 1,099 |
| &nbsp;&nbsp;-- kept for continuity only (invariant 3; not relevant by today's filter but already in the corpus) | 449 |
| Excluded (neither relevant nor previously present) | 23 |

The 449 continuity-only rows are exactly why the corpus-level ID delta is
`+39, -0` rather than something with real losses: without the
continuity rule, up to `1,509 - 1,099 = 410` previously-present AIID ids
could have failed today's keyword filter and (absent the pipeline's
independent retention mechanism, see the implementation note §4) been at
risk of disappearing.

## Field-level diff, AIID-linked entries present in BOTH before and after (n = 1,426, matched by stable `INC-*` id)

| Field | Entries changed | n / 1426 | Justification |
|---|---|---|---|
| `tags` | 1,426 | 100% | **Intended.** New tag vocabulary (`mit-risk-domain:*`, `aiid-duplicate-of:*`) added; old scrape's bare `["aiid"]` tag set replaced. |
| `description` | 1,425 | 99.9% | **Intended -- the core change.** Verbatim/near-verbatim AIID narrative (`og:description`, truncated at 1500 chars) replaced with an original templated facts+link sentence. See implementation note §3 for the exact template and the 0/1548 non-conformance check. |
| `affected` | 1,408 | 98.7% | **Intended.** Old scrape always wrote `affected: ""` (field unpopulated, `scrape_aiid.py:244`). New ingest populates it from the snapshot's structured deployer/developer entity slugs (prettified). A quality gain, not a narrative-content change -- entity slugs are single-word identifiers, not prose. |
| `title` | 403 | 28.3% | **Mostly intended, some incidental.** Breakdown of a 15-entry manual sample: the large majority are HTML-entity-decoding fixes (`&#x27;` -> `'`, `&quot;` -> `"`) -- the old scrape's `og:title` regex-extraction never decoded HTML entities; the new CSV parse does, correctly. A handful upgrade a generic OECD-bridge placeholder title (`"AIID incident #613 (OECD-tracked)"`, the only title available when that id had no other source) to the real AIID title now that `aiid_full.json` covers it. A small number are genuine upstream AIID title edits surfaced by a more current snapshot than the original scrape date -- an incidental instance of exactly the "edited AIID entries re-diffed" reconciliation WS4-T2 will formalize; not claimed as WS4-T2 being done. |
| `attack_vector` | 236 | 16.5% | **Expected side effect, not a defect.** Reclassified from `TAXONOMY_RULES` run against a cleaner, more complete text signal (structured DB `description` vs. a possibly-truncated/HTML-scraped `og:description`) -- same heuristic function, better input. |
| `date` | 54 | 3.8% | **Intended improvement.** Structured `incidents.csv` date field vs. the old scrape's regex-over-HTML date extraction (which had multiple fallback heuristics down to an incident-id-range guess -- see `scrape_aiid.py:117-130`). |
| `mitre_atlas` | 41 | 2.9% | Downstream of `attack_vector` reclassification + `fill_taxonomy()` backfill in `merge_and_dedupe.py`. |
| `owasp_llm` | 33 | 2.3% | Same. |
| `owasp_asi` | 33 | 2.3% | Same. |
| `nist_ai_rmf` | 31 | 2.2% | Same. |
| `year` | 20 | 1.4% | Same root cause as `date`. |
| `severity` | 19 | 1.3% | **Mixed -- 16 justified, 3 flagged as an inherited defect, not fixed here.** See below. |
| `category`, `source_ids` | 0 | 0% | Unchanged, as expected (both scripts write `"real-world"` / the same `AIID-<n>` canonical form). |

## `severity` changes -- the one field with a known false-positive class

19 of 1,426 AIID-linked entries changed `severity`. Manually reviewed all 19:

- **16 are genuine reclassifications**, e.g. `INC-03174` (aiid_id 1232,
  "Reportedly Fatal Xiaomi SU7 Ultra Crash...") moved Medium -> Critical:
  the old scrape's severity heuristic missed the word "fatal" (present in
  the title itself) -- almost certainly because the old `og:description`
  text it matched against differed from the authoritative snapshot
  description; the new classification is more correct, not less.
- **3 are a confirmed false-positive class, inherited unchanged from the
  reused `scrape_aiid.py::severity_for()`**: its Critical-severity keyword
  check does a plain substring match for `"fatal"`, which also matches
  `"non-fatal"`. Affected: `INC-07339` (aiid_id 320, "... Collided with
  Parked Fire Truck..."), `INC-07335` (aiid_id 294, "Tesla Autopilot ...
  Non-Fatal Collision in Greece"), `INC-06096` (aiid_id 304, "Tesla on FSD
  ... Wrong Lane... non-fatal collision"). Quantified independently against
  the full `ingest/aiid_full.json`: of 120 entries flagged `Critical`, 5
  trip on the `"non-fatal"` substring (2 of the 5, aiid_id 151 and 1296,
  aren't in this 1,426-entry continuity set so don't show up in the
  before/after diff, but carry the same defect going forward).

This bug **pre-dates this swap** (it lives in `scrape_aiid.py`, reused
per the Makefile's explicit instruction to reuse its parsing logic, not
introduced here) and is a severity-heuristic-quality issue, not a
licensing issue. Per this task's scope boundary (channel swap + exclusion
handling only -- not general data quality), it is **flagged, not fixed**;
the fix (exclude `"non-fatal"`/`"non fatal"` from the `"fatal"` trigger,
or move to a proper severity rubric) belongs to WS2-T5 (Severity rubric),
which already exists on the plan to fix exactly this class of "bare
keyword max-on-merge inflation" problem.

## Field-level diff, `ingest/aiid_full.json` itself vs. its own pre-swap content

Not meaningfully comparable field-by-field (the whole point of the swap is
that every persisted field's *derivation method* changed), but mechanically
verified:

- **0 / 1,548** entries in the new file have a `description` that does not
  start with the literal templated prefix `"AI Incident Database (AIID)
  entry #"` -- i.e. zero verbatim/near-verbatim upstream narrative persisted.
- **0** references to `reports.csv`, `reports.bson`, or
  `translations/reports.bson` anywhere in `scripts/ingest_aiid_snapshot.py`
  (the member allow-list in `extract_members()` never names them).

## Reproduce this delta

```
git stash -u   # or run on a clean pre-swap checkout of data/incidents.json
python scripts/ingest_aiid_snapshot.py       # regenerates ingest/aiid_full.json (network)
python scripts/parse_existing.py             # offline
python scripts/merge_and_dedupe.py           # offline
python scripts/render_markdown.py            # offline
python scripts/render_docs_stats.py          # offline
python scripts/validate.py                   # offline
pytest tests -q
```

`ingest_aiid_snapshot.py` is the only network-touching step; everything
from `parse_existing.py` onward (== `make build`) is fully offline, reading
only the committed `ingest/*.json` snapshot files.
