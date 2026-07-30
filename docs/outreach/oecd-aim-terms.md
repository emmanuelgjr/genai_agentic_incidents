# Draft — OECD AI Incidents and Hazards Monitor (AIM): reuse terms + bulk-channel question

**STATUS:** 📝 **DRAFTED (2026-07-30) — not yet sent, not yet reviewed by
red-reviewer.** Per the committed-artifact working agreement (`CLAUDE.md`),
this file is written to disk and committed before being shown to the user or
to a review gate. This is a genuinely new draft: no OECD outreach file
existed anywhere in this repo's git history before this one —
`git log --all --diff-filter=A -- 'docs/outreach/*'` returns the complete
set of outreach files ever committed here (`aiaaic-correction.md`,
`aiaaic-facts-link.md`, `aiid-goodwill.md`, `airi-draft4-export-request.md`,
`annotator-recruitment.md`, `mit-airi-courtesy.md`, `README.md`) and none of
them is OECD-related. `docs/SOURCE_LICENSES.md` §1.5 previously recorded an
"Outreach date: 2026-07-15 (drafted; not yet sent)" that described an
artifact which never existed on any branch — corrected alongside this draft
(user ruling E20, 2026-07-29/30). Do not edit the message body below once
sent — the sent version is what OECD has, and editing it here would make
this file misdescribe what they were told.

**Send status:** Not sent. The user verifies the recipient and sends; log
the actual send date on `docs/outreach/README.md` and in
`docs/SOURCE_LICENSES.md` §1.5 afterward.

**To (UNCONFIRMED):** `ai@oecd.org`. Not found by this draft's own first-pass
check — `/en/about` and `/en/incidents-methodology` genuinely have zero
`mailto:`/`@` addresses in raw HTML, confirmed by red-reviewer's raw-HTML
check, so that absence finding was real, not a tool artifact. The address
surfaced one hop away, at `https://oecd.ai/en/contact` — the same WS0-T1
lesson as ever (check the pages the target's own navigation points at), one
hop from the site's own nav. Foreman-verified independently: HTTP 200,
101,661 bytes, `mailto:` links = `['ai@oecd.org']`, the only `@` address on
the page, present verbatim. **Still UNCONFIRMED in the sense that matters
for sending:** the user should confirm this is the right desk for a
licensing/reuse-terms question, not a general AI-policy inbox, before using
it.

**Suggested subject:** AI Incidents and Hazards Monitor (AIM) — reuse terms
for indexed data + is there a bulk channel?

---

Hello OECD.AI / AI Incidents and Hazards Monitor team,

I maintain **genai_incidents**, an open, machine-readable index of publicly
reported GenAI and agentic-AI security incidents, mapped to frameworks
(OWASP LLM/ASI, NIST AI RMF, MITRE ATLAS). Our own aggregation is published
under CC BY 4.0; each upstream source's own terms are recorded and carried
through rather than overridden.

We currently index security-relevant incidents from the AI Incidents and
Hazards Monitor (AIM), reading each incident's own published page. Your
methodology page notes that AIM narrative content is drawn from third-party
news outlets and isn't OECD's own IP to relicense — that's helpful context,
but it leaves us without a clear, directly-read answer for what governs
reuse of AIM's *own* structured data (incident IDs, dates, category tags,
cross-references) specifically.

Two things we'd value your help with:

1. **Preferred reuse terms.** We weren't able to load the general OECD terms
   and conditions page (`oecd.org/en/about/terms-conditions.html`) via our
   own automated retrieval — it returned an HTTP 403. That's very likely a
   limit on our end rather than anything about the page itself, but it means
   we can't point to a page we've directly read for what applies to AIM
   specifically. Could you confirm or point us to the terms that govern
   reuse of AIM's own data, and any preferred attribution or citation format?

2. **A sanctioned bulk channel.** We currently read individual incident
   pages one at a time via AIM's own published sitemap. If there's a bulk
   export, an API, or another channel you'd prefer indexes like ours use
   instead, we'd rather use that than continue fetching page-by-page.

No urgency — happy to work with whatever's easiest on your end, and glad to
share more about what we index if useful.

Thank you for your time,
[Maintainer name]
genai_incidents

---

## Facts verified for this draft (internal — not part of the message)

- **The 403.** `https://www.oecd.org/en/about/terms-conditions.html` →
  HTTP 403 via WebFetch, re-checked live 2026-07-30 — same outcome as the
  2026-07-15 finding already on record in `docs/SOURCE_LICENSES.md` §1.5.
  The 403 is genuinely still current, not a stale claim being repeated.
