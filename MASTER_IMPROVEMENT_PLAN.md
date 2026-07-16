# genai_incidents — Master Improvement Plan

**Version:** 1.1 · **Owner:** @emmanuelgjr · **Target:** v3.0.0
**Changes from v1.0:** all defects from the July 2026 self-audit fixed — exact task count (49), calendar replaced with dependency-ordered phases, staged invariants, baseline-first acceptance criteria, rejects-log privacy fix, deterministic summarization, archiving criterion made rate-limit-realistic, and 4 previously-unowned items added (Zenodo redeposit, CONTRIBUTING rewrite, v3.0 migration guide, AI-assisted-change policy).

**Scope:** every issue from the July 2026 external review (36 items) plus 4 audit additions, mapped to **8 workstreams (WS0–WS7) and exactly 50 tasks** (49 as of v1.1; WS4-T9 added 2026-07-16 — see the task-count-check section). Each task has an ID (`WS<n>-T<n>`), a priority (P0 = existential/legal, P1 = credibility, P2 = quality, P3 = polish), an effort estimate (S < half day, M = 1–2 days, L = 3+ days), files touched, and acceptance criteria written so they can be verified mechanically.

---

## The Five Load-Bearing Problems

Everything below is a symptom of one of these. Every PR should state which one it advances.

| # | Problem | Workstreams |
|---|---------|-------------|
| LB1 | **Identity** — incidents, vulnerabilities, and attack capabilities are one undifferentiated corpus | WS1 |
| LB2 | **Label validity** — heuristic mappings with no measured error rate | WS2 |
| LB3 | **Licensing & provenance chain** — acquisition (scraping/ToS) and redistribution (CC-BY relicense) both unresolved | WS0 |
| LB4 | **Governance & sustainability** — single maintainer, no editorial/dispute/PII/retraction policy | WS5 |
| LB5 | **Flat data model** — a list exported in STIX format, not a graph; three clocks in one date field | WS3 |

---

## Phases (dependency-ordered — no calendar dates)

Phases replace the v1.0 week schedule, which was unrealistic for a solo maintainer and contained a hard dependency inversion (the Phase-3 annotation study required an annotator recruited by a task previously scheduled after it). Phases are gated by exit criteria, not dates. Honest solo-pace expectation: Phase 1 alone is likely 4–8 weeks of elapsed time because WS0-T1 involves reading ~20 sets of legal terms and waiting on outreach replies. Work other Phase-1 tasks in parallel with that wait.

- **Phase 1 — "Honest" (→ release v2.7.0).** Docs sync'd, licensing chain documented, overclaims removed, quick wins shipped, **second annotator recruitment started (WS5-T2a)**. *Exit criteria:* WS0-T2/T5/T6, WS6-T2, WS3-T5 (decision made) done; WS0-T1 has zero blank rows — every row resolved or carrying pending-outreach status with dates; WS5-T2a outreach sent; **WS0-T3 reduction complete for sources already confirmed non-redistributable (AIAAIC now; others as their WS0-T1 rows resolve); remaining sources gated on their WS0-T1 outcomes**; **WS4-T9 done (a silently-dead ingest means the dataset misrepresents its own freshness — that is this phase's subject, not a later phase's).** *(Amended 2026-07-16: WS0-T3 was a P0 task with no phase assignment in v1.1 — the task that fixes what WS0-T1 documents was scheduled nowhere. The fold is deliberately scoped: an unscoped fold of the full ~20-source reduction would deadlock Phase 1 behind WS0-T1's outreach waits.)*
- **Phase 2 — "Restructured" (→ v3.0.0-beta).** Corpus split, schema v2 (dates + conflicts + confidence + sanitized variant), ID migration executed per the Phase-1 decision, **migration guide drafted (WS6-T8)**. *Exit criteria:* WS1-T1–T4, WS3-T1/T2/T6, WS2-T3, WS6-T8 done; determinism CI green on the new pipeline. *Gate:* Phase 2 structural work must not begin while WS0-T1 licensing outcomes for a source are unknown — licensing determines what data may even be kept.
- **Phase 3 — "Validated" (→ v3.0.0).** Label audit with error rates, ATLAS benchmark in CI, dedupe error rate measured, ingest snapshots pinned, CVE allowlist live. *Exit criteria:* WS2-T1/T2/T4/T5, WS4-T1/T4/T5, WS1-T5/T6, WS7-T3, WS6-T7, WS5-T5 done. *Dependency note:* WS2-T2 requires the annotator recruited via WS5-T2a — started in Phase 1 precisely so it lands in time.
- **Phase 4 — "Durable" (→ v3.1.0, ongoing).** Governance docs complete, PII redaction pass, signing, reconciliation, archiving backlog draining, graph relationships, distribution upgrades, co-maintainer or institutional home. *Exit criteria:* remaining tasks done; the project survives the maintainer taking a month off.

---

## Invariants (staged — mirror into CLAUDE.md)

v1.0 declared these active from day one while the enforcing infrastructure was itself a plan task — a reviewer applying them on day one would bounce everything. Fixed: each invariant has an **Active from** gate. Before its gate lands, an invariant is *advisory*: do not violate it in new work, but absence of its enforcement machinery is not a defect.

