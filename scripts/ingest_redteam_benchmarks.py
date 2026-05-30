"""
Curated catalogue of public red-team / safety benchmarks for LLMs and agents.

These are *research-demonstrated* attack corpora — the academic counterpart to
the garak / promptfoo probe catalogues already ingested. Each entry documents
a benchmark, the attack class it exercises, and its canonical paper/repo, mapped
to OWASP/ATLAS so it sits alongside real-world incidents.

Output: ingest/redteam_benchmarks.json  (picked up by merge_and_dedupe.py).

This is a hand-curated, citation-backed list (no scraping); add benchmarks by
appending to BENCHMARKS.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"

# (slug, year, title, attack_vector, owasp_llm, owasp_asi, mitre_atlas,
#  description, [(ref_title, url, type), ...])
BENCHMARKS = [
    ("jailbreakbench", 2024, "JailbreakBench: open robustness benchmark for LLM jailbreaking",
     "jailbreak", ["LLM01"], [], ["AML.T0054"],
     "JBB-Behaviors: 100 misuse behaviours across 10 OpenAI-policy categories "
     "(harassment, malware, physical/economic harm, fraud, disinformation, sexual "
     "content, privacy, expert/government advice) plus an evolving set of jailbreak "
     "artifacts. NeurIPS 2024 Datasets & Benchmarks.",
     [("JailbreakBench", "https://jailbreakbench.github.io/", "research"),
      ("Paper (NeurIPS 2024)", "https://arxiv.org/abs/2404.01318", "paper")]),
    ("harmbench", 2024, "HarmBench: standardized evaluation for automated red-teaming",
     "jailbreak", ["LLM01"], [], ["AML.T0054"],
     "~400 harmful behaviours (incl. contextual and multimodal) for automated "
     "red-teaming and robust-refusal evaluation across 18 attack methods. ICML 2024.",
     [("HarmBench", "https://www.harmbench.org/", "research"),
      ("Paper (ICML 2024)", "https://arxiv.org/abs/2402.04249", "paper")]),
    ("advbench", 2023, "AdvBench: harmful behaviours & strings (GCG adversarial suffixes)",
     "jailbreak", ["LLM01"], [], ["AML.T0054", "AML.T0043"],
     "Harmful-behaviour and harmful-string sets introduced with the Greedy "
     "Coordinate Gradient (GCG) universal adversarial-suffix attack on aligned LLMs.",
     [("Paper — Universal and Transferable Adversarial Attacks", "https://arxiv.org/abs/2307.15043", "paper"),
      ("llm-attacks repo", "https://github.com/llm-attacks/llm-attacks", "research")]),
    ("agentharm", 2025, "AgentHarm: harmfulness benchmark for tool-calling LLM agents",
     "agent-hijack", ["LLM06"], ["ASI08"], ["AML.T0053"],
     "110 malicious agent tasks across 11 harm categories (fraud, cybercrime, "
     "harassment, drugs, etc.) with rule-based scoring; measures whether agents "
     "complete harmful multi-step tool-use, incl. under jailbreak templates. ICLR 2025.",
     [("Paper (ICLR 2025)", "https://arxiv.org/abs/2410.09024", "paper")]),
    ("agentdojo", 2024, "AgentDojo: prompt-injection attacks & defenses for LLM agents",
     "indirect-prompt-injection", ["LLM01"], ["ASI01"], ["AML.T0051.001"],
     "Dynamic environment of realistic agent tasks (banking, Slack, travel, "
     "workspace) where harm arises from prompt injections planted in tool outputs; "
     "evaluates attacks and defenses. NeurIPS 2024 Datasets & Benchmarks.",
     [("Paper (NeurIPS 2024)", "https://arxiv.org/abs/2406.13352", "paper"),
      ("AgentDojo repo", "https://github.com/ethz-spylab/agentdojo", "research")]),
    ("injecagent", 2024, "InjecAgent: indirect prompt-injection benchmark for tool-integrated agents",
     "indirect-prompt-injection", ["LLM01"], ["ASI01"], ["AML.T0051.001"],
     "1,054 test cases probing tool-integrated LLM agents for susceptibility to "
     "indirect prompt injection (direct harm + data exfiltration intents).",
     [("Paper", "https://arxiv.org/abs/2403.02691", "paper")]),
    ("os-harm", 2025, "OS-Harm: safety benchmark for computer-use agents",
     "agent-hijack", ["LLM06"], ["ASI08"], ["AML.T0053"],
     "Benchmark for computer-use / GUI agents covering deliberate misuse, prompt "
     "injection, and model misbehaviour on real OS tasks, with an automated judge.",
     [("Paper", "https://arxiv.org/abs/2506.14866", "paper")]),
    ("hackaprompt", 2023, "HackAPrompt: global prompt-injection/jailbreak competition dataset",
     "prompt-injection", ["LLM01"], [], ["AML.T0051"],
     "~600k adversarial prompts crowdsourced from a global prompt-hacking "
     "competition; a large real-world corpus of human jailbreak/injection attempts. EMNLP 2023.",
     [("Paper (EMNLP 2023)", "https://arxiv.org/abs/2311.16119", "paper")]),
    ("strongreject", 2024, "StrongREJECT: high-quality jailbreak evaluation benchmark",
     "jailbreak", ["LLM01"], [], ["AML.T0054"],
     "Forbidden-prompt set plus an autograder that measures how useful a jailbroken "
     "response actually is, correcting over-estimation by prior jailbreak metrics. NeurIPS 2024.",
     [("Paper", "https://arxiv.org/abs/2402.10260", "paper")]),
    ("safetyprompts", 2024, "SafetyPrompts.com: open catalogue of LLM safety datasets",
     "other", ["LLM01"], [], [],
     "A living, curated index of 100+ open datasets for LLM safety evaluation "
     "(jailbreaks, toxicity, bias, value alignment) — a meta-source for red-team corpora.",
     [("SafetyPrompts.com", "https://safetyprompts.com/", "research"),
      ("Paper", "https://arxiv.org/abs/2404.05399", "paper")]),
]


def build() -> list[dict]:
    out = []
    for slug, year, title, av, llm, asi, atlas, desc, refs in BENCHMARKS:
        out.append({
            "source_id": f"REDTEAM-{slug}",
            "title": title,
            "date": str(year),
            "year": year,
            "category": "red-team",
            "description": desc,
            "attack_vector": av,
            "affected": "LLM / agent evaluation surface",
            "severity": "Medium",
            "owasp_llm": llm,
            "owasp_asi": asi,
            "mitre_atlas": atlas,
            "references": [{"title": t, "url": u, "type": ty} for (t, u, ty) in refs],
            "tags": ["red-team", "benchmark", "research-demonstrated", slug],
        })
    return out


def main() -> None:
    records = build()
    INGEST.mkdir(parents=True, exist_ok=True)
    (INGEST / "redteam_benchmarks.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"[redteam] wrote {len(records)} benchmark entries -> ingest/redteam_benchmarks.json")


if __name__ == "__main__":
    main()
