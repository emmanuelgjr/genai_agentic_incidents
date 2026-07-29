# Draft — AIAAIC: correction to our retention description (E17)

**STATUS:** ⚠ DRAFT — awaiting user send. Foreman-written 2026-07-29.
**Send status:** NOT SENT as of 2026-07-29. Log the send date here and on the
board when it goes out.

**What this corrects.** `docs/outreach/aiaaic-facts-link.md`, sent to AIAAIC
**2026-07-27**, described what we retain as "categorical facts only (system,
technology, sector, jurisdiction) plus a link back to the AIAAIC record". That
is a closed list, and it is incomplete — it affirmatively excludes the AIAAIC
headline (carried verbatim as our `title`) and `affected` (carried verbatim
from AIAAIC's Developer/Deployer cells). Logged as **E17**: the fourth
non-exhaustive licensing enumeration in this workstream, and the only one that
has left the repository. It went to the party whose reply gates E13/D17, and it
is the basis on which they are being asked a licensing question — an answer
given on an incomplete description is worth less to us than an accurate one.

**⚠ SEND-ORDER CONDITION — read before sending.** The marker paragraph below
claims the row-level marker covers every AIAAIC-citing row. That becomes true
when the **E16 implementation merges** (marker extended from 1,422 to all 1,517
citing rows). **If you send AFTER that merge, the text below is accurate as
written.** If you send BEFORE it, swap in the alternate paragraph at the bottom.
The 2026-07-18 tense correction to the earlier draft exists because a draft
described in-progress work in the perfect tense; do not reintroduce that.

**To:** AIAAIC (same recipient as the 2026-07-27 message — reply on that thread)
**Suggested subject:** Re: AIAAIC data reuse at scale — correction to what we retain

---

Hello again,

Following up on my message of 27 July with a correction. We audited our own data
against your sheet cell by cell, and the description I gave you of what we
retain was incomplete — it listed only the categorical facts, and we in fact
carry more of your content than that. Nothing about our practice has changed;
only the accuracy of how I described it. Since you are being asked a licensing
question, you should have the complete picture.

What we actually retain from an AIAAIC record (not every item applies to every
record — we ingest via two paths of different vintage):

- the **AIAAIC record ID**, and a link back to the record;
- the **headline, verbatim**, as our entry title;
- the **affected developer or deployer** organisation name, verbatim from your
  Developer and Deployer cells;
- the categorical facts I did list — **system, technology, sector,
  jurisdiction** — with sector and jurisdiction also carried as tags;
- the **date** of the incident;
- and in our older hand-curated entries, the **headline again inside the
  citation itself**, as the title of the reference pointing back to you.

We do not carry your editorial write-ups — purpose, ethical issues,
consequences, response — as I said.

The count in my earlier message was also slightly off: our dataset cites
**1,517** AIAAIC records, not ~1,513.

Every one of those rows carries a machine-readable, row-level marker recording
that its content derives from AIAAIC under CC BY-SA 4.0, so the attribution
travels with the data itself rather than sitting only in a notice file.

My questions from the 27 July message stand unchanged, and I would still very
much value your view on them.

Best regards,
[Maintainer name]
genai_incidents

---

## Alternate marker paragraph — use ONLY if sending before the E16 merge

> 1,422 of those rows carry a machine-readable, row-level marker recording that
> their content derives from AIAAIC under CC BY-SA 4.0; we are extending that
> marker to the remaining 95 now, so it will travel with every AIAAIC-derived
> row rather than sitting only in a notice file.

---

## Provenance of the corrected list (internal — not part of the message)

The list is the empirically closed enumeration recorded on the board 2026-07-29:
all 1,422 marked rows joined to the cached source sheet by AIAAIC ID
(1,422/1,422 joined), every published string tested against every source cell
for exact equality. Verbatim-carry set: `source_ids`==id (1,422),
`title`==headline (1,417), `date`==occurred (1,411), `references[].url`==summary
(1,397), `affected`==developer/deployer/sector/system (1,198/528/81/73), plus
`description` embedding the four categorical cells and `tags` carrying
slugified `sector-*`/`juris-*`.

`date` was ruled *not carried content* for disclosure purposes — a bare fact,
regex-derived (`parse_year`, `ingest_aiaaic_sheet.py:338`) — but is listed to
AIAAIC anyway. Under-completeness is the failure being corrected here, so the
note errs long.

**The citation line covers a finding that post-dates the closure.** The
empirical sweep covered the 1,422 sheet-derived rows only; the 95 hand-curated
AIAAIC-citing rows were never swept. The E16 review (license-auditor,
`docs/audits/E16-title-similarity-review-2026-07-29.md`) found, and the foreman
confirmed against `ingest/aiaaic_incidents.json` joined to the cached sheet,
that `references[0].title` on those rows carries AIAAIC's headline verbatim
behind a literal `"AIAAIC - "` prefix — on **49 of the 92 joinable rows**,
including **all 13** whose `title` is being replaced under D18(b). The
sheet-derived 1,422 are unaffected: `ingest_aiaaic_sheet.py:482` sets the
reference title to the fixed literal `"AIAAIC entry"`.

User ruling 2026-07-29: **leave the reference titles as they are and disclose
them.** Naming a cited work by its own title is attribution, not appropriation,
and stripping it would degrade the citation. The consequence this note must
carry, and does: the D18(b) retitle removes AIAAIC's verbatim headline from the
field we assert as our own, and **does not** remove it from the row.
