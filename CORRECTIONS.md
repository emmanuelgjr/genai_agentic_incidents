# Corrections log

A public, append-only record of accepted data corrections and removals — what
changed, why, and the evidence. An authoritative dataset is one you can
*correct*; this log makes every correction transparent and auditable.

How to propose one: open a [Data correction](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=data_correction.yml)
or [Scope dispute](https://github.com/emmanuelgjr/genai_incidents/issues/new?template=scope_dispute.yml)
issue. Accepted changes are applied via PR and logged here. Removed incident IDs
are also recorded in [`data/id_deprecations.json`](data/id_deprecations.json) so
old citations still resolve.

| Date | Change | Scope | Reason | Evidence / PR |
|------|--------|-------|--------|---------------|
| 2026-06-11 | **Removed ~800 out-of-scope `malicious-package` entries** (e.g. `chai-mocks`, `sudo-prompt`, `nemo-reporter`) | bulk removal | Generic npm malware matched on weak substrings (`ai`, `prompt`, `nemo`); not AI incidents per [INCLUSION.md](INCLUSION.md). malicious-package 465 → 61. | PR #63 (v2.3.1); recorded as `out-of-scope` removals in `id_deprecations.json` |
| 2026-06-10 | Removed `CVE-2026-35020` | single removal | CNA-rejected (withdrawn from NVD). | v2.2.0 enrichment |
| 2026-06-10 | Removed MITRE ATLAS technique `AML.T0039` | mapping fix | Phantom technique — never existed in any ATLAS release (duplicated T0048). | PR #26 |

_Newest first. Each row links to the PR and, for removals, the deprecation record._
