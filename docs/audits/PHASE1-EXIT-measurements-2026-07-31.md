# Phase-1 exit criteria — re-derived measurements, 2026-07-31

**Purpose: supply `[R] re-derived` evidence for the final Phase-1 exit checklist.**
Measured by the foreman on `ws6/release-notes-v290` at `dcc90ed6`, whose tree is
identical to `main` (`c4d856c9`) for every file below — the branch carries only
`PROGRESS.md`.

**Why this file exists.** PROGRESS.md's exit-checklist format rule states that
evidence cells are marked **[R] re-derived** (measured now, command shown) or
**[A] attested** (artifacts present, verdict is testimony), and that **no
criterion asserting a measurable property of the repo may be marked met on [A]
alone.** Four merges landed on 2026-07-31 and moved most of these numbers, so
the figures in `docs/audits/PHASE1-EXIT-2026-07-30.md` are stale by
construction. That file is a **dated record** and is not edited — it is
superseded, per working agreement 4. This is the superseding measurement.

## Method

Every figure below was produced by reading `data/*.json` directly or by running
the named command. **No figure is transcribed from the board, from the
2026-07-30 checklist, or from any agent report.** Where a number disagrees with
a previously recorded one, the disagreement is stated rather than silently
corrected.

## Corpus and composition

| Property | Value | How |
|---|---|---|
| Corpus entries | **13,060** | `len(json.load(data/incidents.json))` |
| Tombstones (`id_deprecations.json`) | **1,051** | direct read |
| Net change this release | **13,119 → 13,060 (−59)** | vs `804cb6ee` |
| Of which retired, not reduced | **59**, all `into: null` | all tombstoned; invariant 3 |

**The 59 are a retirement, not a reduction.** They were the corpus's only
surviving source rows in the orphaned `ingest/oecd_aim_incidents.json`. Any
downstream text describing this release as a pure text change is wrong.

## Licensing state

| Property | Value | How |
|---|---|---|
| `content_license` markers | **1,517**, all `CC-BY-SA-4.0`, all `source: aiaaic` | direct read |
| OECD-AIM-sourced rows | **3,829** | `source_ids` prefix scan |
| …carrying per-entry OECD attribution | **3,829 / 3,829 (100%)** | `references[].title` match |
| …carrying the reduced `description` | **3,667 / 3,829** | template-prefix match |
| …carrying a `content_license` marker | **0** | direct read |

The **162** OECD-sourced rows without the reduced description ship *another
source's* description, having lost the merge — so no OECD narrative reaches
`description` on any row.

> **⚠ UPDATE 2026-07-31 — SUPERSEDING NOTE. Do not regenerate this section; the
> text above stands as the record of what was measured before the error was
> found.** This file did not state a `title` figure, but the board and
> `NOTICE-DATA` did, and it was **wrong: the correct figures are `title`
> verbatim on 3,667 of 3,829 rows, residue 162** — **identical to the
> `description` partition above, not one row apart.**
> **The flaw:** the earlier measurement joined each row to **the first of its
> `OECD-AIM-` source_ids**. **58 rows carry more than one**; `INC-00311` carries
> twelve and its title matches its fourth, so it scored as non-OECD.
> Re-measured against *all* of each row's OECD sources, `title_any == desc_set`
> exactly. **The mechanistic reason, which should have made the split
> suspicious on sight: `merge_into()` never touches `title` or `description`,
> so both survive iff OECD won the merge — they are necessarily the same
> partition.** Found by the release-notes drafter, which cross-validated three
> independent ways rather than re-running the method that produced the figure.
> `NOTICE-DATA` and `.reuse/dep5` are routed for correction to 3,667/162. The **0** marker count is E23's ruling, not a gap:
AIID's and OECD's postures differ from AIAAIC's for reasons specific to each
maker's legal situs.

**Per D24, this table is not a second home for these figures.** The
authoritative homes are `NOTICE-DATA` (the `title` count) and
`docs/SOURCE_LICENSES.md`'s summary-of-outcomes row (the `description` count).
This file is a dated measurement record, not a live surface.

