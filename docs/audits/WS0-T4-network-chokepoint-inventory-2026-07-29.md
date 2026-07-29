# WS0-T4 conduct-half: network chokepoint inventory (2026-07-29)

Completeness proof for invariant 5 (`MASTER_IMPROVEMENT_PLAN.md`: "All
network fetching goes through `ingest/common.py`") going active on this
task's merge, and the evidence base for `docs/INGESTION_CONDUCT.md`. This
document inherits and completes a prior specialist session's uncommitted
work on branch `ws0/t4-conduct-half` (`scripts/ingest_utils.py` promoted to
`ingest/common.py`); the findings below are re-derived independently, not
copied from the prior session's state.

## 1. Per-script inventory

Every script under `scripts/` that performs, or historically performed, a
live network fetch, its target(s), the `ingest.common` function it routes
through, its robots.txt verdict (re-verified 2026-07-29 via
`ingest.common.robots_allowed()` itself — dogfooding the real code path, not
a separate probe), and its pacing.

| Script | Target(s) | Chokepoint function | robots verdict | Pacing |
|---|---|---|---|---|
| `build_cwe_capec.py` | `capec.mitre.org/data/csv/2000.csv.zip` | `fetch_once()` | Allowed | `DEFAULT_MIN_INTERVAL` (1.0 s), no override |
| `ingest_aiaaic_sheet.py` | `docs.google.com/spreadsheets/.../export?format=csv` | `conditional_fetch()` | Allowed | `DEFAULT_MIN_INTERVAL` |
| `ingest_aiid_snapshot.py` | `incidentdatabase.ai/research/snapshots/` (index); `pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-*.tar.bz2` (archive) | `robust_fetch()` (both) | Allowed (both hosts) | `DEFAULT_MIN_INTERVAL` |
| `ingest_airi_navigator.py` | `airi-navigator.com/downloads/airi-data.zip` | `conditional_fetch()` | Allowed | `DEFAULT_MIN_INTERVAL` |
| `ingest_cisa_kev.py` | `www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` | `fetch_once()` | **Unverifiable, allowlisted** (§2 below) | `DEFAULT_MIN_INTERVAL` (rate limit unaffected by the allowlist) |
| `ingest_cve_nvd_expanded.py` — NVD phase | `services.nvd.nist.gov/rest/json/cves/2.0` | `fetch_once()` (via the script's own `http_get()` retry wrapper) | Allowed | `NVD_SLEEP` (§3 below) |
| `ingest_cve_nvd_expanded.py` — GHSA phase | GitHub GraphQL, via `gh api graphql` subprocess | **N/A — not a Python-level fetch** (§4 below) | N/A | GitHub's own CLI rate limiting |
| `ingest_cve_nvd_expanded.py` — OSV phase | `api.osv.dev/v1/query` | `fetch_once()` (via `http_post_json()`) | Allowed | `DEFAULT_MIN_INTERVAL` (§3 below) |
| `ingest_oecd_aim.py` | `oecd.ai/sitemaps/incident-monitor-sitemap.xml`; `oecd.ai/en/incidents/<id>` (many, `ThreadPoolExecutor(max_workers=10)`) | `fetch_once()` (sitemap); `robust_fetch()` (pages) | Allowed | `DEFAULT_MIN_INTERVAL`, enforced **globally across the 10 worker threads** via `_rate_limit()`'s shared lock — see `ingest/common.py:177-197` |
| `scripts/scrape_aiid.py` | `incidentdatabase.ai/cite/<id>/` | **None — disabled, dead code** | N/A | N/A |

Robots verdicts were obtained by calling `ingest.common.robots_allowed()`
directly against every live target URL above, 2026-07-29 (session log
preserved below in §5). This exercises the actual production code path,
not a hand-written duplicate check.

## 2. CISA allowlist evidence (`ROBOTS_UNVERIFIABLE_ALLOWLIST["www.cisa.gov"]`)

Re-derived independently twice today (once matching the specialist report
this task inherited, once as this task's own verification), via a raw
`urllib.request.urlopen()` probe against four distinct User-Agent strings
plus `urllib`'s own unmodified default, against both the `www` and apex
hosts, plus the KEV feed URL itself:

| Target | Project UA | Plain browser UA | Bare non-Mozilla token | `urllib` default |
|---|---|---|---|---|
| `https://www.cisa.gov/robots.txt` | 403 | 403 | 403 | 403 |
| `https://cisa.gov/robots.txt` | 403 | 403 | 403 | 403 |
| KEV feed JSON | 200 (1,567,768 B) | 200 (1,567,768 B) | 200 (1,567,768 B) | 200 (1,567,768 B) |

Every UA gets an identical result on both endpoints — the byte count is
identical across all four UAs on the feed, and the refusal is identical
across all four UAs on robots.txt. This is what "unverifiable for any
client, not specifically blocked for us" means concretely: there is no UA
string that would make this pass, so fail-closed would permanently exclude
a source that has never actually refused this project's requests. Compare
`robots_allowed()`'s own live verdict for all 12 real ingest targets,
captured the same session (only CISA refuses; every other target —
`docs.google.com`, `aiaaic.org`, `airi-navigator.com`, `oecd.ai` (both the
sitemap and an incident page), `services.nvd.nist.gov`, `capec.mitre.org`,
`incidentdatabase.ai`, the AIID R2 bucket, `api.osv.dev`, `api.github.com`
— verifies True).

The allowlist entry (`ingest/common.py:122-154`) waives ONLY the
could-not-verify refusal; it has no effect if `cisa.gov` ever starts
serving a genuine `Disallow` rule (see
`tests/test_ingest_common.py::test_robots_allowlist_does_not_override_an_explicit_disallow`,
which proves this against a synthetic allowlisted host). Rate limiting and
the identifying User-Agent are unaffected — both are enforced in
`fetch_once()` unconditionally, after the robots check, regardless of the
allowlist (`ingest/common.py:336-347`).

## 3. NVD / OSV pacing — declared and justified (not a silent regression)

### NVD

**Old model** (pre-migration `ingest_cve_nvd_expanded.py`): `time.sleep(NVD_SLEEP)`
called explicitly after each page fetch and after each keyword. Effective
spacing between request *starts* = (request/parse duration) + `NVD_SLEEP` —
strictly more than `NVD_SLEEP`, but as a side effect of local processing
time, not a deliberate margin.

**New model**: `min_interval=NVD_SLEEP` passed to `fetch_once()` via the
script's own `http_get()`, which reserves the next allowed slot in
`ingest.common._rate_limit()` *before* the request runs
(`ingest/common.py:177-197`). Both ad hoc `time.sleep(NVD_SLEEP)` calls were
removed.

**Derivation of the new model's actual spacing** (worked through
`_rate_limit()`'s implementation): for two sequential calls where the first
request takes duration *D*, the second call's rate-limit wait resolves to
`max(0, min_interval - D)`, so the gap between the two requests' **start**
times is `max(D, min_interval)` — i.e. request-start spacing is *at least*
`min_interval`, always, regardless of how long the previous request took.
This is the textbook-correct way to enforce an "N requests per T seconds"
API contract, because such contracts are counted by request arrival time at
the server, not by client-side processing time — arguably a *more*
correct enforcement than the old model, not merely a different one.

**Contract check** (`docs/SOURCE_LICENSES.md` §2.2: "5 req/30s
unauthenticated, 50 req/30s with an API key"), i.e. a minimum required
spacing of `30/5 = 6.0` s unauthenticated or `30/50 = 0.6` s authenticated.
Actual `NVD_SLEEP` (`ingest_cve_nvd_expanded.py:365`): `0.7` s authenticated,
`6.5` s unauthenticated.

| Mode | Required minimum spacing | Actual `NVD_SLEEP` | Margin |
|---|---|---|---|
| Unauthenticated | 6.0 s | 6.5 s | +0.5 s (8.3%) |
| Authenticated (API key) | 0.6 s | 0.7 s | +0.1 s (16.7%) |

**Verdict: compliant, with a smaller-but-still-positive margin than before,
and via a more precise enforcement mechanism.** No code change made here;
`NVD_SLEEP`'s existing values already clear the documented floor in both
modes. If a tighter safety margin is wanted, the fix is bumping the two
`NVD_SLEEP` constants (e.g. 6.5→7.0, 0.7→0.8), not restoring the old
duration-dependent sleep pattern, which conflated implementation detail
(local parse time) with the actual contract.

### OSV

`fetch_osv()`'s per-target loop previously had an explicit
`time.sleep(0.3)` between `OSV_TARGETS` entries; this was removed and
replaced by nothing but `ingest.common`'s own default —
`http_post_json()` doesn't override `min_interval`, so every OSV request is
paced at `DEFAULT_MIN_INTERVAL` (1.0 s). `docs/SOURCE_LICENSES.md` §2.4
records no documented OSV.dev rate-limit contract to check this against, so
there is no floor to fall below — but the change is **more** conservative
than before (0.3 s → 1.0 s), the opposite direction from the NVD change.
Noted per this task's brief so both directions are on the record rather
than only the one that reads as a regression.

## 4. `gh api graphql` (GHSA phase) — scoping note, not a defect

`ingest_cve_nvd_expanded.py`'s GHSA phase (`fetch_ghsa()`) shells out to
GitHub's own CLI (`subprocess.run(["gh", "api", "graphql", ...])`), not a
Python-level HTTP call. It therefore does **not** route through
`ingest.common` and is not caught by the literal Accept-criterion grep
(`requests.|urllib|httpx`) either — `subprocess`/`gh` match neither pattern.

This was not one of the three scripts named in the board's completeness
proof (`build_cwe_capec.py`, `ingest_cisa_kev.py`,
`ingest_cve_nvd_expanded.py`'s NVD/OSV phases), and the brief for this task
did not flag it — surfacing it here because a reviewer re-deriving the
"single network chokepoint" property independently would find it, and an
un-flagged gap is worse than a flagged, reasoned one.

**Assessment: reasonably out of this invariant's intended scope, not a
bypass that should be migrated.** `gh` is GitHub's own official,
authenticated CLI tool; it carries its own auth, rate-limit awareness, and
retry/backoff behavior, none of which this project's `ingest.common` could
meaningfully improve on by wrapping it. There is no robots.txt-equivalent
concept for an authenticated GraphQL API call made through its own vendor's
tool — robots.txt governs unauthenticated crawling of publicly served
pages, which this is not. `ingest_external.py`'s MITRE ATLAS ingestion
(local `git clone`, per `docs/SOURCE_LICENSES.md` §3.1: "Scrape-permitted:
N/A — local clone of a public repo") already establishes the same kind of
precedent for a different non-HTTP-fetch access method.

**Recommendation, not implemented here (scope bound):** if this project
later wants `ingest.common` to also govern non-HTTP CLI-mediated network
access (e.g. logging every `gh` invocation's pacing centrally), that is a
separate, larger design decision — worth a future task, not a unilateral
addition to this one. Flagging it here so the foreman/user can decide
whether the invariant's wording should be narrowed to say "HTTP(S)
fetching" explicitly, closing this ambiguity rather than leaving it
implicit.

## 5. `robots_allowed()` live verdict transcript (2026-07-29)

Captured by calling `ingest.common.robots_allowed()` directly against every
real ingest target (the actual production function, not a rewritten
duplicate):

```
https://docs.google.com/spreadsheets/d/.../export?format=csv&gid=888071280 -> True
https://www.aiaaic.org/aiaaic-repository -> True
https://www.airi-navigator.com/downloads/airi-data.zip -> True
https://oecd.ai/sitemaps/incident-monitor-sitemap.xml -> True
https://oecd.ai/en/incidents/test -> True
https://services.nvd.nist.gov/rest/json/cves/2.0 -> True
https://capec.mitre.org/data/csv/2000.csv.zip -> True
https://incidentdatabase.ai/research/snapshots/ -> True
https://pub-72b2b2fc36ec423189843747af98f80e.r2.dev/backup-test.tar.bz2 -> True
https://api.osv.dev/v1/query -> True
https://api.github.com/graphql -> True
https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json -> False (unverifiable; allowlisted separately, see §2)
```

## 6. Residual grep — the plan's Accept criterion, run literally and classified

The plan's Accept criterion, run **verbatim**:

```
grep -rn 'requests\.|urllib|httpx' scripts/
```

produces these hits today (2026-07-29, post-migration):

| File:line | Match | Classification | Why |
|---|---|---|---|
| `ingest_aiaaic_sheet.py:26` | `from urllib.parse import urlparse` | **non-network helper** | Used only in `_is_aiaaic_host()` to validate a hostname against untrusted upstream summary-cell URLs; never used to fetch anything. |
| `ingest_cve_nvd_expanded.py:30` | `import urllib.error` | **non-network helper** | Exception types only, for the script's own `except` clauses around `fetch_once()`'s errors. |
| `ingest_cve_nvd_expanded.py:31` | `import urllib.parse` | **non-network helper** | `urlencode()` for building a query string, consumed by `fetch_once()` afterward — never calls `urlopen` itself. |
| `ingest_cve_nvd_expanded.py:329` | `except (urllib.error.URLError, urllib.error.HTTPError, ...)` | **non-network helper** | Exception handling in `http_get()`'s retry loop around `fetch_once()`. |
| `ingest_cve_nvd_expanded.py:350` | `except (urllib.error.URLError, urllib.error.HTTPError, ...)` | **non-network helper** | Same, in `http_post_json()`. |
| `ingest_cve_nvd_expanded.py:392` | `urllib.parse.urlencode(params)` | **non-network helper** | Builds the NVD query URL string, passed to `http_get()` → `fetch_once()`; does not itself perform a fetch. |
| `scrape_aiid.py:14` | `import urllib.request` | **inert-fetch-in-disabled-code** | Only used by `fetch_one()`, called only from `main()` (disabled — see below). |
| `scrape_aiid.py:15` | `import urllib.error` | **inert-fetch-in-disabled-code** | Same. |
| `scrape_aiid.py:81` | `req = urllib.request.Request(...)` | **inert-fetch-in-disabled-code** | Inside `fetch_one()`. |
| `scrape_aiid.py:85` | `urllib.request.urlopen(req, ...)` | **inert-fetch-in-disabled-code** | The actual live-fetch call — but unreachable: `main()` is never invoked by `make ingest-all` (`Makefile:87`, commented out) or by anything else that runs; `ingest_aiid_snapshot.py` imports only `TAXONOMY_RULES`, `is_security_relevant`, `map_taxonomy`, `severity_for` from this module — pure classification functions, never `fetch_one`/`main`. |
| `scrape_aiid.py:87` | `except (urllib.error.URLError, ...)` | **inert-fetch-in-disabled-code** | Same function. |

**Zero live-fetch matches** outside `ingest/common.py`. All matches are
either non-network stdlib helpers (`urllib.parse`, `urllib.error` used for
exception types / URL encoding, never for fetching) or inside
`scrape_aiid.py`'s permanently disabled `main()`/`fetch_one()`.

A repo-wide grep for the actual dangerous surface (`requests\.(get|post|...)|httpx\.|urllib\.request\.urlopen`,
i.e. excluding the non-fetching `urllib.parse`/`urllib.error` false-positive
sources above) confirms the same conclusion from the opposite direction —
exactly four files match: `ingest/common.py` (the chokepoint itself — two
real calls, the robots-fetch at `_get_robots_parser()` and the live-content
fetch at `fetch_once()`, plus several docstring/comment mentions of the
`urllib.request.urlopen` name that aren't calls at all), `scrape_aiid.py`
(the named inert exception), and `tests/test_ingest_common.py` /
`tests/conftest.py` (both only reference the dotted name as a **string**
argument to `unittest.mock.patch(...)`, which never executes a call).
(WS0-T4 bounce #1, R6: this section previously hardcoded a specific
docstring-mention count that drifted the next time this module's prose was
edited — the exact number isn't the property that matters and this
paragraph no longer asserts one; `tests/test_network_chokepoint.py::test_chokepoint_file_itself_still_contains_the_fetch_surface`
is the actual enforcement that the two real calls exist, not this doc.)

`tests/test_network_chokepoint.py` enforces this going forward via AST
parsing (resolving call targets through each file's own import bindings,
so aliasing doesn't evade it), not string grep — see that file's own
docstring for why AST beats grep here (the literal-grep noise above is
exactly the false-positive class an AST-based check avoids). It has four
tests: no bypass exists outside the chokepoint + the named inert exception;
the inert exception is still actually inert (Makefile tripwire); the
chokepoint module itself still contains the expected fetch surface
(positive control, so a "zero bypasses found" result can't be a broken
scanner finding nothing); and the literal Accept-criterion grep's matched
file set is pinned so a NEW match gets a human classification instead of
silently joining this table's assumptions.

**Sanity-checked non-vacuously**: the AST scanner was verified against
three synthetic bypass patterns before being trusted for the assertion
above — a direct `urllib.request.urlopen(...)` call, a `requests.get(...)`
call, and a `from urllib.request import urlopen; urlopen(...)` call — all
three were correctly detected outside their host files.

## 7. Accept criterion verdict

The plan's Accept criterion (`MASTER_IMPROVEMENT_PLAN.md:82`) has two
clauses:

> grep shows no `requests.`/`urllib`/`httpx` usage outside
> `ingest/common.py`; outreach emails drafted, sent (human sends), and
> logged with dates in the doc.

**Clause 1 (grep), literal reading: FAILS.** The literal grep command in
the criterion's own text, run against `scripts/` as scoped, returns 11
non-empty hits (§6 above) — none of them a live bypass, but the literal
command does not exit clean. **Clause 1, documented/intended reading:
PASSES.** The property the invariant actually protects — a single, enforced
home for the fetch surface (`urlopen`, `requests.*`, `httpx.*`) — holds with
zero exceptions beyond the one named, justified, dead-code case, and that
holding is now enforced by `tests/test_network_chokepoint.py`, not merely
asserted in prose.

**Clause 2 (outreach), verdict: PARTIALLY SATISFIED.** AIID and AIAAIC both
have drafted-and-sent outreach with logged dates (`docs/INGESTION_CONDUCT.md`'s
outreach log). **OECD AI Incidents and Hazards Monitor has no outreach draft
of any kind** — not merely unsent, entirely absent from
`docs/outreach/`. This is a real gap against the criterion's plain text,
not a documentation omission on this task's part.

**Overall, in the user's own terms (Phase-1 exit checklist: "flag any
criterion satisfied on a TECHNICALITY"): this criterion is satisfied on a
documented reading for clause 1 and NOT satisfied for clause 2.** Flagging
both explicitly rather than rounding either up:
- Clause 1's literal grep command, if run exactly as written in the plan,
  fails today and will keep failing as long as `urllib.parse`/`urllib.error`
  exist anywhere in `scripts/` for non-network purposes — which is a
  permanent, correct feature of the code, not a defect to fix away. **This
  task recommends the plan's Accept-criterion wording be tightened** — e.g.
  to name the actual fetch surface (`urlopen`/`requests.<verb>`/`httpx.<verb>`)
  rather than the bare substrings `urllib`/`httpx`, which the module's own
  non-network standard-library usage will always trip. This is a wording
  recommendation only; per this task's scope bounds, the plan itself is not
  edited here — the foreman/user makes that call.
- Clause 2 is an outright gap, escalated to the user by the foreman
  separately from this report (per this task's brief); this task does not
  draft the missing OECD email (outreach is license-auditor/user territory)
  and does not claim clause 2 is satisfied.

## 8. Test suite fix (finding 1)

`tests/test_ingest_common.py::test_fetch_once_raises_permission_error_when_robots_disallows`
was mis-scoped relative to its own name: it fed a 403 on `/robots.txt`
itself (the could-not-verify / fail-closed path) while asserting on
`mock_open.call_count == 1`, when `_get_robots_parser()`'s deliberate
one-retry policy (`ingest/common.py:206-210`, a real observed
transient-failure mode from this module's own development) makes that path
cost exactly 2 `urlopen` calls. It also didn't patch `time.sleep`, so the
suite burned a real 1 s sleep on every run.

Fixed by:
- Renaming the existing test to
  `test_fetch_once_raises_permission_error_when_robots_unverifiable`,
  correcting its assertion to `call_count == 2`, patching
  `ingest.common.time.sleep`, and asserting both calls targeted
  `robots.txt` (never the content URL).
- Adding a new, correctly-named
  `test_fetch_once_raises_permission_error_when_robots_disallows`, covering
  the genuine path this project's own naming convention implies: robots.txt
  fetched successfully (one call, no retry), and its rules explicitly
  forbid the URL.
- Adding four allowlist-specific tests (`ROBOTS_UNVERIFIABLE_ALLOWLIST` true
  case, non-allowlisted-host false case, allowlist-does-not-override-a-real-Disallow,
  and an end-to-end `fetch_once()` success case for an allowlisted host) and
  one signature test proving `fetch_once()` has no `check_robots` parameter.

`python -m pytest -q`: **261 passed** (was 250 passed / 1 failed before this
task; +6 in `tests/test_ingest_common.py`, +4 new in
`tests/test_network_chokepoint.py`. 2.15 s wall time — the accidental 1 s
sleep is gone).

## 9. `ingest/` package leakage into the built distribution (finding 8)

Verified empirically, not just by reading `pyproject.toml`: installed
`build`+`hatchling` locally (dev-tooling only, not added to
`pyproject.toml`'s `dependencies = []`) and ran `python -m build --wheel
--sdist` to a scratch directory outside the repo, then inspected both
archives' member lists.

- **Wheel**: 10 entries total, **zero** matching `ingest` in any form.
- **Sdist**: 18 entries total. One `ingest`-related entry:
  `genai_incidents-2.8.0/ingest/README.md`. **Not new leakage from this
  task** — `ingest/README.md` predates WS0-T4 (added at commit `8e624ba7`,
  confirmed via `git log --follow`) and is a plain doc file, not code or
  data. It appears because hatchling's sdist target unconditionally
  includes README/LICENSE/`.gitignore`-named files at any path regardless
  of the `[tool.hatch.build] include` allowlist (`docs/outreach/README.md`
  shows the identical behavior in the same sdist listing) — a standing
  hatchling default this task's config changes don't touch. Neither
  `ingest/__init__.py`, `ingest/common.py`, nor any `ingest/*.json` corpus
  file appears in either archive.
- `git status --porcelain --untracked-files=all` was empty of build
  artifacts both during and after this check — the build ran entirely
  against a temp output directory outside the repo tree, confirmed clean.

**Conclusion: no leakage, confirmed by an actual build, not just
config-reading.** `merge_and_dedupe.py`'s `INGEST.glob("*.json")`
(`scripts/merge_and_dedupe.py:1336`) is also unaffected by the new `.py`
files, since `glob("*.json")` never matches `.py` extensions regardless of
how many exist alongside the JSON files.

## 10. `ingest/__pycache__` gitignored

Confirmed: `.gitignore`'s blanket `__pycache__/` rule (top of file) covers
it; `git status --porcelain --untracked-files=all` never shows an
`ingest/__pycache__/` entry despite `ingest/` now being an importable
package with cached bytecode after every test run.

## 11. USER_AGENT version/prefix (finding 7)

- **Version drift**: `USER_AGENT` carried a hardcoded `genai_incidents/2.0`
  against the project's actual `pyproject.toml` version, `2.8.0`. Fixed —
  bumped to `2.8.0`. This project has no single source of truth for its own
  version yet (`scripts/merge_and_dedupe.py:1687` hardcodes the identical
  `"2.8.0"` string independently, the same pattern, not a novel one this
  task introduced); introducing one is a repo-wide decision out of this
  task's scope, flagged here as a follow-up rather than attempted
  unilaterally.
- **`Mozilla/5.0` prefix — REVERSED in bounce #1 (D3), see §13.** This
  section originally kept the `Mozilla/5.0` prefix, reasoning only about the
  over-match risk (a host rule targeting the literal token "mozilla" would
  also catch us). red-reviewer correctly identified that this reasoning
  never examined the opposite, worse direction: **under-matching**. An
  operator who reads our identifying UA and writes a rule naming
  `genai_incidents` specifically would have been silently ignored, because
  `robotparser.Entry.applies_to()` reduces a `Mozilla/5.0`-led UA string to
  the bare token `"mozilla"` — an identity that cannot be addressed by name
  is not the "identifying User-Agent" the conduct policy promises. The WAF-
  rejection risk that justified keeping the prefix also turned out to have
  no supporting measurement: a live probe (§13) found zero difference in
  robots verdict or fetch outcome across all 18 real target checks between
  a `Mozilla/5.0`-led and a project-token-led UA, including on CISA — the
  one host with any on-record evidence of UA-sensitive behavior at all.
  **Decision reversed: `USER_AGENT` now leads with the project token**
  (`genai_incidents/2.8.0 (+https://github.com/emmanuelgjr; contact:
  emmanuelgjr@gmail.com)`), addressable by name, with the `mozilla`
  over-match risk removed as a side effect of the same change.

## 12. Zero-data-delta proof (working agreement 2)

This task is data-neutral by design (a conduct/tooling migration, not a
data transform), so the deliverable is a proof of *no* delta, not a delta
table.

**Method**: ran the full `make build` sequence manually (`make` itself is
unavailable in this shell environment; ran each of its four constituent
commands directly — `python scripts/parse_existing.py`,
`python scripts/merge_and_dedupe.py`, `python scripts/render_markdown.py`,
`python scripts/render_docs_stats.py`, `python scripts/validate.py`, i.e.
`merge render render-docs-stats validate` per `Makefile:6`) on this branch,
with this task's `ingest/common.py`/script changes applied, and compared
against `git status --porcelain --untracked-files=all` before and after,
plus explicit SHA-256 hashes of every `data/*.json` file and `INCIDENTS.md`
taken immediately before the sequence and immediately after.

**Result**: `git status --porcelain` is byte-identical before and after
(same pre-existing WS0-T4 file list; zero new or modified entries under
`data/`, `docs/incidents/`, `docs/data/`, or `src/genai_incidents/data/`).
The explicit SHA-256 hashes of all nine `data/*.json` files and
`INCIDENTS.md` are identical before and after, including
`data/legacy_consolidated.json` (gitignored, regenerates a `date.today()`
stamp on every run — identical here because this session's run happened on
the same calendar day as the snapshot it was compared against, not because
the stamping logic was disabled). `13119/13119` entries validated with `0`
errors; `render-docs-stats` reported "all doc surfaces already match
`data/stats.json` (no-op)".

**Conclusion: confirmed zero data delta.** This task made no network calls
during `make build` (consistent with `ingest/common.py`'s own module
docstring claim, `WS4-T1`'s `make build` contract, and this task's own scope
bound against touching `data/*.json`) and produced byte-identical
committed/tracked build output.

---

# Bounce #1 (2026-07-29): D1–D3, R1–R6

red-reviewer BOUNCE #1, foreman-reproduced. Three defects (D1–D3) and six
advisories the foreman elevated to required (R1–R6). This section documents
each fix, its verification, and — for D1 and D3 — evidence beyond what the
bounce report asked for, surfaced by following each fix downstream rather
than stopping at the line the report named.

## 13. D3: UA identification probe (Mozilla/5.0-led vs. project-token-led)

`urllib.robotparser.Entry.applies_to()` reduces a UA string to
`useragent.split("/")[0].lower()` before matching it against a rule's own
`User-agent:` token. Confirmed directly:

```
"genai_incidents/2.8.0 (+https://github.com/emmanuelgjr; contact: ...)".split("/")[0].lower() -> "genai_incidents"
"Mozilla/5.0 (genai_incidents/2.8.0; +https://github.com/emmanuelgjr; ...)".split("/")[0].lower() -> "mozilla"
```

A `robotparser` check against both synthetic rule sets confirms the
practical consequence:

| Rule | Mozilla/5.0-led UA | project-token-led UA |
|---|---|---|
| `User-agent: genai_incidents` / `Disallow: /` | **NOT blocked** (rule never matches — silently ignored) | Blocked (correctly addressed) |
| `User-agent: mozilla` / `Disallow: /` | Blocked (incidental over-match) | Not blocked |

Then, per the bounce report's instruction, re-ran the robots-verdict and a
live content-fetch probe across every real ingest target with BOTH UA
shapes, to check for a regression before switching:

| Target | Mozilla-led | project-token-led | Match |
|---|---|---|---|
| `docs.google.com/robots.txt` | 200 / 582 B | 200 / 582 B | same |
| AIAAIC sheet CSV export | 200 / 961,119 B | 200 / 961,119 B | same |
| `aiaaic.org/robots.txt` | 404 | 404 | same |
| `aiaaic.org/aiaaic-repository` | 200 / ~4.51 MB | 200 / ~4.51 MB | same (see note below) |
| `airi-navigator.com/robots.txt` | 200 / 169 B | 200 / 169 B | same |
| AIRI ZIP download | 404 | 404 | same (pre-existing withdrawal, unrelated to UA) |
| `oecd.ai/robots.txt` | 200 / 128 B | 200 / 128 B | same |
| `oecd.ai` incident-monitor sitemap | 200 / 1,820,305 B | 200 / 1,820,305 B | same |
| `services.nvd.nist.gov/robots.txt` | 404 | 404 | same |
| NVD API (1-result query) | 200 / 2,517 B | 200 / 2,517 B | same |
| `capec.mitre.org/robots.txt` | 200 / 274 B | 200 / 274 B | same |
| `incidentdatabase.ai/robots.txt` | 404 | 404 | same |
| AIID snapshots index | 200 / 369,429 B | 200 / 369,429 B | same |
| R2 bucket `/robots.txt` | 404 | 404 | same |
| `api.osv.dev/robots.txt` | 404 | 404 | same |
| `api.github.com/robots.txt` | 404 | 404 | same |
| `www.cisa.gov/robots.txt` | 403 | 403 | same |
| CISA KEV feed | 200 / 1,567,768 B | 200 / 1,567,768 B | same |

**Zero regressions across all 18 checks, including CISA — the one host
with any on-record evidence of UA-sensitive behavior at all.** The single
apparent difference (the AIAAIC repository page: 4,511,105 B vs. 4,511,157
B, a 52-byte gap) is **not UA-driven** — re-fetched the identical URL with
the identical UA three times in a row and got three different byte counts
(4,511,045 / 4,511,104 / 4,511,156), proving the page itself is dynamic
(embeds some per-request-varying content — a timestamp, token, or similar)
and the earlier apparent UA-linked difference was coincidental page churn
between two nearly-simultaneous requests, not a UA effect. (This page is
also not part of this pipeline's actual fetch surface — AIAAIC ingestion
reads `docs.google.com`'s CSV export, not this HTML page directly; it was
probed anyway for completeness since earlier documents referenced it.)

**Conclusion: the WAF-rejection concern that justified keeping
`Mozilla/5.0` had no supporting measurement, and does not hold up against
one.** `USER_AGENT` now leads with the project token:
`genai_incidents/2.8.0 (+https://github.com/emmanuelgjr; contact:
emmanuelgjr@gmail.com)` — see `ingest/common.py`'s updated comment
(immediately above the `USER_AGENT` constant) for the full reasoning, and
§11 above (updated in place) for the corrected decision record.

## 14. D1: `PermissionError` retry-masking, fixed, followed downstream

**The bug**: `PermissionError` is an `OSError` subclass
(`issubclass(PermissionError, OSError) == True`, confirmed). `robust_fetch()`
and `conditional_fetch()` (`ingest/common.py`) both caught the broad
`OSError` family, so a robots.txt refusal — which should propagate
immediately per the docstring's own stated intent — was instead retried
with exponential backoff (up to 2+4=6s wasted) and then re-raised as a
generic `RuntimeError("Failed to fetch ... after N attempts: ...")`,
indistinguishable from ordinary network flakiness. `ingest_cve_nvd_expanded.py`'s
`http_get()`/`http_post_json()` had the identical bug.

**Fix**: added `except PermissionError: raise` ahead of the broad
`OSError`-inclusive clause in all four functions (`robust_fetch`,
`conditional_fetch` in `ingest/common.py`; `http_get`, `http_post_json` in
`ingest_cve_nvd_expanded.py`). A robots refusal now propagates immediately
and unwrapped, retaining its specific, clear message.

**Followed downstream, empirically, not just reasoned about** — ran three
scripted probes (mocking `fetch_once`/`urlopen` to raise `PermissionError`
and observing what actually happens through the real call chains):

1. `robust_fetch()` now propagates `PermissionError` (not `RuntimeError`) —
   confirmed.
2. `http_get()` now propagates `PermissionError` — confirmed. This closes a
   SECOND bug the bounce report flagged as a disclosure item, as an
   automatic consequence of the D1 fix: `fetch_nvd_keyword()`'s
   `except RuntimeError as e: break` no longer catches the exception (it's
   not a `RuntimeError`), so it propagates OUT of `fetch_nvd_keyword()`
   entirely, **skipping** the unconditional `cache_file.write_text(all_items)`
   line that used to run right after the old `break`. Confirmed empirically:
   a mocked robots-refusal run left `cache_file.exists() == False` — no
   poisoned empty-result cache gets written for a robots-blocked keyword
   anymore. (This risk remains open for OTHER persistent failures that
   still get wrapped as `RuntimeError` — e.g. a host down for all 4
   retries — a separate, pre-existing issue out of this bounce's scope.)
3. `fetch_page()` (`ingest_oecd_aim.py`) now propagates `PermissionError`
   past its own `except RuntimeError as e:` swallow — confirmed. Inside
   `main()`'s `ThreadPoolExecutor`, `fut.result()` has no surrounding
   `try`/`except`, so this crashes `ingest_oecd_aim.py`'s whole process
   (non-zero exit) rather than silently skipping one page and continuing —
   see §18 (R4) for what this means operationally, verified against the
   actual GitHub Actions workflow rather than assumed.

**A further, genuinely new finding, beyond what either D1 or R4 named**:
`ingest_cve_nvd_expanded.py`'s `main()` wraps its per-keyword call to
`fetch_nvd_keyword()` in `except Exception as e: print(...); continue` — a
broader catch than `fetch_nvd_keyword()`'s own inner `except RuntimeError`.
This DOES catch the now-propagating `PermissionError`, one level up, and
the loop would otherwise continue silently trying every remaining NVD
keyword against the same now-provably-blocked host, each failing
identically, ending with the script exiting 0 and 0 NVD-phase results —
correctly distinguishable in the log (each line now says "refusing to
fetch... robots.txt disallows" instead of "GET ... failed after 4
attempts"), but not surfaced as a script- or workflow-level failure signal
at all. **Fixed**: added a specific `except PermissionError` branch in that
loop that prints one clear "NVD phase aborted" message and `break`s out of
the per-keyword loop entirely (instead of wastefully repeating an
already-confirmed refusal N more times), while leaving the GHSA/OSV phases
below — different hosts, unaffected — to run normally. This does NOT make
the script exit non-zero for this case; see §18 for why that's disclosed
as a known, accepted limitation rather than also fixed here.

## 15. D2: the vacuous Makefile tripwire, fixed and self-tested

**The bug**: `tests/test_network_chokepoint.py`'s
`test_the_inert_allowlist_entry_is_still_actually_inert` asserted
`"python scripts/scrape_aiid.py" not in makefile.splitlines()` — an exact
whole-line string match. Make recipe lines are tab-prefixed
(`"\tpython scripts/scrape_aiid.py"`), and `str.splitlines()` does not
strip that tab, so `"\tpython scripts/scrape_aiid.py" !=
"python scripts/scrape_aiid.py"` as plain strings — the assertion could
**never** fire against the exact regression it existed to catch (a real
recipe re-enablement), regardless of whether the line was actually
commented out. Foreman-reproduced by editing a copy of the Makefile to
re-enable the recipe as a genuine tab-indented line and confirming the old
assertion still passed.

**Fix**: replaced the check with `_makefile_live_scrape_aiid_lines()`,
which implements the actual Make semantic that matters — a line is a
comment (safely ignorable) if and only if its first character is literally
`#` (this is how Make itself recognizes comments, before it looks for a
leading-tab recipe line); anything else mentioning `scrape_aiid.py` is
live. Added `test_makefile_scrape_aiid_tripwire_actually_fires`, a
non-vacuity proof exercising the checker against the real commented line
plus three realistic re-enablement shapes (bare tab-indented recipe,
`$(PYTHON)`-substituted recipe, and a whitespace-varied recipe) — the first
is silent, all three of the others are caught. Both tests pass against the
real Makefile today; the self-test proves the checker isn't just
coincidentally passing the way its predecessor was.

## 16. R2: AST scanner coverage, expanded

`tests/test_network_chokepoint.py`'s `NETWORK_CALL_TARGETS` covered
`urlopen`/`requests.*`/`httpx.*` only. Added `urllib.request.urlretrieve`
(the realistic accidental regression — a one-line convenience call nobody
would think to route through `fetch_once()`), `urllib.request.build_opener`,
`http.client.HTTPConnection`/`HTTPSConnection`, and
`socket.create_connection` (the lowest-level stdlib primitive everything
above eventually calls). `_production_py_files()` switched from
`.glob("*.py")` to `.rglob("*.py")` under both `scripts/` and `ingest/`, so
a future subdirectory is scanned rather than silently skipped (neither
directory has one today; `scripts/__pycache__` and `ingest/{_cache,_state,
__pycache__}` hold no `.py` files, confirmed). red-reviewer's original
aliasing coverage claim (`import urllib.request as ur`,
`from urllib.request import urlopen as f`) was independently confirmed true
and is unaffected by this addition — this was purely an enumeration gap in
the target set, not a design flaw in the resolution logic.

## 17. R3: the robots.txt fetch itself is now rate-limited

**The gap**: `_get_robots_parser()` called `urllib.request.urlopen()`
directly, never through `_rate_limit()` — so a host whose robots.txt is
never cacheable (any host on `ROBOTS_UNVERIFIABLE_ALLOWLIST`, by
definition, since an unverifiable outcome is deliberately never cached —
see the module's own comment on `_robots_cache`) took up to 2 unpaced
requests plus a 1s retry sleep on **every single call**, contradicting
`docs/INGESTION_CONDUCT.md`'s claim that the limiter applies "for every
host, unconditionally."

**Fix**: `_get_robots_parser()` and `robots_allowed()` both gained an
optional `min_interval` parameter (defaulting to `DEFAULT_MIN_INTERVAL`,
so no caller is forced to change); `_get_robots_parser()` now calls
`_rate_limit(host, min_interval)` before each `urlopen()` attempt.
`fetch_once()` forwards its OWN `min_interval` argument into
`robots_allowed(url, min_interval)`, so the robots probe and the content
fetch that follows share one consistent per-host pacing budget — e.g. NVD's
tighter documented cadence (`NVD_SLEEP`) now governs its own robots-probe
pacing too, not just its content fetches.

**Verified two ways**: an interaction test
(`test_get_robots_parser_routes_through_the_shared_rate_limiter`) confirms
`_get_robots_parser()` calls the real `_rate_limit()` function with the
expected `(host, min_interval)` pair; a forwarding test
(`test_fetch_once_forwards_its_min_interval_to_the_robots_check`) confirms
`fetch_once()` passes its own `min_interval` through rather than always
using the module default. Both are interaction/mock-based, not
timing-based, so they stay fast and deterministic (a timing-based version
of this test would have reintroduced exactly the accidental-real-sleep
problem D1's own test fixes removed — see the note on
`test_robots_denial_is_not_cached_so_a_later_check_can_recover`, which
needed `min_interval=0` added to both its calls once robots.txt fetches
started sharing state with content-fetch pacing, or it would burn a real
~1s sleep in its second, previously-unpaced `with` block).

## 18. R4: two disclosures, verified against the actual CI mechanics rather than assumed

**(a) Per-path robots refusals and the pre-existing swallow patterns.**
Traced precisely (not just asserted) how a robots refusal now behaves for
each script that has one, post-D1-fix:

- **CISA** (`ingest_cisa_kev.py`): no swallow at all — a top-level, bare
  `fetch_once()` call with no surrounding `try`/`except`. A refusal crashes
  the script (non-zero exit) directly.
- **OECD** (`ingest_oecd_aim.py`): `fetch_page()`'s `except RuntimeError`
  no longer catches `PermissionError` (§14), so it propagates through
  `ThreadPoolExecutor.Future.result()` in `main()` (no surrounding
  `try`/`except` there either) and crashes the whole script, same as CISA.
- **NVD** (`ingest_cve_nvd_expanded.py`): `main()`'s per-keyword
  `except Exception` DOES catch it (§14) — the script does NOT crash;
  §14's added fix aborts the NVD phase specifically with one clear message,
  but the process still exits 0, and GHSA/OSV/KEV phases (unaffected,
  different hosts) still run to completion.

**What this means operationally, verified against the actual workflow YAML
rather than assumed:**
- `.github/workflows/auto-refresh.yml` runs AIRI/AIAAIC/**OECD**/**KEV**
  each as its own step with `continue-on-error: true` (lines 37-57) — so a
  CISA- or OECD-triggered process crash does NOT fail the whole workflow
  run on a single occurrence. It DOES mark that step's `outcome` as
  `failure`, which feeds two places: the "Ingest result summary" step
  (aborts the run only if ALL of AIRI+AIAAIC+OECD fail, `auto-refresh.yml:81-84`
  — note this specific check does not count KEV) and
  `scripts/check_source_health.py`'s per-source CONSECUTIVE-failure
  counter (`ingest/_state/source_health.json`, persisted durably via the
  `refresh-state` branch) — only after **3+ consecutive weekly failures**
  for a given source does "Enforce source health" (`auto-refresh.yml:242-246`)
  fail the workflow run outright. This is a graceful, tracked degradation:
  visible immediately per-run, durable across runs, hard-gating only on
  persistence — not "a single robots refusal breaks everything" and not
  "silently reports success either."
- `.github/workflows/cve-enrich.yml` (NVD's workflow) has **no**
  `continue-on-error` on its "Re-pull AI/ML CVEs" step, and no
  consecutive-failure tracking at all — but since NVD's `main()` absorbs
  the robots refusal internally (per §14's added fix, it now aborts the
  NVD phase cleanly rather than looping through it) and still exits 0, this
  distinction doesn't come into play: **an NVD robots refusal is loud in
  the console log and silent in every other respect** — no step failure,
  no health-counter entry, no workflow-level signal. This is a real,
  disclosed limitation, weaker than CISA's and OECD's degradation paths,
  and out of this bounce's scope to close further (would mean deciding
  whether a partial CVE-enrichment run should block the whole PR, a design
  question beyond "fix the retry-wrapper masking").
- The empty-cache-poisoning risk for NVD (§14, point 2) is now closed for
  robots-refusal-specifically; nothing else changes about `fetch_nvd_keyword()`'s
  behavior for other failure modes.

**(b) Fail-closed's operational blast radius.** `docs/INGESTION_CONDUCT.md`
argued fail-closed's ethics (refuse loudly rather than risk scraping past
an operator's stated wishes) without stating its exposure: this pipeline
currently touches **12 distinct hosts, once a day, over one network path**
(the AIRI/AIAAIC/OECD/KEV weekly run plus the NVD/GHSA/OSV on-demand run).
A host that 403s its robots.txt intermittently, or serves it differently
by geography/CDN edge, now breaks an ingest that used to work under the
pre-WS0-T4 no-robots-check code — a real behavior change worth stating
plainly, not just defending in the abstract. Both (a) and (b) are now
stated explicitly in `docs/INGESTION_CONDUCT.md`'s conduct-policy sections,
not left implicit.

## 19. R5, summarized (three items, three different resolutions)

1. `robust_fetch()`'s warm-cache short-circuit (`cache_path.exists() and
   ...`) returns bytes with **no robots check at all** — correct behavior
   (it's a local-disk read, not a network request; there is nothing to
   check permission for), but was undocumented. **Disclosed**: added to
   `robust_fetch()`'s own docstring (`ingest/common.py`).
2. The robots-probe's rate-limiter exemption. **Fixed** — see §17 (R3).
3. The allowlist's evidence standard being process (a human writing
   careful prose) rather than code (something that actually checks the
   prose is there and non-empty). **Fixed** — see R1 below.

## 20. R1: the allowlist can no longer be silently widened

**The gap**: `ROBOTS_UNVERIFIABLE_ALLOWLIST["evil.example.com"] = {}` waives
fail-closed for a brand-new host with zero evidence and passes the entire
suite unmodified — nothing at runtime reads `reason`/`evidence_date`/
`evidence`/`still_enforced`; `robots_allowed()` only checks dict
membership. red-reviewer correctly named this the same anti-pattern the
`check_robots` parameter was removed for: an opt-out reachable by a
one-line edit isn't a check.

**Fix**: `test_robots_unverifiable_allowlist_is_pinned_and_fully_evidenced`
(`tests/test_ingest_common.py`) pins the exact host set (mirroring
`test_literal_accept_criterion_grep_is_documented_not_silently_clean`'s
pinned-set pattern in `tests/test_network_chokepoint.py` — the asymmetry
red-reviewer flagged, that one set was pinned and this one wasn't, no
longer exists) and asserts every entry carries all four required fields as
non-empty strings. A new entry with an empty or placeholder value now fails
CI; a new entry at all requires deliberately updating the pinned set,
which is the natural point to also confirm its evidence meets the same bar
as `www.cisa.gov`'s.

## 21. R6: cosmetic count fixed at the root, not just corrected for today

§6 above previously asserted a specific `urllib.request.urlopen` occurrence
count for `ingest/common.py` that was already wrong when written (3 vs. the
actual 4) and, being a hardcoded number describing prose that keeps
changing, would have gone stale again the next time this module's comments
were edited — which is exactly what happened between the original
submission and this bounce (now 5, after this bounce's own new comments).
Fixed at the root: the paragraph no longer asserts a specific count at all,
describing the two real calls qualitatively instead and pointing to
`test_chokepoint_file_itself_still_contains_the_fetch_surface` as the
actual enforcement that they exist — a test, not a hand-counted number in
prose, is the thing that should never go stale here.

## 22. Test count and zero-data-delta re-confirmation (bounce #1)

`python -m pytest -q`: **265 passed** (was 261 before this bounce; +2 R3
interaction tests, +1 R1 allowlist-pinning test, +1 D2 non-vacuity test —
net +4 from the additions above, since D2's fix replaced one test with two
without a net change beyond that +1).

Zero-data-delta re-confirmed by the same method as §12, re-run after all
bounce-#1 changes: `git status --porcelain --untracked-files=all` shows
only the same code/test/doc files this bounce touched
(`ingest/common.py`, `scripts/ingest_cve_nvd_expanded.py`,
`tests/conftest.py`, `tests/test_ingest_common.py`,
`tests/test_network_chokepoint.py`, this document) — zero `data/*.json` or
generated-doc changes; explicit SHA-256 hashes of all `data/*.json` files
and `INCIDENTS.md`, taken immediately before and after a full manual
`make build` sequence re-run, are identical.
