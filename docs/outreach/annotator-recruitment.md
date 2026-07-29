# Draft — second annotator recruitment (WS2-T2 label-quality study)

**STATUS:** 📤 **SENT to Mayur021 2026-07-27** (board: WS5-T2a row; header
corrected 2026-07-29 — it had still read "DRAFT — ready for user review" two
days after the send). Reply awaited; follow-up option ~2026-08-03. Do not edit
the message body below — the sent version is what the recipient has.
**Satisfies the Phase-1 exit criterion "WS5-T2a outreach sent"**
(`MASTER_IMPROVEMENT_PLAN.md:28`). Note WS2-T2's blocked-by lifts only on a
COMMITTED annotator, not on the send.
**To:** Mayur021 (GitHub handle) — top candidate, contacted via a
GitHub comment/mention (no email address is used here — see PII note below).
Ranked backups in the Candidates section if Mayur021 is unreachable or
declines.
**Suggested subject:** Would you help validate ~200 incident labels for
genai_incidents?

**PII note:** no email addresses were looked up or used in identifying
candidates — only public GitHub activity (fork/PR/issue events). Contact is
via GitHub (a comment on their PR/issue, a mention, or GitHub's own message
feature) unless the user already has a direct channel to this person.

---

Hi [First name / handle],

I maintain **genai_incidents**, an open, consolidated, machine-readable index
of publicly reported GenAI and agentic-AI security incidents, mapped to
frameworks like OWASP LLM Top 10, OWASP Agentic Security Initiative, and MITRE
ATLAS. [If sending to Mayur021: I noticed you forked the repo and opened a PR
adding a `reversibility_class` label for the Replit incident (INC-03152)
against the rubric you proposed in #74 — that's exactly the kind of judgment
call I'm asking about below, so I'm reaching out directly.]

**The ask.** I'm running a small human-validation study on our heuristic
labels and need a second, independent annotator — right now every label in
the dataset comes from one person (me) plus rule-based heuristics, and I want
an outside check before publishing accuracy numbers. Concretely:

- Label a stratified random sample of **~200 entries** (already drawn by
  corpus, quality tier, and year, with a fixed random seed — you'd get the
  same sample list I use).
- For each entry, independently assign **four fields**: OWASP LLM Top 10
  category, OWASP Agentic Security Initiative category, attack vector, and
  severity. A written labeling guide (definitions + worked examples for each
  field) is provided — no code required.
- Join **one or two adjudication sessions** (a call or an async written
  exchange, your preference) to walk through entries where your labels and
  mine disagree, so we can record *why* and reach a resolved label together.

**Time estimate.** Budgeting roughly 4–6 minutes per entry to read the
incident summary and assign all four fields puts independent labeling at
about **15–20 hours** for the 200-entry sample. Historically this kind of
comparison finds real disagreement on a meaningful minority of entries — I'd
plan for **an additional 3–5 hours** across one or two adjudication sessions
covering the entries that don't match. So, all-in, **roughly 20–25 hours**,
self-paced over as many weeks as you need — there's no fixed deadline on
your side, only on when I publish the results.

**What you'd need.** Familiarity with security or AI-incidents concepts
(you clearly have this) — no programming required, no access to our
pipeline or infrastructure. I'll send the sample as a plain spreadsheet or
CSV with the labeling guide alongside it.

**What you'd get.** Named credit in the published study — you'd be
acknowledged by name in `docs/LABEL_QUALITY.md` and in the dataset's
datasheet under "§Composition," where the annotation methodology and
inter-annotator agreement (Cohen's κ) are reported. If you're interested in
being listed as a co-author on any accompanying write-up, that's absolutely
discussable — I don't want to promise something I haven't cleared with you
in detail, but I'm open to it and would rather talk it through than assume
either way.

**No pressure at all.** If the timing or scope doesn't work for you, or
you'd rather not, just say so — I'll try the next person on my list, and
there's no downside either way. If you're interested but ~200 entries feels
like too much, I'm also happy to talk about a smaller slice.

Thanks for even reading this far — and for the fork/PR either way, it's
genuinely useful signal that people are looking at the labeling logic
closely.

Best,
[Maintainer name]
genai_incidents

---

## Candidates

Identified from public GitHub activity (forks: `GET
/repos/emmanuelgjr/genai_incidents/forks`; issues+PRs: `GET
/repos/emmanuelgjr/genai_incidents/issues?state=all&per_page=100`), fetched
2026-07-27. Handle and public activity only — no emails, no identity or
employer speculation. Ordered by engagement signal (strongest first).

| Rank | Handle | Signal | Date(s) |
|------|--------|--------|---------|
| 1 | **Mayur021** | Filed issue #74 proposing the `reversibility_class` rubric, then forked the repo and opened PR #85 implementing it — `reversibility_class=external-reversible` for incident INC-03152 (Replit), merged by the maintainer. Authorship of the rubric itself, not just an applied PR, is the strongest engagement signal in the scan — direct, substantive engagement with the project's labeling conventions. Strongest and only candidate with hands-on labeling-adjacent contribution. | Filed #74 2026-06-13; forked 2026-07-02; PR #85 opened 2026-07-02, merged 2026-07-03 |
| 2 | praveenbommalibits | Forked the repo; no further public activity (no issues or PRs) observed. | Forked 2026-06-22 |
| 3 | HyperPentestAI | Forked the repo; no further public activity observed. | Forked 2026-06-08 |
| 4 | joel-correa | Forked the repo; no further public activity observed. | Forked 2026-06-04 |
| 5 | ksmaheshkumar | Forked the repo; no further public activity observed. | Forked 2026-06-04 |
| 6 | upenderadepu | Forked the repo; no further public activity observed. | Forked 2026-06-04 |

**Notes on the fetch:** the issues endpoint returned **98 entries total**
across all pages (issues and PRs share GitHub's numbering; page 2 came back
empty, confirming completeness). Of those, **75** were opened by the
maintainer (`emmanuelgjr`), **21** by bot accounts (13 `github-actions[bot]` +
8 `ecc-tools[bot]` — automated data-refresh/tooling PRs, excluded as
candidates), and **2** by Mayur021 (issue #74 and PR #85, row 1 above). No
other forker has filed an issue or PR as of this fetch, so ranks 2–6 rest on
the fork signal alone, which is weaker — someone can fork a repo out of
passing interest with no further engagement. If Mayur021 declines or doesn't
respond, the fallback order above is a reasonable next-best guess, not a
strong signal.

Because the study needs only **one** collaborator, send to Mayur021 first;
only move to the next row if they decline or don't respond within a
reasonable window (e.g., two weeks).