| # | Invariant | Active from |
|---|-----------|-------------|
| 1 | Never headline-count incidents + vulnerabilities + capabilities as one number | WS1-T3 done |
| 2 | Every taxonomy mapping written to data carries `{method, confidence}` | WS2-T3 done |
| 3 | Never delete an entry; set status (retracted/disputed/merged) and tombstone | now (manual edits); pipeline-enforced at WS4-T2 |
| 4 | `added` immutable; `updated` bumps only on content change | now (existing CI) |
| 5 | All network fetching goes through `ingest/common.py` (rate limit, robots.txt, UA) | WS0-T4 done |
| 6 | Docs pull counts from `data/stats.json`; hardcoded totals fail CI | WS6-T2 done |
| 7 | Raw upstream text only in full JSON; min.json/HF ship sanitized variants | WS3-T6 done |
| 8 | Merge-heuristic changes must not regress `scripts/benchmark_atlas.py` F1 > 2 pts | WS2-T1 done |
| 9 | IDs append-only, never reused; `id_deprecations.json` append-only | now |
| 10 | New source ⇒ its row in `docs/SOURCE_LICENSES.md` lands in the same PR | WS0-T1 file exists |

---

## WS0 — Legal, Licensing & Truthfulness (P0) — 6 tasks

*LB3. Do this first: it constrains what data you may even keep.*

### WS0-T1 · Per-source license & ToS audit (P0, L)
For each of the ~20 upstream source classes, document: license/terms (quote the operative clause + URL + date checked), whether bulk scraping is permitted (robots.txt + ToS), whether verbatim redistribution is permitted, whether CC-BY relicensing is compatible, and contact status.
- **Known conflicts:** AIAAIC is **CC BY-SA** (share-alike — incompatible with a plain CC-BY relicense); AIID has its own terms; OECD content has reuse conditions; verbatim vendor-blog text is copyrighted and not yours to relicense.
- **Files:** new `docs/SOURCE_LICENSES.md` (columns: source · license · scrape-permitted · redistribute-verbatim · relicense-compatible · action · date-checked).
- **Actions per outcome:** (a) compatible → document; (b) BY-SA → honor share-alike for that subset (split license by corpus) or reduce to facts+link; (c) prohibited → drop verbatim text, keep `id + url + original ≤2-sentence summary`; (d) unknown → email the maintainer and record pending status.
- **Accept:** every source in `scripts/ingest_*.py` has a row; no row is blank — UNKNOWN rows carry outreach date + follow-up date. Ambiguity is never resolved in the project's favor.

### WS0-T2 · Fix the LICENSE files so GitHub can parse them (P0, S)
GitHub currently shows "Unknown, Unknown licenses found."
- **Files:** `LICENSE` → verbatim SPDX MIT text; `LICENSE-DATA` → verbatim CC-BY-4.0 legalcode (or the WS0-T1 outcome: "CC-BY-4.0 for original content; per-source terms in SOURCE_LICENSES.md for aggregated content"); SPDX headers or `.reuse/dep5`.
- **Accept:** GitHub license detector shows MIT + CC-BY-4.0; a `licensee detect .`-equivalent check passes. *Verification is mechanical and belongs to review (the license-auditor role has no shell access by design) — the implementer states the check; the reviewer runs it.*

### WS0-T3 · Replace verbatim upstream prose with summaries where required (P0→P1, L)
**Phase: 1, scoped** — reduction lands now for sources already confirmed non-redistributable (AIAAIC per decision D2); every other source is gated on its own WS0-T1 row resolving. Do not treat this task as blocked on the whole audit finishing.

Follows from T1. For sources where verbatim text is not redistributable: `description`, `impact`, `mitigations` become an original summary + always the source URL. Keep verbatim only where licensed.
- **Derivative-work constraint (from decision D2, 2026-07-16):** for share-alike sources, summaries must be written **from the primary sources the upstream links to — never paraphrased from the upstream's own prose.** A close paraphrase of BY-SA text is arguably a derivative work, which would reimport the share-alike obligation the reduction exists to shed. This applies to AIAAIC today; it applies to any future BY-SA source by the same logic. Reducing to "facts + link" is only a real remedy if the facts are independently sourced — laundering the same prose through a paraphrase is not a reduction.
- **Determinism (fixed from v1.0):** summaries may be model-assisted but are generated **once**, committed to a source-of-record file (`data/summaries/<source>.json`), spot-checked by a human, and regenerated only per-entry when the upstream entry changes. The build pipeline *reads* committed summaries; it never calls a model. This preserves byte-for-byte reproducibility (WS4-T1) — unpinned LLM output in the build path is banned.
- **Files:** `scripts/summarize_descriptions.py` (offline generator), `data/summaries/`, `scripts/merge_and_dedupe.py`, schema: `description_provenance: verbatim|summary|original`.
- **Accept:** `jq '[.[] | select(.description_provenance=="verbatim")] | length'` = 0 for prohibited sources; `make build` makes no network/model calls; summaries directory committed.

