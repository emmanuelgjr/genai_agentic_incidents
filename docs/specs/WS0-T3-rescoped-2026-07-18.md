# WS0-T3 — AIAAIC Facts-Reduction — RE-SCOPED IMPLEMENTATION SPEC

**Date:** 2026-07-18
**Supersedes:** the implementation portion of the D9-approved spec.
**Status:** DRAFT — awaiting user review. Nothing dispatches until the user
approves this spec.
**Correction basis:** D9 approved the field-cut as a pure licensing operation.
It is not. The ungated rebuild silently relabelled **372 AIAAIC entries**
because two deterministic-build heuristics read the *published* `description`
prose that the cut removes. See `docs/audits/WS0-T3-cascade-2026-07-18.md` for
the full evidence. This spec keeps the D9 licensing decision intact and fixes
the coupling.

---

## 1. Unchanged from D9 (still binding)

- AIAAIC per-row `description` keeps **only** categorical facts —
  `system` · `technology` · `sector` · `jurisdiction` — plus the existing
  reference link. It **drops** AIAAIC's editorial-prose cells
  `purpose` · `ethical` · `consequence` · `response` (CC BY-SA-protected
  expression). No model summary (facts + link, per D2).
- Schema fields `description_provenance` (`verbatim|summary|original`) and
  `description_source` (slug) stay, both excluded from `merge_into` (already
  committed at `a2d7a26e`).

## 2. New requirements (the fix)

### (a) Decouple label derivation from the published description

The mapping/corpus seed must be computed from AIAAIC's structured cells captured
**at ingest, before description composition** — never re-derived from the
published, prose-stripped `description`.

**Correction (2026-07-18, D10 — the user caught this).** The earlier draft said
the ingest row "retains the `ethical` cell internally." That is **wrong**:
`ingest/aiaaic_sheet_incidents.json` is a tracked, committed, public file, so
any retained AIAAIC prose is still redistributed. **No AIAAIC verbatim editorial
prose may persist in ANY committed file** (see the prose audit below).

- At ingest, `ingest_aiaaic_sheet.py` **extracts the `ethical` cell into a
  controlled-vocabulary tag list** — normalized categorical values only, e.g.
  `aiaaic_ethical_tags: ["misinformation", "safety"]`, mapped from AIAAIC's
  ethical-issue labels through a fixed, committed vocabulary. A categorical fact
  list, not expression. The mapping/corpus seed reads **this list** (plus the
  categorical cells system/technology/sector/jurisdiction), never the published
  `description` and never any retained raw prose.
- The two coupled heuristics currently reading the published description
  (`scripts/merge_and_dedupe.py`):
  - `classify_attack_vector()` / the finalize-reclassify block (`:1282–1305`)
    — Path A (`attack_vector` → OWASP/ATLAS/NIST via
    `seed_frameworks_from_vector()` `:287` and `fill_taxonomy()` `:640`).
  - `_classify_corpus()` (`:534`, applied `:1358`) — Path B (`corpus`
    → landmark tier via `_derive_tier()` `:161`).
  must receive their classification text from the **structured ingest cells**
  for AIAAIC-origin entries, not from the published `description`.
- Both the published `description` in `data/incidents.json` **and** the
  `description` in `ingest/aiaaic_sheet_incidents.json` are reduced to the
  categorical form. The raw prose cells (purpose/ethical/consequence/response)
  are consumed transiently during ingest and **written nowhere**. Any internal
  field the classifiers read must be excluded from `merge_into` and must hold
  only normalized tags — never prose. The invariant is: **published prose
  removal must not move any label, and no committed file carries AIAAIC prose.**
- **Prose audit — must reach 0 in every committed file.** Today
  `ingest/aiaaic_sheet_incidents.json` carries prose in all four dropped cells:
  **Purpose 1485, Ethical issues 1498, Reported consequences 421, Response 281**
  (of 1500 records); `ingest/aiaaic_incidents.json` (95 records) is already
  clean (0). Acceptance greps the cell markers (`AIAAIC report:` / `Purpose:` /
  `Ethical issues:` / `Reported consequences:` / `Response:`) across all
  committed `ingest/*.json` and `data/*.json` and requires **0**. Each of the
  four dropped cells is audited the same way — any that carries prose in a
  committed file is removed; only normalized categorical derivations
  (`aiaaic_ethical_tags`, and the kept system/technology/sector/jurisdiction
  facts) may remain.

