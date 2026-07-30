# E21 — OECD AIM narrative-text licence re-analysis (§1.5)

**Commissioned by the user, 2026-07-30, as a release-gating investigation.**
Answers `docs/audits/PHASE1-EXIT-2026-07-30.md` BLOCKER A: does the
`Redistribute-verbatim: NO` finding in `docs/SOURCE_LICENSES.md` §1.5 rest on
a premise that holds for the text `scripts/ingest_oecd_aim.py` actually
ships? **Outcome: (B) — the reduction is still required.** Not because the
prior premise (quoted third-party news copy) turned out to be true — it
didn't — but because the correct premise, established below, is a *different
and equally disqualifying* one under this project's own conservative-default
rule.

**Method note.** I have no Bash. Every fetch below is WebFetch or WebSearch.
Per this file's own standing rule (`docs/SOURCE_LICENSES.md` header) and the
brief's standing rule, I say plainly where I could not get a raw-HTML
verbatim read and rely instead on a tool's paraphrase or a search-engine
snippet — those places are marked **NOT PRIMARY-SOURCE QUOTABLE (by me,
today)** and named as a check for red-reviewer to run with `curl`.

---

## 1. What was already established (re-verified, not re-derived)

Per the brief, these six facts were measured 2026-07-29/30 by the WS0-T4/OECD
gates and the foreman. I did not re-run them; I read the artifacts that
record them (`docs/SOURCE_LICENSES.md` §1.5, `docs/outreach/oecd-aim-terms.md`,
`docs/audits/PHASE1-EXIT-2026-07-30.md`, `scripts/ingest_oecd_aim.py`) and
confirm they are consistent with the code as it stands today
(`normalize_body()`, `scripts/ingest_oecd_aim.py:176-265`):

1. The `evidences`-fallback branch (`ingest_oecd_aim.py:201-205`) fired for
   **0 of 4,160** rows checked; the shipping `description` is effectively
   100% the `summary` path (`:199,208`).
2. On a deep-parsed page, `summary` does not appear anywhere inside the
   concatenated `evidences` blob.
3. AIM's `evidences` strings read as analytical/evaluative sentences (e.g.
   *"The AI system's role in generating and spreading false content is
   pivotal to the harm experienced"*), not verbatim news excerpts.
4. The board records a 2026-07-16 red-reviewer finding that OECD written
   content published as of 2024-07-01 is CC BY 4.0, sourced to a `curl` HTTP
   200 on `oecd.org/en/about/terms-conditions.html` that I could not
   reproduce today (see §2 below) — **this fact currently rests on that
   board record plus today's search corroboration, not on a primary fetch I
   performed.**
5. The AIM methodology page's third-party-IP disclaimer is verbatim and
   current (raw-HTML `curl`, red-reviewer, 2026-07-30, confirmed twice):
   *"Any of the copyrights, trademarks, service marks, collective marks,
   design rights, or other intellectual property or proprietary rights that
   are mentioned, cited, or otherwise included in the AIM are the property
   of their respective owners."*
6. `oecd.org/en/about/terms-conditions.html` 403s across every client/UA
   combination tried by the foreman on 2026-07-30, including `curl`.

**I independently re-confirmed #6 today**, and it still holds — see §2.

## 2. New primary-source fetches performed today (2026-07-30)

### 2.1 The general OECD terms page is still unreachable to any tool I have

- `https://www.oecd.org/en/about/terms-conditions.html` → WebFetch → **HTTP
  403.**
- `https://www.oecd.org/termsandconditions/` (the URL `oecd.ai`'s own footer
  actually links to — see §2.2) → WebFetch → **HTTP 403.**
- `https://www.oecd.org/en/about/oecd-open-by-default-policy.html` (the named
  open-access policy page) → WebFetch → **HTTP 403.**
- `https://www.oecd.org/en/about/news/press-releases/2024/07/oecd-data-publications-and-analysis-become-freely-accessible.html`
  (the July-2024 press release announcing the policy) → WebFetch → **HTTP
  403.**
