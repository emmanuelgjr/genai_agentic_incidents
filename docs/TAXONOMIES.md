# Taxonomies

This dataset maps each incident to four (sometimes five) taxonomies. They don't compete — they describe **different facets** of the same incident.

## Quick chooser

| Question | Use |
|---|---|
| What kind of failure is this at the LLM layer? | **OWASP LLM Top 10** |
| What kind of failure is this at the agent layer? | **OWASP Agentic Top 10 (ASI)** |
| What organizational risk function should respond? | **NIST AI RMF** |
| What adversary tactic/technique was used? | **MITRE ATLAS** |
| Where in the architecture did it originate / impact? | **MAESTRO** (companion) |
| Does response get paged or queued — could the closing action be undone? | **Reversibility class** (landmark tier) |

---

## OWASP Top 10 for LLM Applications (2025)

Source: <https://genai.owasp.org/llm-top-10/>

Failure-mode catalog focused on LLM-based applications regardless of agency.

| Code | Name |
|---|---|
| LLM01 | Prompt Injection |
| LLM02 | Sensitive Information Disclosure |
| LLM03 | Supply Chain |
| LLM04 | Data and Model Poisoning |
| LLM05 | Improper Output Handling |
| LLM06 | Excessive Agency |
| LLM07 | System Prompt Leakage |
| LLM08 | Vector and Embedding Weaknesses |
| LLM09 | Misinformation |
| LLM10 | Unbounded Consumption |

**Use it when:** the incident involves an LLM API, RAG system, or LLM-backed feature — even if the system has no agent loop.

---

## OWASP Agentic Top 10 (ASI)

Source: <https://genai.owasp.org/resource/agentic-ai-threats-and-mitigations/>

Failure-mode catalog focused on **agentic** systems — agents with planning loops, tool use, memory, and inter-agent communication.

| Code | Name |
|---|---|
| ASI01 | Agent Goal Hijack |
| ASI02 | Tool Misuse & Exploitation |
| ASI03 | Identity & Privilege Abuse |
| ASI04 | Agentic Supply Chain Vulnerabilities |
| ASI05 | Unexpected Code Execution (RCE) |
| ASI06 | Memory & Context Poisoning |
| ASI07 | Insecure Inter-Agent Communication |
| ASI08 | Cascading Failures |
| ASI09 | Human-Agent Trust Exploitation |
| ASI10 | Rogue Agents |

**Use it when:** the system exhibits agentic properties — tool invocation, autonomous planning, memory, or multi-agent orchestration. Don't force-fit ASI codes onto purely-LLM incidents.

---

## NIST AI Risk Management Framework (AI 100-1)

Source: <https://www.nist.gov/itl/ai-risk-management-framework>

Risk-management framework, not a failure catalog. Four functions:

| Function | Description |
|---|---|
| GOVERN | A culture of risk management is cultivated and present |
| MAP | Context and risks related to context are identified |
| MEASURE | Risks are assessed, analyzed, or tracked |
| MANAGE | Risks are prioritized and acted upon |

Each function has subcategories with stable identifiers (e.g., `MEASURE-2.7` "AI system security and resilience are evaluated and documented").

