# Source Licenses & Terms-of-Service Audit

**Task:** WS0-T1 · **Status:** every upstream source class enumerated from
`scripts/ingest_*.py` / `scripts/scrape_*.py` carries a row below; none are
blank. Ambiguous terms are marked **UNKNOWN** and are *not* resolved in the
project's favor — the conservative reading (fewer rights, not more) is
applied until outreach resolves them.

**How to read this table:**
- **scrape-permitted** — is bulk/automated fetching of this upstream allowed
  per its robots.txt and/or its Terms of Service, independent of licensing?
- **redistribute-verbatim** — may we keep and ship the source's own text
  (titles, descriptions, narrative) unmodified in our corpus?
- **relicense-compatible** — can content from this source be included under
  this project's CC-BY-4.0 data relicense without a carve-out?
- **action** — (a) compatible, document as-is · (b) share-alike (BY-SA):
  split license for that corpus / reduce to facts+link · (c) prohibited:
  drop verbatim text, keep `id + url + ≤2-sentence original summary` ·
  (d) unknown: outreach sent/drafted, pending status recorded.
- **UNKNOWN** — *terms not located by the methods stated in the row. This is
  **not** confirmed absence.* An UNKNOWN records the limits of our retrieval,
  not a fact about the upstream. Absence-based findings here are presumed
  method-suspect: on 2026-07-16 this document recorded AIAAIC as having no
  license, and it was wrong — the clause was in the raw HTML of both pages
  checked, split across tags inside a 4.4 MB page, and a markdown-converting
  fetch silently truncated it away. Any row asserting absence must state the
  retrieval method used and is verified against raw HTML (curl + grep, not
  rendered text) before it stands. Structured endpoints (e.g. a GitHub API
  `license` field) are not exposed to that failure mode; rendered HTML pages
  are. Treat an UNKNOWN as "go look again with a better tool," never as
  "there is nothing there."

Per invariant #10 (active the moment this file exists): any new source added
after this file lands must get its row in the same PR.

All terms below were fetched and read on **2026-07-15**. Terms change —
re-check before relying on a stale "date-checked."

---

## 1. Real-world incident sources

