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

## ⛔ §5 IS NOT ACCEPTED — RE-SCOPED TO WS4 PIPELINE-ENGINEER (user ruling, 2026-07-30)

**Do not implement from §5. It failed its gate twice and is retained only as
input to the task that replaces it.** §§1–4 — the licensing analysis and the
(A)/(B) verdict — are **accepted and merged**; red-reviewer confirmed them twice
(*"The analysis is right and I have now confirmed it twice"*). §5 is the
implementation spec, and it is superseded.

**Two gating defects stand unfixed in the text below:**

1. **§5.1 mechanism 1 is a no-op.** It claims *"no `merge_and_dedupe.py` code
   change needed at all"* and cites `quality_tier` as precedent. Both false: the
   entry reaching the classifiers is rebuilt from an explicit whitelist at
   `merge_and_dedupe.py:793-813` that contains **no `corpus` key**, so a `corpus`
   value set at ingest is **discarded**, `if not e.get("corpus")` is always true,
   and the relabel ships. `quality_tier` is absent from the same whitelist; its
   `:1440` guard exists for the **overrides file**, not ingest sources. A seed
   field costs **three** touchpoints (whitelist, use, strip — see `:1555-1560`,
   `additionalProperties:false`), not zero. **This is the dangerous kind of
   wrong: an implementer would choose mechanism 1 precisely because it is
   advertised as free.**
2. **The scope misses a second OECD ingest file.** `merge_and_dedupe.py:1336`
   globs **every** `ingest/*.json`. `ingest/oecd_aim_incidents.json` holds **86
   rows whose `source_id`s are entirely disjoint** from the 4,160 (0 shared),
   **all 86 reach `data/incidents.json`**, and **59 carry a verbatim
   `description`**. Nothing reads or writes it — orphaned since `edaefc92`
   (2026-05-13). **The reduction population is 3,726, not 3,667.** Both the
   specialist's and red-reviewer's earlier counts joined against the full file
   only and inherited the same blind spot.

**Why this was re-scoped rather than bounced a third time (user ruling):** *"the
licensing conclusion and its implementation are different claims verified by
different competencies."* Both bounces were facts about `merge_and_dedupe.py`'s
internals, specified by a WS0 docs specialist with no shell to execute or test
them. That is a **role mismatch, not a defect in the ruling** — the same lesson
as license-auditor delegating shell checks to red-reviewer, now applied at task
level.

**What survives §5 as binding input to the replacement task:** the `corpus`
cascade itself (77–150 rows, measured); the constraint that any persisted seed
must carry the **derived signal only, never the narrative** (a literal
`_aiaaic_seed_facts` mirror would defeat the reduction under a new field name —
the specialist caught this against both the foreman's and the gate's
instruction); the **local-transform** backfill mechanism, which needs no re-fetch
and reaches 100% of rows; and §5.5's owed disclosure fields.

## 5. Scope and effort for the reduction

**Revision note (BOUNCE #1, this section only — §§1–4 and the (A)/(B)
verdict are unchanged).** The gate's re-verification confirmed §§1–4 in full,
including that the o3-mini quote (§2.4) is not a paraphrase artifact
(byte-identical raw HTML, `curl`, apostrophe-style the only divergence). What
follows are five additions to *this section*: a real 77–150-row
corpus-relabelling defect in the plan as originally written, two evidentiary
additions that strengthen (not reopen) §3, a corrected re-ingest sizing, a
better backfill mechanism, and one owed-but-out-of-scope sub-item.

### 5.0 Two evidentiary additions to §3's Layer-3 argument (§4's verdict unchanged)

**The express non-grant clause — quoted here for the first time in this
project.** On the same raw-HTML page as fact #5 (§1, `oecd.ai/en/incidents-methodology`),
immediately adjacent to the disclaimer already quoted, the page continues:

> *"The OECD is not endorsed by, does not endorse, and is not affiliated with
> any of the holders of such rights, and as such, the OECD cannot and do not
> grant any rights to use or otherwise exploit these protected materials
> included herein."*

This does not by itself resolve Layer 3 — whether an LLM-generated summary
*is* "these protected materials" is still the open question — but it is a
materially stronger fact than an ownership footnote: it is OECD **expressly
declining to grant** rights over material it identifies as third-party-protected
and "included herein." §3's Reading-for-(B) bullet should be read as
reinforced by this clause, not merely by inference from the shorter
disclaimer sentence alone.

