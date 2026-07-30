# E23 Ruling — Does AIID-Derived Content Need the Row-Level Marker AIAAIC Has?

**Task:** E23 (second half — the ruling on pipeline-engineer's fact-finding
measurement). **Author:** WS0 license-auditor. **Input:**
`docs/audits/E23-aiid-scope-measurement-2026-07-30.md` (pipeline-engineer,
`main` @ `dba4adc6`, read in full — every count and mechanism below is
taken from that file, not re-derived and not second-guessed). Also relies
on, without re-deriving: `docs/audits/WS0-E13-database-right-2026-07-18.md`
(E13, the AIAAIC database-right precedent, amended 2026-07-27) and
`docs/audits/E16-title-similarity-review-2026-07-29.md` (E16/E15/D17, the
AIAAIC headline-copyright precedent).

---

**Revision log (2026-07-30, BOUNCE #1 — six prose defects; outcome
CONFIRMED unchanged by the gate):** this document originally characterized
AIID's maker as "a California nonprofit corporation" and grounded Layer 1's
copyright reasoning in AIID's Terms-of-Use choice-of-law clause; neither
survives review and both are corrected below. The corrected finding is
narrower but no weaker: AIID's maker is **US-situated** (a specific state
of incorporation is not established in AIID's own materials and, per §3,
is not material to the outcome), and Layer 1's connecting factor is that
**situs**, matching E13's own method exactly rather than a variant of it —
a ToS choice-of-law clause governs contract disputes, not copyright
subsistence, and in any case cannot itself supply a copyright rule (US
copyright is exclusively federal). Two supporting citations are corrected
to the right source page (the EIN is on `/about/`, not `/terms-of-use/`,
where this document originally cited it) and one is re-characterized (the
Sacramento address is a DMCA agent address under 17 U.S.C. 512, not a
stated registered office). A reinforcing qualitative claim that AIID's
titles read as "plain factual labels" is retracted — full-corpus
measurement contradicts it (median 13 words, above *Infopaq*'s 11-word
bar; 925/1,548 titles carry a hedging qualifier) — and Layer 1 now rests on
the situs finding alone. The Attribution finding (§4) is corrected from an
n=2 sample ("every row") to the measured population (1,463–1,464 of 1,465,
with the two exceptions named and explained rather than smoothed over).
**None of these corrections changes the outcome.** The gate independently
reproduced the empirical claims this ruling depends on and found the
outcome sound; what follows is the corrected text.

---

## Outcome

**(2) — MARKING NOT REQUIRED for the population that ships, and the
asymmetry with AIAAIC is JUSTIFIED — but stated with a (3)-style tripwire
for a second, currently-dormant population that does not ship today.**

This is not a coin toss resolved cautiously in the project's favor. Two
independent legal reasons — one turning on U.S. copyright law's categorical
short-phrase exclusion, one turning on the exact UK/EU database-right
maker-qualification gate E13 §4.1 already built for this project's own
qualification — both point the same way, for the same underlying fact:
**AIID's maker is a U.S.-situated entity, not a UK/EU one.** That single
fact is why AIID and AIAAIC are not "the same posture,"
despite AIID's license being the confirmed one and AIAAIC's being open.
`NOTICE-DATA` and `.reuse/dep5` are wrong to describe them as parallel, and
must stop (see "What NOTICE-DATA / .reuse/dep5 owe," below).

A second population — 63 hand-curated rows in `ingest/aiid_incidents.json`
plus 1,457 AIRI-Navigator rows sharing AIID's `AIID-<n>` source-ID
convention — carries real, uncleared risk (paraphrased titles, narrative
descriptions of unverified provenance, possibly touching AIID's
license-excluded `reports.text`) but **does not reach the shipped corpus**,
per E23 §3's two-way-verified merge-precedence finding. That population is
**not ruled clean** — it is ruled *out of scope today*, with an explicit
tripwire: if it ever starts shipping, this ruling does not carry over to it
and a fresh review is required before it ships. See "The tripwire," below.

---

## 1. The fact that decides this, verified independently of the brief and of E23