### 1.1 AIAAIC Repository
*Ingested by:* `scripts/ingest_aiaaic_sheet.py` (reads the AIAAIC-maintained
Google Sheet CSV export at `docs.google.com/spreadsheets/d/.../export?format=csv`).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY-SA 4.0.** aiaaic.org's site-wide footer, present on both the homepage and `/aiaaic-repository` (the exact page fronting the ingested sheet), states: *"AIAAIC content is available to use, copy, adapt, and redistribute under a"* [CC BY-SA 4.0 licence](https://creativecommons.org/licenses/by-sa/4.0/). Verified by direct primary-source fetch (raw HTML, not a markdown-converting tool): `curl -sL https://www.aiaaic.org/` → HTTP 200 → `grep -oi "cc by-sa"` → 3 hits; `https://www.aiaaic.org/aiaaic-repository` → HTTP 200 → 1 hit; independently corroborated by a second party's identical grep counts. Only `/about-aiaaic` genuinely lacks the notice. **Why my own earlier WebFetch-based attempts missed this:** the clause is split across HTML tags (`...under a </span><a class="XqQF9c" href="https://creativecommons.org/licenses/by-sa/4.0/">CC BY-SA 4.0 licence</a>`) inside a 4.4 MB page; a markdown-converting fetch of a page that size loses trailing content instead of rendering the split anchor as an adjacent link — the page is server-rendered, not JavaScript-dependent, contrary to my earlier hypothesis. That mechanism is now understood and doesn't change the fact itself, which is established. |
| Scrape-permitted | `aiaaic.org` itself returns 404 for `/robots.txt` (no file = no stated restriction). The actual fetch target is `docs.google.com`; its robots.txt (`https://docs.google.com/robots.txt`, fetched 2026-07-15) has `Allow: /spreadsheet` (prefix match, covers `/spreadsheets/d/.../export`) ahead of the blanket `Disallow: /`, so the CSV-export mechanism itself is not blocked by Google's robots.txt. No AIAAIC-specific ToS beyond the general CC BY-SA grant was found for the sheet-fetch cadence itself. |
| Redistribute-verbatim | **YES under the upstream grant** — CC BY-SA permits verbatim copying and adaptation, conditioned on share-alike redistribution and attribution. That said, **decision D2 (2026-07-16, human) means we choose not to exercise this right**: see Action. |
| Relicense-compatible | **NO.** Share-alike (BY-SA) is definitionally incompatible with folding this content into a plain CC-BY relicense of the whole corpus — a true statement about the upstream grant, independent of what we choose to do with it. |
| Action | **(b) copyright share-alike, honored by reduction — not by split-licensing.** Per decision D2 (2026-07-16, human): do not carry AIAAIC verbatim cell text; keep `title` (headline) + short taxonomy-tag facts (sector, jurisdiction, technology) + a source pointer to the specific AIAAIC entry. The dataset stays under one clean CC-BY-4.0 license with **no BY-SA subset** — there is no AIAAIC-specific `license: CC-BY-SA-4.0` field and no corresponding LICENSE-DATA carve-out (this recommendation is withdrawn; superseded by D2). The ATLAS/garak Apache-2.0 carve-outs (§3.1/§3.3) are unaffected — those stand on their own facts and D2 doesn't touch them. This is now the **permanent** handling for the *copyright* question, not an interim measure pending outreach. A narrow, non-blocking clarification email to AIAAIC (attribution format preferred; confirming the recurring Google-Sheet CSV-export cadence is fine) is still worth sending but gates nothing. **This does not resolve licensing risk for AIAAIC in full: the separate EU/UK sui generis database-right question is OPEN**, not answered by D2's copyright reasoning (facts are not copyrightable expression, but the database right protects a database's contents — including bare facts — as such, regardless of copyrightability). See `docs/audits/WS0-E13-database-right-2026-07-18.md` (E13, 2026-07-18), which finds subsistence and substantiality of AIAAIC's database right each more-likely-than-not for the current ~1,513-row extraction, and finds facts+link only a partial mitigation. Pending qualified counsel or a user decision among: (a) engage counsel, (b) redesign the ingest more conservatively, or (c) knowingly accept residual risk. |
| Derivative-work constraint (D2) | **AIAAIC-derived summaries must be written from the primary sources AIAAIC links to — never paraphrased from AIAAIC's own prose.** A close paraphrase of BY-SA text is arguably a derivative work, which would reimport the share-alike obligation that reducing to facts+link exists to shed. "Facts + link" is only a real remedy if the facts are independently sourced; laundering the same prose through a paraphrase is not a reduction. Binds the WS0-T3 implementation (see the plan's WS0-T3 body, which carries the same constraint). |
| Date-checked | 2026-07-15 (fact); 2026-07-16 (independently re-verified by primary-source fetch; D2 recorded same date) |

