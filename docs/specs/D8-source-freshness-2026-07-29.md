# D8 source-freshness marking — application spec

**Status:** shape and application both landed 2026-07-29 (schema + docs + validator + pipeline; marker applied to 1,380 rows). §6b's weekly registry/counter reconciliation is **specified but NOT built** — see §6b.
**Owner of this document:** schema-architect (WS3). **Implements:** decision D8,
marking half only, as unblocked by D20(c).
**Applying task:** pipeline-engineer (WS4). **Date:** 2026-07-29.

The retire-or-replace half of D8 stays parked until MIT replies or
**2026-08-28**. Nothing in this spec touches it, and nothing here depends on it.

---

## 1. What already exists (do not re-derive)

| Artifact | State |
|---|---|
| `schema/source_freshness.schema.json` | New. Shape of the registry. |
| `data/source_freshness.json` | New. The registry itself, all four tracked sources, AIRI marked `stale`. |
| `schema/incident.schema.json` | `source_freshness` property added; `source_status` description corrected. Packaged mirror `src/genai_incidents/schema/incident.schema.json` regenerated and in sync. |
| `docs/DATA_DICTIONARY.md` | `source_freshness` row, corrected `source_status` row, `tags` row note, new **Source freshness** section. |
| `scripts/validate.py` | Validates the registry against its schema; `check_registry_provenance()` holds it to its own `observed_from` claim; `check_source_freshness()` cross-checks any markers present. Reports `1380 entr(ies) carry a source_freshness marker` and exits clean (was 0 before the application landed). |

**The registry is not generated and must not become so.** It is a curated input
in the sense `data/curation_overrides.json` is one — hand-authored in a gated
task, reviewed, read by the build, written by nothing. It has to be: `stale_since`
comes from the WS4-T9 run-log audit, `hold` records a human decision and its
deadline, `row_marker` declares row selection, `coverage` states what nothing
measures. **A build-time generator would be the trap, not the escape**: on `main`
the authoritative counter lives on the `refresh-state` branch and reading it
needs network, which the build path forbids — so a generator could only read
`main`'s copy, the one D5 leaves stale by design, and would stamp it into a
published artifact every build. Instead the machine-derivable half is *checked*
offline (`check_registry_provenance`, bounded — it proves the registry matches
the copy it claims to have read, not that it is current) and is *to be
reconciled* weekly against the authoritative counter (§6b — **specified, not yet
implemented**; until it lands, an out-of-date registry is caught only when a
human notices).

`python scripts/validate.py` → `13119/13119 entries valid; 0 with errors.`
`python -m pytest tests -q` → 226 passed.

## 2. The rule to implement

A row is **contributed to** by source *S* when it carries *S*'s
`row_marker.value` tag from the registry. For each entry:

```
stale = sorted(key for key, src in registry["sources"].items()
               if src["status"] == "stale"
               and src["row_marker"] is not None
               and src["row_marker"]["value"] in entry_tags)
if stale:
    entry["source_freshness"] = {
        "status": "stale",
        "as_of": min(registry["sources"][k]["last_success"] for k in stale),
        "sources": stale,
    }
```

Sources with `row_marker: null` (CISA KEV) never mark rows — that is a design
decision recorded in the registry, not an omission to fix.

## 3. Where it goes in the build — and why the placement is load-bearing

Put the derivation in **`scripts/merge_and_dedupe.py` step 6g**, the provenance
block that already sets `tier` / `source_count` / `confidence` /
`source_status` / `capec_ids` / `purl` (currently around
`scripts/merge_and_dedupe.py:1549-1570`).

Two properties of that location are what make this correct:

1. **It runs after history stamping.** `_CONTENT_FIELDS`
   (`scripts/merge_and_dedupe.py:1074`) is an allowlist and does not contain
   `source_freshness`, so the new field cannot enter `_content_snapshot()` and
   cannot bump `updated` / `last_seen`. **1,380 rows gaining a bumped `updated`
   would be both an unintended delta and a false claim** — no content changed;
   we are describing content that has not changed since 2026-05-31.
2. **It is re-derived every build**, which the marker must be.

**Re-derive, do not `setdefault`.** Retained priors are carried VERBATIM from
the previous `data/incidents.json` (step 6c) and bypass dedupe, so a retained
row can arrive already carrying a marker from an earlier build. `pop` the field
first, then set it if the rule applies — otherwise a source that recovers
leaves permanent stale markers on exactly the rows least able to shed them.
This is the same carry-forward hazard `source_status` has on retained rows.

**Registry, never the counter.** Read `data/source_freshness.json`. Do **not**
read `ingest/_state/source_health.json`: `main`'s copy is stale **by design**
(D5, accepted advisory), so a build reading it would republish a deliberately
stale file as current — a new instance of the class this work closes. Load it
the way `_load_curation_overrides()` loads its input
(`scripts/merge_and_dedupe.py:947`); it is a curated build input, not a
generated artifact.

**Do not put the registry under `ingest/`.** `merge_and_dedupe.py:1312` globs
`INGEST.glob("*.json")`; any JSON file placed as a direct child of `ingest/`
is ingested as a corpus source.

## 4. Surfaces

