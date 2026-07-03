"""
Ingest from external GitHub repos cloned under ../_external/.

Produces, into ingest/:
  atlas_full.json             ← all MITRE ATLAS case studies (YAML -> JSON)
  cset_harm_taxonomy.json     ← CSET harm taxonomy (controlled vocabulary; not incidents)
  garak_probes.json           ← one entry per garak probe (canonical attack classes)
  promptfoo_plugins.json      ← one entry per promptfoo red-team plugin
  cve_ai_curated.json         ← ModelOriented/CVE-AI curated list
  aiid_oecd_relationships.json ← AIID<->OECD bridge entries (one per OECD link)

Each output entry uses the tolerant `ingest` shape — `scripts/merge_and_dedupe.py`
normalizes them into the canonical incident schema.
"""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import date

EXTERNAL = Path(__file__).resolve().parents[2] / "_external"
INGEST = Path(__file__).resolve().parents[1] / "ingest"
INGEST.mkdir(parents=True, exist_ok=True)


def safe_yaml_load(text: str) -> dict:
    """Parse ATLAS YAML files. PyYAML is listed in requirements.txt."""
    try:
        import yaml
    except ImportError as exc:
        raise SystemExit(
            "PyYAML is required for ingest_external.py. "
            "Run `pip install -r requirements.txt`."
        ) from exc
    return yaml.safe_load(text)


# ---------------------------------------------------------------------------
# 1) MITRE ATLAS full corpus
# ---------------------------------------------------------------------------
ATLAS_TECH_TO_LLM = {
    "AML.T0051": ["LLM01"], "AML.T0051.000": ["LLM01"], "AML.T0051.001": ["LLM01"],
    "AML.T0054": ["LLM01"], "AML.T0057": ["LLM02"], "AML.T0056": ["LLM07"],
    "AML.T0010": ["LLM03"], "AML.T0010.001": ["LLM03"], "AML.T0010.002": ["LLM03"],
    "AML.T0010.003": ["LLM03"], "AML.T0018": ["LLM04"], "AML.T0019": ["LLM04"],
    "AML.T0020": ["LLM04"], "AML.T0050": ["LLM05"], "AML.T0060": ["LLM05"],
    "AML.T0053": ["LLM06"], "AML.T0048": ["LLM06"], "AML.T0066": ["LLM08"],
    "AML.T0070": ["LLM08"], "AML.T0058": ["LLM09"], "AML.T0029": ["LLM10"],
    "AML.T0034": ["LLM10"], "AML.T0046": ["LLM10"],
}

ATLAS_TECH_TO_ASI = {
    "AML.T0051": ["ASI01"], "AML.T0051.000": ["ASI01"], "AML.T0051.001": ["ASI01"],
    "AML.T0053": ["ASI02"], "AML.T0050": ["ASI05"], "AML.T0012": ["ASI03"],
    "AML.T0055": ["ASI03"], "AML.T0010": ["ASI04"], "AML.T0010.001": ["ASI04"],
    "AML.T0066": ["ASI06"], "AML.T0020": ["ASI06"], "AML.T0048": ["ASI09"],
    "AML.T0048.003": ["ASI09"], "AML.T0011": ["ASI05"], "AML.T0011.000": ["ASI05"],
    "AML.T0049": ["ASI05"], "AML.T0060": ["ASI06"], "AML.T0024": ["ASI03"],
}


# Pinned ATLAS release parsed by ingest_atlas(). Upstream retired the
# per-object data/ tree and froze dist/ATLAS.yaml at 5.6.0; the versioned
# v6 dist files are the maintained, reproducible source.
ATLAS_DIST = ("dist", "v6", "ATLAS-2026.06.yaml")