### 1.2 AI Incident Database (AIID) — direct scrape
*Ingested by:* `scripts/scrape_aiid.py` (concurrently fetches
`incidentdatabase.ai/cite/<id>/` HTML pages, 12 worker threads, and reads
`og:title`/`og:description` meta tags).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY-SA 4.0** for specific named collections only — `incidentdatabase.ai/terms-of-use/` (fetched 2026-07-15) states: *"The following database collections are licensed under the Creative Commons attribution share-alike license"* (incidents, quickadd, duplicates, taxa, classifications, entities, entity_relationships). It explicitly **excludes** the `text` field of the `reports` collection from that license. |
| Scrape-permitted | **NO.** The same Terms of Use state, verbatim: *"High-volume means of accessing the Site, including but not limited to bots and spiders, are prohibited."* `scrape_aiid.py` runs a `ThreadPoolExecutor(max_workers=12)` against every `/cite/<id>/` URL harvested from sitemaps — this is exactly the high-volume/bot access the ToS prohibits, currently in production. |
| Redistribute-verbatim | **NO** for the `text` field (explicitly carved out of the CC license, and AIID's own ownership over it is not established either — likely third-party news-article excerpt). The `og:description` scraped here may or may not correspond 1:1 to the excluded `text` field internally; that ambiguity does not matter because the *access method itself* is already prohibited regardless of which field is touched. |
| Relicense-compatible | **NO** for the CC-BY-SA-licensed fields (share-alike ≠ plain CC-BY) — see §1.2 action. The `text` field is out of scope for any relicensing since it isn't AIID's to license in the first place. |
| Action | **(b) + (c), and this is the most severe finding in this audit: the ingestion *method* is a live ToS violation, independent of the licensing question.** AIID publishes official weekly snapshots (JSON/MongoDB/CSV) at `incidentdatabase.ai/research/snapshots/` → `https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/`, going back to March 2021 — this is the sanctioned bulk-access channel the plan anticipated ("AIID has data dumps — use them instead of OG scraping," WS0-T4). See the exact pipeline-engineer requirement in the report: **retire `scrape_aiid.py`'s concurrent HTML fetch; replace with the official snapshot download.** Content from the CC-BY-SA fields must be split-licensed (CC-BY-SA, not blanket CC-BY) in any relicense manifest; the `text`/narrative field must never be reproduced verbatim. |
| Date-checked | 2026-07-15 |

### 1.3 AI Incident Database (AIID) — via AIID's own repo data file
*Ingested by:* `scripts/ingest_external.py::ingest_aiid_oecd_bridge()` (reads
`_external/aiid/site/gatsby-site/migrations/data/oecd_relationships_2025_09_09.json`,
a file from AIID's own cloned GitHub repo) and `scripts/scrape_aiid.py`'s
`load_aiid_urls()` (same file, used only to enumerate IDs) plus two
`_external/sitemap-*.xml` files.

| Field | Value |
|---|---|
| License | Same rights-holder as §1.2 (AIID / Responsible AI Collaborative). The `responsible-ai-collaborative/aiid` GitHub repo's own code-license field returns `"Other"`/`NOASSERTION` via the GitHub API (fetched 2026-07-15) — no plain LICENSE file at `main` (404 on the raw URL). This governs the *site's code*, not necessarily this specific data file, whose content (AIID-incident-ID ↔ OECD-URL pairs) is a factual mapping table, not creative expression. |
| Scrape-permitted | N/A — local git clone of a public repo, not a live fetch. |
| Redistribute-verbatim | The mapping itself (ID + URL pairs) is treated as facts, not copyrightable expression — low risk. The *synthesized description* the ingest writes (`"Cross-listed in the AI Incident Database (AIID) as incident #{id} and tracked by the OECD AI Incidents Monitor..."`) is original text, not copied. |
| Relicense-compatible | Compatible for the ID/URL facts and the original description sentence. |
| Action | (a) compatible, low risk. No change required beyond noting the repo's own unclear code license doesn't cover a bare facts file we already treat conservatively. |
| Date-checked | 2026-07-15 |

### 1.4 MIT FutureTech AIRI Navigator
*Ingested by:* `scripts/ingest_airi_navigator.py` (downloads
`airi-navigator.com/downloads/airi-data.zip`).

| Field | Value |
|---|---|
| License | **CONFIRMED CC BY 4.0**, established one hop away from AIRI Navigator itself. AIRI Navigator's own pages were re-tested a second time on 2026-07-16 by raw-HTML substring search (not a rendered or summarizing fetch) across the home page (198,546 bytes), /about (96,530 bytes), and all 23 /about and 27 /datasets JS bundles, for "cc by", "creative commons", "licen[cs]e", and "by-sa" — zero hits everywhere. That negative finding is genuine: these are small, low-content pages, so the truncation mechanism that produced the AIAAIC false negative doesn't plausibly apply, and this check confirms that directly rather than by inference. The license lives one hop away, at the source AIRI Navigator names as its own: its Terms-of-Use modal (the text lives only inside a bundled JS file, so a rendered HTML fetch of the page never surfaces it) states that the data presented on the site is drawn from the MIT AI Risk Repository at airisk.mit.edu and related research datasets, and points users to that database page for more information. Following that named source: airisk.mit.edu returned HTTP 200, 112,503 bytes of raw HTML, whose footer (a Webflow embed div) reads: "Website copyright MIT FutureTech 2026. Data from the MIT AI Risk Initiative is licensed under CC BY 4.0," linking to creativecommons.org/licenses/by/4.0. This is corroborated independently by that same page's own JSON-LD metadata, whose publishing-principles field points to the identical creativecommons.org/licenses/by/4.0 URL. Verification: raw-HTML fetch, cross-checked independently by two parties (red-reviewer and the foreman) on 2026-07-16. This transcription did not involve any new fetch against airisk.mit.edu or airi-navigator.com; the facts above were handed over already shell-verified per the board's WS0-T1 close-out brief (decision D3). |
| Scrape-permitted | airi-navigator.com's own robots.txt returned HTTP 200 with a permissive rule set: all user agents allowed at the root, with five paths disallowed — /embed/, /admin, /login, /design-system, and /api/. Terms of Use is the modal quoted above, and it is real operative text, not merely the data-quality caveat this row previously described. The /api/ disallow is the one restriction worth flagging: even if an API existed for this data, scraping it would not be conduct-compliant; it does not cover the ZIP-download path (see Action below for that path's current status). |
| Redistribute-verbatim | Compatible for AIRI Navigator's own data under the confirmed CC BY 4.0 grant, with attribution. Remains **UNKNOWN** specifically for the AIID-derived fields the tool wraps — see Relicense-compatible. |
| Relicense-compatible | Compatible for AIRI's own CC BY 4.0 data with attribution. **UNKNOWN** only for whether AIID's CC-BY-SA share-alike (Section 1.2) applies transitively to the AIID-derived fields AIRI Navigator wraps — a wrapper's own license cannot grant away an upstream share-alike obligation it doesn't itself hold. |
| Action | **(d) UNKNOWN, narrowed.** AIRI Navigator's own license is now established as CC BY 4.0 (see License above). What remains open is only the transitive-AIID-share-alike question. Outreach is redrafted accordingly: it now asks the AIRI Navigator maintainer (Spencer Michaels, contact given on the AIRI site) only about the AIID-derived-fields question, not about AIRI's own license, which the footer at airisk.mit.edu already answers. Separately, and independent of licensing: the ZIP download this ingest relies on (airi-navigator.com/downloads/airi-data.zip, the ZIP_URL constant in scripts/ingest_airi_navigator.py) now returns HTTP 404 with zero bytes, checked on both hosts with a browser user agent and referer header on 2026-07-16. The site's own source ties the download link's rendering to a feature-flag comparison that currently evaluates false, so the withdrawal looks deliberate on MIT FutureTech's part rather than an accidental move of the file. Cross-reference WS4-T9 / E6, which independently found this ingest currently non-functional. This source produces no data until that separate, non-licensing problem is fixed. |
| Outreach date | 2026-07-16 (redrafted; not yet sent) |
| Follow-up date | 2026-08-06 (21 days) |
| Date-checked | 2026-07-16 |

### 1.5 OECD AI Incidents and Hazards Monitor (AIM)
*Ingested by:* `scripts/ingest_oecd_aim.py` (scrapes `oecd.ai/en/incidents/<id>`
pages via their embedded Angular `ng-state` JSON).

| Field | Value |
|---|---|
| License | Split. General OECD terms (`oecd.org/en/about/terms-conditions.html`) apply to OECD's *own* IP: *"Except where additional restrictions apply as stated above, you can extract from, download, copy, adapt, print, distribute, share and embed Data for any purpose, even for commercial use,"* conditioned on attribution (cite per the source's own citation format, or `OECD (year), (dataset name), (data source) DOI or URL (accessed on (date))`), with the same acknowledgment requirement passed through to any sub-licensees. Separately, **OECD written content published from 1 July 2024 onward defaults to CC BY 4.0** (the copyright/front-page of a given piece states whether a CC license applies and which one). **Re-fetch caveat:** this page still returned HTTP 403 to my direct automated fetch on 2026-07-15 (tried twice, both `https://` and `http://`) — both quotes above are corroborated across two independent web searches rather than a direct 200 read, which is a step up in confidence from the earlier single-cached-excerpt version of this row but still short of a primary-source fetch. The AIM-specific methodology page (`oecd.ai/en/incidents-methodology`, fetched 2026-07-15, direct 200) explicitly disclaims: *"Any of the copyrights, trademarks... included in the AIM are the property of their respective owners"* — meaning the incident narrative text (drawn from aggregated third-party news articles) is **not OECD's to relicense**, and by extension not ours, regardless of which general-terms regime applies to OECD's own content. |
| Scrape-permitted | `oecd.ai/robots.txt` (fetched 2026-07-15) disallows only French-language sections (`/fr/community/`, `/fr/catalogue/`, `/fr/wonk/`, `/fr/dashboards/`, `/fr/data`) — no rule blocks `/en/incidents/`. No explicit rate limit stated; the ingest script already caches and paces 10 concurrent workers, but should route through the WS0-T4 common rate-limiter like every other scraper. |
| Redistribute-verbatim | **NO** for narrative/summary text derived from third-party news content (per AIM's own disclaimer above). The ingest currently writes `body.get("summary")` or article "evidences" text into our `description` field — this is exactly the third-party-sourced content the disclaimer flags. |
| Relicense-compatible | Compatible for OECD's own structural data (incident IDs, dates, AIID cross-reference IDs, taxonomy tags) under OECD's general terms with attribution. **Not compatible** for the summary/evidence narrative text. |
| Action | **(b)/(c) hybrid.** Reduce `description` to structural facts + link where the text is evidence-derived narrative; add "Source: OECD AI Incidents and Hazards Monitor" attribution per entry. Outreach still drafted, because the open question isn't OECD's general terms (now reasonably well corroborated above) but whether AIM's own summary/evidence text counts as OECD's IP under those general terms or as the third-party content AIM's own disclaimer flags — that specific boundary is what remains genuinely unresolved. |
| Outreach date | 2026-07-15 (drafted; not yet sent) |
| Follow-up date | 2026-08-05 (21 days) |
| Date-checked | 2026-07-15 |

---

## 2. Vulnerability / advisory sources

### 2.1 CISA Known Exploited Vulnerabilities (KEV) catalog
*Ingested by:* `scripts/ingest_cisa_kev.py` (fetches
`cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json`).

| Field | Value |
|---|---|
| License | **CC0 1.0** confirmed via the community/CISA-adjacent mirror `cisagov/kev-data` LICENSE file (fetched 2026-07-15): *"The KEV database is distributed under the Creative Commons 0 1.0 License. You may use this data in any legal manner..."* Independently, as a work of the U.S. federal government, KEV content is not subject to domestic copyright (17 U.S.C. §105) regardless. The catalog JSON itself (fetched 2026-07-15) carries no license field in its metadata, but this is consistent with public-domain status rather than a gap. |
| Scrape-permitted | **YES** — the URL is CISA's own published machine-readable feed, designed for exactly this consumption. |
| Redistribute-verbatim | **YES.** |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

### 2.2 National Vulnerability Database (NVD)
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 1 — NVD REST API
2.0 keyword search).

