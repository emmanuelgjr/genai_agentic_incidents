# WS0-T4 swap-half: AIID official-snapshot channel swap (2026-07-18)

**Task:** WS0-T4 swap-half only (decision D1, 2026-07-16). The stop-half
(disabling `scripts/scrape_aiid.py`'s network fetch in `make ingest-all`)
landed 2026-07-16 (`Makefile:89`, commit history around "board WS0-T4
stop-half done"). This note documents the replacement channel implemented
here, landing in the same change as the code (branch
`ws0t4-aiid-snapshot-swap`).

## 1. Confirmed sanctioned channel (verified live, 2026-07-18)

Per `docs/SOURCE_LICENSES.md` §1.2, AIID publishes official weekly
snapshots at `https://incidentdatabase.ai/research/snapshots/`. Verified
live before coding:

- **Index page** (`WebFetch` + `curl`, 2026-07-18): lists snapshots by
  timestamped filename `backup-<YYYYMMDDHHMMSS>.tar.bz2`, weekly cadence
  (confirmed filenames from 2026-03-02 through 2026-07-13 present on the
  page), served from the Cloudflare R2 bucket
  `https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/<filename>`.
- **Latest snapshot at verification time:** `backup-20260713110347.tar.bz2`,
  102,012,196 bytes, `sha256=4d7b16d92f69054494a9a728c78a8201fcd790d70c250a527c02233d773d6730`
  (recorded in `ingest/aiid_full.provenance.json`, regenerated on every
  `make ingest-aiid` run).
- **Archive contents** (`tar -tvjf`, downloaded and inspected directly):
  a `mongodump_full_snapshot/` tree containing, per top-level collection,
  BOTH a flat CSV export (`incidents.csv`, `reports.csv`,
  `classifications_*.csv`, `duplicates.csv`, `quickadd.csv`) AND a raw
  `mongodump`-format BSON dump under `aiidprod/` (plus a `translations/`
  subtree with only `incidents.bson`/`reports.bson`). A `license.txt` file
  ships inside the archive itself: *"Report contents are subject to their
  own intellectual property rights. Unless otherwise noted, the database
  is shared under (CC BY-SA 4.0)."* This corroborates
  `docs/SOURCE_LICENSES.md` §1.2's existing finding (from AIID's
  `terms-of-use/` page) rather than superseding it.

## 2. What this ingest reads from the archive -- and what it never touches

`scripts/ingest_aiid_snapshot.py` extracts exactly three CSV members plus
`license.txt` via `tarfile`, by name, from an in-memory `BytesIO` (nothing
is ever unpacked to disk beyond the archive itself, cached under the
gitignored `ingest/_cache/aiid_snapshot/`):

- `mongodump_full_snapshot/incidents.csv` -- `incident_id`, `date`, `title`,
  `description`, alleged-deployer/developer/harmed-party entity slugs.
- `mongodump_full_snapshot/duplicates.csv` -- AIID's own duplicate→true
  incident-number mapping.
- `mongodump_full_snapshot/classifications_MIT.csv` -- the MIT AI Risk
  Repository taxonomy classification (Risk Domain / Risk Subdomain -- a
  closed, fixed vocabulary).

It **never opens** `reports.csv`, `reports.bson`,
`translations/reports.bson`, or `aiidprod/reports.bson` -- the member list
in `extract_members()` simply does not name them, so the "exclude
`reports.text`" requirement is enforced by omission, not by extract-then-
discard. It also never touches `classifications_CSETv1*.csv`,
`classifications_CSETv0.csv`, or `classifications_GMF.csv`: those tables
were inspected and rejected for this scope because CSETv1/CSETv0 mix
categorical fields with free-text "Notes"/"Full Description"/"AI System
Description" columns, and GMF's "* Snippets" columns contain **literal
quoted excerpts from report text** (e.g. `"Snippet Text: An off-brand Paw
Patrol video called ... features several disturbing scenarios."`) --
exactly the report-derived narrative prose this exclusion exists to keep
out, just re-surfaced under a different collection name. Extending
coverage to those tables is flagged as future work requiring a
per-column narrative-vs-categorical audit; not attempted here.

No image/video binaries or their source URLs are extracted or fabricated
(the snapshot ships none as first-class members reachable from the
members this script reads) -- the board's exclusion note
(`PROGRESS.md:112`) is satisfied by not producing anything to exclude.

## 3. How `description` narrative is kept out of the corpus

AIID's own `incidents.description` field (part of the CC-BY-SA-licensed
`incidents` collection, and NOT the excluded `reports.text` field) is
read from the CSV, but is used **only as an ephemeral, in-memory
classification signal** -- feeding the reused `is_security_relevant()` /
`map_taxonomy()` / `severity_for()` heuristics from `scrape_aiid.py` -- and
is **never written to the output file**. The persisted `description` is
always an original templated sentence built from structured facts:

```
AI Incident Database (AIID) entry #<id>: <title>. Alleged deployer/developer:
<entities>. See the linked AIID entry for full narrative, sourcing, and
classification.
```

`title` (a short AIID-authored headline) is kept verbatim -- the same
category of content the AIAAIC D2 reduction treats as safe to keep
(headline, not narrative). This is **more conservative than the retired
scrape**, which persisted a truncated (1500-char) verbatim `og:description`
into every entry's `description` field. Verified mechanically: every one
of the 1,548 entries in the regenerated `ingest/aiid_full.json` starts
with the literal templated prefix (`0` non-conforming rows checked by
script; see the delta report).

This does **not** resolve AIID's CC-BY-SA share-alike question in full --
that remains open, parallel to the still-open AIAAIC database-right
question (E13). See the updated `docs/SOURCE_LICENSES.md` §1.2 for the
explicit open-item flag.

## 4. Invariant 3 (never silently drop a previously-present entry)

Two independent layers guard this swap against silently dropping AIID
incidents that were already in the corpus:

1. **Ingest-level:** `load_existing_aiid_ids()` reads the current
   `data/incidents.json` for every AIID `incident_id` already referenced
   (via `aiid_id` or an `AIID-<n>[-OECD]` source_id, from ANY ingest
   file -- not just this one) and unconditionally keeps that row in the
   new `aiid_full.json`, regardless of what the fresh security-relevance
   filter decides. Only genuinely new AIID incidents (never previously
   ingested) are gated by the keyword filter.
2. **Pipeline-level (pre-existing, independent of this task):**
   `scripts/merge_and_dedupe.py`'s retention step (`load_retained_priors` /
   the step-6c top-up) already carries forward, verbatim, any
   previously-published incident whose keys are no longer covered by any
   fresh source, stamping `"source_status": "retained"`. This general
   mechanism is a second, independent safety net.

Result, verified against the actual rebuild (see the delta report):
**0 corpus IDs removed**, 39 net-new AIID-derived `INC-*` ids added.

## 5. Expected delta (summary; full numbers in the delta report)

- Corpus: 12,986 → 13,025 entries (+39, 0 removed).
- `ingest/aiid_full.json`: 1,571 AIID incidents in the snapshot → 1,548
  written (1,099 security-relevant + 449 kept for continuity per §4) →
  23 excluded (neither relevant nor previously present).
- Of the 1,426 AIID-linked entries present both before and after (same
  `INC-*` id): `description` changes in nearly all of them (narrative →
  templated facts+link, the intended change), `title` changes in ~28%
  (mostly HTML-entity-decoding fixes inherited from the old `og:title`
  scrape, some genuine title upgrades/upstream edits), `attack_vector` /
  `severity` / taxonomy fields shift in a minority (reclassification from
  a cleaner, more complete signal than the old truncated/HTML-scraped
  text) -- including one pre-existing false-positive class in the reused
  `severity_for()` heuristic (substring match on `"fatal"` catching
  `"non-fatal"`), flagged, not fixed here (out of this task's scope;
  belongs to WS2-T5).

## 6. Scope explicitly NOT covered here

- `ingest/common.py` universal conduct routing, `docs/INGESTION_CONDUCT.md`,
  invariant 5 activation, other sources' conduct -- remainder of WS0-T4,
  not this dispatch.
- AIAAIC ingest -- untouched (WS0-T3 held).
- `ingest/aiid_incidents.json` (111-row hand-curated file) and
  `ingest/aiid_oecd_relationships.json` (681-row repo-bridge file, §1.3) --
  untouched; neither is produced by `scrape_aiid.py`, so neither is in
  scope for this channel swap.
- Full AIID CC-BY-SA / sui-generis-database-right resolution -- flagged as
  an open item in `docs/SOURCE_LICENSES.md` §1.2, not resolved by this
  change, same posture as AIAAIC's still-open E13 database-right question.
- CSETv1/CSETv0/GMF structured-taxonomy extraction -- flagged as future
  work needing a per-column audit, not attempted.