- `web.archive.org` is blocked to this tool entirely (`WebFetch` returns "unable
  to fetch from web.archive.org" before even attempting the request) — no
  archived-snapshot workaround was available to me.

**This confirms fact #6 is still current, not stale**, and extends it: every
oecd.org page I tried that would carry the operative CC-BY-4.0/Data-reuse
clause text 403s to me, with no available workaround. **Fact 4's operative
clause therefore remains NOT PRIMARY-SOURCE QUOTABLE by me today.** What
follows on this specific point is corroboration, not verification:

Three independent WebSearch queries today, worded differently, converged on
the same specifics without me feeding them the specifics in advance:

> *"Most OECD written content published as of 1 July 2024 is licensed under a
> Creative Commons Attribution BY 4.0 licence (CC BY 4.0)... For content
> published before 1 July 2024... generally available for commercial and
> non-commercial purposes on terms similar to CC BY 4.0."*

and, separately quoted by a second query:

> *"Except where additional restrictions apply, you can extract from,
> download, copy, adapt, print, distribute, share and embed Data for any
> purpose, even for commercial use. However, you must give appropriate
> credit to the OECD by using the citation associated with the relevant
> Data, or... OECD (year), (dataset name), (data source) DOI or URL (accessed
> on (date))."*

Both are consistent with §1.5's existing text verbatim, and with the
2026-07-16 board record. **I am treating fact 4 exactly as the existing
document already does — "corroborated across independent web searches...
still short of a primary-source fetch" — not upgrading its evidentiary
status, because I could not.** Check for red-reviewer: re-run all four
`curl` fetches above (no-UA and browser-UA) to confirm the 403s are still
current before this file is relied on again.

A distinct and important fact **did** come through with a genuine primary
fetch, and it separates "Data" from "written content" for OECD generally:
written-content categories named in a search snippet are *"OECD
publications, working papers, journal articles, policy papers, policy
briefs, case studies and country notes"* — a list of discrete authored
publications. AIM's per-incident metadata fields are not natively any of
these. This matters for §3.

### 2.2 `oecd.ai` (the AIM host) is reachable, and its own terms are OECD's general terms

`https://oecd.ai` → WebFetch → HTTP 200. Footer:

> Terms & conditions — `https://www.oecd.org/termsandconditions/`
> Privacy policy — `https://www.oecd.org/privacy/`
> © 2026 OECD. All rights reserved

This establishes `oecd.ai` incorporates `oecd.org`'s general terms as its
own — but this is a generic footer link, not AIM-specific. §2.3 supplies the
AIM-specific version of the same fact, and it is stronger.

### 2.3 AIM itself explicitly says it is governed by the general terms

`https://oecd.ai/en/incidents-methodology` → WebFetch → **HTTP 200** (the
same page red-reviewer independently `curl`-verified twice on 2026-07-30 for
fact #5; that page has an established track record of raw-HTML fidelity in
this project). Asked for the exact sentence, verbatim, no paraphrase:

> *"Your use of the OECD AI incidents and hazards monitor (previously AI
> Incidents Monitor) ("AIM") is subject to the terms and conditions found at
> www.oecd.org/termsandconditions."*

**This is new to this file.** It answers the brief's central instruction —
"look at what OECD's own pages name as their terms... on AIM pages
themselves" — directly: AIM does not merely inherit `oecd.ai`'s generic
footer terms by omission; it says so on its own methodology page.

**Caveat, stated because it matters for what follows:** this establishes
*that* OECD's general terms formally govern use of the AIM *service*. It
does not by itself establish that AIM's specific text fields are the kind of
content those terms were written to cover, nor that OECD's grant is
effective against whatever rights the underlying news sources may hold. See
§3.

### 2.4 The pivotal new fact: AIM's title/summary fields are LLM-generated from third-party news, not composed by OECD staff or quoted from source articles

This is the fact that changes the outcome from what the brief's own working
hypothesis expected. Same page, same fetch, asked specifically what
"summary" is and how it is produced — quoted verbatim, with surrounding
context so "this metadata" is unambiguous:

> *"Each event is enriched with relevant metadata, including an event title,
> summary, the harm type, severity, affected stakeholders, and the country
> where it occurred, among others. This metadata is LLM-generated (OpenAI's
> o3-mini) from the top three articles of each event, selected from
> different news outlets."*

I independently cross-checked this with a second, separately-worded WebSearch
query, which returned the **identical sentence, byte-for-byte** without my
having supplied it. Two different tool calls converging on identical text
is not full independence (both ultimately read the same underlying page),
but it is stronger than a single paraphrase and is consistent with how this
project treats "corroborated, not yet raw-HTML-verified" facts elsewhere.
**Check for red-reviewer: `curl` this exact string against
`https://oecd.ai/en/incidents-methodology` before this fact is treated as
settled — it is the single most load-bearing fact in this analysis, on a
page this project's own tooling has previously mis-summarized once already
(the disclaimer-quote incident, 2026-07-30, resolved in the page's favor,
but the near-miss is exactly why this fact needs the same check.)**