| Field | Value |
|---|---|
| License | CVE/NVD records are U.S. government work (public domain domestically), but the NVD API imposes contractual usage terms independent of copyright: `nvd.nist.gov/developers/terms-of-use` (fetched 2026-07-15) requires a displayed notice — *"This product uses the NVD API but is not endorsed or certified by the NVD"* — states *"If you modify the content accessed through the API, you may not attribute the source as the NVD,"* and restricts API keys to the original requestor ("Keys should not be used by, or shared with, individuals or organizations other than the original requestor"). |
| Scrape-permitted | **YES, within stated rate limits** — 5 req/30s unauthenticated, 50 req/30s with an API key; the ingest script already paces requests accordingly (`NVD_SLEEP`). |
| Redistribute-verbatim | **YES** for unmodified content (public domain). Modified/derived text must not be presented as if it were still NVD's own text. |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible, with one compliance gap:** the required attribution notice above is not displayed anywhere in this repo's docs, README, or site. See the exact remediation requirement in the report. |
| Date-checked | 2026-07-15 |

### 2.3 GitHub Security Advisory Database (GHSA)
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 2 — `gh api graphql`
against `securityAdvisories`, both `GENERAL` and `MALWARE` classifications).

| Field | Value |
|---|---|
| License | **CC-BY 4.0**, confirmed via `github/advisory-database` repo (fetched 2026-07-15): *"This project is licensed under the terms of the CC-BY 4.0 open source license."* |
| Scrape-permitted | **YES** — accessed via GitHub's official authenticated GraphQL API (`gh api graphql`), not scraping. |
| Redistribute-verbatim | **YES**, with attribution. |
| Relicense-compatible | **YES** — CC-BY 4.0 is directly compatible with this project's CC-BY relicense (no share-alike conflict). |
| Action | **(a) compatible.** Confirm the render layer credits "GitHub Advisory Database" per entry (GHSA ID + link is already present in `references`). |
| Date-checked | 2026-07-15 |

