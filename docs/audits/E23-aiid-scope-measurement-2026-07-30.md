# E23 — AIID Scope Measurement: Does AIID Need the Marker AIAAIC Has?

**Task:** E23, commissioned directly by the user (release-gating measurement).
**Author:** pipeline-engineer. **Establishes facts only — does not rule.**
Whether any AIID-derived content requires marking is WS0 license-auditor's
reserved lane (`CLAUDE.md`); this document is that ruling's input.
**Method:** mirrors E16's join-and-search
(`docs/audits/E16-title-similarity-review-2026-07-29.md`) — join corpus rows
back to the pinned upstream artifact, search every field for surviving
upstream text, count exact/near matches, and report what a threshold-based
summary would have missed. Read E16 first; this document assumes it.
**Reproduced from:** `main` at `dba4adc6`. All measurements below are
re-derivable from committed files with no network access (see the Method
note in §7 on why one candidate live-check was *not* performed).
**Working files:** all probe scripts and intermediate JSON were written to
the session scratchpad
(`C:\Users\emman\AppData\Local\Temp\claude\...\scratchpad\`), never to
`data/*.json` or `ingest/*.json` — no committed input was touched by any
probe run in this task.

---

## 0. Answer in one paragraph, for the impatient reader

**Six** distinct code/data paths put AIID-labelled content in front of the
corpus, not three. Of those, **one dominates almost totally**: the sanctioned
snapshot (`ingest/aiid_full.json`, §1.2a) supplies verbatim-by-design
`title` text (from AIID's CC-BY-SA-licensed `incidents` collection) plus an
always-original templated `description`, and its content **wins the merge
for 1,463 of 1,465** AIID-tagged corpus rows (99.86%) — this is the same
population `docs/SOURCE_LICENSES.md` §1.2a already flags as open
(share-alike/database-right, same posture as AIAAIC's E13). **The other five
paths are, empirically, close to moot**: a hand-curated 111-row file
(`ingest/aiid_incidents.json`) contains real risk — independently paraphrased
titles and unverifiable-provenance narrative descriptions on 63 genuinely
AIID-sourced rows — but **every single one of those 63 rows' own title and
description text is superseded in the shipped corpus by the sanctioned
snapshot's version**, a deterministic, code-verified outcome of file-load
order plus URL/source-ID-keyed dedup, not a lucky accident. The same holds,
in every case checked, for AIRI Navigator's independently-composed
AIID-cross-referenced text (1,457 rows sharing the `AIID-<n>` source-ID
convention). The bridge file and the one curation override carry no
AIID-derived expressive text at all. **`content_license` is 0/1,466 on any
AIID-flagged row** — confirmed empirically and mechanically: no AIID code
path ever calls anything like AIAAIC's `aiaaic_content_license()`.

---

## 1. Every path AIID content reaches the corpus (six, not three)

| # | Path | Mechanism | Rows (pre-merge) | Verbatim AIID text? |
|---|---|---|---|---|
| (a) | `scripts/ingest_aiid_snapshot.py` → `ingest/aiid_full.json` | Sanctioned weekly-snapshot ingest, §1.2a, **ACTIVE** | 1,548 | `title` yes (by design); `description` no (templated); `references[].title` no (generic label) |
| (b) | `ingest/aiid_incidents.json` — **AIID-<n> rows only** | Hand-curated, static JSON, no producing script (parallel to `ingest/aiaaic_incidents.json`) | 63 (of 111 total in the file — see (b′)) | `title` — paraphrased, not verbatim, 0/63 exact; `description` — rich narrative, unverified provenance; `references[0].title` — verbatim AIID title on 2/63 only |
| (b′) | *same file*, **EXT-<...> rows** | Same file, **not AIID content** | 48 (of 111) | None — original hand-authored security-research writeups (PromptArmor, Aim Labs, Legit Security, Wiz, etc.); 1 of the 48 cites an AIID **entity** page URL only (a fact, not text) |
| (c) | `scripts/ingest_external.py::ingest_aiid_oecd_bridge()` → `ingest/aiid_oecd_relationships.json` | AIID↔OECD ID/URL cross-reference bridge, §1.3 | 681 | None — synthesized description, generic reference titles |
| (d) | `data/curation_overrides.json` key `"AIID-1263"` | Manual editorial override | 1 | None — structured fields (`reversibility_class`, `discovery_method`) + a `_note` citing Anthropic's and Paul Weiss's own publications, zero AIID text |
| (e) | `scripts/scrape_aiid.py` | **RETIRED** (§1.2, WS0-T4/D1); disabled in `Makefile`; reused only as a taxonomy-classification function library (`TAXONOMY_RULES`, `is_security_relevant`, `map_taxonomy`, `severity_for`) by (a) | 0 committed output of its own (shared the `aiid_full.json` filename, now overwritten by (a)) | N/A |
| (f) | `scripts/ingest_airi_navigator.py` → `ingest/airi_navigator_incidents.json` | AIRI Navigator's own ingest, §1.4 — emits rows keyed `source_id: f"AIID-{aiid_id}"` when AIRI's row carries an AIID cross-reference, with AIRI's **own** `title`/`description` text (not copied from AIID, but of open transitive-share-alike status per §1.4) | 1,457 (of that file's total, **all** tagged `aiid`) | Not AIID's own text, but AIID-adjacent per §1.4's already-open question — included here because "an unenumerated path is the failure mode" and this file's `source_id` convention makes it participate directly in AIID's own dedup keying (§3) |

**Also checked and confirmed empty:** `data/legacy_consolidated.json` (239
entries, loaded with highest priority before any `ingest/*.json` file) — zero
AIID/`incidentdatabase.ai` references anywhere in it (`grep -i
"aiid\|incidentdatabase"` → no matches). It cannot be a seventh path.

Path (f) was not named in the brief's "at minimum" list. It surfaced because
`ingest_airi_navigator.py:120` falls back to
`f"https://incidentdatabase.ai/cite/{aiid_id}"` whenever AIRI's own row lacks
an `aiid_url`, and — more consequentially — `ingest_airi_navigator.py:138`
sets `"source_id": f"AIID-{aiid_id}"`, the **identical source-ID convention**
paths (a) and (b) use. That single line is why AIRI's ingest participates in
AIID's own source-ID-keyed dedup (§3) rather than living in its own,
separately-keyed lane the way path (c)'s `AIID-<n>-OECD` suffix does.

---

## 2. Per-path, per-field measurement

### 2a. `ingest/aiid_full.json` (1,548 rows) — the dominant path

Verified by full-file scan (not sampling), against the script's own documented
guarantee:

| Field | Finding |
|---|---|
| `title` | Verbatim, by design (`ingest_aiid_snapshot.py:269` copies `row["title"]` from `incidents.csv` unmodified) — confirmed present verbatim on all 1,548 rows by construction; this is the licensed `incidents` collection's own `title` column. |
| `description` | **0/1,548** deviate from the fixed template `"AI Incident Database (AIID) entry #{id}: {title}. [Alleged deployer/developer: {affected}. ]See the linked AIID entry for full narrative, sourcing, and classification."` — verified by regex match across every row. AIID's own free-text `description` (part of the licensed `incidents` collection) is read only as an ephemeral classification signal (`ingest_aiid_snapshot.py:272`) and never reaches this output — confirmed both by code read and by this measurement. |
| `references[0].title` | **0/1,548** deviate from the fixed template `"AIID incident #{id}"` (url `https://incidentdatabase.ai/cite/{id}/`, type `report`) — verified by exact match across every row, including URL and type. No hidden verbatim headline the way E16 found for AIAAIC — this field is a generic citation label, not AIID's own text. |
| `reports` collection | Never extracted from the snapshot archive — `extract_members()` (`ingest_aiid_snapshot.py:196-216`) names only `incidents.csv`, `duplicates.csv`, `classifications_MIT.csv`, `license.txt`; `reports.csv`/`reports.bson` are not in the wanted-member set and the function would raise if they were required and missing. |

**Note on the raw upstream itself:** unlike AIAAIC (where E16 joined against
the raw cached sheet, `ingest/_cache/aiaaic_sheet.csv`, committed), **AIID's
raw upstream CSV is never committed** — `ingest/_cache/` is entirely
git-ignored (`.gitignore:29`), and `ingest/aiid_full.json` is itself
`ingest_aiid_snapshot.py`'s *output* (the already-reduced facts+link form),
not a pinned copy of AIID's raw `incidents.csv`. **This is a correction to
the brief's premise** ("the pinned snapshot is committed at
`ingest/aiid_full.json`") worth stating precisely: what's pinned is the
*provenance record* (`ingest/aiid_full.provenance.json` — snapshot filename,
URL, sha256, counts) plus the *reduced output*, not the raw upstream table.
Practically this doesn't weaken the measurement for this path, because the
reduction script's own guarantee (title verbatim, description templated) is
independently verifiable by code read and confirmed exactly by the full-file
scan above — there is no *hidden* verbatim content to discover here the way
E16 found in AIAAIC's `references[0].title`, because this path's design
already discloses upfront which field is verbatim.

### 2b. `ingest/aiid_incidents.json` — the 63 genuinely AIID-sourced rows

**Join method:** parsed `AIID-(\d+)` from `source_id`, looked up the same
`aiid_id` in `ingest/aiid_full.json` (used here as ground truth for AIID's
own canonical `incidents.title`, since it's independently confirmed verbatim
per §2a), computed `difflib.SequenceMatcher` ratio — the identical method and
library E16 used.

**Coverage:** all 63 `AIID-<n>` rows joined successfully (63/63, 100% —
because any AIID entry already cross-referenced in the corpus is
unconditionally preserved in `aiid_full.json` regardless of the current
security-relevance filter, per `ingest_aiid_snapshot.py`'s
`load_existing_aiid_ids()`/invariant-3 mechanism). No UNJOINED rows, unlike
AIAAIC's 3.

**`title` field — our paraphrase vs. AIID's own title:**

| Band | Count |
|---|---|
| Exact string match | 0 / 63 |
| Ratio ≥ 0.8, not exact | 36 / 63 |
| Ratio < 0.8 | 27 / 63 |
| Range / mean | 0.277 – 1.0 / ≈0.80 |

Worked examples (highest and lowest ratios):

| aiid_id | ratio | our `title` | AIID's `title` (from `aiid_full.json`) |
|---|---|---|---|
| 306 | 1.0 | Tesla on Autopilot TACC crashed into van on European highway | Tesla on Autopilot TACC Crashed into Van on European Highway |
| 314 | 1.0 | Stable Diffusion abused by 4chan users to deepfake celebrity porn | Stable Diffusion Abused by 4chan Users to Deepfake Celebrity Porn |
| 20 | 0.979 | Collection of Tesla Autopilot-Involved Crashes | A Collection of Tesla Autopilot-Involved Crashes |
| 6 | 0.577 | Microsoft's Tay chatbot poisoned via coordinated user input on Twitter | Microsoft's TayBot Allegedly Posts Racist, Sexist, and Anti-Semitic Content to Twitter |
| 617 | 0.277 | Issaquah Washington high school student generates AI nudes of classmates | Male student allegedly used AI to generate nude photos of female classmates at a high school in Issaquah, Washington |

**A qualitative observation, offered as a fact for license-auditor's own
application of the E16 standard, not a ruling:** the highest-ratio rows
differ from their AIID counterpart only in letter-casing and trivial word
drops (Title Case → sentence case; "A Collection of" → "Collection of") —
this is a materially different shape from E16's AIAAIC findings, where
near-1.0 rows retained AIAAIC's *editorial* choices (a specific verb, a
scare-quote, a clause order). AIID's own titles here read as plain
subject-verb-object incident labels rather than headline-style editorializing
— whether that changes the *Infopaq* analysis is a copyright judgment call
outside this document's remit. The lowest-ratio rows are genuine independent
condensation (shorter, restructured, sometimes voice-flipped) of AIID's often
longer, more heavily-hedged ("Allegedly", "Purported", "Reportedly") titles.

**`references[0].title` — the field E16's brief specifically asked me to
check, because that's where E16's own most valuable finding was:** this is
**not structural** in `ingest/aiid_incidents.json`, unlike AIAAIC's file.

| Pattern | Count |
|---|---|
| Full verbatim AIID title present (`"Incident {id}: {title}"`) | 2 / 63 (aiid_id 6, 20) |
| Bare citation label only (`"Incident {id}"`, no title text) | 61 / 63 |

For the 2 exceptions, the recovered title exactly or near-exactly matches
`aiid_full.json`'s title (ratio 1.0 and 0.979 respectively — see table
above). This is a genuinely different shape from AIAAIC's file, where E16
found the AIAAIC-headline-behind-a-prefix pattern on ≥31/47 sampled and
called it "structural to the whole 95-row set." Here it is the opposite: an
occasional, not structural, pattern.

**`description` field — the open item, stated plainly rather than
guessed at:**

- Length 142–348 characters (mean 249).
- 44 / 63 rows cite **only** the AIID reference URL — no independent
  secondary source is visible in the record to support a "written from
  cited sources, not from AIID's own prose" reading for those rows.
- 19 / 63 cite at least one non-AIID secondary source alongside the AIID
  citation (Wikipedia, CBS News, IEEE Spectrum, Microsoft's own blog, etc.).
- 18 / 63 contain a quoted phrase. Reading them: these are overwhelmingly
  **factual quotes of the incident's own actors or the AI system's own
  output** (Microsoft's press statement; a chatbot's actual generated
  text, e.g. "That's a legally binding offer"; a jailbreak prompt's literal
  wording) — a different pattern from E16's AIAAIC finding, where the
  retained quotes were AIAAIC's own scare-quoted editorial characterizations
  embedded in a headline. Quoting an incident's own facts is not, on its
  face, quoting AIID's editorial expression.
- **No AIID upstream text is committed anywhere in this repository to check
  this field against.** `incidents.csv`'s own `description` column
  (licensed, part of the `incidents` collection) is fetched at ingest time
  by path (a) but treated as an ephemeral, never-persisted classification
  signal — nothing from it is ever written to a committed file.
  `reports.text` (explicitly **excluded** from AIID's CC-BY-SA grant, and of
  uncertain AIID-ownership even before licensing) is never extracted from
  the snapshot archive by any ingest script in this repo, committed nowhere,
  and was not fetched live for this measurement (§7 explains why). **This
  means: whether these 63 hand-authored descriptions echo AIID's own
  `incidents.description`, echo the excluded `reports.text`, or are
  independent synthesis from the cited secondary sources, is genuinely
  unresolved by anything committed in this repository.** This is the single
  most consequential open item this document surfaces — see §5.

### 2c. `ingest/aiid_oecd_relationships.json` (681 rows)

Full code read of `ingest_aiid_oecd_bridge()` (`ingest_external.py:202-247`):
`title` is always the fixed template `"AIID incident #{id} (OECD-tracked)"`;
`description` is always the fixed sentence `"Cross-listed in the AI Incident
Database (AIID) as incident #{id} and tracked by the OECD AI Incidents
Monitor. See the linked entries for full context, victims, references, and
harm classification."`; both `references[].title` entries are generic labels
(`"AIID #{id}"`, `"OECD AI Incidents Monitor entry"`). **Zero fields carry
any upstream-derived string, verbatim or paraphrased** — confirmed by
inspecting every distinct value these two fields take across the 681 rows
(exactly two title shapes, exactly one description string modulo the id
substitution). Matches `docs/SOURCE_LICENSES.md` §1.3's existing "(a)
compatible, low risk" characterization exactly; this measurement adds
nothing new here.

### 2d. `data/curation_overrides.json` key `"AIID-1263"`

One override object: `reversibility_class`, `discovery_method` (both closed
enum values) plus a `_note` citing `anthropic.com/news/disrupting-AI-espionage`
and a Paul Weiss client memo — both non-AIID sources, both the curator's own
summarization. No AIID text of any kind.

---

## 3. The finding the brief did not anticipate: merge precedence makes the risky content a dead letter

**This is the equivalent of E16's `references[0].title` discovery — a field
(here, a *mechanism*) nobody had thought to check.** `ingest/aiid_incidents.json`
sits committed in this repository with real, measurable risk (§2b: paraphrased
titles, description text of unverified provenance). **But 0% of that file's
own title/description text for the 63 genuinely-AIID rows reaches
`data/incidents.json`, the artifact this project actually redistributes.**

**Verified two ways, not asserted:**

**(i) Direct evidence — the shipped corpus itself.** For every one of the 63
`AIID-<n>` source_ids in `ingest/aiid_incidents.json`, the corresponding row
in `data/incidents.json` today carries `description` matching the regex
`^AI Incident Database \(AIID\) entry #\d+: ` — i.e., `aiid_full.json`'s
exact template, not the hand-curated file's narrative text. **63/63 (100%).**
Cross-checked at the whole-population level: of all 1,465 corpus rows
carrying an `aiid_id`, **1,463 (99.86%)** match this same template; the 2
exceptions (aiid_id 898, 1574) carry a *different* non-AIID source's content
(a research-blog-sourced entry and an OECD-AIM entry respectively — both
already covered by their own sources' existing licensing rows, not new AIID
exposure). An initial title-string comparison flagged 6 apparent divergences,
not 2; 4 of those 6 (aiid_id 164, 608, 1413, 1431) turned out to be **false
positives** from a non-breaking-space character (`\xa0`) present in the raw
`aiid_full.json` title but normalized away by `normalize_entry()` before it
reaches the corpus — corrected using the description-template match, a
signal immune to that artifact, and independently spot-checked on `aiid_id
164` (`repr()` diff at the exact byte).

**(ii) Mechanism — why this is guaranteed, not lucky, verified by code read.**
`scripts/merge_and_dedupe.py:1336`: `for src in sorted(INGEST.glob("*.json"))`
— files load in **alphabetical order**. `"aiid_full.json"` sorts before
`"aiid_incidents.json"` (`f` < `i`), confirmed directly
(`sorted(["aiid_full.json","aiid_incidents.json"])` →
`['aiid_full.json', 'aiid_incidents.json']`). Every row in both files shares
the identical `source_id` convention `AIID-<n>`. Dedup priority is CVE-key
→ **source-ID-key** → URL-key → fuzzy-title-key
(`merge_and_dedupe.py:1246-1290`), and the **first** entry seen for a given
key becomes `deduped.append(e)` — the permanent merge target
(`merge_and_dedupe.py:1292-1295`). `merge_into(target, src)`
(`merge_and_dedupe.py:1781-1799`) touches only an explicit allow-list
(taxonomies, tags, `source_ids`, a handful of fill-if-empty scalar fields,
and references deduped **by URL**, target's claim wins ties) — **`title` and
`description` are not in that list and are never overwritten.** Since
`aiid_full.json` processes first, its row for a given `AIID-<n>` always
becomes the target, and `aiid_incidents.json`'s later row for the same ID
only contributes its allow-listed fields (its non-AIID reference URLs —
Wikipedia, CBS News, etc. — do survive this way, confirmed on `AIID-6`'s
final reference list). **Its own `title`/`description`, and even its own
`references[0]` (which shares the exact same `incidentdatabase.ai/cite/{id}/`
URL as `aiid_full.json`'s reference, so it collides and is silently dropped
by the URL-keyed reference dedup at `merge_and_dedupe.py:1793-1799`) never
reach the shipped row.** This was independently confirmed with a read-only
in-process repro (loading the real `legacy_consolidated.json` +
`sorted(ingest/*.json)` through the actual `normalize_entry`/`dedupe_entries`
functions imported from `scripts/merge_and_dedupe.py`, inspecting the
in-memory result, **writing no output file**) — the repro's survivors match
the committed corpus's content exactly for every ID checked.

**The same reasoning applies to path (f).** `ingest/airi_navigator_incidents.json`
sorts alphabetically *after* `aiid_full.json` too
(`sorted(['aiid_full.json','airi_navigator_incidents.json'])` confirms
`aiid_full.json` first), shares the `AIID-<n>` source-ID convention, and is
therefore subject to the identical target-wins mechanism. **In every case
checked** (all 1,465 `aiid_id`-bearing corpus rows), no surviving row's
content matches AIRI Navigator's own composed text — the two rows (898,
1574) whose content isn't `aiid_full.json`'s template are, respectively, a
research-blog-sourced entry and an OECD-AIM entry, not AIRI Navigator's own
text either.

**What this means, stated as a fact, not a ruling:** the population that
actually reaches, and is redistributed via, `data/incidents.json` and its
downstream exports (`incidents.min.json`, STIX, HuggingFace, the rendered
site) is — for AIID — overwhelmingly path (a) alone: verbatim `title` from a
**confirmed-licensed** collection, plus an always-original `description`.
The genuinely uncertain content (paths (b) and (f)'s own composed text) sits
committed in this public repository's `ingest/` working files but does not
ship in the redistributed dataset artifact. Whether that distinction matters
for licensing purposes — i.e., whether a committed-but-unshipped file in a
public git history is itself a "redistribution" requiring the same treatment
— is exactly the kind of question this document surfaces for license-auditor
rather than answers.

---

## 4. Reconciling the foreman's 1,464 / 0 figures

| Signal | Count |
|---|---|
| `tags` contains `"aiid"` | **1,464** (exact match to the foreman's figure) |
| `aiid_id` field present | 1,465 |
| `source_id`/`source_ids` matches `AIID-<n>[-OECD]` | 1,465 |
| `references[].url` contains `incidentdatabase.ai` | 1,465 |
| **Union of all four signals** | **1,466** |
| `content_license` marker present, on any row in the union | **0** (confirmed exactly) |

The union (1,466) exceeds the tag-only count (1,464) by 2, for two
independent, fully explained reasons — per the brief's instruction to check
reference-domain and source_id in addition to tags:

1. **`AIID-1574` / `OECD-AIM-2026-04-03-c16a`** (the Lake Zurich High School
   entry, §3's second exception) — tagged only `oecd-aim`, missing `aiid`,
   because the surviving content is OECD-AIM's, not AIID's, and the ingest
   that actually wrote this row's tags never adds `"aiid"` on its own; the
   `aiid_id` field is still set (a fill-if-empty merge field). This is a
   tag-heuristic undercount of a row that's genuinely AIID-cross-referenced
   but not AIID-content-bearing.
2. **`EXT-2024-WORMGPT-FRAUDGPT`** — a wholly non-AIID hand-curated entry
   (§1(b′)) whose only AIID footprint is a reference to an AIID **entity**
   page (`incidentdatabase.ai/entities/fraudgpt/`, not an incident citation)
   — a URL fact, zero AIID text.

**Mechanically, why the marker is 0/1,466, not just empirically:**
`grep -rn "content_license"` across `scripts/` finds it set (as opposed to
merely read/propagated) in exactly one place —
`ingest_aiaaic_sheet.py:542`, `"content_license": aiaaic_content_license()`,
called unconditionally on every row that ingest emits. No AIID ingest path
((a), (b), (c), or (f)) calls anything equivalent. `merge_and_dedupe.py:873-874`
propagates `content_license` from a raw ingest row into the corpus entry
*if present on the raw row* — pure pass-through, source-agnostic, and
already correctly carrying AIAAIC's marker through merges. **The reason
AIID carries 0 is entirely that no ingest script for it has ever set the
field — not a schema gap, not a merge-pipeline gap.**

**A mechanical, non-licensing fact worth recording for whoever implements
a ruling:** the marker's own shape (`docs/specs/WS0-T3-marker-shape-2026-07-27.md`
§1) is **deliberately source-generic** — `content_license.source` is a free
string value, not a fixed enum, and the schema's `$comment` on the AIAAIC-keyed
conditional explicitly "instructs the next editor to extend it per source
rather than delete it" (§84-89 of that spec). If license-auditor rules AIID
needs marking, implementing it is a small, well-precedented lift mirroring
`aiaaic_content_license()` — no schema change, and `merge_into`'s
allow-list already leaves `content_license` untouched (sticky-by-omission,
the same mechanism §3 showed for `title`/`description`), so no merge-pipeline
change either.

---

## 5. Facts for license-auditor — not a ruling

Stated as the brief asked: which populations carry surviving AIID text, from
which collections, and therefore what needs a ruling.

- **The population that actually ships (≈1,463 of 13,119 corpus rows, all
  via path (a)):** carries AIID's own `title` **verbatim**, sourced from the
  `incidents` collection — a collection AIID's own terms-of-use **confirms**
  is CC-BY-SA 4.0 licensed (`docs/SOURCE_LICENSES.md` §1.2/§1.2a), not an
  open copyright-subsistence question the way AIAAIC's headline is (E15).
  `description` on every one of these rows is original template text, never
  AIID's own prose. This is exactly the population `SOURCE_LICENSES.md`
  §1.2a already flags open — "same class of open question as AIAAIC's E13
  finding" (share-alike / possible sui-generis database right over the
  `incidents`/`classifications` collections) — and this measurement adds
  no new fact changing that characterization; it *confirms* the population's
  size and confirms no hidden verbatim text exists beyond the disclosed
  `title` field (§2a).
- **The population with genuinely unresolved provenance (63 rows'
  worth of text, sourced from the `incidents` collection at minimum,
  possibly touching the excluded `reports.text`, sitting in
  `ingest/aiid_incidents.json`):** does **not** reach the redistributed
  corpus (§3), but does sit committed in this public repository. Whether
  that residual fact requires action is a licensing-scope-of-"redistribution"
  question this document is not positioned to answer.
- **The population that is AIID-adjacent but not AIID's own text (1,457
  rows in `ingest/airi_navigator_incidents.json` sharing the `AIID-<n>`
  source-ID convention):** already tracked as an open item under §1.4 (the
  transitive-share-alike question for AIRI-wrapped AIID fields), unaffected
  by this measurement except to confirm none of that text survives the
  corpus merge either (§3).
- **Zero risk, confirmed:** paths (c) and (d) — no AIID-derived expressive
  text in either.

**If the answer to "does any of it need marking the way AIAAIC's did"
resolves to yes for path (a)'s ~1,463 rows**, the marker's shape is already
built source-generically (§4) and the fix is a small, precedented ingest
change — not a schema or merge-pipeline change. **If it resolves to yes for
the 63 hand-curated rows or the 1,457 AIRI-cross-referenced rows**, the
marking question is complicated by the fact that the content in question is
not actually part of the artifact `data/incidents.json`/its exports
redistribute (§3) — marking a row whose risky content never ships would mark
the wrong artifact; the more relevant question may be whether
`ingest/aiid_incidents.json` itself (as a committed, publicly-visible file)
needs treatment independent of the corpus-marking mechanism entirely.

---

## 6. Not covered / limitations, stated plainly

- **The `description` field of the 63 hand-curated rows remains genuinely
  unverified against any AIID upstream text** (§2b) — this repo commits no
  raw AIID `incidents.description` or `reports.text` to check it against.
  See §7 for why a live check was not attempted.
- **Not all 1,457 AIRI-Navigator AIID-cross-referenced rows were individually
  checked against the shipped corpus** — only the 6 rows where the corpus's
  title-string comparison first flagged a divergence (§3), 2 of which turned
  out to be genuine (and neither is AIRI's own text). The claim that AIRI's
  own composed text never survives is stated as "in every case checked," not
  as an exhaustive 1,457-row proof.
- **The merge-precedence mechanism (§3) was verified for the specific 63 +
  6 IDs checked**, via a read-only repro plus direct code read of
  `merge_and_dedupe.py`'s dedup/merge functions. I did not re-run the repro
  against the full ~13,000-entry corpus (would require touching every
  ingest file, not just the AIID-relevant ones, for no additional AIID-specific
  information) — the code-level mechanism (alphabetical glob order,
  allow-list-only `merge_into`, URL-keyed reference dedup) is general and
  gives no reason to expect the 63/6 sample is unrepresentative, but that is
  an inference from a verified mechanism, not a full-population re-proof.
- **Headline/content drift over time** (AIID could have edited its own
  `incidents.title` since the 2026-07-13 snapshot `ingest/aiid_full.json`
  was built from) was not checked — no live fetch was performed (§7).

## 7. Method note: the one live check considered and not performed

The most direct way to close the §2b/§5 open item (does the hand-curated
`description` field echo AIID's own `incidents.description` or the excluded
`reports.text`, or is it independent synthesis) would be to view one or two
live AIID `/cite/<id>/` pages. **This was not done.** The brief's constraint
was explicit ("this task should need no network at all... if you think you
need a fetch, say why first") and the brief's own countervailing-fact section
already establishes that WS0-T4's *shipped* path treats AIID description
text as ephemeral/never-persisted; since §3 independently establishes that
the hand-curated file's description text never reaches the shipped corpus
either, resolving this specific provenance question would inform the status
of a non-shipped, committed working file, not the redistributed dataset —
a real but lower-stakes question than the release-gating one this task was
commissioned to answer. Flagged as a candidate follow-up for
license-auditor's own judgment on whether it's worth pursuing, not performed
here.

---

## Summary for the foreman

- **Six enumerated paths** (§1), not three — path (f) (AIRI Navigator's
  `AIID-<n>`-keyed rows) was not named in the brief and its participation in
  AIID's own dedup keying is the reason it matters.
- **Per-path/per-field counts and worked examples**: §2.
- **The load-bearing, unanticipated finding**: merge precedence
  (alphabetical file load order + source-ID/URL-keyed dedup + an allow-list
  `merge_into` that never touches `title`/`description`) makes the hand-curated
  file's own risky content a dead letter in the shipped corpus — 63/63 and,
  in every case checked, the AIRI-Navigator population too. Verified two
  independent ways (§3).
- **1,464/0 reconciled**: exact tag match, union of 1,466 with two fully
  explained additions, 0/1,466 marked — confirmed both empirically and by
  the absence of any AIID-side call to a marker-setting function (§4).
- **Facts routed to license-auditor, no ruling made** (§5): the ~1,463-row
  shipped population carries verbatim `title` from a *confirmed*-licensed
  collection (same open share-alike/database-right posture already on
  record); the 63-row and 1,457-row populations carry genuinely uncertain
  text that does not ship.
- **File**: `docs/audits/E23-aiid-scope-measurement-2026-07-30.md`.
- **Not covered**: full-population re-verification beyond the checked IDs;
  the hand-curated description field's true upstream provenance (no live
  fetch performed, §7); AIID headline drift over time.
