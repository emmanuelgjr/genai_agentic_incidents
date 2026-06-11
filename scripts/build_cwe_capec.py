"""
build_cwe_capec.py
==================

Build an authoritative CWE -> CAPEC mapping from MITRE's CAPEC corpus and write
it to mappings/cwe_capec.json. Each CAPEC entry lists its Related Weaknesses
(CWE ids); we invert that to CWE -> sorted list of CAPEC ids.

Committed and refreshed deliberately (CAPEC changes rarely), so the build stays
deterministic — merge_and_dedupe reads the committed map, never the live feed.
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "mappings" / "cwe_capec.json"
CAPEC_CSV_ZIP = "https://capec.mitre.org/data/csv/2000.csv.zip"  # "Mechanisms of Attack" view (all)


def main() -> None:
    print(f"[capec] fetching {CAPEC_CSV_ZIP}", flush=True)
    raw = urllib.request.urlopen(CAPEC_CSV_ZIP, timeout=90).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    txt = z.read(z.namelist()[0]).decode("utf-8", "replace")
    rdr = csv.DictReader(io.StringIO(txt))
    # The id column name can carry a BOM/quotes; find it robustly.
    id_col = next((c for c in rdr.fieldnames if c.strip().strip("'\"").upper() == "ID"),
                  rdr.fieldnames[0])

    cwe_to_capec: dict[str, set[str]] = {}
    n_capec = 0
    for row in rdr:
        capec_id = (row.get(id_col) or "").strip()
        if not capec_id.isdigit():
            continue
        n_capec += 1
        related = row.get("Related Weaknesses") or ""
        for cwe_num in re.findall(r"(\d+)", related):
            cwe_to_capec.setdefault(f"CWE-{cwe_num}", set()).add(f"CAPEC-{capec_id}")

    mapping = {cwe: sorted(caps, key=lambda c: int(c.split("-")[1]))
               for cwe, caps in sorted(cwe_to_capec.items(),
                                       key=lambda kv: int(kv[0].split("-")[1]))}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(
        {"_source": "MITRE CAPEC (Mechanisms of Attack view)",
         "_capec_count": n_capec, "cwe_to_capec": mapping},
        indent=2) + "\n", encoding="utf-8")
    print(f"[capec] {n_capec} CAPECs -> {len(mapping)} CWEs mapped -> {OUT}", flush=True)


if __name__ == "__main__":
    main()
