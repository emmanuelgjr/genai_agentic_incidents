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

**To (UNCONFIRMED):** OECD.AI / AI Incidents and Hazards Monitor (AIM) team
— **no named contact or mailto link was found** by this draft's own check
(`https://oecd.ai/en/about` and `https://oecd.ai/en/incidents-methodology`,
both fetched 2026-07-30; neither page's text surfaced a contact address).
This is an absence finding, and per this file's own method-suspect standard
for absence findings, it should not be read as "OECD has no contact
address" — only as "this draft's retrieval method didn't surface one."
Recommend the user check `oecd.ai`'s own contact/press page directly before
sending, or route through a general OECD data-team inquiry channel if one is
known; red-reviewer can raw-HTML-grep the two pages above for `mailto:`/`@`
as a second check. Absent a better address, the general
`termsandconditions`/OECD.AI contact surface is the fallback.

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
- **AIM methodology page — substance corroborated, exact quote not
  re-verified verbatim.** `https://oecd.ai/en/incidents-methodology` →
  HTTP 200, re-checked live 2026-07-30. The third-party-content disclaimer
  is still present in substance — this fetch surfaced "The AIM is populated
  with news articles from various third-party outlets... with which the
  OECD has no affiliation," "Their use or inclusion in the AIM does not
  imply that you may use them for any other purpose," and a pointer to
  `www.oecd.org/termsandconditions` — but the exact string
  `docs/SOURCE_LICENSES.md` §1.5 quotes from 2026-07-15 ("Any of the
  copyrights, trademarks... included in the AIM are the property of their
  respective owners") did not appear verbatim in this fetch's output.
  **This is very likely my own tool's limitation, not a page change**:
  WebFetch runs a summarizing/paraphrasing model over the fetched content
  rather than returning raw HTML, so it is not a reliable verbatim-quote
  instrument even when it correctly reports substance (the standing
  absence-finding caveat in `docs/SOURCE_LICENSES.md`'s header applies
  here too, even though this is a presence finding, not an absence one).
  I did not put the disputed exact string in the message above — the
  message doesn't quote AIM's own text at all — so nothing in the draft
  depends on resolving this. **Flagged for red-reviewer:** a raw
  `curl`+`grep` of `oecd.ai/en/incidents-methodology` for the exact 2026-07-15
  string would settle whether the page changed or my tool paraphrased.
- **robots.txt — unchanged.** `oecd.ai/robots.txt` re-fetched 2026-07-30:
  same five French-language `Disallow` rules as the 2026-07-15 record, no
  rule affecting `/en/incidents/`.
- **Sitemap now redirects to a different host — new finding, not
  previously recorded.** `https://oecd.ai/sitemaps/incident-monitor-sitemap.xml`
  (the exact URL `scripts/ingest_oecd_aim.py::SITEMAP_URL` fetches) returned
  a 302 to `https://incidents-server.oecdai.org/api/v1/sitemap.xml` when
  checked live 2026-07-30. This doesn't change anything about OECD's
  license/terms and isn't referenced in the message above, but it is a
  conduct-relevant fact: `ingest/common.py`'s `robots_allowed()` and
  `_rate_limit()` key off the *original* URL's host (`oecd.ai`), and
  `urllib`'s automatic redirect-following means the actual bytes come from
  `incidents-server.oecdai.org`, whose own robots.txt is never checked by
  this pipeline. I could not confirm with WebFetch alone whether individual
  `/en/incidents/<id>` incident pages (not just the sitemap) redirect the
  same way — reported to the foreman/pipeline-engineer separately, not
  resolved here.
- **Ingest currently retains third-party narrative text — a live gap in
  the Action this draft's own source row calls for, found while verifying
  this draft, not previously recorded as a completion-status fact.** Direct
  read of `scripts/ingest_oecd_aim.py::normalize_body()`: `description =
  (summary or title).strip()`, built from `body.get("summary")` or article
  `evidences` text — i.e. the reduction to structural-facts-only that
  `docs/SOURCE_LICENSES.md` §1.5's Action cell calls for ("Reduce
  `description` to structural facts + link where the text is
  evidence-derived narrative") has **not been implemented in code**. The
  outreach message above does not claim we exclude narrative text, for
  exactly this reason — an earlier draft of this message said "not
  narrative text" and that claim would have been false against the current
  code; it was removed rather than sent. See the report for the exact
  requirement routed to pipeline-engineer.
- **No named contact found.** Two pages checked (`/en/about`,
  `/en/incidents-methodology`), both via WebFetch, both came back with no
  mailto/contact surfaced. Treated as method-suspect per this project's own
  standing rule, not as confirmation OECD has no contact channel.

**What I did not verify, and left out or hedged accordingly:**
- **OECD's actual general terms text** — not quoted in the message (the
  message asks OECD to confirm, rather than asserting our own reading of a
  page we couldn't load).
- **Whether AIM's own structured facts (not narrative) are within OECD's
  general reuse grant** — this is the open question the email exists to
  ask, not asserted either way.
- **A specific recipient address** — genuinely unconfirmed; flagged above
  rather than guessed at.