**What this means concretely:** the earlier hypothesis in
`docs/SOURCE_LICENSES.md` §1.5 (added 2026-07-30, pre-this-file) was that
`summary` "reads as a composed OECD abstract" — implicitly, OECD staff
prose. That is not what it is. It is **machine output synthesized from
copyrighted third-party news article text**, produced automatically at
ingestion time with no human authorship in the loop for that specific
string. `title` is generated by the identical pipeline, in the identical
sentence. **`title` therefore carries the same open question as `summary`**
— see the brief's explicit ask about this and §5 below.

---

## 3. The analysis: does OECD's own grant reach LLM-synthesized-from-third-party-news text?

This is the real hinge, and it is a different, harder question than "is this
OECD prose or a quoted excerpt" — the brief's own framing, reasonably, before
this fact was known. Three layers:

**Layer 1 — does OECD's general reuse policy formally extend to AIM at all?**
Yes, established directly (§2.3), not by inference from a generic footer.

**Layer 2 — which OECD content category do `title`/`summary` fall into, if
they fall into a clean one at all: "Data" (extract/copy/adapt/distribute for
any purpose incl. commercial, attribution required, no date gate) or
"Written content" (CC BY 4.0 only if published 2024-07-01 or later, and only
if OECD-owned)?** AIM's own page groups `title`/`summary` alongside
`harm_type`/`severity`/`affected stakeholders`/`country` as one undifferentiated
"metadata" bundle attached to a structured event record — that reads far
closer to dataset fields ("Data") than to a discrete authored publication
(the "written content" list is *publications, working papers, journal
articles, policy papers, policy briefs, case studies, country notes* — none
of which "a two-sentence auto-generated incident abstract" resembles). If
forced to classify, Data is the better fit, and the Data clause is actually
the *more* permissive of the two (no date gate, "any purpose, even
commercial"), so a clean Layer-2 resolution alone would push toward (A).

**Layer 3 — the actual blocker: can OECD grant reuse rights over text an LLM
produced by processing three copyrighted third-party news articles, given
OECD did not write that text and a jurisdiction's copyright regime may not
even vest authorship in OECD (or anyone) for a purely machine output?** This
is where Layers 1–2 stop mattering. Neither the "Data" clause nor the
"Written content" clause can grant a right OECD does not hold. Two readings
compete, and neither is frivolous:

- **Reading for (A):** OECD operates AIM as a transformative aggregation
  product, wraps the whole service (Layer 1) in its own terms, and — like
  many news aggregators, wire-rewrite services, or a database compiler's own
  compilation right — is asserting normal reuse terms over its *own
  synthesized output*, distinct from the underlying raw news it doesn't
  claim to own. AIM's stated mission (an evidence base "to inform... policy
  discussions") and OECD's open-by-default posture both cut this way; a
  short, non-verbatim, three-source LLM digest is a plausible candidate for
  "OECD's own processed product."
- **Reading for (B):** the AIM-specific disclaimer (fact #5) exists on the
  *methodology* page, layered on top of and separate from the general
  terms — a page whose entire purpose is to explain how AIM's content
  pipeline works. That is exactly where an operator would place a carve-out
  if it knew its content-generation process (LLM summarization of scraped
  copyrighted news) creates residual third-party-rights exposure its general
  Data/Written-content policies weren't written to address. "Otherwise
  included in the AIM" is broad enough to sweep in text substantively
  derived from cited third-party sources, not only literal excerpts — and
  the very next disclaimer sentence ties AIM's substance directly to
  third-party outlets it has "no affiliation" with.

**I do not think either reading is unreasonable, and I want to be honest
that this is a genuinely closer call than AIAAIC's copyright analysis was.**
What resolves it for this project is not that reading (B) is clearly
correct — it is this project's own standing rule: *ambiguous terms are not
resolved in the project's favor; conservatism means claiming fewer rights,
not fewer facts* (`docs/SOURCE_LICENSES.md` header; restated in my own
operating brief). Layer 3 is genuinely ambiguous. Per that rule, it resolves
to **(B): the reduction is still required** — not because AIM's content is
established third-party news copy (it isn't — that hypothesis is now
disproven), but because its actual provenance (LLM output derived from
copyrighted third-party news, of uncertain and unresolved ownership) is a
different, and here still-disqualifying, category the project's conservative
default reaches independently.

**One supporting observation, stated as an inference, not a verified fact:**
the `evidences` strings quoted in fact #3 (analytical, evaluative sentences,
not excerpt-like) are consistent with `evidences` *also* being LLM output
from the same pipeline rather than raw scraped text — which would mean
almost none of what flows through AIM's `ng-state` JSON is literal
third-party prose at all. I have not verified this specifically for
`evidences` (only `title`/`summary`/`harm_type`/`severity`/`stakeholders`/`country`
are named in the quoted sentence), so I am not relying on it — but if true,
it removes the last practical argument for reading fact #5's disclaimer
narrowly ("only literal inclusions"), since there would be little literal
third-party text left to disclaim over, sharpening the reading-for-(B) case
in §3 rather than weakening it.

---

## 4. Outcome

**(B) — the `Redistribute-verbatim: NO` finding stands, on a corrected
rationale.** Criterion 8 in `docs/audits/PHASE1-EXIT-2026-07-30.md` is
**NOT MET as written**; BLOCKER A is not resolved by this finding. Scope and
effort follow in §5, as the brief specifically asked for under outcome (B).

This is not a rebuild-on-suspicion call: it rests on two new, dated,
primary-source (or primary-source-adjacent) facts not previously on the
board — AIM's explicit self-incorporation of the general terms (§2.3) and,
decisively, the LLM-generation mechanism (§2.4) — plus this project's
existing conservative-resolution rule applied to the genuine ambiguity those
facts leave in Layer 3.

## 5. Scope and effort for the reduction

**Rows:** the **3,667** rows already measured shipping verbatim OECD-derived
`description` text in `data/incidents.json`
(`docs/audits/PHASE1-EXIT-2026-07-30.md` BLOCKER A). I did not re-count this
myself (no Bash); red-reviewer should re-run whatever count produced 3,667
before treating it as current for a backfill plan.

**Fields:**
- **`description`** (`ingest_oecd_aim.py:208`, sourced 100% from `summary`,
  `:199`) — **in scope, must be reduced.**
- **`title`** (`:181`, `:252`, and reused verbatim as `references[0].title`
  at `:222`) — **flagged, not put in this reduction's mandatory scope.**
  It is generated by the identical LLM pipeline (§2.4), so it carries the
  identical Layer-3 question. But a short event-label is far less likely to
  carry protectable third-party expression than a multi-sentence digest, and
  this project already has a standing precedent for exactly this
  size/risk distinction: AIAAIC's own retained headline (§1.1, E15/D17) is
  tracked as a narrower, separately-open question rather than folded into
  the main reduction. I am treating OECD's `title` the same way —
  **tracked as a parallel open question, same posture as E15/D17, not
  blocking this reduction and not itself resolved here.**
- **`references[1:]` article titles** (`:227`, each article's own
  `art.get("title")`) — **out of scope, unaffected.** These are the
  underlying news articles' own headlines, kept as citations of the cited
  work by its own title — the exact pattern the user's 2026-07-29 ruling
  (D17) already found acceptable for AIAAIC. No new question here.
- **`affected`** (`:229-235`, from `body.get("company")`, a structured name
  list) — **out of scope**, low risk: a bare entity-name list is closer to
  fact than to narrative expression, and is plausibly OECD's own structured
  "Data" in the Layer-2 sense regardless of how Layer 3 resolves for
  free-text fields.
- **`attack_vector`/`owasp_llm`/`owasp_asi`/`severity`** — **out of scope**,
  already architecturally correct: `full_text` (`collect_text()`, `:143-156`,
  which includes `summary`/`evidences`) is used only as an ephemeral,
  in-memory classification signal and is never itself persisted — the exact
  pattern `ingest_aiid_snapshot.py` (§1.2a) already uses for AIID's
  CC-BY-SA-excluded `reports.text`. No change needed to this part.

**Reduced form — exact code-level requirement for pipeline-engineer:**

In `scripts/ingest_oecd_aim.py::normalize_body()` (currently `:199-210`),
replace

```python
summary = body.get("summary") or ""
if not summary:
    for art in body.get("articles") or []:
        ev = art.get("evidences") or []
        if isinstance(ev, list) and ev:
            summary = " ".join(e for e in ev if isinstance(e, str))[:1000]
            if summary:
                break
description = (summary or title).strip()
if len(description) < 20:
    description = (title + ". " + description).strip()
```

with an **originally-templated sentence built only from structural facts**
already available in `normalize_body()`'s own scope (`source_ids[0]`,
`date`/`year`, `affected`, `attack_vector`, `url`) — never from
`summary`/`evidences`. This codebase already has the right precedent to
copy, in the same repo, one function away:
`ingest_external.py::ingest_aiid_oecd_bridge()` (`:225-232`) builds exactly
this kind of original sentence — `f"Cross-listed in the AI Incident Database
(AIID) as incident #{aiid_id} and tracked by the OECD AI Incidents
Monitor..."` — from IDs and facts alone. `summary`/`evidences`/`full_text`
continue to feed `is_security_relevant()`/`map_taxonomy()`/the severity
heuristic exactly as today (untouched), just never written to output. Final
sentence wording is pipeline-engineer's call, not mine.

