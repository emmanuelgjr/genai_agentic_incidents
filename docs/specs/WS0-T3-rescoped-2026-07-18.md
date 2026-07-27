# WS0-T3 — AIAAIC Facts-Reduction — RE-SCOPED IMPLEMENTATION SPEC

**Date:** 2026-07-18
**Supersedes:** the implementation portion of the D9-approved spec.
**Status:** DRAFT — the §2(e) dispatch hold is **LIFTED (2026-07-27)** per
D11 (`docs/audits/WS0-E13-database-right-2026-07-18.md` §6.1; PROGRESS.md D11
row): the E13 direction is decided as options **(b)+(d)**. §6 below folds
D11(b)'s row-level attribution/ShareAlike containment requirements into this
spec. **Awaiting user review of this amendment specifically** before any
dispatch; once approved, the implementation chain is schema-architect (field/
tag shape, §6.1) → pipeline-engineer (impl) → red-reviewer (gate, per the
standing transformative-data-operation rule). Nothing dispatches until the
user approves this amended spec.
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

### (e) Database-right requirements (from E13, 2026-07-18)

E13 (`docs/audits/WS0-E13-database-right-2026-07-18.md`) found that D2/D9 resolve
the **copyright** question only; the EU/UK **sui generis database right** is a
distinct regime this reduction does not, by itself, dispose of. Two requirements
land in WS0-T3 (the rest are user/policy decisions — see the E13 escalation on
the board):

- **Ingest instrumentation.** Add committed logging (not just the existing
  stdout `print(f"[aiaaic] {len(rows)} raw rows")` at `ingest_aiaaic_sheet.py:390`)
  recording, per ingest run, AIAAIC's **live total Incidents-sheet row count**
  alongside the count retained after GenAI filtering — a real denominator for
  any future substantiality re-check.
- **Database-right acceptance gate.** WS0-T3's acceptance must carry a
  database-right item **distinct from** the copyright/prose-audit gate. The
  "0 dropped-cell markers" / "categorical facts only" checks close the
  *copyright / share-alike* sub-question **only**; they do not close AIAAIC
  licensing risk generally. Until the E13 escalation is resolved by the user,
  WS0-T3 must not represent AIAAIC licensing as "resolved."

**Hold lifted (2026-07-27) — D11 decided.** The user has decided the E13
direction: **D11 = options (b)+(d)** (`docs/audits/WS0-E13-database-right-2026-07-18.md`
§6.1; PROGRESS.md D11 row). D11(b) is a **lightweight row-level containment**
— not the heavier pointer-only/row-ceiling redesign this paragraph originally
warned might discard the controlled-vocab-tag plumbing above; that plumbing
(§2(a)) stands unchanged, see §6.4. D11(d) (scope-narrowing toward
security-relevant entries) is the standing Phase-2/WS1-T4 direction and
starts nothing in this spec. See **§6** for the D11(b) implementation
requirements. This spec (as amended by §6) is ready to move to
schema-architect/pipeline-engineer once the user reviews and approves this
amendment — the prior blanket hold on dispatch is lifted; the requirement
that the user review this specific amendment first is not.

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
  classification field (sole writer of `schema/`); **also owns the field/tag
  shape decision for the D11(b) per-row attribution/ShareAlike marker (§6.1)**,
  including the explicit min.json inclusion/exclusion call (§6.1(ii)).
- **pipeline-engineer** — `ingest_aiaaic_sheet.py` (retain cells internally,
  reduce published description), classifier plumbing in `merge_and_dedupe.py`,
  the regression test (b), the delta report (c), the validation sample (d),
  the rebuild, **and the D11(b) marker propagation + corpus-level notice text
  in `NOTICE-DATA`/`.reuse/dep5`/README (§6.1(iii), §6.3)**.
- **red-reviewer** — gates on the zero-unintended-delta report; PASS merges per
  D7. **Also gates §6.2's D11(b) acceptance additions** (marker coverage
  greps, corpus-notice-text greps) as part of the same PASS/BOUNCE verdict.

## 5. Acceptance checklist

