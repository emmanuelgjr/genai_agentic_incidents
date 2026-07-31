# Phase 1 — release packet

**Do not regenerate.** Dated record, assembled by the foreman 2026-07-31.
Written for the maintainer to read before cutting v2.9.0 and declaring Phase 1.

> **Status of the final gate: ✅ PASS.** The exit checklist
> (`docs/audits/PHASE1-EXIT-2026-07-31.md`) passed at `344a7abe` after three
> bounces — *"Merge, and send the packet with clause 2 open."* **Every
> component of this packet is now merged to `main` and gated.**

## 1. What you are being asked to decide

**One thing is genuinely open, and it is not the project's to close.**

**Criterion 9, clause 2 — the OECD outreach email.** Drafted at
`docs/outreach/oecd-aim-terms.md`, gated PASS, **not sent**. Recipient
`ai@oecd.org`, **unconfirmed as to desk**. Three of four sent and logged
(AIAAIC, AIID, MIT AIRI — all 2026-07-27, confirmed from the sent folder and
logged 2026-07-29).

Per this project's own escalation rule, agents draft outreach and the
maintainer sends it. Two honest ways forward:

- **Send it** → criterion 9 closes 4-of-4, FLAG 3 disappears, and Phase 1
  exits with **no open criteria**.
- **Declare with it open** → the checklist reports it as open, in plain
  language, and it closes whenever you send.

**Both are legitimate. What is not legitimate is marking it met.** This project
has twice recorded criteria satisfied by dates attached to drafts that did not
exist (E18, E20). Rounding 3-of-4 up to 4 **on the exit checklist itself**
would be the third and the worst, and it is the one thing every gate on this
sequence was told to check.

**Then:** cut v2.9.0 (bump `pyproject.toml`, `CITATION.cff`, `data/stats.json`;
tag). **Nothing in this packet has cut the release** — all three version
strings still read `2.8.0` and the latest tag is `v2.8.0`, verified.

## 2. What shipped — six gated merges on `main`

| Merge | What | Gate |
|---|---|---|
| `7365aee7` | E21 §5 OECD AIM narrative reduction | PASS, 0 defects |
| `6f06eaeb` | E21 §5.3 per-entry OECD attribution | PASS, 0 defects |
| `ac7299bb` + `e07852fc` | Licensing surfaces: OECD paragraph, dep5 grammar, §1.5 | 2 bounces → user escalation → D24 → PASS |
| `c4d856c9` | README rewrite | 2 bounces → user ruling → PASS |
| `a54e5ce7` | v2.9.0 pre-release packet (notes, CHANGELOG, notices, pointer) | 2 bounces → PASS |

Eleven gate verdicts, three user escalations, and **four figures corrected** —
one of which was wrong on a public licensing surface.

## 3. The corpus, as measured

Re-derived 2026-07-31 against `main`. Full method in
`docs/audits/PHASE1-EXIT-measurements-2026-07-31.md`; per-criterion evidence in
`docs/audits/PHASE1-EXIT-2026-07-31.md`.

| | |
|---|---:|
| Entries | **13,060** |
| Since `v2.8.0` (12,986) | **+74** — 135 added, 61 removed |
| Removed **without** a tombstone | **0** |
| Tombstones | **1,051** |
| `content_license` markers | **1,517**, all AIAAIC |
| OECD-sourced rows | **3,829** |
| …carrying per-entry OECD attribution | **3,829 / 3,829** |
| …carrying the reduced `description` | **3,667** |
| `source_status` | **13,060 / 13,060** |
| Tests | **314 passed** |
| Invariant-6 drift gate | **exit 0** |

**The corpus is 59 entries smaller than the internal checkpoint, and those were
remediated by retirement, not reduction.** No surface describes this release as
a pure text change.

## 4. What is still open, and owned

None of these blocks Phase-1 exit. Each has an owner on the board.

1. **`.zenodo.json` carries no `version` key at all** — not stale, absent.
   Worse in kind than a wrong value: **no sweep can see a missing field.**
   Owner WS6, with the redeposit workflow.