**Use it when:** you want to surface **which control area should have caught or contained** the incident. For an indirect prompt injection that exfiltrates data: `MEASURE-2.7` (security testing missed this), `MAP-2.1` (the deployment context wasn't well-understood), `MANAGE-2.3` (no incident-response procedure).

A companion **AI 600-1 Generative AI Profile** maps GenAI-specific risks to the same subcategory IDs — see <https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.600-1.pdf>.

---

## MITRE ATLAS

Source: <https://atlas.mitre.org/>

Adversary-centric taxonomy of tactics and techniques against ML/AI systems, modeled after MITRE ATT&CK. Tactics use `AML.TA00xx` IDs; techniques use `AML.T00xx` (with optional `.NNN` subtechnique suffix).

Key LLM-era techniques used heavily in this dataset:

| Technique | Name |
|---|---|
| `AML.T0010` | ML Supply Chain Compromise |
| `AML.T0018` | Backdoor ML Model |
| `AML.T0020` | Poison Training Data |
| `AML.T0024` | Exfiltration via ML Inference API |
| `AML.T0048` | External Harms |
| `AML.T0051` | LLM Prompt Injection (`.000` Direct, `.001` Indirect) |
| `AML.T0053` | LLM Plugin Compromise |
| `AML.T0054` | LLM Jailbreak |
| `AML.T0056` | Extract LLM System Prompt |
| `AML.T0057` | LLM Data Leakage |
| `AML.T0066` | RAG Poisoning |

**Use it when:** you want to communicate the incident in adversarial-emulation terms — what an attacker is **doing**, not what is **broken**.

See `mappings/mitre_atlas.json` for the full technique list used here.

---

## MAESTRO architectural layers (companion)

Source: <https://genai.owasp.org/resource/genai-security-project-maestro/>

Companion model that describes **where in the AI/agent architecture** an incident originates, impacts, or could be controlled. Used by the legacy `incidents.json` source and preserved on those entries.

| Layer | Name |
|---|---|
| L1 | Foundation Models |
| L2 | Data Operations |
| L3 | Agent Frameworks & Tooling |
| L4 | Deployment & Infrastructure |
| L5 | Evaluation & Observability |
| L6 | Security & Compliance |
| L7 | Human Factors & UX |

The `role` field on a MAESTRO mapping indicates whether the layer was the `origin`, `impact`, `blind-spot`, `control`, `amplifier`, or `propagation` vector.

---

## Reversibility class

Proposed in [#74](https://github.com/emmanuelgjr/genai_incidents/issues/74) (lineage: OWASP AISVS C09-02 reversibility-classification gating). Severity says how bad; `reversibility_class` says whether incident response gets **paged or queued** — the same attack vector routes very differently depending on what the closing action could undo.

Four **ordered** classes, least → most severe:

| Rank | Class | Meaning |
|---|---|---|
| 1 | `read-only` | No state mutation — the agent observed, read, summarized, or inferred but did not act on external systems. |
| 2 | `reversible` | Mutation undoable in-session or by trivial in-system action (file recoverable from trash, internal-only draft). |
| 3 | `external-reversible` | Mutation undoable only via an external compensating action (refund, retraction, correction outreach, manual cleanup). |
| 4 | `irreversible` | No compensating action possible (unrecoverable deletion, funds transferred, content published and indexed). |

Scope rules (precision-over-coverage):
- **Landmark tier only** — enforced as a `validate.py` integrity invariant. `tier` is re-derived each build, so a labeled entry drifting out of the landmark set fails CI rather than shipping a stale judgment.
- **Evidence-gated** — assigned via `data/curation_overrides.json` only where the source evidence describes the closing action, with evidence and review date in the override `_note`. Feed/auto entries stay empty rather than guessing.
- **Absence means unassessed, not `read-only`.**
- The JSON-schema enum carries no order — consumers must rank explicitly (alphabetical sorting puts `irreversible` between the two reversible classes).

---

## VERIS crosswalk (export-only)

Source: <https://github.com/vz-risk/veris> (VERIS 1.4.1 — the incident vocabulary behind the Verizon DBIR and VCDB)

Not a per-incident schema field: a hand-curated crosswalk in [`mappings/veris.json`](../mappings/veris.json) from the controlled `attack_vector` vocabulary to VERIS enum paths, emitted as `veris:*` machinetags in the MISP feed (`scripts/export_misp.py`). Anchored on VERIS 1.4.1's GenAI enums (`action.hacking.variety` "Prompt injection", asset "S - LLM application"). It makes incidents legible to DBIR-contributor and risk-quantification consumers without adding schema surface.

Curation rules: closest defensible enum only — values with no honest VERIS equivalent (`algorithmic-bias`, `other`) stay unmapped; the LLM-application asset tag is attached only to vectors that by definition target an LLM/agent app. Deliberately **not** derived by chaining ATLAS→ATT&CK→VERIS: only ~20% of ATLAS techniques have ATT&CK anchors, and none of the AI-native ones do.

**Use it when:** consuming the MISP feed alongside VERIS-coded corpora (DBIR, VCDB) or FAIR-style risk tooling. Note MISP's bundled `veris` taxonomy predates VERIS 1.4.1, so the AI-specific tags render as plain tags until upstream refreshes it.

---

## How they map to each other

The frameworks overlap deliberately. A single incident often hits **several** codes across taxonomies. Example: ShadowLeak (zero-click ChatGPT Deep Research data exfiltration).

| Taxonomy | Mapping for ShadowLeak |
|---|---|
| OWASP LLM | `LLM01` (indirect prompt injection), `LLM02` (sensitive info disclosure), `LLM06` (excessive agency through connectors) |
| OWASP ASI | `ASI01` (goal hijack), `ASI02` (tool misuse — connectors), `ASI09` (human-agent trust exploitation) |
| NIST AI RMF | `MEASURE-2.7` (security testing gap), `MAP-3.5` (human oversight), `GOVERN-6.1` (third-party connector risk) |
| MITRE ATLAS | `AML.T0051.001` (LLM Prompt Injection — indirect), `AML.T0057` (LLM Data Leakage), `AML.T0048` (External Harms) |
| MAESTRO | `L3` origin (connectors), `L5` blind-spot (no telemetry to catch this), `L6` impact (compliance/data) |

Don't pick favorites. Use them together.
