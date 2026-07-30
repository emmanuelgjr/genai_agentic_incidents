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

## Outcome

**(2) — MARKING NOT REQUIRED for the population that ships, and the
asymmetry with AIAAIC is JUSTIFIED — but stated with a (3)-style tripwire
for a second, currently-dormant population that does not ship today.**

This is not a coin toss resolved cautiously in the project's favor. Two
independent legal reasons — one turning on U.S. copyright law's categorical
short-phrase exclusion, one turning on the exact UK/EU database-right
maker-qualification gate E13 §4.1 already built for this project's own
qualification — both point the same way, for the same underlying fact:
**AIID's maker is a U.S. (California) nonprofit corporation, not a UK/EU
one.** That single fact is why AIID and AIAAIC are not "the same posture,"
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
own Terms of Use directly (`https://incidentdatabase.ai/terms-of-use/`, the
same page `docs/SOURCE_LICENSES.md` §1.2 already quotes for the CC-BY-SA
grant itself) rather than assume the parallel holds.

**Method note, per this file's own standing rule:** this was a WebFetch
read, not a raw `curl`+`grep` of the HTML — the same tool this project's own
standing rule flags as having produced false paraphrases twice before.
Unlike an *absence* finding, this is a *presence* finding of specific,
distinctive strings (an EIN, a street address, a named venue), which is a
lower-risk shape for a summarizing tool to fabricate wholesale than a
negative claim — and it is corroborated by an independent `WebSearch` (not
the same tool or fetch) returning consistent facts from two unrelated
sources (LinkedIn: Los Angeles HQ; a nonprofit-directory site: Sacramento,
CA; both plus a stated "IRS ruling in 2023," i.e., U.S. tax-exempt status).
Still, this is the single most load-bearing fact in this ruling, so it
should not be treated as fully closed until raw-HTML-confirmed. **Exact
check for red-reviewer:** `curl -sL https://incidentdatabase.ai/terms-of-use/
| grep -i -E "Sacramento|Responsible AI Collaborative, Inc\.|governing
law|Los Angeles County|88-1046583"` — if any of these fail to appear in the
raw HTML, this ruling's Layer 1 and Layer 2 conclusions below must be
revisited before being relied on further.

**What the Terms of Use state (WebFetch, 2026-07-30, not yet raw-HTML
confirmed):**
- The operating entity is **"Responsible AI Collaborative, Inc.,"**
  registered at **"2108 N St N, Sacramento, CA 95816"** — a California
  corporation, not a UK or EEA one.
- **Governing law:** *"the Agreement and any access to or use of our Site
  will be governed by the laws of the state of California, U.S.A.,
  excluding its conflict of law provisions."*
- **Venue:** the state and federal courts of **Los Angeles County,
  California**; arbitration also sited in Los Angeles.
