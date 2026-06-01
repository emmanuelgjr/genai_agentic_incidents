# Retain-on-drop for the genai_incidents pipeline

**Date:** 2026-06-01
**Status:** Approved (design); pending implementation
**Author:** maintainer + Claude Code

## Problem

The weekly auto-refresh silently loses incidents. The 2026-05-31 refresh PR
(#18) showed a net change of +5 (7,725 → 7,730) that masked **245 added /
240 removed** entries. Investigation confirmed the removals are not dedupe
merges (only 6 of 240 are recorded in `id_deprecations.json`) and the dropped
incidents do not reappear under any other id — they are genuinely gone. Several
are substantive real-world events (Waymo robotaxi recall, Tesla Autopilot
fatalities, etc.).

### Root cause (confirmed in code)

1. **The OECD ingester is a sliding window.** `scripts/ingest_oecd_aim.py`
   fetches only the newest `DEFAULT_LIMIT = 3000` sitemap URLs (the
   `Weekly auto-refresh` workflow passes `3000`) and **overwrites** the
   committed `ingest/oecd_aim_full_incidents.json` with just that fetch. The
   security-relevant OECD corpus exceeds 3,000 entries, so on each run the
   oldest entries fall outside the window and are erased from the committed
   ingest file.
2. **The build is not retentive.** `scripts/merge_and_dedupe.py` rebuilds
   `data/incidents.json` purely from `ingest/*.json` + `legacy_consolidated.json`.
   The previous `data/incidents.json` is read **only** for timestamp/id
   stability (`_load_prev_state`), never as a retention source. Anything missing
   from the current ingest files vanishes.

Net effect: as the OECD window slides, ~235 incidents/week silently disappear.

## Goal & semantics

Make the dataset **archival**: once an incident is published in
`data/incidents.json`, it is never silently dropped because an upstream source
stopped returning it. Incidents leave the dataset **only** via the existing
explicit deprecation/merge path (`id_deprecations.json`).

Two complementary fixes (both, per maintainer decision):

- **Part A** stops the loss at the source (OECD ingest file accumulates).
- **Part B** is a general backstop for *any* source that drops entries.

Out of scope (deliberate future follow-up): a `source_status` / `last_seen`
provenance field to distinguish "live in upstream feed" from "retained but
upstream no longer lists it." That requires per-entry last-seen tracking, which
collides with the cross-day determinism rule and spans the schema, validator,
and exports — it deserves its own focused PR.

## Part A — OECD ingester union (`scripts/ingest_oecd_aim.py`)

Extract the write step into a pure helper and union the fresh fetch with the
committed file instead of overwriting:

```
def union_with_existing(fresh: list[dict], existing: list[dict]) -> list[dict]:
    """Union by source_id. Fresh wins on conflict; aged-out entries survive.
    Output sorted by source_id for a deterministic, stable-ordered file."""
```

- Key on `source_id` (`OECD-AIM-<id>`).
- Entry in both → take the **fresh** version (latest content).
- Entry only in `existing` (aged out of the window) → **keep it**.
- Sort output by `source_id` so the committed file ordering is stable.

`main()` loads the existing committed file (if present), calls
`union_with_existing(out, existing)`, and writes the union. Result: the
committed OECD ingest file only grows; nothing ages out.

## Part B — build-level retention backstop (`scripts/merge_and_dedupe.py`)

Add **step 2b** in `main()`, immediately after the ingest files are loaded
(step 2) and before dedupe (step 3):

1. Read the previous `data/incidents.json` (reuse the already-open read in
   `_load_prev_state` or read once and pass through).
2. Build the deprecations `from`-set from `id_deprecations.json`.
3. For each prior incident whose `id` is **not** in the deprecations set,
   append it to `all_entries`.

The existing dedup machinery then handles everything:

- A prior incident that also appears in a fresh ingest matches on
  `source_id` / CVE / URL / title and **merges**. Ingest entries are appended
  *before* priors, so the fresh entry is the dedup survivor and the prior merges
  into it (fresh content wins).
- A prior incident with no fresh match **survives on its own**.

Prior entries flow through the **same** normalize → finalize-vector →
seed-frameworks → curation-overrides → `_apply_history` path as everything else,
so a retained entry is treated identically to a freshly-ingested one.

### Determinism (the critical constraint)

The build must rebuild byte-identically across UTC days (see
`pipeline-determinism`). Retention is safe because:

- A retained entry's content is unchanged from the previous output, so its
  `_content_snapshot` matches the stored snapshot and `_apply_history` preserves
  `updated` — no spurious bump, no `generated` flap, drift check stays clean.
- Idempotent: feeding the output back in produces the same set of survivors.
- Deterministic ordering: priors are appended in their stored order (stable by
  `id`); fresh-vs-prior conflicts always resolve to the fresh survivor.

This is the area to test hardest, given the prior `attack_vector`-before-
`_apply_history` determinism bug.

## Testing

- **Retention:** remove an entry from an ingest fixture, rebuild, assert the
  entry persists in `data/incidents.json` with the **same** `INC-` id.
- **Deprecation still wins:** an id present in `id_deprecations.json` `from` is
  **not** resurrected by retention.
- **Ingester union:** unit-test `union_with_existing` directly (pure function,
  no network) — aged-out entry survives, shared entry takes fresh content,
  output is sorted by `source_id`.
- **Determinism:** build twice and with a faked future `date.today()`; assert
  zero field diffs and stable `generated`.

## Validation against PR #18

After the change, re-running the refresh flow on current `main` must **retain**
the ~235 OECD incidents that PR #18 would have dropped, rather than losing them.
Verify concretely (rebuild, diff incident-id set vs. main) before claiming done.

## Files touched

- `scripts/ingest_oecd_aim.py` — extract + call `union_with_existing`.
- `scripts/merge_and_dedupe.py` — add step 2b (retention backstop).
- `tests/` — new retention, deprecation, union, and determinism tests.

No schema, export (STIX/HF), or docs changes — retention is silent in v1.

## Rollout

Ship as a focused PR: branch → push → watch CI green → squash-merge → pull main
(per `working-style-pr-cadence`). Then re-run the weekly auto-refresh so the
next refresh PR is built on the retentive pipeline. Close the stale PR #18 and
re-run rather than merging it (its branch predates this change).