### WS0-T4 · Scraping conduct policy + outreach (P0, M)
Document ingestion conduct: robots.txt respected, rate limits, identifying User-Agent, contact email. Implement via shared `ingest/common.py` (rate-limit + robots check) that all network scripts route through. Email AIID, AIAAIC, OECD AIM describing the project and requesting blessing / an official export (AIID has data dumps — use them instead of OG scraping).
- **Files:** `docs/INGESTION_CONDUCT.md`, `ingest/common.py`, all `scripts/ingest_*.py` / `scrape_*.py`.
- **Accept:** grep shows no `requests.`/`urllib`/`httpx` usage outside `ingest/common.py`; outreach emails drafted, sent (human sends), and logged with dates in the doc.

### WS0-T5 · Kill every overclaim in one pass (P0, S)
- "Single source of truth" → "a consolidated, machine-readable index of…"; add a short "How this differs from AIID / MIT AI Risk Repository / AVID" pointer (full comparison is WS7-T1).
- "TAXII 2.1 endpoint" → "static TAXII-compatible discovery document" until WS6-T4 resolves.
- "mapped to all four taxonomies" → enumerate the actual list (LLM Top-10, ASI, NIST AI RMF, ATLAS, MAESTRO, VERIS tags), each marked `core` / `companion` / `experimental` — resolves the MAESTRO ambiguity.
- **Files:** `README.md`, repo description, `docs/DATASHEET.md`, site index, HF card, `.zenodo.json`.
- **Accept:** grep for "single source of truth" returns 0 hits across repo + site + HF card; taxonomy list identical on all surfaces.

### WS0-T6 · Citation ethics: preferred-citation + per-incident credit (P1, S)
`preferred-citation` guidance: cite the dataset for aggregate use, cite the *underlying source* for individual incidents. Rendered "how to cite this incident" line per entry. Datasheet gains an explicit warning box: labels are heuristic; do not treat mapping counts as measured prevalence.
- **Files:** `CITATION.cff`, `scripts/render_markdown.py`, site template, `docs/DATASHEET.md`.
- **Accept:** every rendered incident shows primary-source citation; datasheet warning box present.

---

## WS1 — Corpus Identity & Restructure (P0/P1) — 6 tasks

*LB1. One dataset becomes three, each with its own quality bar.*

### WS1-T1 · Define the three sub-corpora (P0, M)
`docs/CORPUS_MODEL.md` first:
1. **incidents** — real-world exploitation, breach, misuse. Bar: verifiable occurrence, named/describable victim system, occurrence date.
2. **vulnerabilities** — CVEs/advisories affecting AI stacks. Bar: CVE or advisory ID, product identifier (WS3-T3).
3. **capabilities** — attack-technique catalog. **Every garak probe and promptfoo plugin entry moves here.** Research PoCs stay in incidents (`category: research`) only if demonstrated against a real deployed system; otherwise capabilities. Ambiguous → capabilities.
- **Accept:** rules are decidable — classify 20 random entries per the written rules in a doc appendix; any entry requiring judgment beyond the rules ⇒ tighten the rules before implementation.

### WS1-T2 · Implement the split in the pipeline (P0, L)
`corpus` mandatory + validated; outputs `data/incidents.json` / `vulnerabilities.json` / `capabilities.json` + `all.json` compat through v3.x. One schema per corpus (different required fields), coordinated with WS3.
- **Files:** `scripts/merge_and_dedupe.py`, `scripts/render_markdown.py`, `schema/`, `scripts/validate.py`, site, HF loader, Python lib.
- **Accept:** zero garak/promptfoo `source_ids` in incidents.json (jq assertion); three files emitted; per-corpus required fields enforced; `make build` twice is byte-identical.

### WS1-T3 · Stop headline-counting the union (P0, S)
- **Accept:** `data/stats.json` has `{incidents, vulnerabilities, capabilities}` keys; README/releases/datasheet/site show three numbers, never one; activates invariant 1.

### WS1-T4 · Scope-drift handling: pre-LLM / non-GenAI entries (P1, M)
Human decision (Phase 1 escalation): (a) rename scope to "AI security incidents" or (b) tag `ai_system_type: genai|agentic|classical-ml|algorithmic` and default headline/site filters to genai+agentic. **Recommendation: (b).**
- **Accept:** every entry has `ai_system_type` (source-level defaults + documented keyword rules); resulting distribution reported; site default filter set.

### WS1-T5 · Rejects log — the negative dataset (P1, M)
Log every evaluated-and-excluded candidate to `data/rejects.jsonl` with reason codes (`out-of-scope`, `no-source-url`, `duplicate`, `fairness-only-no-security-primitive`, `license-prohibited`, `pii-redaction`, …).
- **Privacy/licensing fix (from v1.0):** the log stores **identifiers only** — `{candidate_source_id, url, reason_code, date}` — **never upstream text**, titles included. For `license-prohibited` and `pii-*` reasons, store `sha256(url)` instead of the URL if the URL itself is the problem. The rejects log must not republish what WS0-T3/WS5-T3 exist to remove.
- **Accept:** rebuild produces rejects.jsonl; count in stats.json; `jq` confirms no field beyond the four allowed keys.