2. **`VERSION = "2.0.0"` exported from `src/genai_incidents/__init__.py`** while
   `pyproject.toml` says `2.8.0`, and it is in `__all__`. Owner WS6-T1 — the
   right fix is deciding what a consumer may ask for, not adding a fourth
   string to drift.
3. **WS6-T4's undecided fork.** Its acceptance criterion says "no surface says
   'TAXII endpoint'" (in-place correction); the one surviving instance sits
   under a **past-release heading**, where working agreement 4 says supersede,
   never rewrite. **The two point opposite ways on the only line WS6-T4
   exists to fix.** Decide before dispatching it.
4. **Collapse the OECD `title`/`description` figures into one stated
   partition** on `NOTICE-DATA` and `.reuse/dep5`. They are one partition
   published as two numbers, which is what let one drift. Proposed text ready.
5. **Generate `NOTICE-DATA` from a manifest.** The per-source licensing
   asymmetry has now been fixed **four times by hand**. A manifest, a
   generator, and a CI check that fails on divergence converts "did the author
   remember" into "did CI catch drift."
6. **OECD provenance labelling** — a one-row curation override where the
   general fix belongs in ingest.

Plus, from the last gate: **add a do-not-regenerate marker when the release is
cut** — `docs/releases/` sits outside `DOC_SURFACES`, so the notes' hardcoded
totals are guarded by nothing but the gate that reviewed them.

## 5. The five technicality flags

| Flag | State |
|---|---|
| **1** — WS3-T5 row contradicted D13 | **Fixed**, via a dated correction that preserves what the cell previously said |
| **2** — criterion 6 satisfied on false statements until 2026-07-30 | **Disclosed, not resolved.** A statement about history, not a defect |
| **3** — criterion 9 clause 2 is 3-of-4 | **OPEN — yours** |
| **4** — `CHANGELOG`'s "Static TAXII 2.1 endpoint" | **Open**, with the fork above. Every *live* surface is correct |
| **5** — criterion 10 met by a date that did not exist for 12 days | **Disclosed as history.** The date now exists and is machine-readable |

## 6. What this phase taught, which is worth more than any figure here

**The dominant failure mode was not bad judgement. It was checks that cannot
fail** — seven instances, four agents, six unrelated tools, every one caught
before it reached a conclusion but several only by a second look. A verification
whose output is *identical* in the passing case and in the case where it never
ran: `git rev-parse HEAD` reading the same attached or detached; a parser that
scanned zero rows and would have reported clean from an empty set; line-based
greps on wrapped prose returning false negatives four times; a failed merge
announced as success by a chained `echo`; `git push` to an unmoved ref exiting
zero.

**And its second-order form, which cost the most.** Twice a figure was
"confirmed" by a second party re-running the first party's method and getting
the first party's answer — and twice that agreement was read as verification.
**It is not: an identical method reproduces identical bugs.** A wrong count
reached two public licensing surfaces that way. What caught it was a drafter
that cross-validated three independent ways and **refused to write the board's
number**, and a gate that deliberately chose a route nobody had used.

**And its third form, discovered last:** removing a figure does not remove the
claim — it removes the ability to check it. "A substantial majority" is a
quantitative claim wearing qualitative clothes, exactly as checkable as a
number, and it was wrong. **The qualitative rewrite is the *unfalsifiable*
form, not the safer one.**

The rule that replaced it: **a figure invariant under the artifact's own
creation may be stated with its date; a figure that moves because the artifact
exists must be a command.**

## 7. Where to look

- `docs/audits/PHASE1-EXIT-2026-07-31.md` — the checklist; one row per
  criterion, every one `[R]`-backed
- `docs/audits/PHASE1-EXIT-measurements-2026-07-31.md` — the measurements and
  their methods, including two that were wrong and how
- `docs/releases/v2.9.0.md` — the draft release notes, with every affected ID
- `docs/audits/v290-bundle-gate-verdict-2026-07-31.md` — the bundle gate's
  testimony
- `PROGRESS.md` — gate verdicts recorded verbatim, foreman corrections, and the
  six routed follow-ups
