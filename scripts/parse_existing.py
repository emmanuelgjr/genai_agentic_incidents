"""
Parse the three legacy source files into the unified incident schema.

Inputs (relative to project root):
  legacy/incidents.json                       (114 entries, structured)
  legacy/ASI_Agentic_Exploits_Incidents.md    (~45 entries, table-format)
  legacy/additional-exploits-incidents.md     (~80 entries, table-format)

Output:
  data/legacy_consolidated.json (validated against schema)

Mapping rules:
  - existing "owasp_entries" with LLMxx values -> owasp_llm
  - existing "owasp_entries" with DSGAIxx values -> owasp_dsgai
  - Existing MAESTRO layers preserved
  - ASI codes parsed from MD tables -> owasp_asi
  - NIST AI RMF / MITRE ATLAS inferred from attack_vector and OWASP mapping
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "legacy"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

# Heuristic mapping: OWASP LLM Top 10 -> common MITRE ATLAS techniques + NIST AI RMF subcategories
LLM_TO_ATLAS = {
    "LLM01": ["AML.T0051", "AML.T0051.000", "AML.T0051.001"],
    "LLM02": ["AML.T0057", "AML.T0024"],
    "LLM03": ["AML.T0010", "AML.T0010.001", "AML.T0010.003"],
    "LLM04": ["AML.T0018", "AML.T0019", "AML.T0020", "AML.T0059"],
    "LLM05": ["AML.T0050", "AML.T0060"],
    "LLM06": ["AML.T0053", "AML.T0048"],
    "LLM07": ["AML.T0056", "AML.T0067"],
    "LLM08": ["AML.T0066", "AML.T0070"],
    "LLM09": ["AML.T0058", "AML.T0048.001"],
    "LLM10": ["AML.T0029", "AML.T0034", "AML.T0046"],
}

ASI_TO_ATLAS = {
    "ASI01": ["AML.T0051"],
    "ASI02": ["AML.T0053", "AML.T0050"],
    "ASI03": ["AML.T0012", "AML.T0055"],
    "ASI04": ["AML.T0010", "AML.T0010.001"],
    "ASI05": ["AML.T0050", "AML.T0011", "AML.T0049"],
    "ASI06": ["AML.T0066", "AML.T0020", "AML.T0059"],
    "ASI07": ["AML.T0053"],
    "ASI08": ["AML.T0048"],
    "ASI09": ["AML.T0048.001", "AML.T0048.003"],
    "ASI10": ["AML.T0048"],
}

LLM_TO_NIST = {
    "LLM01": ["MEASURE-2.7", "MAP-2.1", "MANAGE-2.3"],
    "LLM02": ["MEASURE-2.10", "MEASURE-2.7", "GOVERN-1.1"],
    "LLM03": ["GOVERN-6.1", "GOVERN-6.2", "MAP-4.1"],
    "LLM04": ["MEASURE-2.7", "MAP-4.2", "MANAGE-3.2"],
    "LLM05": ["MEASURE-2.7", "MEASURE-2.5"],
    "LLM06": ["MAP-3.5", "GOVERN-3.2", "MANAGE-2.4"],
    "LLM07": ["MEASURE-2.7", "MEASURE-2.10"],
    "LLM08": ["MEASURE-2.7"],
    "LLM09": ["MEASURE-2.5", "MEASURE-2.8", "MANAGE-4.3"],
    "LLM10": ["MEASURE-2.4", "MANAGE-2.2"],
}

ASI_TO_NIST = {
    "ASI01": ["MEASURE-2.7", "MAP-2.1"],
    "ASI02": ["MAP-3.5", "MEASURE-2.7", "GOVERN-3.2"],
    "ASI03": ["GOVERN-1.4", "MEASURE-2.7"],
    "ASI04": ["GOVERN-6.1", "GOVERN-6.2", "MAP-4.1"],
    "ASI05": ["MEASURE-2.7", "MANAGE-2.3"],
    "ASI06": ["MEASURE-2.7", "MAP-4.2"],
    "ASI07": ["MEASURE-2.7", "MAP-4.1"],
    "ASI08": ["MANAGE-2.3", "MANAGE-4.1", "GOVERN-6.2"],
    "ASI09": ["GOVERN-3.2", "MAP-3.5", "MEASURE-2.8"],
    "ASI10": ["GOVERN-1.4", "MANAGE-2.4", "GOVERN-6.2"],
}

# Common attack vector -> additional ATLAS / NIST hints
ATTACK_VECTOR_HINTS = {
    "rce": (["AML.T0050", "AML.T0049"], ["MEASURE-2.7", "MANAGE-2.3"]),
    "deserialization": (["AML.T0010.001", "AML.T0050"], ["MEASURE-2.7", "GOVERN-6.1"]),
    "supply-chain": (["AML.T0010"], ["GOVERN-6.1", "GOVERN-6.2"]),
    "ssrf": (["AML.T0049"], ["MEASURE-2.7"]),
    "command-injection": (["AML.T0050"], ["MEASURE-2.7"]),
    "sandbox-escape": (["AML.T0050"], ["MEASURE-2.7", "MANAGE-2.3"]),
    "prompt-injection": (["AML.T0051", "AML.T0051.000"], ["MEASURE-2.7", "MAP-2.1"]),
    "indirect-prompt-injection": (["AML.T0051.001"], ["MEASURE-2.7", "MAP-2.1"]),
    "jailbreak": (["AML.T0054"], ["MEASURE-2.7"]),
    "data-exfiltration": (["AML.T0024", "AML.T0025", "AML.T0057"], ["MEASURE-2.10", "MEASURE-2.7"]),
    "memory-poisoning": (["AML.T0020", "AML.T0066"], ["MEASURE-2.7", "MAP-4.2"]),
    "tool-abuse": (["AML.T0053"], ["MAP-3.5", "MEASURE-2.7"]),
}


def slug_to_id(n: int) -> str:
    return f"INC-{n:05d}"


def normalize_owasp(codes: list[str]) -> tuple[list[str], list[str], list[str]]:
    llm, asi, dsgai = [], [], []
    for c in codes or []:
        c = c.strip().upper()
        if c.startswith("LLM"):
            llm.append(c[:5])  # LLM01..LLM10
        elif c.startswith("ASI"):
            asi.append(c[:5])
        elif c.startswith("DSGAI"):
            dsgai.append(c[:7])
    return sorted(set(llm)), sorted(set(asi)), sorted(set(dsgai))


def derive_atlas_and_nist(llm, asi, attack_vector):
    atlas, nist = set(), set()
    for c in llm:
        for t in LLM_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in LLM_TO_NIST.get(c, []):
            nist.add(n)
    for c in asi:
        for t in ASI_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in ASI_TO_NIST.get(c, []):
            nist.add(n)
    if attack_vector:
        av_key = attack_vector.lower().strip()
        if av_key in ATTACK_VECTOR_HINTS:
            ax, nx = ATTACK_VECTOR_HINTS[av_key]
            atlas.update(ax)
            nist.update(nx)
    return sorted(atlas), sorted(nist)


# ---------------------------------------------------------------------------
# 1) Existing structured JSON
# ---------------------------------------------------------------------------
def parse_json_source(path: Path, start_id: int) -> tuple[list[dict], int]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out = []
    next_id = start_id
    for entry in raw.get("incidents", []):
        llm, asi, dsgai = normalize_owasp(entry.get("owasp_entries", []))
        av = entry.get("attack_vector", "")
        # Try to extract a controlled-vocab attack_vector tag
        av_norm = ""
        av_lower = av.lower()
        for k in ATTACK_VECTOR_HINTS:
            if k in av_lower:
                av_norm = k
                break
        if not av_norm:
            # fallback to first word
            av_norm = av_lower.split("—")[0].split("-")[0].strip().split()[0] if av_lower else ""

        atlas, nist = derive_atlas_and_nist(llm, asi, av_norm)

        new_entry = {
            "id": slug_to_id(next_id),
            "source_ids": [entry.get("id", "")] if entry.get("id") else [],
            "title": entry.get("title", "").strip(),
            "date": entry.get("date", str(entry.get("year", ""))),
            "year": int(entry.get("year", 0)) or None,
            "category": entry.get("category", "real-world"),
            "description": entry.get("description", "").strip(),
            "attack_vector": av_norm or av or "other",
            "affected": entry.get("affected", "").strip(),
            "impact": entry.get("impact", "").strip(),
            "severity": entry.get("severity", "Medium"),
            "owasp_llm": llm,
            "owasp_asi": asi,
            "owasp_dsgai": dsgai,
            "nist_ai_rmf": nist,
            "mitre_atlas": atlas,
            "maestro_layers": entry.get("maestro_layers", []),
            "mitigations": entry.get("mitigations", []),
            "references": [
                {"title": r.get("title", ""), "url": r.get("url", ""), "type": r.get("type", "other")}
                for r in entry.get("references", []) if r.get("url")
            ],
            "tags": entry.get("tags", []),
            "added": str(date.today()),
            "updated": str(date.today()),
        }
        # Year defaults
        if not new_entry["year"]:
            m = re.match(r"(\d{4})", str(new_entry["date"]))
            if m:
                new_entry["year"] = int(m.group(1))

        out.append(new_entry)
        next_id += 1
    return out, next_id


# ---------------------------------------------------------------------------
# 2) Markdown table parser (ASI tracker + additional-exploits)
# ---------------------------------------------------------------------------
TABLE_HEADER_RE = re.compile(r"^\|\s*Date\s*\|\s*Exploit", re.IGNORECASE)
SEP_RE = re.compile(r"^\|[-\s:|]+\|\s*$")
DATE_RE = re.compile(r"\*\*([A-Za-z]{3,9})\s*(\d{4})\*\*|\*\*(\d{4})\*\*")
MONTH_MAP = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Nov": "11", "Dec": "12",
    "January": "01", "February": "02", "March": "03", "April": "04",
    "June": "06", "July": "07", "August": "08", "September": "09",
    "October": "10", "November": "11", "December": "12",
}


def split_md_row(row: str) -> list[str]:
    # Split on | but ignore leading/trailing
    parts = [c.strip() for c in row.strip("|").split("|")]
    # Replace HTML <br> with newline
    return [re.sub(r"<br\s*/?>", "\n", p, flags=re.IGNORECASE) for p in parts]


def parse_date_cell(cell: str) -> tuple[str, int | None]:
    m = DATE_RE.search(cell)
    if not m:
        # try plain "2025" or "2023-2024"
        m2 = re.search(r"(\d{4})", cell)
        if m2:
            return m2.group(1), int(m2.group(1))
        return "", None
    if m.group(3):  # plain "**2026**"
        return m.group(3), int(m.group(3))
    month_word, year = m.group(1), m.group(2)
    month = MONTH_MAP.get(month_word[:3].capitalize(), "")
    if month:
        return f"{year}-{month}", int(year)
    return year, int(year)


def parse_md_table(path: Path, start_id: int) -> tuple[list[dict], int]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    out = []
    next_id = start_id
    in_table = False
    for raw in lines:
        line = raw.rstrip()
        if TABLE_HEADER_RE.match(line):
            in_table = True
            continue
        if SEP_RE.match(line):
            continue
        if not in_table:
            continue
        if not line.startswith("|"):
            in_table = False
            continue
        cells = split_md_row(line)
        if len(cells) < 4:
            continue

        date_cell, title_cell, impact_cell, mapping_cell = cells[0], cells[1], cells[2], cells[3]
        links_cell = cells[4] if len(cells) > 4 else ""

        # Title — usually **Title**
        title = re.sub(r"\*\*", "", title_cell).strip()
        if not title:
            continue

        date_str, year = parse_date_cell(date_cell)
        if not year:
            continue

        # ASI codes
        asi_codes = sorted(set(re.findall(r"ASI(\d{2})", mapping_cell)))
        asi_codes = [f"ASI{c}" for c in asi_codes]

        # Heuristic LLM mapping from ASI / vector keywords in impact text
        llm_codes = set()
        impact_lower = impact_cell.lower()
        if "prompt injection" in impact_lower or "indirect prompt" in impact_lower or "ASI01" in mapping_cell:
            llm_codes.add("LLM01")
        if "data exfiltrat" in impact_lower or "leak" in impact_lower or "exposed" in impact_lower:
            llm_codes.add("LLM02")
        if "supply chain" in impact_lower or "ASI04" in mapping_cell:
            llm_codes.add("LLM03")
        if "poison" in impact_lower or "memory" in impact_lower or "ASI06" in mapping_cell:
            llm_codes.add("LLM04")
        if "rce" in impact_lower or "code execution" in impact_lower or "ASI05" in mapping_cell:
            llm_codes.add("LLM05")
        if "agency" in impact_lower or "autonom" in impact_lower or "without approval" in impact_lower or "without consent" in impact_lower:
            llm_codes.add("LLM06")
        if "system prompt" in impact_lower:
            llm_codes.add("LLM07")
        if "rag" in impact_lower or "embedding" in impact_lower or "vector" in impact_lower:
            llm_codes.add("LLM08")
        if "hallucinat" in impact_lower or "misinformation" in impact_lower or "false" in impact_lower:
            llm_codes.add("LLM09")
        llm_codes = sorted(llm_codes)

        # Attack vector
        av = "other"
        for k in ATTACK_VECTOR_HINTS:
            if k in impact_lower:
                av = k
                break
        if av == "other":
            if "rce" in impact_lower:
                av = "rce"
            elif "injection" in impact_lower:
                av = "prompt-injection"
            elif "exfil" in impact_lower or "data theft" in impact_lower or "leak" in impact_lower:
                av = "data-exfiltration"

        # Severity heuristic
        sev = "Medium"
        if "cvss 9" in impact_lower or "cvss 10" in impact_lower or "critical" in impact_lower:
            sev = "Critical"
        elif "cvss 8" in impact_lower or "cvss 7" in impact_lower or "high" in impact_lower:
            sev = "High"
        elif "cvss 4" in impact_lower or "cvss 5" in impact_lower or "cvss 6" in impact_lower:
            sev = "Medium"

        # References
        refs = []
        for m in re.finditer(r"\[([^\]]+)\]\((https?://[^\)]+)\)", links_cell):
            link_title, url = m.group(1), m.group(2)
            ref_type = "advisory" if "nvd" in url.lower() or "cve" in url.lower() else (
                "vendor" if any(v in url.lower() for v in ["microsoft.com", "aws.amazon.com", "google.com", "anthropic.com", "openai.com"]) else "research"
            )
            refs.append({"title": link_title, "url": url, "type": ref_type})

        if not refs:
            # No URL -> not validated, skip
            continue

        # CVEs
        cves = sorted(set(re.findall(r"CVE-\d{4}-\d{4,7}", title + " " + impact_cell + " " + links_cell)))

        atlas, nist = derive_atlas_and_nist(llm_codes, asi_codes, av)

        entry = {
            "id": slug_to_id(next_id),
            "source_ids": [],
            "cve_ids": cves,
            "title": title,
            "date": date_str,
            "year": year,
            "category": "real-world",
            "description": re.sub(r"\s+", " ", impact_cell).strip(),
            "attack_vector": av,
            "affected": title.split("--")[0].split("—")[0].strip(),
            "severity": sev,
            "owasp_llm": llm_codes,
            "owasp_asi": asi_codes,
            "nist_ai_rmf": nist,
            "mitre_atlas": atlas,
            "references": refs,
            "tags": [],
            "added": str(date.today()),
            "updated": str(date.today()),
        }
        out.append(entry)
        next_id += 1
    return out, next_id


def main():
    next_id = 1
    all_entries: list[dict] = []

    json_path = LEGACY / "incidents.json"
    if json_path.exists():
        entries, next_id = parse_json_source(json_path, next_id)
        print(f"[legacy json]  parsed {len(entries):4d} entries (next_id={next_id})")
        all_entries.extend(entries)

    for md in ["ASI_Agentic_Exploits_Incidents.md", "additional-exploits-incidents.md"]:
        md_path = LEGACY / md
        if md_path.exists():
            entries, next_id = parse_md_table(md_path, next_id)
            print(f"[{md:40s}] parsed {len(entries):4d} entries (next_id={next_id})")
            all_entries.extend(entries)

    out_path = DATA / "legacy_consolidated.json"
    out_path.write_text(
        json.dumps(
            {
                "version": "1.0.0",
                "generated": str(date.today()),
                "source": "legacy consolidation",
                "incidents": all_entries,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
        newline="\n",
    )
    print(f"[output] wrote {len(all_entries)} entries -> {out_path}")


if __name__ == "__main__":
    main()