| Surface | Change |
|---|---|
| `data/incidents.json` | Carries the marker in full. |
| `data/incidents.min.json` | Carry it **conditionally**, exactly as `content_license` is carried at `scripts/merge_and_dedupe.py:1690-1694` — added only when present, never emitted as `null`. The slim shape truncates `tags` to 8 (`tags[:8]`), so a min.json consumer may not see the `airi-navigator` tag at all; the marker is the only freshness signal that reliably reaches them. |
| `docs/data/incidents.min.json`, `src/genai_incidents/data/incidents.min.json` | Mirrors; `scripts/render_markdown.py` copies them. Run it. |
| HuggingFace export | **No change needed** — `scripts/export_huggingface.py:148-149` dumps each row verbatim, so the field rides along. |
| STIX bundle | **Out of scope here.** `scripts/export_stix.py` builds SDOs field by field, so the marker will not appear unless added. Whether to mirror it as `x_source_freshness` (the D14 `x_content_license` precedent) is distribution-engineer's call — flagged, not specified. |
| Site templates | **No target exists.** Grepping site sources, README and docs finds no renderer for the `eu-ai-act` tag family; the as-of annotation D8 asks for is delivered by the data (`source_freshness.as_of` on precisely those rows) and the documentation. Do not build a renderer under this task. |
| `data/stats.json` / `DOC_SURFACES` | **No new key, no new count.** Invariant 6: no freshness count may reach a `DOC_SURFACES` file unless marker-derived, and none is needed. |

## 5. Expected field-level delta — the zero-unintended-delta gate

Measured on `data/incidents.json` at `378bf9b3` (13,119 entries):

| Quantity | Before | After | Intended? |
|---|---|---|---|
| Entry count | 13,119 | 13,119 | unchanged |
| ID set | — | identical | unchanged |
| Entries with `source_freshness` | 0 | **1,380** | **intended, the only field-level change** |
| `source_status` values | 13,110 active / 9 retained | identical | unchanged — this is the point of not overloading it |
| `tags` | — | identical on every row | unchanged; **no `eu-ai-act-*` tag is added, removed or annotated in-place** |
| `updated` / `last_seen` | — | identical on every row | unchanged (see §3) |
| every other field | — | identical | unchanged |

Assertions the applying task should be able to state and the reviewer to
re-derive independently:

1. Marked set == the 1,380 entries carrying tag `airi-navigator`.
2. That set is **exactly** the set carrying a tier `eu-ai-act-*` tag —
   symmetric difference **0** (verified at `378bf9b3`).
3. **`INC-02549` is NOT marked.** It carries a bare `eu-ai-act` tag, is
   manually authored and non-AIRI (E10's caveat). A marking that catches it has
   selected on the tag family instead of on source provenance.
4. The **109** entries carrying both `airi-navigator` and `oecd-aim` list
   `["airi_navigator"]` only — OECD is `ok`, and claiming its contribution is
   stale would be false.
5. Every marked row has `as_of == "2026-05-31"`; none has any other value.
6. No entry with `source_status: "retained"` is marked, at present — none of
   the 9 retained entries is AIRI-derived. This is an observation, not an
   invariant: the four states are independent by design.
7. Build is byte-identical across two consecutive runs.

## 6. Two code changes that come with the application

**(a) Completeness gate — required, `scripts/validate.py`.** The validator
currently checks that markers present are *consistent* with the registry; it
does not check that markers that *should* be present *are*. Add, in the same PR
as the data:

> For every registry source with `status == "stale"` and a non-null
> `row_marker`, every entry carrying that tag must have a `source_freshness`
> marker listing it; and no entry may carry a marker naming a source whose tag
> it does not have (already checked).

It is deliberately absent today because it would fail on the current corpus —
the corpus this task exists to fix. Landing it with the data makes the marking
non-optional from then on: a future build that silently stops marking fails
loudly instead of quietly reverting to the state of 2026-06-07.

**(b) Registry/counter reconciliation — required, `.github/workflows/auto-refresh.yml`.**
The registry's `observed_at` claims it was reconciled against the authoritative
counter; the DATA_DICTIONARY states the weekly refresh reconciles them and fails
loudly on divergence. **That sentence is true only once this lands.** If the
foreman splits (b) into a follow-up task, the one sentence in
`docs/DATA_DICTIONARY.md` §Source freshness beginning "The counter is what keeps
the registry honest" must be softened in the same PR that defers it — do not
leave a documented mechanism that does not exist.

Design:

- **Where:** between *Restore source health counters from refresh-state branch*
  and *Persist source health counters to refresh-state branch*
  (`.github/workflows/auto-refresh.yml:109-145`). That window is the **only**
  point in the run where the authoritative counter is in the working tree — the
  persist step resets the file back to `main`'s copy immediately afterwards, and
  the build runs after that. A check placed after the build would compare the
  registry against `main`'s stale-by-design copy and pass while meaning nothing.
- **Compare only:** the source key set, each source's `status`, and each
  source's `last_success`. **Do not compare `consecutive_failures` or
  `last_attempt`** — a dead source increments its counter every week, so
  publishing it would guarantee weekly divergence and turn the check into the
  `::warning::` nobody reads, which is the failure WS4-T9 was written to abolish.
  The registry deliberately publishes neither.
- **Behaviour:** report divergence as an error and fail the step. **Do not
  auto-rewrite the registry.** It is a reviewed publication on `main`; a silent
  unattended rewrite is both the write to `main` D5 refused and a bypass of
  review on a public claim. A human flips the status in a gated task, as this
  one did.
- Natural home: a `--registry <path>` flag on `scripts/check_source_health.py`,
  which already loads the authoritative state at exactly that point. Placement
  is the implementer's call; the window and the compared fields are not.
- **Keep the WS4-T6 boundary:** gate on step outcome, never on row counts.

## 7. What this buys for the next dead source

Declaring source #5 dead is a **status flip in `data/source_freshness.json`** —
set `status: "stale"`, `last_success`, `stale_since`, optionally a dated `hold`.
No schema change, no new field, no migration, no per-row authoring. Every row
that source contributed to is marked on the next build, and the completeness
gate makes it non-optional. AIRI is instance two after WS4-T9's class fix; this
is the shape that stops there being an instance-three special case.