Neither the brief nor E23 asked where AIID's own maker is domiciled — E13's
UK/EU database-right analysis for AIAAIC turned heavily on AIAAIC being
UK-situated, and the brief's framing implicitly carried that assumption
over to AIID by calling the two exposures "the same class." I checked AIID's
own Terms of Use and About page directly (`https://incidentdatabase.ai/terms-of-use/`,
the same page `docs/SOURCE_LICENSES.md` §1.2 already quotes for the CC-BY-SA
grant itself, and `https://incidentdatabase.ai/about/`) rather than assume
the parallel holds.

**Method note, per this file's own standing rule — and a correction on this
pass.** This was a WebFetch read, not a raw `curl`+`grep` of the HTML — the
same tool this project's own standing rule flags as having produced false
paraphrases twice before. On red-reviewer's raw-HTML re-check: the
governing-law clause held exactly as originally quoted (verbatim, under a
"Jurisdiction" heading). Two other citations did not survive unchanged —
the EIN (88-1046583) is stated on **`/about/`**, not `/terms-of-use/`,
where this document originally cited it (my probe checked the wrong page);
and the Sacramento address on `/terms-of-use/` is the site's **designated
DMCA Copyright Agent address under 17 U.S.C. 512** — *"RAIC's designated
Copyright Agent … is: DMCA Agent, Responsible AI Collaborative, Inc., 2108
N St N, Sacramento, CA 95816"* — not a stated corporate registered office,
which this document originally implied by calling it "registered at."
**No page on either domain states a state of incorporation**, and there is
no basis in AIID's own materials for the "California corporation"
characterization this document originally used — retracted below. **Exact
check for red-reviewer, corrected to the right page for each fact:**
`curl -sL https://incidentdatabase.ai/about/ | grep -i -E "88-1046583|Form
990"` for the EIN/tax-exempt fact; `curl -sL
https://incidentdatabase.ai/terms-of-use/ | grep -i -E "governed by the
laws of the state of California|Los Angeles County|DMCA Agent"` for the
governing-law/venue/agent-address facts.

**What AIID's own pages state, now correctly attributed:**
- **Entity name:** "Responsible AI Collaborative, Inc." (both pages).
- **US tax-exempt status:** an EIN (**88-1046583**) and a reference to a
  Form 990 filing, stated on **`/about/`** — corroborated by `WebSearch`'s
  independent "IRS ruling in 2023" finding.
- **Governing law** (`/terms-of-use/`, "Jurisdiction" heading, confirmed
  verbatim on raw-HTML re-check): *"the Agreement and any access to or use
  of our Site will be governed by the laws of the state of California,
  U.S.A., excluding its conflict of law provisions."*
- **Venue** (`/terms-of-use/`): the state and federal courts of **Los
  Angeles County, California**; arbitration also sited in Los Angeles.
- **DMCA agent address** (`/terms-of-use/`): the Sacramento address quoted
  above — a notice address under 17 U.S.C. 512, not a registered office.
- **Not stated anywhere on either page: a state of incorporation.**

**What this does and does not establish.** It establishes AIID's maker is
**US-situated** — principal place of business, venue, and arbitration all
in Los Angeles, California; US federal tax-exempt status; a
California/U.S.-law-selecting Terms of Use — and not UK- or EEA-situated by
any measure available. It does **not** establish a specific state of
incorporation, and — per §3 below — **that gap is not material**: reg
18(2)'s UK-nexus test and Art 11's EEA-nexus test fail identically for a
body whose principal place of business, venue, and tax domicile are all in
the United States, regardless of which particular US state issued its
certificate of incorporation.

