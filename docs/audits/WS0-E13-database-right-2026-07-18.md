# E13 — EU/UK Sui Generis Database Right Assessment: AIAAIC Extraction

**Date:** 2026-07-18
**Task:** E13 (WS0-T1 follow-up escalation)
**Scope:** Legal-risk assessment only. No data/schema/pipeline change made or
implied by this file directly — see §6 for requirements routed to other work.
**Author's standing method note:** per the license-auditor's absence-finding
rule, any "not located" / "no statement found" claim below states the
retrieval method used and is flagged, not treated as confirmed absence.

**Amendment log (2026-07-18, same-day, user-directed):** three amendments
were added after this file's original text was complete: (i) §4.1 — a
missing predicate in the §4(b) analysis (database-right *qualification*,
distinct from substantial investment); (ii) §6 item 5 — a fourth escalation
option, scoping the AIAAIC extraction to security-relevant entries only;
(iii) updates to the §4(b)/fork discussion, the §5 bottom line, and the
§5.1 counsel-question list flowing from (i) and (ii). All three are marked
inline as **AMENDMENT (2026-07-18)** blocks. Nothing in the original
analysis below is deleted or reversed by these amendments — they add a
conditional narrowing and a new mitigation option, both flagged as resting
on a user-supplied factual premise (see §4.1).

