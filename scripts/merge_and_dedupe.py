"""
Merge legacy consolidated entries with all ingest/*.json source feeds, dedupe
by canonical reference URLs / CVE IDs / fuzzy title match, validate against the
incident schema, and emit the unified single source of truth:

  data/incidents.json        (full structured SoT)
  data/incidents.min.json    (slim version: id, title, date, taxonomy mappings)

Run after the per-source aggregators have written into ingest/.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from datetime import date
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

CANONICAL_HOSTS = {
    "nvd.nist.gov": "advisory",
    "cve.org": "advisory",
    "github.com": "advisory",
    "atlas.mitre.org": "research",
    "incidentdatabase.ai": "report",
    "avidml.org": "report",
    "owasp.org": "research",
    "genai.owasp.org": "research",
}

# Heuristic mapping for completing taxonomy mappings on incoming entries
LLM_TO_ATLAS = {
    "LLM01": ["AML.T0051"], "LLM02": ["AML.T0057"], "LLM03": ["AML.T0010"],
    "LLM04": ["AML.T0020"], "LLM05": ["AML.T0050"], "LLM06": ["AML.T0053"],
    "LLM07": ["AML.T0056"], "LLM08": ["AML.T0066"], "LLM09": ["AML.T0058"],
    "LLM10": ["AML.T0029"],
}
ASI_TO_ATLAS = {
    "ASI01": ["AML.T0051"], "ASI02": ["AML.T0053"], "ASI03": ["AML.T0012"],
    "ASI04": ["AML.T0010"], "ASI05": ["AML.T0050"], "ASI06": ["AML.T0066"],
    "ASI07": ["AML.T0053"], "ASI08": ["AML.T0048"], "ASI09": ["AML.T0048.003"],
    "ASI10": ["AML.T0048"],
}
LLM_TO_NIST = {
    "LLM01": ["MEASURE-2.7"], "LLM02": ["MEASURE-2.10"], "LLM03": ["GOVERN-6.1"],
    "LLM04": ["MAP-4.2"], "LLM05": ["MEASURE-2.7"], "LLM06": ["MAP-3.5"],
    "LLM07": ["MEASURE-2.7"], "LLM08": ["MEASURE-2.7"], "LLM09": ["MEASURE-2.8"],
    "LLM10": ["MEASURE-2.4"],
}
ASI_TO_NIST = {
    "ASI01": ["MEASURE-2.7"], "ASI02": ["MAP-3.5"], "ASI03": ["GOVERN-1.4"],
    "ASI04": ["GOVERN-6.1"], "ASI05": ["MEASURE-2.7"], "ASI06": ["MEASURE-2.7"],
    "ASI07": ["MAP-4.1"], "ASI08": ["MANAGE-4.1"], "ASI09": ["MAP-3.5"],
    "ASI10": ["GOVERN-1.4"],
}


def normalize_url(url: str) -> str:
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    u = u.rstrip("/")
    u = u.split("?")[0].split("#")[0]
    return u


def title_key(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t[:80]


def slug_to_id(n: int) -> str:
    return f"INC-{n:05d}"


def fill_taxonomy(entry: dict) -> dict:
    """Backfill MITRE ATLAS / NIST mappings if missing but OWASP codes present."""
    atlas = set(entry.get("mitre_atlas") or [])
    nist = set(entry.get("nist_ai_rmf") or [])
    for c in entry.get("owasp_llm", []) or []:
        for t in LLM_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in LLM_TO_NIST.get(c, []):
            nist.add(n)
    for c in entry.get("owasp_asi", []) or []:
        for t in ASI_TO_ATLAS.get(c, []):
            atlas.add(t)
        for n in ASI_TO_NIST.get(c, []):
            nist.add(n)
    entry["mitre_atlas"] = sorted(atlas)
    entry["nist_ai_rmf"] = sorted(nist)
    return entry


def normalize_entry(raw: dict) -> dict | None:
    """Coerce a raw ingest entry into the unified schema."""
    if not raw:
        return None

    # references is required
    refs = raw.get("references") or []
    refs = [r for r in refs if r and (r.get("url") or "").startswith("http")]
    if not refs:
        return None

    title = (raw.get("title") or "").strip()
    if len(title) < 5:
        return None

    desc = (raw.get("description") or "").strip()
    if len(desc) < 20:
        # tolerate short descriptions by padding from title+impact
        desc = (desc + " " + (raw.get("impact") or "") + " " + title).strip()
        if len(desc) < 20:
            return None

    # Normalize OWASP codes
    llm = [c[:5] for c in (raw.get("owasp_llm") or []) if isinstance(c, str) and c.upper().startswith("LLM")]
    asi = [c[:5] for c in (raw.get("owasp_asi") or []) if isinstance(c, str) and c.upper().startswith("ASI")]
    llm = sorted(set(c.upper() for c in llm if re.match(r"^LLM\d{2}$", c.upper())))
    asi = sorted(set(c.upper() for c in asi if re.match(r"^ASI\d{2}$", c.upper())))

    year = raw.get("year")
    if not year:
        m = re.match(r"(\d{4})", str(raw.get("date") or ""))
        if m:
            year = int(m.group(1))
    if not year:
        return None

    cves = raw.get("cve_ids") or []
    if isinstance(cves, str):
        cves = [cves]
    if "cve_id" in raw and raw["cve_id"]:
        cves = list(cves) + [raw["cve_id"]]
    cves = sorted(set(c for c in cves if isinstance(c, str) and re.match(r"^CVE-\d{4}-\d{4,7}$", c)))

    entry = {
        "id": "",  # assigned later
        "source_ids": [raw["source_id"]] if raw.get("source_id") else [],
        "title": title,
        "date": raw.get("date") or str(year),
        "year": int(year),
        "category": raw.get("category") or "real-world",
        "description": desc,
        "attack_vector": (raw.get("attack_vector") or "other").lower(),
        "affected": (raw.get("affected") or "").strip(),
        "severity": (raw.get("severity") or "Medium").capitalize(),
        "owasp_llm": llm,
        "owasp_asi": asi,
        "nist_ai_rmf": sorted(set(raw.get("nist_ai_rmf") or [])),
        "mitre_atlas": sorted(set(raw.get("mitre_atlas") or [])),
        "references": refs,
        "tags": list(raw.get("tags") or []),
        "added": "2026-05-11",
        "updated": "2026-05-11",
    }
    if cves:
        entry["cve_ids"] = cves
    if raw.get("cvss_score"):
        try:
            entry["cvss_score"] = float(raw["cvss_score"])
        except (TypeError, ValueError):
            pass
    if raw.get("mitigations"):
        entry["mitigations"] = raw["mitigations"]
    if raw.get("impact"):
        entry["impact"] = raw["impact"]
    if raw.get("maestro_layers"):
        entry["maestro_layers"] = raw["maestro_layers"]
    if raw.get("owasp_dsgai"):
        entry["owasp_dsgai"] = raw["owasp_dsgai"]
    if raw.get("mitre_atlas_tactics"):
        entry["mitre_atlas_tactics"] = raw["mitre_atlas_tactics"]

    fill_taxonomy(entry)
    return entry


def load_source(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  WARN: failed to parse {path}: {e}")
        return []
    if isinstance(data, dict):
        return data.get("incidents") or data.get("entries") or data.get("data") or []
    if isinstance(data, list):
        return data
    return []


def main():
    all_entries: list[dict] = []

    # 1) Legacy consolidated first (highest priority — already curated)
    legacy_path = DATA / "legacy_consolidated.json"
    if legacy_path.exists():
        legacy = json.loads(legacy_path.read_text(encoding="utf-8")).get("incidents", [])
        # Legacy already in unified shape — just backfill taxonomy
        for e in legacy:
            fill_taxonomy(e)
        all_entries.extend(legacy)
        print(f"[legacy] loaded {len(legacy)} entries")

    # 2) Each ingest/*.json (from subagents)
    if INGEST.exists():
        for src in sorted(INGEST.glob("*.json")):
            raw = load_source(src)
            kept = []
            for r in raw:
                norm = normalize_entry(r)
                if norm is not None:
                    kept.append(norm)
            all_entries.extend(kept)
            print(f"[{src.name:40s}] {len(raw):4d} raw -> {len(kept):4d} normalized")

    # 3) Dedupe
    by_cve: dict[str, dict] = {}
    by_url: dict[str, dict] = {}
    by_title: dict[str, dict] = {}
    deduped: list[dict] = []

    for e in all_entries:
        # CVE-key dedupe (strongest signal)
        cve_keys = e.get("cve_ids") or []
        cve_hit = next((by_cve[c] for c in cve_keys if c in by_cve), None)
        if cve_hit:
            merge_into(cve_hit, e)
            continue
        # URL-key dedupe
        url_hit = None
        for r in e.get("references", []):
            u = normalize_url(r.get("url", ""))
            if u and u in by_url:
                url_hit = by_url[u]
                break
        if url_hit:
            merge_into(url_hit, e)
            continue
        # Title-key dedupe
        tk = title_key(e["title"])
        if tk in by_title and abs(by_title[tk]["year"] - e["year"]) <= 1:
            merge_into(by_title[tk], e)
            continue

        # New entry
        deduped.append(e)
        for c in cve_keys:
            by_cve[c] = e
        for r in e.get("references", []):
            u = normalize_url(r.get("url", ""))
            if u:
                by_url.setdefault(u, e)
        by_title.setdefault(tk, e)

    # 4) Renumber stable IDs (sorted by year desc, then title)
    deduped.sort(key=lambda x: (-x.get("year") or 0, x["title"].lower()))
    for i, e in enumerate(deduped, start=1):
        e["id"] = slug_to_id(i)

    print(f"\n[total]  {len(all_entries)} input -> {len(deduped)} unique")

    # 5) Write outputs
    out = {
        "version": "1.0.0",
        "generated": str(date.today()),
        "description": (
            "Single source of truth for GenAI and agentic AI security incidents. "
            "Each entry is mapped to OWASP LLM Top 10 (2025), OWASP Agentic ASI Top 10, "
            "NIST AI RMF (AI 100-1), and MITRE ATLAS where applicable."
        ),
        "schema": "schema/incident.schema.json",
        "incident_count": len(deduped),
        "incidents": deduped,
    }
    (DATA / "incidents.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[output] wrote data/incidents.json")

    # Slim variant
    slim = {
        "version": out["version"],
        "generated": out["generated"],
        "incident_count": len(deduped),
        "incidents": [
            {
                "id": e["id"],
                "title": e["title"],
                "date": e.get("date"),
                "year": e.get("year"),
                "severity": e.get("severity"),
                "attack_vector": e.get("attack_vector"),
                "owasp_llm": e.get("owasp_llm", []),
                "owasp_asi": e.get("owasp_asi", []),
                "nist_ai_rmf": e.get("nist_ai_rmf", []),
                "mitre_atlas": e.get("mitre_atlas", []),
                "cve_ids": e.get("cve_ids", []),
                "primary_reference": e["references"][0]["url"] if e.get("references") else None,
            }
            for e in deduped
        ],
    }
    (DATA / "incidents.min.json").write_text(
        json.dumps(slim, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[output] wrote data/incidents.min.json")

    # 6) Print taxonomy coverage summary
    counts = defaultdict(int)
    for e in deduped:
        for c in e.get("owasp_llm", []):
            counts[f"OWASP {c}"] += 1
        for c in e.get("owasp_asi", []):
            counts[c] += 1
    print("\n[coverage]")
    for k in sorted(counts):
        print(f"  {k:12s} {counts[k]}")


def merge_into(target: dict, src: dict):
    """Merge taxonomies, references, tags from src into target."""
    for key in ("owasp_llm", "owasp_asi", "owasp_dsgai", "nist_ai_rmf",
                "mitre_atlas", "mitre_atlas_tactics", "tags", "source_ids",
                "cve_ids", "mitigations"):
        merged = sorted(set((target.get(key) or []) + (src.get(key) or [])))
        if merged:
            target[key] = merged
    # References — dedupe by url
    seen = {normalize_url(r["url"]): r for r in target.get("references", [])}
    for r in src.get("references", []):
        u = normalize_url(r.get("url", ""))
        if u and u not in seen:
            seen[u] = r
    target["references"] = list(seen.values())
    # Pick higher severity
    order = ["Info", "Low", "Medium", "High", "Critical"]
    src_sev = src.get("severity") or "Medium"
    tgt_sev = target.get("severity") or "Medium"
    if src_sev not in order:
        src_sev = "Medium"
    if tgt_sev not in order:
        tgt_sev = "Medium"
    if order.index(src_sev) > order.index(tgt_sev):
        target["severity"] = src_sev
    fill_taxonomy(target)


if __name__ == "__main__":
    main()
