"""
ingest_cve_nvd_expanded.py
==========================

Pulls AI / ML / LLM / agentic-AI related CVEs from:
  1. NVD REST API 2.0  (https://services.nvd.nist.gov/rest/json/cves/2.0)
  2. GitHub Security Advisory Database (via `gh api graphql`)
  3. OSV.dev (https://api.osv.dev/v1/query) for ecosystem package scans

Output: ingest/cve_nvd_expanded.json

Schema (per entry):
  source_id, cve_id, title, date, year, category, description,
  attack_vector, affected, severity, cvss_score,
  owasp_llm[], owasp_asi[], nist_ai_rmf[], mitre_atlas[],
  references[{title,url,type}], tags[]

The script is restartable: it caches each NVD keyword response as a JSON file
under ingest/_cache/nvd/<slug>.json so re-runs don't re-hammer NVD.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"
CACHE_NVD = INGEST / "_cache" / "nvd"
CACHE_GHSA = INGEST / "_cache" / "ghsa"
CACHE_OSV = INGEST / "_cache" / "osv"
for d in (CACHE_NVD, CACHE_GHSA, CACHE_OSV):
    d.mkdir(parents=True, exist_ok=True)

OUT_FILE = INGEST / "cve_nvd_expanded.json"


# ----------------------------------------------------------------------------
# Keyword list for NVD scans (expanded set covering AI/ML/LLM/agent ecosystem)
# ----------------------------------------------------------------------------
NVD_KEYWORDS = [
    "LLM",
    "large language model",
    "language model",
    "AI agent",
    "agentic",
    "prompt injection",
    "MCP server",
    "Model Context Protocol",
    "retrieval augmented",
    "Hugging Face",
    "transformers",
    "LangChain",
    "LlamaIndex",
    "vLLM",
    "MLflow",
    "Ray",
    "Triton inference",
    "ONNX",
    "PyTorch",
    "TensorFlow",
    "Ollama",
    "AnythingLLM",
    "Flowise",
    "AutoGen",
    "CrewAI",
    "Cursor",
    "Copilot",
    "Codeium",
    "n8n",
    "Dify",
    "ChromaDB",
    "Pinecone",
    "Weaviate",
    "Qdrant",
    "Milvus",
    "Gradio",
    "Streamlit",
    "Jupyter",
    "ComfyUI",
    "Automatic1111",
    "Stable Diffusion",
    "Open WebUI",
    "vector database",
    "embeddings server",
    "Bentoml",
    "Kubeflow",
    "SageMaker",
    "Vertex AI",
    "OpenAI",
    "Anthropic",
    "Gemini",
    "Claude",
    "ChatGPT",
    "GPT-4",
    "fine-tuning",
    "model serving",
    "neural network",
    "machine learning",
    "deep learning",
    "Llama",
    # Expanded 2026-06: high-CVE-count AI/ML products missing above.
    "Langflow",
    "LiteLLM",
    "LangGraph",
    "Rasa",
    "NeMo",
    "DeepSpeed",
    "InvokeAI",
    "text-generation-webui",
    "llama.cpp",
    "GPT4All",
    "LocalAI",
    "LibreChat",
    "text generation inference",
    "SGLang",
    "LMDeploy",
    "TensorRT-LLM",
    "OpenVINO",
    "DeepSeek",
    "Mistral",
    "Qwen",
    "pgvector",
    "FAISS",
    "Haystack",
    "Semantic Kernel",
    "PrivateGPT",
    "AutoGPT",
    "MetaGPT",
    "Label Studio",
    "ZenML",
    "ClearML",
    "Weights & Biases",
]

# AI / ML / LLM context filters - a CVE is kept only if its description or
# CPE entries match at least one of these tokens (case-insensitive).
AI_CONTEXT_TOKENS = [
    "llm", "language model", "language-model", "agent", "agentic", "prompt",
    "ai ", " ai-", "artificial intelligence", "machine learning", "ml ",
    "deep learning", "neural", "transformer", "embedding", "vector store",
    "vector database", "rag ", "retrieval-augmented", "retrieval augmented",
    "huggingface", "hugging face", "langchain", "llamaindex", "vllm",
    "mlflow", "kubeflow", "bentoml", "ray.io", "ray serve", "triton",
    "tensorflow", "pytorch", "onnx", "ollama", "anythingllm", "flowise",
    "autogen", "crewai", "n8n", "dify", "chromadb", "pinecone", "weaviate",
    "qdrant", "milvus", "gradio", "comfyui", "automatic1111", "stable diffusion",
    "open webui", "openwebui", "ollama", "mcp ", "model context protocol",
    "openai", "anthropic", "claude", "chatgpt", "gpt-", "llama", "mistral",
    "cursor", "copilot", "codeium", "cody", "sourcegraph", "fine-tuning",
    "model serving", "inference server", "ai-driven", "ai assistant",
    "ai chatbot", "ai chat", "generative ai", "genai", "foundation model",
    # Expanded 2026-06.
    "langflow", "litellm", "langgraph", "rasa", "nemo", "deepspeed",
    "invokeai", "text-generation-webui", "llama.cpp", "llama-cpp", "gpt4all",
    "localai", "librechat", "text generation inference", "sglang", "lmdeploy",
    "tensorrt-llm", "tensorrt", "openvino", "deepseek", "qwen", "pgvector",
    "faiss", "haystack", "semantic kernel", "semantic-kernel", "privategpt",
    "autogpt", "metagpt", "label studio", "label-studio", "zenml", "clearml",
    "weights & biases", "wandb", "diffusers", "litserve", "guardrails",
]


# ----------------------------------------------------------------------------
# Vendors / products we should *always* include when a CPE references them,
# even if the description text wouldn't otherwise pass the AI-context filter.
# (Lower-cased substrings matched against `cpe23Uri`.)
# ----------------------------------------------------------------------------
AI_PRODUCT_CPE_FRAGMENTS = [
    "langchain", "llamaindex", "vllm", "mlflow", "ray_project", "bentoml",
    "huggingface", "hugging_face", "ollama", "anythingllm", "flowise",
    "autogen", "crewai", "comfyui", "automatic1111", "stable-diffusion",
    "stable_diffusion", "open-webui", "open_webui", "openwebui",
    "chromadb", "weaviate", "qdrant", "milvus", "pinecone",
    "transformers", "pytorch", "tensorflow", "onnxruntime", "onnx",
    "triton-inference-server", "triton_inference_server", "kubeflow",
    "h2oai", "deepjavalibrary", "bigscience", "modelscope", "litellm",
    "lobehub", "lobe-chat", "lobechat", "dify", "n8n",
    "sourcegraph", "cursor", "github_copilot", "codeium", "cody",
    "openai", "anthropic", "google", "deepset", "haystack",
    "label_studio", "labelstud.io", "label-studio", "binplist", "joblib",
    "scikit-learn", "scikit_learn", "tensorflow_serving",
    # Expanded 2026-06.
    "langflow", "langgraph", "rasa", "deepspeed", "invokeai",
    "text-generation-webui", "llama.cpp", "llama_cpp", "gpt4all", "localai",
    "librechat", "sglang", "lmdeploy", "tensorrt", "openvino", "deepseek",
    "qwen", "pgvector", "faiss", "semantic-kernel", "privategpt", "autogpt",
    "metagpt", "zenml", "clearml", "wandb", "diffusers", "litserve",
    "guardrails_ai", "guardrails-ai", "vertexai", "sagemaker",
]


# ----------------------------------------------------------------------------
# Mapping heuristics
# ----------------------------------------------------------------------------
ATTACK_VECTOR_PATTERNS = [
    ("prompt-injection", [r"prompt injection", r"indirect prompt", r"jailbreak"]),
    ("deserialization", [
        r"deserialization", r"deserialize", r"unsafe pickle",
        r"pickle\.load", r"yaml\.load", r"unsafe yaml", r"unmarshal",
        r"insecure deserialization",
    ]),
    ("ssrf", [r"server.?side request forgery", r"\bssrf\b"]),
    ("sql-injection", [r"sql injection", r"\bsqli\b"]),
    ("command-injection", [
        r"command injection", r"os command", r"shell injection",
        r"argument injection", r"argument-injection",
    ]),
    ("path-traversal", [
        r"path traversal", r"directory traversal", r"\.\./\.\.", r"zip slip",
        r"arbitrary file read", r"arbitrary file write",
        r"arbitrary file overwrite",
    ]),
    ("xss", [r"cross.?site scripting", r"\bxss\b", r"stored xss", r"reflected xss"]),
    ("auth-bypass", [
        r"authentication bypass", r"auth bypass", r"missing authentication",
        r"improper authentication", r"improper authorization",
        r"access control",
    ]),
    ("sandbox-escape", [
        r"sandbox escape", r"sandbox bypass", r"escape the sandbox",
        r"container escape",
    ]),
    ("info-disclosure", [
        r"information disclosure", r"information exposure",
        r"sensitive information", r"information leak", r"data leak",
    ]),
    ("rce", [
        r"remote code execution", r"\brce\b", r"arbitrary code",
        r"arbitrary command", r"code execution", r"command execution",
    ]),
]


def infer_attack_vector(description: str) -> str:
    d = (description or "").lower()
    # Order matters - check prompt-injection / deserialization before generic rce.
    for vec, patterns in ATTACK_VECTOR_PATTERNS:
        for p in patterns:
            if re.search(p, d):
                return vec
    return "other"


def map_owasp_and_atlas(description: str, attack_vector: str):
    """Return (owasp_llm[], owasp_asi[], mitre_atlas[])."""
    d = (description or "").lower()
    llm = ["LLM03"]   # default: AI supply chain
    asi = ["ASI04"]
    atlas: list[str] = []

    if attack_vector == "rce":
        llm.append("LLM05"); asi.append("ASI05"); atlas.append("AML.T0050")
    if attack_vector == "deserialization":
        llm.append("LLM05"); asi.append("ASI05"); atlas += ["AML.T0010.001", "AML.T0050"]
    if attack_vector == "prompt-injection":
        llm = ["LLM01", "LLM05"]; asi = ["ASI01", "ASI05"]; atlas.append("AML.T0051")
    if attack_vector in ("ssrf", "path-traversal"):
        llm.append("LLM05"); asi.append("ASI05")
        if attack_vector == "ssrf":
            atlas.append("AML.T0049")
    if attack_vector == "command-injection":
        llm.append("LLM05"); asi.append("ASI05"); atlas.append("AML.T0050")
    if attack_vector == "auth-bypass":
        asi.append("ASI03")
    if attack_vector == "info-disclosure":
        llm.append("LLM02"); asi.append("ASI02")
        atlas.append("AML.T0024")
    if attack_vector == "sandbox-escape":
        llm.append("LLM05"); asi.append("ASI05"); atlas.append("AML.T0050")
    if attack_vector == "xss":
        llm.append("LLM05"); asi.append("ASI05")
    if attack_vector == "sql-injection":
        llm.append("LLM05"); asi.append("ASI05")

    if "credential" in d or "api key" in d or "secret" in d or "token leak" in d:
        if "ASI03" not in asi:
            asi.append("ASI03")
    if "training data" in d or "data poisoning" in d or "dataset" in d:
        if "LLM04" not in llm:
            llm.append("LLM04")
        if "ASI04" not in asi:
            asi.append("ASI04")
        atlas.append("AML.T0020")
    if "model" in d and ("poison" in d or "backdoor" in d):
        atlas.append("AML.T0018")

    return sorted(set(llm)), sorted(set(asi)), sorted(set(atlas))


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


# ----------------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------------
def http_get(url: str, headers: dict | None = None, retries: int = 4, sleep_base: float = 6.0):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers or {"User-Agent": "ai-incidents-ingest/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last_err = e
            wait = sleep_base * (attempt + 1)
            print(f"  [warn] GET {url[:120]}... failed ({e}); retry in {wait:.0f}s", flush=True)
            time.sleep(wait)
    raise RuntimeError(f"GET {url} failed after {retries} attempts: {last_err}")


def http_post_json(url: str, payload: dict, headers: dict | None = None, retries: int = 3):
    data = json.dumps(payload).encode("utf-8")
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json",
                         "User-Agent": "ai-incidents-ingest/1.0", **(headers or {})},
            )
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(4 * (attempt + 1))
    raise RuntimeError(f"POST {url} failed: {last_err}")


# ----------------------------------------------------------------------------
# NVD fetch
# ----------------------------------------------------------------------------
NVD_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"
NVD_PAGE = 2000
# NVD rate limits: 5 req / 30s without an API key, 50 req / 30s with one.
# Request a free key at https://nvd.nist.gov/developers/request-an-api-key
NVD_API_KEY = os.environ.get("NVD_API_KEY", "").strip()
NVD_SLEEP = 0.7 if NVD_API_KEY else 6.5


def fetch_nvd_keyword(keyword: str) -> list[dict]:
    """Fetch ALL pages for one NVD keyword query, with on-disk cache."""
    cache_file = CACHE_NVD / f"{slugify(keyword)}.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text("utf-8"))
            if isinstance(cached, list):
                print(f"  [cache] {keyword}: {len(cached)} CVEs", flush=True)
                return cached
        except Exception:  # noqa: BLE001
            pass

    print(f"  [nvd]   {keyword}: querying...", flush=True)
    headers = {"User-Agent": "ai-incidents-ingest/1.0"}
    if NVD_API_KEY:
        headers["apiKey"] = NVD_API_KEY
    all_items: list[dict] = []
    start = 0
    while True:
        params = {
            "keywordSearch": keyword,
            "resultsPerPage": NVD_PAGE,
            "startIndex": start,
        }
        url = f"{NVD_URL}?{urllib.parse.urlencode(params)}"
        try:
            data = http_get(url, headers=headers)
        except RuntimeError as e:
            print(f"  [warn] giving up on {keyword}: {e}", flush=True)
            break
        vulns = data.get("vulnerabilities", []) or []
        all_items.extend(vulns)
        total = data.get("totalResults", 0)
        start += NVD_PAGE
        if start >= total or not vulns:
            break
        time.sleep(NVD_SLEEP)

    # Pace between keyword queries too — the limit is a rolling 30s window
    # across all requests, not per keyword.
    time.sleep(NVD_SLEEP)
    cache_file.write_text(json.dumps(all_items), encoding="utf-8")
    print(f"  [nvd]   {keyword}: {len(all_items)} CVEs cached", flush=True)
    return all_items


# ----------------------------------------------------------------------------
# Convert one NVD vulnerability record -> our schema
# ----------------------------------------------------------------------------
def nvd_to_record(v: dict) -> dict | None:
    cve = v.get("cve") or v
    cve_id = cve.get("id")
    if not cve_id:
        return None

    # English description
    descr = ""
    for d in cve.get("descriptions", []) or []:
        if d.get("lang") == "en":
            descr = d.get("value") or ""
            break
    if not descr:
        return None

    # CPE strings (for vendor/product filter)
    cpes: list[str] = []
    for cfg in cve.get("configurations", []) or []:
        for node in cfg.get("nodes", []) or []:
            for m in node.get("cpeMatch", []) or []:
                c = m.get("criteria")
                if c:
                    cpes.append(c.lower())

    # AI-relevance filter
    descr_l = descr.lower()
    cpe_blob = " ".join(cpes)
    has_token = any(tok in descr_l for tok in AI_CONTEXT_TOKENS)
    has_product = any(frag in cpe_blob for frag in AI_PRODUCT_CPE_FRAGMENTS)
    if not (has_token or has_product):
        return None

    # CVSS - prefer v3.1, then v3.0, then v2
    cvss_score = None
    cvss_vector = None
    severity = None
    metrics = cve.get("metrics", {}) or {}
    for key in ("cvssMetricV31", "cvssMetricV30", "cvssMetricV2"):
        if metrics.get(key):
            m0 = metrics[key][0]
            cdata = m0.get("cvssData", {}) or {}
            cvss_score = cdata.get("baseScore") or m0.get("baseScore")
            cvss_vector = cdata.get("vectorString")
            severity = (cdata.get("baseSeverity") or m0.get("baseSeverity")
                        or m0.get("cvssData", {}).get("baseSeverity"))
            if severity:
                severity = severity.title()
            break

    # CWE ids from the NVD `weaknesses` block (CWE-NNN, skipping NVD-CWE-noinfo).
    cwe_ids = sorted({
        d.get("value") for w in (cve.get("weaknesses") or [])
        for d in (w.get("description") or [])
        if (d.get("value") or "").startswith("CWE-")
    })
    if not severity and cvss_score is not None:
        # Fall back to thresholds.
        if cvss_score >= 9.0:
            severity = "Critical"
        elif cvss_score >= 7.0:
            severity = "High"
        elif cvss_score >= 4.0:
            severity = "Medium"
        else:
            severity = "Low"
    severity = severity or "Medium"

    # Dates
    published = cve.get("published") or ""
    year = None
    date_str = ""
    if published:
        date_str = published[:7]
        try:
            year = int(published[:4])
        except ValueError:
            year = None
    if not year:
        m = re.match(r"CVE-(\d{4})-", cve_id)
        if m:
            year = int(m.group(1))

    # Affected (best-effort)
    affected = ""
    if cpes:
        # take a unique vendor/product summary
        seen = set()
        parts = []
        for c in cpes:
            try:
                bits = c.split(":")
                vendor = bits[3]
                product = bits[4]
            except IndexError:
                continue
            key = f"{vendor}/{product}"
            if key in seen:
                continue
            seen.add(key)
            parts.append(key)
            if len(parts) >= 4:
                break
        affected = ", ".join(parts)

    # References
    refs = [{"title": "NVD", "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}", "type": "advisory"}]
    seen_urls = {refs[0]["url"]}
    for r in cve.get("references", []) or []:
        u = r.get("url")
        if not u or u in seen_urls:
            continue
        seen_urls.add(u)
        tags = [t.lower() for t in (r.get("tags") or [])]
        if "vendor advisory" in tags:
            rtype = "vendor"
        elif "patch" in tags:
            rtype = "patch"
        elif "exploit" in tags:
            rtype = "exploit"
        elif "third party advisory" in tags:
            rtype = "advisory"
        else:
            rtype = "reference"
        refs.append({"title": r.get("source") or u, "url": u, "type": rtype})
        if len(refs) >= 6:
            break

    # Attack vector + mapping
    attack_vector = infer_attack_vector(descr)
    owasp_llm, owasp_asi, atlas = map_owasp_and_atlas(descr, attack_vector)

    # Title - 1-line synopsis (first sentence, truncated)
    first = re.split(r"(?<=[.!?])\s+", descr.strip(), maxsplit=1)[0]
    if len(first) > 180:
        first = first[:177] + "..."
    title = first or cve_id

    # Tags
    tags = ["cve", "nvd"]
    if attack_vector and attack_vector != "other":
        tags.append(attack_vector)
    for frag in AI_PRODUCT_CPE_FRAGMENTS:
        if frag in cpe_blob:
            tags.append(frag.replace("_", "-").replace(".", "-"))
            if len(tags) >= 8:
                break
    if not any(t for t in tags if t not in ("cve", "nvd")):
        # fall back to description-derived keyword tags
        for tok in ("langchain", "llamaindex", "vllm", "mlflow", "ollama",
                    "anythingllm", "flowise", "autogen", "huggingface",
                    "transformers", "pytorch", "tensorflow", "onnx",
                    "comfyui", "open-webui", "n8n", "dify"):
            if tok in descr_l:
                tags.append(tok)

    return {
        "source_id": cve_id,
        "cve_id": cve_id,
        "title": title,
        "date": date_str,
        "year": year,
        "category": "vulnerability-disclosure",
        "description": descr.strip(),
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": severity,
        "cvss_score": cvss_score,
        "cvss_vector": cvss_vector,
        "cwe_ids": cwe_ids,
        "owasp_llm": owasp_llm,
        "owasp_asi": owasp_asi,
        "nist_ai_rmf": [],
        "mitre_atlas": atlas,
        "references": refs,
        "tags": sorted(set(tags)),
    }


# ----------------------------------------------------------------------------
# GHSA fetch (via gh CLI)
# ----------------------------------------------------------------------------
GHSA_QUERY = """
query($after: String) {
  securityAdvisories(first: 100, classifications: %s, after: $after, orderBy: {field: PUBLISHED_AT, direction: DESC}) {
    nodes {
      ghsaId
      summary
      description
      publishedAt
      severity
      cvss { score vectorString }
      cwes(first: 10) { nodes { cweId } }
      identifiers { type value }
      references { url }
      vulnerabilities(first: 10) { nodes { package { ecosystem name } } }
    }
    pageInfo { endCursor hasNextPage }
  }
}
"""


def fetch_ghsa(max_pages: int = 400, classification: str = "GENERAL") -> list[dict]:
    """
    Fetch recent GHSA advisories via `gh api graphql`. We page through
    until `max_pages` pages or until the publish date drops below 2022
    (older advisories are unlikely to be AI/agentic). ``max_pages`` is set
    high enough that the 2022 date floor — not the page cap — is what stops
    paging, so coverage is complete back to 2022 rather than truncated at
    the newest N. ``classification`` is GENERAL (CVE-style advisories) or
    MALWARE (malicious-package advisories, e.g. AI typosquats).
    """
    cache_file = CACHE_GHSA / f"advisories_{classification.lower()}.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text("utf-8"))
            if isinstance(cached, list):
                print(f"  [cache] ghsa/{classification}: {len(cached)} advisories", flush=True)
                return cached
        except Exception:  # noqa: BLE001
            pass

    query = GHSA_QUERY % classification
    all_nodes: list[dict] = []
    cursor: str | None = None
    for page in range(max_pages):
        after_arg = ["-f", f"after={cursor}"] if cursor else []
        cmd = ["gh", "api", "graphql", "-f", f"query={query}", *after_arg]
        try:
            # encoding= matters: text=True alone decodes with the locale
            # codec (cp1252 on Windows) and UnicodeDecodeErrors on UTF-8
            # advisory text, silently yielding 0 advisories.
            out = subprocess.run(cmd, capture_output=True, text=True,
                                 encoding="utf-8", errors="replace", timeout=90)
        except FileNotFoundError:
            print("  [warn] gh CLI not available; skipping GHSA", flush=True)
            return []
        if out.returncode != 0:
            print(f"  [warn] gh GHSA call failed: {out.stderr[:200]}", flush=True)
            break
        try:
            data = json.loads(out.stdout)
        except Exception as e:  # noqa: BLE001
            print(f"  [warn] GHSA JSON parse failed: {e}", flush=True)
            break
        adv = (data.get("data") or {}).get("securityAdvisories") or {}
        nodes = adv.get("nodes") or []
        all_nodes.extend(nodes)
        page_info = adv.get("pageInfo") or {}
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        # Stop early if we've already paged into pre-2022 advisories.
        if nodes and nodes[-1].get("publishedAt", "")[:4] < "2022":
            break
        time.sleep(1.5)
        if (page + 1) % 5 == 0:
            print(f"  [ghsa/{classification}] page {page + 1}: total {len(all_nodes)}", flush=True)

    cache_file.write_text(json.dumps(all_nodes), encoding="utf-8")
    print(f"  [ghsa/{classification}] fetched {len(all_nodes)} advisories", flush=True)
    return all_nodes


AI_ECOSYSTEM_PACKAGES = {
    # (ecosystem, name-substr) any match -> AI-relevant
    "pip": {
        "langchain", "llama-index", "llamaindex", "vllm", "mlflow",
        "transformers", "huggingface", "ray", "bentoml", "kubeflow",
        "ollama", "openai", "anthropic", "litellm", "label-studio",
        "haystack", "deepset", "guardrails", "rebuff", "presidio",
        "torch", "tensorflow", "onnx", "onnxruntime", "pandas-ai",
        "autogen", "crewai", "chromadb", "weaviate", "qdrant", "milvus",
        "pinecone", "gradio", "streamlit", "comfyui", "diffusers",
        "litserve", "lobe", "open-webui", "dify", "n8n", "agentops",
        "pyspark", "ml-",  "ml_",
        # Expanded 2026-06.
        "langflow", "langgraph", "rasa", "deepspeed", "llama-cpp-python",
        "fastchat", "text-generation", "localai", "privategpt", "autogpt",
        "metagpt", "zenml", "clearml", "wandb", "faiss", "pgvector",
        "semantic-kernel", "guidance", "instructor", "dspy", "outlines",
        "vertexai", "sagemaker", "nemo", "openvino", "sglang", "lmdeploy",
    },
    "npm": {
        "langchain", "llamaindex", "vllm", "openai", "anthropic",
        "@langchain", "@huggingface", "@modelcontextprotocol", "mcp-",
        "flowise", "n8n", "lobe-chat", "open-webui", "anything-llm",
        "@vercel/ai", "ai-",
        # Expanded 2026-06.
        "librechat", "@anthropic-ai", "@openai", "ollama", "@mistralai",
        "langgraph", "@langchain/", "transformers.js", "@xenova/transformers",
    },
    "go": {"langchaingo", "ollama", "openai-go"},
    "rubygems": {"langchainrb", "openai", "anthropic"},
    "maven": {"langchain4j", "djl", "tribuo", "deeplearning4j"},
    "cargo": {"llama", "candle", "burn-"},
    "nuget": {"semantic-kernel", "openai", "anthropic", "llamasharp"},
    "composer": {"orhanerday/open-ai"},
}


def ghsa_is_ai(node: dict) -> bool:
    pkgs = node.get("vulnerabilities", {}).get("nodes", []) or []
    for p in pkgs:
        pkg = p.get("package") or {}
        eco = (pkg.get("ecosystem") or "").lower()
        name = (pkg.get("name") or "").lower()
        wanted = AI_ECOSYSTEM_PACKAGES.get(eco, set())
        for w in wanted:
            if w in name:
                return True
    blob = ((node.get("summary") or "") + " " + (node.get("description") or "")).lower()
    return any(tok in blob for tok in AI_CONTEXT_TOKENS)


def ghsa_to_record(node: dict, malware: bool = False) -> dict | None:
    if not ghsa_is_ai(node):
        return None

    cve_id = None
    for ident in node.get("identifiers", []) or []:
        if (ident.get("type") or "").upper() == "CVE":
            cve_id = ident.get("value")
            break
    ghsa_id = node.get("ghsaId") or ""

    description = (node.get("description") or node.get("summary") or "").strip()
    if not description:
        return None

    severity = (node.get("severity") or "").title() or "Medium"
    cvss_score = ((node.get("cvss") or {}).get("score"))
    cvss_vector = ((node.get("cvss") or {}).get("vectorString")) or None
    cwe_ids = sorted({
        c.get("cweId") for c in ((node.get("cwes") or {}).get("nodes") or [])
        if (c.get("cweId") or "").startswith("CWE-")
    })
    published = (node.get("publishedAt") or "")
    date_str = published[:7] if published else ""
    year = int(published[:4]) if published[:4].isdigit() else None

    refs = []
    if cve_id:
        refs.append({"title": "NVD", "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}", "type": "advisory"})
    if ghsa_id:
        refs.append({"title": ghsa_id, "url": f"https://github.com/advisories/{ghsa_id}", "type": "advisory"})
    for r in node.get("references", []) or []:
        url = r.get("url")
        if not url:
            continue
        if url in {x["url"] for x in refs}:
            continue
        refs.append({"title": url, "url": url, "type": "reference"})
        if len(refs) >= 6:
            break

    pkgs = node.get("vulnerabilities", {}).get("nodes", []) or []
    affected = ", ".join(
        f"{(p.get('package') or {}).get('ecosystem','').lower()}/"
        f"{(p.get('package') or {}).get('name','')}"
        for p in pkgs[:3]
    )

    attack_vector = infer_attack_vector(description)
    owasp_llm, owasp_asi, atlas = map_owasp_and_atlas(description, attack_vector)

    title = (node.get("summary") or description.splitlines()[0])[:200]

    tags = ["cve" if cve_id else "ghsa", "ghsa"]
    if malware:
        tags += ["malicious-package", "supply-chain"]
    if attack_vector and attack_vector != "other":
        tags.append(attack_vector)
    for p in pkgs:
        nm = ((p.get("package") or {}).get("name") or "").lower()
        if nm:
            tags.append(re.sub(r"[^a-z0-9.-]+", "-", nm).strip("-"))
            if len(tags) >= 7:
                break

    return {
        "source_id": cve_id or ghsa_id,
        "cve_id": cve_id,
        "ghsa_id": ghsa_id,
        "title": title,
        "date": date_str,
        "year": year,
        "category": "threat-report" if malware else "vulnerability-disclosure",
        "description": description[:1500],
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": severity,
        "cvss_score": cvss_score,
        "cvss_vector": cvss_vector,
        "cwe_ids": cwe_ids,
        "owasp_llm": owasp_llm,
        "owasp_asi": owasp_asi,
        "nist_ai_rmf": [],
        "mitre_atlas": atlas,
        "references": refs,
        "tags": sorted(set(tags)),
    }


# ----------------------------------------------------------------------------
# OSV.dev fetch for specific AI packages
# ----------------------------------------------------------------------------
OSV_TARGETS = [
    ("langchain", "PyPI"), ("langchain-experimental", "PyPI"),
    ("langchain-community", "PyPI"), ("llama-index", "PyPI"),
    ("llama-index-core", "PyPI"), ("vllm", "PyPI"), ("mlflow", "PyPI"),
    ("transformers", "PyPI"), ("ray", "PyPI"), ("bentoml", "PyPI"),
    ("gradio", "PyPI"), ("streamlit", "PyPI"),
    ("anthropic", "PyPI"), ("openai", "PyPI"), ("litellm", "PyPI"),
    ("autogen-agentchat", "PyPI"), ("crewai", "PyPI"),
    ("haystack-ai", "PyPI"), ("guardrails-ai", "PyPI"),
    ("rebuff", "PyPI"), ("presidio-analyzer", "PyPI"),
    ("chromadb", "PyPI"), ("qdrant-client", "PyPI"), ("weaviate-client", "PyPI"),
    ("pinecone-client", "PyPI"), ("pymilvus", "PyPI"),
    ("label-studio", "PyPI"), ("torch", "PyPI"), ("tensorflow", "PyPI"),
    ("onnx", "PyPI"), ("onnxruntime", "PyPI"), ("pandas-ai", "PyPI"),
    ("diffusers", "PyPI"), ("safetensors", "PyPI"), ("accelerate", "PyPI"),
    ("peft", "PyPI"), ("optimum", "PyPI"),
    ("langchain", "npm"), ("llamaindex", "npm"),
    ("@langchain/core", "npm"), ("@langchain/community", "npm"),
    ("openai", "npm"), ("@anthropic-ai/sdk", "npm"),
    ("flowise", "npm"), ("@n8n/n8n", "npm"),
    ("anythingllm", "npm"), ("lobe-chat", "npm"),
    ("open-webui", "npm"), ("@modelcontextprotocol/sdk", "npm"),
    ("langchaingo", "Go"), ("github.com/ollama/ollama", "Go"),
    ("github.com/sashabaranov/go-openai", "Go"),
]


def fetch_osv() -> list[dict]:
    cache_file = CACHE_OSV / "results.json"
    if cache_file.exists():
        try:
            cached = json.loads(cache_file.read_text("utf-8"))
            if isinstance(cached, list):
                print(f"  [cache] osv: {len(cached)} vulns", flush=True)
                return cached
        except Exception:  # noqa: BLE001
            pass

    all_vulns: list[dict] = []
    seen = set()
    for name, eco in OSV_TARGETS:
        payload = {"package": {"name": name, "ecosystem": eco}}
        try:
            data = http_post_json("https://api.osv.dev/v1/query", payload)
        except Exception as e:  # noqa: BLE001
            print(f"  [warn] osv {eco}/{name}: {e}", flush=True)
            continue
        vulns = data.get("vulns", []) or []
        for v in vulns:
            vid = v.get("id")
            if not vid or vid in seen:
                continue
            seen.add(vid)
            v["_pkg"] = {"name": name, "ecosystem": eco}
            all_vulns.append(v)
        time.sleep(0.3)

    cache_file.write_text(json.dumps(all_vulns), encoding="utf-8")
    print(f"  [osv]   {len(all_vulns)} unique vulns", flush=True)
    return all_vulns


def osv_to_record(v: dict) -> dict | None:
    osv_id = v.get("id") or ""
    aliases = v.get("aliases") or []
    cve_id = next((a for a in aliases if a.startswith("CVE-")), None)
    ghsa_id = next((a for a in aliases if a.startswith("GHSA-")), None)

    description = (v.get("details") or v.get("summary") or "").strip()
    if not description:
        return None

    summary = (v.get("summary") or description.split("\n", 1)[0])[:200]
    published = v.get("published") or v.get("modified") or ""
    date_str = published[:7] if published else ""
    year = int(published[:4]) if published[:4].isdigit() else None

    severity = "Medium"
    cvss_score = None
    cvss_vector = None
    cwe_ids: list[str] = []  # OSV doesn't carry CWE for these entries
    for sev in v.get("severity", []) or []:
        if sev.get("type") in ("CVSS_V3", "CVSS_V31", "CVSS_V4"):
            score_str = sev.get("score", "")
            m = re.search(r"CVSS:[\d.]+/.*", score_str)
            if m:
                cvss_vector = m.group(0)
            # If a numeric base score is in the payload, NVD typically owns it;
            # we leave cvss_score as None unless we find a baseScore field.
            try:
                # Some packages publish numeric scores under .score directly.
                if score_str.replace(".", "").isdigit():
                    cvss_score = float(score_str)
            except Exception:  # noqa: BLE001
                pass

    refs = []
    if cve_id:
        refs.append({"title": "NVD", "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}", "type": "advisory"})
    if ghsa_id:
        refs.append({"title": ghsa_id, "url": f"https://github.com/advisories/{ghsa_id}", "type": "advisory"})
    refs.append({"title": "OSV", "url": f"https://osv.dev/vulnerability/{osv_id}", "type": "advisory"})
    for r in v.get("references", []) or []:
        url = r.get("url")
        if not url:
            continue
        if url in {x["url"] for x in refs}:
            continue
        refs.append({"title": url, "url": url, "type": "reference"})
        if len(refs) >= 6:
            break

    pkg = v.get("_pkg", {})
    affected = f"{pkg.get('ecosystem','').lower()}/{pkg.get('name','')}"

    attack_vector = infer_attack_vector(description)
    owasp_llm, owasp_asi, atlas = map_owasp_and_atlas(description, attack_vector)

    tags = ["osv"]
    if cve_id:
        tags.append("cve")
    if ghsa_id:
        tags.append("ghsa")
    if attack_vector and attack_vector != "other":
        tags.append(attack_vector)
    tags.append(re.sub(r"[^a-z0-9.-]+", "-", pkg.get("name", "").lower()).strip("-"))

    return {
        "source_id": cve_id or ghsa_id or osv_id,
        "cve_id": cve_id,
        "ghsa_id": ghsa_id,
        "osv_id": osv_id,
        "title": summary,
        "date": date_str,
        "year": year,
        "category": "vulnerability-disclosure",
        "description": description[:1500],
        "attack_vector": attack_vector,
        "affected": affected,
        "severity": severity,
        "cvss_score": cvss_score,
        "cvss_vector": cvss_vector,
        "cwe_ids": cwe_ids,
        "owasp_llm": owasp_llm,
        "owasp_asi": owasp_asi,
        "nist_ai_rmf": [],
        "mitre_atlas": atlas,
        "references": refs,
        "tags": sorted(set(t for t in tags if t)),
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    print("=== Phase 1: NVD keyword scans ===", flush=True)
    if NVD_API_KEY:
        print("  [nvd]   NVD_API_KEY set: 50 req/30s rate, 0.7s pacing", flush=True)
    else:
        print("  [nvd]   no NVD_API_KEY: 5 req/30s public rate, 6.5s pacing "
              "(set NVD_API_KEY to speed this up ~10x)", flush=True)
    raw_nvd: dict[str, dict] = {}   # cve_id -> vuln object
    for kw in NVD_KEYWORDS:
        try:
            items = fetch_nvd_keyword(kw)
        except Exception as e:  # noqa: BLE001
            print(f"  [error] {kw}: {e}", flush=True)
            continue
        for v in items:
            cid = ((v.get("cve") or v).get("id"))
            if cid and cid not in raw_nvd:
                raw_nvd[cid] = v
    print(f"  -> {len(raw_nvd)} unique NVD CVEs across all keywords", flush=True)

    records: dict[str, dict] = {}  # source_id -> record
    kept_nvd = 0
    for cid, v in raw_nvd.items():
        rec = nvd_to_record(v)
        if rec:
            records[rec["source_id"]] = rec
            kept_nvd += 1
    print(f"  -> {kept_nvd} NVD CVEs passed AI-context filter", flush=True)

    print("=== Phase 2: GHSA scan ===", flush=True)
    # Two passes: GENERAL (CVE-style advisories) and MALWARE (malicious
    # packages — AI-ecosystem typosquats and trojaned deps). Both are paged
    # back to the 2022 floor, not capped at the newest N.
    for classification in ("GENERAL", "MALWARE"):
        is_malware = classification == "MALWARE"
        ghsa_nodes = fetch_ghsa(classification=classification)
        kept_ghsa = 0
        for node in ghsa_nodes:
            rec = ghsa_to_record(node, malware=is_malware)
            if not rec:
                continue
            sid = rec["source_id"]
            # If we already have this id, merge GHSA refs in instead.
            if sid in records:
                existing = records[sid]
                seen_urls = {r["url"] for r in existing["references"]}
                for r in rec["references"]:
                    if r["url"] not in seen_urls:
                        existing["references"].append(r)
                        seen_urls.add(r["url"])
                existing["tags"] = sorted(set(existing["tags"] + rec["tags"]))
                continue
            records[sid] = rec
            kept_ghsa += 1
        print(f"  -> {kept_ghsa} new GHSA/{classification} entries added", flush=True)

    print("=== Phase 3: OSV ecosystem scan ===", flush=True)
    osv_vulns = fetch_osv()
    kept_osv = 0
    for v in osv_vulns:
        rec = osv_to_record(v)
        if not rec:
            continue
        sid = rec["source_id"]
        if sid in records:
            existing = records[sid]
            seen_urls = {r["url"] for r in existing["references"]}
            for r in rec["references"]:
                if r["url"] not in seen_urls:
                    existing["references"].append(r)
                    seen_urls.add(r["url"])
            existing["tags"] = sorted(set(existing["tags"] + rec["tags"]))
            continue
        records[sid] = rec
        kept_osv += 1
    print(f"  -> {kept_osv} new OSV-only entries added", flush=True)

    out = sorted(records.values(),
                 key=lambda r: (r.get("year") or 0, r.get("date") or ""),
                 reverse=True)
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {len(out)} entries -> {OUT_FILE}", flush=True)

    # Report
    year_counts: dict[int, int] = {}
    vendor_counts: dict[str, int] = {}
    for r in out:
        y = r.get("year") or 0
        year_counts[y] = year_counts.get(y, 0) + 1
        for v in (r.get("affected") or "").split(","):
            v = v.strip()
            if not v:
                continue
            vendor = v.split("/", 1)[0]
            if vendor:
                vendor_counts[vendor] = vendor_counts.get(vendor, 0) + 1

    print("\nYear breakdown:")
    for y in sorted(year_counts, reverse=True):
        print(f"  {y}: {year_counts[y]}")
    print("\nTop 20 vendors:")
    for v, n in sorted(vendor_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"  {v}: {n}")


if __name__ == "__main__":
    main()
