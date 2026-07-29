# E16 (D18) — content_license marker extension + verbatim-title retitle: full field-level delta

**Date:** 2026-07-29
**Author:** pipeline-engineer
**Authorizing decision:** PROGRESS.md D18 (2026-07-29) — E16 resolved: (a) extend the
`content_license` marker to all 95 AIAAIC-citing hand-curated rows, (b) replace the
13 verbatim-identical titles with project-authored ones.
**Branch:** `ws0/e16-marker-and-retitles`.
**Scope:** deliverables (a) and (b) only. The 47-row `>=0.8` per-row licensing
ruling is `docs/audits/E16-title-similarity-review-2026-07-29.md` (license-auditor,
committed separately at `b22aff59`, not touched by this doc).
**Code changed:** none. `scripts/merge_and_dedupe.py`'s existing propagation
mechanism (`content_license` sticky-by-omission, `_CONTENT_FIELDS` list) is used
as-is. Only `ingest/aiaaic_incidents.json` (hand-curated source data — editing it
is the curation path) and the generated `data/`/`docs/`/`INCIDENTS.md`/`src/`
build artifacts changed.

---

## 1. Mechanism choice for deliverable (a)

**Chosen: write `content_license` directly into the 95 hand-curated JSON records
in `ingest/aiaaic_incidents.json`** (option i), not derive it in the build path
(option ii).

Reasoning:
- The schema's own field description (`schema/incident.schema.json:94`, quoted
  in full in §5 below) says the marker is "**Set at ingest**... by whichever
  entry survives dedup as the merge target" — i.e. the schema's stated model is
  that this is an ingest-time fact about the record, not a build-time inference.
  Writing it into the hand-curated source file matches that model; synthesizing
  it later in `merge_and_dedupe.py` from a new AIAAIC-specific heuristic would
  not — and would duplicate, in new special-case code, exactly the fact this
  file's curator already knows when adding a row (it cites an
  `aiaaic.org/aiaaic-repository/` reference).