**Amendment log (2026-07-27, user-directed):** the factual premise §4.1
flagged as user-supplied and unconfirmed on 2026-07-18 (genai_incidents'
maker's domicile) is now **confirmed** by the user, who is genai_incidents'
maker: sole individual maker, habitually resident in Canada, no UK/EEA
maker involved. This converts §4.1's conditional finding into an
established one and is folded in as dated **"Update (2026-07-27)"** blocks
in §4.1, §5, and item 7 of §5.1, plus a new **§6.1 Revised Direction Menu
(2026-07-27)** that re-costs the four §6 options against the now-bounded
worst case (row-level ShareAlike on AIAAIC-derived rows only — the
database-level §4(b) escalation is closed). Nothing from the 2026-07-18
text or amendments is deleted or reversed; §1–§3's AIAAIC-side findings
(subsistence, substantiality, facts+link's incompleteness as a mitigation)
are explicitly unaffected and remain this file's live, unresolved risk.

## 0. Question presented

Does reducing AIAAIC-derived entries to "facts + link" (**D2**) suffice to
lawfully extract ~1,513 AIAAIC-derived rows into a redistributed public
dataset **under the UK/EU sui generis database right** — a regime distinct
from, and not disposed of by, the copyright analysis D2 actually performed?

**Short answer: no, not established as sufficient. This is a
needs-qualified-counsel situation** (see §5). D2's reasoning ("facts are not
copyrightable, so keep facts+link") answers the copyright/share-alike
question and does not address, and was never framed to address, the database
right, which protects a database's *contents* — including bare facts — as
such, regardless of copyrightability. That is the entire point of the right's
existence: it exists precisely because facts and compilations of facts often
fall outside copyright.

---

## 1. Subsistence — does AIAAIC's database right plausibly exist?

**Statutory basis:** UK Copyright and Rights in Databases Regulations 1997
(SI 1997/3032) reg 13(1): *"A property right ('database right') subsists...
in a database if there has been a substantial investment in obtaining,
verifying or presenting the contents of the database."* Mirrored by Directive
96/9/EC Art 7(1) (same three heads: obtaining / verifying / presenting,
"qualitatively and/or quantitatively" substantial).

**Investment character.** *British Horseracing Board v William Hill*
(C‑203/02) draws the line that decides most real cases: investment in
**"obtaining"** means *"resources used to seek out existing independent
materials and collect them in the database"* (¶31); investment in
**"creating"** the underlying data (generating material that did not
previously exist) is excluded (¶33). Investment in **"verification"** means
resources spent, during the database's creation and operation, to *"ensure
the reliability of the information ... to monitor the accuracy of the
materials collected"* (¶34) — and, critically, verification work done at the
stage of *creating* the underlying material does **not** count (same ¶).

Applied to AIAAIC: AIAAIC did not create the underlying events (a chatbot
mishap, a deepfake, a lawsuit). It researches, sources, cross-checks against
third-party reporting, and logs those events into a structured record with a
controlled multi-field schema (system, technology, sector, jurisdiction,
purpose, ethical issues, consequences, response — the eight cells named in
`docs/specs/WS0-T3-rescoped-2026-07-18.md`). That is squarely **obtaining +
verifying + presenting pre-existing external material**, the fact pattern
BHB says is protected — not BHB's own excluded fact pattern (investment in
generating race-card data BHB itself created). *Directmedia* (C‑304/07)
found comparable protected investment in a compiled poem-title index built
over ~2.5 years at a stated cost of EUR 34,900 — a scale much smaller than
what a multi-thousand-row, actively-maintained, weekly-updated incident
repository plausibly represents. **On the investment-character question,
subsistence looks more likely than not.**

**What I could not confirm this session, and why it matters:** I attempted
to retrieve AIAAIC's own description of its research/verification
methodology and repository scale from `aiaaic.org/about-aiaaic` and
`aiaaic.org/aiaaic-repository` via WebFetch. Both returned only navigation-
menu content, no methodology or scale statement. Per the standing rule, I
treat this as **method-suspect, not confirmed absence** — these are exactly
the large, JS-menu-heavy pages where a markdown-converting fetch has already
once produced a false negative on this same site (the 2026-07-16 CC BY-SA
miss recorded in `docs/SOURCE_LICENSES.md`). **This does not change the
subsistence conclusion** (which rests on the *character* of what AIAAIC
visibly does — structured, sourced, multi-field, continuously-updated
incident logging — not on a self-description I couldn't retrieve), but a
direct quote of AIAAIC's own investment/methodology statement, if one
exists, would strengthen the record for counsel. **Recommend:** red-reviewer
run a raw-HTML `curl` + text search of `aiaaic.org/about-aiaaic` for
methodology language before this is relied on as a negative finding.

**Update (2026-07-18, red-reviewer raw-HTML verification, check
`e13-rawhtml-check`, PROGRESS.md E13 row):** the recommendation above was
carried out. `curl` against the raw HTML (bypassing the WebFetch
markdown-conversion failure mode this file's method note flags) found:
AIAAIC is a Google Site that embeds its prose directly in the initial HTML
response — this explains, and closes off, why WebFetch saw nav-only content
(a rendering/conversion gap, not a missing statement to begin with). Against
that raw HTML, `/about-aiaaic` **still names no legal entity, no UK (or
any other) domicile, and no founder** — the absence is now confirmed
against raw HTML, not merely inferred from a lossy fetch, and **no
investment/methodology self-statement exists on the page to quote either.**
This means the reg 18 UK-nexus premise below remains an external inference
(from the E13 dispatch brief and general public understanding of AIAAIC,
not from AIAAIC's own site) and the maker-qualification hedge stands
**checked and still open**, not merely "not yet checked." Separately, the
same check found a dedicated `/terms` page exists at aiaaic.org but is
**login-gated** — it returns an HTTP 302 redirect to a Google sign-in flow
rather than page content. **This is a new, explicit evidence gap:** the
public footer's CC BY-SA notice (confirmed still live on both the home page
and the repository page, per `docs/SOURCE_LICENSES.md` §1.1) is not
necessarily AIAAIC's complete terms — any additional database-right, reuse,
or ShareAlike-scope instruction could live behind that gate, unverifiable by
this audit's tools without credentials. This is an independent reason,
beyond the database-right question itself, the AIAAIC clarification email
already drafted in `docs/SOURCE_LICENSES.md` §1.1 is worth sending, and a
fact counsel should be told rather than one this file resolves.

**Qualification (who must the maker be).** Reg 18 (as amended by the
Intellectual Property (Copyright and Related Rights) (Amendment) (EU Exit)
Regulations 2019, SI 2019/605 reg 28, in force 31 Dec 2020) currently
requires the maker to be a UK national/habitual resident, or a body
incorporated/formed in the UK meeting the reg 18(2) UK-nexus conditions —
"EEA" was substituted with "United Kingdom" throughout. **If AIAAIC's maker
(the legal entity operating aiaaic.org) is UK-domiciled**, UK database right
plausibly subsists for material made/substantially made from 31 Dec 2020
onward. I did **not** independently confirm AIAAIC's precise legal
entity/registration this session (no Companies House / charity-register
lookup performed, no shell access) — the E13 brief states "AIAAIC is
UK-based" and I have not found anything contradicting that, but the specific
maker entity should be confirmed before this is treated as settled, since
qualification turns on the *maker*, not the *site's apparent nationality*.
I also did not verify the exact text of any pre-2021/transitional
"standstill" provision governing rights in database material substantially
made before exit day under the prior EEA-nexus test — flagged as an open
textual point for counsel, not resolved here.

Separately: under Directive 96/9/EC Art 11, a UK maker generally does **not**
qualify for the *EU*-law database right for material made after the UK
ceased to be an EEA state, absent a reciprocity agreement (none located).
This project is US/internationally distributed; exposure most plausibly
sits under **UK law** given AIAAIC's UK nexus, with EU-law exposure a
secondary, less-developed question (see counsel question 6, §5.1).

**Conclusion:** Subsistence is **plausible, better than 50/50**, resting on
(a) the character of AIAAIC's work matching the "obtaining/verifying/
presenting pre-existing material" fact pattern BHB protects, and (b) a
UK-maker assumption I could not independently verify to primary-source
certainty this session.

---

## 2. Substantiality — is ~1,513 rows "substantial"?

**Statutory basis.** Reg 16(1): infringement is extracting/re-utilising
*"all or a substantial part... of the contents."* Reg 16(2) / Directive Art
7(5): *"the repeated and systematic extraction... of insubstantial parts...
may amount to the extraction... of a substantial part"* if it conflicts with
normal exploitation or unreasonably prejudices the maker's legitimate
interests. BHB (operative part 3) sets the test as **quantitative** (volume
extracted vs. total volume of the database) **and/or qualitative** (scale of
the investment in obtaining/verifying/presenting *the part actually taken*,
independent of its proportion to the whole).

**Quantitative — updated 2026-07-18 with a verified denominator.** At
original writing I could not obtain a precise, current total-row count for
AIAAIC's live "Incidents" sheet (the `about`/`repository` pages returned
nav-menu content only, per §1; the working figures were a stale third-party
summary — "1009 incidents and 411 issues" as of **September 2024** — and an
inferred upper bound from entry IDs as high as **AIAAIC2265**). **Both are
now superseded.** red-reviewer's raw-HTML/gviz check (`e13-rawhtml-check`,
2026-07-18, PROGRESS.md E13 row) queried the linked Incidents Google
Sheet's own `gviz` row-count endpoint directly — not a page-scrape — and
found a **live total of approximately 1,995 rows** (this file's own earlier
stale fallback had settled on ~1,420; that number is also retired). Against
this verified total, our GenAI-scoped extraction of **1,513 rows**
(`docs/audits/WS0-T3-cascade-2026-07-18.md:30`, confirmed against the
rebuilt tree) works out to **≈1,513 / ≈1,995 ≈ 76% of AIAAIC's entire
repository** — the gviz count is of the whole linked Incidents sheet, not
merely an AI/GenAI-scoped tab, so this is a same-denominator, apples-to-
apples fraction. **This must be read as strongly substantial on the
quantitative axis, not as "cutting toward insubstantiality."** A larger
denominator only weakens a substantiality finding if the extracted *share*
of it shrinks; here the share is roughly three-quarters of the entire
database, squarely within what BHB's quantitative test treats as
substantial. (Note for the record: an informal gloss on this same
corrected-denominator fact, recorded on the E13 PROGRESS.md board row,
read the bigger number as cutting toward insubstantiality — that reading is
incorrect at this magnitude and is superseded by this paragraph; the
relevant question is always the *share* taken, not the raw size of the
denominator in isolation.) This closes the quantitative gap this paragraph
originally flagged as unresolved — the number is now verified, not merely
"the more defensible working assumption."

**Qualitative.** AIAAIC's GenAI-related incidents are very plausibly the
most actively curated, most recently verified, most publicly referenced
slice of its repository, given the current level of public and research
interest in generative-AI harms specifically (this project's own existence
is evidence of that demand). Under BHB, qualitative substantiality does not
require majority-share extraction — it asks whether the *investment behind
the part taken* is itself significant. On that test, extracting AIAAIC's
entire GenAI coverage looks qualitatively significant even setting the
quantitative question aside.

**Aggregation via repeated ingest (reg 16(2)/Art 7(5)).** The ingest is a
recurring, scheduled pull of the same Google Sheet CSV export (per
`docs/SOURCE_LICENSES.md` §1.1: "Ingested by `scripts/ingest_aiaaic_sheet.py`
(reads the AIAAIC-maintained Google Sheet CSV export...)"; the E13 brief
characterizes the cadence as weekly). *Directmedia* held that extraction
does not need to be a single bulk act — transfers made following individual,
on-screen assessment still count, and repeated/systematic transfers of
individually-insubstantial parts that *cumulatively reconstruct* a
substantial part are caught. *Innoweb* (C‑202/12) goes further: a system
engineered to make the effective entirety of a third-party database's
content retrievable through it — by real-time translation of queries and
presentation of results — re-utilises "all or a substantial part" even
without one bulk copy event, because the *systematic, standing mechanism*
is what the right targets. Our ingest is exactly this shape: an automated,
recurring mechanism that, run over time, keeps enlarging the retained
AIAAIC-derived corpus toward (and likely already past) AIAAIC's own GenAI
coverage. **The recurring cadence is an aggravating fact under this specific
line of case law, not a mitigating one** — it is the paradigm case Art
7(5)/reg 16(2) was written to stop "insubstantial-extraction-by-degrees"
from evading.

**Conclusion:** Substantiality is **more likely than not met — and now
better evidenced than at this file's original writing**, on both
quantitative (a verified **≈76% share of AIAAIC's entire live repository**,
per the corrected figure above, not an order-of-magnitude estimate) and
qualitative (GenAI subset = high-investment, high-currency slice) grounds,
independently reinforced by the repeated/systematic-ingest aggregation
rule. The quantitative question is now closed to a real, verified number
for this snapshot in time (the §6 recommendation for a *committed,
per-run* logging artifact — rather than a one-time manual check — still
stands, since the denominator will keep moving), and the direction of the
evidence points toward "substantial," not away from it.

---

## 3. Does "facts + link" avoid the right?

**No — this is the central finding, and it is the gap the brief correctly
identified.** D2's premise is a copyright premise: "facts are not
copyrightable expression, so a bare fact + link carries no copyright
exposure." That premise is true *for copyright*. It is not a premise the
database right shares. Reg 13/Art 7 protect **"the contents of the
database"** as such — investment-protected data — with no requirement that
the contents be original expression. That is the right's entire reason for
existing: to protect compilers of factual/non-copyrightable data against
free-riding on their obtaining/verifying/presenting investment.

The four categorical fields the reduced description keeps — `system` ·
`technology` · `sector` · `jurisdiction` — are not independently-researched
facts we derived ourselves; they are **AIAAIC's own classification
decisions**, i.e., elements of AIAAIC's database schema populated through
AIAAIC's own editorial/verification process (per `docs/specs/WS0-T3-rescoped-2026-07-18.md`
§1, these come straight from AIAAIC's structured spreadsheet cells). *That
is precisely "the contents of the database"* in the reg 13/Art 7 sense.
*Directmedia* is directly on point: the CJEU held extraction does not
require verbatim reproduction of the source's own prose — transferring the
underlying *data points* (there: poem titles, individually assessed and
reformatted into a new list) into a new organized form is itself capable of
constituting "extraction." Our facts+link record does exactly that
operation with AIAAIC's system/technology/sector/jurisdiction cells.

A further, easily-missed point: arguably the single most investment-heavy
element of AIAAIC's editorial output per entry is not the prose write-up at
all — it's **AIAAIC's underlying decision that a given real-world event
belongs in its repository as an AI/algorithmic incident, at all**, plus its
classification of that event against AIAAIC's own controlled taxonomy. That
judgment is exactly what "obtaining + verifying + presenting" protects, and
it is precisely what a facts+link record reproduces (by definition — the
record only exists because AIAAIC already decided "this is an incident" and
tagged it). Dropping the prose cells (purpose/ethical/consequence/response)
reduces the *volume* of contents taken and is a genuine, real mitigation —
but it does not remove the extraction of AIAAIC's core categorization
judgment, which is arguably the qualitatively weightiest content in the row.

**Conclusion:** facts+link is a **partial, not complete**, mitigation. It
meaningfully shrinks what's taken (four fields instead of eight, no prose)
and is worth keeping regardless of the database-right outcome. But it does
not, on the reasoning above, take the extraction out of "contents of the
database" territory, and the substantiality analysis in §2 suggests the
extraction at 1,513 rows / recurring cadence is not a safely insubstantial
slice even after the reduction.

**One additional, ruled-out mitigation worth naming:** reg 20(1)'s fair-
dealing exception (extraction for teaching/research, non-commercial, source
indicated) does not apply to this project as scoped — it requires the use
to be **"not for any commercial purpose,"** and this project explicitly
relicenses its output corpus under a plain CC-BY-4.0 grant that *permits
downstream commercial reuse* (per D2/D9's "one clean CC-BY-4.0 license"
design). Granting commercial rights onward defeats the non-commercial
condition regardless of the maintainers' own non-commercial status. This
exception is not a viable path here and should not be relied on.

---

## 4. CC BY-SA 4.0 §4 coupling

Per the CC BY-SA 4.0 legal code, §4 ("Sui Generis Database Rights") reads,
in the operative parts:

- §4(a): where the licensor holds Sui Generis Database Rights in licensed
  material, §2(a)(1)'s reuse grant extends to "**extract, reuse, reproduce,
  and Share all or a substantial portion of the contents of the database**."
- §4(b): "**if You include all or a substantial portion of the database
  contents in a database in which You have Sui Generis Database Rights,
  then the database in which You have Sui Generis Database Rights (but not
  its individual contents) is Adapted Material, including for purposes of
  Section 3(b); and**" (quoted verbatim from the CC BY-SA 4.0 legal code,
  creativecommons.org/licenses/by-sa/4.0/legalcode, wording re-verified
  2026-07-18 — previously omitted from this file's §4).
- §4(c): "**You must comply with the conditions in Section 3(a)**" — i.e.
  attribution **and ShareAlike** — "**if You Share all or a substantial
  portion of the contents of the database.**"

**§4(b) analysis — this sharpens, and does not merely supplement, the
§4(c) conclusion below.** §4(c) alone could be (mis)read as scoping
ShareAlike to "whatever portion of AIAAIC's contents we're sharing" — i.e.
potentially confinable to an isolable AIAAIC-derived field subset, which is
exactly the kind of carve-out D2/D9's "single clean CC-BY-4.0, no BY-SA
subset" design implicitly hopes stays available. §4(b) forecloses that
narrower reading in the specific fact pattern this project matches: taking
a substantial portion of AIAAIC's BY-SA database contents (the categorical
facts extracted per §3 above) and including them in *our own* database —
the genai_incidents corpus — over which this project plausibly holds its
own sui generis database right (the corpus is built through the same kind
of "obtaining/verifying/presenting" investment, across dozens of ingest
scripts and manual curation, that §1 above finds grounds AIAAIC's own
right — not independently confirmed for our own project in this file, see
counsel question 7 below). Where that condition is met, §4(b)'s operative
effect is that it is **our whole database — not merely the extracted
AIAAIC rows — that becomes "Adapted Material," expressly including for
purposes of §3(b)** (the ShareAlike condition: same-license-or-BY-SA-
Compatible Adapter's License, license notice retained, no additional
restrictive terms). That is a materially broader unit of obligation than a
§4(c)-only reading suggests: the ShareAlike condition would run against
**the corpus as a database**, via §3(b)'s Adapter's-License mechanics, not
against a quarantinable AIAAIC-derived subset. Combined with §2's
substantiality finding, this reinforces rather than reverses this file's
verdict — it strengthens the case that "needs qualified counsel" is the
correct posture, and adds a distinct, database-level question counsel
should address (question 7, §5.1) alongside the row-level ones already
listed there.