### 2.4 OSV.dev
*Ingested by:* `scripts/ingest_cve_nvd_expanded.py` (Phase 3 — `api.osv.dev/v1/query`
against the `OSV_TARGETS` list of PyPI, npm, and Go-ecosystem packages).

| Field | Value |
|---|---|
| License | OSV.dev is an **aggregator**; the *code* (`google/osv.dev` repo, fetched 2026-07-15) is Apache-2.0, but individual **records carry their originating database's license**, per `google.github.io/osv.dev/data/` (fetched 2026-07-15): PyPI Advisory Database = **CC-BY 4.0**, GitHub Advisory Database = **CC-BY 4.0**, Go Vulnerability Database = **CC-BY 4.0** (confirmed separately at `vuln.go.dev/copyright`, fetched 2026-07-15: *"licensed under the Creative Commons Attribution 4.0 License"*). Given `OSV_TARGETS` only queries PyPI/npm/Go ecosystems, every source database actually reachable by this script is CC-BY 4.0. |
| Scrape-permitted | **YES** — official public API designed for this query pattern. |
| Redistribute-verbatim | **YES**, with attribution to the specific originating advisory database (not just "OSV"). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** Ensure per-entry attribution names the originating DB (e.g. "PyPI Advisory Database via OSV.dev"), not just "OSV," since that's whose license actually applies. |
| Date-checked | 2026-07-15 |

