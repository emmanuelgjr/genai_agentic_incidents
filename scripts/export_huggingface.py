"""
Build a Hugging Face Datasets package for the incident corpus:

  dist/hf/incidents.jsonl   one incident per line (load_dataset-friendly)
  dist/hf/README.md         dataset card (YAML front matter + usage)

Then optionally push to the Hub:

  HF_TOKEN=...  python scripts/export_huggingface.py --push --repo <user>/genai-incidents

`dist/` is a build artifact (gitignored). The JSONL is a flat projection of
data/incidents.json["incidents"], so `datasets.load_dataset("json", ...)`
and `load_dataset("<repo>")` both work.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "dist" / "hf"

CARD = """\
---
license: cc-by-4.0
language:
  - en
pretty_name: GenAI & Agentic AI Security Incidents
tags:
  - security
  - ai-safety
  - llm
  - incidents
  - owasp
  - mitre-atlas
  - nist-ai-rmf
task_categories:
  - text-classification
size_categories:
  - 1K<n<10K
configs:
  - config_name: default
    data_files: incidents.jsonl
---

# GenAI & Agentic AI Security Incidents

{count} real-world and research GenAI / agentic-AI security incidents, each mapped to
**OWASP LLM Top 10 (2025)**, **OWASP Agentic (ASI) Top 10**, **NIST AI RMF**, and
**MITRE ATLAS** (techniques + tactics). Dataset version `{version}`.

```python
from datasets import load_dataset
ds = load_dataset("{repo}", split="train")
ds = ds.filter(lambda r: "LLM01" in (r["owasp_llm"] or []))   # prompt-injection incidents
```

- Code: <https://github.com/emmanuelgjr/genai_incidents>
- Schema & field reference: [`docs/DATA_DICTIONARY.md`](https://github.com/emmanuelgjr/genai_incidents/blob/main/docs/DATA_DICTIONARY.md)
- Provenance, scope & limitations: [`docs/DATASHEET.md`](https://github.com/emmanuelgjr/genai_incidents/blob/main/docs/DATASHEET.md)
- Citation: see [`CITATION.cff`](https://github.com/emmanuelgjr/genai_incidents/blob/main/CITATION.cff) · DOI [10.5281/zenodo.20248676](https://doi.org/10.5281/zenodo.20248676)

**Licence:** data CC-BY-4.0, code MIT. Each entry carries a `quality_tier`
(`curated` / `reviewed` / `auto`) so consumers can filter by vetting level.
"""


def build(out_dir: Path) -> tuple[int, Path]:
    raw = json.loads((DATA / "incidents.json").read_text(encoding="utf-8"))
    incidents = raw.get("incidents", [])
    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl = out_dir / "incidents.jsonl"
    with jsonl.open("w", encoding="utf-8", newline="\n") as fh:
        for inc in incidents:
            fh.write(json.dumps(inc, ensure_ascii=False, sort_keys=True) + "\n")
    card = CARD.format(count=f"{len(incidents):,}", version=raw.get("version", "?"),
                       repo="emmanuelgjr/genai-incidents")
    (out_dir / "README.md").write_text(card, encoding="utf-8", newline="\n")
    return len(incidents), jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true", help="upload to the Hugging Face Hub")
    ap.add_argument("--repo", default="emmanuelgjr/genai-incidents")
    args = ap.parse_args()

    n, jsonl = build(OUT)
    print(f"[hf] wrote {n} records -> {jsonl} (+ README.md)")

    if args.push:
        import os
        token = os.environ.get("HF_TOKEN")
        if not token:
            print("[hf] HF_TOKEN not set; skipping upload", file=sys.stderr)
            sys.exit(1)
        from huggingface_hub import HfApi
        api = HfApi(token=token)
        api.create_repo(args.repo, repo_type="dataset", exist_ok=True)
        api.upload_folder(folder_path=str(OUT), repo_id=args.repo, repo_type="dataset")
        print(f"[hf] pushed to https://huggingface.co/datasets/{args.repo}")


if __name__ == "__main__":
    main()