**The strongest form of the pro-(A) argument, developed fully, then answered.**
§3 as written states the pro-(A) case as an aggregator's-own-processed-product
argument but does not develop its strongest form, which is a copyrightability
argument, not an ownership one: **if the raw LLM output carries no copyright
at all** — a live position in at least the US Copyright Office's own guidance
on works lacking sufficient human authorship, and unsettled more broadly —
**then there is nothing for OECD to grant and, more importantly, nothing for
genai_incidents to infringe by copying the string itself**, however OECD's
own terms characterize it. Taken to its logical end, this argument would
moot Layer 3 entirely: no one's copyright, no one's claim.

**Why (B) still wins even against this strongest form:** the argument proves
too little, because it answers the wrong question. "No new copyright vests in
the LLM's output" does not mean "the output carries no one's protected
expression." An LLM summarizing three copyrighted news articles can still
reproduce those articles' *protected expression* — their distinctive
phrasing, framing, or the selection/arrangement of facts that constitutes the
articles' own expressive content — inside its output, in which case the
*articles'* copyright (which unquestionably exists and is held by the
originating news outlets, not OECD, not us) governs the output regardless of
whether the output itself is independently copyrightable by anyone. Whether
a *given* summary crosses that line is a substantial-similarity question this
project cannot answer at the corpus level without inspecting individual
summaries against their source articles — exactly the kind of fact-intensive
question this document's own header says is presumed method-suspect until
checked, not resolved in the project's favor by default. And the express
non-grant clause quoted above reads as OECD's own acknowledgment of
precisely this risk — it is a clean fit for "we may be redistributing
material derived from protected third-party expression and are not
purporting to clear it for you," and a poor fit for "we hold no rights here
because there's nothing to hold." **The strongest pro-(A) argument defeats a
narrower risk (OECD's own claim to the output) than the one that actually
governs redistribution (the source articles' claim, mediated through the
output) — so it does not change the outcome.** (B) stands.

### 5.1 Rows and fields

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
  CC-BY-SA-excluded `reports.text`. No change needed to this part. **Gate-verified,
  0 changes across all three candidate templates tried** — these four are
  genuinely safe, and the field this bullet-set originally omitted is the
  next one.
- **`corpus` — MISSED IN THE ORIGINAL DRAFT OF THIS FILE; IN SCOPE, gating.**
  `merge_and_dedupe.py::_classify_corpus()` (`:574-594`) computes `corpus`
  from `entry.get("description")` for any entry that isn't AIAAIC-origin
  (`_aiaaic_seed_text()`, `:534-571`, returns `None` for
  `description_source != "aiaaic"`, so OECD rows fall through to
  `desc_text = entry.get("description") or ""` at `:580` — the composed,
  about-to-be-reduced string). OECD rows carry no pre-set `corpus` today (0
  of 4,160), and `merge_and_dedupe.py:1442`'s `if not e.get("corpus"):
  e["corpus"] = _classify_corpus(e)` guard recomputes it from scratch on
  every build. **This is exactly the coupling the WS0-T3 cascade docstring
  (`:547-551`) names as having already "silently relabelled 372 AIAAIC
  entries" once** — it is live for OECD today, not theoretical, and the gate
  measured it directly: substituting three candidate reduced-description
  templates into the 3,829 OECD-tagged rows and re-running `_classify_corpus`
  moves **150 rows** (template mentioning "Incidents and Hazards Monitor",
  all `ai-harm`→`security`) or **81 rows** (77/4 split, either of two
  neutral/bare-facts templates). Because final template wording is
  delegated to pipeline-engineer (§5.2 below), **the exact count is not
  fixable by naming one number here — the requirement has to bind the
  mechanism, not a template choice.**

  **Recommendation: structural decoupling, not a one-time accepted delta.**
  A one-time delta is a legitimate *fallback* (see below) but leaves the
  defect class open — any later change to the description template (a typo
  fix, a tone edit) could silently move `corpus` again, for the same reason
  it did the first time. Two mechanisms achieve decoupling; either is
  acceptable, pipeline-engineer's call which:
  1. **Compute and persist `corpus` at ingest time**, in
     `ingest_oecd_aim.py::normalize_body()`, from the full `full_text` signal
     (`:143-156`) — the same signal `attack_vector`/`severity` already use —
     using the identical keyword classification `merge_and_dedupe.py`
     applies (`_SECURITY_KEYWORDS_FOR_CORPUS`/`_AI_HARM_KEYWORDS`, shared or
     duplicated). `merge_and_dedupe.py:1442`'s existing "respect an explicit
     value if the source already declares one" guard then takes effect
     unmodified — no `merge_and_dedupe.py` code change needed at all. This
     is the same mechanism `quality_tier` already relies on for sources that
     set it themselves.
  2. **Add an OECD branch to the `_aiaaic_seed_text()` decoupling pattern**
     (`:534-571`), gated on the OECD equivalent of `description_source`.
     **Critical difference from the AIAAIC precedent, stated explicitly so
     it isn't missed:** AIAAIC's seed fields (`aiaaic_seed_facts`,
     `aiaaic_ethical_tags`) are safe to persist because they are categorical
     labels, not prose. **For OECD, the text that currently drives
     classification *is* the LLM-generated narrative this reduction exists
     to stop shipping.** A seed field that persists that same text under a
     new key (e.g. a hidden `oecd_seed_text`) would defeat the reduction —
     it would still be redistributing the narrative, just unlabeled. If this
     mechanism is chosen, the persisted seed must be the **derived signal
     only** (e.g. the specific `_SECURITY_KEYWORDS_FOR_CORPUS`/`_AI_HARM_KEYWORDS`
     terms actually matched, or a plain `security`/`ai-harm` boolean/enum),
     never the narrative text that was matched against.

  **Fallback, if decoupling is deferred:** a one-time, enumerated,
  justified `corpus` delta — reported per the Field-level delta rule
  (`CLAUDE.md`) with the actual row count and both-direction breakdown
  (this section's 150 or 81/4 figures are the gate's dry-run estimates
  against candidate templates, not the number the shipped template will
  produce) — **and a note in the PR that any future OECD description-wording
  change must re-run this delta check**, since the defect class stays open
  under this fallback.

### 5.2 Reduced form — exact code-level requirement for pipeline-engineer

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

### 5.3 Attribution — a separate requirement, owed regardless of how Layer 3 resolves for the narrative fields

Whatever structural facts continue to ship (id, date, taxonomy tags,
`affected`, AIID cross-reference ids) sit squarely under OECD's general
Data-reuse clause (Layer 2, §3), which is conditioned on attribution in
OECD's own specified format: *"OECD (year), (dataset name), (data source)
DOI or URL (accessed on (date))."* §1.5's Action cell has called for a
"Source: OECD AI Incidents and Hazards Monitor" line since 2026-07-15/30 and
it is still not implemented. Requirement: add one attribution reference
entry per OECD-sourced row (parallel to how §2.3/§2.4's GHSA/OSV rows are
handled — "Confirm the render layer credits... per entry"), e.g. `{"title":
"OECD (<year>), AI Incidents and Hazards Monitor, <page-url> (accessed on
<ingest-date>)", "url": "<page-url>", "type": "citation"}`, or wherever this
repo's render layer already surfaces such citations for other sources.

### 5.4 Backfill vs. forward-fix — revised, with corrected sizing and a better mechanism

**Sizing correction (foreman code-verified, treated as established per
protocol).** My original draft assumed `DEFAULT_LIMIT = 3000` was close to
the full corpus and that `OECD_AIM_LIMIT=0` was mainly a cache question. Both
were wrong in ways that matter for feasibility, not just degree:
- The live sitemap has **10,000** matching incident URLs (`curl -L` →
  10,001 `<loc>` entries, 10,000 passing the ingest's own `/en/incidents/<id>`
  filter), not ~3,000.
- `ingest/_cache/oecd_aim/` is **empty and gitignored** — a full re-ingest is
  a cold, fully-networked pass, not a cache replay.
- At `ingest/common.py:106`'s `DEFAULT_MIN_INTERVAL = 1.0` (confirmed present
  in this codebase), shared across the 10-worker pool, a 10,000-page pass has
  a **~167-minute floor** — against `auto-refresh.yml`'s 60-minute timeout.
  **`OECD_AIM_LIMIT=0` as a CI job (including via `workflow_dispatch`) is
  infeasible; it is feasible only as a one-off run outside CI.**