---

## 3. Attack-capability / taxonomy sources

### 3.1 MITRE ATLAS
*Ingested by:* `scripts/ingest_external.py::ingest_atlas()` (parses
`_external/atlas-data/dist/v6/ATLAS-2026.06.yaml`, a git-cloned public repo).

| Field | Value |
|---|---|
| License | **Apache License 2.0**, confirmed via `mitre-atlas/atlas-data` LICENSE file (fetched 2026-07-15): *"Copyright 2021-2026 MITRE. Licensed under the Apache License, Version 2.0."* |
| Scrape-permitted | N/A — local clone of a public repo. |
| Redistribute-verbatim | **YES** under Apache-2.0 terms (case-study titles/descriptions are reproduced from the dist YAML). |
| Relicense-compatible | **YES, with a carve-out.** Apache-2.0 does not require share-alike, but it does require preserving the copyright/license notice on the covered material — MITRE's Apache-2.0 notice must stay attached to ATLAS-derived case-study text specifically; it cannot be silently folded into a blanket "CC-BY-4.0, all rights reserved by us" claim. |
| Action | **(a) compatible**, but the repo's licensing docs (LICENSE-DATA / this file) must state the ATLAS-derived carve-out explicitly — this is a direct input to WS0-T2. |
| Date-checked | 2026-07-15 |

### 3.2 CSET-AIID Harm Taxonomy
*Ingested by:* `scripts/ingest_external.py::ingest_cset()` (checks for the
presence of `_external/CSET-AIID-harm-taxonomy` and, if present, writes
**one** original reference entry describing the taxonomy — no data is
extracted from the repo's own files).

| Field | Value |
|---|---|
| License | **UNKNOWN / none granted.** GitHub API for `georgetown-cset/CSET-AIID-harm-taxonomy` (fetched 2026-07-15) returns `"license": null` — no LICENSE file, meaning default all-rights-reserved copyright applies. **Method note (added 2026-07-16):** this finding comes from the GitHub REST API's structured `license` JSON field, not a WebFetch of a rendered HTML page — small, fixed-shape JSON, not subject to the page-length/markdown-conversion failure mode that produced the AIAAIC miss. I did not additionally re-check via a raw `curl` of the repo's file tree (no shell access); red-reviewer can confirm with `gh api repos/georgetown-cset/CSET-AIID-harm-taxonomy --jq .license` if a second check is wanted. |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | **NO** (no permission granted) — moot in practice, since the current code does not copy any of the repo's actual content; it writes one original, hand-authored description of what the taxonomy is, with a link. |
| Relicense-compatible | **NO** for repo content generally; the single original description sentence we write ourselves is fine. |
| Action | **(d) UNKNOWN, low current risk.** Outreach drafted to confirm reuse permission in case this ever grows beyond a single reference entry (see report). No code change required today since no verbatim content is taken. |
| Outreach date | 2026-07-15 (drafted; not yet sent) |
| Follow-up date | 2026-08-05 (21 days) |
| Date-checked | 2026-07-15 |

### 3.3 NVIDIA garak
*Ingested by:* `scripts/ingest_external.py::ingest_garak()` (reads probe
`.py` files under `_external/garak/garak/probes/` and extracts each probe's
module docstring).

| Field | Value |
|---|---|
| License | **Apache License 2.0**, confirmed via `NVIDIA/garak` LICENSE file (fetched 2026-07-15). Copyright held by Leon Derczynski (2023) and NVIDIA Corporation & Affiliates (2023). |
| Scrape-permitted | N/A — local clone of a public repo. |
| Redistribute-verbatim | **YES under Apache-2.0**, but note this is the one source in this file where verbatim reproduction is *actually happening*: `ingest_garak()` copies each probe's docstring text directly into our `description` field (`"NVIDIA garak LLM vulnerability scanner probe `{probe_name}`. " + desc`). Apache-2.0 permits this, conditioned on preserving the copyright/license notice for the reproduced material. |
| Relicense-compatible | **YES, with the same carve-out as ATLAS (§3.1)** — garak-derived descriptions remain under Apache-2.0 attribution, not folded into a blanket CC-BY claim. |
| Action | **(a) compatible**, but needs an explicit NOTICE/attribution carve-out in LICENSE-DATA (WS0-T2 input) naming garak-derived entries specifically. |
| Date-checked | 2026-07-15 |

### 3.4 promptfoo
*Ingested by:* `scripts/ingest_external.py::ingest_promptfoo()` (extracts
plugin/strategy ID strings from `_external/promptfoo/src/redteam/constants/*.ts`;
writes original descriptions, not copied source text).

| Field | Value |
|---|---|
| License | **MIT**, confirmed via `promptfoo/promptfoo` LICENSE file (fetched 2026-07-15). |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | Not attempted — descriptions are original ("promptfoo red-team {kind} `{pid}`. Defines an automated test for this attack class..."), not copied from source. MIT would permit verbatim reuse anyway (with notice retained). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

### 3.5 ModelOriented/CVE-AI (curated CVE list)
*Ingested by:* `scripts/ingest_external.py::ingest_cve_ai_curated()` (reads
CSV/JSON export files from `_external/CVE-AI`, copying `title`/`description`
fields into our schema).

| Field | Value |
|---|---|
| License | **MIT**, confirmed via `ModelOriented/CVE-AI` repo footer license badge (fetched 2026-07-15). |
| Scrape-permitted | N/A — local clone. |
| Redistribute-verbatim | **YES** under MIT, with attribution (already present via the reference link to the GitHub repo). |
| Relicense-compatible | **YES.** |
| Action | **(a) compatible.** No change required. |
| Date-checked | 2026-07-15 |

---

## 4. Academic red-team benchmarks (hand-curated citations)

*Ingested by:* `scripts/ingest_redteam_benchmarks.py` — the script's own
docstring states this is *"a hand-curated, citation-backed list (no
scraping)."* Each `BENCHMARKS` tuple is an **original, hand-written
description** (benchmark size, harm categories, venue) with citation links;
no paper abstract or benchmark prompt data is scraped or copied verbatim.
That fact is the load-bearing compliance point for every row below: facts
about a published benchmark (size, categories, venue) are not copyrightable
expression, and none of these entries reproduce the papers' actual text.

