# v2.9.0 bundle — gate verdict record

**Do not regenerate.** Dated record of the third-gate PASS, kept per working
agreement 5: the artifacts are re-derivable from the repo forever, the
testimony is not.

## v2.9.0 bundle — FINAL PASS verdict (red-reviewer, third gate, 2026-07-31)

Recorded per working agreement 5. Gate's summary: *"Three gates, two defects,
both real and both fixed. The central figure — 3,667 / 162 — is confirmed by
four routes landing on one identical ID set, and by `merge_into()`'s source
showing why it must be a single partition."*

**Defect cleared**, verified on whitespace-normalized text with blockquote
markers stripped: `overcounting the residue by one` present · `undercounting`
**zero occurrences anywhere** · `as of 8afa39c0` present · `both now carry`
absent. Direction **re-derived at that tree**, not carried over: broken residue
163 vs true 162 → +1 → OVERCOUNT.

**The subject-attachment check the foreman asked for — right word, right
subject.** The foreman asked it to confirm the corrected clause attaches to the
*broken method* rather than to the correction, since that passage had had its
direction wrong once already. Ruled correct on three independent grounds: the
participial adjunct sits **inside** the `that`-clause whose subject is "both"
and whose predicate is "had been reading … against only the first", and a
participle attaches to the subject of the clause it occupies; it cannot attach
to "corrected", which sits outside that clause, is separated by a finite clause
boundary and ~24 words ("which English participial adjuncts do not reach
across"), and is semantically excluded because the reader has just been told in
the same sentence that both files now carry 3,667/162. It also recorded two
compressions it read for and deliberately did **not** flag — "both had been
reading" is a mild metonymy (files don't read; the method behind their figures
did), and "one row's title" compresses "every row's title, but it changed the
answer for one row" — *"so the record shows they were checked rather than
skipped."*

**Everything re-run at `151fb331`, not assumed:** corpus 13,060 · landmark
1,905 · v2.8.0 12,986 · +135 / −61 / net +74 · 59 tombstones all `into: null` ·
`content_license` 1,517 · AIID union 1,466 with **0** · `source_freshness`
1,380 · OECD 3,829 · at `references[0]` 3,667 · `aiid_id` among them **1** ·
citation-bearing 4,197 (+368) · **59-list == tombstoned set True** · **27-list
all live True**. `pytest` **314 passed** · `check_stats_drift` **exit 0** · HEAD
attached throughout, **no checkout** · **no strays** · release **still not cut**
(three version strings 2.8.0, tags top at v2.8.0) · cross-file claim still true
(`NOTICE-DATA:183`, `.reuse/dep5:70` both 3,667/162) · sweep for `the other 163`
and `undercounting` → **zero hits**, the only surviving `3,666` being `:132`'s
correct render claim · the five deliverables **byte-identical** to the tree
cleared at bounce #2.

**⚠ PROCESS POINT AGAINST THE FOREMAN, AND IT IS FAIR.** The foreman told the
gate *"board commits since `86cf84eb` are PROGRESS.md-only."* **`151fb331`
landed mid-gate and was not** — it added 28 lines to
`docs/audits/PHASE1-EXIT-measurements-2026-07-31.md`, **one of the seven files
in this bundle's own diff against `main`.** It reached the gate as a
file-changed notification rather than a brief. No harm: it verified rather than
assumed, re-deriving both new claims independently — criterion 2, exactly one
hit, a generated incident page quoting an upstream advisory's API description,
**zero project-voice**; criterion 6, **135 rows, 0 empty cells**, reached via a
**`>= 3` pipe threshold, a different route that does not reproduce the six-pipe
bug.** Ruled **not** a scope defect (the file was already in the bundle at gate
1, and the brief described exit-criteria measurements as part of the packet).
**The lesson is the foreman's: "board-only" was asserted without checking
whether the touched file was in the bundle, and the next gate may not get the
notification.**

**⭐ It extended the check-that-cannot-fail lesson to a third instance:** *"this
is the third instance today across three unrelated tools — `rev-parse`, the
six-pipe parser, and the line-based grep you warned me about above, which would
have made ME report this fix as unlanded. The lesson is about how checks are
written, not about any one tool."*

**Four advisories, none blocking.**
1. `PHASE1-EXIT-measurements-2026-07-31.md:67`'s "are routed for correction" is
   now overtaken — **and the gate ruled this correct behaviour, not a defect**,
   putting the distinction on the record so the board does not read it as
   inconsistent with bounce #1: **that file is a dated audit with a
   do-not-regenerate marker, so agreement 4 says preserve; the release notes are
   a live consumer-facing document that will be published, which is why the same
   shape was a defect there and is not here.**
2. `docs/releases/` sits outside `DOC_SURFACES`, so the notes' ~15 hardcoded
   totals are guarded by nothing but this gate — **add the do-not-regenerate
   marker when the release is cut.**
3. The notes remain a third home for 3,667/162 — in scope for the `d9318dc8`
   collapse proposal.
4. `INC-00554` carries **100** OECD source_ids.