This is a materially stronger primary-source basis than E13 had for
AIAAIC's own domicile — E13 §1 explicitly could not determine AIAAIC's
"precise legal entity/registration" and worked from an unconfirmed
assumption ("the E13 brief states 'AIAAIC is UK-based' and I have not found
anything contradicting that"). Here, AIID's own pages name the exact
entity, its US tax-exempt status, and its principal place of business/venue
— a firmer footing than AIAAIC's even without a stated incorporation state.

---

## 2. Layer 1 — Copyright over the one piece of AIID's own text that ships

**What actually ships, per E23 §2a/§3/§4:** on the ~1,463 corpus rows where
AIID content survives the merge (path (a), `ingest/aiid_full.json`), the
`title` field is AIID's own text, verbatim, by design — the only field that
is. `description` is **0/1,548** deviation from an always-original template
that never persists AIID's own prose (E23 §2a); `references[].title` is a
generic citation label, not AIID's own wording (unlike AIAAIC's
`references[0].title`, which E16 found independently carries AIAAIC's
headline on ≥31/47 sampled rows — AIID has no equivalent hidden-verbatim
field, confirmed by full-file scan, not sampling).

**The connecting factor is situs, not a contract clause — corrected on this
pass.** This document originally grounded the choice of governing law in
AIID's Terms-of-Use choice-of-law clause itself. That does not hold, for
two independent reasons: **(a)** a ToS choice-of-law clause governs
disputes over site use, not copyright subsistence — under Berne Art 5(2),
copyright subsistence is governed by the law of the country where
protection is claimed, a different question the clause was never written
to answer; and **(b)** the clause as quoted selects *"the laws of the state
of California"* specifically, and state law cannot supply a copyright rule
at all — US copyright is exclusively federal, and 17 U.S.C. 301 preempts
equivalent state-law rights. A state choice-of-law clause cannot be the
thing that imports Circular 33.

**The correct connecting factor, applying E13 §5.1 item 8's own method
rather than a contract clause:** E13's method for AIAAIC was never "AIAAIC's
contract selects UK law" — it was *"AIAAIC is UK-situated... this file
already treats UK/EU law as the governing regime... the same choice of
governing law applies to the copyright question, since it concerns the same
UK-situated rights-holder's same content."* **The operative fact is the
rights-holder's own situs, not a clause in its terms of service.** Applying
that to AIID: per §1 above, AIID's maker is US-situated (principal place of
business, venue, and arbitration in Los Angeles, California; US federal
tax-exempt status). That situs is what puts U.S. copyright law in play for
the same content-ownership question — the Terms of Use's own California
choice-of-law clause is retained only as **corroborating evidence of that
situs**, not as the operative choice-of-law rule.

U.S. Copyright Office Circular 33 ("Works Not Protected by Copyright") /
37 C.F.R. 202.1(a) categorically excludes **"titles, names, short phrases,
and slogans"** from copyright protection — a bright-line rule, not a
case-by-case "author's-own-intellectual-creation" test. This is the exact
rule AIAAIC's headline question (E15/D17) could **not** invoke, because
AIAAIC is UK-situated and UK/EU law (*Infopaq*, *Meltwater*) has no
equivalent categorical carve-out — which is precisely why AIAAIC's headline
question had to go to counsel rather than resolve in-house. For AIID, the
categorical U.S. rule applies directly and disposes of the question: **a
bare AIID `title` field carries no protectable expression under the law of
AIID's own situs.**

**A reinforcing qualitative claim this document originally made does not
survive full-corpus measurement, and is retracted rather than kept as a
soft addition.** The original text claimed AIID's titles read as "plain
subject-verb-object incident labels," citing two of E23's own examples.
Measured across all 1,548 titles in `aiid_full.json` (red-reviewer,
2026-07-30): mean length is **95 characters / 12.9 words**, median **13
words** — above the 11-word extract *Infopaq* itself held capable of
protection — **925 of 1,548** contain a hedging qualifier
(Allegedly/Reportedly/Purported/Apparently) and **340** contain a quoted
phrase. The corpus contains titles like *"Google Gemini Reportedly
Reinforced Delusions, Allegedly Contributing to Florida User's Near-Harm
Episode and Suicide"* — edited, hedged, and structured, not a bare label.
The two examples originally cited here (9 and 6 words respectively) are
real but unrepresentative of the population. **On content alone, AIID's
titles are not demonstrably less editorial than AIAAIC's**, and this
document no longer claims otherwise. **Layer 1's conclusion rests on the
situs finding alone, not on any claim about the qualitative character of
AIID's titles.**