### 4.1 AMENDMENT (2026-07-18): the missing predicate — does genai_incidents itself *qualify* for a sui generis database right at all?

**This amendment identifies a gap in the §4(b) analysis above: that analysis
developed only one of the two limbs a database right requires, and the
second limb is a threshold gate, not a factor to weigh.** The sui generis
database right subsists only where **both** hold:

1. **Substantial investment** in obtaining/verifying/presenting the
   contents (reg 13(1) / Art 7(1)) — the limb the §4(b) analysis above
   discussed, reasoning by analogy to §1's AIAAIC investment analysis.
2. **Qualification** (reg 18 / Art 11) — the maker must be a UK national or
   UK habitual resident, or a body incorporated/formed in the UK meeting
   the reg 18(2) UK-nexus conditions (central administration or principal
   place of business in the UK, **or** registered office in the UK with
   operations "linked on an ongoing basis with the economy of the United
   Kingdom") — or, for the *EU*-law right, an EEA-national/EEA-formed
   equivalent under Directive 96/9/EC Art 11. Reg 18(1)'s opening words are
   a hard gate — *"Database right does not subsist in a database unless...
   its maker... was"* one of the qualifying persons listed — **not** a
   sliding-scale factor alongside investment. A database can reflect
   enormous investment and still hold **no** database right if its maker
   fails qualification.

**Countries outside the UK/EEA generally have no equivalent sui generis
database right.** Canada is one: Canadian law has no separate statutory
database right analogous to reg 13/Art 7; a compilation of data is
protected in Canada only through ordinary copyright, gated by the
*originality* (skill-and-judgment) threshold the Supreme Court of Canada
set in *CCH Canadian Ltd. v. Law Society of Upper Canada*, 2004 SCC 13 —
and that is a copyright test (protecting the *selection/arrangement*, i.e.
expression), not an investment-in-obtaining-facts test. This is the
general, well-established position on Canadian law (confidence: high, on
publicly available secondary-source confirmation of "no separate sui
generis statutory database protection in Canada" plus the *CCH Canadian*
citation for how compilations are instead treated; this audit did not do
an exhaustive review of the Canadian Copyright Act's every provision, so
treat the "no equivalent right" conclusion as the standard practitioner
position rather than as independently verified against every possible
Canadian statutory source).

**Applying this to genai_incidents.** §4(b)'s second predicate (stated in
the §4(b) analysis paragraph above: "the genai_incidents corpus... over
which this project plausibly holds its own sui generis database right")
depends on genai_incidents passing **both** limbs, not just the investment
one. **Factual/jurisdictional premise supplied by the user, not
independently verified by this audit (no shell, no incorporation-registry
access): genai_incidents is understood to be made and maintained in
Canada.** This conclusion is conditional on that premise — the user (or
foreman) should confirm the actual nationality/habitual-residence/
incorporation of whoever is properly "the maker" of this project (an
individual maintainer, an unincorporated project, a GitHub-org entity,
etc. — "maker" is itself a term with content under reg 14, not necessarily
whichever person happens to run `make build`).

**If the Canada premise holds — i.e., genai_incidents' maker is Canadian
and not a UK/EEA national, resident, or incorporated/formed body — then:**

- **genai_incidents does NOT hold a UK or EU sui generis database right**,
  regardless of how much obtaining/verifying/presenting investment has
  gone into assembling the corpus (dozens of ingest scripts, manual
  curation, cross-referencing — investment alone cannot cure a
  qualification failure; reg 18 is a gate, not a weight).
- **§4(b) cannot fire.** §4(b)'s text requires including AIAAIC's contents
  "in a database in which You have Sui Generis Database Rights." If
  genai_incidents has no such right, there is no database for §4(b) to
  operate on — the clause has no subject-matter to attach to, not merely a
  weak case for attaching.
- **The database-level ShareAlike route (§4(b) → §3(b), "the database...
  is Adapted Material") falls away.** We fall back to **§4(c) → §3(a)**:
  attribution + ShareAlike attaching only to the AIAAIC-derived *contents
  extracted* (the row-level facts), not to genai_incidents' corpus as a
  whole. That is a materially smaller unit of obligation — it constrains
  how the extracted AIAAIC facts themselves must be licensed/attributed,
  not the licensing posture of the entire redistributed dataset.

**What this resolves, and what it plainly does not:**

- It does **not** dispose of **AIAAIC's own** database right. AIAAIC's
  right (if it subsists at all) turns on **AIAAIC's** maker qualifying —
  assessed independently in §1 above, on the (unverified-to-primary-source)
  assumption AIAAIC's maker is UK-domiciled. Our own qualification (or
  lack of it) has no bearing on whether AIAAIC's right exists.
- Our extraction can still **infringe** AIAAIC's right if AIAAIC's right
  subsists and our extraction is substantial (§1–§2, unaffected by this
  amendment).
- **§4(c)'s row-level ShareAlike can still attach** to the extracted
  AIAAIC-derived facts if the extraction is substantial (§2 already finds
  this more-likely-than-not). This amendment removes the *database-level*
  escalation only — it does not remove the underlying substantiality/
  infringement exposure the rest of this file establishes, and it does not
  touch §3's finding that facts+link does not itself avoid the right.

**Nature of this question.** Unlike AIAAIC's own subsistence (§1) and the
substantiality line (§2), which are fact-intensive legal judgment calls
this audit's tools cannot close, **the qualification question is
substantially a factual/jurisdictional one**: confirm where genai_incidents'
maker is domiciled/incorporated, then apply the black-letter reg 18 / Art 11
text quoted above. It may be answerable without engaging counsel, once the
maker's domicile is confirmed — though if the "who is the maker" question
turns out to be genuinely ambiguous (e.g., a multi-jurisdiction contributor
base with no single incorporated entity), that residual question is a fair
one to route to counsel alongside the others in §5.1.

### Update (2026-07-27): premise confirmed — conclusion now established, not conditional

The domicile premise this section flagged above as user-supplied and
unverified **is now confirmed**. The user — genai_incidents' human lead and
the maker in question — attested, 2026-07-27: **genai_incidents has a sole
maker; that maker is an individual, not an entity; the individual is
habitually resident in Canada; no UK or EEA entity or individual is
involved in making or maintaining the database.** This is first-party fact
(the attesting party *is* the maker), not a third-party inference or a
finding this audit's tools produced, so it is recorded here as established
rather than as a working assumption pending confirmation.

Applying reg 18(1)(a) (the individual-maker limb) directly: genai_incidents'
maker is not "a national of the United Kingdom or habitually resident within
the United Kingdom" — reg 18(1)(a) fails. The reg 18(1)(b)/(2)
corporate-nexus limb does not apply at all, because there is no incorporated
body — the maker is a sole individual. Directive 96/9/EC Art 11's parallel
EEA-nationality test fails for the identical reason. **genai_incidents
therefore does not qualify for either the UK or the EU sui generis database
right**, on the maker-nexus limb alone, independent of how the
investment-substantiality limb (limb 1 above) would otherwise resolve — reg
18 is a threshold gate, not a factor to weigh alongside investment, exactly
as this section stated before the premise was confirmed. Canada has no
equivalent statutory sui generis right (*CCH Canadian*, 2004 SCC 13, already
cited above), so there is no alternate UK/EU-equivalent right the maker's
Canadian residence itself confers in its place.

**This closes limb 2 of the §4.1 predicate to a definite NO, on established
fact rather than a conditional premise.** The consequence stated in "If the
Canada premise holds..." above no longer depends on an "if": genai_incidents
does not hold a UK or EU sui generis database right; §4(b) cannot fire (there
is no database right for it to attach to — not merely a weak case for
attaching); the database-level ShareAlike escalation via §4(b) → §3(b) is
**dead**, not merely conditionally narrowed. The fallback to §4(c) → §3(a)
row-level ShareAlike on the AIAAIC-derived contents actually extracted
stands as the operative worst case, entirely unaffected by this update — it
turns on AIAAIC's own subsistence (§1) and our extraction's substantiality
(§2), neither of which this update touches, because both are about AIAAIC's
right, not ours.

**Residual, narrower than before.** Of the three residual points the
"Nature of this question" paragraph above and counsel question 7 (§5.1)
previously left open: (i) "premise not confirmed" is now **moot** —
confirmed; (iii) "who is the maker... for a multi-contributor project" is
now **resolved** — the maker is a sole individual, so there is no
multi-party ambiguity to adjudicate; (ii) "whether genai_incidents might
separately hold a sui generis-equivalent right under some other country's
law" (a jurisdiction beyond UK/EU/Canada) remains open in principle — this
audit has not surveyed jurisdictions beyond those three — but it now matters
*only* for the §4(b) database-level escalation specifically, and reg 18/Art
11 qualification for the UK/EU right is firmly answered NO regardless of
that residual. Given the maker is a single Canadian-resident individual, a
"some other jurisdiction confers a substitute right" scenario would require
a specific, additional statutory hook this audit has no present reason to
suspect exists, and is not pursued further here absent a specific lead.

**Sources for this amendment:** SI 1997/3032 reg 18 (as amended by SI
2019/605 reg 28), quoted operative text: "*Database right does not subsist
in a database unless, at the material time, its maker... was — (a) an
individual who was a national of the United Kingdom or habitually resident
within the United Kingdom, (b) a body which was incorporated under the law
of any part of the United Kingdom and which... satisfied one of the
conditions in paragraph (2)... [or] (c) a partnership or other
unincorporated body...*" — reg 18(2): "*(a) that the body has its central
administration or principal place of business within the United Kingdom,
or (b) that the body has its registered office within the United Kingdom
and the body's operations are linked on an ongoing basis with the economy
of the United Kingdom.*" (legislation.gov.uk/uksi/1997/3032/regulation/18,
re-verified 2026-07-18). Directive 96/9/EC Art 11 (EEA-nationality
requirement for the parallel EU-law right, already cited in §1/§7 above).
*CCH Canadian Ltd. v. Law Society of Upper Canada*, 2004 SCC 13 (Canadian
compilation protection runs through copyright originality, not a sui
generis database right).

