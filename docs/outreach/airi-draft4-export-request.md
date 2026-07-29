# Draft — MIT AI Risk Initiative: sanctioned export/API request ("AIRI Draft 4", redraft)

**STATUS:** DRAFT — pending red-reviewer verdict against current board state, then user send. This is a **redraft**. The original "Draft 4" was recorded on the board (`PROGRESS.md`, D8/E10) as "ready to send" and never existed in any commit on any branch — `git log --all --diff-filter=A` shows it was never added, `--diff-filter=D` shows nothing deleted. It was a chat-only deliverable, the **fifth** lost that way, logged as **E18** (2026-07-29). This replacement is written directly to disk per the committed-artifact working agreement, before being shown to the user.

**Send status:** NOT SENT as of 2026-07-29. Log the send date here and on the board (E10/D8 rows) the moment it goes out — **D8's 30-day AIRI-hold clock starts on the send of *this* message, not on `mit-airi-courtesy.md`** (already sent 2026-07-27, see relationship note below). Until this is sent, the hold has no end date by construction — that open-endedness is the entire reason this task exists.

**To:** `airisk@mit.edu` — found as a live contact address via a `mailto:` link in the "Collaborate with us" / "Get in touch" section of a raw fetch of `airisk.mit.edu` itself, 2026-07-29. This is a *presence* finding (the link is either in the fetched content or it isn't), not an absence finding, so it is not exposed to the markdown-truncation failure mode that produced the AIAAIC false negative. Per standing outreach protocol, the user still does a final check before sending — recipient addresses are always user-verified regardless of how the draft found them.

**Suggested subject:** AIRI Navigator dataset — sanctioned export/API request + a licensing provenance question

**Relationship to `docs/outreach/mit-airi-courtesy.md`:** that message (sent 2026-07-27, to Spencer Michaels via the AIRI Navigator site — a different address than this one) was a courtesy heads-up about the dead ZIP download plus an informal version of the provenance question below. **D8's 30-day clock is keyed specifically to this message, not the courtesy note** — the board's own 2026-07-29 docs-warden sweep (finding N7) confirms the two are distinct and explicitly rejects reading the courtesy send as having already started the clock. This draft (a) makes the sanctioned-export/API ask the courtesy note only touched on informally, and (b) restates the transitive-AIID question more precisely, since AIRI Navigator's own licence is now confirmed CC BY 4.0 (`docs/SOURCE_LICENSES.md` §1.4) in a way the courtesy note could not yet state with full confidence when it was written. No reply to the courtesy note is on record on the board as of this draft.

---

Hello,

I maintain **genai_incidents**, an open, freely-relicensed index of AI incidents, and we ingested the AIRI Navigator public bulk-data export while it was available, under AIRI's own **CC BY 4.0** terms — the licence stated at airisk.mit.edu, which AIRI Navigator's own Terms of Use names as the source of the data it presents.

That bulk download is no longer reachable: the ZIP now returns a 404 on both hosts we've checked, and the on-page download link appears to have been withdrawn rather than simply moved or broken. When we noticed, we stopped relying on the ingest rather than working around the missing file — we are not scraping the site to reconstruct the dataset by other means.

Two things we'd value your help with:

1. **Is there a sanctioned export or API for this data now, or planned?** We're glad to work within whatever terms you'd prefer — rate limits, an access-request process, a specific attribution format, anything else.

2. **A licensing provenance question**, a more precise version of something we also asked via the AIRI Navigator site on 27 July: part of the AIRI dataset appears to derive from the AI Incident Database, which publishes under CC BY-SA 4.0 — a share-alike licence, distinct from AIRI Navigator's own CC BY 4.0. Do AIID-derived records within the AIRI dataset carry AIID's share-alike obligation through to downstream users like us, or does AIRI's own CC BY 4.0 grant cover them as redistributed? We're asking about your own understanding of the data's provenance, not raising a concern about your licensing choices — it's the kind of thing that's cheap for you to answer and hard for us to work out independently.

For context on why this matters on our end: roughly 1,100 of the incidents we index currently carry EU AI Act regulatory-mapping tags that trace back to AIRI Navigator data. Those mappings are on hold at their last successful update (31 May) rather than being removed, while we wait to hear from you. A sanctioned channel would let us keep them current instead of leaving them as a snapshot.

No urgency beyond wanting to get this right — happy to work with whatever's easiest on your end.

Thank you for your time,
[Maintainer name]
genai_incidents

---

## Facts verified for this draft (internal — not part of the message)

- **AIRI Navigator's own licence — CC BY 4.0.** Not re-fetched this session; treated as settled per `docs/SOURCE_LICENSES.md` §1.4, which records independent cross-checks by red-reviewer and the foreman on 2026-07-16 (raw-HTML fetch of AIRI Navigator's ToS modal naming airisk.mit.edu as its source, corroborated by airisk.mit.edu's own footer and JSON-LD `publishingPrinciples`).
- **ZIP download dead.** Re-verified fresh this session, 2026-07-29: `https://www.airi-navigator.com/downloads/airi-data.zip` → HTTP 404 (WebFetch). Matches the board's 2026-07-16/18 finding (E6, `docs/SOURCE_LICENSES.md` §1.4); still true today, 13 days later.
- **robots.txt permissive, with `/api/` disallowed.** Re-verified fresh this session, 2026-07-29 — full raw contents: `Allow: /` at root; `Disallow:` `/embed/`, `/admin`, `/login`, `/design-system`, `/api/`. Identical to the board's prior finding.
- **Withdrawal characterization — hedged, not asserted.** The message says "appears to have been withdrawn," matching `docs/SOURCE_LICENSES.md` §1.4's own hedge ("the withdrawal looks deliberate... rather than an accidental move of the file") and `mit-airi-courtesy.md`'s sent wording ("appears to be gone... appears gated"). E6 on the board states this more flatly ("deliberately withdrawn") but per this task's brief I did not upgrade the hedged board language into an assertion of MIT's intent in an outward-facing message.
- **Ingest dead-since / last-successful-refresh dates.** Per D8 and the WS4-T9 report on the board: dead since 2026-06-07, last successful refresh 2026-05-31. Not independently re-derived this session (no shell access); taken from the board record, which itself is reviewer-confirmed.
- **At-risk figure (~1,100).** This is the red-reviewer-confirmed figure from the WS4-T9 gate (PROGRESS.md, E10 row), independently re-derived from raw data by the reviewer using its own population definitions and landing on the same number — not the specialist's original ~124 underestimate that gate corrected. I cited this figure, not the frozen-corpus row count (which the board records as two close but distinct numbers — 1,457 committed May rows vs. 1,456 with live incident URLs — so I left that number out of the outward-facing message entirely to avoid citing an ambiguity I didn't resolve).
- **Recipient address.** Confirmed via a `mailto:` link found in a raw WebFetch of `airisk.mit.edu`, 2026-07-29 (presence-finding, see header note on why this is lower-risk than an absence claim).
- **Transitive-AIID framing.** Drawn from `docs/SOURCE_LICENSES.md` §1.4's "Relicense-compatible" cell and `docs/audits/WS0-E13-database-right-2026-07-18.md`, which state the open question as: does AIRI's CC BY 4.0 grant extend to AIID-derived fields, or does AIID's CC-BY-SA share-alike apply transitively to them. Phrased in the message as a provenance question about MIT's own understanding of their data, per this task's brief — not a challenge to AIRI's licence and not a request for legal advice.

**What I did not verify, and left out or hedged accordingly:**
- **MIT's intent** behind the withdrawal — not asserted anywhere in the message, per the brief.
- **Whether Spencer Michaels replied** to the 27 July courtesy note — no reply is recorded anywhere on the board as of this draft; I did not assert non-reply as a settled fact, only that none is on record.
- **The exact frozen-corpus row count** — two slightly different numbers exist on the board (1,457 vs. 1,456); I omitted a specific row count from the outward-facing message rather than pick one without resolving the discrepancy myself.
