"""
Render data/incidents.json -> INCIDENTS.md (human-readable SoT).

Layout:
  - Header with metadata + taxonomy summary
  - Sortable table grouped by year, descending
  - Per-incident detail blocks linked from the table
"""

from __future__ import annotations

import json
from pathlib import Path
from collections import Counter, defaultdict
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "INCIDENTS.md"


def md_escape(s: str) -> str:
    return (s or "").replace("|", "\\|").replace("\n", " ").strip()


def render():
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    entries = raw["incidents"]

    by_year = defaultdict(list)
    for e in entries:
        by_year[e["year"]].append(e)

    llm_counts = Counter()
    asi_counts = Counter()
    atlas_counts = Counter()
    sev_counts = Counter()
    for e in entries:
        for c in e.get("owasp_llm", []):
            llm_counts[c] += 1
        for c in e.get("owasp_asi", []):
            asi_counts[c] += 1
        for c in e.get("mitre_atlas", []):
            atlas_counts[c] += 1
        sev_counts[e.get("severity", "Medium")] += 1

    lines: list[str] = []
    lines.append("# GenAI & Agentic AI Security Incidents")
    lines.append("")
    lines.append(f"Single source of truth for GenAI and agentic AI security incidents.")
    lines.append(f"Each entry is mapped to **OWASP LLM Top 10 (2025)**, **OWASP Agentic Top 10 (ASI)**, **NIST AI RMF**, and **MITRE ATLAS**.")
    lines.append("")
    lines.append(f"- **Version:** {raw.get('version','1.0.0')}")
    lines.append(f"- **Generated:** {raw.get('generated', str(date.today()))}")
    lines.append(f"- **Total incidents:** **{len(entries)}**")
    lines.append(f"- **Machine-readable:** [`data/incidents.json`](data/incidents.json) · [`data/incidents.min.json`](data/incidents.min.json)")
    lines.append(f"- **Schema:** [`schema/incident.schema.json`](schema/incident.schema.json)")
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.append("### Severity")
    lines.append("")
    lines.append("| Severity | Count |")
    lines.append("|---|---:|")
    for s in ["Critical", "High", "Medium", "Low", "Info"]:
        if sev_counts.get(s):
            lines.append(f"| {s} | {sev_counts[s]} |")
    lines.append("")
    lines.append("### OWASP LLM Top 10 (2025)")
    lines.append("")
    lines.append("| Code | Name | Count |")
    lines.append("|---|---|---:|")
    llm_names = {
        "LLM01":"Prompt Injection","LLM02":"Sensitive Information Disclosure",
        "LLM03":"Supply Chain","LLM04":"Data and Model Poisoning",
        "LLM05":"Improper Output Handling","LLM06":"Excessive Agency",
        "LLM07":"System Prompt Leakage","LLM08":"Vector and Embedding Weaknesses",
        "LLM09":"Misinformation","LLM10":"Unbounded Consumption",
    }
    for code, name in llm_names.items():
        lines.append(f"| {code} | {name} | {llm_counts.get(code,0)} |")
    lines.append("")
    lines.append("### OWASP Agentic Top 10 (ASI)")
    lines.append("")
    lines.append("| Code | Name | Count |")
    lines.append("|---|---|---:|")
    asi_names = {
        "ASI01":"Agent Goal Hijack","ASI02":"Tool Misuse & Exploitation",
        "ASI03":"Identity & Privilege Abuse","ASI04":"Agentic Supply Chain Vulnerabilities",
        "ASI05":"Unexpected Code Execution (RCE)","ASI06":"Memory & Context Poisoning",
        "ASI07":"Insecure Inter-Agent Communication","ASI08":"Cascading Failures",
        "ASI09":"Human-Agent Trust Exploitation","ASI10":"Rogue Agents",
    }
    for code, name in asi_names.items():
        lines.append(f"| {code} | {name} | {asi_counts.get(code,0)} |")
    lines.append("")
    lines.append("### Top MITRE ATLAS Techniques")
    lines.append("")
    lines.append("| Technique | Count |")
    lines.append("|---|---:|")
    for tech, count in atlas_counts.most_common(15):
        lines.append(f"| `{tech}` | {count} |")
    lines.append("")

    lines.append("## Index by Year")
    lines.append("")
    lines.append("Click an incident ID to jump to its detail block. Detail blocks are below the index.")
    lines.append("")

    for year in sorted(by_year.keys(), reverse=True):
        rows = by_year[year]
        lines.append(f"### {year} — {len(rows)} incidents")
        lines.append("")
        lines.append("| ID | Date | Title | Severity | OWASP LLM | OWASP ASI |")
        lines.append("|---|---|---|---|---|---|")
        for e in sorted(rows, key=lambda x: x.get("date") or ""):
            llm = ", ".join(e.get("owasp_llm", []))
            asi = ", ".join(e.get("owasp_asi", []))
            lines.append(
                f"| [`{e['id']}`](#{e['id'].lower()}) "
                f"| {md_escape(e.get('date',''))} "
                f"| {md_escape(e['title'])} "
                f"| {md_escape(e.get('severity',''))} "
                f"| {llm} | {asi} |"
            )
        lines.append("")

    lines.append("## Incident Details")
    lines.append("")

    for year in sorted(by_year.keys(), reverse=True):
        for e in sorted(by_year[year], key=lambda x: x.get("date") or ""):
            lines.append(f"### {e['id']}")
            lines.append("")
            lines.append(f"**{e['title']}**  ")
            lines.append(f"_{e.get('date','')} · {e.get('category','')} · Severity: {e.get('severity','')}_")
            if e.get("cve_ids"):
                lines.append("")
                lines.append("CVEs: " + ", ".join(f"`{c}`" for c in e["cve_ids"]))
            if e.get("cvss_score") is not None:
                lines.append(f"CVSS: **{e['cvss_score']}**")
            lines.append("")
            lines.append(e.get("description", ""))
            lines.append("")
            if e.get("affected"):
                lines.append(f"**Affected:** {e['affected']}  ")
            if e.get("attack_vector"):
                lines.append(f"**Attack vector:** `{e['attack_vector']}`  ")
            if e.get("impact"):
                lines.append(f"**Impact:** {e['impact']}  ")
            lines.append("")
            if e.get("owasp_llm"):
                lines.append(f"**OWASP LLM Top 10:** {', '.join(f'`{c}`' for c in e['owasp_llm'])}  ")
            if e.get("owasp_asi"):
                lines.append(f"**OWASP Agentic (ASI):** {', '.join(f'`{c}`' for c in e['owasp_asi'])}  ")
            if e.get("nist_ai_rmf"):
                lines.append(f"**NIST AI RMF:** {', '.join(f'`{c}`' for c in e['nist_ai_rmf'])}  ")
            if e.get("mitre_atlas"):
                lines.append(f"**MITRE ATLAS:** {', '.join(f'`{c}`' for c in e['mitre_atlas'])}  ")
            if e.get("maestro_layers"):
                ml = ", ".join(f"`{l['layer']} {l.get('label','')}`" for l in e["maestro_layers"])
                lines.append(f"**MAESTRO layers:** {ml}  ")
            lines.append("")
            if e.get("mitigations"):
                lines.append("**Mitigations:**")
                for m in e["mitigations"]:
                    lines.append(f"- {m}")
                lines.append("")
            if e.get("references"):
                lines.append("**References:**")
                for r in e["references"]:
                    title = r.get("title") or r["url"]
                    lines.append(f"- [{title}]({r['url']})" + (f" _({r.get('type')})_" if r.get('type') else ""))
                lines.append("")
            if e.get("tags"):
                lines.append("**Tags:** " + ", ".join(f"`{t}`" for t in e["tags"]))
                lines.append("")
            lines.append("---")
            lines.append("")

    lines.append("")
    lines.append("> Generated by `scripts/render_markdown.py`. Do not edit by hand — edit the source JSON instead.")

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(entries)} incidents, {sum(len(l) for l in lines):,} chars)")


if __name__ == "__main__":
    render()
