# E16 / D18 — Per-Row Licensing Review of the 47 Title/Headline Near-Matches

**Task:** D18's second clause — *"The 47 rows at >=0.8 similarity: license-auditor
reviews and rules PER ROW."*
**Scope:** `title` field of the 47 hand-curated `ingest/aiaaic_incidents.json`
rows sitting at >=0.8 normalised similarity to the AIAAIC headline of the
entry they cite, per the foreman-generated join
(`E16-title-join.md`, source cache `ingest/_cache/aiaaic_sheet.csv` sha256
`fa2390ec67669f9b4cb0ac766ec5ce2d4545d8b433d9369701a777fb06dbd2ac`).
**Author:** license-auditor. **Does not write data/schema/board.**
**Concurrency note:** `ingest/aiaaic_incidents.json` was being edited live by a
parallel agent (marker extension + 13-row retitle) while this review was
conducted. Everything below about `title`/`references[].title` **content**
(the wording comparisons) is stable under that edit, because the marker work
adds a `content_license` object and does not touch `title`/`description`/
`references`. Two observations below (the "already-retitled" rows) are
timestamped snapshots of a moving file and are named as such.

---

## 1. The standard applied

**Ruling standard, stated in advance:** *convergent fact-description is
defensible; verbatim (or near-verbatim paraphrase) is not.* The dividing
question for each row: given the underlying facts (actors, amounts,
technology, outcome), would an independent writer describing those same facts
— without AIAAIC's text in front of them — plausibly produce wording this
close, purely because the facts pin down the content? Or does the closeness
carry over AIAAIC's own **editorial choices** — its specific verb, its
clause order, its foregrounding, a quoted/scare-quoted phrase — which are not
the only way the fact could have been said?

Governing law (already on record in this repo, not re-derived here): AIAAIC
is UK-situated and its CC BY-SA grant is the operative one (`SOURCE_LICENSES.md`
§1.1); the US short-phrase carve-out (Circular 33) does not apply in the
UK/EU. *Infopaq* (CJEU C-5/08) allows even an 11-word extract to be protected
where it reflects "the author's own intellectual creation" through choice and
combination of words; *NLA v Meltwater* holds headlines specifically can be
independent works, case by case, no blanket exemption (both already cited on
the board at E15/D17). But bare facts, and expression so constrained by the
facts that there was no real room for a creative choice, remain unprotected —
that is the idea/expression line these rulings turn on.

**Concrete markers used, ordered by how strongly they push toward "not
defensible":**
- **(i) A retained quoted/scare-quoted phrase** copied out of the AIAAIC
  headline (e.g. `'incorrectly'`, `'child pornography'`, `'child porn'`) —
  quotation is AIAAIC's own editorial device, not a fact.
- **(ii) A retained distinctive verb or clause construction** that is not the
  only natural way to phrase the fact (`cripples`, `swamp`, `extol`, `hit
  with`, `recommends X kills himself`, `draws concerns`, `misidentifies`) —
  picking a specific one of several equally natural options is a stylistic
  choice, not a forced consequence of the facts.
- **(iii) A retained clause architecture** (subject/verb/object ordering,
  what's foregrounded vs. appended) even where a noun or two has been
  swapped, added, or dropped.
- Against those: **differences limited to** a synonym swap, an added/dropped
  parenthetical, subtitle, proper noun, or a corrected/updated figure, while
  the rest of the sentence differs in construction too — this is the
  signature of convergence, because the load-bearing facts (who, what,
  amount, technology) are what pin a compressed headline-length sentence
  down, and there is real room for two independent writers to construct that
  sentence differently around the same facts.
- Shared **genre-conventional vocabulary** ("deepfake", "facial recognition",
  "chatbot", "data breach", "scam") common across the whole corpus is never
  itself a mark of copying.

**Three rulings, defined:**
- **DEFENSIBLE — convergent fact-description.** The overlap is concentrated
  in the load-bearing nouns/numbers/proper names; the surrounding verb,
  clause order, or framing differs enough that independent drafting from the
  same facts is the more plausible explanation.
- **NOT DEFENSIBLE — reproduces AIAAIC's editorial expression.** Our title
  retains AIAAIC's specific sentence architecture (the same verb, the same
  clause order, the same foregrounding) essentially unchanged, with only
  cosmetic edits (synonym swap; add/drop a proper noun, number, or
  parenthetical). If you undo the 1–3 word difference, the sentences are the
  same sentence.
- **BORDERLINE (intermediate — used only where genuinely needed).** A
  meaningful share of the sentence has been independently reconstructed
  (different framing, a real added fact) even though a fact-driven core or
  an isolable phrase is still shared. Used for 2 of the 47 (rows 25, 32
  below) where the retained content is closer to convergence than to
  paraphrase but a specific element still gives me pause.