**Consistency with the AIAAIC precedent (D2/D17), as the brief asked me to
weigh — and this survives the retraction above.** This is not a departure
from how the project treats retained titles — it is the same standard,
applied to different facts, yielding a different result for a principled,
stated reason: **situs**. AIAAIC's headline question stayed open because
UK/EU law — the law of AIAAIC's own situs — has no categorical
short-phrase exclusion. AIID's headline question resolves because U.S.
law — the law of AIID's own situs — does. The distinction is not, and does
not need to be, that AIID's content is less editorial than AIAAIC's; on the
measurement above it plausibly is not. The two retained-headline situations
are treated differently for a real, stated jurisdictional reason, not an
unexplained split, and that reason holds on the situs finding by itself.

---

## 3. Layer 2 — CC BY-SA §4 / sui generis database right

E13 §4.1 already built the exact tool this layer needs, for a symmetric
question: does a maker who is not a UK national/resident and not
UK/EEA-incorporated hold a UK or EU sui generis database right at all? E13
applied that test to **genai_incidents itself** (finding: no, on the
confirmed fact that genai_incidents' sole maker is an individual habitually
resident in Canada) and found the answer is a **threshold gate**, not a
factor to weigh against investment: *"Database right does not subsist in a
database unless... its maker was"* one of the qualifying UK/EEA persons
(reg 18(1), SI 1997/3032, as amended; Directive 96/9/EC Art 11's parallel
EEA-nationality test for the EU right). A database can reflect enormous
investment and still hold **no** right if its maker fails qualification.

**Applying the identical test to AIID's maker, not genai_incidents' own —
this is the other side of the same gate:**

- Reg 18(1)(a) (individual limb): does not apply — the maker is a
  corporation, not an individual.
- Reg 18(1)(b)/(2) (corporate limb): requires incorporation under UK law
  **and** either UK central administration/principal place of business, or
  a UK registered office linked to the UK economy. Responsible AI
  Collaborative, Inc. is **US-situated** — principal place of business,
  venue, and arbitration all in Los Angeles, California, per its own Terms
  of Use, with US federal tax-exempt status (EIN 88-1046583, `/about/`) —
  with no stated UK central administration, principal place of business, or
  registered office. None of reg 18(2)'s UK-nexus conditions are met.
- Directive 96/9/EC Art 11 (parallel EU-law test): requires EEA
  nationality/incorporation — also not met by a US-situated entity.

**A specific state of incorporation is not established in AIID's own
materials (§1), and this analysis does not need one:** reg 18(2)'s UK-nexus
test and Art 11's EEA-nexus test fail identically for a body whose
principal place of business, venue, and tax domicile are all in the United
States, regardless of which particular US state issued its certificate of
incorporation. Nothing below turns on that unestablished fact.

