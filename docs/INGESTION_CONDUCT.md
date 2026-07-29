# Ingestion conduct policy

WS0-T4 (`MASTER_IMPROVEMENT_PLAN.md`). This document states what the code in
`ingest/common.py` **enforces** — not an aspiration, a description. Every
claim below cites the line(s) in `ingest/common.py` that make it true as of
this writing (commit history / `git blame` will drift the exact line numbers
over time; the function names will not). If a claim here and the code
disagree, the code is right and this doc is stale — file that as a defect
against this doc, not against the code.

Invariant 5 (`MASTER_IMPROVEMENT_PLAN.md`, staged-invariants table, Active
from "WS0-T4 done"): **all network fetching for this repo's ingest pipeline
goes through `ingest/common.py`.** See
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` for the
completeness proof (every ingest script, its fetch targets, and confirmation
nothing else in the repo performs a live fetch) and
`tests/test_network_chokepoint.py` for the CI enforcement of that property
going forward.

## What every request through `ingest/common.py` gets

### 1. An identifying User-Agent + contact address

`USER_AGENT` (`ingest/common.py:95-98`) is a single module-level constant:

```
genai_incidents/2.8.0 (+https://github.com/emmanuelgjr; contact: emmanuelgjr@gmail.com)
```

It names the project, links to the repo, and gives a contact address
(`emmanuelgjr@gmail.com`) — the same address already published as this
project's security/abuse contact in `SECURITY.md`, reused rather than
invented for this purpose. `fetch_once()` sends this on every request
(`ingest/common.py:366`) and **strips and replaces** any caller-supplied
`User-Agent` header rather than merging it (`ingest/common.py:367-368`), so
no calling script can accidentally (or deliberately) send an unidentified or
differently-identified request — enforced, not just the default; see
`tests/test_ingest_common.py::test_fetch_once_strips_caller_supplied_user_agent`
for the specific regression this guards (a caller-supplied
`ai-incidents-ingest/1.0` string that `ingest_cve_nvd_expanded.py` hardcoded
before this migration).

**The token leads the string; it is not `Mozilla/5.0`-prefixed** (changed
in WS0-T4 bounce #1, D3, from an earlier `Mozilla/5.0 (genai_incidents/2.8.0;
...)` form). `urllib.robotparser.Entry.applies_to()` — the function every
Python-stdlib robots.txt check ultimately calls — reduces a UA string to
`useragent.split("/")[0].lower()` before comparing it to a rule's own
`User-agent:` token. A `Mozilla/5.0`-led string reduces to the bare token
`"mozilla"`, identical to essentially every browser and most bots: an
operator who read this UA and wrote `User-agent: genai_incidents` in their
robots.txt would have been silently ignored. Leading with the project token
makes that reduction resolve to `"genai_incidents"` — addressable by name —
and removes the incidental `mozilla` over-match risk in the same move. A
live probe across all 18 real ingest-target URLs (robots.txt AND the actual
content endpoint, both UA shapes) found **zero** difference in outcome,
including on `www.cisa.gov` — the one host with any on-record evidence of
UA-sensitive behavior at all — so the WAF-rejection concern that originally
justified the `Mozilla/5.0` prefix had no supporting measurement. Full
evidence: `docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`
§13.

Version number (`2.8.0`) and the full reasoning above are in the comment
immediately above the constant (`ingest/common.py:61-94`).

### 2. A robots.txt check before every fetch, fail-closed

`robots_allowed(url, min_interval)` (`ingest/common.py:279-313`) is checked
by `fetch_once()` before every request (`ingest/common.py:355-361`); a
disallowed or unverifiable URL raises `PermissionError` and the request is
never sent.

**Fail-closed, deliberately:** if robots.txt itself cannot be verified —
anything other than a 200 with parseable rules, or a confirmed 404 meaning
"no file published" — the fetch is refused, not assumed permitted
(`ingest/common.py:282-290`, `_get_robots_parser()` at
`ingest/common.py:207-276`). `_get_robots_parser()` retries once (with a 1 s
pause) before giving up, because a fast burst of parallel probe requests
during this module's own development drew one spurious 403 from a host whose
robots.txt was a confirmed clean 404 seconds later — a real, observed
transient-failure mode (`ingest/common.py:215-219`).

A confirmed 404 (no robots.txt at all) is read as "no stated restriction,"
not as an unreachable check — consistent with `docs/SOURCE_LICENSES.md`'s
existing reading of aiaaic.org's own 404 (`ingest/common.py:256-263`).

**There is no caller-side way to skip this check.** `fetch_once()` has no
`check_robots`-style parameter (`ingest/common.py:316-324`) — this was a
deliberate removal: a boolean flag on a shared function is an opt-out
reachable by a one-line edit at any call site, which defeats the point of a
single enforced chokepoint. The only way to waive the robots check for a
specific host is the enumerated allowlist below, which requires editing this
module in a reviewed commit.

**The robots.txt fetch itself is rate-limited too**, not just the content
fetch that follows it (`ingest/common.py:247`, inside
`_get_robots_parser()`'s retry loop) — this was a real gap until WS0-T4
bounce #1 (R3): the probe used to call `urlopen()` directly, unpaced, so a
host whose robots.txt could never be cached (any host on
`ROBOTS_UNVERIFIABLE_ALLOWLIST`, by construction — see the module's
`_robots_cache` comment on why an unverifiable outcome is never cached)
would take unpaced requests on **every single call**. `robots_allowed()`
now forwards its own `min_interval` into the probe, so a host's robots.txt
fetch and its content fetches share one consistent pacing budget, and the
"for every host, unconditionally" claim about the rate limiter (§3 below) is
now literally true, not just true of content fetches.

**Operational exposure of fail-closed (bounce #1, R4b), stated plainly, not
just argued for ethically:** this pipeline currently touches 12 distinct
hosts, mostly once a day, over one network path (the weekly
AIRI/AIAAIC/OECD/KEV run plus the on-demand NVD/GHSA/OSV run). A host that
403s its own robots.txt intermittently, or serves it differently by
geography or CDN edge, now breaks an ingest that worked fine under the
pre-WS0-T4 code, which never checked robots.txt at all. That is the direct,
accepted cost of fail-closed over fail-open — see the ethical case above —
stated here as an exposure, not only defended as a policy.

#### Exception: `ROBOTS_UNVERIFIABLE_ALLOWLIST`

One host is currently on this allowlist: **`www.cisa.gov`**
(`ingest/common.py:129-161`). `www.cisa.gov` and `cisa.gov` both return HTTP
403 on `/robots.txt` for **every** User-Agent tested — this project's own,
a plain browser UA, a bare non-Mozilla token, and urllib's unmodified
default — while the KEV feed itself
(`known_exploited_vulnerabilities.json`, ingested by
`scripts/ingest_cisa_kev.py`) returns HTTP 200 to the same set of UAs.
robots.txt is unreachable for any client here, not specifically blocked for
this project — so fail-closed's ordinary justification ("a host's operator
would have blocked this had their server answered") does not apply: the
server never answers robots.txt for anyone, and the actual feed being
fetched is a published US federal feed explicitly built for automated
consumption.

Verified independently three times now — once for the specialist report
this allowlist entry is drawn from, once during this task's initial pass,
once again during bounce #1's re-verification — each time via a raw
`urllib` probe with multiple distinct User-Agent strings against both hosts
plus the KEV feed URL. Full byte counts and the exact commands are in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md`.

This is also the ONLY entry currently on the allowlist, and that fact is
itself enforced, not just true today:
`tests/test_ingest_common.py::test_robots_unverifiable_allowlist_is_pinned_and_fully_evidenced`
pins the exact host set and requires every entry to carry non-empty
`reason`/`evidence_date`/`evidence`/`still_enforced` fields — added in
bounce #1 (R1) after red-reviewer pointed out that nothing at runtime
actually read those fields, so a new entry with placeholder values would
otherwise waive fail-closed for a brand-new host with zero real evidence
and pass the rest of this suite unmodified.

**What the waiver does NOT cover:**
- It applies only when robots.txt could not be fetched **at all**. A host
  that serves a robots.txt with an explicit `Disallow` rule is refused
  exactly as normal, allowlisted or not (`ingest/common.py:310-313`,
  `robots_allowed()`'s closing block — the allowlist membership check on
  line 312 is reached only when `_get_robots_parser()` returns `None` on
  line 311; a successful parse instead falls through to `rp.can_fetch()` on
  line 313, bypassing the allowlist entirely).
- The per-host rate limit and the identifying User-Agent still apply in
  full to every request to `www.cisa.gov` — nothing about this entry
  changes pacing or identification, only the robots-verification refusal.

A future exception requires the same standard: a host name, a dated,
reproducible evidence trail, and an explicit statement of what stays
enforced — added to `ROBOTS_UNVERIFIABLE_ALLOWLIST` in a reviewed commit,
never a per-call parameter, and passing the pinned-set test above (which
will fail on the host-set change until deliberately updated).

### 3. A minimum interval between requests to the same host

`_rate_limit(host, min_interval)` (`ingest/common.py:184-204`) is called by
`fetch_once()` before every request (`ingest/common.py:364`), for every host,
unconditionally — and, as of bounce #1 (R3, §2 above), by the robots.txt
probe itself too, not just the content fetch. The default spacing is
`DEFAULT_MIN_INTERVAL = 1.0` second (`ingest/common.py:105`); callers may
pass a tighter or looser `min_interval=` for a source with its own
documented cadence (NVD's stated rate-limit contract is the example this
module was built against — see the per-source table below).

The limiter is thread-safe and global per host, not per caller: the next
allowed slot is reserved under a lock before the actual sleep happens, so
concurrent requests to the *same* host from multiple threads (e.g.
`ingest_oecd_aim.py`'s 10-worker pool) still queue up to the single
per-host cadence, while requests to *other* hosts are never blocked by it
(`ingest/common.py:184-204`, docstring explains the two guarantees
explicitly).

### 4. Retry with backoff, on transient failures

`robust_fetch()` (`ingest/common.py:377-436`) and `conditional_fetch()`
(`ingest/common.py:461-523`) both route every attempt through
`fetch_once()` — so robots/rate-limit/UA are enforced on *every* retry, not
just the first attempt — and use exponential backoff (2 s, 4 s, 8 s, ...)
between attempts. A robots.txt refusal (`PermissionError`) is **not**
retried in either function; it propagates immediately and unwrapped
(`ingest/common.py:413-424`, `:502-509`), since retrying a confirmed policy
block wastes backoff time for no chance of success.

**This required its own `except PermissionError: raise` clause ahead of
each function's broad exception catch, not just careful docstring wording**
(bounce #1, D1): `PermissionError` is, surprisingly, an `OSError` subclass
(`issubclass(PermissionError, OSError) == True`), and both functions' broad
`except` clauses already caught `OSError`. Before this fix, a robots
refusal was silently retried with backoff and re-raised as a generic
`RuntimeError("Failed to fetch ... after N attempts: ...")`,
indistinguishable from an ordinary flaky host — the same bug existed in
`ingest_cve_nvd_expanded.py`'s `http_get()`/`http_post_json()`, fixed
identically.

**Downstream, per script, once the exception is no longer masked** — traced
precisely rather than assumed, in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` §18:
- **CISA** and **OECD** ingests now crash their whole process on a robots
  refusal (no surrounding `try`/`except` catches the now-correctly-typed
  exception). `.github/workflows/auto-refresh.yml` runs both with
  `continue-on-error: true` plus a durable per-source consecutive-failure
  counter, so this is loud immediately (visible per-run) and durable
  (tracked across runs) without hard-failing the whole weekly workflow on a
  single occurrence — only after 3+ consecutive weeks.
  `.github/workflows/cve-enrich.yml` has no such tracking or
  `continue-on-error`.
- **NVD**'s `main()` catches the refusal one level up (a broader
  `except Exception` around each keyword) and, per an added fix in the same
  bounce, aborts the whole NVD phase with one clear message rather than
  silently repeating the same refusal across every remaining keyword — but
  the script still exits 0, so an NVD robots refusal is loud in the console
  log only, with no step-, health-counter-, or workflow-level signal at
  all. This is a real, disclosed, and currently accepted limitation, not
  something bounce #1 closed.

Scripts with their own retry cadence (NVD, OSV — both inside
`ingest_cve_nvd_expanded.py`) call `fetch_once()` directly, once per
attempt, inside their own loop, rather than using `robust_fetch()`.

**`robust_fetch()`'s warm-cache path performs no robots check at all** —
returning bytes already on disk is a local-disk read, not a network
request, so there is nothing to check permission for
(`ingest/common.py:389-393`). This was previously true but undocumented;
disclosed here per bounce #1 (R5).

## Per-source pacing

Every real ingest target's chokepoint routing, robots verdict, and pacing is
tabulated in
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` — this
section is the policy statement; that document is the per-source evidence.

## What is out of scope for this module

- **`gh api graphql`** (`ingest_cve_nvd_expanded.py`'s GHSA phase) is a
  `subprocess` call to GitHub's official CLI, not a Python-level HTTP fetch
  — it does not go through `ingest/common.py`, and this document does not
  claim it does. `gh` carries its own authentication, rate-limiting, and
  retry behavior; there is no robots.txt-equivalent for an authenticated
  API called through its vendor's own tool. See the inventory doc for the
  full reasoning on why this is treated as out of this invariant's scope
  rather than silently omitted.
- **`make build`** never imports this module. Ingest scripts are not in the
  deterministic build path (`Makefile`'s `build` target is
  `merge render render-docs-stats validate`, none of which touch the
  network) — `ingest/common.py`'s own module docstring states this, and
  `WS4-T1`'s `make build` contract (no network, no model calls) enforces it
  independently of anything in this file.

## Outreach log

The plan's Accept criterion for this task requires outreach emails to AIID,
AIAAIC, and OECD AIM, "drafted, sent (human sends), and logged with dates."
Per `CLAUDE.md`, outreach is drafted by agents and sent by the user; this
project's escalation rule keeps that division intentionally, and this
pipeline-engineer report does not draft the missing OECD item below (see
note).

All drafts live under `docs/outreach/`; `docs/outreach/README.md` is the
authoritative index. Status as of 2026-07-29:

| Recipient | Draft(s) | Sent | Notes |
|---|---|---|---|
| AI Incident Database (AIID) | `docs/outreach/aiid-goodwill.md` | **2026-07-27** | Goodwill notice: scraping stopped, per-incident attribution added, attribution-terms question. |
| AIAAIC | `docs/outreach/aiaaic-facts-link.md` | **2026-07-27** | Database-right / ShareAlike question. |
| AIAAIC (correction) | `docs/outreach/aiaaic-correction.md` | **2026-07-29** | E17: corrected an earlier under-description of what fields are retained from AIAAIC records. |
| MIT AIRI Navigator | `docs/outreach/mit-airi-courtesy.md` | **2026-07-27** | Courtesy notice (dead ZIP download) + informal transitive-AIID licensing question. |
| MIT AI Risk Initiative | `docs/outreach/airi-draft4-export-request.md` | **2026-07-29** | Substantive sanctioned-export/API request + the same transitive-AIID question, more precisely stated. Starts the D8 30-day AIRI-hold clock. |
| **OECD AI Incidents and Hazards Monitor (AIM)** | **none** | — | **Gap, not satisfied.** No draft exists anywhere under `docs/outreach/` (confirmed against `docs/outreach/README.md`'s own index and `git log --all --diff-filter=A` for any `*oecd*` outreach file — none). `docs/SOURCE_LICENSES.md` §1.5 records an "Outreach date 2026-07-15 (drafted; not yet sent)," which this task's audit could not corroborate against any actual file; that line appears stale. **This gap is being escalated to the user by the foreman separately** (per this task's brief); drafting the OECD outreach email is license-auditor/user territory, not this task's, and is not attempted here. |

**Conclusion on the Accept criterion's outreach clause:** two of three named
recipients (AIID, AIAAIC) have drafted-and-sent outreach with logged dates;
AIID and AIAAIC are additionally corroborated by follow-up/correction
sends. **OECD AIM has no outreach at all.** The outreach clause of the
Accept criterion is therefore **not fully satisfied** — see
`docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md` for the
full Accept-criterion verdict, which covers both the outreach clause and the
grep clause together.