- **AIM methodology page — quote now confirmed verbatim by raw HTML
  (red-reviewer, `curl`, 2026-07-30).** `https://oecd.ai/en/incidents-methodology`
  → HTTP 200. My own 2026-07-30 WebFetch-based re-check surfaced the
  disclaimer's substance ("The AIM is populated with news articles from
  various third-party outlets... with which the OECD has no affiliation,"
  etc.) but not the exact 2026-07-15 quoted string ("Any of the copyrights,
  trademarks... included in the AIM are the property of their respective
  owners") — flagged then as likely my own tool's paraphrasing rather than a
  page change. **Confirmed: the page did not change.** Red-reviewer's raw
  `curl` fetch found the full string present verbatim, twice, in raw HTML:
  *"Any of the copyrights, trademarks, service marks, collective marks,
  design rights, or other intellectual property or proprietary rights that
  are mentioned, cited, or otherwise included in the AIM are the property of
  their respective owners."* The mechanism I flagged (WebFetch summarizes
  rather than returning raw HTML) is confirmed as the actual cause, not a
  live page edit — a correct hedge, resolved in the page's favor.
- **robots.txt — unchanged.** `oecd.ai/robots.txt` re-fetched 2026-07-30:
  same five French-language `Disallow` rules as the 2026-07-15 record, no
  rule affecting `/en/incidents/`.
- **Sitemap redirects to a different host; individual incident pages do
  not (narrowed, red-reviewer/foreman, 2026-07-30).**
  `https://oecd.ai/sitemaps/incident-monitor-sitemap.xml` (the exact URL
  `scripts/ingest_oecd_aim.py::SITEMAP_URL` fetches) 302-redirects to
  `https://incidents-server.oecdai.org/api/v1/sitemap.xml`, confirmed live
  2026-07-30. I flagged this as a possible conduct gap (`ingest/common.py`'s
  `robots_allowed()`/`_rate_limit()` key off the pre-redirect host,
  `oecd.ai`) but could not confirm with WebFetch whether individual
  `/en/incidents/<id>` pages redirect the same way. **They don't:** 7 probes
  (3 from the ingest artifact, 4 fresh from the live sitemap) all returned
  200 with 0 redirects. So this gap is a **1-fetch-per-weekly-run exposure,
  not a per-incident one** — real, but far smaller than the unresolved
  version I reported. The redirected sitemap still emits ~10,000
  `oecd.ai`-hosted incident URLs matching the ingest's own filter, so
  there's no silent-zero-URL failure either. Not fixed in code here;
  reported to pipeline-engineer.
- **Ingest gap confirmed real; the licensing rationale for it is now an
  open question — corrected 2026-07-30 (E21, red-reviewer/foreman
  verification), not resolved here.** Direct read of
  `scripts/ingest_oecd_aim.py::normalize_body()`: `description = (summary or
  title).strip()` — the reduction to structural-facts-only that
  `docs/SOURCE_LICENSES.md` §1.5's Action cell calls for is still **not
  implemented in code**; that part of my original finding stands. **What I
  got wrong:** I characterized the source as "`body.get("summary")` or
  article `evidences` text" as if both were live paths. The `evidences`
  fallback fired for **zero of 4,160 rows checked** — the shipping text is
  effectively 100% the `summary` path, `evidences` present in code but
  inert. **More significantly:** on a deep-parsed page, `summary` doesn't
  appear anywhere inside the concatenated `evidences` blob — it reads as a
  composed OECD abstract, not quoted third-party news prose. If that holds
  generally, the third-party-disclaimer rationale this row's
  Redistribute-verbatim/Relicense-compatible cells rest on may not actually
  apply to what ships, and OECD's own "written content from 1 July 2024
  onward is CC BY 4.0" grant (§1.5 License) could instead govern it. **This
  is escalated to the user and explicitly not decided by me** — see
  `docs/SOURCE_LICENSES.md` §1.5 Action and the summary table row. The
  message above still doesn't claim we exclude narrative text, and that
  omission is correct regardless of how the licensing question resolves —
  the code-level gap is real either way.
- **Contact found — `ai@oecd.org`, one hop away.** The two pages I checked
  (`/en/about`, `/en/incidents-methodology`) genuinely have zero
  `mailto:`/`@` addresses — red-reviewer's raw-HTML check confirmed this
  particular absence finding was real, not a tool artifact, worth recording
  since not every absence finding in this project turns out to be
  method-suspect. The address surfaced one hop away at
  `https://oecd.ai/en/contact` (foreman-verified: HTTP 200, 101,661 bytes,
  sole `mailto:`/`@` address on the page = `ai@oecd.org`). Recorded in the
  To (UNCONFIRMED) field above; the user still confirms it's the right desk
  before sending.

**What I did not verify, and left out or hedged accordingly:**
- **OECD's actual general terms text** — not quoted in the message (the
  message asks OECD to confirm, rather than asserting our own reading of a
  page we couldn't load).
- **Whether AIM's own structured facts (not narrative) are within OECD's
  general reuse grant** — this is the open question the email exists to
  ask, not asserted either way.
- **A specific recipient address** — now recorded (`ai@oecd.org`, found one
  hop away at `/en/contact`); the user still confirms it's the right desk,
  not a general inbox, before sending.