Two of the ten linked code repositories were independently checked; the
other eight were **not** — flagged explicitly rather than guessed, since
none of them currently matter for compliance (no verbatim/code reuse occurs).

| Benchmark | Paper venue/license | Code repo license | Verified? |
|---|---|---|---|
| JailbreakBench | arXiv (2404.01318) | jailbreakbench.github.io | Not verified |
| HarmBench | arXiv (2402.04249) | harmbench.org | Not verified |
| AdvBench / llm-attacks | arXiv (2307.15043) | **MIT** (confirmed, `llm-attacks/llm-attacks` LICENSE, fetched 2026-07-15) | Code verified |
| AgentHarm | arXiv (2410.09024) | (no repo cited in our ingest) | Not verified |
| AgentDojo | arXiv (2406.13352) | **MIT** (confirmed, `ethz-spylab/agentdojo` LICENSE, fetched 2026-07-15) | Code verified |
| InjecAgent | arXiv (2403.02691) | (no repo cited in our ingest) | Not verified |
| OS-Harm | arXiv (2506.14866) | (no repo cited in our ingest) | Not verified |
| HackAPrompt | arXiv (2311.16119) | (no repo cited in our ingest) | Not verified |
| StrongREJECT | arXiv (2402.10260) | (no repo cited in our ingest) | Not verified |
| SafetyPrompts.com | arXiv (2404.05399) | safetyprompts.com | Not verified |