### (b) Regression test — seed independence from published description

Add a test asserting the mapping/corpus seed does **not** depend on published
`description` text: take an AIAAIC-origin entry, blank/rewrite its published
`description` to the reduced categorical form, and assert `attack_vector`,
`owasp_llm`, `mitre_atlas`, `mitre_atlas_tactics`, `nist_ai_rmf`, and `corpus`
are **identical** to the pre-reduction build. A future edit that re-couples the
classifiers to published prose must fail this test.

### (c) Acceptance gate — full field-level before/after delta

Acceptance now requires a **full field-level before/after delta** produced as a
committed artifact, across at minimum:
`attack_vector`, `owasp_llm`, `owasp_asi`, `mitre_atlas`,
`mitre_atlas_tactics`, `nist_ai_rmf`, `owasp_dsgai`, `severity`, `corpus`,
`quality_tier`/`tier`, `landmark_count`, and entry count + ID set.

- **Zero unintended deltas.** Any non-zero delta must be **enumerated and
  justified** in the delta report as intended.
- **Baseline = `a2d7a26e`'s committed data.** The gate requires **ZERO taxonomy
  deltas vs `a2d7a26e` — exact set equality per entry (identical mapping sets),
  not merely similar distributions.** The only deltas permitted are: the
  `description` text (in both `data/incidents.json` and
  `ingest/aiaaic_sheet_incidents.json`), the new `aiaaic_ethical_tags`, and
  `description_provenance` / `description_source`. `attack_vector`, `owasp_llm`,
  `owasp_asi`, `mitre_atlas`, `mitre_atlas_tactics`, `nist_ai_rmf`,
  `owasp_dsgai`, `severity`, `corpus`, `quality_tier`/`tier`, and
  `landmark_count` must be **byte-for-byte unchanged** vs `a2d7a26e`.
  - *Caveat the impl must handle:* `a2d7a26e`'s published labels were themselves
    partly prose-derived (the cascade showed HEAD held `attack_vector` values
    the current ingest code no longer emits). Reproducing them exactly may
    require the re-scoped seed to replicate that mapping logic from
    `aiaaic_ethical_tags`. Any residual divergence is either a defect to
    reconcile or an intended delta to enumerate and justify — **never silent.**
- red-reviewer gates on this delta (see the new standing rule on transformative
  data operations).

### (d) Validation sample as a committed file

Before the batch runs, produce a **committed** validation sample of **15–20
AIAAIC entries showing the actual content of all eight source cells**
(`system` · `technology` · `sector` · `jurisdiction` · `purpose` · `ethical` ·
`consequence` · `response`) alongside the resulting reduced `description`, so a
human can confirm the keep/drop line on real data. This is a file under
`docs/audits/` or `docs/samples/`, **not** chat output.

## 3. Retained mechanism notes (from D9 scoping)

- `merge_into` (`merge_and_dedupe.py:1636-1691`) never touches `description`;
  dedupe is first-hit-wins (`:1059`), so `description`/provenance are sticky to
  the dedup target while `tags`/`source_ids` union. The new fields and any
  internal classification field must stay **excluded from `merge_into`** — that
  exclusion is the AIAAIC-origin detection mechanism.
- `impact` / `mitigations` are already clean (AIAAIC ingest never sets them).
- No network/model in `make build`. `summarize_descriptions.py` /
  `data/summaries/` remain deferred, not scaffolded.

## 4. Owners

- **schema-architect** — any schema shape needed for the internal
  classification field (sole writer of `schema/`).
- **pipeline-engineer** — `ingest_aiaaic_sheet.py` (retain cells internally,
  reduce published description), classifier plumbing in `merge_and_dedupe.py`,
  the regression test (b), the delta report (c), the validation sample (d),
  and the rebuild.
- **red-reviewer** — gates on the zero-unintended-delta report; PASS merges per
  D7.

## 5. Acceptance checklist

- [ ] Published AIAAIC descriptions carry categorical facts only (0 dropped-cell
      markers) — the D9 licensing goal.
- [ ] Full field-level before/after delta committed; **zero unintended deltas**;
      any intended delta enumerated + justified.
- [ ] Regression test (b) present and passing: label seed independent of
      published description text.
- [ ] Validation sample (15–20 entries, all eight cells) committed before batch.
- [ ] `make build` uses no network/model; determinism byte-identical; entry
      count 12,986 preserved.
- [ ] `merge_into` did not gain the new/internal fields.
