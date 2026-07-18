# Foreman answers — E13 assessment + WS0-T3 re-scoped spec (session resume 2026-07-18)

**Author:** foreman (main session). **Purpose:** answer the six specific
questions the user posed on session resume (queue steps 3 and 4) as
decision-support *before* the user chooses the E13 direction. Grounded in
`docs/audits/WS0-E13-database-right-2026-07-18.md` and
`docs/specs/WS0-T3-rescoped-2026-07-18.md`; anchors cited inline. Committed
before being shown, per the committed-artifact working agreement.

**Not** new legal analysis and **not** a decision — E13 remains a
needs-qualified-counsel escalation with three user options (engage counsel /
conservative redesign / knowingly accept residual risk). These answers only
read out what the two committed files already establish, so the user can
choose with the load-bearing points in one place.

---

## Step 3 — from the E13 assessment

### (a) CC BY-SA 4.0 §4(b): does including a substantial portion of a BY-SA database's contents make OUR database Adapted Material, so ShareAlike attaches at the database level rather than per-fact?

**Yes — that is exactly §4(b)'s operative effect — but conditional on two
predicates, and it does not by itself *resolve* the question (still counsel).**

Per E13 §4 (quoting the CC BY-SA 4.0 legal code): §4(b) says that if you
include all or a substantial portion of the database contents "in a database in
which You have Sui Generis Database Rights, then the database in which You have
Sui Generis Database Rights (but not its individual contents) is Adapted
Material, including for purposes of Section 3(b)." Applied here, §4(b) makes
**our whole corpus — not merely the extracted AIAAIC rows — "Adapted Material,"
so the ShareAlike condition (§3(b), via the Adapter's-License mechanics) runs
against the corpus *as a database*, not against a quarantinable AIAAIC-derived
subset.** That is materially broader than a §4(c)-only reading, which one might
otherwise hope to confine to "just the AIAAIC fields." §4(b) forecloses that
narrower reading.

The two predicates that must both hold for §4(b) to bite (E13 §4(b) analysis):
1. **Our extraction is substantial** — E13 §2 finds this more-likely-than-not
   (~1,513 rows ≈ 76% of AIAAIC's ~1,995-row live repository, plus the
   repeated-ingest aggregation rule).
2. **Our corpus itself holds a sui generis database right** — E13 finds this
   *plausible* (the corpus is built through the same obtaining/verifying/
   presenting investment that grounds AIAAIC's own right) but **not
   independently confirmed**; it is counsel question 7 (E13 §5.1).

So: at the database level, yes — and this is a *distinct and more serious*
question than the per-fact §4(c) one, which is precisely why E13 routes it to
counsel as its own question (7) rather than treating §4(c) as the whole story.
The net effect: the "no BY-SA subset / one clean CC-BY-4.0" design goal is
**not currently achieved for the AIAAIC-derived fields**, and under §4(b) the
obligation may not even be confinable to those fields.

### (b) Repeated and systematic extraction of insubstantial parts — our weekly refresh is exactly that pattern; does per-entry reduction dispose of it?

**No.** Per-entry reduction (facts+link) does **not** dispose of the reg
16(2) / Directive Art 7(5) repeated-and-systematic rule.

Per E13 §2 (aggregation via repeated ingest): *Directmedia* (C-304/07) and
*Innoweb* (C-202/12) hold that a standing, systematic extraction mechanism run
over time — one that cumulatively reconstructs a substantial part — is caught
**even without any single bulk-copy event**. Our scheduled recurring pull of the
AIAAIC sheet is exactly that shape. **The recurring cadence is an *aggravating*
fact under this line of case law, not a mitigating one** — it is the paradigm
"insubstantial-extraction-by-degrees" the rule was written to stop.

Reducing each row to categorical facts shrinks the *volume taken per row* but
does not change the *systematic-mechanism* character the rule targets. And it is
close to moot on the current numbers anyway: E13 §2 finds we are very likely
**already over the substantiality line on a single snapshot** (~76% share), so
the aggregation rule is belt-and-suspenders rather than the only route to
"substantial."

### (c) Does the assessment keep infringement distinct from licence-condition compliance?

**Yes — cleanly, and the relationship between the two is the assessment's
central mechanism.** E13 §4 lays out the fork explicitly:

- **Infringement branch (property right, reg 16).** If the extraction is
  *insubstantial*, reg 19(1) gives any lawful user of a published database an
  **unwaivable** entitlement to extract insubstantial parts "for any purpose"
  (reg 19(2) voids any contrary contract term). No infringement, **no licence
  needed, no ShareAlike** — the CC BY-SA conditions are never triggered.
- **Licence-condition branch (§4(c)/§3(a)).** If the extraction is
  *substantial*, the only plausible authority to extract AIAAIC's contents *at
  all* is CC BY-SA §4 — and invoking that grant carries its **ShareAlike +
  attribution conditions** with it (and, per (a), possibly at the database
  level via §4(b)).

The assessment therefore treats "did we infringe the database right" and "are
we complying with the licence grant that would cure that infringement" as two
distinct questions, and shows they **meet at the substantiality threshold**:
below it, no licence is needed; above it, the licence is the only cover and its
conditions attach. There is "no licence-free third option" (E13 §4) — that
conclusion only makes sense because the two regimes are kept separate.

---

## Step 4 — on `docs/specs/WS0-T3-rescoped-2026-07-18.md`

### (a) Does the delta gate require ZERO taxonomy deltas versus a2d7a26e — exact reproduction of the pre-cut mapping set, not merely similar?

**Yes — verbatim.** Spec §2(c): *"The gate requires **ZERO taxonomy deltas vs
`a2d7a26e` — exact set equality per entry (identical mapping sets), not merely
similar distributions.**"* The enumerated fields — `attack_vector`,
`owasp_llm`, `owasp_asi`, `mitre_atlas`, `mitre_atlas_tactics`, `nist_ai_rmf`,
`owasp_dsgai`, `severity`, `corpus`, `quality_tier`/`tier`, and
`landmark_count` — must be **byte-for-byte unchanged**. The *only* permitted
deltas are the `description` text (in both `data/incidents.json` and
`ingest/aiaaic_sheet_incidents.json`), the new `aiaaic_ethical_tags`, and
`description_provenance` / `description_source`.

**One caveat the spec itself flags (§2(c) caveat), which the user should weigh
before dispatch:** `a2d7a26e`'s *own* published labels were partly
prose-derived — the cascade showed HEAD held `attack_vector` values the current
ingest code no longer emits. So reproducing them *exactly* may require the
re-scoped seed to **replicate the old prose-derived mapping logic** out of
`aiaaic_ethical_tags`. The gate is genuinely "zero," but hitting exactly-zero
is non-trivial because the baseline is itself a prose-coupled artifact. The spec
requires any residual divergence to be **either reconciled as a defect or
enumerated and justified as intended — never silent.** That is the right
posture, but it means "zero unintended deltas" is doing real work: some deltas
may turn out to be *intended* (correcting a prose-coupled mislabel), and those
must be argued explicitly, not waved through.

### (b) Is the landmark_count -164 third derivation path root-caused, and is landmark status inside the delta gate?

**Both yes.**

- **Root-caused.** The landmark path is identified as **Path B** in spec §2(a)
  and in the cascade audit: `_classify_corpus()` (`merge_and_dedupe.py:534`,
  applied `:1358`) reads the *published* description; the
  description→`corpus` classification drove an `ai-harm`→`security`
  reclassification on 164 entries, which via `_derive_tier()` (`:161`) dropped
  their landmark status — moving published `landmark_count` **1865→1701
  (−164)**. This is the "third derivation path" beyond Path A
  (description→`attack_vector`→OWASP/ATLAS/NIST). It is understood and its
  mechanism is written down.
- **Inside the gate.** Spec §2(c) lists `corpus`, `quality_tier`/`tier`, **and**
  `landmark_count` among the fields that must be byte-for-byte unchanged, and
  `landmark_count` is an explicit line in the acceptance checklist (§5). Per-
  entry landmark *status* is pinned transitively — it is derived from `corpus` +
  `tier`, both of which are under per-entry set-equality lock — and the
  aggregate `landmark_count` is checked directly on top. *Minor foreman note for
  the implementer (not a gap in the spec):* the direct assertion is on the
  aggregate count plus the two determinant fields; if it is cheap, also
  asserting the per-entry landmark boolean directly would make the intent
  unmistakable. As written the status is already covered.

### (c) Is the validation sample specified as a committed file produced BEFORE the batch runs?

**Yes — verbatim.** Spec §2(d): *"Before the batch runs, produce a **committed**
validation sample of **15–20 AIAAIC entries showing the actual content of all
eight source cells** ... alongside the resulting reduced `description` ... This
is a file under `docs/audits/` or `docs/samples/`, **not** chat output."*
Reinforced in the acceptance checklist (§5): *"Validation sample (15–20 entries,
all eight cells) committed before batch."* Committed file, all eight cells,
before the batch — exactly as the committed-artifact and field-level-delta
working agreements require.

---

## Foreman summary for the direction choice

- **The spec's implementation gates (step 4) are all correctly specified** —
  zero-delta with set equality, the landmark path root-caused and gated, the
  validation sample committed-before-batch. If the user picks a direction that
  keeps the current WS0-T3 ingest shape (facts+link with controlled-vocab
  tags), the spec is ready to dispatch as written. The one thing to go in
  clear-eyed about: exact-zero reproduction may surface *intended* deltas
  (baseline mislabels), which the delta report must enumerate — that is by
  design, not a flaw.
- **The E13 answers (step 3) do not resolve the licensing question** — they
  sharpen it. §4(b) raises a *database-level* ShareAlike exposure broader than
  per-fact; per-entry reduction does not cure the repeated-extraction problem;
  and the infringement/licence-compliance distinction shows there is no
  licence-free third path once extraction is substantial (which E13 finds
  likely). This is why WS0-T3 implementation is **held pending the E13
  direction**: E13 option (b) (conservative redesign — e.g. pointer-only with
  facts re-derived from AIAAIC's own cited primary sources, or row/field
  ceilings) would materially reshape the spec's ingest design, so building the
  controlled-vocab-tag plumbing now risks discarding it.