**Result: AIID's maker fails the UK and EU maker-qualification gates,
exactly as genai_incidents' own maker did in E13 §4.1 — except here it is
AIID, not us, on the failing side of the gate.** Per reg 18(1)'s own
operative language (a threshold, not a weight), **no UK or EU sui generis
database right subsists in AIID's `incidents`/`classifications` collections
at all, regardless of how much obtaining/verifying/presenting investment
AIID has put into them.** This is a stronger, cleaner conclusion than
AIAAIC's: E13 §1 found AIAAIC's own database right *plausibly subsists*
(UK maker, investment pattern matching *BHB*'s protected fact pattern) and
never closed that question — it remains open, pending counsel, because
AIAAIC's UK situs makes the qualification gate a real question rather than
a dispositive one. For AIID, the same gate closes the question outright.

**Consequence for CC BY-SA §4.** §4(a)'s extended grant and §4(c)'s
ShareAlike condition both operate **only** "where the Licensor holds Sui
Generis Database Rights in Licensed Material" (§4's own opening words, per
E13 §4's verbatim transcription of the legal code). If AIID holds no such
right, §4 has no subject-matter of AIID's to attach to — not a weak case
for attaching, the same "no database right, no clause to fire" logic E13
§4.1 already used for genai_incidents' own side of an identical gate.

**One more fact worth naming, though not load-bearing given the above:**
the United States has no sui generis database right of its own — database/
compilation protection in the U.S. runs through ordinary copyright
originality (*Feist Publications, Inc. v. Rural Telephone Service Co.*,
499 U.S. 340 (1991)), the same structural point E13 §4.1 already made about
Canada (via *CCH Canadian*) to close genai_incidents' own qualification
question. So even AIID's *home* jurisdiction would not hand it an
equivalent right to fall back on. There is, on the facts available, no
jurisdiction in play here under which a database right protects AIID's
`incidents`/`classifications` collections against this extraction.

**Net effect on Layer 2:** unlike AIAAIC, where the worst case settles at
§4(c)→§3(a) row-level ShareAlike on AIAAIC-derived content (E13's operative,
still-open finding), **AIID's database-right exposure does not reach even
that row-level worst case — it does not attach at all**, because the right
it would need to attach through does not subsist for this maker in the
first place.

---

## 4. Layer 3 — Attribution

The brief is right that CC BY-SA's attribution condition (§3(a)) is, in
principle, independent of whether ShareAlike bites, and right to flag that
"compatible-but-unattributed" is a real failure mode (E21 §5 found exactly
that for OECD — no attribution string existed anywhere in that ingest).
**That failure mode is not present here, on either the legal or the
practical question:**

- **Legally:** §3(a)'s attribution condition attaches when "You exercise
  the Licensed Rights" (§2's grant to Copyright and Similar Rights). Where,
  per Layers 1–2, no protectable copyright or database right actually
  covers the bare `title` field being copied, no license from AIID was
  needed to copy it, and §3(a) is not compulsorily triggered by that
  specific field — the same structural point that already lets D2 keep
  AIAAIC's bare categorical facts (`system`/`technology`/`sector`/
  `jurisdiction`) without a ShareAlike/attribution obligation attaching to
  those fields specifically.
- **Practically, and this is what actually matters for a reader:**
  attribution is present anyway, and is arguably more thorough per-row than
  AIAAIC's was before its marker existed. **Originally verified on two
  sampled rows only and overstated as "every row" — corrected here to the
  measured population** (red-reviewer, all 1,465 `aiid_id`-bearing rows):
  **1,463 of 1,465** name AIID in a full-sentence `description` (**"AI
  Incident Database (AIID) entry #{id}: {title}. ... See the linked AIID
  entry for full narrative, sourcing, and classification"**); **1,464 of
  1,465** carry a working citation link somewhere in `references`; **1,463
  of 1,465** carry it at `references[0]` specifically.
  **The two exceptions are not gaps, and are worth naming individually
  because they clarify the actual rule rather than just excusing it:**
  `INC-00437` (`aiid_id` 1574) carries no AIID attribution anywhere because
  it is **absent from `aiid_full.json` entirely** — its shipped content is
  OECD-AIM-derived, not AIID's (the same row E23 §4 already names as one of
  the two exceptions to the 1,463-row template match). `INC-08183`
  (`aiid_id` 898) carries its citation link at `references[3]`, not `[0]`,
  because its AIID title was superseded by another source's content.
  **Neither row ships any AIID-authored text, so neither owes AIID
  attribution** — a stronger, more precise statement than "every row," not
  a weaker one.
  **The general rule, made explicit rather than left implicit:**
  attribution is owed, and present, on every row that ships AIID's own
  text; rows carrying only an `aiid_id`/AIID source-ID as a bare
  cross-reference, with no AIID text actually shipping, are a different
  category and are not measured against this obligation at all.
  `README.md:223` additionally names "AI Incident Database (AIID)" with
  links to both `incidentdatabase.ai` and the GitHub repo at the
  collection level. `NOTICE-DATA:92-107` and `.reuse/dep5:35-42` already
  name AIID's CC BY-SA licensing at the document level. The finding stands
  as "already adequate" on the corrected numbers — not a gap to route.