- **Durability.** `ingest/*.json` files are loaded generically by
  `merge_and_dedupe.py:1312` (`INGEST.glob("*.json")` -> `normalize_entry`) with
  **no per-file special-casing today**. Mechanism (ii) would require adding new
  AIAAIC-specific branching into `normalize_entry`, a function every other
  ingest source also flows through — a bad place to special-case one file. A
  future re-curation of `ingest/aiaaic_incidents.json` (adding/editing a row by
  hand, which this file's whole purpose is) sees the marker sitting in the
  record right next to `description`/`references`/etc. and is far more likely to
  carry it forward correctly than to reconstruct an implicit build-time rule.
- The mechanism used to *propagate* the field once present
  (`merge_and_dedupe.py:873-874` raw->entry copy, `:1693-1694` min.json
  conditional-add) is **completely unchanged** — it already handles
  `content_license` from any `ingest/*.json` source generically. No new code
  path was needed or written.
- I did **not** add `description_provenance`/`description_source` to these 95
  rows. D10 already established their descriptions are project-authored
  (`description_provenance` would be `original`, not `aiaaic`); setting
  `description_source: "aiaaic"` would misrepresent the description's actual
  provenance and is out of E16's scope. This is exactly what produces the
  schema tension in §5.

Marker shape (identical across all 95, matches `aiaaic_content_license()` in
`scripts/ingest_aiaaic_sheet.py:309` key-for-key):

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

Edit method: surgical, line-based insertion (one block after each record's
`"description"` line) — **not** a full `json.load`/`json.dump` reserialize,
which would have reformatted every pre-existing compact inline array
(`"owasp_llm": ["LLM09"]` etc.) in this hand-formatted file and produced ~3,800
lines of pure noise. Confirmed via `git diff --stat`: **1,045 insertions, 0
deletions** for this step (95 records x 11 added lines each) — every other byte
in the file is untouched.

## 2. Re-derivation for deliverable (b): 13-vs-12 reconcile

**Re-derived at execution time, not trusted from any stored figure**, against
`ingest/_cache/aiaaic_sheet.csv`:

| | |
|---|---|
| SHA-256 | `fa2390ec67669f9b4cb0ac766ec5ce2d4545d8b433d9369701a777fb06dbd2ac` |
| Size | 961,119 bytes |
| mtime | 2026-07-28 19:26 |

Method (per the foreman's brief, reproduced and independently re-run): join key
= last path segment of our `references[].url` <-> last path segment of an
`aiaaic.org/aiaaic-repository/` URL extracted from the sheet's `summary`
column (case-**insensitive** — see below); similarity = our `title` vs. the
sheet's `headline`, both lowercased with non-alphanumerics collapsed to a
single space and stripped, compared with `difflib.SequenceMatcher.ratio()`.

**Result: 92/95 joined, 3 unjoined; 13 EXACT / 47 >=0.8 / 19 in 0.6-0.8 / 13
<0.6.** This matches the foreman's figures exactly.

One join-methodology finding along the way: a **case-sensitive** slug join
(matching the foreman's stated method literally) gives **91/95 joined, 4
unjoined**, with `AIAAIC-canada-chatgpt-investigation` unjoined because our
reference URL slug is `...-ChatGPT-...` (mixed case, as hand-curated) while the
sheet's current URL for the same entry (AIAAIC1209) is
`...-chatgpt-...` (all-lowercase) — AIAAIC's own URL casing has evidently
normalized since this row was hand-curated. Matching case-insensitively (which
is what "last path segment" join should mean when the underlying resource is
the same) recovers this one row into the 0.6-0.8 band (ratio 0.694), bringing
the counts to 92/95 and 19 in that band — exactly the foreman's numbers. The
**13 EXACT / 47 >=0.8 / 13 <0.6 bands are identical either way** — this
methodology point affects only the always-out-of-my-scope middle band and the
unjoined count, not the retitle set.

The 3 genuinely unjoined rows (present under both methods, and independently
confirmed by a case-insensitive substring search across every URL in the
current sheet): `AIAAIC-miami-pinecrest` (no match at all — the slug does not
appear anywhere in the current sheet), `AIAAIC-c4-dataset` and
`AIAAIC-books3-dataset` (both renamed on AIAAIC's site to longer slugs —
`c4-dataset-is-trained-on-unsafe-copyright-protected-web-content` /
`google-c4-dataset`, and
`books3-dataset-shut-down-after-legal-notice-from-danish-anti-piracy-group` —
so the exact-slug join correctly fails rather than guessing which renamed
entry, if any, is the right counterpart).

**13-vs-12 reconcile (the board's open item, PROGRESS.md, commit `2055445f`):**
resolved precisely, on this artifact, without needing to assume a live-sheet
edit. `AIAAIC0462`'s headline cell in this exact cache is
`'Audio deepfake fraudulently impersonates CEO '` — **with a trailing space**;
our title has none. Under the specified normalization (lowercase, collapse
non-alphanumerics to a single space, **then strip**), the trailing space is
removed and the two strings become identical -> EXACT. Under a raw/strict
string comparison the trailing space makes them unequal -> not exact.
Separately, `AIAAIC-duke-multi-tracking` (AIAAIC1536) also raw-differs
(`facial-recognition` hyphen vs. the sheet's `facial recognition` space) but
would be treated as equal by a comparison that normalizes punctuation to spaces
without necessarily stripping trailing whitespace — consistent with the
re-gate naming *only* `AIAAIC0462` (not also AIAAIC1536) as its one
discrepancy. **Ruling: 13 is correct** on this artifact under the method
specified for this task (normalize-and-strip); the re-gate's 12 is fully
explained by a stricter/non-stripping comparison applied to the *same* cell,
not by an upstream edit between measurements. `AIAAIC0462` / `INC-04464` is
retitled below along with the other 12.

## 3. Retitles (13 rows)

Each new title is independently composed from the record's own (project-
authored, per D10) `description` field and general knowledge of the incident —
not a paraphrase of AIAAIC's headline. Post-retitle similarity to the AIAAIC
headline (same normalized measure) is reported for every row; all are well
below the 0.8 hazard threshold (highest is 0.493).

| `id` | AIAAIC id | `source_id` | Original title (preserved here) | New title | new-vs-AIAAIC ratio |
|---|---|---|---|---|---|
| INC-04464 | AIAAIC0462 | AIAAIC-audio-deepfake-ceo | Audio deepfake fraudulently impersonates CEO | Attacker impersonates company CEO with AI voice clone to authorize fraudulent transaction | 0.331 |
| INC-04602 | AIAAIC1422 | AIAAIC-bangladesh-news-anchor | Deepfake news anchor accuses US of Bangladesh election interference | Pro-government Bangladeshi channels air AI-generated anchors alleging US election meddling | 0.331 |
| INC-03714 | AIAAIC1486 | AIAAIC-philippines-marcos | Deepfake Philippines President urges military action against China | Fabricated Marcos Jr. audio clip calling for military response to China circulates online | 0.377 |
| INC-04258 | AIAAIC1164 | AIAAIC-taylor-swift-mandarin | Taylor Swift speaks in Mandarin deepfake | AI-dubbed clip gives Taylor Swift fluent Mandarin, circulates on Chinese platforms | 0.446 |
| INC-03535 | AIAAIC1447 | AIAAIC-aoc-deepfake-porn | Alexandria Ocasio-Cortez depicted as deepfake pornstar | Non-consensual AI-generated sexual images of Rep. Ocasio-Cortez spread online, spurring DEFIANCE Act | 0.461 |
| INC-04789 | AIAAIC1942 | AIAAIC-opendream-csam | OpenDream AI art generator accused of generating child sex images | OpenDream image tool found capable of producing sexualized depictions of minors despite policy | 0.201 |
| INC-03804 | AIAAIC1941 | AIAAIC-gennomis-csam | GenNomis AI art generator accused of producing explicit child images | Exposed GenNomis AWS bucket leaks roughly 95,000 images including apparent child abuse material | 0.368 |
| INC-03612 | AIAAIC1781 | AIAAIC-character-ai-suicide | Boy commits suicide after relationship with Character.AI chatbot | Teen's death by suicide follows months-long bond with a Character.AI companion persona | 0.493 |
| INC-05113 | AIAAIC1615 | AIAAIC-clearview-france | French privacy watchdog fines Clearview AI for violating privacy | CNIL orders Clearview AI to pay EUR 20 million and erase French biometric data | 0.338 |
| INC-07173 | AIAAIC1536 | AIAAIC-duke-multi-tracking | Duke University pulls facial-recognition dataset after privacy controversy | Duke withdraws DukeMTMC campus-surveillance dataset over non-consensual student footage | 0.335 |
| INC-04075 | AIAAIC1705 | AIAAIC-outabox-biometric | Outabox data breach exposes 1m biometric records | Breach at Australian venue-ID vendor Outabox leaks over a million patrons' biometric data | 0.368 |
| INC-04065 | AIAAIC1485 | AIAAIC-openai-deleted-datasets | OpenAI deleted training datasets believed to contain copyrighted books | Authors Guild v. OpenAI filing alleges destruction of book-training data before inspection | 0.415 |
| INC-04788 | AIAAIC1221 | AIAAIC-openai-stealing-pii | OpenAI, Microsoft sued for 'stealing' personal info to create ChatGPT | Plaintiffs accuse OpenAI and Microsoft of building ChatGPT from scraped personal data | 0.477 |

No schema field exists to record the original title as a structured
"conflict" (`conflicts` is unbuilt, WS3-T2) — per the brief, no such field was
invented. The table above **is** the preservation record for these 13
originals (`source_id`, AIAAIC id, original, new — all four, as required). I
think a schema-level `conflicts` record *is* warranted longer-term (this is
now the second E16-shaped case — an edited field whose prior value has
standing licensing/attribution relevance — and a committed-doc mapping doesn't
`git blame`/query as well as a structured field would), but that's a
schema-architect call under WS3-T2, not one I should make by inventing a field
here.

The `>=0.8` band (47 rows) is untouched — its disposition is
`docs/audits/E16-title-similarity-review-2026-07-29.md`'s per-row ruling, a
separate decision (D18 part not in this deliverable).

## 4. Build

Full rebuild run twice (parse_existing -> merge_and_dedupe -> render_markdown
-> render_docs_stats -> validate), matching `make build`'s target composition
(no `make` binary on this Windows box; ran the constituent commands directly —
same commands the Makefile invokes). No network or model call anywhere in
this path.

```
[total]  18736 input -> 13119 unique
13119/13119 entries valid; 0 with errors.
integrity: no duplicate CVE/source keys; all deprecations resolve.
[check-stats-drift] clean: 5 doc surfaces match data/stats.json, no unmarked hardcoded totals
227 passed in 1.91s
```

**Determinism.** Both runs produced byte-identical output:

| File | SHA-256 (both runs) |
|---|---|
| `data/incidents.json` | `a519963ee56e66d47cc304ca83f97ea01ef7ad2cc894fa7353a1e8c18bdab01e` |
| `data/incidents.min.json` | `13d4fe7fbf97d843c7345840e7c6a5d7d8ce6802d03c5a158f9d5f85464f31e3` |
| `data/stats.json` | `1230cfe89e968e792f734dbb2ebde93d743afca634d5f5c4e5555f6b24bbc40a` |
| `data/id_deprecations.json` | `975d94c7922b41b3dadf7a2be776e516f4571eac417487ba04d87b15f04c5027` (**byte-identical to the pre-change committed version** — 0 new deprecations, invariant 9 intact) |

Pre-change (`HEAD`) blob hashes, for reference:

| File | SHA-256 (HEAD, pre-change) |
|---|---|
| `data/incidents.json` | `b5fa3ae1257c6ac7db4816925a98dda72179d77531843302108e20298de028bb` |
| `data/incidents.min.json` | `e4c126627aa56055efdaba26f281fbac51c60c7f939ed7bf0fe3cfec347e5047` |
| `data/stats.json` | `fdac9162dd4265d5f3cda78f2b525b4ab76152abe68c439aa087a4e0d748a96d` |
| `ingest/aiaaic_incidents.json` | `fd8bf2652441f5c7e1b65cca4ad7503eabe49de10879d79913993253a7131cb9` |

## 5. Full field-level delta — before = pre-change committed `data/incidents.json`
(13,119 entries), after = this rebuild (13,119 entries)

**Entry count: 13,119 -> 13,119 (unchanged). ID set: IDENTICAL** (`before_ids ==
after_ids`, checked as sets — zero additions, zero removals). No split/merge
side-effect from either the marker addition or the 13 retitles — this was the
hazard flagged in the brief (`title_key(e["title"])` dedupe at
`merge_and_dedupe.py:1258`) and it did **not** materialize.

**Fields with any changed value, across the whole 13,119-entry corpus** (every
other field, including every taxonomy field, is byte-for-byte identical on
every entry):

| Field | Rows changed |
|---|---|
| `content_license` | 95 (all `None` -> the marker object; 0 removed) |
| `title` | 13 |
| `updated` | 13 |
| `last_seen` | 13 |

That is the **entire** diff at the entry level. Nothing else moved.

**content_license coverage:** 1,422 -> **1,517** (exactly the expected 1,422 +
95). Verified as a genuine set-level match, not just a count coincidence: the
set of entry IDs with `content_license` present is now **identical** to the
set of entry IDs with an AIAAIC `source_ids` entry (1,517 == 1,517, symmetric
difference = 0, both directions). This means `export_stix.py`'s
`_is_aiaaic_derived()` heuristic (`source_ids`/`tags`-based) and the
field-derived path now agree on every row with zero exceptions — the
precondition D18 named for D15 to retire the interim STIX heuristic is now
satisfied on this artifact.

**`updated`/`last_seen` churn — declared explicitly, per invariant 4.** The 13
rows bumped are **exactly** the 13 retitled rows (`updated & title` = 13 of 13;
`updated but not title and not content_license` = 0). The other 82
marker-only rows (95 - 13 overlap with the retitle set = 82) got
`content_license` added **without** an `updated` bump (`content_license
changed but NOT updated` = 82). **Declaration: this is correct and intended,
not a gap.** `merge_and_dedupe.py`'s `_CONTENT_FIELDS` list (the fingerprint
`_apply_history` diffs to decide whether to bump `updated`,
`merge_and_dedupe.py:1074-1082`) does **not** include `content_license` —
`title` is in that list (hence the retitle bump) but `content_license` is not,
by the same existing design that already excludes `description_source` /
`description_provenance` (documented at `merge_and_dedupe.py:864-868`:
"excluded from merge_into's key lists by omission, so they stay sticky...
same mechanism as description itself"). I did not add or change this list;
the pre-existing convention
already treats attribution/provenance metadata as distinct from "content" for
`updated`-bump purposes, and adding `content_license` to the other 92 rows is
consistent with that convention, not an exception to it. `last_seen` is a
derived echo of `updated` (`merge_and_dedupe.py:1554-1555`,
`e["last_seen"] = e["updated"]`), so its 13-row change is not an independent
fact — it moves in lockstep with `updated` by construction.

`added` is unchanged on all 13 retitled rows (checked directly:
`2026-05-16` on every one) — invariant 4's immutability half holds.

`data/stats.json`'s `generated` field moved `2026-07-28` -> `2026-07-29`
(today's build date) with `incident_count` (13,119), `landmark_count` (1,905),
`version` (2.8.0), `year_min`/`year_max` all unchanged — an expected, once-
per-build-day artifact, not a content signal.

**Heuristic-reads-`title` check (the D9-cascade precedent, explicitly
required).** Grepped every ingest/merge script for `title` reads that feed a
classification decision. Two hits that matter:
- `merge_and_dedupe.py:1354` (`classify_attack_vector` fallback text) reads
  `title` **only when `attack_vector` is missing or `"other"`**. All 95
  hand-curated AIAAIC rows arrive with an explicit non-`"other"` `attack_vector`
  (e.g. `deepfake`), so this path never executes for them — confirmed
  empirically: `attack_vector` is identical on every one of the 13 retitled
  rows, before and after.
- `_classify_corpus()` (`merge_and_dedupe.py:574`) reads
  `title` **unconditionally**, every build, concatenated with description/tags,
  to assign `security` vs. `ai-harm`. This one **does** run on every retitled
  row. Checked per-row, not just in aggregate: all 13 retitled rows are
  `corpus: security` both before and after — **zero cascade**, confirmed
  directly rather than inferred from the aggregate count matching.
- `maybe_rewrite_cve_title()` (`:642`) also reads `title`, but only rewrites
  when the title matches specific CVE-boilerplate prefixes or a "`<Product> is
  a/an ...`" pattern (the second branch additionally requires `cve_ids`); none
  of the 13 new titles match either shape and none of these rows carry
  `cve_ids`, so it is a no-op here (confirmed: the 13 titles landed exactly as
  written, unmodified by this pass).

**Distributions, corpus-wide, before/after — all EQUAL:** `attack_vector`,
`severity`, `corpus`, `quality_tier`/`tier`, `owasp_llm`, `owasp_asi`,
`nist_ai_rmf`, `mitre_atlas` (full per-value counts compared, not just
aggregate totals). `landmark_count` (a `data/stats.json` aggregate, not a
per-entry field) is unchanged at 1,905.

**Rendered-doc churn (`INCIDENTS.md`, `docs/incidents/{2019,2022,2023,2024}.md`,
the three `incidents.min.json` mirrors) — reviewed, not a defect.**
`render_markdown.py` sorts/ranks entries (a monotonic row-index column in
`INCIDENTS.md`, ordered blocks in the year shards); changing 13 titles moves
each of those 13 entries to a new position in that ordering, which
legitimately shifts surrounding row numbers and re-orders blocks — confirmed
by inspecting the actual diffs (each touched year-shard shows exactly one
`<div>` block deleted from its old position and re-inserted, unchanged in
content, at its new position; `INCIDENTS.md`'s diff is the same pattern via
row renumbering). The 4 touched year shards (2019, 2022, 2023, 2024) are
exactly the 4 distinct years among the 13 retitled rows' `date` values — no
other year file changed. `content_license` is not rendered into any Markdown
surface (grepped, no match), so none of that churn is attributable to
deliverable (a). `docs/data/incidents.min.json` and
`src/genai_incidents/data/incidents.min.json` are verified identical to
`data/incidents.min.json` (same SHA-256, `13d4fe7f...`) — mirrors in sync.

## 6. Schema tension — NOT fixed here, exact wording for schema-architect

`schema/incident.schema.json:94` (the `content_license` property description)
currently reads, in full:

> "Row-level license-obligation marker: this entry's CONTENT derives from an
> upstream source whose license imposes obligations (attribution, possibly
> share-alike) on the row itself, over and above the repository's own
> LICENSE-DATA. Source-generic by design — the source is named in the `source`
> VALUE, never in the field name, so any future source with row-level
> obligations reuses this mechanism unchanged. **Set at ingest, in lockstep
> with description_source**, by whichever entry survives dedup as the merge
> target; like description_source it is EXCLUDED from merge_into's
> union/absorb behaviour (that exclusion is what keeps it sticky and truthful)
> and is never overwritten by a later merge. Surfaces: data/incidents.json and
> the HuggingFace export carry it in full; data/incidents.min.json carries it
> on marked rows only, absent elsewhere; the STIX bundle mirrors it per-row as
> an `x_content_license` custom property (D14) — emitted from this field once
> the WS0-T3 Phase B rebuild populates it, and until then from an interim
> AIAAIC-source heuristic that is retired at that rebuild; MISP carries no
> description at all and so no marker (D12(b), as revised by D14). Absence
> means no row-level obligation is known for this entry — NOT that the entry
> is unencumbered."

The bolded clause is now false for 95 rows: after this change, `content_license`
is present on rows whose `description_source` is absent (project-authored
description, per D10) because the row's *title*, not its description, is the
AIAAIC-derived content. **Proposed replacement for that one clause** (rest of
the paragraph unchanged):

> "Set at ingest, by whichever entry survives dedup as the merge target.
> Historically set in lockstep with `description_source` for AIAAIC-sheet rows
> (both provenance fields describe the same aiaaic-origin description); since
> 2026-07-29 (E16/D18) also set independently on the 95 hand-curated AIAAIC
> rows, whose *title* (and, before retitling, in 13 cases the title verbatim)
> derives from AIAAIC even though their `description` is project-authored and
> carries no `description_source`. `content_license` and `description_source`
> are two independent per-field provenance markers that happen to coincide on
> sheet-derived rows, not one joint marker."

The `$comment` at (currently) line ~304 reads, in full:

> "Row-level license obligations are per-source. Today only AIAAIC-origin
> descriptions carry one, so every entry whose description_source is aiaaic
> must also carry content_license. When another source acquires row-level
> obligations, extend this conditional per source — re-scope it, never drop
> it."

**Proposed replacement** (the enforced `if`/`then` conditional below it is
still correct and should NOT change — every `description_source: aiaaic` row
still carries `content_license`, verified: `validate.py` passes 13,119/13,119
after this change with that conditional in force):

> "Row-level license obligations are per-source. Every entry whose
> `description_source` is `aiaaic` must also carry `content_license` (enforced
> below) — that direction still holds. The converse does not: since E16/D18
> (2026-07-29), the 95 hand-curated AIAAIC rows also carry `content_license`
> via their AIAAIC-sourced title/facts, even though their `description` is
> project-authored and carries no `description_source`. When another source
> acquires row-level obligations, extend the conditional per source — re-scope
> it, never drop it."

I did not edit `schema/` — this is schema-architect's file per the brief.

## 7. What I found and did NOT act on

- **STIX heuristic retirement (D15).** Confirmed the precondition D18 named
  (field marker and heuristic now agree on the full 1,517-row set, zero
  exceptions) but did not touch `scripts/export_stix.py` — D15 is a separate
  board decision/task, not this deliverable.
- **`conflicts` schema field.** Opinion given in §3; not implemented — a
  schema-architect/WS3-T2 call.
- **The `>=0.8` band (47 rows).** Left alone per the brief; that's
  `docs/audits/E16-title-similarity-review-2026-07-29.md`'s scope.
- Did not add `description_provenance`/`description_source` to the 95
  hand-curated rows — out of scope for E16 and would misstate provenance (see
  §1).

## 8. Reviewer verification recipe

```
git diff --stat ingest/aiaaic_incidents.json data/incidents.json data/incidents.min.json \
    data/stats.json INCIDENTS.md docs/incidents/2019.md docs/incidents/2022.md \
    docs/incidents/2023.md docs/incidents/2024.md docs/data/incidents.min.json \
    src/genai_incidents/data/incidents.min.json
python scripts/parse_existing.py
python scripts/merge_and_dedupe.py
python scripts/render_markdown.py
python scripts/render_docs_stats.py
python scripts/validate.py
python scripts/check_stats_drift.py
python -m pytest tests -q
python -c "import json; d=json.load(open('data/incidents.json',encoding='utf-8'))['incidents']; \
print('content_license:', sum(1 for e in d if e.get('content_license'))); \
print('entries:', len(d))"
```
Expect: no further diff after re-running the build (determinism); `13119/13119
entries valid; 0 with errors`; stats-drift clean; `227 passed`; `content_license:
1517`; `entries: 13119`.