| Field | Value |
|---|---|
| License (papers) | All ten cite arXiv preprints. arXiv's non-exclusive distribution license (`info.arxiv.org/help/license/`, fetched 2026-07-15) is explicit that it is **"perpetual, non-exclusive"** to arXiv only and **"limits re-use of any type from other entities or individuals"** — i.e. arXiv's license does **not** grant us any reuse right over the papers' text. This is why the ingest script must never copy verbatim abstract/paper text — and, per the code read above, it currently doesn't. |
| Scrape-permitted | N/A — no scraping occurs; this is a hand-authored, hardcoded Python list. |
| Redistribute-verbatim | **NO, and not attempted.** Only original summary sentences + citation links are stored. |
| Relicense-compatible | **YES** for our own original summary sentences (our copyrightable expression). **NOT established** for the underlying datasets (actual jailbreak/attack prompt sets) — those are untouched today and must stay that way absent a fresh per-benchmark check. |
| Action | **(a) compatible as currently implemented**, with a hard guardrail for any future change: **never extend this ingest to copy verbatim abstract text or the underlying benchmark's raw prompt/behavior data without a fresh, per-benchmark license check.** See the exact requirement in the report. |
| Date-checked | 2026-07-15 |

---

## 5. Not a source (helper module)

`scripts/ingest_utils.py` provides `robust_fetch()` / `conditional_fetch()` —
shared HTTP retry/caching helpers used by other ingest scripts. It pulls no
upstream content of its own and gets no row. (Its `USER_AGENT` string and
retry/backoff behavior are relevant to WS0-T4's conduct policy, not to this
per-source license audit.)

---

## Summary of outcomes requiring escalation (not resolved in the project's favor)

| # | Source | Outcome | Why it's an escalation |
|---|---|---|---|
| 1 | AIID direct scrape (`scrape_aiid.py`) | **(b)+(c), active ToS violation** | Bot/high-volume access is explicitly prohibited by AIID's own Terms of Use; an official weekly-snapshot alternative exists today. This is a data-acquisition-method fix, not a data-drop, but it blocks Phase-2 per the plan's gate ("Phase 2 structural work must not begin while WS0-T1 licensing outcomes for a source are unknown"). |
| 2 | AIAAIC Repository | **(b) copyright share-alike resolved by decision D2** — license confirmed CC BY-SA 4.0; handled by reducing to facts+link, not by split-licensing. **The separate EU/UK sui generis database-right question is OPEN, pending qualified counsel / a user decision** (options: engage counsel / conservative ingest redesign / accept residual risk) — see `docs/audits/WS0-E13-database-right-2026-07-18.md` | Verbatim spreadsheet-cell text carried a real copyright share-alike obligation; per D2 (2026-07-16, human) the project honors it by not carrying verbatim text at all, keeping one clean CC-BY-4.0 license with no BY-SA subset. That decision disposes of the *copyright* question only. E13 (2026-07-18) finds AIAAIC's database right plausibly subsists and the ~1,513-row categorical-fields extraction plausibly meets the substantiality threshold even after the D2/D9 reduction — facts+link mitigates but does not eliminate exposure. Not a resolved decision on record; an open question routed to the user. |
| 3 | OECD AIM | **(b)/(c) hybrid** | Narrative summary text is explicitly disclaimed by OECD as third-party IP. |
| 4 | MIT AIRI Navigator | **(d) UNKNOWN, narrowed** — own license confirmed CC BY 4.0; only the transitive AIID share-alike question is open | AIRI Navigator's own license is established via a one-hop raw-HTML check: its Terms-of-Use modal names airisk.mit.edu as its data source, and that page's footer carries the CC BY 4.0 grant, re-verified 2026-07-16 and cross-checked independently by red-reviewer and the foreman. What remains genuinely unresolved is only whether AIID's CC-BY-SA share-alike (Section 1.2) applies transitively to the AIID-derived fields this tool wraps; see §1.4. |
| 5 | CSET-AIID Harm Taxonomy | **(d) UNKNOWN**, low current risk | No license file exists upstream, confirmed via the GitHub API's structured `license` field (not a large-page fetch, so not subject to the AIAAIC failure mode) — only one original sentence currently reproduced. |

Three of the five (AIAAIC, MIT AIRI Navigator, CSET-AIID) originally carried
outreach-pending status. AIAAIC's *copyright* share-alike question is now
resolved and its handling decided (D2) — but AIAAIC separately carries an
**open, unresolved EU/UK sui generis database-right question**, per E13
(2026-07-18, `docs/audits/WS0-E13-database-right-2026-07-18.md`), pending
qualified counsel or a user decision. AIAAIC is therefore **not** fully
closed out. **MIT AIRI Navigator, CSET-AIID Harm Taxonomy, and AIAAIC's
database-right question** remain open with dated pending-status records;
OECD AIM carries a narrower, still-genuine open question (does AIM's own
summary text count as OECD's reusable IP or third-party content?), also
dated. Outreach emails are drafted in the report below, not sent — the
human sends them.