### WS1-T6 · Vendor-blog source bias: document + counterweight (P1, M)
`source_class: vendor-research|independent-researcher|journalism|academic|government|registry` field; datasheet section quantifying corpus share per class; feeds the WS5-T1 CoI statement.
- **Accept:** stats.json breaks down entries by source_class; datasheet section merged.

---

## WS2 — Label Quality & Validation (P0/P1) — 5 tasks

*LB2. The mappings are the value-add; their error rate is unknown.*

### WS2-T1 · ATLAS ground-truth benchmark (P0, M)
MITRE ATLAS case studies carry official technique mappings and are already ingested. `scripts/benchmark_atlas.py` compares heuristic ATLAS mappings against MITRE's labels on the overlap: per-technique P/R/F1 + micro/macro, plus a naive baseline row for context. Wire into CI with the 2-point regression gate (activates invariant 8).
- **Accept:** metrics published in `docs/LABEL_QUALITY.md`; CI fails on >2-point F1 regression; every number reproducible by one command.

### WS2-T2 · Human validation study (P1, L)
Stratified random sample (≥200; corpus × quality_tier × year, fixed seed), **2 annotators** (second annotator recruited via WS5-T2a — Phase 1 prerequisite), labeling OWASP-LLM, ASI, attack_vector, severity. Report Cohen's κ and heuristic accuracy per field; adjudication notes committed.
- **Files:** `scripts/sample_for_annotation.py`, `data/annotations/`, `docs/LABEL_QUALITY.md`.
- **Accept:** κ + per-field accuracy in datasheet §Composition; README links it. **Blocked-by:** WS5-T2a.

### WS2-T3 · Per-mapping confidence in the schema (P1, M)
Mappings become `{"code","method":"heuristic|human|source-provided|llm-assisted","confidence":0–1}`; flat arrays retained as derived compat fields. Schema shape owned by WS3; assignment logic owned here.
- **Accept:** validation requires method on every mapping; site can filter out heuristic-only; activates invariant 2.

### WS2-T4 · Attack the `other` bucket (P1, M)
**Baseline-first (fixed from v1.0):** measure the current `other` share in the incidents corpus at task start (was ~36% at review time; re-measure post-split). Cluster the bucket (deterministic seed; clustering outputs cached and committed so builds never need GPU/model); extend the attack_vector vocabulary where clusters cohere; route harm-not-attack entries to a new `harm_type` field.
- **Accept:** `other` share reduced by **≥50% relative to the measured baseline**; new vocabulary in TAXONOMIES.md; baseline + result both published.

### WS2-T5 · Severity rubric (P1, M)
`docs/SEVERITY_RUBRIC.md` decision table for non-CVSS entries. **Fix max-on-merge inflation:** per-source severities preserved in `conflicts` (WS3-T2); canonical severity is rubric-derived, never bare max().
- **Accept:** rubric published; merge no longer takes max; before/after severity distribution shift recorded in CHANGELOG.

---

## WS3 — Schema & Data Model (P1) — 6 tasks

*LB5.*

### WS3-T1 · Three clocks: date semantics (P1, M)
`occurred_date` / `disclosed_date` / `published_date`, each with `date_precision: day|month|year`. Per-source clock mapping documented in DATA_DICTIONARY. Migration is conservative: unknown clock ⇒ populate `published_date` only — never guess occurrence. Site time-axes default to disclosure date, labeled.
- **Accept:** schema v2 fields + precision; per-source assignment implemented; migration backfills; fixture test green.

### WS3-T2 · `conflicts` field — stop erasing disagreement (P1, M)
`conflicts: [{"field","kept","dropped":[{"value","source"}]}]` recorded whenever merge overrides a value (dates, severity, affected).
- **Accept:** rebuild populates conflicts; datasheet documents it.

### WS3-T3 · Machine-readable product identifiers (P1, L)
`affected_products: [{cpe, purl, vendor, product, version_range}]`, extracted from NVD CPE payloads already present in pulled data.
- **Baseline-first (fixed from v1.0 — the old "≥90%" was unmeasured and likely unattainable given advisories without CPE):** step 1, measure baseline coverage achievable from existing NVD/GHSA/OSV payloads and publish it; step 2, hard floor: **100% of entries whose upstream payload contains CPE/purl data carry it**; step 3, document the residual (advisories with no upstream identifier) and the uplift plan.
- **Accept:** baseline published; hard floor met (jq assertion comparing extracted vs available); residual documented.

