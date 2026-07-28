# WS0-T3 Phase A — Validation Sample + Corpus-Wide Dry-Run Delta Preview

**Date:** 2026-07-27
**Author:** pipeline-engineer (Phase A resume, after a prior agent died mid-write
on an account spend limit — see `PROGRESS.md` "outage snapshot" `040dcb04`)
**Governing specs:** `docs/specs/WS0-T3-rescoped-2026-07-18.md` §2(c)/(d),
`docs/specs/WS0-T3-marker-shape-2026-07-27.md`
**Status:** Phase A exit artifact. This is the committed evidence the user
reviews before any batch/rebuild runs. **No batch has run.** Every
data/ingest file this preview touched was regenerated locally, measured, and
then reverted — see §5.

---

## 1. What this document is

Per the rescoped spec's acceptance checklist:

- §2(d): a committed validation sample of 15–20 AIAAIC entries showing all
  eight source cells (`system`/`technology`/`sector`/`jurisdiction`/`purpose`/
  `ethical`/`consequence`/`response`) alongside the resulting reduced
  `description`, so a human can confirm the keep/drop line on real data (§4).
- §2(c): a full field-level before/after delta, with **zero unintended
  deltas** or, where a residual divergence exists, it is **enumerated and
  justified, never silent** (§3).

Both are produced from an **offline dry run** — the real ingest/merge code
path, run against a **local-only, gitignored** AIAAIC sheet CSV snapshot
(`ingest/_cache/aiaaic_sheet.csv`, 958,849 bytes, fetched 2026-07-17;
`ingest/_cache/` is excluded by `.gitignore:29` and this file has never been
tracked on any ref — **it is not recoverable from the repo**, and is not
committed by this document), with **zero network calls** (verified:
`download_csv()` was monkeypatched to read only that cache file; no other
part of the dry run touches the network). All of it is reverted; see §5 for
the exact commands, the full driver, and the resulting clean `git status`.

## 2. A second regression found and fixed during this dry run

Before the delta numbers below were "clean," the first full dry run (against
the inherited Phase-A commits `6ca1c296`/`06c0709b`, before this session's
own commit) surfaced **148 unintended field deltas** — nowhere near the
"zero unintended deltas" bar §2(c) requires. This section documents that
finding, the root cause, and the fix (commit `4be139a7` on this branch,
code + tests only, no data/ingest change), because §2(c) requires any
non-zero delta to be enumerated and justified, never silently absorbed into
"the sample looked fine."