- [ ] Published AIAAIC descriptions carry categorical facts only (0 dropped-cell
      markers) — the D9 licensing goal.
- [ ] Full field-level before/after delta committed; **zero unintended deltas**;
      any intended delta enumerated + justified.
- [ ] Regression test (b) present and passing: label seed independent of
      published description text.
- [ ] Validation sample (15–20 entries, all eight cells) committed before batch.
- [ ] `make build` uses no network/model; determinism byte-identical; entry
      count preserved exactly (measured against `data/stats.json`
      `incident_count` at the rebuild's base commit; the WS0-T3 reduction
      rewrites `description` content and adds the D11(b) marker — it must add
      or remove **ZERO** entries). *(2026-07-27: this line previously
      hardcoded "12,986 preserved" — that was the count on 2026-07-17; the
      corpus has since moved via weekly refresh #97 and the WS0-T4 snapshot
      swap. Rewritten to a relative, self-refreshing criterion so it can't go
      stale again.)*
- [ ] `merge_into` did not gain the new/internal fields.
- [ ] Committed AIAAIC live-total-row-count logging present (denominator for any substantiality re-check).
- [ ] Database-right acceptance item present and distinct from the copyright/prose gate; AIAAIC licensing NOT represented as fully resolved pending the E13 user decision.
- [ ] **D11(b) row-level containment — see §6.2 for the full, greppable list.**
      Every `description_source == "aiaaic"` entry carries the new marker;
      zero non-AIAAIC entries carry it; `NOTICE-DATA`/`.reuse/dep5`/README
      state the AIAAIC subset's open-database-right/row-level-ShareAlike
      status on par with AIID's existing framing (§6.3); the min.json
      inclusion/exclusion call is explicitly recorded, not defaulted.

## 6. D11(b) row-level attribution/ShareAlike containment (2026-07-27)