---

This creates the exact fork the E13 brief anticipated:

- **If our extraction is insubstantial** (per §2), we don't need CC BY-SA
  §4 at all — reg 19(1) independently gives any *lawful user* of a publicly
  available database an entitlement to extract/re-utilise insubstantial
  parts "for any purpose," and reg 19(2) makes any contract term purporting
  to override that entitlement **void**. No ShareAlike attaches under this
  path, because no CC BY-SA condition is ever triggered.
- **If our extraction is substantial** (the more likely reading per §2–§3),
  the *only* plausible authority for extracting AIAAIC's database contents
  at all is CC BY-SA §4 — and §4(c) then attaches ShareAlike + attribution
  to whatever we extracted, i.e. the reduced facts themselves. That
  re-imports the exact obligation D2/D9's "single clean CC-BY-4.0, no BY-SA
  subset" design goal exists to shed, onto the very fields D2 kept precisely
  because it believed they were "safe."

**There is no license-free third option here.** Database right, unlike
copyright, is not satisfied by "just take the facts, not the expression" —
that move only works against a *copyright* claim. Against a *database
right* claim, the two live options are (i) stay genuinely insubstantial
under reg 19 (no license needed, no ShareAlike), or (ii) rely on the
license's own database-right grant (CC BY-SA §4), which brings ShareAlike
with it. Given §2's substantiality analysis, option (ii) is the more likely
operative one under the current WS0-T3 scope — meaning **the "no BY-SA
subset" goal is not currently achieved for the AIAAIC-derived fields**, even
after the D9/WS0-T3 reduction, unless the extraction is independently
shrunk enough to land in option (i). See §6 for what that would require.