- An EIN (**88-1046583**) is stated, consistent with U.S. tax-exempt
  nonprofit status (corroborated by `WebSearch`'s independent "IRS ruling in
  2023" finding).

This is a materially stronger primary-source basis than E13 had for
AIAAIC's own domicile — E13 §1 explicitly could not determine AIAAIC's
"precise legal entity/registration" and worked from an unconfirmed
assumption ("the E13 brief states 'AIAAIC is UK-based' and I have not found
anything contradicting that"). Here, AIID's own Terms of Use name the exact
entity, its registered address, and its **self-selected governing law** —
California, not the UK, not any EEA state.

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

**Governing law, per the fact established in §1 above:** AIID's own Terms
of Use select California/U.S. law. Applying the identical method E13 §5.1
item 8 already used for AIAAIC ("this file already treats [the rights-
holder's home] law as the governing regime... the same choice of governing
law applies to the copyright question, since it concerns the same
[rights-holder]'s same content") to AIID's California situs rather than
AIAAIC's UK one: **U.S. copyright law governs whether AIID's retained
`title` field is protectable expression.**

U.S. Copyright Office Circular 33 ("Works Not Protected by Copyright")
categorically excludes **"titles, names, short phrases, and slogans"** from
copyright protection — a bright-line rule, not a case-by-case
"author's-own-intellectual-creation" test. This is the exact rule AIAAIC's
headline question (E15/D17) could **not** invoke, because AIAAIC is
UK-situated and UK/EU law (*Infopaq*, *Meltwater*) has no equivalent
categorical carve-out — which is precisely why AIAAIC's headline question
had to go to counsel rather than resolve in-house. For AIID, the categorical
U.S. rule applies directly and disposes of the question: **a bare AIID
`title` field carries no protectable expression under the law AIID itself
selected to govern use of its content.**

**A reinforcing, non-load-bearing observation, already recorded by E23
§2b for a related population and worth noting here too:** even setting the
jurisdictional question aside, AIID's own titles read qualitatively
differently from AIAAIC's. E23 sampled AIID's titles directly (against
`aiid_full.json`, ground truth) and found them to be "plain
subject-verb-object incident labels" — E23's own examples include *"Tesla
on Autopilot TACC Crashed into Van on European Highway"* and *"A Collection
of Tesla Autopilot-Involved Crashes"* — not AIAAIC's colorful editorializing
(scare-quoted phrases, distinctive verbs like "cripples"/"extol"/"swamp"
that E16 §1 identified as the markers pushing toward protection under
*Infopaq*). Even if a UK/EU court somehow applied UK/EU law to AIID content
(a scenario this ruling does not need to reach, given AIID's own
self-selected governing law), the *content itself* looks less likely to
clear *Infopaq*'s bar than AIAAIC's headlines did — and E16 found 42 of 47
of *those* not defensible. This is not the basis for the ruling; it is
noted because it points the same direction as the governing-law finding
rather than cutting against it, which is worth knowing.

**Consistency with the AIAAIC precedent (D2/D17), as the brief asked me to
weigh:** this is not a departure from how the project treats retained
titles — it is the same standard, applied to different facts, yielding a
different result for a principled reason. AIAAIC's headline question stayed
open specifically *because* (a) UK/EU law has no categorical short-phrase
exclusion, and (b) the retained content itself showed AIAAIC's own editorial
choices. Both of those conditions are absent for AIID: (a) is absent
because AIID's own governing law does have that exclusion, and (b) is
absent because AIID's titles read as plain factual labels. The ruling
tracks the precedent's own logic rather than overriding it.

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
  Collaborative, Inc. is a **California** corporation, registered at a
  Sacramento address, with Los Angeles as its stated venue — none of reg
  18(2)'s UK-nexus conditions are met.
- Directive 96/9/EC Art 11 (parallel EU-law test): requires EEA
  nationality/incorporation — also not met by a California corporation.

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
  AIAAIC's was before its marker existed. Verified directly in
  `data/incidents.json` (two sampled rows, `aiid_id` 1 and 2): every
  templated `description` states, in full sentences, **"AI Incident
  Database (AIID) entry #{id}: {title}. ... See the linked AIID entry for
  full narrative, sourcing, and classification"** — a per-row,
  human-readable attribution baked into the shipped text itself, not just a
  separate metadata field — and `references[0]` carries a working link
  (`title: "AIID incident #{id}"`, `url:
  https://incidentdatabase.ai/cite/{id}/`) on every one of these rows.
  `README.md:223` additionally names "AI Incident Database (AIID)" with
  links to both `incidentdatabase.ai` and the GitHub repo at the
  collection level. `NOTICE-DATA:92-107` and `.reuse/dep5:35-42` already
  name AIID's CC BY-SA licensing at the document level. Nothing here needs
  fixing — the finding is a clean "already adequate," not a gap to route.

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
bare title, not protectable expression under the law AIID's own terms
select to govern it, and (b) AIID's maker does not qualify for a UK or EU
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
- **The WebFetch-verification caveat in §1 is a real, not pro forma, open
  point.** Everything in §§2–3 is downstream of AIID's Terms of Use naming
  a California entity and California governing law. I corroborated it with
  an independent `WebSearch`, but neither is a raw-HTML confirmation. The
  exact check is named in §1; until it is run, treat this ruling as
  well-supported but not fully closed, the same posture this document's own
  standing rule would apply to any of my own absence findings, applied here
  to a presence finding instead because the tool's known failure mode is
  the same regardless of which direction the claim runs.