**Corroborating evidence that shaped how I read the close calls:** while
checking each row's real JSON record (not just the join-table strings) I
found that `references[0].title` on the great majority of these same rows
carries AIAAIC's own headline **prefixed `"AIAAIC - "`**, and on **at least
31 of the 47** it is an **exact, word-for-word copy of the current AIAAIC
headline** — separate from, and often more literal than, the `title` field's
own wording (detailed in §4). That means whoever wrote the near-match
`title` had AIAAIC's exact headline sitting in the same record while writing
it. That is affirmative evidence for reading a tight paraphrase as
paraphrase-from-AIAAIC's-text rather than as an independent, coincidental
convergence — precisely the hazard `SOURCE_LICENSES.md` §1.1's
"Derivative-work constraint (D2)" already names: *"AIAAIC-derived summaries
must be written from the primary sources AIAAIC links to — never paraphrased
from AIAAIC's own prose."* Where a row instead shows real independent
redrafting **despite** the exact headline being available in the same
record (rows 39, 40, 43), that is correspondingly stronger evidence for
DEFENSIBLE, not weaker.

---

## 2. Per-row rulings — all 47

| # | source_id | AIAAIC id | ratio | our `title` | AIAAIC `headline` | RULING | Reason |
|---|-----------|-----------|-------|-------------|--------------------|--------|--------|
| 1 | `AIAAIC-proctoru-breach` | AIAAIC0470 | 0.98 | Data breach reveals data of 400,000+ ProctorU users | Data breach reveals data of 440,000 ProctorU users | **Not defensible** | Entire sentence frame retained; only the numeral differs (and note it's a *different* numeral — 400k+ vs 440k — not even a copied fact). |
| 2 | `AIAAIC-singapore-sports-school` | AIAAIC1812 | 0.976 | Singapore Sports School students attacked with AI nude deepfakes | Singapore Sports School students attacked with nude deepfakes | **Not defensible** | Whole clause incl. the specific verb "attacked with" retained; only "AI" inserted. |
| 3 | `AIAAIC-south-korean-arrest-csam` | AIAAIC1186 | 0.972 | South Korean man arrested for using AI to create sexual images of children | South Korean arrested for using AI to create sexual images of children | **Not defensible** | Identical sentence with one word ("man") inserted. |
| 4 | `AIAAIC-megaface` | AIAAIC1555 | 0.972 | MegaFace facial-recognition dataset raises privacy and liability concerns | MegaFace facial recognition dataset raises privacy, liability concerns | **Not defensible** | Word-for-word identical bar punctuation/hyphenation. |
| 5 | `AIAAIC-apple-intelligence-scam-reword` | AIAAIC1873 | 0.963 | Apple Intelligence rewords and prioritises scam messages | Apple Intelligence rewords, prioritises scam messages | **Not defensible** | Word-for-word identical bar "and"/comma. |
| 6 | `AIAAIC-musk-harris-voiceclone` | AIAAIC1616 | 0.953 | Elon Musk shares Kamala Harris voice-clone video ad on X | Elon Musk shares Kamala Harris voice clone video ad | **Not defensible** | Identical sentence, "on X" appended. |
| 7 | `AIAAIC-met-police-youth-worker` | AIAAIC1510 | 0.951 | Youth advocacy worker misidentified by Met Police facial recognition | Youth advocacy worker misidentified by Met Police facial recognition system | **Not defensible** | Identical sentence minus the final word. |
| 8 | `AIAAIC-ai-impersonation-21k` | AIAAIC1006 | 0.945 | AI voice impersonation scams Canadian couple of USD 21,000 | AI impersonation scams Canadian couple of USD 21,000 | **Not defensible** | Identical sentence, one word ("voice") inserted. |
| 9 | `AIAAIC-italian-sora-probe` | AIAAIC1415 | 0.939 | Italian privacy watchdog opens investigation into OpenAI Sora | Italian privacy watchdog opens investigation into Sora | **Not defensible** | Identical sentence and verb phrase; "OpenAI" inserted as a clarifying fact. |
| 10 | `AIAAIC-french-police-fr` | AIAAIC1608 | 0.938 | French national police accused of illegally using facial recognition (Briefcam) | French national police accused of illegally using facial recognition | **Not defensible** | Entire headline retained verbatim as the sentence; parenthetical appended. |
| 11 | `AIAAIC-biden-draft-deepfake` | AIAAIC1163 | 0.935 | President Biden 'calls for US draft' deepfake video | President Biden calls for US draft deepfake | **Not defensible** | Same words, quote-marked and "video" appended — an editorial gloss laid over a copied sentence, not a redraft. |
| 12 | `AIAAIC-venezuela-news-anchors` | AIAAIC0972 | 0.925 | Deepfake news anchors claim Venezuela economic health | Deepfake news anchors extol Venezuela economic health | **Not defensible** | Identical noun phrase/structure; only the verb swapped (a blander synonym for AIAAIC's more colourful "extol") — reads as light editing of a copied sentence, not independent drafting. |
| 13 | `AIAAIC-corsight-gaza` | AIAAIC1413 | 0.925 | Israeli Corsight facial-recognition system misidentifies innocent Gazans | Israel facial recognition system misidentifies innocent Gazans | **Not defensible** | Core clause "___ facial recognition system misidentifies innocent Gazans" retained; "Corsight" inserted as an added fact. |
| 14 | `AIAAIC-eric-adams-robocalls` | AIAAIC1148 | 0.921 | NYC mayor Eric Adams robocalls residents using AI audio deepfakes | NYC mayor Eric Adams robocalls residents with audio deepfakes | **Not defensible** | Near-identical sentence; one preposition/insert swapped. |
| 15 | `AIAAIC-cursor-fake-policy` | AIAAIC1956 | 0.909 | Cursor AI support agent invents user policy, causing user revolt | Cursor AI support agent invents user policy, causing uproar | **Not defensible** | Long, distinctive sentence retained wholesale bar the final noun. |
| 16 | `AIAAIC-chatgpt-leaky-code` | AIAAIC1158 | 0.902 | ChatGPT writes code that makes databases leak sensitive information | Study: ChatGPT writes code that makes databases leak sensitive info | **Not defensible** | Whole sentence retained; only the "Study:" label dropped and "info"→"information". |
| 17 | `AIAAIC-brosnan-art-gallery` | AIAAIC1907 | 0.899 | Deepfake Pierce Brosnan scam cripples Nottingham art gallery | Deepfake Pierce Brosnan scam cripples art gallery | **Not defensible** | Retains the distinctive verb "cripples" (not a forced choice) plus the whole surrounding sentence; "Nottingham" inserted. |
| 18 | `AIAAIC-nudification-telegram` | AIAAIC1774 | 0.897 | AI nudification bots swamp Telegram | Studies: AI nudification bots swamp Telegram | **Not defensible** | Identical bar the dropped "Studies:" label, incl. the distinctive verb "swamp". |
| 19 | `AIAAIC-software-engineers-suit` | AIAAIC1222 | 0.892 | Software engineers sue OpenAI, Microsoft for violating personal privacy (Copilot training) | Software engineers sue OpenAI, Microsoft for violating personal privacy | **Not defensible** | Entire headline retained verbatim as the sentence; parenthetical appended. |
| 20 | `AIAAIC-nomi-al-nowatzki` | AIAAIC1901 | 0.889 | Nomi AI chatbot recommends Al Nowatzki kills himself | Nomi AI chatbot recommends podcast host Al Nowatzki kills himself | **Not defensible** | One of the clearest cases: the unusual, specific construction "recommends [X] kills himself" is not a forced way to phrase this fact and is retained in full; only "podcast host" dropped. |
| 21 | `AIAAIC-clearview-ukraine` | AIAAIC0850 | 0.885 | Ukraine decision to use Clearview AI facial recognition draws concerns | Ukraine use of Clearview AI facial recognition draws concerns | **Not defensible** | Retains the specific construction "___ draws concerns" (one of many equally natural options) plus the rest of the sentence; "decision to" inserted. |
| 22 | `AIAAIC-mrbeast-iphone-scam` | AIAAIC1130 | 0.881 | Deepfake MrBeast iPhone giveaway scam on TikTok | Deepfake MrBeast iPhone giveaway scam | **Not defensible** | Entire headline retained verbatim as the sentence; "on TikTok" appended. |
| 23 | `AIAAIC-laion-5b-csam` | AIAAIC1249 | 0.881 | Child sexual abuse images discovered in LAION-5B training dataset | Child sex abuse images discovered on LAION-5B dataset | **Not defensible** | Distinctive agentless-passive construction "___ images discovered [on/in] LAION-5B ... dataset" retained; only minor synonym/preposition edits. |
| 24 | `AIAAIC-mary-nightingale-scam` | AIAAIC1660 | 0.879 | Mary Nightingale likeness used in AI-generated deepfake scam | Mary Nightingale likeness used in deepfake scam | **Not defensible** | Identical construction "[Name] likeness used in ___ scam"; "AI-generated" inserted. |
| 25 | `AIAAIC-telegram-deepfake-bot` | AIAAIC0347 | 0.873 | Telegram bot creates non-consensual deepfake porn at scale | Telegram AI bots create non-consensual deepfake porn | **Borderline** | Shares the fact-driven noun phrase "non-consensual deepfake porn", but singular/plural bot framing differs and "at scale" is a genuine independent addition — real, if partial, redrafting. |
| 26 | `AIAAIC-clearview-glasses` | AIAAIC0483 | 0.87 | Clearview AI tests live facial-recognition cameras and AR glasses | Clearview AI tests live facial recognition cameras | **Not defensible** | The entire headline ("Clearview AI tests live facial recognition cameras") is retained verbatim as a prefix; "and AR glasses" appended. |
| 27 | `AIAAIC-chatgpt-gdpr-correction` | AIAAIC1469 | 0.87 | ChatGPT said to violate GDPR by not correcting inaccurate personal info | ChatGPT accused of violating GDPR by not correcting inaccurate personal information | **Not defensible** | The specific, non-obvious legal-framing clause "by not correcting inaccurate personal info[rmation]" is retained; only the opening verb phrase paraphrased. *(Side note, outside licensing: "said to" vs. "accused of" softens an allegation into something closer to assertion — an accuracy/register drift worth a separate look, not resolved here.)* |
| 28 | `AIAAIC-swinney-deepfake` | AIAAIC1474 | 0.865 | Deepfake John Swinney 'thanks Nicola Sturgeon' video | Deepfake John Swinney thanks Nicola Sturgeon for his election | **Not defensible** | Core clause "Deepfake John Swinney thanks Nicola Sturgeon" retained verbatim; quote-marked and "video" appended, causal clause dropped. |
| 29 | `AIAAIC-civitai-csam` | AIAAIC1243 | 0.862 | CivitAI generates synthetic 'child pornography' images | CivitAI accused of generating synthetic 'child pornography' images | **Not defensible** | Retains AIAAIC's own scare-quoted phrase `'child pornography'` verbatim — a clear editorial device, not a fact — and drops "accused of" (also a separate accuracy concern: turns an allegation into an assertion). |
| 30 | `AIAAIC-cadillac-fairview` | AIAAIC0148 | 0.861 | Cadillac Fairview covertly uses facial recognition to monitor shoppers | Cadillac Fairview discovered to be covertly using facial recognition to monitor shoppers | **Not defensible** | Retains the distinctive adverb "covertly" and the full object phrase "facial recognition to monitor shoppers"; only "discovered to be ... using" compressed to "uses". |
| 31 | `AIAAIC-italy-bans-chatgpt` | AIAAIC1206 | 0.857 | Italy bans ChatGPT over GDPR privacy concerns (Garante) | Italy bans ChatGPT over data privacy concerns | **Not defensible** | Retains the specific frame "Italy bans ChatGPT over ___ concerns"; "data"→"GDPR" swap, "(Garante)" appended. |
| 32 | `AIAAIC-nz-pensioner-224k` | AIAAIC1788 | 0.852 | New Zealand pensioner loses NZD 224,000 to deepfake Luxon Bitcoin scam | Pensioner loses NZD 224,000 to deepfake Bitcoin scam | **Borderline** | The numeric/currency skeleton is fact-forced, but "New Zealand" and "Luxon" (the specific PM named) are genuine independent additions not in AIAAIC's own headline — meaningful original content layered on a shared fact core. |
| 33 | `AIAAIC-nomi-violence` | AIAAIC1939 | 0.85 | Nomi AI companion bot incites self-harm, sexual violence, terror attacks | Nomi AI companion bot faces scrutiny for inciting self-harm, sexual violence, terror attacks | **Not defensible** | Retains AIAAIC's own enumerated list, in AIAAIC's own order, verbatim — a real editorial selection, not a forced fact. *(Side note: "faces scrutiny for inciting" → "incites" also turns an allegation into an assertion — accuracy concern outside licensing scope.)* |
| 34 | `AIAAIC-chatgpt-bug-history` | AIAAIC0985 | 0.842 | ChatGPT Redis bug exposes user chat histories and payment data | ChatGPT bug exposes user chat histories, payment info | **Not defensible** | Retains "___ bug exposes user chat histories ... payment ___" wholesale; "Redis" inserted. |
| 35 | `AIAAIC-chatgpt-leaks-user-convos` | AIAAIC1120 | 0.841 | ChatGPT leaks user conversations and personal information across sessions | ChatGPT leaks user conversations, personal information | **Not defensible** | Opening clause and core noun phrase identical to the headline; "across sessions" appended as an independent technical detail. |
| 36 | `AIAAIC-cense-ai-leak` | AIAAIC0315 | 0.841 | Cense AI exposes 2.5 million personal records on open database | Cense AI exposes 2.5 million personal records | **Not defensible** | Entire headline retained verbatim as a prefix; "on open database" appended. |
| 37 | `AIAAIC-replika-italy-ban` | AIAAIC1178 | 0.839 | Replika hit with data-processing ban in Italy over child-safety concerns | Replika hit with data ban in Italy over child safety | **Not defensible** | Retains the specific construction "hit with ___ ban in Italy over child safety" (not the forced way to phrase a regulatory sanction) essentially unchanged. |
| 38 | `AIAAIC-chatgpt-walters-defamation` | AIAAIC1208 | 0.835 | ChatGPT falsely accuses Mark Walters of fraud and embezzlement (US defamation suit) | ChatGPT falsely accuses Mark Walters of fraud, embezzlement | **Not defensible** | Entire headline retained verbatim as a prefix, incl. the verb "falsely accuses"; parenthetical appended. |
| 39 | `AIAAIC-taylor-swift-lecreuset` | AIAAIC1293 | 0.831 | Deepfake Taylor Swift fake Le Creuset cookware giveaway scam | Deepfake Taylor Swift offers free Le Creuset cookware scam | **Defensible** | The specific descriptive phrase differs ("fake ... giveaway" vs. "offers free") — a genuine independent word choice for the same "free item" concept; what's shared (celebrity + product name) is fact. Notably, `references[0].title` on this row already quotes AIAAIC's exact headline verbatim, so the writer had it in hand and still chose different wording for `title` — real redrafting, not coincidence. |
| 40 | `AIAAIC-chatgpt-opencage` | AIAAIC0958 | 0.828 | ChatGPT falsely tells users OpenCage offers reverse-phone-lookup service | ChatGPT falsely accuses OpenCage of 'phone lookup' service | **Defensible** | Different verb ("tells users ... offers" vs. "accuses ... of"), and AIAAIC's scare-quoted `'phone lookup'` is not retained — replaced with our own coined "reverse-phone-lookup". The high character-ratio here is largely shared-keyword coincidence (company name, "phone lookup"), not shared sentence architecture — a case where the ratio overstates the real overlap (see §5). |
| 41 | `AIAAIC-energy-243k-voice-clone` | AIAAIC0227 | 0.825 | Fraudsters clone CEO voice to steal USD 243,000 from UK energy firm | Fraudsters clone CEO voice to steal USD 243,000 | **Not defensible** | AIAAIC's entire headline is contained verbatim as the title's prefix, word for word; "from UK energy firm" appended. |
| 42 | `AIAAIC-civitai-deepfakes` | AIAAIC1190 | 0.816 | CivitAI rewards deepfakes of real people via 'bounty' system | CivitAI rewards deepfakes of real people | **Not defensible** | AIAAIC's entire headline retained verbatim as the title's prefix; "via 'bounty' system" appended. |
| 43 | `AIAAIC-clearview-ai` | AIAAIC0320 | 0.816 | Clearview AI mass facial-recognition scraping | Clearview AI facial recognition | **Defensible** | AIAAIC's own "headline" here is a bare 4-word label (company + generic product category) — closer to a directory entry than an authored headline, with little room for the *Infopaq* "author's own intellectual creation" to live in. Our title independently adds "mass ... scraping", a real characterisation not in AIAAIC's text (and `references[0].title` again shows the exact bare headline was available and *not* copied into `title`). |
| 44 | `AIAAIC-thomson-fraud-detect` | AIAAIC1288 | 0.814 | Thomson Reuters Fraud Detect 'incorrectly' identifies fraud against welfare claimants | Thomson Reuters Fraud Detect 'incorrectly' identifies fraud | **Not defensible** | Retains AIAAIC's own scare-quoted `'incorrectly'` verbatim as part of an otherwise-fully-copied headline; "against welfare claimants" appended. |
| 45 | `AIAAIC-remini-csam` | AIAAIC1100 | 0.811 | Remini AI photo enhancer generates 'child porn' from innocent photos | Remini AI photo enhancer generates 'child porn' | **Not defensible** | Retains AIAAIC's own scare-quoted `'child porn'` verbatim as part of an otherwise-fully-copied headline; "from innocent photos" appended. |
| 46 | `AIAAIC-slovakia-audio` | AIAAIC1137 | 0.805 | Deepfake audio claims Slovakian opposition leaders tried to rig election | Deepfake audio recording claims opposition leaders tried to rig Slovakian election | **Not defensible** | Retains the specific, non-obvious verb chain "claims ... tried to rig" wholesale; "recording" dropped, "Slovakian" relocated. |
| 47 | `AIAAIC-chatgpt-psychosis` | AIAAIC2110 | 0.804 | ChatGPT drives Jacob Irwin into psychosis ('AI-induced delusion') | ChatGPT drives Jacob Irwin into psychosis | **Not defensible** | AIAAIC's entire headline retained verbatim as the title's full prefix; our own parenthetical appended. |

No mis-joins found. I checked every pair against the described event (not just
the string) and all 47 describe the same real-world incident as the AIAAIC
entry they're joined to — including the cases that could look like
conflation at a glance (Nomi's two separate entries — general incitement
AIAAIC1939 vs. the named-victim case AIAAIC1901 — and Clearview's three
separate entries — general scraping AIAAIC0320, Ukraine AIAAIC0850, AR
glasses AIAAIC0483 — are each correctly matched to a distinct AIAAIC ID for a
distinct incident, not duplicated).

---

## 3. Counts, and what follows

| Ruling | Count | Rows |
|---|---|---|
| Not defensible (reproduces AIAAIC's editorial expression) | **42** | 1–24, 26–31, 33–38, 41–42, 44–47 |
| Borderline | **2** | 25, 32 |
| Defensible (convergent fact-description) | **3** | 39, 40, 43 |

**This is a much higher not-defensible rate than the board's framing of
"near-identical titling... can be convergent" may have anticipated.** On the
standard above, the overwhelming majority of the 47 are not independent
convergence — they are AIAAIC's own sentence, lightly edited (a word added,
dropped, or swapped), and the `references[0].title` evidence (§4) supports
reading them that way rather than as coincidence.

**Does the row-level `content_license` marker suffice for a "not defensible"
row, or does it need retitling too? — This is a finding for the foreman to
escalate to the user, not something I am resolving.** D18 scoped retitling
to the 13 EXACT-band rows only, on the premise that the 47 near-matches
might turn out to be convergent and not need it. My per-row reading finds
42 of them are not convergent by the same reasoning the board already used
to justify retitling the 13. Two remedy paths, costed:

- **(a) Marker-only (extend current scope no further).** Cost: zero —
  already running, already being extended to all 95 rows. Risk: leaves
  AIAAIC's own sentence, lightly edited, presented as our own `title` field
  on 42 rows — the same fact pattern the board already judged worth fixing
  for the 13 rows at ratio 1.0, just at ratio 0.80–0.98. Treating 0.98 and
  1.0 differently is hard to justify once the actual pairs are read (row 1,
  at 0.98, differs from its EXACT-band neighbours only in that the two texts
  happen to cite different numerals for the same fact).
- **(b) Extend retitling to the 42 not-defensible rows (my recommendation,
  if the project's goal is to minimize the marker's *need* to be invoked
  rather than to rely on it as the sole remedy).** Same mechanism already
  built for the 13 (project-authored replacement title; original preserved
  via the invariant-3 tombstone/conflict-note mechanics, never deleted).
  Cost: ~3.2x the row-count already scoped, no new engineering pattern.
  Benefit: closes the exposure at the field that is actually presented as
  our own editorial content, consistent with the Derivative-work constraint
  (D2) and with §1's finding that most of these are paraphrase, not
  convergence.
- The **2 borderline rows (25, 32)** are lower-priority either way — real
  independent content exists in both; marker-only is a reasonable resting
  point, retitling is optional polish.
- The **3 defensible rows (39, 40, 43)** need no title change. The
  row-level marker (already applying to all 95 regardless of title
  wording) is the correct and sufficient treatment.

**I am flagging this as a "needs retitling" finding, not assuming it will
happen** — per the brief's own instruction, this is the foreman's call to
bring to the user.

---

## 4. A field beyond `title` that carries AIAAIC content — found while checking these 47

**This was not itself in the 47-row brief, but the brief asked me to record
any other field on these 95 rows carrying AIAAIC-derived content, and I found
one.** Every one of the 47 rows' `references[0].title` is a *second*,
independent rendering of AIAAIC's headline, always literally prefixed
`"AIAAIC - "` in the JSON. I checked all 47 against the join table's
`AIAAIC headline` column and against the actual JSON text:

- On **at least 31 of the 47** (rows 2–7, 9–11, 13, 15–19, 22–24, 28, 36–47
  minus the 3 defensible ones — full list available on request, this is a
  by-hand count), `references[0].title` is an **exact, word-for-word copy**
  of the current AIAAIC headline (module a stripped `"Study:"`/`"Studies:"`
  label prefix in 2 cases) — **even on rows where `title` itself is only a
  near-match**, and even on the 3 rows I ruled defensible (39, 40, 43),
  where `title` diverges meaningfully from AIAAIC's wording but
  `references[0].title` does not.
- On the remainder, `references[0].title` is itself a third variant (neither
  exactly our `title` nor exactly the current sheet headline) — most simply
  explained by AIAAIC having edited its own headline sometime between when
  this reference was written and when the sheet was last cached for the
  join (a possibility I could not rule out or confirm without a live/archived
  fetch of AIAAIC's page history — flagged, not resolved, see §6).
- I spot-checked this pattern **outside the 47** too: it holds on 3 sampled
  EXACT-band rows, on 7 sampled 0.6–0.8-band rows, on 4 sampled <0.6-band
  rows, and on all 3 UNJOINED rows. It looks structural to the whole 95-row
  hand-curated set (an artefact of `ingest/aiaaic_incidents.json`'s reference
  construction always rendering `"AIAAIC - " + <the source's own title
  text>`), not particular to the 47.

**Read on risk:** `references[0].title` is always explicitly labelled as
AIAAIC's own text (the `"AIAAIC - "` prefix), so it reads as a citation, not
as an assertion of our own editorial voice — a materially different risk
posture than an unattributed `title` field, and normal, expected bibliographic
practice (quoting a cited work's own title). It is still, however, literal
verbatim reproduction of AIAAIC's protected headline text, which is exactly
the kind of content the row-level `content_license` marker exists to flag —
and because the marker in the JSON I read is attached at the **row** level,
not scoped to a specific field, it appears to already cover this field too.
**I am not certifying that as settled** — I did not see the marker's design
spec, only its JSON shape, and this is exactly the kind of "does the design
suffice" question that belongs to red-reviewer/pipeline-engineer, not to me.

**A concrete, time-sensitive observation from the live file.** Two of the 13
EXACT-band rows had already been retitled by the parallel agent as of my
read (`AIAAIC-audio-deepfake-ceo` → *"Attacker impersonates company CEO with
AI voice clone to authorize fraudulent transaction"*;
`AIAAIC-character-ai-suicide` → *"Teen's death by suicide follows
months-long bond with a Character.AI companion persona"*). On **both**, the
row's `title` field no longer matches AIAAIC's headline — but
`references[0].title` still reads, verbatim and unchanged, `"AIAAIC - Audio
deepfake fraudulently impersonates CEO"` and `"AIAAIC - Boy commits suicide
after relationship with Character AI chatbot"` respectively (the second has
a minor punctuation drift — "Character AI" vs. "Character.AI" — from the
current sheet's own headline, consistent with the drift note above). **This
is not a defect** if `references[0].title`'s citation-of-AIAAIC's-own-title is
the intended, permanent design (it is normal to cite a source by its own
title even after you've retitled your own record) — but it does mean
retitling `title` does **not**, and was never going to, remove AIAAIC's
verbatim headline text from the row entirely; it only removes it from the
field asserted as our own. **Exact requirement for the foreman to route:**
`docs/SOURCE_LICENSES.md` §1.1 and whatever comment/doc accompanies the
`content_license` marker's implementation should say explicitly that
`references[].title` on AIAAIC-citing rows is expected to carry AIAAIC's own
title text as a citation, is covered by the same row-level marker, and is
**not** touched or expected to be touched by the 13/42-row retitle — so a
future editor doesn't read an untouched reference title as a sign the
retitle failed. **Exact check for red-reviewer:** `grep -c '"title": "AIAAIC
- '` (or equivalent) against `ingest/aiaaic_incidents.json` post-merge,
cross-referenced against the 95 AIAAIC-citing row count, to confirm this
field's presence/format is uniform across all 95 and that the marker's own
scope statement (wherever pipeline-engineer records it) names this field
explicitly rather than only `title`/`description`.

---

## 5. Is >=0.8 the right line?

**No — on the evidence, it is set too high, and the ratio itself is an
imperfect proxy for the actual question.** Two separate problems:

**(a) The cutoff draws an arbitrary line through what is otherwise one
continuous population.** I read the four highest-ratio rows in the 0.6–0.8
band directly from the JSON (not just the join-table strings), because they
sit within 0.01–0.02 of the 0.8 boundary:

- `AIAAIC-muah-companion-hack` (0.797): *"Muah AI companion app hack reveals
  attempts to simulate child abuse"* vs. headline *"AI companion app Muah
  hack reveals users trying to simulate child abuse"* — same clause
  ("companion app Muah hack reveals ... to simulate child abuse") reordered
  and lightly trimmed. Would rule **not defensible** under §1's standard,
  the identical reasoning that ruled 42 of the 47 above it.
- `AIAAIC-maxpread-fake-ai-ceo` (0.796): title vs. headline *"Maxpread
  Technologies fake AI CEO investment scam"* — `references[0].title`
  ("AIAAIC - Maxpread Technologies fake AI CEO scam") confirms the full
  clause was available verbatim; title swaps one near-synonym ("fabricated"
  for "fake") and drops "investment". Same pattern as the >=0.8 band's
  not-defensible rows.
- `AIAAIC-xtwitter-swift-images` (0.791) and `AIAAIC-korean-schools-deepfake`
  (0.791): both retain their AIAAIC headline's full clause ("X/Twitter fails
  to remove ... AI images of Taylor Swift"; "Deepfake porn engulfs ...
  Korean schools") with one or two words swapped or appended. Same pattern.

All four would rule **not defensible** by the identical standard applied
above, and are separated from row 47 (ratio 0.804) by a difference (0.007–
0.013) that is well within the noise of how `SequenceMatcher` scores minor
rewording. **The 0.8 cutoff was picked before anyone had read the pairs (per
the brief), and reading them shows the qualitative line does not sit at
0.8** — on this sample it sits measurably lower, likely into the high end of
the 0.6–0.8 band generally, though I have only directly verified these 4 of
the 19 and am not claiming coverage of the rest (see caveat below).

**(b) The ratio is a flawed proxy in both directions.** Two rows in the >=0.8
band I ruled **defensible** (39 at 0.831, 40 at 0.828) sit *above* several
rows I would expect to rule not-defensible in the lower band — because
`SequenceMatcher`'s character-level ratio rewards shared keywords/proper
nouns/company names even where the sentence architecture and verb choice
have been substantially reworked (row 40's ratio is inflated by "ChatGPT",
"OpenCage", and "phone lookup" appearing in both texts despite genuinely
different verbs and no retained quotation). The ratio measures character
overlap, not retained editorial expression — the two are correlated but not
identical, and this row pair is direct proof the correlation breaks down in
both directions.

**What I did not do:** rule all 19 of the 0.6–0.8 band or all 13 of the
<0.6 band individually — that was explicitly not asked. I read the 4 rows
above directly from JSON; for the rest of the 0.6–0.8 band and the whole
<0.6 band I relied on the join table's strings only (not a fresh JSON pull),
and on that basis nothing else in either band looked like an inversion (a
low-ratio row hiding a verbatim/near-verbatim retained clause) — but that is
a lighter-touch check than the one behind the four rows named above and
behind the 47-row table in §2, and I am stating that difference plainly
rather than implying equal coverage. **Recommendation:** if the project
wants a defensible, complete answer rather than a threshold picked in
advance, the same per-row method in §1 should be applied to the 0.6–0.8 band
at minimum — cheap, since it's 19 rows and the method is already built.

---

## 6. The 3 UNJOINED rows — not covered by this review

`AIAAIC-miami-pinecrest`, `AIAAIC-c4-dataset`, `AIAAIC-books3-dataset` could
not be joined to any row in the cached AIAAIC sheet by the foreman's
URL-slug method. I read all three directly in `ingest/aiaaic_incidents.json`
(all three already carry the `content_license` marker as of my read) — their
`title` fields are original-sounding, fact-dense sentences, but **I have no
AIAAIC headline to compare them against, so their titles are unchecked
against any headline and this review makes no claim about them either way.**
If a live/uncached fetch of AIAAIC's sheet or site later resolves a headline
for these three, they should go through the same §1 standard before being
treated as settled.

---

## 7. What I did not check / limitations, stated plainly

- **Headline drift over time.** Several `references[0].title` values are
  close-but-not-exact matches to the *current* cached sheet headline (e.g.
  row 25's, row 32's, row 26's). I could not rule out that AIAAIC has edited
  its own headline since these rows were curated — I have no shell and did
  not attempt a Wayback Machine/archived-page check. Where this matters it
  is noted inline in §2/§4; it does not change any ruling above, since my
  rulings compare against the headline the join table supplied as current,
  but it means the true historical overlap at time-of-writing could differ
  from what I assessed against today's sheet.
- **The concurrent edit.** `ingest/aiaaic_incidents.json` was being actively
  edited by the parallel agent while I read it. Content comparisons
  (title/description/references wording) are unaffected by that edit (the
  marker addition doesn't touch those fields), but any statement above about
  which rows currently carry a `content_license` marker, or which of the 13
  are currently retitled, is a snapshot at read-time, not a verified final
  state — red-reviewer should re-check the merged file's actual state, not
  rely on this document for that.
- **`description` fields.** I read all 47 descriptions directly (shown
  alongside `title`/`references` in my working notes, not reproduced in
  full above for length) and none of them read as a paraphrase of AIAAIC's
  own prose — they are longer, more detailed, and structured differently
  from anything AIAAIC's headline-only join data exposes me to; I have no
  AIAAIC narrative-cell text to compare them against directly (D2 already
  restricts the ingest from ever fetching that cell), so this is a
  plausibility read, not a verified clearance.
- **Full 95-row field sweep.** I sampled `references[0].title` across all
  four bands plus the UNJOINED rows (18 of the 95 rows checked directly in
  JSON, including all 47 in scope) and found the same pattern everywhere I
  looked; I have not read all 95 rows' full JSON, so "structural to the
  whole 95" in §4 is an inference from a broad but partial sample, not an
  exhaustive count. The exact check named in §4 closes this gap cheaply.

---

## Summary for the foreman

- **42 not defensible, 2 borderline, 3 defensible** of the 47 (§2–§3).
- **Escalate to the user:** whether retitling extends to the 42
  not-defensible rows (marker-only leaves AIAAIC's own sentence, lightly
  edited, in the `title` field on those rows) — costed options in §3.
- **New finding, outside the 47:** `references[0].title` independently
  carries AIAAIC's headline (exact on ≥31/47 sampled, structural across the
  95-row set) — likely already covered by the row-level marker, but
  unconfirmed by me; exact doc-language requirement and exact grep check for
  red-reviewer are in §4, including the concrete cross-field gap observed on
  the 2 rows already retitled.
- **Threshold finding:** 0.8 is set too high; at least 4 named rows in the
  0.6–0.8 band read as not-defensible by the identical standard, and 2 rows
  in the >=0.8 band read as defensible despite a higher ratio than those 4 —
  the ratio is a correlated but imperfect proxy in both directions (§5).
- **Not covered:** the 3 UNJOINED rows (§6); the 15 not directly re-checked
  in the 0.6–0.8 band and all 13 of the <0.6 band beyond the join-table
  strings; any headline-drift-over-time question (§7).