**AMENDMENT (2026-07-18) — how §4.1 changes the "substantial" branch
above.** The "substantial" branch as originally written left open whether
§4(c)'s ShareAlike attaches only to the extracted AIAAIC facts, or —
per the §4(b) analysis paragraph earlier in this section — to
genai_incidents' *entire corpus as a database*, via §4(b)'s "Adapted
Material" mechanics. §4.1 narrows that: **the database-level escalation
requires genai_incidents to hold its own sui generis database right, and
per §4.1, conditional on the user-supplied premise that genai_incidents is
made/maintained in Canada, it does not.** So, on that premise, the
"substantial" branch resolves to **§4(c) row-level ShareAlike on the
extracted facts only** — the narrower reading D2/D9 hoped for turns out to
be *right for the database-right-escalation question specifically*, even
though (per §3) it is *not* right for the "does facts+link avoid the right
altogether" question, which §4.1 does not touch. This does **not** change
which option is "more likely operative" between (i) and (ii) above — that
turns on substantiality (§2), which §4.1 does not address — it only
changes the *scope* of what option (ii)'s ShareAlike condition reaches if
it is the operative path.

---

## 5. Bottom line

**Not sufficient as currently reasoned — this needs qualified counsel,
and separately, the ingest design should be tightened regardless of what
counsel eventually says (§6).**