- Under the current `DEFAULT_LIMIT = 3000`, newest-first: rows ranked
  **3,001–10,000 are not merely slow to refresh, they are never refreshed at
  all** under the ingest's normal weekly operation — my original "could take
  a very long time" undersold this; it is an indefinite exclusion, not a
  delay.
- **40 rows are frozen regardless of any code change or `OECD_AIM_LIMIT`
  setting.** `ingest/oecd_aim_full_incidents.json` carries 4,160 OECD URLs;
  today's sitemap carries 4,120 matching URLs for the same window — **40
  have aged out of the sitemap entirely** and are preserved only by
  `union_with_existing()`'s existing-entry-survives behavior (`:268-284`).
  They can never re-enter `normalize_body()` through the normal fetch path
  again, at any limit setting, because they no longer appear in the source
  the ingest reads URLs from.

**Better mechanism, superseding the `OECD_AIM_LIMIT=0` recommendation in the
original draft of this section: a one-off local transform, not a re-ingest.**
Every field the new `description` template needs (§5.2 — `source_id`,
`date`, `affected`, `attack_vector`, `url`) is **already present on every
row currently in `ingest/oecd_aim_full_incidents.json`**, including the 40
aged-out ones — the reduction doesn't need new content, only a rewrite of
one already-populated field using other already-populated fields on the same
row. A standalone migration script that reads the existing committed file,
and for each row:
1. captures the corpus-classification seed from the row's **current**
   `description` value (still the pre-reduction summary text at the moment
   the script runs) using `merge_and_dedupe.py`'s own keyword lists, and
   persists it per §5.1's decoupling requirement, **then**