### WS3-T4 · Relationships — from list to graph (P2, L)
`related: [{type: same-campaign|same-root-cause|exploits|follow-up-of|variant-of, target}]` + `threat_actor`. **Seeding criterion (fixed from v1.0's arbitrary "≥200 edges"):** the shared-CVE seeding pass must be *exhaustive* — every pair of entries sharing a CVE is linked `same-root-cause`; vendor-report campaign names linked where stated. Edge count is reported, not targeted. STIX export gains real relationship objects (with WS6-T3).
- **Accept:** exhaustiveness assertion (script proves no unlinked shared-CVE pair remains); edge count published; STIX bundle contains relationship objects; site shows related incidents.

### WS3-T5 · ID scheme headroom + stability policy (P2 — **decide in Phase 1**, S)
5-digit IDs cap at 99,999. Draft `docs/ID_POLICY.md` presenting both options — widen to 7 digits in the v3.0 break (complete old→new map in `id_deprecations.json`) vs a written padding-agnostic-parsing commitment — with a recommendation; **the human decides in Phase 1**, implementation lands in Phase 2 with the other breaking changes. Policy also states: IDs never reused; tombstones append-only; merged IDs redirect forever.
- **Accept:** decision recorded; policy published; `resolve_id()` tests cover every historical ID.

### WS3-T6 · Sanitized text variant (P1, M)
Raw verbatim kept where licensed (full JSON only); `description_safe` (HTML-escaped, payload-defanged) generated for everything; `incidents.min.json` + HF export use the safe variant.
- **Accept:** min.json and HF contain no raw `<script`/`onerror` strings (grep assertion); round-trip test proves raw preserved in full JSON; activates invariant 7.

---

## WS4 — Pipeline Integrity & Reproducibility (P1) — 9 tasks

### WS4-T1 · Pin ingest snapshots (P1, M)
`ingest/snapshots/<date>/` + `MANIFEST.json` (sha256 per file), committed or attached to releases; releases record the snapshot hash they were built from; `make build SNAPSHOT=<date>`.
- **Accept:** a tagged release rebuilds byte-for-byte from its snapshot.

### WS4-T2 · Retraction & revision sync-back (P1, L)
Reconciliation pass per refresh: REJECTED/DISPUTED CVEs ⇒ `status: retracted|disputed`; CVSS rescores update (old value into `conflicts`); edited/removed AIID entries re-diffed; downward severity revisions propagate. Entries never deleted — status + tombstone reasoning (enforces invariant 3 in the pipeline).
- **Files:** `scripts/reconcile_upstream.py`, schema `status`, weekly workflow.
- **Accept:** fixture test: a REJECTED CVE ends `status: retracted` after reconcile.

### WS4-T3 · Link archiving + dead-link monitoring (P1, M)
Wayback SPN2 submission for reference URLs via `ingest/common.py`, **queued and rate-limited** — SPN2 throttles hard, and archiving the existing ~10k+ URL backlog is a weeks-long trickle by design.
- **Acceptance (fixed from v1.0's unrealistic "≥95% after backfill" gate):** the task is done when (a) the archiving queue + worker are implemented and running error-free over a 7-day window, (b) every *newly ingested* reference is enqueued automatically, and (c) backlog progress is a tracked metric in stats.json with a monthly report. ≥95% total coverage is the tracked *goal state*, not this task's gate. Monthly liveness job opens a dead-links issue; dead references flip `reference.status: dead` and surface `archived_url`.

### WS4-T4 · CVE ingestion: keywords → package allowlist (P1, L)
`data/ai_package_allowlist.json` (CPE/purl) as the primary CVE filter; keyword sweep demoted to a *candidate feeder* requiring curation-override approval. Publish the old sweep's FP rate on a 100-entry sample (sampling coordinated with WS2 methodology).
- **Coverage criterion (fixed from v1.0's arbitrary "≥150"):** the allowlist must cover (a) every package already appearing in the current vulnerabilities corpus and (b) a curated ecosystem seed (inference/serving, agent frameworks, MCP, vector DBs, ML-ops, model formats); final count is reported, not targeted.
- **Accept:** coverage assertions (a)+(b) pass; keyword-only candidates cannot enter the corpus without an override; FP-rate note in LABEL_QUALITY.md.

### WS4-T5 · Dedupe audit + guardrails (P1, M)
Sample 100 merge decisions + 100 near-miss non-merges, hand-verify, publish false-merge and missed-dup rates. Ambiguous fuzzy-title merges route to `data/merge_review_queue.json` instead of auto-merging; per-source title normalizers added.
- **Accept:** error rates published; ambiguous merges require human confirmation.

### WS4-T6 · Parser contract tests (P2, M)
Per-source frozen fixtures + assertions that `normalize_entry` extracts required fields (not just no-crash). Weekly refresh compares live field-population rates to snapshot baseline; fails on >10% drops.
- **Accept:** every ingest script has ≥1 fixture test; population-rate check active in the workflow.

### WS4-T7 · Refresh-PR supply-chain gate (P1, M)
`docs/PIPELINE_THREAT_MODEL.md`; refresh PRs get a rendered diff summary (new/changed/removed; suspicious-content flags: script tags, data-URIs, never-seen domains); required human-reviewed checkbox; suspicious-content linter on every PR.
- **Accept:** threat model published; workflow posts the summary; linter active.

### WS4-T8 · Sign the releases (P2, S)
SHA256SUMS + cosign (Sigstore keyless via GitHub OIDC) on release assets (incidents.json, STIX bundle, HF parquet). Verification instructions tested.
- **Accept:** the documented `cosign verify-blob` procedure succeeds against the latest release.

### WS4-T9 · Dead-ingest triage: AIRI Navigator + the silent-failure pattern (P0, M) — *new 2026-07-16*
**Phase: 1** — a silently-dead ingest means the dataset misrepresents its own freshness, which is squarely Phase 1's "nothing the repo says about itself is false."

Discovered during the WS0-T1 re-gate, not by any test — which is itself the finding. `scripts/ingest_airi_navigator.py:33` fetches `https://www.airi-navigator.com/downloads/airi-data.zip`, which returns **HTTP 404 / 0 bytes** on both hosts (verified with browser UA and Referer, by two independent parties). No cache exists to mask it: `ingest/_cache/` is absent. MIT deliberately withdrew the public download — the site's own JS gates the link behind a flag evaluating false (`"FALSE".toUpperCase()!=="FALSE" && <a href="/downloads/airi-data.zip" download>`). `auto-refresh.yml` runs this ingest under `continue-on-error: true`, and its result-summary step aborts only if **all three** sources fail, so a dead source degrades to a `::warning::` nobody reads.
- **Establish:** is the AIRI ingest dead in the current build? How many corpus entries derive from it, and which fields would be lost or frozen? When did it last succeed (git history of the AIRI-derived data)?
- **Decide (escalate to the human with evidence):** retire the source, or find a sanctioned replacement (MIT FutureTech publish the AI Risk Repository at `airisk.mit.edu` — data is CC BY 4.0 per their footer; establish whether a sanctioned export exists before proposing outreach).
- **Fix the class, not just the instance:** `continue-on-error: true` plus an all-three-must-fail abort threshold is a silent-degradation pattern, not an AIRI bug. Any source that fails N consecutive refreshes must fail loudly or mark its data stale. Coordinate with WS4-T6, whose population-rate check is the mechanism that should have caught this.
- **Invariant 3 applies:** existing AIRI-derived entries are never deleted — status + tombstone if the source is retired.
- **Accept:** the ingest's live/dead status established with evidence; corpus dependency quantified; retire-or-replace decision recorded on the board; a dead or persistently-failing source can no longer pass a refresh as a warning — demonstrated by a test.

---

## WS5 — Governance, Privacy & Sustainability (P0/P1) — 6 tasks

*LB4.*

### WS5-T1 · GOVERNANCE.md (P0, M)
Sections: mission & non-goals · source add/remove criteria · **disputed-entry process** (intake channel → evidence standard → resolution SLA → `disputed` annotation on the entry, never silent deletion) · correction/takedown process with target response time · CoI statement (maintainer affiliations, no paid inclusion, vendor-blog selection criteria — uses WS1-T6 data) · decision authority (BDFL today, stated honestly) · succession plan. Concrete over aspirational: every process names actor + channel + timeframe + outcome.
- **Accept:** merged, linked from README; schema `disputed` status exists (via WS3/WS4).

### WS5-T2 · Bus factor: recruitment & institutional home (P0, split)
- **T2a — second annotator (Phase 1, S):** recruit one collaborator sufficient for the WS2-T2 study (scoped ask: ~200 entries of labeling + adjudication). Draft the outreach; identify candidates from forkers/issue-filers; human sends. *Moved ahead of the annotation study — v1.0 had this dependency inverted.*
- **T2b — co-maintainer / institutional home (Phase 4, ongoing):** pinned "maintainers wanted" issue; direct outreach to engaged contributors; proposal to OWASP GenAI Security Project or AVID for institutional homing.
- **Accept (T2a):** annotator committed before WS2-T2 sampling begins. **Accept (T2b):** ≥1 non-owner with merge rights or a documented institutional relationship within 90 days of Phase-4 start.

### WS5-T3 · PII policy + redaction pass (P0, L)
`docs/PII_POLICY.md`: public figures in public capacity retained · private individuals → role descriptions · minors always redacted. Flag (NER pass) → human review → redaction via curation overrides (survives rebuilds). GDPR-friendly erasure-request channel documented in GOVERNANCE.md.
- **Accept:** policy published; flag-and-review completed over the incidents corpus; erasure channel live.

### WS5-T4 · Naming & neutrality (P2, S)
GOVERNANCE.md paragraph stating the `genai-incidents` namespace intention: earn it via governance, or transfer PyPI/HF names to the org on institutional adoption.
- **Accept:** paragraph merged.

### WS5-T5 · CONTRIBUTING.md rewrite (P1, S) — *new in v1.1*
The corpus split and schema v2 invalidate current contributor instructions ("append an object to data/incidents.json" is wrong post-WS1). Rewrite for: per-corpus contribution paths, mapping method/confidence requirements, the SOURCE_LICENSES.md same-PR rule, validate + render steps, curation-override usage.
- **Accept:** every instruction in CONTRIBUTING.md is executable against the v3.0 layout; stale instructions gone.

### WS5-T6 · AI-assisted change policy (P1, S) — *new in v1.1*
This repo's own drift partly originated in AI-assisted building sessions — for a security dataset, that deserves an explicit policy. GOVERNANCE.md section: all LLM-generated or LLM-assisted changes receive human review before merge; data-affecting changes must pass the benchmark gate (invariant 8) and determinism CI; PRs disclose AI assistance; model output never lands in the deterministic build path (cf. WS0-T3).
- **Accept:** section merged; PR template gains the disclosure checkbox.

---

## WS6 — Distribution & Interfaces (P0–P2) — 8 tasks

### WS6-T1 · Decouple data version from code version (P1, M)
Package exposes `__version__` (code semver) + `data_version` + `data_date`; `fetch_latest()` downloads current data from Pages with SHA-256 verification (hashes from WS6-T5/WS4-T8) and caches; `docs/VERSIONING.md` defines what bumps what (schema field add = data minor; entry corrections = data patch; API break = code major); bundled-snapshot staleness documented prominently.
- **Accept:** clean-venv install → `data_version` accessible → `fetch_latest()` round-trips with hash check; VERSIONING.md answers all three "what bumps what" questions.

### WS6-T2 · Single-source all published counts (P0, S — Phase 1)
`data/stats.json` is the only source of counts; `scripts/render_docs_stats.py` templates them into README/datasheet/site/HF card; CI greps docs for hardcoded totals and fails on mismatch.
- **Accept:** CI check active (activates invariant 6); a deliberately planted stale count on a test branch is caught.

### WS6-T3 · STIX honesty + enrichment (P2, M)
Short term: clearly document the custom `x-genai-incident` SDO with tested OpenCTI/MISP import instructions ("Consuming the STIX bundle" doc, validated against a live throwaway OpenCTI). Post WS3-T4: standard `incident`/`vulnerability`/`campaign`/`intrusion-set` SDOs + relationship objects.
- **Accept:** the documented import procedure works on a live OpenCTI instance.

### WS6-T4 · TAXII: real or honestly-labeled (P2, M/L)
Human decision: deploy an actual TAXII 2.1 server (medallion/worker: collections, pagination, filtering) or keep the honest "static STIX bundle + discovery document" labeling from WS0-T5. Same validation for the MISP feed.
- **Accept:** one of the two states is true, implemented, and documented; no surface says "TAXII endpoint" for a static file.

### WS6-T5 · Website: scale, accessibility, integrity (P2, L)
Paginate/virtualize the table; per-corpus pages; 380px layout; axe-core in CI (no critical violations); Lighthouse accessibility ≥90; publish SHA-256 of served data files (integrity on Pages, since SLA isn't fixable).
- **Accept:** CI scores as stated; table usable on a 380px viewport.

### WS6-T6 · INCIDENTS.md role demotion (P3, S)
Landing page <500 lines: counts from stats.json, recent 50, links to year shards + site.
- **Accept:** `wc -l INCIDENTS.md` < 500.

### WS6-T7 · Zenodo/DOI redeposit workflow (P1, S) — *new in v1.1*
License, citation, and metadata changes (WS0-T2/T5/T6) require a **new versioned Zenodo deposit** — nobody owned this in v1.0. Document concept-DOI vs version-DOI usage; sync `.zenodo.json` with CITATION.cff; make redeposit a release-checklist step.
- **Accept:** post-Phase-1 deposit published with corrected metadata; README cites the concept DOI; release checklist includes the step.

### WS6-T8 · v3.0 migration guide (P0 at Phase 2, M) — *new in v1.1*
The breaking release ("loudly announced" in v1.0, but nobody owned the announcement) needs `docs/MIGRATING_TO_V3.md` for pip/HF/STIX/JSON consumers: corpus split and new file names, date-field split + compat fields, mapping-object shape + flat compat arrays, ID changes per the WS3-T5 decision, deprecation timeline for `all.json` and legacy fields, worked before/after examples for the Python API.
- **Accept:** guide covers every breaking change in the v3.0.0-beta diff (checked against the actual changelog); linked from README, release notes, and the PyPI description.

---

## WS7 — Positioning, Evaluation & Adoption (P1/P2) — 4 tasks

### WS7-T1 · Comparison & positioning doc (P2, M)
`docs/RELATED_WORK.md`: table vs AIID, AIAAIC, OECD AIM, MIT AI Risk Repository, AVID, ATLAS (coverage · granularity · licensing · machine-readability · taxonomy mappings · exports). The differentiator claim must survive a skeptic reading the table — if it doesn't, state the honest differentiator instead.
- **Accept:** README links it; every cell sourced.

### WS7-T2 · Demonstrate use: two worked analyses (P2, M)
CI-executed notebooks in `examples/` (pinned deps, pinned data snapshot, fixed seeds): (1) prompt-injection incident characteristics 2023→2026, disclosure-date basis, with the WS7-T3 completeness caveat computed inline; (2) top AI packages by Critical CVEs — CPE-based post-WS3-T3, free-text `affected` with a marked upgrade point before that.
- **Accept:** both notebooks run clean in CI. **Blocked-by:** WS7-T3.

### WS7-T3 · Temporal completeness analysis (P1, M)
Per-source entry counts by ingestion date vs incident/disclosure date; quantify ingestion-artifact growth; datasheet §"Reading time series"; exported caveat string auto-rendered on any site time-axis chart (hook handed to WS6).
- **Accept:** datasheet section exists; site time-axis charts show the caveat.

### WS7-T4 · Downstream-user registry (P3, S)
Opt-in "Used by" README section + issue template — social proof and an early-warning channel for label misuse.
- **Accept:** template live; section present.

---

## Task count check (self-audit guard)

WS0: 6 · WS1: 6 · WS2: 5 · WS3: 6 · WS4: **9** · WS5: 6 · WS6: 8 · WS7: 4 → **50 tasks**. If you add or remove a task, update this line and the header in the same commit — this plan does not get to drift about its own contents.

*Change log for this line:* 49 (v1.1) → 50 on **2026-07-16**, adding **WS4-T9** (dead-ingest triage: AIRI Navigator + the silent-failure pattern), authorized by the maintainer. Header line updated in the same commit, per the rule above.

---

## Traceability — every review item → task

### Original 36 review items

| Review item | Task(s) |
|---|---|
| Garak/promptfoo counted as incidents; mixed corpus; headline stats | WS1-T1/T2/T3 |
| Scope drift (pre-LLM harms) | WS1-T4 |
| Heuristic labels, no validation, no κ, no confidence | WS2-T1/T2/T3 |
| 36% attack_vector "other" | WS2-T4 |
| Severity undefined; max-on-merge inflation | WS2-T5, WS3-T2 |
| Dedupe fragility, no error rate | WS4-T5 |
| ID tombstone rot / stability | WS3-T5 |
| CC-BY relicensing (AIAAIC BY-SA, AIID, OECD, verbatim vendor text) | WS0-T1/T3 |
| GitHub "Unknown license" | WS0-T2 |
| Verbatim payload foot-gun | WS3-T6 |
| Single maintainer / governance / dispute & takedown | WS5-T1/T2 |
| Vendor-blog curation bias & CoI | WS1-T6, WS5-T1 |
| Temporal completeness unmeasurable | WS7-T3 |
| No CPE/purl product identifiers | WS3-T3 |
| Mixed date granularity | WS3-T1 |
| MAESTRO status ambiguous | WS0-T5 |
| No positioning vs MIT AIRR / AVID; "single source of truth" | WS0-T5, WS7-T1 |
| INCIDENTS.md unusable at 12k | WS6-T6 |
| README/datasheet/release number drift; "four taxonomies" | WS6-T2, WS0-T5 |
| Keyword CVE sweep precision trap | WS4-T4 |
| No retraction/revision sync-back; upward accretion | WS4-T2 |
| Link rot, no archiving | WS4-T3 |
| Custom STIX SDO consumability; static "TAXII endpoint" | WS6-T3/T4, WS0-T5 |
| Refresh-PR supply chain, no threat model, no signing | WS4-T7/T8 |
| No evidence of use; ATLAS ground truth unused | WS7-T2, WS2-T1 |
| Tolerant parsers, tests miss live-format drift | WS4-T6 |
| Namespace squatting / neutrality | WS5-T4 |
| PyPI snapshot staleness; SemVer ambiguity; no fetch_latest | WS6-T1 |
| No rejects log / negative dataset / denominator | WS1-T5 |
| Conflicts silently erased on merge | WS3-T2 |
| Three-way structural split | WS1 (all) |
| Scraping ToS/robots.txt/permission unexamined | WS0-T4 |
| Reproducibility only downstream of network | WS4-T1 |
| Flat model; no campaigns/actors/relationships | WS3-T4 |
| Citation loop launders heuristics; credit to aggregator | WS0-T6, WS2 (all) |
| Three clocks in one date field | WS3-T1 |
| 5-digit ID cap | WS3-T5 |
| Pages endpoints: no SLA/signing/integrity | WS4-T8, WS6-T5 |
| 12k-row table accessibility/mobile | WS6-T5 |
| PII / GDPR exposure | WS5-T3 |

### v1.1 audit additions (plan-side defects → fixes)

| Audit defect | Fix location |
|---|---|
| Plan's own task count wrong ("~60" vs actual) | Header + task-count-check section (49, self-guarded) |
| Week-based calendar unrealistic; annotation study depended on later-phase recruitment | Phases section; WS5-T2 split into T2a (Phase 1) / T2b (Phase 4) |
| Arbitrary acceptance numbers (90% CPE, ≥150 pkgs, ≥200 edges, <15% other) | WS3-T3, WS4-T4, WS3-T4, WS2-T4 rewritten baseline-first |
| Invariants referenced infrastructure not yet built | Staged invariants table with Active-from column |
| Wayback ≥95% gate vs SPN2 rate limits | WS4-T3 acceptance rewritten (queue + metric, not gate) |
| Rejects log republishes prohibited/PII content | WS1-T5 identifiers-only rule |
| Model-assisted summaries break build determinism | WS0-T3 committed source-of-record rule |
| Zenodo/DOI redeposit unowned | WS6-T7 (new) |
| CONTRIBUTING.md invalidated by restructure, unowned | WS5-T5 (new) |
| v3.0 consumer migration guide unowned | WS6-T8 (new) |
| No AI-assisted-change policy | WS5-T6 (new) |
| WS0-T3 had no phase assignment | Phase 1 exit criteria amended (scoped fold) |
| A live ingest's source 404s and fails silently every refresh; no test caught it | WS4-T9 (new, Phase 1) — count 49 → 50 |

*Definition of done for the whole plan: nothing the repo says about itself is false; every label has a measured or declared error bar; every byte of data has a documented right to be there; and the project survives you taking a month off.*