def ingest_atlas() -> int:
    dist = EXTERNAL / "atlas-data"
    for part in ATLAS_DIST:
        dist = dist / part
    if not dist.exists():
        print(f"[atlas] {'/'.join(ATLAS_DIST)} missing — skipping")
        return 0
    try:
        root = safe_yaml_load(dist.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: failed to parse {dist.name}: {e}")
        return 0
    if not isinstance(root, dict):
        return 0
    relationships = root.get("relationships") or {}
    out = []

    for cs_id, cs in sorted((root.get("case-studies") or {}).items()):
        if not isinstance(cs, dict):
            continue

        title = (cs.get("name") or "").strip()
        summary = (cs.get("description") or "").strip()
        if not title or not summary:
            continue

        inc_date = cs.get("date")
        year = None
        date_str = ""
        if inc_date:
            date_str = str(inc_date)
            m = re.match(r"(\d{4})", date_str)
            if m:
                year = int(m.group(1))
        if not year:
            # Look for year in summary or use case-study filing year
            m = re.search(r"\b(20[1-2]\d)\b", summary)
            if m:
                year = int(m.group(1))
        if not year:
            year = 2020  # placeholder; ATLAS publishes pre-LLM cases too

        # Technique/tactic IDs arrive fully resolved in the dist file's
        # `employs` relationships (the old data/ tree needed jinja handles)
        atlas_tech = set()
        atlas_tactics = set()
        for step in (relationships.get(cs_id) or {}).get("employs") or []:
            t = step.get("target") or ""
            if t.startswith("AML.T") and not t.startswith("AML.TA"):
                atlas_tech.add(t)
            tactic = step.get("tactic") or ""
            if tactic.startswith("AML.TA"):
                atlas_tactics.add(tactic)

        # Derive OWASP codes from techniques
        llm = set()
        asi = set()
        for t in atlas_tech:
            for c in ATLAS_TECH_TO_LLM.get(t, []):
                llm.add(c)
            for c in ATLAS_TECH_TO_ASI.get(t, []):
                asi.add(c)

        # Determine category (v6 `type` is "Incident" or "Exercise")
        cat = str(cs.get("type") or "incident").lower()
        category = "real-world" if cat == "incident" else "research"

        refs = []
        for r in cs.get("references") or []:
            url = r.get("url") if isinstance(r, dict) else None
            title_ref = r.get("title") if isinstance(r, dict) else None
            if url:
                refs.append({"title": title_ref or "MITRE ATLAS reference", "url": url, "type": "research"})
        # Always include canonical ATLAS URL
        refs.insert(0, {
            "title": f"MITRE ATLAS — {cs_id}",
            "url": f"https://atlas.mitre.org/studies/{cs_id}",
            "type": "research",
        })

        # Derive severity
        severity = "High"
        s_lower = summary.lower()
        if any(k in s_lower for k in ["critical", "ransomware", "rce", "remote code execution", "$1 billion", "millions of"]):
            severity = "Critical"

        entry = {
            "source_id": f"ATLAS-{cs_id}",
            "title": title,
            "date": date_str if date_str else str(year),
            "year": year,
            "category": category,
            "description": summary[:2000],
            "attack_vector": "adversarial-input",  # default; ATLAS-specific
            "affected": cs.get("target", "") or cs.get("actor", "") or "",
            "severity": severity,
            "owasp_llm": sorted(llm),
            "owasp_asi": sorted(asi),
            "mitre_atlas": sorted(atlas_tech),
            "mitre_atlas_tactics": sorted(atlas_tactics),
            "references": refs,
            "tags": ["atlas", "case-study", category],
        }
        # Better attack-vector
        if any(t.startswith("AML.T0051") for t in atlas_tech):
            entry["attack_vector"] = "prompt-injection"
        elif "AML.T0054" in atlas_tech:
            entry["attack_vector"] = "jailbreak"
        elif "AML.T0010" in atlas_tech or "AML.T0010.001" in atlas_tech:
            entry["attack_vector"] = "supply-chain"
        elif "AML.T0050" in atlas_tech:
            entry["attack_vector"] = "rce"
        elif "AML.T0066" in atlas_tech:
            entry["attack_vector"] = "memory-poisoning"
        elif "AML.T0018" in atlas_tech or "AML.T0020" in atlas_tech:
            entry["attack_vector"] = "model-poisoning"
        elif "AML.T0024" in atlas_tech:
            entry["attack_vector"] = "data-exfiltration"
        elif "AML.T0043" in atlas_tech or any(t.startswith("AML.T0043") for t in atlas_tech):
            entry["attack_vector"] = "adversarial-input"

        out.append(entry)

    (INGEST / "atlas_full.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[atlas]  wrote {len(out)} case studies -> ingest/atlas_full.json")
    return len(out)


# ---------------------------------------------------------------------------
# 2) AIID<->OECD relationships
# ---------------------------------------------------------------------------
def ingest_aiid_oecd_bridge() -> int:
    src = EXTERNAL / "aiid" / "site" / "gatsby-site" / "migrations" / "data" / "oecd_relationships_2025_09_09.json"
    if not src.exists():
        print("[aiid-oecd] mapping file missing — skipping")
        return 0
    data = json.loads(src.read_text(encoding="utf-8"))
    seen = set()
    out = []
    for row in data:
        aiid_id = row.get("incident_id")
        oecd_url = row.get("sameAs")
        if not aiid_id or not oecd_url:
            continue
        key = (aiid_id, oecd_url)
        if key in seen:
            continue
        seen.add(key)
        # OECD URL pattern: https://oecd.ai/en/incidents/2022-01-10-5735
        m = re.search(r"/(\d{4})-(\d{2})-(\d{2})-[0-9a-f]+", oecd_url)
        if not m:
            continue
        y, mo, d_ = m.groups()
        # Build a placeholder entry; merger will dedupe against AIID entries that have descriptions
        out.append({
            "source_id": f"AIID-{aiid_id}-OECD",
            "title": f"AIID incident #{aiid_id} (OECD-tracked)",
            "date": f"{y}-{mo}",
            "year": int(y),
            "category": "real-world",
            "description": (
                f"Cross-listed in the AI Incident Database (AIID) as incident #{aiid_id} and tracked by the "
                f"OECD AI Incidents Monitor. See the linked entries for full context, victims, references, "
                f"and harm classification."
            ),
            "attack_vector": "other",
            "affected": "",
            "severity": "Medium",
            "references": [
                {"title": f"AIID #{aiid_id}", "url": f"https://incidentdatabase.ai/cite/{aiid_id}/", "type": "report"},
                {"title": "OECD AI Incidents Monitor entry", "url": oecd_url, "type": "report"},
            ],
            "tags": ["aiid", "oecd", "cross-listed"],
        })
    (INGEST / "aiid_oecd_relationships.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[aiid-oecd]  wrote {len(out)} relationships -> ingest/aiid_oecd_relationships.json")
    return len(out)


# ---------------------------------------------------------------------------
# 3) CSET-AIID harm taxonomy (controlled vocabulary, not incidents per se)
# ---------------------------------------------------------------------------
def ingest_cset() -> int:
    cset = EXTERNAL / "CSET-AIID-harm-taxonomy"
    if not cset.exists():
        print("[cset] repo missing — skipping")
        return 0
    # CSET publishes their harm taxonomy as a JSON+CSV file. Look for it.
    candidates = list(cset.rglob("*.json")) + list(cset.rglob("*.csv"))
    if not candidates:
        print("[cset] no JSON/CSV found in repo")
        return 0
    # Write the harm taxonomy as a single entry that documents the vocabulary
    out = [{
        "source_id": "CSET-AIID-HARM-TAXONOMY",
        "title": "CSET-AIID Harm Taxonomy (controlled vocabulary)",
        "date": "2024",
        "year": 2024,
        "category": "research",
        "description": (
            "Center for Security and Emerging Technology (CSET) and the Responsible AI Collaborative jointly "
            "published a harm taxonomy that annotates each AI Incident Database (AIID) incident with structured "
            "harm-type labels covering harm vector, severity, sector, location, victim group, and "
            "AI-system-relevance. The taxonomy is a reference, not an incident itself; downstream entries should "
            "cite this when reusing the harm-type labels."
        ),
        "attack_vector": "other",
        "affected": "AI Incident Database",
        "severity": "Info",
        "references": [
            {"title": "CSET-AIID Harm Taxonomy repository", "url": "https://github.com/georgetown-cset/CSET-AIID-harm-taxonomy", "type": "research"},
        ],
        "tags": ["cset", "taxonomy", "reference"],
    }]
    (INGEST / "cset_harm_taxonomy.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[cset]  wrote 1 taxonomy reference entry -> ingest/cset_harm_taxonomy.json")
    return 1


# ---------------------------------------------------------------------------
# 4) garak probes — each probe = one canonical attack class
# ---------------------------------------------------------------------------
GARAK_TO_LLM = {
    "promptinject": ["LLM01"], "latentinjection": ["LLM01"], "ansiescape": ["LLM01", "LLM05"],
    "leakreplay": ["LLM02"], "av_spam_scanning": ["LLM05"],
    "encoding": ["LLM01"], "goodside": ["LLM01"], "dan": ["LLM01"], "lmrc": ["LLM09"],
    "knownbadsignatures": ["LLM05"], "topic": ["LLM09"], "snowball": ["LLM09"],
    "malwaregen": ["LLM06"], "packagehallucination": ["LLM03", "LLM09"],
    "realtoxicityprompts": ["LLM09"], "xss": ["LLM05"], "exploitation": ["LLM05"],
    "divergence": ["LLM02"], "donotanswer": ["LLM09"], "fileformats": ["LLM03"],
    "grandma": ["LLM01"], "atkgen": ["LLM01"], "judge": ["LLM09"], "tap": ["LLM01"],
    "gcg": ["LLM01"], "audio": ["LLM05"], "phrasing": ["LLM01"], "test": ["LLM09"],
    "suffix": ["LLM01"], "continuation": ["LLM09"], "doctor": ["LLM09"],
    "misleading": ["LLM09"], "glitch": ["LLM01"], "topic_": ["LLM09"],
}


def ingest_garak() -> int:
    garak = EXTERNAL / "garak" / "garak" / "probes"
    if not garak.exists():
        print("[garak] probes dir missing — skipping")
        return 0
    out = []
    for f in sorted(garak.glob("*.py")):
        if f.name.startswith("_") or f.name == "base.py":
            continue
        probe_name = f.stem
        text = f.read_text(encoding="utf-8", errors="replace")

        # First docstring
        m = re.search(r'^"""(.+?)"""', text, re.DOTALL | re.MULTILINE)
        if not m:
            continue
        doc = m.group(1).strip()
        title_line = doc.split("\n")[0].strip()
        desc = doc.split("\n\n")[0] if "\n\n" in doc else doc

        # Tags from "tags = [...]" assignments
        tags_match = re.findall(r'tags\s*=\s*\[([^\]]+)\]', text)
        tag_set = set()
        for tg in tags_match:
            tag_set.update(re.findall(r'"([^"]+)"', tg))

        llm = GARAK_TO_LLM.get(probe_name.lower(), [])
        if not llm:
            # Heuristic by name
            n = probe_name.lower()
            if "inject" in n: llm = ["LLM01"]
            elif "leak" in n or "exfil" in n: llm = ["LLM02"]
            elif "tox" in n or "hate" in n or "harm" in n: llm = ["LLM09"]
            elif "dan" in n or "jailbreak" in n: llm = ["LLM01"]
            elif "malware" in n or "exploit" in n: llm = ["LLM06"]

        out.append({
            "source_id": f"GARAK-{probe_name}",
            "title": f"garak probe: {title_line[:120]}",
            "date": "2024",
            "year": 2024,
            "category": "research",
            "description": (
                f"NVIDIA garak LLM vulnerability scanner probe `{probe_name}`. " + desc
            )[:1500],
            "attack_vector": "jailbreak" if "dan" in probe_name.lower() or "jail" in probe_name.lower() else (
                "prompt-injection" if "inject" in probe_name.lower() else "other"
            ),
            "affected": "LLM evaluation surface",
            "severity": "Medium",
            "owasp_llm": llm,
            "owasp_asi": ["ASI01"] if "inject" in probe_name.lower() or "jail" in probe_name.lower() else [],
            "references": [
                {
                    "title": f"garak probe source — {probe_name}",
                    "url": f"https://github.com/NVIDIA/garak/blob/main/garak/probes/{f.name}",
                    "type": "research",
                },
                {"title": "NVIDIA garak", "url": "https://github.com/NVIDIA/garak", "type": "research"},
            ],
            "tags": ["garak", "probe", probe_name] + sorted(tag_set)[:8],
        })

    (INGEST / "garak_probes.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[garak]  wrote {len(out)} probes -> ingest/garak_probes.json")
    return len(out)


# ---------------------------------------------------------------------------
# 5) promptfoo red-team plugins
# ---------------------------------------------------------------------------
def ingest_promptfoo() -> int:
    constants = EXTERNAL / "promptfoo" / "src" / "redteam" / "constants"
    if not constants.exists():
        print("[promptfoo] constants dir missing — skipping")
        return 0
    plugins_text = (constants / "plugins.ts").read_text(encoding="utf-8", errors="replace")
    strategies_text = (constants / "strategies.ts").read_text(encoding="utf-8", errors="replace")

    # Extract plugin IDs (anything in single-quoted strings inside arrays)
    plugin_ids = set(re.findall(r"['\"]([a-z][a-z0-9:_-]*[a-z0-9])['\"](?=\s*[,\]])", plugins_text))
    strategy_ids = set(re.findall(r"['\"]([a-z][a-z0-9:_-]*[a-z0-9])['\"](?=\s*[,\]])", strategies_text))

    # Filter to ones that look like plugin namespaces (avoid CSS classes, etc.)
    plugin_ids = {p for p in plugin_ids if (":" in p or "-" in p) and 3 < len(p) < 80}
    strategy_ids = {s for s in strategy_ids if 3 < len(s) < 80}

    out = []
    for kind, ids in [("plugin", sorted(plugin_ids)), ("strategy", sorted(strategy_ids))]:
        for pid in ids:
            n = pid.lower()
            llm, asi = [], []
            tags = ["promptfoo", "redteam", kind, pid]

            # Map plugin id -> taxonomies
            if pid.startswith("harmful:"):
                llm = ["LLM09"]
                tags.append("harmful")
            elif pid.startswith("bias:"):
                llm = ["LLM09"]
                tags.append("bias")
            elif "prompt" in n and ("inject" in n or "extract" in n):
                llm, asi = ["LLM01", "LLM07"], ["ASI01"]
            elif n in ("hijacking", "indirect-prompt-injection"):
                llm, asi = ["LLM01", "LLM06"], ["ASI01"]
            elif n == "excessive-agency":
                llm, asi = ["LLM06"], ["ASI02", "ASI03"]
            elif n in ("pii", "pii:api-db", "pii:direct", "pii:session", "pii:social"):
                llm = ["LLM02"]
            elif n.startswith("rbac") or n in ("bola", "bfla"):
                llm, asi = ["LLM06"], ["ASI03"]
            elif n in ("shell-injection", "rce", "sql-injection", "ssrf", "debug-access", "imitation"):
                llm, asi = ["LLM05"], ["ASI05"]
            elif n == "ascii-smuggling":
                llm = ["LLM01"]
            elif n == "divergent-repetition":
                llm = ["LLM02"]
            elif n in ("contracts", "competitors", "religion", "politics", "intentional-misuse"):
                llm = ["LLM06"]
            elif "memory" in n or "context" in n:
                asi = ["ASI06"]
            elif "agent" in n or "tool" in n:
                asi = ["ASI02"]
            elif "supply" in n or "package" in n:
                llm, asi = ["LLM03"], ["ASI04"]
            elif "hallucinat" in n:
                llm = ["LLM09"]
            elif "donotanswer" in n or "beavertails" in n or "cyberseceval" in n:
                llm = ["LLM09"]

            # Skip cosmetic IDs (CSS-class shaped)
            if pid in ("strategy", "plugin", "true", "false", "none"):
                continue

            out.append({
                "source_id": f"PROMPTFOO-{kind}-{pid}",
                "title": f"promptfoo {kind}: {pid}",
                "date": "2024",
                "year": 2024,
                "category": "research",
                "description": (
                    f"promptfoo red-team {kind} `{pid}`. Defines an automated test for this attack class "
                    f"in promptfoo's open-source LLM/agent evaluation framework. See plugin source for "
                    f"attack-pattern details and example payloads."
                ),
                "attack_vector": (
                    "prompt-injection" if "inject" in n else
                    "jailbreak" if "jail" in n or "dan" in n or "crescendo" in n else
                    "data-exfiltration" if "leak" in n or "exfil" in n or "pii" in n else
                    "rce" if "shell" in n or "rce" in n else
                    "tool-abuse" if "hijack" in n or "agent" in n else
                    "other"
                ),
                "affected": "LLM/agent evaluation surface",
                "severity": "Medium",
                "owasp_llm": llm,
                "owasp_asi": asi,
                "references": [
                    {
                        "title": f"promptfoo {kind} {pid}",
                        "url": f"https://www.promptfoo.dev/docs/red-team/{kind}s/{pid.split(':')[0]}/",
                        "type": "documentation",
                    },
                    {"title": "promptfoo", "url": "https://github.com/promptfoo/promptfoo", "type": "research"},
                ],
                "tags": tags,
            })

    (INGEST / "promptfoo_plugins.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[promptfoo]  wrote {len(out)} plugins+strategies -> ingest/promptfoo_plugins.json")
    return len(out)


# ---------------------------------------------------------------------------
# 6) ModelOriented/CVE-AI curated list
# ---------------------------------------------------------------------------
def ingest_cve_ai_curated() -> int:
    cve_ai = EXTERNAL / "CVE-AI"
    if not cve_ai.exists():
        print("[cve-ai] repo missing — skipping")
        return 0
    out = []
    # Look for CSV or JSON exports of CVE data
    for f in cve_ai.rglob("*.csv"):
        try:
            with f.open(encoding="utf-8", errors="replace") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
            print(f"[cve-ai] {f.name}: {len(rows)} rows; fields: {reader.fieldnames}")
            for row in rows:
                cve = next((row[k] for k in row if "cve" in k.lower() and row.get(k)), None)
                if not cve or not re.match(r"^CVE-\d{4}-\d{4,7}$", cve):
                    continue
                title = next((row[k] for k in row if k.lower() in ("title", "name", "summary", "description")), cve)
                desc = next((row[k] for k in row if "descr" in k.lower()), title)
                year_match = re.match(r"CVE-(\d{4})", cve)
                year = int(year_match.group(1)) if year_match else 2024
                severity = next((row[k] for k in row if "sever" in k.lower() or "cvss" in k.lower()), "Medium")
                affected = next((row[k] for k in row if k.lower() in ("vendor", "product", "affected", "package")), "")
                out.append({
                    "source_id": f"CVE-AI-{cve}",
                    "cve_id": cve,
                    "title": title[:200],
                    "date": str(year),
                    "year": year,
                    "category": "vulnerability-disclosure",
                    "description": desc[:1500],
                    "attack_vector": "other",
                    "affected": affected,
                    "severity": "Critical" if "9" in severity or "10" in severity else ("High" if "8" in severity or "7" in severity else "Medium"),
                    "owasp_llm": ["LLM03"],  # most curated AI CVEs are supply-chain
                    "owasp_asi": ["ASI04"],
                    "references": [
                        {"title": f"NVD {cve}", "url": f"https://nvd.nist.gov/vuln/detail/{cve}", "type": "advisory"},
                        {"title": "CVE-AI curated list", "url": "https://github.com/ModelOriented/CVE-AI", "type": "research"},
                    ],
                    "tags": ["cve", "ai-package", "curated"],
                })
        except Exception as e:
            print(f"  WARN: failed to read {f.name}: {e}")
    # Also try YAML/JSON
    for f in list(cve_ai.rglob("*.json"))[:3]:
        if f.name in ("package.json", "package-lock.json"):
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for row in data:
                    cve = row.get("id") or row.get("cve") or row.get("cve_id") if isinstance(row, dict) else None
                    if cve and re.match(r"^CVE-\d{4}-\d{4,7}$", cve):
                        year = int(cve.split("-")[1])
                        out.append({
                            "source_id": f"CVE-AI-{cve}",
                            "cve_id": cve,
                            "title": row.get("title", row.get("summary", cve))[:200],
                            "date": str(year),
                            "year": year,
                            "category": "vulnerability-disclosure",
                            "description": row.get("description", row.get("summary", cve))[:1500],
                            "attack_vector": "other",
                            "affected": row.get("affected", ""),
                            "severity": "Medium",
                            "owasp_llm": ["LLM03"],
                            "owasp_asi": ["ASI04"],
                            "references": [
                                {"title": f"NVD {cve}", "url": f"https://nvd.nist.gov/vuln/detail/{cve}", "type": "advisory"},
                                {"title": "CVE-AI curated list", "url": "https://github.com/ModelOriented/CVE-AI", "type": "research"},
                            ],
                            "tags": ["cve", "ai-package", "curated"],
                        })
        except Exception:
            pass

    # dedupe by CVE
    by_cve = {}
    for e in out:
        by_cve.setdefault(e["cve_id"], e)
    out = list(by_cve.values())
    (INGEST / "cve_ai_curated.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"[cve-ai]  wrote {len(out)} CVE entries -> ingest/cve_ai_curated.json")
    return len(out)


def main():
    counts = {}
    counts["atlas"] = ingest_atlas()
    counts["aiid_oecd_bridge"] = ingest_aiid_oecd_bridge()
    counts["cset"] = ingest_cset()
    counts["garak"] = ingest_garak()
    counts["promptfoo"] = ingest_promptfoo()
    counts["cve_ai"] = ingest_cve_ai_curated()
    print("\n[summary]")
    for k, v in counts.items():
        print(f"  {k:25s} {v}")


if __name__ == "__main__":
    main()