## Freshness and status fields

| Property | Value | How |
|---|---|---|
| Rows carrying `source_status` | **13,060 / 13,060** | direct read |
| Rows carrying `source_freshness` | **1,380** | direct read |
| Tracked sources | **4** (`aiaaic_sheet`, `airi_navigator`, `cisa_kev`, `oecd_aim`) | `data/source_freshness.json` |
| Sources `stale` | **1** — `airi_navigator` | ditto |
| …carrying a decision date | **yes** — `{"decision": "D8", "until": "2026-08-28"}` | ditto |

This satisfies D20(b)(ii)'s sharpened form of criterion 10: every dead source
has either a remediation or a hold **carrying a decision date**. The registry's
own note records that the marking never depended on the MIT reply and is not
part of the hold.

## Active-invariant gates

| Gate | Result | Command |
|---|---|---|
| Invariant 6 — docs pull counts from `stats.json` | **exit 0**, "clean: 5 doc surfaces match" | `python scripts/check_stats_drift.py` |
| Test suite | **314 passed** | `python -m pytest -q` |

## The five technicality flags — current state

| Flag | 2026-07-30 state | State now |
|---|---|---|
| **FLAG 1** — WS3-T5 row contradicts D13 | open; owner foreman | **✅ FIXED.** The row reads "done — decision MADE: E4 resolved by D13", with a **dated correction preserving what it previously said** rather than a silent rewrite. |
| **FLAG 2** — criterion 6 met only as of 2026-07-30 | flagged | **Unchanged and unchangeable** — it is a statement about history, not a defect to fix. Stays disclosed. |
| **FLAG 3** — criterion 9 clause 2 is 3-of-4 | OECD drafted, not sent | **Unchanged — USER ACTION.** Closes when the user sends and logs the date. |
| **FLAG 4** — `CHANGELOG` "Static TAXII 2.1 endpoint" | open; owner WS6 | **Still present at `CHANGELOG.md:179`** (line moved from `:137` only because E21's `[Unreleased]` was inserted above; text byte-identical). **Every live surface is correct.** Now carries an undecided fork — see below. |
| **FLAG 5** — criterion 10 met by a date that did not exist for 12 days | flagged | **Unchanged** — statement about history. The date now exists and is machine-readable. |

## The banked consistency items

| Item | State |
|---|---|
| **dep5:44** — the maker-non-qualification grammar | **✅ RESOLVED**, merged. `.reuse/dep5` now attributes non-subsistence to **maker** non-qualification, matching `NOTICE-DATA`. |
| **REUSE lint** | **Figure has drifted twice** — 63/204 → 69/226 → 69/227. **Do not cite a stored number; re-measure at packet time or omit.** The underlying non-compliance is long-known and unchanged. |

## Open, and not blocking Phase-1 exit

- **FLAG 4's fork, undecided:** `CHANGELOG.md:179` sits under a **past-release
  heading** (`[2.5.0]`). Working agreement 4 says a record of what was claimed
  then is **superseded with a dated note, never rewritten**; WS6-T4's
  acceptance criterion says *"no surface says 'TAXII endpoint'"*, phrased as
  **in-place correction**. The two point opposite ways on the one line WS6-T4
  exists to fix. **Decide before dispatching WS6-T4, not mid-task.**
- **`VERSION = "2.0.0"`** exported from `src/genai_incidents/__init__.py:39`
  while `pyproject.toml` says `2.8.0`, and it is in `__all__`. Routed to
  WS6-T1, whose job is deciding what a consumer should be able to ask for.
- **The optional four-character README improvement** ("refuse to open **new**
  bridges"), gate-pre-verified, needs no re-gate if taken.

## What this file does not claim

- It is **not** the exit checklist. It supplies measurements; the checklist
  applies them to criteria and states met/not-met.
- It does **not** re-verify gate verdicts. Those are testimony, recorded on the
  board per working agreement 5.
- Its figures are **true as of `c4d856c9`**. Anything merged after that must be
  re-measured — this file is a record of a moment, not a live surface.