**Attribution — a separate requirement, owed regardless of how Layer 3
resolves for the narrative fields:** whatever structural facts continue to
ship (id, date, taxonomy tags, `affected`, AIID cross-reference ids) sit
squarely under OECD's general Data-reuse clause (Layer 2, §3), which is
conditioned on attribution in OECD's own specified format: *"OECD (year),
(dataset name), (data source) DOI or URL (accessed on (date))."* §1.5's
Action cell has called for a "Source: OECD AI Incidents and Hazards Monitor"
line since 2026-07-15/30 and it is still not implemented. Requirement: add
one attribution reference entry per OECD-sourced row (parallel to how
§2.3/§2.4's GHSA/OSV rows are handled — "Confirm the render layer credits...
per entry"), e.g. `{"title": "OECD (<year>), AI Incidents and Hazards
Monitor, <page-url> (accessed on <ingest-date>)", "url": "<page-url>",
"type": "citation"}`, or wherever this repo's render layer already
surfaces such citations for other sources.

**Backfill vs. forward-fix:** per D10's precedent (fix-forward, no history
rewrite — explicitly named in my brief), no past release/tag is altered.
But `union_with_existing()` (`:268-284`) merges by `source_id` with "fresh
wins on conflict" — meaning the 3,667+ rows already shipping verbatim text
in the *current working tree* will only get fixed as their sitemap entries
are naturally re-fetched. Given `DEFAULT_LIMIT = 3000` (newest-first) and a
weekly cadence, older rows could take a very long time to organically
refresh. **Recommendation (not a decision — the user/pipeline-engineer's
call): run a one-time `OECD_AIM_LIMIT=0` full re-ingest immediately after
the code fix lands**, to force every existing row's `description` to be
rebuilt before the next release cut, rather than leaving 3,667 verbatim rows
in the shipped corpus to fade out over many weekly cycles. Whether the
on-disk cache (`ingest/_cache/oecd_aim/`) is warm enough to make this a pure
reprocessing pass (no new network fetches) or requires materially new
fetching (subject to the board's own already-flagged A2 pacing/timeout
concern for a full-corpus OECD run) is a runtime question for
pipeline-engineer to size — I don't have that number.

**Verification requirement (Field-level delta rule, `CLAUDE.md`):** the
rollout must publish a full before/after delta on `description` (and
`title` only if a future decision brings it into scope) across all affected
rows, plus entry-count/ID-set unchanged (invariant 3) and confirmation that
`attack_vector`/`owasp_llm`/`owasp_asi`/`severity` outputs are byte-identical
before/after (the classification signal computation is untouched — only
what gets persisted as `description` changes).

**Exact checks for red-reviewer, all shell-based, named per my role:**
1. `curl` `https://oecd.ai/en/incidents-methodology` and `grep` for the
   exact string `This metadata is LLM-generated (OpenAI's o3-mini) from the
   top three articles of each event, selected from different news outlets.`
   — confirms §2.4, the single most load-bearing fact here, is not a
   WebFetch paraphrase.