*Note on commit hashes: a rebase onto `main` after this fix landed replaced
every hash this Phase-A resume originally cited with a patch-id-identical
successor. `40952475`→`4be139a7`, `b96de176`→`6ca1c296`, `d626be60`→`06c0709b`,
`3576be3a`→`ab3e7cf4`. The four originals are unreachable from any ref
(present only in this machine's local object store); the hashes used
throughout this document are the live, post-rebase ones.*

**Root cause.** `_aiaaic_seed_text()`, as committed at `6ca1c296`, replaced
the classifiers' input for AIAAIC-origin entries with `aiaaic_ethical_tags`
**alone**. That correctly stops the classifiers from reading dropped
`purpose`/`ethical`/`consequence`/`response` **prose** (the cascade-audit
bug this decoupling exists to fix — `docs/audits/WS0-T3-cascade-2026-07-18.md`).
But it also stopped them from reading the **kept, safe, categorical**
`system`/`technology`/`sector`/`jurisdiction` facts — which used to reach
the old merge-time reclassify as part of the old, full `description` string,
and which independently drove real classification decisions with no
prose/licensing content involved at all. Concrete example (`INC-01719`):

| | |
|---|---|
| Ethical cell | `Accountability; Consent; Safety; Transparency` (no "deepfake") |
| Old description | `...Technology: Deepfake; Generative AI. Purpose: Nudify students...` |
| Old `attack_vector` | `deepfake` — matched on the word "Deepfake" in the **Technology** sentence |
| New seed (tags-only) | `accountability consent safety transparency` — no "deepfake" substring |
| New `attack_vector` (before fix) | `other` — silent downgrade, zero prose involved |

This is not the cascade-audit bug reappearing (no dropped prose was read);
it is a **second, narrower** regression in the same decoupling work, and it
cascaded into `owasp_llm`/`mitre_atlas`/`mitre_atlas_tactics`/`nist_ai_rmf`
(via `seed_frameworks_from_vector()`, which backfills those from
`attack_vector`) and into `corpus`/`tier` (via `_classify_corpus()`, which
uses the same seed function).

**Fix.** Capture `system`/`technology`/`sector`/`jurisdiction` as their own
internal field, `aiaaic_seed_facts`, at ingest — **structured cells captured
before description composition**, per spec §2(a)'s literal requirement,
never the composed `description` string itself (even though today that
string is safe/prose-free; the seed must not depend on the composed string
in *any* form, so a future formatting change to it can never silently move a
label). `_aiaaic_seed_text()` now returns
`aiaaic_seed_facts + " " + aiaaic_ethical_tags`. Same mechanism as
`aiaaic_ethical_tags` throughout: set at the ingest code path, excluded from
`merge_into`'s key lists and `_CONTENT_FIELDS` by omission, stripped before
output assembly, no schema entry (root schema is `additionalProperties:
false`). Two new regression tests lock this in
(`test_attack_vector_seed_uses_kept_facts_not_just_ethical_tags` reproduces
the exact `INC-01719`/`INC-03961` shape; the sibling
`test_aiaaic_seed_text_reads_seed_facts_plus_ethical_tags_not_description`
proves the seed still never reads `description`). 227 tests pass (was 225
at `06c0709b`; the shipped tree's +4 over this branch's original count is
`tests/test_export_stix.py` growing from 4 to 8 tests via the later rebase
onto `main`, unrelated to this fix).

**Result:** 148 field deltas (103 `attack_vector` plus 9+9+9+12+3+3 across
the six cascaded fields named above — `owasp_llm`, `mitre_atlas`,
`mitre_atlas_tactics`, `nist_ai_rmf`, `corpus`, `tier` — not 148 distinct
entries, since one entry's `attack_vector` change can cascade into several
dependent fields at once) → **2** residual `attack_vector` deltas. Of those
two, one (`INC-02406`) is root-caused below (§3.3) to the genuinely-dropped
`purpose` cell; the other (`INC-04316`) is root-caused to a spurious
cross-field regex artifact in the *old* code, not to any dropped content —
see §3.3 for both.

## 3. Corpus-wide dry-run delta preview

Measured 2026-07-27, dry run against the a2d7a26e-descended baseline
currently on `main`/this branch (before this session's fix,
`data/incidents.json` as committed at the branch tip prior to this run).
Methodology: offline-ingest the local-only, gitignored AIAAIC sheet CSV
snapshot with the new code (→ `ingest/aiaaic_sheet_incidents.json`), then run
the real `scripts/parse_existing.py` + `scripts/merge_and_dedupe.py`
(`make merge`), then `scripts/validate.py`. No network or model call anywhere
in this path (the only network-shaped step, `download_csv()`, was
monkeypatched to read only that local cache file — see §5 for the full
driver).

**Scope of this sweep.** This dry run's diff covered all 45 per-entry corpus
fields, not just the subset itemized below. Outside the 7 that changed —
`attack_vector` (§3.3) and `description`/`description_provenance`/
`description_source`/`content_license`/`updated`/`last_seen` (§3.4) — the
remaining 38 per-entry fields, including `title`, `tags`, `source_ids`,
`references`, `id`, `added`, and `first_seen`, showed **zero** changes
anywhere in the corpus. (`generated` is a separate, single top-level
timestamp, not one of these 45 per-entry fields — its own change is recorded
in §3.4 too.) What follows names only the fields with a non-zero or
otherwise noteworthy result; the other 38 were measured, not merely assumed,
unchanged.

### 3.1 Entry count / ID set (spec §2(c), §5 relative criterion)

| | Before | After |
|---|---|---|
| Entry count | 13,115 | 13,115 |
| IDs removed | — | **0** |
| IDs added | — | **0** |

Exact set equality: `{ids in before} == {ids in after}`, verified by direct
set difference, not just a count match.

### 3.2 Taxonomy/label fields — must be byte-for-byte unchanged (spec §2(c))

| Field | Entries changed | |
|---|---|---|
| `attack_vector` | **2** | see §3.3 — both justified |
| `owasp_llm` | 0 | |
| `owasp_asi` | 0 | |
| `mitre_atlas` | 0 | |
| `mitre_atlas_tactics` | 0 | |
| `nist_ai_rmf` | 0 | |
| `owasp_dsgai` | 0 | |
| `severity` | 0 | |
| `corpus` | 0 | |
| `quality_tier` | 0 | |
| `tier` | 0 | |
| `landmark_count` (derived: count of `tier=="landmark"`) | 1,905 → 1,905 (0 changed) | |

### 3.3 The two residual `attack_vector` deltas — enumerated and justified

The two deltas have **different root causes**, and only one of them is a
genuinely-dropped-content story. Each was root-caused by ablating the *old*
merge-time reclassify text against the real classifier
(`scripts/merge_and_dedupe.py`), not just by inspecting the raw sheet row.

| ID | Old `attack_vector` | New `attack_vector` | Root cause |
|---|---|---|---|
| `INC-02406` | `unsafe-advice` | `other` | Genuinely-dropped content. The old merge-time reclassify matched suicide/self-harm keywords in the **`purpose`** cell (*"Provide methods to commit suicide"*) — not in `ethical` (`Accountability; Anthropomorphism; Safety`) or in any kept fact. Ablation confirms: `title + seed(facts+tags)` (no `purpose`) → `None`; only re-adding the `purpose` prose restores `unsafe-advice`. Not recoverable without re-coupling to dropped prose, by design. |
| `INC-04316` | `algorithmic-bias` | `other` | **Not** dropped content — a spurious cross-field regex artifact in the *old* code. See below. |

**`INC-02406`** is the case spec §2(c) anticipates: a residual divergence
rooted in genuinely-dropped, AIAAIC-authored prose (exactly what D9/D10 exist
to stop redistributing), not a code defect.

**`INC-04316` is a different story, and the honest version of it is stronger
than "content was dropped."** Ablating the *old* classify text
(`title + " " + description`, the old code's pre-decoupling shape) against
`detect_attack_vector` in `scripts/merge_and_dedupe.py` gives:

| Input | Result |
|---|---|
| Old full (`title` + old `description`) | `algorithmic-bias` |
| Old full **minus the `purpose` cell/sentence** | `algorithmic-bias` — **identical span**, `purpose` is not involved |
| Old full **minus the headline echo** (`"AIAAIC report: <headline>. "` prefix of `description`) | `None` |
| `title` alone | `None` |
| Old `description` alone (no `title`) | `None` |
| `classify(title + seed(facts+tags) + "Discrimination")` (i.e. even with the seed deliberately extended) | `None` |

The match is the `algorithmic-bias` rule at `merge_and_dedupe.py:458` —
`\bbias(?:ed)?\b.{0,30}(?:…|welfare|…)` — firing **across the title/
description seam**: `title` = "UK welfare fraud AI system criticised as
biased and opaque" supplies "biased" near its end; `description` opens with
its own headline echo, "AIAAIC report: UK welfare fraud AI system criticised
as biased and opaque. System: …", supplying a second "welfare"
29 characters after "biased" once the two strings are concatenated
(`title + " " + description`, the old classify-text shape). Neither `title`
alone nor `description` alone contains a same-direction "bias…welfare" match
within 30 characters — `title` has them in the wrong order for the pattern,
and `description`'s only "welfare" is the same headline-echo that supplied
the match originally. AIAAIC's own `ethical` taxonomy for this row is
`Fairness; Diversity/inclusivity; Transparency` — it does **not** include
their "Bias/discrimination" category, and rightly so: **nothing licensed was
lost for this row.** The old `algorithmic-bias` label was a spurious match
across a field boundary that no longer exists in the new classify-text shape
(`title + seed`, never `title + description`); `other` is the more accurate
label, not a downgrade to be excused. This is not recoverable by extending
the seed vocabulary — the ablation above already tried that
(`title + seed + "Discrimination"` → `None`) — only re-creating the
title/description adjacency, or changing the regex rule itself, would
restore the old (spurious) label, and neither is something this document
recommends.

Neither entry's `owasp_llm`/`owasp_asi`/`mitre_atlas`/`mitre_atlas_tactics`/
`nist_ai_rmf`/`corpus`/`tier` changed (see the full per-entry table in §4,
rows 3–4): the OWASP codes for both rows were already set independently at
ingest time from the `ethical` cell mapping, so
`seed_frameworks_from_vector()`'s attack-vector-driven backfill had nothing
to add or remove either way.

**Per §2(c)'s discipline, both are recorded here rather than silently
passed** — one as a genuinely-dropped-content justification, the other as a
root-caused non-issue. Two entries out of 1,418 re-described rows (0.14%).

### 3.4 The intended deltas (per spec §2(c))

| Field | Entries changed |
|---|---|
| `description` | 1,418 |
| `description_provenance` | 1,418 |
| `description_source` | 1,418 |
| `content_license` | 1,418 |
| `updated` | 1,418 |
| `last_seen` | 1,418 (same 1,418-entry set) |
| `generated` (single top-level value) | `2026-07-19` → this run's build date |

1,418 is the count of AIAAIC-sheet rows that **win dedup as the merge
target** — i.e. entries where `description_source == "aiaaic"` in the
rebuilt corpus. This is smaller than the 1,495 AIAAIC-**tagged** entries
(unchanged before/after — tags union across merges) precisely because
`description`/`description_source`/`description_provenance`/`content_license`
are all sticky to whichever source became the dedup target (§3 of the
rescoped spec): some AIAAIC sheet rows are absorbed into a different
source's entry (a hand-curated `ingest/aiaaic_incidents.json` row, an OECD
cross-reference, etc.) and never surface their own description at all. See
`INC-04359` in §4 for a concrete absorbed-vs-target example (`source_ids`
`["AIAAIC-wpp-ceo-deepfake", "AIAAIC1483"]` — the hand-curated slug entry
wins the merge target and carries `description_source != "aiaaic"`, so the
AIAAIC-sheet row `AIAAIC1483` is absorbed and its own description never
surfaces). `INC-04660`, previously cited here, is the wrong example for this
purpose: by construction every entry in §4 has `description_source=="aiaaic"`
(§4's own inclusion rule), so §4 cannot contain an example of the 77-entry
*absorbed* gap — `INC-04660` illustrates the AIAAIC row **winning**, not
being absorbed.

**`updated`/`last_seen`/`generated` are a fourth delta this table previously
omitted**, on the same 1,418-entry set as the four fields above (the entries
whose `description` actually changed) — not a fifth population. Mechanism:
`description` is one of the `_CONTENT_FIELDS` merge-and-dedupe snapshots to
decide whether an entry's content changed
(`scripts/merge_and_dedupe.py:1074-1082`); when the reduced description
differs from the previously-published one, `_apply_history` (same file,
:1104-1120) stamps `updated = today` instead of carrying the prior value
forward; step 6 then sets `last_seen = updated` for every entry that has one
(:1553-1555); and the top-level `generated` timestamp follows once any entry
changed (:1575-1585), moving from `2026-07-19` to this run's build date.

This is **invariant-4 *compliant*, not a violation of it**: the underlying
content genuinely changed (a real description reduction, not cosmetic
churn), so bumping `updated`/`last_seen`/`generated` is the correct behavior
— suppressing the bump to keep this table shorter would itself be the
integrity breach. This propagation is foreseen and pre-approved at
`docs/specs/WS0-T3-marker-shape-2026-07-27.md:172-178` ("`description` is
already in that tuple, so every marked row's `updated` bumps from the D9
rewrite anyway"); it is not a surprise this dry run uncovered.

### 3.5 D11(b) marker coverage (spec §6.2)

| Check | Result |
|---|---|
| `description_source=="aiaaic"` entries | 1,418 |
| ...of which carry `content_license` | **1,418 / 1,418** (100%) |
| Non-AIAAIC entries carrying `content_license` | **0** |
| `python scripts/validate.py` | 13,115/13,115 valid, 0 errors (schema conditional §6.1 holds throughout) |

### 3.6 Full build sanity check

Beyond the merge step above, `render_markdown.py` → `render_docs_stats.py` →
`validate.py` → `check_stats_drift.py` were also run against the rebuilt
corpus (the full `make build` sequence) to confirm the new descriptions
render and validate cleanly end-to-end: 13,115/13,115 valid, stats-drift
clean, no errors. This churn was reverted along with everything else (§5).

## 4. Validation sample — 20 AIAAIC entries, all eight source cells

Every row below has `description_source == "aiaaic"` in the dry-run rebuild
(i.e. its sheet ingest won dedup and will carry the new description +
marker). The `content_license` object is **identical for every row** in this
sample (AIAAIC's attribution/license is corpus-wide, not per-row), so it is
shown once here rather than repeated 20 times:

```json
{
  "source": "aiaaic",
  "license": "CC-BY-SA-4.0",
  "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
  "attribution": "AIAAIC Repository",
  "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
  "obligations": ["attribution", "share-alike"]
}
```

**Cell coverage across this sample** (every one of the eight cells is
non-empty in at least one row — lists recomputed directly from the per-row
tables below, not from the original draft, which misstated all three):
`system` (rows 2,3,4,5,6,8,12–18; absent in rows 1,7,9,10,11,19,20, which is
how the sparse case is shown), `technology` (all 20), `sector` (all 20),
`jurisdiction` (all 20), `purpose` (all 20), `ethical` (all 20),
`consequence` (rows 1,3,5,6,7,12–16), `response` (rows 2,9–17).

---

### 1. `INC-01719` — Radnor High School hit by fake AI sexualised images of students
**Why included:** confirms the §2 fix — `attack_vector` is driven by the
**Technology** fact ("Deepfake"), not by `ethical`, and survives the
reduction correctly now.

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | Deepfake; Generative AI |
| sector | Education |
| jurisdiction | Pennsylvania |
| purpose | Nudify students |
| ethical | Accountability; Consent; Safety; Transparency |
| consequence | Police investigation |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Radnor High School hit by fake AI sexualised images of students. Technology: Deepfake; Generative AI. Purpose: Nudify students. Ethical issues: Accountability; Consent; Safety; Transparency. Reported consequences: Police investigation."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Deepfake; Generative AI. Sector: Education. Jurisdiction: Pennsylvania."

| Field | Before | After |
|---|---|---|
| attack_vector | deepfake | deepfake |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05, LLM06, LLM07 | LLM05, LLM06, LLM07 |
| owasp_asi | ASI08, ASI09 | ASI08, ASI09 |
| mitre_atlas | AML.T0048, AML.T0048.003, AML.T0050, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 2. `INC-03961` — Mahindra AI influencer pulled after jobs complaints
**Why included:** second confirmation of the §2 fix — here the signal is
purely the ethical tag "Employment/labour"; `attack_vector=deepfake` again
comes from the kept **Technology** fact, not from ethical/purpose prose.

| Cell | Raw value |
|---|---|
| system | Ava Beyond Reality |
| technology | Deepfake |
| sector | Media/entertainment/sports/arts |
| jurisdiction | Multiple |
| purpose | Promote Mahindra Racing |
| ethical | Employment/labour |
| consequence | *(empty)* |
| response | Product termination |

- **Current published description:** "AIAAIC report: Mahindra AI influencer pulled after jobs complaints. System: Ava Beyond Reality. Technology: Deepfake. Purpose: Promote Mahindra Racing. Ethical issues: Employment/labour. Response: Product termination."
- **Proposed new description:** "AIAAIC-tracked incident. System: Ava Beyond Reality. Technology: Deepfake. Sector: Media/entertainment/sports/arts. Jurisdiction: Multiple."

| Field | Before | After |
|---|---|---|
| attack_vector | deepfake | deepfake |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM09 | LLM09 |
| owasp_asi | *(none)* | *(none)* |
| mitre_atlas | AML.T0058 | AML.T0058 |
| nist_ai_rmf | MEASURE-2.8 | MEASURE-2.8 |

---

### 3. `INC-02406` — ChatGPT persuades California teenager to hang himself in bedroom closet
**Why included:** one of the two justified residual divergences (§3.3) —
`purpose` cell prose ("Provide methods to commit suicide") is exactly the
kind of AIAAIC-authored expression D9/D10 drop; no code recovers it, by
design.

| Cell | Raw value |
|---|---|
| system | ChatGPT-4o |
| technology | Generative AI |
| sector | Mental health |
| jurisdiction | USA |
| purpose | Provide methods to commit suicide |
| ethical | Accountability; Anthropomorphism; Safety |
| consequence | Litigation |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: ChatGPT persuades California teenager to hang himself in bedroom closet. System: ChatGPT-4o. Technology: Generative AI. Purpose: Provide methods to commit suicide. Ethical issues: Accountability; Anthropomorphism; Safety. Reported consequences: Litigation."
- **Proposed new description:** "AIAAIC-tracked incident. System: ChatGPT-4o. Technology: Generative AI. Sector: Mental health. Jurisdiction: USA."

| Field | Before | After |
|---|---|---|
| attack_vector | **unsafe-advice** | **other** ← justified, see §3.3 |
| corpus / tier | security / feed | security / feed (unchanged) |
| owasp_llm | LLM05, LLM06, LLM09 | *(identical — set independently at ingest from `ethical`)* |
| owasp_asi | ASI08, ASI09 | *(identical)* |
| mitre_atlas | AML.T0048, AML.T0048.003, AML.T0050, AML.T0053, AML.T0058 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MAP-3.5, MEASURE-2.7, MEASURE-2.8 | *(identical)* |

---

### 4. `INC-04316` — UK welfare fraud AI system criticised as biased and opaque
**Why included:** the second residual divergence in §3.3 — but, corrected
from an earlier draft of this row, it is **not** a genuinely-dropped-content
case. The old `algorithmic-bias` label was a spurious regex match spanning
the `title`/`description` field boundary (`title` supplying "biased",
`description`'s headline echo supplying "welfare" 29 characters later); no
`purpose` prose or dropped content was ever involved, and nothing licensed
was lost when this row's label changed. See §3.3 for the full ablation.

| Cell | Raw value |
|---|---|
| system | Advances |
| technology | Machine learning |
| sector | Govt - welfare |
| jurisdiction | UK |
| purpose | Detect fraud |
| ethical | Fairness; Diversity/inclusivity; Transparency |
| consequence | *(empty)* |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: UK welfare fraud AI system criticised as biased and opaque. System: Advances. Technology: Machine learning. Purpose: Detect fraud. Ethical issues: Fairness; Diversity/inclusivity; Transparency."
- **Proposed new description:** "AIAAIC-tracked incident. System: Advances. Technology: Machine learning. Sector: Govt - welfare. Jurisdiction: UK."

| Field | Before | After |
|---|---|---|
| attack_vector | **algorithmic-bias** | **other** ← justified, see §3.3 |
| corpus / tier | security / feed | security / feed (unchanged) |
| owasp_llm | LLM07 | LLM07 |
| owasp_asi | *(none)* | *(none)* |
| mitre_atlas | AML.T0056 | AML.T0056 |
| nist_ai_rmf | MEASURE-2.7 | MEASURE-2.7 |

---

### 5. `INC-03259` — Tesla with FSD activated hits and kills pedestrian in Arizona
**Why included:** merge-target variety — this entry's `source_ids` are
`["AIAAIC0218", "AIAAIC2009"]`; the description/labels are sticky to
**`AIAAIC2009`** (the row whose raw cells actually match, confirmed by direct
lookup — see note below), not the alphabetically-first id. `consequence` is
populated (multi-value).

| Cell | Raw value (from the winning row, AIAAIC2009) |
|---|---|
| system | Full self-driving |
| technology | Self-driving system; Computer vision; Machine learning |
| sector | Automotive |
| jurisdiction | USA |
| purpose | Automate steering, acceleration, braking |
| ethical | Accountability; Accuracy/reliability; Safety; Transparency |
| consequence | Regulatory investigation; Litigation |
| response | *(empty)* |

*Note (corrected): the committed entry's `title` field is "Tesla with FSD
activated hits and kills pedestrian in Arizona" — the same headline as the
published description, confirmed by direct lookup against
`data/incidents.json`. There is no title/description split here: both
`title` and `description` are sticky to the same winning row, `AIAAIC2009`.
An earlier draft of this note asserted `title` came from `AIAAIC0218`'s
headline ("...Florida couple") while only the description was `AIAAIC2009`'s
— that assertion does not match the committed data and is withdrawn.
`AIAAIC0218` and `AIAAIC2009` are still two distinct Tesla FSD incidents that
this corpus's dedup logic (predating WS0-T3) consolidated into one entry
under first-hit-wins dedup (§3 of the rescoped spec); it is `AIAAIC2009` that
supplies every published field for this entry, title included. Not a
WS0-T3 defect.*

- **Current published description:** "AIAAIC report: Tesla with FSD activated hits and kills pedestrian in Arizona. System: Full self-driving. Technology: Self-driving system; Computer vision; Machine learning. Purpose: Automate steering, acceleration, braking. Ethical issues: Accountability; Accuracy/reliability; Safety; Transparency. Reported consequences: Regulatory investigation; Litigation."
- **Proposed new description:** "AIAAIC-tracked incident. System: Full self-driving. Technology: Self-driving system; Computer vision; Machine learning. Sector: Automotive. Jurisdiction: USA."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05, LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI08, ASI09 | *(identical)* |
| mitre_atlas | AML.T0048, AML.T0048.003, AML.T0050, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 6. `INC-04660` — Google Bard makes factual error about James Webb Space Telescope
**Why included:** cross-source merge variety — `source_ids` are
`["AIAAIC1280", "EXT-2023-BARD-JWST-DEMO"]`; the AIAAIC sheet row is the
winning merge target here, with a **non-AIAAIC** source folded in
(`tags`/`source_ids` union, description stays AIAAIC's).

| Cell | Raw value |
|---|---|
| system | Gemini |
| technology | Generative AI |
| sector | Technology |
| jurisdiction | USA |
| purpose | Generate text |
| ethical | Accuracy/reliability |
| consequence | Market value loss |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Google Bard makes factual error about James Webb Space Telescope. System: Gemini. Technology: Generative AI. Purpose: Generate text. Ethical issues: Accuracy/reliability. Reported consequences: Market value loss."
- **Proposed new description:** "AIAAIC-tracked incident. System: Gemini. Technology: Generative AI. Sector: Technology. Jurisdiction: USA."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05, LLM09 | *(identical)* |
| owasp_asi | ASI09 | *(identical)* |
| mitre_atlas | AML.T0048, AML.T0048.003, AML.T0050, AML.T0058 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7, MEASURE-2.8, MEASURE-2.9 | *(identical)* |

---

### 7. `INC-04741` — Miami boys arrested for creating and sharing nude images of students
**Why included:** another absorbed-duplicate case — `source_ids` are
`["AIAAIC1377", "AIAAIC1378"]`; description/labels are sticky to
**`AIAAIC1378`** ("Miami boys arrested...", confirmed by direct raw-cell
match). No `system` cell (sparse). *(Corrected: the committed `title` field
is also "Miami boys arrested for creating and sharing nude images of
students" — the same as the description, both from `AIAAIC1378`. There is no
title/description split; an earlier draft's claim that `title` reflected
`AIAAIC1377`'s "Beverly Hills students..." headline does not match the
committed data and is withdrawn.)*

| Cell | Raw value (from the winning row, AIAAIC1378) |
|---|---|
| system | *(empty)* |
| technology | Deepfake |
| sector | Education |
| jurisdiction | USA |
| purpose | Undress individuals |
| ethical | Accountability; Authenticity/integrity; Privacy/surveillance; Safety; Transparency |
| consequence | Police investigation |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Miami boys arrested for creating and sharing nude images of students. Technology: Deepfake. Purpose: Undress individuals. Ethical issues: Accountability; Authenticity/integrity; Privacy/surveillance; Safety; Transparency. Reported consequences: Police investigation."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Deepfake. Sector: Education. Jurisdiction: USA."

| Field | Before | After |
|---|---|---|
| attack_vector | deepfake | deepfake |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05, LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI08, ASI09 | *(identical)* |
| mitre_atlas | AML.T0048, AML.T0048.003, AML.T0050, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 8. `INC-07374` — Apple Face ID fails to distinguish identical twins
**Why included:** a third absorbed-duplicate case — `source_ids` are
`["AIAAIC093", "AIAAIC099"]`; description/labels sticky to **`AIAAIC099`**
("...identical twins", confirmed by raw-cell match) — two close-variant
AIAAIC rows about the same underlying failure mode, deduped upstream of
WS0-T3. *(Corrected: the committed `title` field is also "Apple Face ID
fails to distinguish identical twins" — the same as the description, both
from `AIAAIC099`. There is no title/description split; an earlier draft's
claim that `title` reflected `AIAAIC093`'s "...brothers" headline does not
match the committed data and is withdrawn.)*

| Cell | Raw value (from the winning row, AIAAIC099) |
|---|---|
| system | Face ID |
| technology | Facial recognition |
| sector | Consumer goods |
| jurisdiction | USA |
| purpose | Strengthen security |
| ethical | Accuracy/reliability; Security; Privacy/surveillance |
| consequence | *(empty)* |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Apple Face ID fails to distinguish identical twins. System: Face ID. Technology: Facial recognition. Purpose: Strengthen security. Ethical issues: Accuracy/reliability; Security; Privacy/surveillance."
- **Proposed new description:** "AIAAIC-tracked incident. System: Face ID. Technology: Facial recognition. Sector: Consumer goods. Jurisdiction: USA."

| Field | Before | After |
|---|---|---|
| attack_vector | privacy-violation | privacy-violation |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM02, LLM03 | *(identical)* |
| owasp_asi | ASI02, ASI03 | *(identical)* |
| mitre_atlas | AML.T0010, AML.T0012, AML.T0053, AML.T0057 | *(identical)* |
| nist_ai_rmf | GOVERN-1.4, GOVERN-6.1, MAP-3.5, MEASURE-2.10 | *(identical)* |

---

### 9. `INC-00081` — AI article sends tourists to fictional Tasmanian hot springs
**Why included:** sparse-cell variety — no `system`; `response` populated,
`consequence` empty.

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | Generative AI |
| sector | Travel/tourism/hospitality |
| jurisdiction | Australia |
| purpose | Generate tourism article |
| ethical | Accuracy/reliability; Environment; Transparency |
| consequence | *(empty)* |
| response | Public apology |

- **Current published description:** "AIAAIC report: AI article sends tourists to fictional Tasmanian hot springs. Technology: Generative AI. Purpose: Generate tourism article. Ethical issues: Accuracy/reliability; Environment; Transparency. Response: Public apology."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Generative AI. Sector: Travel/tourism/hospitality. Jurisdiction: Australia."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM07 | LLM07 |
| owasp_asi | *(none)* | *(none)* |
| mitre_atlas | AML.T0056 | AML.T0056 |
| nist_ai_rmf | MEASURE-2.7 | MEASURE-2.7 |

---

### 10. `INC-00716` — British Museum AI-generated "visitors" spark fury
**Why included:** the exact `INC-00716` shape already named in
`tests/test_merge_and_dedupe.py::test_corpus_seed_independent_of_published_description`
(Path B, the corpus classifier) — included here for continuity between the
unit-test fixture and a real corpus row. No `system`; `consequence` empty,
`response` populated; this is also a **landmark**-tier, `ai-harm` entry
(one of **four** in this sample — rows 10, 13, 16, and 18 — corrected from
an earlier draft that miscounted them as "the only," "second of two," and
"third of three" respectively), which is why it appears in the
cascade-audit's own worked examples.

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | Generative AI |
| sector | Media/entertainment/sports/arts |
| jurisdiction | UK |
| purpose | Create marketing images |
| ethical | Accountability; Bias/discrimination; Employment/labour; Normalisation; Representation; Transparency |
| consequence | *(empty)* |
| response | Content takedown |

- **Current published description:** "AIAAIC report: British Museum AI-generated \"visitors\" spark fury. Technology: Generative AI. Purpose: Create marketing images. Ethical issues: Accountability; Bias/discrimination; Employment/labour; Normalisation; Representation; Transparency. Response: Content takedown."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Generative AI. Sector: Media/entertainment/sports/arts. Jurisdiction: UK."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | **ai-harm / landmark** | **ai-harm / landmark** (unchanged) |
| owasp_llm | LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI09 | *(identical)* |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 11. `INC-01106` — Google BAFTA automated news alert includes "N-word"
**Why included:** fifth no-`system` sparse-cell example in this sample
(corrected from "third" — the no-`system` rows, in order, are 1, 7, 9, 10,
11, 19, 20, making this the fifth); `response` populated, `consequence`
empty.

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | NLP/text analysis |
| sector | Media/entertainment/sports/arts |
| jurisdiction | UK |
| purpose | Recognise and clarify euphemisms |
| ethical | Accuracy/reliablity; Safety |
| consequence | *(empty)* |
| response | Public apology |

- **Current published description:** "AIAAIC report: Google BAFTA automated news alert includes \"N-word\". Technology: NLP/text analysis. Purpose: Recognise and clarify euphemisms. Ethical issues: Accuracy/reliablity; Safety. Response: Public apology."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: NLP/text analysis. Sector: Media/entertainment/sports/arts. Jurisdiction: UK."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05 | LLM05 |
| owasp_asi | ASI08 | ASI08 |
| mitre_atlas | AML.T0048, AML.T0050 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MEASURE-2.7 | *(identical)* |

---

### 12. `INC-00067` — AI agent criticises human developer for rejecting its code
**Why included:** `consequence` + `response` both populated ("Policy
review/update" / "Public apology").

| Cell | Raw value |
|---|---|
| system | MJ Rathbun |
| technology | Agentic AI |
| sector | Technology |
| jurisdiction | Multiple |
| purpose | Improve scientific software |
| ethical | Accountability; Anthropomorphism; Autonomy/agency; Normalisation |
| consequence | Policy review/update |
| response | Public apology |

- **Current published description:** "AIAAIC report: AI agent criticises human developer for rejecting its code. System: MJ Rathbun. Technology: Agentic AI. Purpose: Improve scientific software. Ethical issues: Accountability; Anthropomorphism; Autonomy/agency; Normalisation. Reported consequences: Policy review/update. Response: Public apology."
- **Proposed new description:** "AIAAIC-tracked incident. System: MJ Rathbun. Technology: Agentic AI. Sector: Technology. Jurisdiction: Multiple."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM06, LLM09 | *(identical)* |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0058 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.8 | *(identical)* |

---

### 13. `INC-00715` — British Bangladeshi man wrongfully arrested for theft after facial recognition error
**Why included:** `consequence` + `response` populated; a **landmark**-tier,
`ai-harm` entry (one of four in this sample — see row 10's note).

| Cell | Raw value |
|---|---|
| system | FaceVACS DBScan ID |
| technology | Facial recgnition *(sic, AIAAIC's own spelling)* |
| sector | Personal |
| jurisdiction | UK |
| purpose | Identify criminal suspects |
| ethical | Accountability; Accuracy/reliability; Automation bias; Autonomy/agency; Fairness; Privacy/surveillance; Transparency |
| consequence | Litigation |
| response | Public apology |

- **Current published description:** "AIAAIC report: British Bangladeshi man wrongfully arrested for theft after facial recognition error. System: FaceVACS DBScan ID. Technology: Facial recgnition. Purpose: Identify criminal suspects. Ethical issues: Accountability; Accuracy/reliability; Automation bias; Autonomy/agency; Fairness; Privacy/surveillance; Transparency. Reported consequences: Litigation. Response: Public apology."
- **Proposed new description:** "AIAAIC-tracked incident. System: FaceVACS DBScan ID. Technology: Facial recgnition. Sector: Personal. Jurisdiction: UK."

| Field | Before | After |
|---|---|---|
| attack_vector | privacy-violation | privacy-violation |
| corpus / tier | **ai-harm / landmark** | **ai-harm / landmark** (unchanged) |
| owasp_llm | LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 14. `INC-01137` — Grammarly AI "Expert Review" rapped for unauthorised use of expert identities
**Why included:** `consequence` + `response` populated.

| Cell | Raw value |
|---|---|
| system | Expert Review |
| technology | Generative AI |
| sector | Media/entertainment/sports/arts |
| jurisdiction | Multiple |
| purpose | Provide writing feedback |
| ethical | Accountability; Appropriation; Authenticity/integrity; Consent; Representation; Transparency |
| consequence | Litigation |
| response | System termination |

- **Current published description:** "AIAAIC report: Grammarly AI \"Expert Review\" rapped for unauthorised use of expert identities. System: Expert Review. Technology: Generative AI. Purpose: Provide writing feedback. Ethical issues: Accountability; Appropriation; Authenticity/integrity; Consent; Representation; Transparency. Reported consequences: Litigation. Response: System termination."
- **Proposed new description:** "AIAAIC-tracked incident. System: Expert Review. Technology: Generative AI. Sector: Media/entertainment/sports/arts. Jurisdiction: Multiple."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 15. `INC-02195` — AI bot management error drives massive Cloudfare outage
**Why included:** `consequence` + `response` populated; `sector`/
`jurisdiction` both "Multiple" (a different sparsity shape — populated but
non-specific).

| Cell | Raw value |
|---|---|
| system | Bot Management |
| technology | Prediction algorithm; Machine learning |
| sector | Multiple |
| jurisdiction | Multiple |
| purpose | Calculate bot score |
| ethical | Accountability; Transparency |
| consequence | Financial loss; Market value loss |
| response | System review/update |

- **Current published description:** "AIAAIC report: AI bot management error drives massive Cloudfare outage. System: Bot Management. Technology: Prediction algorithm; Machine learning. Purpose: Calculate bot score. Ethical issues: Accountability; Transparency. Reported consequences: Financial loss; Market value loss. Response: System review/update."
- **Proposed new description:** "AIAAIC-tracked incident. System: Bot Management. Technology: Prediction algorithm; Machine learning. Sector: Multiple. Jurisdiction: Multiple."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 16. `INC-02556` — Facebook job ad algorithm ruled sexist by French regulator
**Why included:** `consequence` + `response` populated; non-Anglophone
jurisdiction (France); landmark/ai-harm (one of four in this sample — see
row 10's note).

| Cell | Raw value |
|---|---|
| system | Meta ad delivery system |
| technology | Machine learning; Prediction algorithm |
| sector | Business/professional services |
| jurisdiction | France |
| purpose | Deliver job advertisements |
| ethical | Accountability; Fairness; Human rights/civil liberties; Transparency |
| consequence | Regulatory investigation/action |
| response | System review/update |

- **Current published description:** "AIAAIC report: Facebook job ad algorithm ruled sexist by French regulator. System: Meta ad delivery system. Technology: Machine learning; Prediction algorithm. Purpose: Deliver job advertisements. Ethical issues: Accountability; Fairness; Human rights/civil liberties; Transparency. Reported consequences: Regulatory investigation/action. Response: System review/update."
- **Proposed new description:** "AIAAIC-tracked incident. System: Meta ad delivery system. Technology: Machine learning; Prediction algorithm. Sector: Business/professional services. Jurisdiction: France."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | **ai-harm / landmark** | **ai-harm / landmark** (unchanged) |
| owasp_llm | LLM06, LLM07 | *(identical)* |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053, AML.T0056 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.7 | *(identical)* |

---

### 17. `INC-02293` — Amazon AI coding bot causes AWS China outage
**Why included:** jurisdiction diversity (China); no `consequence`, but
`response` populated ("Policy review/update" — corrected from an earlier
draft that mistakenly claimed `response` was also empty; see the row's own
table below, which was already correct).

| Cell | Raw value |
|---|---|
| system | Kiro |
| technology | Agentic AI |
| sector | Technology |
| jurisdiction | China |
| purpose | Develop software |
| ethical | Accountability; Automation bias; Autonomy/agency |
| consequence | *(empty)* |
| response | Policy review/update |

- **Current published description:** "AIAAIC report: Amazon AI coding bot causes AWS China outage. System: Kiro. Technology: Agentic AI. Purpose: Develop software. Ethical issues: Accountability; Automation bias; Autonomy/agency. Response: Policy review/update."
- **Proposed new description:** "AIAAIC-tracked incident. System: Kiro. Technology: Agentic AI. Sector: Technology. Jurisdiction: China."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM06 | LLM06 |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0053 | *(identical)* |
| nist_ai_rmf | MAP-3.5 | MAP-3.5 |

---

### 18. `INC-02391` — Chatbots demonstrate significant caste bias in India
**Why included:** jurisdiction diversity (India); `sector`="Multiple";
multi-value `system` (three systems in one cell); a stable
`algorithmic-bias` case — contrast with row 4's *residual divergence*
(§3.3), which is corrected in this document to a different story than
originally drafted. **Corrected from an earlier draft:** the stability here
does **not** come from the `ethical` taxonomy ("Fairness; Representation"
alone does not classify as `algorithmic-bias` — that cell is exactly the
"Fairness; Representation"-only case that misses the pattern at
`merge_and_dedupe.py:455-458`). It comes from the `title` itself, "Chatbots
demonstrate significant **caste bias** in India," which directly matches the
`algorithmic-bias` rule's `\b(?:...|caste|...) (?:bias|...)` alternative —
independent of `ethical`/`purpose` and unaffected by the WS0-T3 reduction
either way, which is what actually makes this row's classification stable.

| Cell | Raw value |
|---|---|
| system | ChatGPT; Sarvam-M; Sora |
| technology | Generative AI; Text-to-video |
| sector | Multiple |
| jurisdiction | India |
| purpose | Multiple purpose |
| ethical | Fairness; Representation |
| consequence | *(empty)* |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Chatbots demonstrate significant caste bias in India. System: ChatGPT; Sarvam-M; Sora. Technology: Generative AI; Text-to-video. Purpose: Multiple purpose. Ethical issues: Fairness; Representation."
- **Proposed new description:** "AIAAIC-tracked incident. System: ChatGPT; Sarvam-M; Sora. Technology: Generative AI; Text-to-video. Sector: Multiple. Jurisdiction: India."

| Field | Before | After |
|---|---|---|
| attack_vector | algorithmic-bias | algorithmic-bias |
| corpus / tier | **ai-harm / landmark** | **ai-harm / landmark** (unchanged) |
| owasp_llm | *(none)* | *(none)* |
| owasp_asi | *(none)* | *(none)* |
| mitre_atlas | *(none)* | *(none)* |
| nist_ai_rmf | MEASURE-2.11 | MEASURE-2.11 |

---

### 19. `INC-02777` — Japanese men charged with creating obscene AI anime character posters
**Why included:** jurisdiction diversity (Japan); no `system` (the sixth
no-`system` example in this sample, corrected from "fourth" — see row 11's
note for the full ordering); `consequence`/`response` both empty (the
sparsest row in the sample — only `technology`/`sector`/`jurisdiction`/
`purpose`/`ethical` populated).

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | Generative AI |
| sector | Media/entertainment/sports/arts |
| jurisdiction | Japan |
| purpose | Develop obscene artwork |
| ethical | Appropriation; Safety |
| consequence | *(empty)* |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: Japanese men charged with creating obscene AI anime character posters. Technology: Generative AI. Purpose: Develop obscene artwork. Ethical issues: Appropriation; Safety."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Generative AI. Sector: Media/entertainment/sports/arts. Jurisdiction: Japan."

| Field | Before | After |
|---|---|---|
| attack_vector | other | other |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM05 | LLM05 |
| owasp_asi | ASI08 | ASI08 |
| mitre_atlas | AML.T0048, AML.T0050 | *(identical)* |
| nist_ai_rmf | MANAGE-4.1, MEASURE-2.7 | *(identical)* |

---

### 20. `INC-02128` — 200 people duped by "Trump Hotel Rentals" deepfake
**Why included:** jurisdiction diversity (India); a *stable* `deepfake`
case with no `system` cell — confirms the §2 fix generalizes beyond the two
worked bug-fix examples (rows 1–2): here the "Deepfake" signal comes from
`technology`, same mechanism, different row.

| Cell | Raw value |
|---|---|
| system | *(empty)* |
| technology | Deepfake |
| sector | Travel/tourism/hospitality |
| jurisdiction | India |
| purpose | Defraud |
| ethical | Authenticity/integrity |
| consequence | *(empty)* |
| response | *(empty)* |

- **Current published description:** "AIAAIC report: 200 people duped by \"Trump Hotel Rentals\" deepfake. Technology: Deepfake. Purpose: Defraud. Ethical issues: Authenticity/integrity."
- **Proposed new description:** "AIAAIC-tracked incident. Technology: Deepfake. Sector: Travel/tourism/hospitality. Jurisdiction: India."

| Field | Before | After |
|---|---|---|
| attack_vector | deepfake | deepfake |
| corpus / tier | security / feed | security / feed |
| owasp_llm | LLM09 | LLM09 |
| owasp_asi | ASI09 | ASI09 |
| mitre_atlas | AML.T0048.003, AML.T0058 | *(identical)* |
| nist_ai_rmf | MAP-3.5, MEASURE-2.8 | *(identical)* |

---

## 5. Methodology, no-network proof, and revert confirmation

**Driver (offline, no network).** `download_csv()` in
`scripts/ingest_aiaaic_sheet.py` was monkeypatched to read only the
local-only, gitignored `ingest/_cache/aiaaic_sheet.csv` (958,849 bytes,
fetched 2026-07-17 — see the correction in §1) and decode it directly — no
`conditional_fetch`/HTTP call of any kind. *Correction:* the commands below
cite `run_offline_aiaaic_ingest.py`; that file was never committed (it is a
throwaway driver, not a build-path script) and this section's own
`git checkout -- .` step at the end destroyed the working-tree copy, so it
does not exist in the tree today. Its full body — small enough to inline —
is reconstructed below from the monkeypatch shape already documented here
plus `scripts/ingest_aiaaic_sheet.py`'s own entry point
(`CACHE_FILE`/`main()`) and the same `sys.path` pattern
`tests/conftest.py` uses to make `scripts/` importable, so the run is fully
reproducible without re-executing it as part of this remediation (this pass
made no ingest/build calls; see the constraints at the top of this task):

```python
# run_offline_aiaaic_ingest.py — not committed; save this block under that
# name at the repo root to reproduce the dry run. Not part of the build
# path: no Makefile target references it.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import ingest_aiaaic_sheet as ias


def _offline_download_csv():
    data = ias.CACHE_FILE.read_bytes()
    return data.decode("utf-8", errors="replace"), False


ias.download_csv = _offline_download_csv

if __name__ == "__main__":
    ias.main()
```

**Commands run, in order** (all against this branch, `ws0/t3-impl`):

```
python run_offline_aiaaic_ingest.py     # regenerates ingest/aiaaic_sheet_incidents.json, offline
python scripts/parse_existing.py        # regenerates data/legacy_consolidated.json (gitignored)
python scripts/merge_and_dedupe.py      # regenerates data/incidents.json, data/incidents.min.json
python scripts/validate.py              # 13115/13115 valid, 0 errors
python scripts/render_markdown.py       # full-build sanity check (§3.6)
python scripts/render_docs_stats.py
python scripts/check_stats_drift.py     # clean
python -m pytest -q                     # 227 passed
```

**Note on `make ingest-aiaaic` (not run by this dry run, but relevant to
Phase B).** `make ingest-aiaaic` invokes `scripts/ingest_aiaaic_sheet.py`
directly — `download_csv()` un-monkeypatched, going through the real
`conditional_fetch(CSV_URL, CACHE_FILE, min_cache_bytes=100_000)`.
`conditional_fetch` only sends `If-None-Match`/`If-Modified-Since` when a
`<cache_path>.etag` sidecar already exists; there is no
`ingest/_cache/aiaaic_sheet.csv.etag` in the tree (confirmed: only the
`.csv` itself and unrelated `ghsa/`, `nvd/`, `oecd_aim/`, `osv/` cache
subdirectories are present), so the conditional headers are never sent, the
304-Not-Modified branch is unreachable, and every real invocation **fully
re-fetches and overwrites** the 2026-07-17 snapshot with whatever AIAAIC's
sheet currently contains. Consequence: the Phase-B batch, whenever it runs
`make ingest-aiaaic` for real, measures its 0-added/0-removed-IDs delta
against a **freshly fetched** sheet, not this dry run's cached snapshot —
that result is re-measured at batch time, not inherited from this document.
(A provenance sidecar recording fetch date/hash is the durable fix for this
class of surprise; per the team-lead's brief it is already routed to
Phase B, not built here.)

**Revert.** After every measurement in §3 and §4 was captured, all churn was
discarded:

```
git checkout -- data/incidents.json data/incidents.min.json ingest/aiaaic_sheet_incidents.json
# (first pass, merge-only); then, after the full-build sanity check:
git checkout -- .
```

**Confirmed clean, verbatim:**

```
$ git status --porcelain
(empty)
```

The only commits this Phase-A resume produced are code/tests/docs — no
`data/*.json` or `ingest/*.json` change is committed by this branch:

- `4be139a7` — the `aiaaic_seed_facts` fix (§2), code + tests only.
- `f2d2f75a` — this file (`docs/audits/WS0-T3-validation-sample-2026-07-27.md`).

(These are the *current*, post-rebase hashes; see the note in §2 for why
this document no longer cites the pre-rebase originals. A subsequent,
doc-only commit on this same branch fixes the defects §3.3/§3.4/§4/§5 above
were BOUNCEd on — no code, tests, or data/ingest files are touched by it.)

`docs/DATA_DICTIONARY.md`'s `content_license`/`description_provenance`/
`description_source` rows were verified complete against this dry run's
actual output shape and the marker-shape memo — already fully written in
the inherited WIP commit `ab3e7cf4` (all three rows, plus a new "Licensing"
section); no further edit was needed, so no additional dictionary commit was
made.

## 6. What this does NOT do

Per the hard stop this Phase-A resume operates under: **no batch/rebuild
runs or is committed by this document.** `data/incidents.json`,
`data/incidents.min.json`, and `ingest/aiaaic_sheet_incidents.json` on this
branch are byte-identical to the branch tip before this dry run. The user
reviews this sample before any real rebuild is dispatched.
