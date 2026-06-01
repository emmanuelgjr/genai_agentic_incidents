"""
Ingest the OECD AI Incidents and Hazards Monitor (AIM) corpus.

Source: https://oecd.ai/en/incidents (Angular SPA)
        Sitemap: https://oecd.ai/sitemaps/incident-monitor-sitemap.xml

Each incident page embeds an Angular `<script id="ng-state">` JSON blob with
the full incident record (title, articles, evidences, concepts, aiid_ids,
location, etc.). We scrape pages concurrently with on-disk caching, filter
to security-relevant entries, and emit one ingest file.

Defaults:
  - Fetches the most recent N URLs from the sitemap (newest first).
  - LIMIT defaults to a few thousand; set OECD_AIM_LIMIT=0 to grab all.
  - Pages cached under ingest/_cache/oecd_aim/ so the script is restartable.

Output: ingest/oecd_aim_full_incidents.json
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from ingest_utils import robust_fetch

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
CACHE = INGEST / "_cache" / "oecd_aim"
CACHE.mkdir(parents=True, exist_ok=True)

SITEMAP_URL = "https://oecd.ai/sitemaps/incident-monitor-sitemap.xml"
USER_AGENT = "Mozilla/5.0 (genai_incidents/1.0; +https://github.com/emmanuelgjr)"

# Default page cap. Override with OECD_AIM_LIMIT=N (0 = unlimited).
DEFAULT_LIMIT = 3000
MAX_WORKERS = 10

# Security-relevant keyword filter applied to title + summary + evidences.
SECURITY_KEYWORDS = (
    "prompt injection prompt-injection jailbreak jailbroken deepfake voice clone "
    "voice cloning data leak data breach leaked exposed exfiltrat ransomware "
    "phishing vishing smishing rce remote code execution command injection "
    "sandbox escape ssrf sql injection deserialization supply chain model theft "
    "model extraction membership inference adversarial evasion poisoning "
    "backdoor scam fraud imperson spoofed spoofing malware trojan worm "
    "vulnerab exploit hack hijack stole stolen theft unauthorized credential "
    "password api key api-key token hallucina misinform disinform election "
    "influence operation propaganda chatbot fake image fake video synthetic "
    "cyberattack cyber attack cybersecurity csam child sexual abuse "
    "bias discriminat surveillance facial recognition biometric privacy "
    "autonomous weapon killer robot wrongful arrest racial profil "
    "child safety self-harm suicide grooming radicalization weaponize "
    "intellectual property copyright"
).split()

KEYWORD_TO_OWASP: list[tuple[str, list[str], list[str], str]] = [
    ("prompt inject", ["LLM01"], ["ASI01"], "prompt-injection"),
    ("jailbreak", ["LLM01"], ["ASI01"], "jailbreak"),
    ("deepfake", ["LLM09"], ["ASI09"], "deepfake"),
    ("voice clone", ["LLM09"], ["ASI09"], "deepfake"),
    ("imperson", ["LLM09"], ["ASI09"], "other"),
    ("data leak", ["LLM02"], ["ASI03"], "data-exfiltration"),
    ("data breach", ["LLM02"], ["ASI03"], "data-exfiltration"),
    ("exfil", ["LLM02"], ["ASI02"], "data-exfiltration"),
    ("ransomware", [], ["ASI05", "ASI10"], "rce"),
    ("phishing", [], ["ASI09"], "other"),
    ("scam", [], ["ASI09"], "other"),
    ("fraud", [], ["ASI09"], "other"),
    ("rce", ["LLM05"], ["ASI05"], "rce"),
    ("remote code execution", ["LLM05"], ["ASI05"], "rce"),
    ("supply chain", ["LLM03"], ["ASI04"], "supply-chain"),
    ("poisoning", ["LLM04"], ["ASI06"], "model-poisoning"),
    ("model theft", ["LLM02"], [], "model-extraction"),
    ("model extraction", ["LLM02"], [], "model-extraction"),
    ("adversarial", [], [], "adversarial-input"),
    ("hallucina", ["LLM09"], [], "other"),
    ("misinform", ["LLM09"], [], "other"),
    ("disinform", ["LLM09"], [], "other"),
    ("propaganda", ["LLM09"], [], "other"),
    ("election", ["LLM09"], [], "other"),
    ("influence operation", ["LLM09"], [], "other"),
    ("csam", ["LLM09"], [], "other"),
    ("child sexual", ["LLM09"], [], "other"),
    ("wrongful arrest", [], [], "other"),
    ("facial recognition", [], [], "other"),
    ("biometric", [], [], "other"),
    ("surveillance", [], [], "other"),
    ("autonomous weapon", [], ["ASI10"], "other"),
    ("self-harm", ["LLM05"], ["ASI09"], "other"),
    ("suicide", ["LLM05"], ["ASI09"], "other"),
    ("racial profil", ["LLM09"], [], "other"),
]


def load_sitemap() -> list[str]:
    print(f"[aim] fetching sitemap {SITEMAP_URL}")
    req = urllib.request.Request(SITEMAP_URL, headers={"User-Agent": USER_AGENT})
    text = urllib.request.urlopen(req, timeout=30).read().decode(
        "utf-8", errors="replace"
    )
    urls = re.findall(r"<loc>([^<]+)</loc>", text)
    # Only /en/incidents/<id> pages, not the landing /en/incidents
    urls = [u for u in urls if re.match(r"https://oecd\.ai/en/incidents/[^/]+$", u)]
    print(f"[aim] sitemap has {len(urls)} incident URLs")
    return urls


def fetch_page(url: str) -> str | None:
    slug = url.rstrip("/").split("/")[-1]
    cache_file = CACHE / f"{slug}.html"
    try:
        data = robust_fetch(url, cache_file, timeout=20, max_retries=3, min_cache_bytes=1000)
        return data[:800_000].decode("utf-8", errors="replace")
    except RuntimeError as e:
        print(f"  ! {slug}: {e}", file=sys.stderr)
        return None


def extract_state(text: str) -> dict | None:
    """Parse the Angular ng-state script JSON blob."""
    m = re.search(
        r'<script[^>]*id="ng-state"[^>]*>(.+?)</script>', text, re.S
    )
    if not m:
        return None
    try:
        state = json.loads(m.group(1))
    except json.JSONDecodeError:
        return None
    for k, v in state.items():
        if not isinstance(v, dict):
            continue
        body = v.get("b")
        if isinstance(body, dict) and body.get("id") and body.get("title"):
            return body
    return None


def collect_text(body: dict) -> str:
    parts = [
        body.get("title") or "",
        body.get("summary") or "",
        " ".join(body.get("evidences") or []),
    ]
    for art in body.get("articles") or []:
        if not isinstance(art, dict):
            continue
        parts.append(art.get("title") or "")
        ev = art.get("evidences") or []
        if isinstance(ev, list):
            parts.append(" ".join(e for e in ev if isinstance(e, str)))
    return " ".join(parts).lower()


def is_security_relevant(text: str) -> bool:
    return any(kw in text for kw in SECURITY_KEYWORDS)


def map_taxonomy(text: str) -> tuple[list[str], list[str], str]:
    llm: set[str] = set()
    asi: set[str] = set()
    attack_vector = "other"
    for kw, l, a, av in KEYWORD_TO_OWASP:
        if kw in text:
            llm.update(l)
            asi.update(a)
            if attack_vector == "other" and av != "other":
                attack_vector = av
    return sorted(llm), sorted(asi), attack_vector


def normalize_body(body: dict, url: str) -> dict | None:
    full_text = collect_text(body)
    if not is_security_relevant(full_text):
        return None

    title = (body.get("title") or "").strip()
    if len(title) < 5:
        return None

    date = (body.get("date") or "").strip()
    year = None
    m = re.match(r"^(\d{4})", date)
    if m:
        year = int(m.group(1))
    if not year:
        # Fall back to URL slug like 2026-03-22-955e
        m = re.search(r"/(\d{4})-(\d{2})-(\d{2})-", url)
        if m:
            year = int(m.group(1))
            date = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    if not year or year < 1980 or year > 2030:
        return None

    summary = body.get("summary") or ""
    if not summary:
        # Use first article's evidences as a description.
        for art in body.get("articles") or []:
            ev = art.get("evidences") or []
            if isinstance(ev, list) and ev:
                summary = " ".join(e for e in ev if isinstance(e, str))[:1000]
                if summary:
                    break
    description = (summary or title).strip()
    if len(description) < 20:
        description = (title + ". " + description).strip()

    llm, asi, attack_vector = map_taxonomy(full_text)

    # Severity heuristic
    sev = "Medium"
    if any(k in full_text for k in ("killed", "death", "fatal", "ransom", "billions", "national security")):
        sev = "Critical"
    elif any(k in full_text for k in ("breach", "stolen", "leaked", "exfil", "rce", "arrest")):
        sev = "High"

    # References: page URL + any article URLs.
    references = [{"title": title, "url": url, "type": "report"}]
    for art in (body.get("articles") or [])[:6]:
        au = (art or {}).get("url")
        at = (art or {}).get("title") or au or "news"
        if au:
            references.append({"title": at[:160], "url": au, "type": "news"})

    company = body.get("company") or []
    if isinstance(company, list):
        affected = ", ".join(c for c in company if isinstance(c, str))[:200]
    elif isinstance(company, str):
        affected = company[:200]
    else:
        affected = ""

    tags = ["oecd-aim"]
    if body.get("is_legacy"):
        tags.append("oecd-legacy")
    aiid_ids = body.get("aiid_ids") or []
    source_ids = [f"OECD-AIM-{body['id']}"]
    if isinstance(aiid_ids, list):
        for a in aiid_ids:
            try:
                source_ids.append(f"AIID-{int(a)}")
            except (TypeError, ValueError):
                pass

    return {
        "source_id": source_ids[0],
        "_extra_source_ids": source_ids[1:],
        "title": title[:300],
        "date": date or str(year),
        "year": year,
        "category": "real-world",
        "description": description[:1500],
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": sev,
        "owasp_llm": llm,
        "owasp_asi": asi,
        "mitre_atlas": [],
        "references": references,
        "tags": tags,
    }


def union_with_existing(fresh: list[dict], existing: list[dict]) -> list[dict]:
    """Union the fresh fetch with the previously-committed ingest file so the
    OECD corpus only ever grows. Keyed by ``source_id`` (``OECD-AIM-<id>``):
    fresh wins on conflict (latest content); entries present only in
    ``existing`` (aged out of the newest-N sitemap window) are kept. Output is
    sorted by ``source_id`` so the committed file has stable, deterministic
    ordering (lexicographic by source_id; OECD ids are date/hash-suffixed strings, not bare integers)."""
    by_id: dict[str, dict] = {}
    for e in existing:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    for e in fresh:
        sid = e.get("source_id")
        if sid:
            by_id[sid] = e
    return sorted(by_id.values(), key=lambda e: e.get("source_id") or "")


def main():
    limit_env = os.environ.get("OECD_AIM_LIMIT", str(DEFAULT_LIMIT))
    try:
        limit = int(limit_env)
    except ValueError:
        limit = DEFAULT_LIMIT
    urls = load_sitemap()
    if limit > 0:
        urls = urls[:limit]
        print(f"[aim] capped to {limit} URLs (set OECD_AIM_LIMIT=0 for all)")

    t0 = time.time()
    pages: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {ex.submit(fetch_page, u): u for u in urls}
        for i, fut in enumerate(as_completed(futures), 1):
            u = futures[fut]
            text = fut.result()
            if text:
                pages[u] = text
            if i % 200 == 0:
                elapsed = time.time() - t0
                rate = i / max(elapsed, 0.001)
                print(f"  fetched {i}/{len(urls)} ({rate:.1f} pages/s)")

    print(f"[aim] fetched {len(pages)}/{len(urls)} pages in {time.time()-t0:.0f}s")

    out = []
    parse_fail = 0
    for url, text in pages.items():
        body = extract_state(text)
        if not body:
            parse_fail += 1
            continue
        norm = normalize_body(body, url)
        if norm:
            # Flatten the extra AIID source_ids back into the array form
            # the merger expects (it reads a single source_id field).
            extras = norm.pop("_extra_source_ids", [])
            if extras:
                norm["extra_source_ids"] = extras
            out.append(norm)

    print(
        f"[aim] parsed: {len(pages) - parse_fail} ok, {parse_fail} unparseable; "
        f"{len(out)} security-relevant kept"
    )

    out_path = INGEST / "oecd_aim_full_incidents.json"
    existing: list[dict] = []
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, OSError):
            existing = []
    merged = union_with_existing(out, existing)
    print(
        f"[aim] union: {len(out)} fetched + {len(existing)} existing "
        f"-> {len(merged)} retained"
    )
    out_path.write_text(
        json.dumps(merged, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"[aim] wrote -> {out_path}")


if __name__ == "__main__":
    main()
