# Phase-1 exit checklist — gate verdict record

**Do not regenerate.** Dated record of the final PASS, kept per working
agreement 5: the artifacts are re-derivable from the repo forever, the
testimony is not.

**VERDICT: PASS** at `344a7abe`, after three bounces. Gate's closing:
*"Merge, and send the packet with clause 2 open."*

## The counts, settled from the tool's own section headings

This is what finally ended the 62-vs-69 question, and it did so by reading
`reuse lint`'s own labels rather than by arithmetic inference or anyone's
filter:

```
62 files  <- "The following files have no copyright and licensing information:"
 7 files  <- "The following files have no licensing information:"
tracked: 231 | missing copyright: 62 | missing licence: 69 | 62/231 = 26.8%
```

**62 is the "neither" set, 7 is the licence-only set, 62 + 7 = 69.** Both
earlier measurements were correct and counted different well-defined
categories. Nothing was ever unstable.

**Reflexivity verified, not asserted:** `.reuse/dep5:76` is `Files: docs/*` /
`License: CC-BY-4.0`, and the checklist file appears in the lint output **only
under `MISSING LICENSES`** — never in the 62/69 set. So its statement that
committing it "moves the compliant-over-total ratio while leaving the
non-compliant count untouched" is true as a matter of the tool's behaviour.

## Nothing regressed

`pytest` **314 passed** · `check_stats_drift.py` **exit 0** · entries
**13,060** · tombstones **1,051** · `content_license` **1,517** all `aiaaic` ·
OECD **3,829 / 3,667 / 162** · `[R]` **13**, `[A]` **10**, all ten criteria
`[R]`-backed · **`Clause 2 ⚠ OPEN — 3 of 4 sent, NOT 4 of 4` present, "4 of 4
sent" absent.** Scope: one file, +16/−28, exactly two hunks. No strays. HEAD
attached throughout; no checkout.

## ⭐ The catch the author made, recorded as the author's finding

The verification recipe had said the count was *"NOT reproducible from this
file"* — **true when written under the no-count rule, and falsified by the
paragraph above it the moment the count was restored.** Neither the gate nor
the foreman flagged it; the gate had asked for one paragraph and would have
re-verified one paragraph.

**The author read the whole file for consequences of its own edit and found a
statement that edit had invalidated.** In the gate's words, *"a materially
better standard than the one I set for the re-verification"* — and it is the
exact failure shape that bounced work repeatedly across this phase: **a claim
true when written, invalidated by a later edit in its own file.**

Also correct: deleting the old reflexivity paragraph **wholesale rather than
patching it**, since it ended with a ruling the restored count contradicts.
Keeping it would have left the document arguing with itself.

## The three bounces, accounted for honestly

- **Bounce #1** — three real defects in the artifact: a fabricated quotation,
  two `[A]`-only criteria carrying measurable halves, and a reflexively
  unstable figure. **Genuinely the document's.**
- **Bounce #2** — a false characterization **the gate introduced**, by
  repeating an unmeasured list from the original prose in its own bounce text.
  **The gate's error; the author applied it faithfully.**
- **Bounce #3** — a false magnitude ("a substantial majority" for 27%) that
  **filled the vacuum left by the foreman's no-count rule.** The foreman's
  error, recorded at `ff2d29c1`.

**Through all three, the load-bearing content never wavered** — twenty-plus
figures, ten criteria, five flags, and above all the refusal to round 3-of-4 up
to 4. **Criterion 9 clause 2 is reported open, in plain language, in three
places, with nothing anywhere contradicting it. That is what this checklist was
for, and it holds.**

## Advisory (cosmetic, does not hold the merge)

Deleting the old paragraph removed the bolded lead-in heading the second banked
consistency item, so that section now shows one titled item and one opening on
a bare fenced block. **Content complete and correct; only scan-ability
regressed.** A four-word lead-in restores the parallel. Fix whenever the file
is next touched, or not at all — it changes no claim.

Both bounce-#1 advisories the foreman dropped (`source_freshness.json:26`, the
implicit banned-phrase self-exemption) were correctly dropped. **No open items
remain from any of the three bounces.**
