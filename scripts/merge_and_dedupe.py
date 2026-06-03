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
MAPPINGS = ROOT / "mappings"
DATA.mkdir(parents=True, exist_ok=True)


def _load_atlas_technique_tactics() -> dict[str, list[str]]:
    """technique-id -> [tactic-id, ...] from the committed ATLAS reference."""
    try:
        m = json.loads((MAPPINGS / "mitre_atlas.json").read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return {}
    return {tid: e["tactics"] for tid, e in (m.get("techniques") or {}).items()
            if isinstance(e, dict) and e.get("tactics")}


_ATLAS_TECHNIQUE_TACTICS = _load_atlas_technique_tactics()

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

# Seed a framework mapping from the attack_vector for entries that arrive
# with no OWASP/NIST/ATLAS at all. Security exploits (and OWASP's own
# LLM09 "Misinformation" category) map to OWASP LLM codes, which then
# cascade through fill_taxonomy() to ATLAS + NIST. Societal-harm vectors
# (privacy, bias, CSAM, self-harm) have no clean OWASP fit, so they seed
# the appropriate NIST AI RMF control directly.
_VECTOR_TO_OWASP_LLM = {
    "prompt-injection": ["LLM01"], "indirect-prompt-injection": ["LLM01"], "jailbreak": ["LLM01"],
    "data-exfiltration": ["LLM02"], "info-disclosure": ["LLM02"],
    "membership-inference": ["LLM02"], "model-inversion": ["LLM02"],
    "supply-chain": ["LLM03"],
    "model-poisoning": ["LLM04"], "memory-poisoning": ["LLM04"], "backdoor": ["LLM04"],
    "rce": ["LLM05"], "xss": ["LLM05"], "sql-injection": ["LLM05"],
    "command-injection": ["LLM05"], "ssrf": ["LLM05"], "path-traversal": ["LLM05"],
    "deserialization": ["LLM05"],
    "agent-hijack": ["LLM06"], "tool-abuse": ["LLM06"],
    "misinformation": ["LLM09"], "hallucination": ["LLM09"], "deepfake": ["LLM09"],
    "dos": ["LLM10"], "model-extraction": ["LLM10"], "model-theft": ["LLM10"],
}
_VECTOR_TO_NIST_SEED = {
    "privacy-violation": ["MAP-4.1", "MEASURE-2.10"],
    "algorithmic-bias": ["MEASURE-2.11"],
    "csam-generation": ["MEASURE-2.6"],
    "unsafe-advice": ["MEASURE-2.6"],
    "adversarial-input": ["MEASURE-2.7"],
    "evasion": ["MEASURE-2.7"],
}
_VECTOR_TO_ATLAS_SEED = {
    "adversarial-input": ["AML.T0015"],
    "evasion": ["AML.T0015"],
}


def seed_frameworks_from_vector(entry: dict) -> None:
    """Seed OWASP/NIST/ATLAS from the (finalized) attack_vector, but only for
    entries that have no framework mapping at all. Never overrides an existing
    mapping; the seeded OWASP code then cascades through fill_taxonomy()."""
    if (entry.get("owasp_llm") or entry.get("owasp_asi")
            or entry.get("mitre_atlas") or entry.get("nist_ai_rmf")):
        return
    av = (entry.get("attack_vector") or "").strip()
    llm = _VECTOR_TO_OWASP_LLM.get(av)
    if llm:
        entry["owasp_llm"] = list(llm)
    nist = _VECTOR_TO_NIST_SEED.get(av)
    if nist:
        entry["nist_ai_rmf"] = sorted(set((entry.get("nist_ai_rmf") or []) + list(nist)))
    atlas = _VECTOR_TO_ATLAS_SEED.get(av)
    if atlas:
        entry["mitre_atlas"] = sorted(set((entry.get("mitre_atlas") or []) + list(atlas)))


def normalize_url(url: str) -> str:
    if not url:
        return ""
    u = url.strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    u = u.split("?")[0].split("#")[0]
    u = u.rstrip("/")
    return u


def title_key(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9]+", " ", t).strip()
    t = re.sub(r"\s+", " ", t)
    return t[:80]


def slug_to_id(n: int) -> str:
    return f"INC-{n:05d}"


_ATTACK_VECTOR_NORMALIZE: dict[str, str] = {
    "supply": "supply-chain",
    "prompt": "prompt-injection",
    "direct": "prompt-injection",
    "indirect": "indirect-prompt-injection",
    "adversarial": "adversarial-input",
    "poisoning": "model-poisoning",
    "membership": "membership-inference",
    "agent": "agent-hijack",
    "credential": "auth-bypass",
    "authentication": "auth-bypass",
    "oauth": "auth-bypass",
    "hardcoded": "auth-bypass",
    "insecure": "auth-bypass",
    "cross": "xss",
    "code": "rce",
    "fraud": "deepfake",
    "no": "other",
    "not": "other",
    "multi": "other",
    "mass": "other",
    "ai": "other",
    "data": "other",
    "self": "other",
    "real": "other",
    "harmful": "other",
    "json": "other",
    "dual": "other",
    "zero": "other",
    "training": "other",
    "autonomous": "other",
    "persistent": "other",
    "user": "other",
    "infrastructure": "other",
    "multimodal": "other",
    "corpus": "other",
    "gradual": "other",
    "design": "other",
    "documents": "other",
    "maximum": "other",
    "systemic": "other",
    "knowledge": "other",
    "mcp": "other",
    "100–256": "other",
}

# Keyword -> attack_vector classifier. Order matters: first hit wins.
# Used to replace the catch-all "other" on entries that have no explicit
# attack_vector field but whose title/description contains an obvious one.
_ATTACK_VECTOR_RULES: list[tuple[str, str]] = [
    (r"indirect[\s-]*prompt", "indirect-prompt-injection"),
    (r"prompt[\s-]*inject", "prompt-injection"),
    (r"jailbreak|jailbroken", "jailbreak"),
    (r"deepfake|voice clon|face swap|face[\s-]*generat", "deepfake"),
    (r"impersonat|fake (?:ceo|cfo|executive|employee)|vishing", "deepfake"),
    (r"command injection|cmd injection|os command", "command-injection"),
    (r"path traversal|directory traversal|\\.\\./", "path-traversal"),
    (r"\bSSRF\b|server[\s-]*side request forgery", "ssrf"),
    (r"\bSQL\b injection|sqli\b", "sql-injection"),
    (r"\bXSS\b|cross[\s-]*site scripting", "xss"),
    (r"\bRCE\b|remote code execution|sandbox escape", "rce"),
    (r"arbitrary code|code execution|arbitrary command", "rce"),
    (r"deserializ|insecure deserial", "deserialization"),
    (r"auth(?:entication|orization)? bypass|missing auth|improper auth", "auth-bypass"),
    (r"hardcoded (?:key|secret|credential|password|token)", "auth-bypass"),
    (r"data exfil|exfiltrat|data breach|data leak", "data-exfiltration"),
    (r"model theft|model extract", "model-extraction"),
    (r"model invers", "model-inversion"),
    (r"membership inference", "membership-inference"),
    (r"adversarial (?:example|input|patch|attack)|evasion attack", "adversarial-input"),
    (r"data poisoning|backdoor|model poisoning", "model-poisoning"),
    (r"memory poison|context poison|rag[\s-]*poison|corpus[\s-]*poison", "memory-poisoning"),
    (r"agent (?:goal )?hijack|goal hijack", "agent-hijack"),
    (r"tool (?:misuse|abuse)|plugin compromise", "tool-abuse"),
    (r"supply[\s-]*chain|typosquat|malicious package|dependency confusion", "supply-chain"),
    (r"denial[\s-]*of[\s-]*service|\bDoS\b|\bDDoS\b|resource[\s-]*exhaust", "dos"),
    (r"info(?:rmation)?[\s-]*disclos|sensitive data exposure", "info-disclosure"),
    (r"insider threat|insider attack", "insider"),
    (r"hallucina|confabula", "hallucination"),
    (r"misinform|disinform", "misinformation"),
    (r"phishing|spear[\s-]*phish|smishing", "phishing"),
    (r"ransomware|ransom[\s-]*attack", "ransomware"),
    (r"malware|trojan|worm", "malware"),
    (r"(?:privacy|surveillance)[\s-]*(?:violat|breach|invasion)", "privacy-violation"),
    (r"bias(?:ed)?[\s-]*(?:algorithm|model|output|decision)", "algorithmic-bias"),
    # AI-harm vectors. These run after the security rules above, so an entry
    # is only labelled with a harm vector when no security exploit matched —
    # this is what pulls the AIAAIC ai-harm corpus out of the "other" bucket.
    # Patterns are deliberately high-precision (demographic/decision context
    # for bias, generative-AI context for misinformation, etc.) so a fuzzy
    # keyword in a description doesn't mislabel a record.
    (r"\bcsam\b|\bcsae\b|child sexual abuse|child (?:porn|sexual abuse)"
     r"|sexualis\w+ (?:a |the )?(?:child|minor)"
     r"|ai[\s-]generated .{0,20}(?:child|minor).{0,12}(?:sexual|porn|nude|abuse)"
     r"|generat\w+ .{0,24}child (?:porn|sexual)"
     r"|nudif\w+ .{0,20}(?:child|minor|student|girl|teen)"
     r"|(?:sexual|nude|explicit|pornographic) .{0,30}minors?\b"
     r"|minors?\b.{0,20}(?:sexual abuse|sexual image|explicit image|nude image|porn)",
     "csam-generation"),
    (r"\bsuicid\w+|self[\s-]harm|encourag\w+ .{0,20}(?:suicide|self-harm|kill)"
     r"|incit\w+ .{0,20}(?:self-harm|violence|suicide|terror)|bomb[\s-]?making"
     r"|how to (?:make|build|create|synthesize) .{0,20}(?:bomb|weapon|explosive|nerve agent|meth)"
     r"|coach\w* .{0,15}suicide|promot\w+ .{0,10}(?:suicide|self-harm|eating disorder)",
     "unsafe-advice"),
    (r"deepfake|voice clon\w+|face[\s-]?swap\w*|nudif\w+"
     r"|ai[\s-]generated (?:nude|porn|explicit|intimate|sexual)"
     r"|synthetic (?:nude|porn|intimate)"
     r"|non[\s-]consensual (?:intimate|sexual|nude|porn)|fake nude",
     "deepfake"),
    (r"facial recognition|mass surveillance"
     r"|biometric (?:surveillance|tracking|database|data|privacy|information)"
     r"|covert(?:ly)? .{0,12}(?:record|track|monitor|surveil)|location tracking"
     r"|scrap\w+ .{0,24}(?:faces|photos|profiles|personal data|biometric)"
     r"|secretly (?:record|collect|track|monitor)|invasive .{0,10}surveillance",
     "privacy-violation"),
    (r"\b(?:racial|racism|gender|sexis\w+|ethnic|caste|religious|disabilit\w+|\bage\b|demographic) "
     r"(?:bias|discriminat\w+|stereotyp\w+)"
     r"|discriminat\w+ (?:against|based on|toward|by)|biased against"
     r"|\bbias(?:ed)?\b.{0,30}(?:hiring|recruit|loan|credit|sentenc|arrest|police|policing|grading|admission|healthcare|transplant|welfare|mortgage|housing|insurance)"
     r"|perpetuat\w+ .{0,18}(?:racial|gender|sexis|racis|stereotype|inequal)",
     "algorithmic-bias"),
    (r"defam\w+|\blibel\w*|\bslander"
     r"|fabricat\w+ .{0,20}(?:quote|stor|claim|source|case|citation|legal)"
     r"|false (?:legal )?citation|hallucinat\w+ .{0,20}(?:case|citation|source|legal)"
     r"|made[\s-]up .{0,12}(?:case|citation|legal)"
     r"|(?:chatbot|chatgpt|\bai\b|\bllm\b|gemini|copilot|\bbard\b|grok) .{0,40}(?:false (?:claim|information|accusation)|spread\w* (?:false|misinfo))",
     "misinformation"),
]


_VALID_SEVERITIES = ("Critical", "High", "Medium", "Low", "Info")


# Sources we consider "auto-ingested" — present in bulk feeds but not
# individually vetted by a maintainer. Anything else (legacy/, hand-curated
# JSON, researcher-blog ingest) starts as "reviewed".
def _classify_quality_tier(entry: dict) -> str:
    """Heuristic quality tier:

      - ``curated``  — legacy hand-written entries (always source_id LEGACY-*),
        or entries with a populated `mitigations` list and >=2 source_ids.
      - ``reviewed`` — sourced from a maintained research catalogue
        (ATLAS, AIID hand-pick, OWASP, AVID, AIRI, researcher blogs), a
        hand-picked AIAAIC slug entry, or an NVD-analyst-scored CVE.
      - ``auto``     — bulk-ingested from the NVD CVE feed (unscored), the
        AIAAIC numeric sheet, OECD AIM, promptfoo, or garak.
    """
    src_ids = entry.get("source_ids") or []
    if any(s.startswith("LEGACY-") for s in src_ids):
        return "curated"
    if entry.get("mitigations") and len(src_ids) >= 2:
        return "curated"
    has_curated_source = any(
        s.startswith(("ATLAS-", "AIID-", "AVID-", "OWASP-", "RES-", "EXT-", "OECD-",
                      "USENIX-", "NDSS-", "CCS-", "ARXIV-", "INC-", "VTR-"))
        for s in src_ids
    )
    # Hand-picked AIAAIC entries use slug IDs (AIAAIC-<slug>); the bulk sheet
    # uses numeric IDs (AIAAIC<n>). Only the numeric bulk form is "auto".
    has_aiaaic_slug = any(re.match(r"^AIAAIC-[a-z]", s) for s in src_ids)
    if has_curated_source or has_aiaaic_slug:
        return "reviewed"
    # NVD assigns CVSS/CWE to CVEs — that analyst scoring is catalogue review,
    # so a CVSS-scored CVE is "reviewed". Unscored/raw CVE pulls stay "auto".
    if any(s.startswith("CVE-") for s in src_ids) and entry.get("cvss_score") is not None:
        return "reviewed"
    has_bulk = any(
        s.startswith(("OECD-AIM-", "CVE-", "PROMPTFOO-", "GARAK-")) or re.match(r"^AIAAIC\d", s)
        for s in src_ids
    )
    if has_bulk:
        return "auto"
    return "reviewed"


# Tag rules that move an entry to the `ai-harm` corpus instead of the
# default `security` corpus. The split is deliberate: a deepfake fraud is
# `security`; a hiring-algorithm-discriminates story is `ai-harm`.
_AI_HARM_KEYWORDS = (
    "discriminat", "racial bias", "gender bias", "hiring algorithm",
    "wrongful arrest", "wrongful denial", "credit scoring", "welfare benefit",
    "social scoring", "predictive policing", "biased recommendation",
    "biased recidivism", "biased loan", "biased medical", "algorithmic bias",
    "fairness", "demographic parity",
)
_SECURITY_KEYWORDS_FOR_CORPUS = (
    "deepfake", "voice clone", "voice-clone", "prompt inject", "jailbreak",
    "exfil", "data breach", "data leak", "rce", "remote code execution",
    "command injection", "ssrf", "supply chain", "supply-chain", "csam",
    "malware", "ransomware", "phishing", "scam", "fraud", "exploit", "cve-",
    "vulnerability", "auth bypass", "sandbox escape", "poisoning", "backdoor",
)


def _classify_corpus(entry: dict) -> str:
    """`security` or `ai-harm`. Security wins ties — a deepfake scam is
    a security incident even if it also has a fairness angle."""
    if entry.get("cve_ids"):
        return "security"
    text = (
        (entry.get("title") or "")
        + " "
        + (entry.get("description") or "")
        + " "
        + " ".join(entry.get("tags") or [])
    ).lower()
    has_security = any(kw in text for kw in _SECURITY_KEYWORDS_FOR_CORPUS)
    if has_security:
        return "security"
    has_harm = any(kw in text for kw in _AI_HARM_KEYWORDS)
    if has_harm:
        return "ai-harm"
    return "security"


def _normalise_severity(value: object) -> str:
    """Coerce assorted severity inputs (None, 'None', '', invalid strings)
    into a schema-valid value. Defaults to Medium."""
    if value is None:
        return "Medium"
    s = str(value).strip().capitalize()
    if s in _VALID_SEVERITIES:
        return s
    return "Medium"


def classify_attack_vector(text: str) -> str | None:
    """Return the first matching attack vector keyword, or None."""
    if not text:
        return None
    lower = text.lower()
    for pattern, vec in _ATTACK_VECTOR_RULES:
        if re.search(pattern, lower, re.I):
            return vec
    return None


# CVE-style titles like "A flaw has been found in X." get rewritten when we
# can identify the affected product + a vulnerability class. The full
# original sentence stays in the description.
_CVE_TITLE_PREFIXES = (
    "A flaw has been found in ",
    "A vulnerability has been found in ",
    "A vulnerability was detected in ",
    "A security flaw has been discovered in ",
    "A security flaw has been found in ",
    "A weakness has been identified in ",
    "A weakness was discovered in ",
)


def maybe_rewrite_cve_title(entry: dict) -> None:
    """Rewrite generic CVE/product-blurb titles into '<product> — <vector> (CVE-...)'.

    Handles two common shapes coming out of NVD/GHSA:
      1. "A flaw has been found in X up to 3.4."   → boilerplate prefix
      2. "X is an open-source Python package..."    → product description blurb
    A single canonical title makes title-key dedup actually work for the
    same-product/same-year cluster of CVEs.
    """
    title = (entry.get("title") or "").strip()
    cve_ids = entry.get("cve_ids") or []
    cve_suffix = f" ({cve_ids[0]})" if cve_ids else ""
    vec = entry.get("attack_vector") or "other"
    if vec == "other":
        vec = classify_attack_vector(entry.get("description") or title) or "vulnerability"
    pretty_vec = vec.replace("-", " ").title()

    body: str | None = None

    # Shape 1: boilerplate CVE prefix.
    for p in _CVE_TITLE_PREFIXES:
        if title.startswith(p):
            body = title[len(p):]
            break

    # Shape 2: "<Product> is a/an <description>." — extract the product name.
    if body is None:
        m = re.match(
            r"^([A-Za-z0-9@/_+.\-]{2,40}(?:\s+[A-Za-z0-9@/_+.\-]{1,20}){0,3})\s+is\s+(?:a|an|the)\s+",
            title,
        )
        if m and cve_ids:
            # Only rewrite product blurbs when we have a CVE to anchor on —
            # otherwise we'd be inventing a vague title with no provenance.
            body = m.group(1)
            entry["title"] = f"{body.strip()} — {pretty_vec}{cve_suffix}"[:200]
            return

    if body is None:
        return

    product = re.split(
        r"\s+up to\s+|\s+versions? prior to\s+|\s+before\s+|[.,;]", body, maxsplit=1
    )[0].strip()
    if not product or len(product) > 80:
        return
    entry["title"] = f"{product} — {pretty_vec}{cve_suffix}"[:200]


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
    # Derive ATLAS tactics from the (final) technique set — subtechniques
    # (AML.Txxxx.yyy) inherit their parent technique's tactics.
    tactics = set(entry.get("mitre_atlas_tactics") or [])
    for t in atlas:
        tac = _ATLAS_TECHNIQUE_TACTICS.get(t)
        if not tac and t.count(".") >= 2:  # subtechnique AML.Txxxx.yyy -> parent
            tac = _ATLAS_TECHNIQUE_TACTICS.get(t.rsplit(".", 1)[0])
        if tac:
            tactics.update(tac)
    if tactics:
        entry["mitre_atlas_tactics"] = sorted(tactics)
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

    def _clean(s: str) -> str:
        """Strip stray carriage returns and collapse runs of whitespace.
        Some NVD CVE descriptions carry literal ``\\r\\n`` sequences from
        the source HTML; keeping them produces mixed line endings in the
        rendered markdown and confuses the CI drift check."""
        return re.sub(r"\s+", " ", (s or "").replace("\r", " ")).strip()

    title = _clean(raw.get("title"))
    if len(title) < 5:
        return None

    desc = _clean(raw.get("description"))
    if len(desc) < 20:
        # tolerate short descriptions by padding from title+impact
        desc = _clean(desc + " " + (raw.get("impact") or "") + " " + title)
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
    cves = sorted(set(c for c in cves if isinstance(c, str) and re.match(r"^CVE-\d{4}-\d{4,9}$", c)))

    # source IDs may arrive as a single `source_id` string OR as a
    # `source_ids` array (some ingest scripts emit multiple upstream IDs
    # per row, e.g. OECD AIM rows that cross-reference AIID).
    src_ids: list[str] = []
    if raw.get("source_id"):
        src_ids.append(raw["source_id"])
    if isinstance(raw.get("source_ids"), list):
        src_ids.extend(s for s in raw["source_ids"] if isinstance(s, str))
    if isinstance(raw.get("extra_source_ids"), list):
        src_ids.extend(s for s in raw["extra_source_ids"] if isinstance(s, str))
    # Canonicalise: `AIID-1234-OECD` (from the legacy OECD bridge file) and
    # `AIID-1234` (from scrape_aiid + ingest_oecd_aim) reference the same
    # AIID incident — collapse to a single canonical form so dedup matches.
    src_ids = [
        re.sub(r"^AIID-(\d+)-OECD$", r"AIID-\1", s) for s in src_ids
    ]

    raw_vec = (raw.get("attack_vector") or "").lower().strip()
    raw_vec = _ATTACK_VECTOR_NORMALIZE.get(raw_vec, raw_vec)
    if not raw_vec or raw_vec == "other":
        classified = classify_attack_vector((title or "") + " " + (desc or ""))
        if classified:
            raw_vec = classified
        else:
            raw_vec = "other"

    entry = {
        "id": "",  # assigned later
        "source_ids": sorted(set(src_ids)),
        "title": title,
        "date": raw.get("date") or str(year),
        "year": int(year),
        "category": raw.get("category") or "real-world",
        "description": desc,
        "attack_vector": raw_vec,
        "affected": (raw.get("affected") or "").strip(),
        "severity": _normalise_severity(raw.get("severity")),
        "owasp_llm": llm,
        "owasp_asi": asi,
        "nist_ai_rmf": sorted(set(raw.get("nist_ai_rmf") or [])),
        "mitre_atlas": sorted(set(raw.get("mitre_atlas") or [])),
        "references": refs,
        "tags": list(raw.get("tags") or []),
        # added/updated stamped in main() after dedupe, using the previous
        # output as the source of truth for `added` so CI runs stay stable.
        "added": raw.get("added") or "",
        "updated": raw.get("updated") or "",
    }
    if cves:
        entry["cve_ids"] = cves
    cwes_raw = raw.get("cwe_ids") or raw.get("cwe") or []
    if isinstance(cwes_raw, str):
        cwes_raw = [cwes_raw]
    cwes = sorted(
        {
            c.upper()
            for c in cwes_raw
            if isinstance(c, str) and re.match(r"^CWE-\d{1,4}$", c.upper())
        }
    )
    if cwes:
        entry["cwe_ids"] = cwes
    if raw.get("cvss_score"):
        try:
            entry["cvss_score"] = float(raw["cvss_score"])
        except (TypeError, ValueError):
            pass
    if isinstance(raw.get("cvss_vector"), str) and raw["cvss_vector"].startswith("CVSS:"):
        entry["cvss_vector"] = raw["cvss_vector"]
    # Surface the canonical AIID numeric id as a first-class field when we
    # have one (either explicitly, or parsed from an AIID-<n> source_id).
    aiid_id = raw.get("aiid_id")
    if not aiid_id:
        for sid in src_ids:
            m = re.match(r"^AIID-(\d+)$", sid)
            if m:
                aiid_id = int(m.group(1))
                break
    if aiid_id:
        try:
            entry["aiid_id"] = int(aiid_id)
        except (TypeError, ValueError):
            pass
    if isinstance(raw.get("disclosure_date"), str) and re.match(
        r"^\d{4}(-\d{2}(-\d{2})?)?$", raw["disclosure_date"]
    ):
        entry["disclosure_date"] = raw["disclosure_date"]
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
    maybe_rewrite_cve_title(entry)
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


DEPRECATIONS_PATH = DATA / "id_deprecations.json"
CURATION_OVERRIDES_PATH = DATA / "curation_overrides.json"


def _load_curation_overrides() -> dict[str, dict]:
    """Load explicit, durable curation decisions keyed by source_id.

    Format: ``{"overrides": {"<source_id>": {"quality_tier": "reviewed",
    "severity": "High", "_note": "..."}, ...}}``. These are human/assisted
    review decisions that override the heuristic classifiers and survive
    rebuilds. Keys starting with ``_`` (e.g. ``_note``) are metadata and are
    not written onto the entry.
    """
    if not CURATION_OVERRIDES_PATH.exists():
        return {}
    try:
        raw = json.loads(CURATION_OVERRIDES_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return raw.get("overrides", {}) if isinstance(raw, dict) else {}


def _load_prev_incidents() -> list[dict]:
    """Read the previously-published incidents list (empty if none yet)."""
    prev_path = DATA / "incidents.json"
    if not prev_path.exists():
        return []
    try:
        data = json.loads(prev_path.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return []
    return data.get("incidents", []) if isinstance(data, dict) else []


def _load_deprecated_ids() -> set[str]:
    """Ids that were explicitly retired via merge/dedupe. These must never be
    resurrected by retention."""
    if not DEPRECATIONS_PATH.exists():
        return set()
    try:
        deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return set()
    if not isinstance(deprec, dict):
        return set()
    return {d.get("from") for d in deprec.get("deprecations", []) if d.get("from")}


def load_retained_priors(
    prev_incidents: list[dict], deprecated_ids: set[str]
) -> list[dict]:
    """Return previously-published incidents eligible for retention: all priors
    that have an id and were NOT explicitly deprecated. This applies only the
    deprecation filter; the caller (the step 6c top-up in main) decides which of
    these the fresh build no longer covers and appends those verbatim."""
    out: list[dict] = []
    for e in prev_incidents:
        eid = e.get("id")
        if not eid or eid in deprecated_ids:
            continue
        out.append(e)
    return out


def _load_prev_state() -> tuple[
    dict[str, tuple[str, str, dict]],
    dict[str, str],
    int,
]:
    """Read the previous output so the build can:

      - Preserve `added` and gate `updated` (timestamps).
      - Reuse stable `id` strings via CVE / source_id keys.
      - Carry the monotonic ID counter forward so freshly-introduced rows
        get IDs above every ID we've ever used.

    Returns ``(timestamps, id_by_key, next_id)``.
    """
    timestamps: dict[str, tuple[str, str, dict]] = {}
    id_by_key: dict[str, str] = {}
    next_id = 1
    prev_path = DATA / "incidents.json"
    if not prev_path.exists():
        return timestamps, id_by_key, next_id
    try:
        prev = json.loads(prev_path.read_text(encoding="utf-8")).get("incidents", [])
    except (json.JSONDecodeError, OSError):
        return timestamps, id_by_key, next_id
    seen_ids = set()
    for e in prev:
        added = e.get("added") or ""
        updated = e.get("updated") or added
        snap = _content_snapshot(e)
        eid = e.get("id", "")
        if eid:
            seen_ids.add(eid)
            for c in e.get("cve_ids") or []:
                id_by_key.setdefault(c, eid)
            for s in e.get("source_ids") or []:
                id_by_key.setdefault(s, eid)
        if not added:
            continue
        for c in e.get("cve_ids") or []:
            timestamps.setdefault(c, (added, updated, snap))
        for s in e.get("source_ids") or []:
            timestamps.setdefault(s, (added, updated, snap))
    # Also walk previously-tombstoned IDs so we never accidentally reuse one.
    if DEPRECATIONS_PATH.exists():
        try:
            deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8"))
            for dep in deprec.get("deprecations", []):
                seen_ids.add(dep.get("from", ""))
        except (json.JSONDecodeError, OSError):
            pass
    max_n = 0
    for i in seen_ids:
        m = re.match(r"^INC-(\d+)$", i)
        if m:
            max_n = max(max_n, int(m.group(1)))
    next_id = max_n + 1
    return timestamps, id_by_key, next_id


# Backwards-compatibility shim — earlier code paths read just the timestamps.
def _load_prev_timestamps() -> dict[str, tuple[str, str, dict]]:
    return _load_prev_state()[0]


# Fields that count as "content" for the purposes of bumping `updated`.
# `references` is intentionally included so that gaining a new news link
# bumps the timestamp, but `added`/`updated` themselves obviously do not.
_CONTENT_FIELDS = (
    "title", "date", "year", "category", "description", "attack_vector",
    "affected", "impact", "severity", "owasp_llm", "owasp_asi", "owasp_dsgai",
    "nist_ai_rmf", "mitre_atlas", "mitre_atlas_tactics", "cve_ids", "cwe_ids",
    "cvss_score", "cvss_vector", "aiid_id", "disclosure_date",
    "mitigations", "references", "tags",
)


def _content_snapshot(entry: dict) -> dict:
    """Return a hashable-equivalent snapshot of the entry's content fields."""
    snap = {}
    for k in _CONTENT_FIELDS:
        v = entry.get(k)
        if isinstance(v, list):
            # Sort lists so cosmetic reordering doesn't bump updated.
            try:
                snap[k] = sorted(
                    v,
                    key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False),
                )
            except TypeError:
                snap[k] = v
        else:
            snap[k] = v
    return snap


def _apply_history(entry: dict, prev_ts: dict[str, tuple[str, str, dict]]) -> None:
    """Look up the entry's previous timestamps by any matching CVE/source ID
    and apply them. Bump `updated` only when content actually changed."""
    today = str(date.today())
    keys = list(entry.get("cve_ids") or []) + list(entry.get("source_ids") or [])
    prev = next((prev_ts[k] for k in keys if k in prev_ts), None)
    if prev is None:
        # Brand-new row — stamp it with today's date.
        entry["added"] = entry.get("added") or today
        entry["updated"] = today
        return
    prev_added, prev_updated, prev_snap = prev
    entry["added"] = prev_added
    if _content_snapshot(entry) == prev_snap:
        entry["updated"] = prev_updated
    else:
        entry["updated"] = today


def main():
    # 0) Load the previous output: timestamps, the id-by-key map (so stable
    #    INC-* IDs survive a rebuild), and the monotonic ID counter.
    prev_ts, prev_id_by_key, next_id = _load_prev_state()

    all_entries: list[dict] = []

    # 1) Legacy consolidated first (highest priority — already curated)
    legacy_path = DATA / "legacy_consolidated.json"
    if legacy_path.exists():
        legacy = json.loads(legacy_path.read_text(encoding="utf-8")).get("incidents", [])
        # Legacy already in unified shape — backfill taxonomy and stamp a
        # synthetic source_id on entries that never had one (table-parsed
        # rows from the original markdown trackers).
        for e in legacy:
            fill_taxonomy(e)
            if not e.get("source_ids"):
                slug = e.get("id") or e.get("title", "legacy")
                e["source_ids"] = [f"LEGACY-{slug}"]
            maybe_rewrite_cve_title(e)
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
    by_src: dict[str, dict] = {}
    deduped: list[dict] = []

    def _reindex(target: dict) -> None:
        """Refresh every dedup index for ``target`` after a merge. If a key
        (CVE / source_id / reference URL) already maps to a *different*
        previously-deduped entry, that other entry is transitively absorbed
        into ``target`` and tombstoned so we don't end up with two records
        for what is really one incident."""

        def _claim(idx: dict, key: str) -> None:
            other = idx.get(key)
            if other is None:
                idx[key] = target
                return
            if other is target or other.get("_tombstoned"):
                idx[key] = target
                return
            # Transitive merge: pull other's content into target and retire it.
            merge_into(target, other)
            other["_tombstoned"] = True
            idx[key] = target

        for c in target.get("cve_ids") or []:
            _claim(by_cve, c)
        for s in target.get("source_ids") or []:
            _claim(by_src, s)
        for r in target.get("references", []) or []:
            u = normalize_url(r.get("url", ""))
            if u:
                _claim(by_url, u)

    for e in all_entries:
        # CVE-key dedupe (strongest signal)
        cve_keys = e.get("cve_ids") or []
        cve_hit = next((by_cve[c] for c in cve_keys if c in by_cve), None)
        if cve_hit:
            merge_into(cve_hit, e)
            _reindex(cve_hit)
            continue
        # Source-ID dedupe (e.g. AIID-1234 referenced from both AIID scrape
        # and OECD AIM's aiid_ids cross-reference).
        src_keys = e.get("source_ids") or []
        src_hit = next((by_src[s] for s in src_keys if s in by_src), None)
        if src_hit:
            merge_into(src_hit, e)
            _reindex(src_hit)
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
            _reindex(url_hit)
            continue
        # Title-key dedupe
        tk = title_key(e["title"])
        if tk in by_title and abs(by_title[tk]["year"] - e["year"]) <= 1:
            merge_into(by_title[tk], e)
            _reindex(by_title[tk])
            continue

        # New entry
        deduped.append(e)
        _reindex(e)
        by_title.setdefault(tk, e)

    # 4) Drop entries that got transitively absorbed during reindex, but
    #    record their old IDs so old citations can be resolved.
    surviving: list[dict] = []
    tombstones: list[dict] = []  # [{from, into, reason, date}, ...]
    today_str = str(date.today())
    for e in deduped:
        if e.pop("_tombstoned", False):
            tombstones.append(e)
        else:
            surviving.append(e)

    # 4b) Finalize attack_vector (normalize fragments + reclassify "other")
    #     BEFORE stamping history. attack_vector is part of the content
    #     snapshot, so finalizing it afterwards would make _apply_history
    #     compare a stale value against the previous output and spuriously
    #     bump `updated` (and therefore `generated`) on every rebuild —
    #     breaking the drift check whenever CI runs on a later calendar day.
    for e in surviving:
        vec = (e.get("attack_vector") or "other").lower().strip()
        vec = _ATTACK_VECTOR_NORMALIZE.get(vec, vec)
        if not vec or vec == "other":
            classified = classify_attack_vector(
                (e.get("title") or "") + " " + (e.get("description") or "")
            )
            vec = classified or "other"
        e["attack_vector"] = vec

    # 4c) Backfill framework mappings for entries that arrived with no
    #     OWASP/NIST/ATLAS at all, seeding from the now-final attack_vector
    #     (then cascading OWASP -> ATLAS/NIST via fill_taxonomy). Runs before
    #     history stamping so the seeded mappings are part of the snapshot.
    for e in surviving:
        seed_frameworks_from_vector(e)
        fill_taxonomy(e)

    # 4d) Apply curation overrides (durable human/assisted review decisions)
    #     before history stamping, so overridden content fields are part of
    #     the snapshot and an override-set quality_tier is respected in step 5.
    curation = _load_curation_overrides()
    if curation:
        applied = 0
        for e in surviving:
            ov = next((curation[s] for s in (e.get("source_ids") or []) if s in curation), None)
            if ov:
                for k, v in ov.items():
                    if not k.startswith("_"):
                        e[k] = v
                applied += 1
        print(f"[curation] applied {applied} override(s) from {CURATION_OVERRIDES_PATH.name}")

    # 5) Apply stable timestamps + classifiers (quality_tier, corpus).
    for e in surviving:
        _apply_history(e, prev_ts)
        # Respect any explicit value the source carried; only classify
        # when the entry doesn't already declare one.
        if not e.get("quality_tier"):
            e["quality_tier"] = _classify_quality_tier(e)
        if not e.get("corpus"):
            e["corpus"] = _classify_corpus(e)

    # 6) Assign stable INC-* IDs. Reuse the previous ID for any entry whose
    #    CVE / source_id appeared before; otherwise allocate from the
    #    monotonic counter that survives across builds.
    deprecations_new: list[dict] = []
    used_ids: set[str] = set()
    for e in surviving:
        keys = list(e.get("cve_ids") or []) + list(e.get("source_ids") or [])
        old_id = next((prev_id_by_key[k] for k in keys if k in prev_id_by_key), None)
        # If multiple previous IDs collide into one new row, keep the
        # smallest and record the rest as deprecations pointing at the
        # survivor — this protects citations of merged-away IDs.
        ids_seen = sorted({prev_id_by_key[k] for k in keys if k in prev_id_by_key})
        chosen = ids_seen[0] if ids_seen else None
        if chosen and chosen not in used_ids:
            e["id"] = chosen
            used_ids.add(chosen)
        else:
            e["id"] = slug_to_id(next_id)
            used_ids.add(e["id"])
            next_id += 1
        for extra in ids_seen[1:]:
            if extra != e["id"]:
                deprecations_new.append(
                    {"from": extra, "into": e["id"], "reason": "merged", "date": today_str}
                )

    # 6b) Record entries that lost a fight to a transitive merge.
    for ts_entry in tombstones:
        # Find which surviving entry absorbed it via shared CVE/source_id.
        keys = list(ts_entry.get("cve_ids") or []) + list(ts_entry.get("source_ids") or [])
        target_id = next(
            (s["id"] for s in surviving if (set(s.get("cve_ids") or []) | set(s.get("source_ids") or [])) & set(keys)),
            None,
        )
        if not target_id:
            continue
        old_id = next((prev_id_by_key[k] for k in keys if k in prev_id_by_key), None)
        if old_id and old_id != target_id:
            deprecations_new.append(
                {"from": old_id, "into": target_id, "reason": "transitive-merge", "date": today_str}
            )

    # 6c) Retention top-up: restore previously-published incidents that the
    #     fresh build no longer covers (their upstream source dropped them), so
    #     the dataset is archival and never silently loses an incident. A prior
    #     is restored only if it was not explicitly deprecated AND none of its
    #     source_ids / cve_ids are already represented in the fresh build. It is
    #     carried VERBATIM — keeping its id / added / updated and bypassing
    #     dedupe — because re-feeding already-built records through the
    #     raw-ingest dedupe is non-idempotent (it re-canonicalises and can
    #     oscillate). See docs/superpowers/specs/2026-06-01-retain-on-drop-design.md
    covered_keys: set[str] = set()
    for e in surviving:
        covered_keys.update(e.get("cve_ids") or [])
        covered_keys.update(e.get("source_ids") or [])
    eligible = load_retained_priors(_load_prev_incidents(), _load_deprecated_ids())
    carried = 0
    no_keys = 0
    for prior in eligible:
        pid = prior.get("id")
        keys = set(prior.get("cve_ids") or []) | set(prior.get("source_ids") or [])
        if not keys:
            # No source_id/cve_id anchor → can't test coverage. This should
            # never happen for committed output (normalize_entry rejects keyless
            # rows), so surface it loudly rather than dropping it silently.
            no_keys += 1
            continue
        if (keys & covered_keys) or pid in used_ids:
            continue
        surviving.append(prior)
        covered_keys.update(keys)
        used_ids.add(pid)
        carried += 1
    print(f"[retention] carried {carried}/{len(eligible)} eligible prior(s) no longer in any source")
    if no_keys:
        print(f"[retention] WARNING: {no_keys} eligible prior(s) had no source_id/cve_id and could not be retained")

    deduped = surviving

    print(f"\n[total]  {len(all_entries)} input -> {len(deduped)} unique")

    # 7) Compute `generated`: today only if anything actually changed since
    #    the previous output; otherwise preserve the previous timestamp so
    #    CI drift checks don't flap on every daily re-run.
    today = str(date.today())
    any_change = any((e.get("updated") or "") == today for e in deduped)
    prev_generated = ""
    try:
        prev_generated = (
            json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
            .get("generated", "")
        )
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        prev_generated = ""
    generated = today if any_change or not prev_generated else prev_generated

    # 8) Merge deprecations with the on-disk history and persist.
    prev_deprec: list[dict] = []
    if DEPRECATIONS_PATH.exists():
        try:
            prev_deprec = json.loads(DEPRECATIONS_PATH.read_text(encoding="utf-8")).get(
                "deprecations", []
            )
        except (json.JSONDecodeError, OSError):
            prev_deprec = []
    # Dedupe: keep the earliest record for each `from` id (preserves history).
    seen_from = {d.get("from"): d for d in prev_deprec if d.get("from")}
    for d in deprecations_new:
        seen_from.setdefault(d["from"], d)
    deprecations_all = sorted(
        seen_from.values(),
        key=lambda x: (x.get("from") or "", x.get("date") or ""),
    )
    if deprecations_all:
        DEPRECATIONS_PATH.write_text(
            json.dumps(
                {"deprecations": deprecations_all},
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
            newline="\n",
        )
        print(f"[output] wrote {DEPRECATIONS_PATH.name} ({len(deprecations_all)} entries)")

    # 9) Write outputs
    out = {
        "version": "2.1.0",
        "generated": generated,
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
        json.dumps(out, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
    )
    print(f"[output] wrote data/incidents.json")

    # Slim variant — used by the static site for filtering and inline
    # row expansion. Description is truncated so the JSON stays under
    # ~5 MB, the soft limit for snappy first-paint over typical home
    # broadband, while still showing enough context to triage an entry.
    def _short(text: str, limit: int = 280) -> str:
        text = (text or "").strip()
        if len(text) <= limit:
            return text
        cut = text[: limit - 1]
        # Don't break a word mid-token.
        sp = cut.rfind(" ")
        if sp > limit * 0.6:
            cut = cut[:sp]
        return cut.rstrip() + "…"

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
                "description": _short(e.get("description")),
                "affected": _short(e.get("affected"), limit=120),
                "tags": (e.get("tags") or [])[:8],
                "quality_tier": e.get("quality_tier"),
                "corpus": e.get("corpus"),
            }
            for e in deduped
        ],
    }
    (DATA / "incidents.min.json").write_text(
        json.dumps(slim, indent=2, ensure_ascii=False),
        encoding="utf-8",
        newline="\n",
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
                "cve_ids", "cwe_ids", "mitigations"):
        merged = sorted(set((target.get(key) or []) + (src.get(key) or [])))
        if merged:
            target[key] = merged
    # Single-value fields: take src's value when target doesn't have one.
    for key in ("cvss_vector", "aiid_id", "disclosure_date", "impact"):
        if not target.get(key) and src.get(key):
            target[key] = src[key]
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
    # Prefer the more specific / more plausible date.
    # Specificity: YYYY-MM-DD > YYYY-MM > YYYY. A future-year date should be
    # overridden by a same-or-earlier date from any other source.
    current_year = date.today().year
    src_date = (src.get("date") or "").strip()
    tgt_date = (target.get("date") or "").strip()

    def _date_score(d: str) -> tuple[int, int]:
        if re.match(r"^\d{4}-\d{2}-\d{2}", d):
            return (3, int(d[:4]))
        if re.match(r"^\d{4}-\d{2}", d):
            return (2, int(d[:4]))
        if re.match(r"^\d{4}", d):
            return (1, int(d[:4]))
        return (0, 0)

    src_score, src_year = _date_score(src_date)
    tgt_score, tgt_year = _date_score(tgt_date)
    tgt_future = tgt_year > current_year
    src_future = src_year > current_year
    if src_score and (
        (tgt_future and not src_future)
        or (not tgt_future and src_score > tgt_score and not src_future)
    ):
        target["date"] = src_date
        target["year"] = src_year or target.get("year")
    fill_taxonomy(target)


if __name__ == "__main__":
    main()