---

## 5. The tripwire — the population this ruling does NOT clear

E23 §3 establishes, two ways (empirically and by code-level mechanism
read), that the 63 hand-curated rows in `ingest/aiid_incidents.json` and the
1,457 AIRI-Navigator rows sharing AIID's `AIID-<n>` source-ID convention
**never reach the shipped corpus** — their own `title`/`description`/
`references[0]` are silently superseded because `aiid_full.json` sorts
first alphabetically and wins every dedup collision, an artifact of file
naming and merge order, not a designed compliance guarantee. That
population carries real, uncleared risk this ruling does not resolve:
paraphrased (not verbatim) titles; narrative `description` text 142–348
characters long (well past Circular 33's "short phrase" territory even
under the favorable governing-law analysis above, if it were ever to ship);
and, per E23 §2b/§7, **genuinely unverifiable provenance** — nothing
committed in this repository pins AIID's raw `incidents.description` or the
license-excluded `reports.text` to check that 63-row population against.

**This ruling's "not required" conclusion in §§2–4 applies to the
~1,463-row population that actually ships (path (a)) and does not extend
to this second population, because the reasons it doesn't need marking are
different in kind, not just degree** — path (a)'s title is short,
plausibly-AIID's-own, and legally unprotectable under AIID's own governing
law; the 63-row population's descriptions are long, of unknown authorship,
and were never tested against either standard.

**Tripwire, stated the way E20's CSET ruling stated its own:** if any
future pipeline, dedup, or merge-order change ever causes
`ingest/aiid_incidents.json`'s own `title`/`description` text, or AIRI
Navigator's own composed `AIID-<n>`-tagged text, to start reaching
`data/incidents.json` (e.g., a fix to alphabetical glob ordering, an
extension of `merge_into`'s allow-list to cover `title`/`description`, or a
change to which file "wins" a source-ID collision), **this ruling does not
carry over automatically — that population REOPENS as needing its own
review before it ships**, and the specific open question (does its
narrative text echo AIID's licensed `incidents.description`, the excluded
`reports.text`, or independent synthesis — E23 §2b, unresolved) must be
answered first, not treated as cleared by this document.

---

## 6. What the v2.9.0 release notice must say

`docs/audits/PHASE1-EXIT-2026-07-30.md`'s draft supersession notice
currently carries a scope caveat: *"AIID-derived rows carry no
`content_license` marker in this release either, and whether they require
one is an open question under review."* **That is no longer accurate — it
is answered, not open.** The notice is owed a replacement statement to this
effect: AIID-derived rows were separately reviewed (E23 measurement +
this ruling) and found not to require a row-level marker for the content
that actually ships, because (a) the only AIID-authored text retained is a
bare title, not protectable expression under U.S. copyright law — the law
of AIID's own situs — and (b) AIID's maker does not qualify for a UK or EU
sui generis database right in the first place. This is a *more* reassuring
statement than the current hedge, not a less reassuring one, and should be
stated plainly rather than left as a caveat — while still naming the
tripwire in §5 above, so a future reader who extends the AIID ingest knows
the boundary of what was cleared. **I am not drafting the literal notice
text** (out of my lane per the brief); this is the exact content the
foreman should route to whoever owns that file for the release.

## What NOTICE-DATA / .reuse/dep5 owe

Both currently state (verified by direct read, 2026-07-30):
- `NOTICE-DATA:104-106`: *"Unlike AIAAIC's copyright share-alike question,
  which decision D2 disposes of, AIID's CC-BY-SA share-alike exposure and a
  parallel EU/UK sui generis database-right question remain OPEN and are
  NOT resolved by this handling — flagged the same way as AIAAIC's E13
  finding."*
- `.reuse/dep5:39-40`: *"but AIID's CC-BY-SA share-alike and a parallel
  database-right question remain an open, unresolved item, same posture as
  AIAAIC's E13 finding."*