2. Same page, `grep` for `Your use of the OECD AI incidents and hazards
   monitor` and `termsandconditions` — confirms §2.3.
3. `curl` (no-UA and browser-UA) against
   `https://www.oecd.org/en/about/terms-conditions.html`,
   `https://www.oecd.org/termsandconditions/`, and
   `https://www.oecd.org/en/about/oecd-open-by-default-policy.html` —
   confirm all three still 403, so fact 4's "not primary-source quotable"
   status is current before this file is next relied on.
4. After pipeline-engineer's fix lands: confirm 0 rows in
   `data/incidents.json` with a source-id matching `OECD-AIM-*` whose
   `description` text is a verbatim substring of (or identical to) the
   corresponding `summary` value in `ingest/oecd_aim_full_incidents.json` —
   this is the acceptance check for the reduction actually landing.

---

## 6. What this file does not claim

It does not claim OECD's own CC BY 4.0 general policy is unreal or
unreachable in general — the corroboration for it (§2.1) is consistent and
multiply sourced, just not primary-fetchable by any tool I have today. It
does not claim reading (A) in §3 is unreasonable — a good-faith counter-case
exists and is stated in full. It resolves the way it does because Layer 3 is
genuinely ambiguous and this project's own standing rule resolves genuine
ambiguity conservatively, not because the evidence points unambiguously to
(B). It does not resolve the `title` question — that is explicitly carried
forward as a parallel open item, same posture as AIAAIC's E15/D17. It does
not implement or backfill anything — those are requirements for
pipeline-engineer, named above, not actions taken here.
