# E5 / WS1-T4 — measured corpus composition

**Do not regenerate.** Dated measurement, 2026-07-31, against `main` @ `62bc5a7e`.

**Why this exists:** the user named the **E5 / WS1-T4 scope decision** (rename
the dataset vs `ai_system_type` tagging; the plan recommends tagging) as the
opening act of Phase 2, **to come to them with measured corpus composition**.
This supplies that measurement so the decision is not taken on impressions.
**It takes no position on the decision.**

## The headline split

| | count | share |
|---|---:|---:|
| Corpus | **13,060** | |
| `corpus: security` | **12,519** | **95.9%** |
| `corpus: ai-harm` | **541** | **4.1%** |

**This is the fact the decision turns on.** The project is named for *GenAI &
Agentic AI Security Incidents*, and by its own classifier **96% of what it holds
is security**. The AI-harm population is real but small.

## Vulnerability-shaped vs incident-shaped

| | count |
|---|---:|
| Rows carrying `cve_ids` | **5,279** |
| Rows with no CVE | **7,781** |

**Roughly 40% of the corpus is CVE-bearing.** WS1-T1's premise — that
*incidents*, *vulnerabilities* and *capabilities* are different things sharing
one table — is measurable here rather than argued: a CVE advisory and a
deployed-system harm report are not the same kind of object, and invariant 1
(*never headline-count them as one number*) exists because of it.

## Source families (by `source_id` prefix; rows may carry several)

| Family | rows |
|---|---:|
| CVE | 6,986 |
| OECD | 4,160 |
| AIID | 1,552 |
| GHSA | 1,018 |
| PROMPTFOO | 174 |
| RES | 133 |
| ARXIV | 116 |
| INC | 113 |
| AVID | 109 |
| LEGACY | 108 |
| AIAAIC | 95 |
| VTR | 82 |
| ATLAS | 70 |
| EXT | 48 |

**CVE + GHSA = 8,004 source references** — the vulnerability feeds dominate by
volume. **PROMPTFOO (174) and ATLAS (70)** are the populations WS1-T2 proposes
moving out of *incidents* entirely: promptfoo plugins are **capabilities**
(test coverage), not events that happened.

## Tier

| | count |
|---|---:|
| `landmark` | **1,905** |
| `feed` | **11,155** |

## What this does and does not establish

- **Establishes:** the corpus is overwhelmingly security-classified and
  substantially CVE-derived; the non-incident populations WS1-T2 targets are
  small and countable.
- **Does not establish:** whether the right remedy is a **rename** or
  **`ai_system_type` tagging**. That is E5, and it is the user's call. The
  numbers bear on it — a 96/4 split is an argument for one framing, and 4.1%
  being 541 real harm records is an argument against discarding the other —
  **but they do not decide it.**
- **Caveat on `corpus`:** this field is assigned by keyword classifiers
  (`merge_and_dedupe.py`'s `_SECURITY_KEYWORDS_FOR_CORPUS` /
  `_AI_HARM_KEYWORDS`), not by human review. **It is a heuristic label**, and
  WS2 is the workstream that would establish how good it is. Treat 95.9/4.1 as
  the classifier's opinion, not as ground truth.