2. overwrites `description` with the new structural template,

reaches **100% of currently-shipping OECD rows, including all 40 aged-out
ones, at zero network cost and no CI-timeout exposure** — strictly better
than `OECD_AIM_LIMIT=0` on every axis (completeness, cost, feasibility). The
normal ingest-time code fix (§5.2) still lands, for rows added in future
runs, which do need to compute the seed fresh from a real fetch since they
have no prior committed `description` to read it from. **`OECD_AIM_LIMIT=0`
is not needed for the licensing backfill at all** under this mechanism; if
pipeline-engineer separately wants to force-refresh AIM content for
freshness reasons unrelated to this reduction, that's a distinct
maintenance decision, now correctly sized (~167 min, one-off, outside CI)
rather than assumed cheap.

### 5.5 Owed, but explicitly out of scope for this reduction

All **3,829** OECD-tagged rows carry `description_source: None`,
`description_provenance: None`, and **`content_license: None`** — the third
parallel to the D11/E16 AIAAIC row-level marker mechanism. **This is owed
independent of the (A)/(B) verdict — it stands under (A) as much as under
(B)** — and is named here only because §5 already extends past pure
licensing into an attribution requirement (§5.3), so a short pointer belongs
here too. **Not scoped or designed here** — marking mechanism, field values,
and rollout are a separate task, not decided by this bounce.

### 5.6 Verification requirement (Field-level delta rule, `CLAUDE.md`)

The rollout must publish a full before/after delta on `description`,
**`corpus`** (target: 0 unintended moves, given §5.1's decoupling
requirement — if the fallback path is used instead, the actual delta must be
enumerated and justified, not asserted as 0), and `title` only if a future
decision brings it into scope — across all affected rows, plus
entry-count/ID-set unchanged (invariant 3) and confirmation that
`attack_vector`/`owasp_llm`/`owasp_asi`/`severity` outputs remain
byte-identical before/after (unaffected by this change; the classification
signal computation itself is untouched).

**Exact checks for red-reviewer, all shell-based, named per my role:**
1. `curl` `https://oecd.ai/en/incidents-methodology` and `grep` for the
   exact string `This metadata is LLM-generated (OpenAI's o3-mini) from the
   top three articles of each event, selected from different news outlets.`
   — confirms §2.4, the single most load-bearing fact here, is not a
   WebFetch paraphrase. **(Already independently re-derived by the gate for
   BOUNCE #1 — byte-identical, apostrophe-style the only divergence — this
   check can be treated as closed unless the page changes.)**
2. Same page, `grep` for `Your use of the OECD AI incidents and hazards
   monitor`, `termsandconditions`, and — new this bounce — `the OECD cannot
   and do not grant any rights to use or otherwise exploit these protected
   materials included herein` — confirms §2.3 and the §5.0 non-grant quote.
3. `curl` (no-UA and browser-UA) against
   `https://www.oecd.org/en/about/terms-conditions.html`,
   `https://www.oecd.org/termsandconditions/`, and
   `https://www.oecd.org/en/about/oecd-open-by-default-policy.html` —
   confirm all three still 403. **(Already re-confirmed by the gate for
   BOUNCE #1.)**
4. `curl -L https://oecd.ai/sitemaps/incident-monitor-sitemap.xml` and count
   `<loc>` entries matching `/en/incidents/<id>` — confirm the 10,000/4,120
   figures in §5.4 before sizing any re-ingest or the aged-out-row count.
5. After pipeline-engineer's fix lands: confirm 0 rows in
   `data/incidents.json` with a source-id matching `OECD-AIM-*` whose
   `description` text is a verbatim substring of (or identical to) the
   corresponding pre-fix `summary`/`description` value — the acceptance
   check for the reduction actually landing.
6. Same post-fix pass: confirm `corpus` is unchanged for all OECD-tagged
   rows relative to a pre-fix snapshot (0 moves if decoupling per §5.1 was
   implemented; otherwise, confirm the delta matches whatever was enumerated
   and justified under the §5.1 fallback).

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