**Both sentences are now false and must be replaced, not merely softened.**
They are owed a statement that: (1) AIID's content-licensing question is
**resolved**, not open, for the population that ships; (2) the reason it
resolves favorably is AIID's maker being U.S.-situated (Circular 33's
categorical short-phrase exclusion; no UK/EU database-right qualification)
— the *opposite* posture from AIAAIC's still-open UK-situated question, not
the same one; (3) the resolution does **not** extend to
`ingest/aiid_incidents.json`'s hand-curated content or AIRI Navigator's own
AIID-cross-referenced text, which remain unreviewed and are kept out of the
shipped corpus only by current merge mechanics — the tripwire from §5
above belongs in this framing too, since NOTICE-DATA/dep5 are exactly the
kind of durable, easily-stale surface the working-agreement's
field-level-delta and committed-artifact rules exist to keep honest. I am
not drafting the literal replacement text for either file (out of my lane
per the brief); this is the exact content owed.

---

## 7. `docs/SOURCE_LICENSES.md` §1.2a — amended directly (my file)

Amended in this same change (see the diff): §1.2a's "Relicense-compatible"
and "Action" cells, which previously read "OPEN ITEM, same posture as
AIAAIC's E13 database-right question" and "content-licensing question
flagged open, not closed," now record this ruling's resolution, point to
this file, and state the §5 tripwire explicitly. The "Summary of outcomes
requiring escalation" table's AIID row and its surrounding closing
paragraph are updated the same way CSET-AIID's entry was updated after E20
— from "open, pending" to "resolved, with a named reopen condition" — and
the pending-outreach count implications are noted (AIID's outreach, sent
2026-07-27 per §1.4/§1.2a's outreach history, was asking the *transitive
AIRI-wrapper* question, not this one; it remains separately open and
unaffected by this ruling — I have not touched that).

---

## 8. What this brief did not anticipate

- **AIID's maker domicile was never established anywhere on this board
  before this ruling**, and it turned out to be the single decisive fact —
  more decisive than the "confirmed vs. open license" asymmetry the brief
  centered on. The brief's framing ("why is the direction odd — the
  confirmed license carries no marker, the open one carries 1,517")
  dissolves once the domicile fact is in hand: a clearly-worded CC-BY-SA
  grant over content that carries no underlying copyright or database right
  in the first place confers nothing to worry about, however clear the
  grant's wording is. The two sources were never in the same posture; nobody
  had checked the fact that would have shown that before now.
- **The ruling for the shipped population and the ruling for the two
  non-shipped populations are not the same ruling, and I have been
  deliberate about not letting the first quietly cover the second** — see
  §5. E23 itself flagged this distinction as the thing "nobody had thought
  to check" for AIID (mirroring E16's `references[0].title` discovery for
  AIAAIC); this ruling preserves that distinction rather than collapsing it
  for a tidier one-line answer.
- **The WebFetch-verification caveat in §1 was a real, not pro forma, open
  point, and it caught real errors on the first gate pass.** Everything in
  §§2–3 is downstream of AIID's own pages establishing its US situs
  (principal place of business, venue, tax-exempt status) and its Terms of
  Use's own California choice-of-law clause (retained as corroborating
  evidence of that situs, not as the operative connecting factor — see §2's
  correction). Red-reviewer's raw-HTML re-check confirmed the governing-law
  clause verbatim but found the EIN mis-cited to the wrong page and the
  Sacramento address mis-characterized as a registered office rather than a
  DMCA agent address — both corrected above. This is the exact failure mode
  the standing rule warns about, caught by doing the check rather than
  skipping it, and it is worth carrying forward as a live example rather
  than an abstract warning.
- **Two items the gate found are explicitly the foreman's to route, not
  mine to fix:** `docs/audits/PHASE1-EXIT-2026-07-30.md:228` points readers
  at the retired §1.2 rather than the active §1.2a; and `INC-00437`
  (`aiid_id` 1574) carries an AIID source-ID while its narrative is
  OECD-derived with `description_provenance: null` — placing it in E21's
  population while still tagged to AIID. Both are noted here only so they
  aren't lost between the gate's report and the foreman's board.
