"""
Ingest the public AIAAIC Repository spreadsheet.

Source: the canonical Google Sheet linked from
        https://www.aiaaic.org/aiaaic-repository
        (sheet id 1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI,
        Incidents tab gid 888071280)

AIAAIC's spreadsheet is the curated, maintainer-managed source — the
slug-style entries in ingest/aiaaic_incidents.json were hand-picked and
use vanity IDs (e.g. AIAAIC-wpp-ceo-deepfake). The sheet uses canonical
`AIAAIC{N}` integer IDs and currently lists 2,244 incidents.

Output: ingest/aiaaic_sheet_incidents.json — picked up by
scripts/merge_and_dedupe.py and deduped by AIAAIC URL when present.
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache"
CACHE.mkdir(parents=True, exist_ok=True)

SHEET_ID = "1Bn55B4xz21-_Rgdr8BBb2lt0n_4rzLGxFADMlVW0PYI"
SHEET_GID = "888071280"  # "Incidents" tab
CSV_URL = (
    f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export"
    f"?format=csv&gid={SHEET_GID}"
)
CACHE_FILE = CACHE / "aiaaic_sheet.csv"

# AIAAIC headers come on row index 1 of the dump (row 0 is the section
# label "Incidents"). Columns are positional in the export.
COL_ID, COL_HEADLINE, COL_OCCURRED, COL_DEPLOYER, COL_DEVELOPER = 0, 1, 2, 3, 4
COL_SYSTEM, COL_TECH, COL_PURPOSE = 5, 6, 7
COL_TRIGGER, COL_ETHICAL = 8, 9
COL_JURISDICTION, COL_SECTOR = 10, 11
COL_HARM_INDIV, COL_HARM_SOCIETAL, COL_HARM_ENV = 12, 13, 14
COL_CONSEQ, COL_RESPONSE = 15, 16
COL_SUMMARY = 17

# Security-relevant ethical-issue / news-trigger / technology values.
# We keep an entry if it touches security, privacy, or trustworthiness OR
# the technology is GenAI/agentic. AIAAIC has many fairness/bias-only
# entries that we explicitly want to exclude per the project policy.
SECURITY_ETHICAL_ISSUES = {
    "security",
    "privacy/surveillance",
    "robustness",
    "safety",
    "accountability",
    "human/civil rights",
    "child sexual abuse material",
    "misinformation",
    "disinformation",
    "deepfake",
}

# Technology keywords that automatically qualify (generative / agentic /
# LLM-adjacent capabilities — out of scope is purely-classical ML).
GENAI_TECH_KEYWORDS = (
    "generative ai",
    "large language model",
    "llm",
    "agentic",
    "voice clone",
    "voice-clone",
    "deepfake",
    "chatbot",
    "diffusion",
    "text-to-image",
    "image generation",
    "video generation",
    "code generation",
)

SECURITY_HEADLINE_KEYWORDS = (
    "deepfake jailbreak prompt injection exfiltrat ransomware phishing scam "
    "fraud breach leak hack exploit hijack rce remote code malware impersonat "
    "spoofed credential stolen unauthorized backdoor poisoning csam "
    "child sexual"
).split()

# Map AIAAIC ethical issue → OWASP LLM / ASI codes.
ETHICAL_TO_OWASP_LLM = {
    "Security": ["LLM02", "LLM03"],
    "Privacy/surveillance": ["LLM02"],
    "Accuracy/reliability": ["LLM05", "LLM09"],
    "Anthropomorphism": ["LLM09"],
    "Safety": ["LLM05"],
    "Robustness": ["LLM04", "LLM05"],
    "Transparency": ["LLM07"],
    "Accountability": ["LLM06"],
    "Misinformation": ["LLM09"],
    "Disinformation": ["LLM09"],
}
ETHICAL_TO_OWASP_ASI = {
    "Security": ["ASI02", "ASI03"],
    "Privacy/surveillance": ["ASI03"],
    "Safety": ["ASI08"],
    "Accountability": ["ASI09"],
    "Accuracy/reliability": ["ASI09"],
    "Misinformation": ["ASI09"],
    "Disinformation": ["ASI09"],
    "Anthropomorphism": ["ASI09"],
}

CONSEQUENCE_TO_SEVERITY = {
    "Loss of life": "Critical",
    "Significant financial damage": "High",
    "Litigation": "Medium",
    "System termination": "Medium",
    "Imprisonment": "Critical",
    "Injury": "High",
    "Defamation": "Medium",
}


def download_csv() -> str:
    """Fetch the sheet (with disk cache)."""
    if CACHE_FILE.exists() and CACHE_FILE.stat().st_size > 100_000:
        return CACHE_FILE.read_text(encoding="utf-8")
    print(f"[aiaaic] downloading {CSV_URL}")
    req = urllib.request.Request(
        CSV_URL, headers={"User-Agent": "Mozilla/5.0 (genai_agentic_incidents)"}
    )
    text = urllib.request.urlopen(req, timeout=60).read().decode(
        "utf-8", errors="replace"
    )
    CACHE_FILE.write_text(text, encoding="utf-8")
    return text


def parse_year(occurred: str) -> int | None:
    m = re.search(r"\b(19|20)\d{2}\b", occurred or "")
    return int(m.group(0)) if m else None


def split_taxonomy(cell: str) -> list[str]:
    if not cell:
        return []
    return [p.strip() for p in re.split(r"[;,/]\s*", cell) if p.strip()]


def is_security_relevant(row: dict) -> bool:
    ethical = {e.lower() for e in split_taxonomy(row.get("ethical", ""))}
    if ethical & SECURITY_ETHICAL_ISSUES:
        return True
    headline = (row.get("headline") or "").lower()
    if any(kw in headline for kw in SECURITY_HEADLINE_KEYWORDS):
        return True
    tech = (row.get("technology") or "").lower()
    if any(kw in tech for kw in GENAI_TECH_KEYWORDS):
        # Generative/agentic tech: include even without explicit security framing
        # (downstream merge will dedupe against AIID/other sources).
        return True
    return False


def detect_attack_vector(row: dict) -> str:
    text = (
        (row.get("headline") or "")
        + " "
        + (row.get("ethical") or "")
        + " "
        + (row.get("purpose") or "")
    ).lower()
    if "deepfake" in text or "voice clone" in text:
        return "deepfake"
    if "prompt inject" in text or "jailbreak" in text:
        return "prompt-injection"
    if "exfil" in text or "data leak" in text or "data breach" in text:
        return "data-exfiltration"
    if "ransom" in text or "rce" in text or "remote code" in text:
        return "rce"
    if "phishing" in text or "scam" in text or "fraud" in text or "imperson" in text:
        return "other"  # social engineering → keep generic
    if "csam" in text or "child sexual" in text:
        return "other"
    if "misinform" in text or "disinform" in text:
        return "other"
    return "other"


def detect_severity(row: dict) -> str:
    conseq = split_taxonomy(row.get("consequence", ""))
    harm_indiv = split_taxonomy(row.get("harm_indiv", ""))
    all_harms = conseq + harm_indiv
    # Walk from worst to least
    for label in ("Loss of life", "Imprisonment", "Injury",
                  "Significant financial damage", "Defamation",
                  "Litigation", "System termination"):
        if label in all_harms:
            return CONSEQUENCE_TO_SEVERITY[label]
    return "Medium"


def normalize_row(raw_row: list[str]) -> dict | None:
    while len(raw_row) < 19:
        raw_row.append("")
    if not (raw_row[COL_ID] or "").startswith("AIAAIC"):
        return None
    if raw_row[COL_ID] == "AIAAIC ID#":  # second header row
        return None

    row = {
        "id": raw_row[COL_ID].strip(),
        "headline": (raw_row[COL_HEADLINE] or "").strip(),
        "occurred": (raw_row[COL_OCCURRED] or "").strip(),
        "deployer": (raw_row[COL_DEPLOYER] or "").strip(),
        "developer": (raw_row[COL_DEVELOPER] or "").strip(),
        "system": (raw_row[COL_SYSTEM] or "").strip(),
        "technology": (raw_row[COL_TECH] or "").strip(),
        "purpose": (raw_row[COL_PURPOSE] or "").strip(),
        "trigger": (raw_row[COL_TRIGGER] or "").strip(),
        "ethical": (raw_row[COL_ETHICAL] or "").strip(),
        "jurisdiction": (raw_row[COL_JURISDICTION] or "").strip(),
        "sector": (raw_row[COL_SECTOR] or "").strip(),
        "harm_indiv": (raw_row[COL_HARM_INDIV] or "").strip(),
        "harm_societal": (raw_row[COL_HARM_SOCIETAL] or "").strip(),
        "harm_env": (raw_row[COL_HARM_ENV] or "").strip(),
        "consequence": (raw_row[COL_CONSEQ] or "").strip(),
        "response": (raw_row[COL_RESPONSE] or "").strip(),
        "summary": (raw_row[COL_SUMMARY] or "").strip(),
    }
    if not row["headline"] or len(row["headline"]) < 5:
        return None
    year = parse_year(row["occurred"])
    if not year or year < 1980 or year > 2030:
        return None
    if not is_security_relevant(row):
        return None

    ethical_items = split_taxonomy(row["ethical"])
    owasp_llm: set[str] = set()
    owasp_asi: set[str] = set()
    for item in ethical_items:
        owasp_llm.update(ETHICAL_TO_OWASP_LLM.get(item, []))
        owasp_asi.update(ETHICAL_TO_OWASP_ASI.get(item, []))

    # Headline pattern fallbacks
    h = row["headline"].lower()
    if "deepfake" in h or "voice clone" in h or "imperson" in h:
        owasp_llm.add("LLM09")
        owasp_asi.add("ASI09")
    if "prompt inject" in h or "jailbreak" in h:
        owasp_llm.add("LLM01")
        owasp_asi.add("ASI01")
    if "data leak" in h or "data breach" in h or "exfil" in h:
        owasp_llm.add("LLM02")
        owasp_asi.add("ASI03")

    affected = (row["developer"] or row["deployer"] or row["system"]).strip()
    if not affected and row["sector"]:
        affected = row["sector"]

    # The summary cell often has multiple URLs separated by spaces / newlines
    urls = re.findall(r"https?://[^\s,;]+", row["summary"])
    aiaaic_slug = None
    references = []
    for u in urls[:8]:
        u_clean = u.strip(",.;")
        rtype = "report" if "aiaaic.org" in u_clean else "news"
        ref_title = "AIAAIC entry" if "aiaaic.org" in u_clean else u_clean
        references.append({"title": ref_title, "url": u_clean, "type": rtype})
        if "aiaaic.org" in u_clean and "/aiaaic-repository/" in u_clean:
            slug = u_clean.rstrip("/").split("/")[-1]
            aiaaic_slug = slug

    if not references:
        # Synthesise a placeholder using the canonical entry URL form.
        slug = re.sub(r"[^a-z0-9]+", "-", row["headline"].lower()).strip("-")
        references.append({
            "title": "AIAAIC entry",
            "url": f"https://www.aiaaic.org/aiaaic-repository/ai-algorithmic-and-automation-incidents/{slug}",
            "type": "report",
        })

    description = (
        f"AIAAIC report: {row['headline']}. "
        + (f"System: {row['system']}. " if row["system"] else "")
        + (f"Technology: {row['technology']}. " if row["technology"] else "")
        + (f"Purpose: {row['purpose']}. " if row["purpose"] else "")
        + (f"Ethical issues: {row['ethical']}. " if row["ethical"] else "")
        + (f"Reported consequences: {row['consequence']}. " if row["consequence"] else "")
        + (f"Response: {row['response']}." if row["response"] else "")
    ).strip()

    tags = ["aiaaic", "aiaaic-sheet"]
    if row["sector"]:
        tags.append("sector-" + re.sub(r"\s+", "-", row["sector"].lower()))
    if row["jurisdiction"]:
        tags.append("juris-" + re.sub(r"\s+", "-", row["jurisdiction"].lower())[:24])

    return {
        "source_id": row["id"],
        "title": row["headline"][:300],
        "date": str(year),
        "year": year,
        "category": "real-world",
        "description": description[:1500],
        "attack_vector": detect_attack_vector(row),
        "affected": affected[:200],
        "severity": detect_severity(row),
        "owasp_llm": sorted(owasp_llm),
        "owasp_asi": sorted(owasp_asi),
        "mitre_atlas": [],
        "references": references,
        "tags": tags,
    }


def main():
    body = download_csv()
    rows = list(csv.reader(io.StringIO(body)))
    print(f"[aiaaic] {len(rows)} raw rows")

    out = []
    skipped = 0
    for row in rows:
        norm = normalize_row(row)
        if norm:
            out.append(norm)
        else:
            skipped += 1

    out_path = INGEST / "aiaaic_sheet_incidents.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[aiaaic] wrote {len(out)} security-relevant entries -> {out_path} (skipped {skipped})")


if __name__ == "__main__":
    main()