**Decision basis.** `docs/audits/WS0-E13-database-right-2026-07-18.md` §6.1,
decided 2026-07-27 as **D11 = options (b)+(d)** (PROGRESS.md D11 row). E13's
final state, after the 2026-07-27 domicile confirmation: genai_incidents
holds no UK/EU sui generis database right (sole Canadian-resident individual
maker), so CC BY-SA §4(b) database-level ShareAlike is **dead**; the
worst-case exposure is §4(c)→§3(a) **row-level** ShareAlike/attribution on
AIAAIC-derived rows only, conditional on AIAAIC's own right subsisting (§1
there, plausible/more-likely-than-not) and our extraction being substantial
(§2 there, ≈76% of AIAAIC's live repository). D11(b) contains that worst case
at the row level. D11(d) (scope-narrowing toward security-relevant entries,
WS1-T4/E5) is the standing Phase-2 direction and is cross-referenced here
only (§6.4) — it starts nothing in this spec.

### 6.1 Requirements

These are acceptance-criteria-level requirements, not schema edits — the
field/tag shape is **schema-architect's** call (sole writer of `schema/`);
this spec records only what the shape must accomplish.

**(i) Machine-readable per-row marker.** Every AIAAIC-origin row — detected
via `description_source == "aiaaic"` (the existing merge-into-excluded
detection mechanism, §1/§2(a) above) — must carry a machine-readable
attribution/license marker distinct from `description_source` itself (which
names provenance for the *description* field specifically and is not itself
a license/ShareAlike declaration). schema-architect chooses the shape — a
dedicated per-row field (e.g. `content_license` / `attribution_notice`), a
tag in the existing `tags` list, or another mechanism; this spec does not
prescribe which. Whatever the shape, it must be **source-generic in
naming** (not `aiaaic_license` or similarly source-locked): a future source
could need the identical mechanism, and AIID's own NOTICE-DATA/.reuse/dep5
text already flags a parallel open question (§6.3).

**(ii) Survives merge/dedupe; appears in every surface that carries the
row.** The marker must have the same sticky semantics as `description_source`
— set once by whichever entry survives dedup as the merge target, excluded
from `merge_into`'s union/absorb behavior (§3 above), never silently dropped.
Checked against every current published surface:

- `data/incidents.json` (the full record) — carries it directly once the
  field/tag exists; no additional plumbing needed beyond the field itself.
- `data/incidents.min.json` — **verified it does not currently carry
  `description_provenance` or `description_source` at all**
  (`merge_and_dedupe.py:1590-1613`'s `slim` dict keeps only id/title/date/
  year/severity/attack_vector/owasp_llm/owasp_asi/nist_ai_rmf/mitre_atlas/
  cve_ids/primary_reference/description/affected/tags/quality_tier/corpus).
  Adding the new marker here is a **new field addition to a deliberately
  slim, taxonomy-focused projection**, not a passthrough of an existing
  field. This spec does **not** resolve whether min.json should carry it —
  arguments run both ways (min.json is widely redistributed and the
  ShareAlike notice arguably needs to travel with it; against that, it is a
  design change to a schema explicitly scoped to taxonomy facts, beyond this
  reduction's stated scope). **Flagged as an open decision for
  schema-architect/pipeline-engineer, to be resolved explicitly and recorded
  in the implementation report — not defaulted either way.**
- HF export (`scripts/export_huggingface.py`) — verified this is a **flat
  projection of `data/incidents.json["incidents"]`** (`export_huggingface.py:11-13`),
  so the marker propagates automatically once added to the full record; no
  separate HF-export code change is needed for the machine marker itself.
  The **corpus-level notice** (requirement (iii) below) is separate and
  belongs in the HF dataset card's prose (the `CARD` template, same file),
  which does not currently mention AIAAIC or any per-source ShareAlike
  status at all.
- STIX (`scripts/export_stix.py`) / MISP (`scripts/export_misp.py`) —
  **verified neither currently reads `description`, `description_source`, or
  `description_provenance`** (grepped both files: no matches beyond the
  fields each already maps — MISP's attribute set is
  `title`/`tags`/`cve_ids`/`references` only, `export_misp.py:75-127`; STIX's
  bundle construction shows the same absence). Neither export currently
  surfaces AIAAIC-derived content in a form the marker would need to travel
  with. **This spec does not require STIX/MISP to gain the marker** unless
  and until either export is changed to carry `description` or equivalent
  AIAAIC-derived content — a conditional requirement, not a present one;
  pipeline-engineer should re-check this conclusion if either exporter's
  field set changes.
- `.zenodo.json` — carries only repository-level metadata (title, creators,
  license), not per-row content; no per-row marker applies. Whether it needs
  a brief mention as part of the corpus-level notice (iii) was not checked in
  this task (out of scope — this task touches only this spec file); flag for
  whoever implements (iii) to verify.

**(iii) Corpus-level notice.** `NOTICE-DATA` and the README source list must
state the AIAAIC subset's status: CC BY-SA-derived facts, database-right
question OPEN pending AIAAIC's reply (or qualified-counsel resolution),
ShareAlike honored at the row level via the (i) marker. **This folds in and
discharges the parked 2026-07-18 docs-warden follow-up** (board note: AIAAIC's
open-question visibility asymmetry vs. AIID's, in `NOTICE-DATA`/`.reuse/dep5`/
README) — see §6.3 for the exact asymmetry found and the file list this
discharges.

### 6.2 Acceptance additions

- [ ] Every entry with `description_source == "aiaaic"` carries the new
      marker — e.g. `jq '.incidents[] | select(.description_source=="aiaaic") | select(<marker-field-absent-or-empty>)'`
      against `data/incidents.json` returns empty.
- [ ] Zero non-AIAAIC entries carry the marker — same query inverted:
      `jq '.incidents[] | select(.description_source!="aiaaic") | select(<marker-field-present>)'`
      returns empty — **unless** a future source is deliberately given the
      same marker, in which case this assertion is re-scoped per-source, not
      dropped; the source-generic naming in (i) already anticipates this.
- [ ] `NOTICE-DATA` states the AIAAIC subset's CC BY-SA/database-right/
      row-level-ShareAlike status (greppable: the AIAAIC paragraph names
      "database right"/"database-right" as "open"/"OPEN", matching the
      AIID paragraph's existing pattern — §6.3).
- [ ] README's source list / licensing text states the same status
      consistently with NOTICE-DATA (identical substance, not necessarily
      identical wording).
- [ ] `.reuse/dep5`'s `data/*`-block comment states the same status
      consistently (same test as above).
- [ ] The min.json inclusion/exclusion decision (§6.1(ii)) is **explicitly
      recorded** in the implementation report — not silently defaulted
      either way.
- [ ] The existing zero-unintended-delta gate (§2(c)) and the D10
      committed-ingest prose-strip acceptance (§2(a)/(d)) are **UNCHANGED
      and still bind** — D11(b) adds a new field/tag and new docs text; it
      must not touch any taxonomy field, and the delta report must show the
      new marker as the only additional intended delta beyond what §2(c)
      already enumerates.

### 6.3 The docs-warden asymmetry this discharges

Verified directly in this task: `NOTICE-DATA` (repository root) and
`.reuse/dep5` both currently state, for AIID: *"AIID's CC-BY-SA share-alike
and a parallel database-right question remain an open, unresolved item, same
posture as AIAAIC's E13 finding"* — but AIAAIC's own paragraph in the **same
two files**, immediately preceding that sentence, states flatly (NOTICE-DATA):
*"AIAAIC content is never carried verbatim in this dataset... so no
share-alike obligation attaches and LICENSE-DATA carries no BY-SA
carve-out"* / (`.reuse/dep5`): *"AIAAIC-derived entries carry no BY-SA subset
per decision D2"* — with **no mention that the database-right question is
open**, even though the AIID sentence immediately after it depends on the
reader already knowing AIAAIC has an equivalent open finding. A reader of
only the AIAAIC paragraph in either file would reasonably conclude AIAAIC is
fully resolved; only the AIID paragraph's cross-reference reveals otherwise.
This is exactly the visibility asymmetry the 2026-07-18 docs-warden sweep
flagged and parked pending E13's outcome. **Files to fix, folded into this
spec's file list so they land with the D11(b) implementation:**
- `NOTICE-DATA` (currently lines ~43-47, the AIAAIC paragraph)
- `.reuse/dep5` (currently lines ~18-19, the AIAAIC clause inside the
  `data/*` block comment)
- README's "Sources aggregated" AIAAIC bullet (`README.md:225`) — currently
  a bare description with no licensing caveat at all, unlike the AIID bullet
  two lines above it which already notes the snapshot-channel method. Lower
  priority than the two licensing-framing files above (the README bullet
  list was never a licensing-status surface for any other source either),
  but should get the same one-line pointer to NOTICE-DATA/SOURCE_LICENSES.md
  for consistency, per requirement (iii).

### 6.4 What D11 does NOT change

- The facts-only reduction (D9's field cut: keep `system`/`technology`/
  `sector`/`jurisdiction` + link, drop `purpose`/`ethical`/`consequence`/
  `response`) stands exactly as specced in §1 above.
- The D10 committed-ingest prose strip (§2(a)/(d): no AIAAIC verbatim prose
  in any committed file, including `ingest/aiaaic_sheet_incidents.json`)
  stands exactly as specced.
- The label-seed decoupling (§2(a)) and its regression test (§2(b)) stand
  exactly as specced — `aiaaic_ethical_tags` remains the classifier input,
  never the published description.
- The committed validation sample (§2(d), 15–20 entries) stands exactly as
  specced.
- The per-run AIAAIC row-count/denominator logging (§2(e), first bullet)
  stands exactly as specced.
- D11(d) (scope-narrowing to security-relevant entries) is **Phase-2/
  WS1-T4/E5** territory and appears in this spec only as a cross-reference
  (§6's decision-basis paragraph); nothing in WS0-T3 implements it.
- The AIAAIC outreach question (`docs/outreach/aiaaic-facts-link.md`)
  remains in flight, unsent pending the user (per CLAUDE.md, the user sends
  outreach personally). Its answer may later **simplify** this containment
  — a waiver, or a "we don't consider this to engage database right" reply,
  could turn the marker from a ShareAlike-implying notice into an
  attribution-only one. **This spec should be re-checked against any AIAAIC
  reply before final implementation sign-off**, not treated as permanently
  fixed once written.