This is not a coin-flip call I'm declining to make out of excess caution —
the specific facts that would resolve it (AIAAIC's actual investment scale
and its maker's precise legal domicile; the exact current size of AIAAIC's
live sheet as a denominator; where UK courts would in practice draw the
insubstantial/substantial line for a categorical-facts-only, ~1,500-row,
recurring extraction) are fact-intensive determinations this audit's tools
(WebFetch/WebSearch against primary legislation/case law, no access to
AIAAIC's internal records, no shell) cannot close to the confidence a
public, at-scale, durable redistribution decision warrants. The honest
answer, at the diligence level this task calls for, is: the weight of the
primary-source analysis above points toward **exposure remaining after the
D2/D9 reduction**, not toward "resolved."

**AMENDMENT (2026-07-18):** the qualification analysis at §4.1 **narrows**
this bottom line without reversing it. Conditional on the user-supplied
premise that genai_incidents' maker is Canadian (not UK/EEA), §4.1 finds
genai_incidents does not itself hold a sui generis database right, so the
§4(b) *database-level* ShareAlike escalation does not arise — one specific
question (counsel question 7 below) is substantially resolved by
jurisdictional fact-checking rather than by paid legal judgment. **This
does not shrink the core exposure the rest of this file establishes**:
AIAAIC's own right (§1), the substantiality of our extraction (§2), the
inadequacy of facts+link as a complete mitigation (§3), and the §4(c)
row-level ShareAlike attachment (§4) are all unaffected by §4.1 and remain
"needs qualified counsel" questions. The practical effect of §4.1 is to
confine the *worst-case unit of obligation* from "the entire redistributed
corpus" down to "the extracted AIAAIC-derived facts" — a real, favorable
narrowing, but not a resolution of whether that smaller obligation attaches
at all.

**Update (2026-07-27) — the §4.1 premise is now established fact, not a
condition.** The "conditional on the user-supplied premise" qualifier above
is retired: the user, who is genai_incidents' maker, has confirmed the
underlying fact directly (sole individual maker, habitually resident in
Canada, no UK/EEA maker involved — see §4.1's 2026-07-27 update for the full
predicate and its reg 18/Art 11 application). The bottom line now sorts as
follows.

**DEAD (no longer live exposure):**
- The §4(b) database-level ShareAlike escalation against genai_incidents'
  own corpus. genai_incidents does not hold a UK or EU sui generis database
  right (maker-qualification fails reg 18(1)(a)/Art 11 on established
  fact), so §4(b) has no database-right subject-matter of ours to attach
  to.
- Counsel question 7 (§5.1) — resolved on first-party fact for its main
  branch (whether genai_incidents holds its own right); only a narrow
  residual survives (see the updated item 7 below).

**SURVIVED (still live, still needs the direction decision at §6.1):**
- AIAAIC's own database-right subsistence (§1) — plausible, better than
  50/50, resting entirely on AIAAIC's own maker/investment characteristics,
  independent of ours.
- The substantiality of our extraction against AIAAIC's database (§2) —
  more likely than not met, ≈76% of AIAAIC's live repository, unaffected by
  our own qualification finding.
- Facts+link as an incomplete mitigation against the database right (§3) —
  unaffected; this update resolves *whose* database right could attach at
  the database level, not whether facts+link avoids extraction of AIAAIC's
  contents in the first place.
- §4(c) → §3(a) row-level ShareAlike attaching to the AIAAIC-derived facts
  actually extracted, if AIAAIC's right subsists and the extraction is
  substantial (§1–§2) — this is now the **sole** operative worst case, not
  one of two possible worst cases, since the database-level route is
  closed.

**Net effect.** The worst-case unit of obligation is no longer "confined
from the entire corpus down to the extracted facts, pending confirmation"
(§4.1's original 2026-07-18 framing) — it is now **settled** at row-level
ShareAlike on AIAAIC-derived content only, as an established conclusion.
This is a real, favorable, and now-final narrowing of *what could be owed
if the obligation attaches at all*; it is not a narrowing of *whether
AIAAIC-side risk exists* — AIAAIC's subsistence, our extraction's
substantiality, and the §4(c) attachment question remain exactly as this
file's original analysis assessed them, and the direction decision at §6.1
is the live open item.

### 5.1 Exact questions for counsel

**Status as of 2026-07-27:** questions 1–6 below remain fully live — they
all concern AIAAIC's own database right and our extraction from it, none
of which turn on genai_incidents' own qualification, so the fact confirmed
in §4.1 does not touch them. Question 7 is resolved on its main branch (see
its updated entry below), with one narrow residual point remaining.

1. On these facts — a UK-based repository maker (entity/domicile to be
   confirmed), maintaining a structured, multi-field incident database
   built from research/verification of third-party reporting, published
   under CC BY-SA 4.0, from which ~1,513 entries' categorical fields
   (`system`/`technology`/`sector`/`jurisdiction`) are extracted by an
   automated recurring process into a public, commercially-relicensable
   (CC-BY-4.0) dataset — does UK sui generis database right (SI 1997/3032
   as amended) plausibly subsist, and does the maker qualify under the
   current reg 18 UK-nexus test?
2. Does that extraction constitute extraction of "a substantial part...
   evaluated qualitatively and/or quantitatively" under reg 16(1)/Art 7(1),
   applying BHB's investment-based qualitative test and Directmedia's
   holding that verbatim reproduction of the source's own expression is not
   required for "extraction"?
3. Does the recurring/weekly re-ingest trigger reg 16(2)/Art 7(5)'s
   repeated-and-systematic-extraction-of-insubstantial-parts rule, given
   the growing cumulative total already at 1,513 rows, applying Directmedia
   and Innoweb's reasoning that a standing, systematic extraction mechanism
   (not just a single bulk copy) can itself constitute re-utilisation of a
   substantial part?
4. If CC BY-SA 4.0 §4 is the operative authority (because reg 19's
   insubstantial-part safe harbor is unavailable), does §4(c)/§3(a)
   ShareAlike then attach to the redistributed AIAAIC-derived facts, and is
   a narrower AIAAIC-specific CC-BY-SA carve-out within an otherwise CC-BY
   corpus the only lawful path — contrary to D2's "no BY-SA subset" goal?
5. What extraction design (row-count ceiling, field-count ceiling, refresh
   cadence, or a shift to using AIAAIC purely as a discovery/pointer source
   with facts independently re-derived from AIAAIC's own cited primary
   sources rather than from AIAAIC's cells) would counsel consider
   defensibly insubstantial under reg 19?
6. Given the UK maker but international/EU-reaching redistribution, is
   there material additional exposure under an EU member state's
   implementation of Directive 96/9/EC (noting Art 11's EEA-nationality
   requirement and the post-Brexit UK/EU divergence), and if so, which
   regime should the project treat as controlling?
7. Does genai_incidents itself plausibly hold its own UK/EU sui generis
   database right in the assembled corpus (built through obtaining/
   verifying/presenting investment analogous to §1's analysis of AIAAIC),
   and if so, does CC BY-SA 4.0 §4(b) attach ShareAlike (via §3(b)) to the
   redistribution of the corpus **as a database**, rather than only to the
   extracted AIAAIC-derived fields — and if that database-level obligation
   attaches, what would compliance require given the corpus's mixed-license,
   multi-source composition (Apache-2.0 ATLAS/garak carve-outs, CC-BY GHSA/
   OSV/NVD content, etc.)?

   **AMENDMENT (2026-07-18) — narrowed, not fully mooted.** §4.1
   substantially resolves the first half of this question — *does
   genai_incidents hold its own sui generis right* — without counsel,
   **conditional on the user confirming genai_incidents' maker is
   domiciled/incorporated in Canada** (or any other non-UK/EEA
   jurisdiction): if confirmed, the answer is "no" on qualification grounds
   alone (reg 18 / Art 11), regardless of how the investment question would
   otherwise come out, and the §4(b)-database-level/mixed-license-
   compliance half of this question **does not arise**. What remains a
   genuine open item for counsel, narrower than originally framed: (i) if
   the maker's domicile turns out to be UK/EEA after all (premise not
   confirmed), the full original question stands unresolved; (ii) even on
   the Canada premise, whether genai_incidents might separately hold a
   sui generis right under **some other country's law** if one exists
   (this audit did not survey jurisdictions beyond UK/EU/Canada); and
   (iii) confirming precisely who "the maker" is in reg 14's sense for a
   multi-contributor open-source project, if that turns out to be
   contested. Counsel spend on this question, if any, should be scoped to
   those narrower residual points, not the whole original question.

   **Update (2026-07-27) — resolved, not merely narrowed.** The premise
   this amendment left conditional ("conditional on the user confirming...")
   is now confirmed as first-party fact (§4.1, 2026-07-27 update): sole
   individual maker, habitually resident in Canada, no UK/EEA maker
   involved. The first half of question 7 — does genai_incidents hold its
   own sui generis database right — is answered **no**, on established fact,
   and no counsel spend is warranted on that half. Of the three residual
   points listed above: (i) is **moot** (confirmed Canada, not UK/EEA); (ii)
   remains open in principle but only as a completeness point — this audit
   has no specific reason to suspect a sole Canadian-resident individual
   holds an equivalent right under some other, unsurveyed jurisdiction's
   law, and is not pursuing it further absent a specific lead; (iii) is
   **resolved** (sole individual maker, no multi-contributor ambiguity to
   adjudicate). Net: question 7 no longer needs counsel time except, at
   most, a brief note on residual (ii) if the project wants that
   completeness check — a materially smaller ask than the original
   question.

---

## 6. New requirements for WS0-T3 (routed via foreman)

These are additive to, not replacing, the existing WS0-T3 re-scoped spec
(`docs/specs/WS0-T3-rescoped-2026-07-18.md`). None of them are implemented
by this file; they are exact requirements for the foreman to route.

1. **Docs correction (owner: WS0/license-auditor, future task).**
   `docs/SOURCE_LICENSES.md` §1.1's AIAAIC "Action" cell currently reads
   *"(b) share-alike, resolved by decision D2"* and the summary table
   (bottom of the file) lists AIAAIC as *"Listed here as a resolved
   decision on record, not an open question."* Both overstate the current
   state of the analysis: D2 resolves the **copyright** share-alike
   question; it does **not** resolve, and per this assessment likely does
   **not** dispose of, the **database-right** question. The row should be
   corrected to record the database-right question as open, pending
   counsel, per this file — I am not making that edit in this task per the
   E13 brief's "do not touch data/schema" scope, but it should not remain
   uncorrected once this assessment is on record, since an uncorrected
   "resolved" claim is now known to be inaccurate.
2. **Ingest instrumentation (owner: pipeline-engineer).** Add logging (a
   committed artifact, not just the existing stdout `print(f"[aiaaic]
   {len(rows)} raw rows")` at `ingest_aiaaic_sheet.py:390`) that records,
   per ingest run: the total row count of AIAAIC's live "Incidents" sheet,
   alongside the count actually retained after GenAI filtering. Without
   this, no future substantiality assessment has a real, current
   denominator — today's §2 analysis had to reason from a stale third-party
   estimate and an inferred ID-range upper bound, neither a primary-source
   number.
3. **Do not let retained AIAAIC coverage grow unmonitored.** Recommend a
   documented threshold or periodic re-assessment trigger (e.g., "re-open
   this analysis if AIAAIC-derived rows exceed N, or exceed X% of AIAAIC's
   current total Incidents-sheet size") pending counsel's eventual
   guidance — this is a policy/spec decision for the user or foreman, not
   one I'm resolving here.
4. **WS0-T3's acceptance checklist should add a database-right gate**
   distinct from its existing copyright/prose-audit gate (the zero-
   dropped-cell-marker check in `docs/specs/WS0-T3-rescoped-2026-07-18.md`
   §2(a)). The current checklist's "Published AIAAIC descriptions carry
   categorical facts only ... — the D9 licensing goal" item should not be
   read, on its own, as closing out AIAAIC licensing risk generally; per
   this file, it closes out only the copyright/share-alike sub-question.
5. **Escalate to the user, per CLAUDE.md step 8** ("WS0-T1 outcomes
   requiring data drops/summarization" and "any invariant/task conflict"):
   this finding plausibly requires either (a) counsel engagement before
   the ~1,513 AIAAIC-derived rows are further expanded or relied on as
   final, or (b) a materially more conservative AIAAIC ingest redesign
   than WS0-T3 currently specifies (see counsel question 5, §5.1), or
   (c) accepting residual risk knowingly, as a business decision, with
   this file as the documented basis, **or (d) — AMENDMENT (2026-07-18) —
   scope the extraction to security-relevant entries only.** Which of those
   four the project takes is not mine to decide.

   **(d) in detail.** §2's substantiality finding turns on the *proportion*
   of AIAAIC's database taken: currently ~1,513 rows against AIAAIC's
   ~1,995-row live repository, ≈76%. A large share of those 1,513 entries
   are algorithmic-harm / bias / misinformation cases that fail
   genai_incidents' own GenAI-security scope test — the same scope-drift
   issue already pending as **WS1-T4 / E5** (Phase-1 escalation: rename to
   "AI security incidents," or tag `ai_system_type: genai|agentic|
   classical-ml|algorithmic` and default filters to genai+agentic; the
   plan's stated recommendation is the tagging option).

   - **Quantitative effect.** Narrowing to the security-relevant
     (genai+agentic-security) subset of AIAAIC's coverage would shrink the
     numerator without changing AIAAIC's ~1,995-row denominator, reducing
     the extracted share — potentially far enough that the remaining
     extraction lands on the "insubstantial" side of reg 16(1). If it does,
     reg 19's unwaivable lawful-user entitlement applies and **no
     ShareAlike attaches at all** — a stronger outcome than either §4.1's
     database-level narrowing or a §4(c) row-level obligation, because no
     license condition is triggered in the first place. This is not
     guaranteed — it depends on how large the security-relevant subset
     turns out to be against the 1,995 denominator, which is not yet
     measured — but it is the only option on this list capable of reaching
     the "no license needed" outcome rather than a "comply with ShareAlike"
     outcome.
   - **Qualitative caveat (BHB).** Substantiality is also qualitative:
     under BHB, a smaller *share* can still be qualitatively substantial if
     it captures the high-investment slice of the source database. The
     genai_incidents-relevant slice of AIAAIC's coverage is very plausibly
     AIAAIC's most-current, most-actively-maintained, highest-public-
     interest content (§2's existing qualitative analysis) — narrowing to
     that slice does not obviously *reduce* the qualitative exposure and
     may simply *relocate* it: fewer rows, but concentrated in precisely
     the content most likely to be found qualitatively significant. Option
     (d) is a real, evidence-based lever on the quantitative axis; it is
     not a clean answer on the qualitative axis, and should not be
     represented as fully resolving §2's substantiality finding on its
     own.
   - **Cross-reference to WS1-T4/E5 — one lever, two purposes.** The scope
     decision pending under WS1-T4/E5 (whether/how to confine
     genai_incidents to genuinely GenAI-security-relevant incidents) and
     this licensing-substantiality question are **the same decision** —
     narrowing AIAAIC-derived intake to security-relevant entries would
     simultaneously (i) reduce the extracted proportion of AIAAIC's
     database for licensing purposes (this file) and (ii) fix the corpus
     scope-drift issue WS1-T4/E5 already flags as a Phase-1 priority. The
     user should see these as one lever serving both, not two independent
     decisions to make separately.
   - **Compatibility.** Option (d) is compatible with, and can be combined
     with, option (b) (conservative ingest redesign) — scoping *what* gets
     extracted and redesigning *how* it gets extracted address different
     axes of the same exposure. Of the four options, (d) is potentially the
     cheapest risk-reducer, since it may remove the need for a CC BY-SA
     ShareAlike compliance path entirely rather than requiring the project
     to build and maintain one.

### 6.1 Revised direction menu (2026-07-27)

The qualification fact confirmed in §4.1 changes what each of the four
options below actually buys and costs, because it changes the **worst-case
unit of obligation**: before 2026-07-27, the worst case was ambiguous
between "row-level ShareAlike on the extracted AIAAIC facts" (§4(c)) and
"database-level ShareAlike on genai_incidents' entire redistributed corpus"
(§4(b), if genai_incidents itself held a sui generis right). That ambiguity
is now resolved: **§4(b) is dead — the worst case is row-level ShareAlike on
the ~1,513 AIAAIC-derived rows only.** Nothing about AIAAIC's own subsistence
(§1) or the substantiality of our extraction (§2) has changed; what has
changed is the ceiling on how bad it gets if that exposure materializes.
Each option is re-costed below against that new ceiling.

**(a) Engage counsel.**
What it now buys is narrower, and correspondingly cheaper, than it would
have been before 2026-07-27: counsel's brief no longer needs to cover
"does our entire redistributed corpus need to carry a ShareAlike
obligation" (that question is now closed to "no" on established fact) —
only "does AIAAIC's database right subsist and is our extraction
substantial (§1–§2), and if so, how do we design a compliant row-level
attribution/ShareAlike mechanism for the AIAAIC-derived rows (§4(c))." That
is a smaller, more bounded legal question than the file's original framing,
and should cost less to have answered. It still requires genuine legal
judgment this audit's tools cannot supply — §1/§2 remain fact-intensive,
UK-database-law questions, not something first-party attestation can
settle the way §4.1's qualification question was settled.

**(b) Conservative ingest redesign** (row/field ceilings, or pointer-only
with facts re-derived from AIAAIC's own cited primary sources).
This option gets **more attractive**, not less, under the new ceiling. Its
original justification had to guard against two different failure modes —
a row-level obligation AND a whole-corpus contagion risk via §4(b) — which
meant a genuinely conservative redesign might have needed to consider
heavier interventions (e.g., a full pointer-only rebuild) to keep the
*whole corpus* clean. With §4(b) dead, a much lighter design now suffices:
isolating the AIAAIC-derived rows into a clearly attributed,
ShareAlike-flagged subset (a metadata tag plus an attribution/license
notice attached to those specific rows) fully contains the exposure,
because there is no longer a mechanism by which that subset's obligation
could spread to the rest of the corpus. **This is the option whose
cost/benefit improves the most from the qualification finding.**

**(c) Knowingly accept residual risk, with this file as documented basis.**
This option is **now more defensible to take**, because the risk being
accepted is precisely bounded rather than open-ended: at most, row-level
ShareAlike/attribution exposure on the AIAAIC-derived subset of the corpus,
not a dataset-wide relicensing threat. If AIAAIC ever asserted a claim, the
practical remedy under this ceiling would be to retrofit attribution/
ShareAlike notice onto the AIAAIC-derived rows specifically — a contained,
bounded fix, not a full-corpus renegotiation. This does not mean the risk is
zero or trivial (§1–§2's "more likely than not" findings on subsistence and
substantiality are unaffected), only that its *ceiling* is now known and
smaller than the file's original framing implied.

**(d) Scope the extraction to security-relevant entries only** (synergy
with WS1-T4/E5).
This option's own mechanics are **unaffected** by the qualification
finding — it works on the substantiality axis (§2) by shrinking the
numerator against AIAAIC's ~1,995-row denominator, entirely independent of
whether genai_incidents itself qualifies for a database right. What changes
is the *context* it operates in: even if (d) does not succeed in pushing
the extraction to reg 19 insubstantiality, the fallback is now known to be
row-level only. (d) remains the only option on this list capable of
reaching a "no ShareAlike condition triggered at all" outcome (via reg 19),
and remains compatible with, and cheaper to combine with, (b).

**Does the qualification finding change the recommendation ordering? Yes,
in one specific way.** The original 2026-07-18 framing treated (b) and (d)
as the two "real mitigation" options and (c) as a last-resort fallback
mainly because the ceiling was unbounded. With the ceiling now fixed at
row-level-only, (c) is no longer a last resort — it is a genuinely
proportionate response *if* the project is comfortable carrying a bounded,
row-level attribution/ShareAlike obligation on the AIAAIC-derived subset
indefinitely. My recommendation ordering is: **(b) lightweight row-level
tagging/attribution design, combined with (d) scope-narrowing where WS1-T4/
E5 already justifies it on independent grounds, as the primary path; (c) as
an explicitly acceptable interim or permanent posture given the now-bounded
ceiling, if the project prefers not to build (b); (a) counsel engagement
reserved for if the project wants a definitive answer on AIAAIC's own
subsistence/substantiality (§1–§2) rather than continuing to operate on
this file's "more likely than not" findings.** This is a change from the
original framing, which could not rule out that (a) was effectively
required given an unbounded worst case — that pressure is now off.

**The cheapest input, regardless of which option the project takes,
remains the pending AIAAIC outreach question** —
`docs/outreach/aiaaic-facts-link.md`, cleared to send, asking AIAAIC
directly whether it considers an extraction at this scale to engage its
database right and trigger ShareAlike. That question addresses §1/§2
directly (AIAAIC's own view of subsistence and substantiality) at zero
legal cost, and its answer would sharpen every option above regardless of
which is chosen — a "no, we don't consider this to engage database right"
answer would support (c) as adequate as-is; a "yes" answer would strengthen
the case for (a) or (b). Per CLAUDE.md, the user reviews and sends outreach
personally; this file recommends sending it promptly, in parallel with
whichever direction option is chosen, rather than waiting for it before
proceeding.

---

## 7. Sources cited

**Legislation (primary):**
- Copyright and Rights in Databases Regulations 1997 (SI 1997/3032):
  reg 12 (interpretation — extraction/re-utilisation definitions),
  reg 13 (database right — substantial-investment test),
  reg 16 (infringement — substantial part; repeated/systematic
  insubstantial-parts aggregation),
  reg 18 (qualification for database right, current UK-nexus text as
  amended),
  reg 19 (lawful users — unwaivable insubstantial-part entitlement),
  reg 20 + Schedule 1 (exceptions — non-commercial teaching/research fair
  dealing).
  legislation.gov.uk/uksi/1997/3032
- The Intellectual Property (Copyright and Related Rights) (Amendment)
  (EU Exit) Regulations 2019 (SI 2019/605), reg 28 (substituting "EEA" →
  "United Kingdom" in reg 18). legislation.gov.uk/uksi/2019/605
- Directive 96/9/EC on the legal protection of databases: Art 7 (object of
  protection; extraction/re-utilisation definitions; repeated/systematic
  insubstantial-parts rule), Art 8 (lawful users' rights/obligations),
  Art 11 (beneficiaries of protection — EEA-nationality requirement).
  eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:31996L0009

**Case law (CJEU, primary):**
- *The British Horseracing Board Ltd and Others v William Hill
  Organization Ltd*, C‑203/02, judgment of 9 Nov 2004 — obtaining/creating
  distinction (¶¶31–33), verification-investment scope (¶34), quantitative/
  qualitative substantial-part test (operative part 3).
  eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62002CJ0203
- *Directmedia Publishing GmbH v Albert-Ludwigs-Universität Freiburg*,
  C‑304/07, judgment of 9 Oct 2008 — extraction does not require verbatim
  reproduction; repeated/systematic transfer of insubstantial parts that
  would reconstitute a substantial part is caught.
  eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:62007CJ0304
- *Innoweb BV v Wegener ICT Media BV*, C‑202/12, judgment of 19 Dec 2013 —
  a standing, systematic mechanism making a third-party database's content
  effectively retrievable can itself constitute re-utilisation of a
  substantial part, without one bulk copy event.
  eur-lex.europa.eu/legal-content/EN/TXT/?uri=celex:62012CJ0202

**License text (primary):**
- Creative Commons Attribution-ShareAlike 4.0 International, Legal Code,
  §4 (Sui Generis Database Rights). creativecommons.org/licenses/by-sa/4.0/legalcode

**Amendment sources (2026-07-18, added for §4.1 / §6(d)):**
- SI 1997/3032 reg 18(1)–(2) (qualification for database right — UK-nexus
  text as currently in force, re-verified against legislation.gov.uk
  directly for this amendment). legislation.gov.uk/uksi/1997/3032/regulation/18
- Directive 96/9/EC Art 11 (EEA-nationality requirement for the parallel
  EU-law right) — already cited above, re-applied here to genai_incidents'
  own (non-)qualification rather than AIAAIC's.
- *CCH Canadian Ltd. v. Law Society of Upper Canada*, 2004 SCC 13 — cited
  for the general, secondary-source-confirmed position that Canadian law
  has no sui generis database right and protects compilations only through
  copyright's originality (skill-and-judgment) threshold. Confidence: high
  on the general position; this audit did not exhaustively review the
  Canadian Copyright Act for every provision (see §4.1 confidence note).
- `MASTER_IMPROVEMENT_PLAN.md` WS1-T4 / PROGRESS.md E5 row (GenAI-security
  scope-drift issue cross-referenced in §6 option (d) as the same lever as
  the substantiality-reduction question).

**Fact source (2026-07-27, first-party, added for the §4.1/§5/§5.1/§6.1
updates):**
- User attestation, 2026-07-27, supplied directly by genai_incidents' human
  lead, who is the maker in question: sole individual maker, habitually
  resident in Canada, no UK or EEA entity or individual involved in making
  or maintaining the database. Treated as first-party fact (the attesting
  party is the maker), not as an inference or a finding this audit's tools
  produced; converts §4.1's 2026-07-18 conditional premise to an
  established fact.

**Project sources (context, not legal authority):**
- `docs/specs/WS0-T3-rescoped-2026-07-18.md` (D2/D9/D10 scope and the
  eight AIAAIC source cells).
- `docs/SOURCE_LICENSES.md` §1.1 (AIAAIC row, existing copyright-only
  analysis).
- `docs/audits/WS0-T3-cascade-2026-07-18.md:30` (confirmed 1,513
  AIAAIC-derived entry count in the rebuilt tree).
- `scripts/ingest_aiaaic_sheet.py:390` (existing but non-persisted raw-row
  count logging).
- `PROGRESS.md` (E2/D2 decision record; WS0-T1 close-out material; E13 row
  carries the 2026-07-18 red-reviewer raw-HTML verification, check
  `e13-rawhtml-check`, folded into §1/§2 above).

**Not independently confirmed this session (flagged, not asserted):**
AIAAIC's precise maker entity/legal domicile; AIAAIC's own stated
methodology/investment scale; the exact text of any pre-2021 EEA-era
standstill provision for database material substantially made before UK
exit day. `aiaaic.org/about-aiaaic` and `aiaaic.org/aiaaic-repository` were
fetched via WebFetch and returned only navigation-menu content — treated as
method-suspect per the standing rule, not as confirmed absence of a
methodology statement.

**Update (2026-07-18):** the maker entity/domicile and methodology/
investment-scale gaps above were *not* closed by the follow-up raw-HTML
check — see the §1 update — they remain genuinely absent even in raw HTML,
which is a stronger (checked, still-negative) finding than the original
method-suspect flag. AIAAIC's current total live-sheet row count **is** now
confirmed: ≈1,995 rows via a direct `gviz` query against the linked
Incidents sheet (red-reviewer, `e13-rawhtml-check`, 2026-07-18; see §2),
removed from this "not confirmed" list accordingly. A dedicated `/terms`
page was also found to exist but is login-gated, unverifiable without
credentials — a new evidence gap, not a resolved one; see §1.
