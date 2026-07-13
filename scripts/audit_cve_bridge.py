"""Precision audit of grandfathered CVE-bridge merges (issue #88).

Fixing #36 (PR #87) added a full-strength disjoint-CVE weak-key guard: a
weak key (shared reference URL / templated title) may no longer bridge two
entries whose CVE sets are disjoint, because two advisories about *different*
CVEs are different incidents. To keep committed rebuilds byte-stable, PR #87
*grandfathers* pre-existing bridges (``_same_prior`` in
``merge_and_dedupe.dedupe``) rather than un-merging them. Issue #88 tracks a
precision audit of that grandfathered population.

This script quantifies and classifies the population directly from committed
``data/incidents.json`` — no rebuild required. An incident is a *bridge
suspect* when it carries >=2 distinct CVE ids. The audit question: which are
"one advisory, many CVEs" (legitimate, keep merged) vs "many advisories
bridged by a generic URL / template title" (wrong, should split)?

Signals per suspect:
  n_cve       distinct cve_ids
  n_nvd_adv   distinct NVD /vuln/detail advisory URLs among references
  year_spread distinct CVE years (a single advisory rarely spans many years)
  out_of_scope repo's own INCLUSION.md matcher (scope contamination, not just
              over-merge — e.g. a non-GenAI product's CVEs bridged in)

Classification (deliberately conservative — precision over coverage):
  LIKELY_SPLIT  n_cve >= --split-cve (default 10): no single advisory
                plausibly covers this many distinct CVEs; the bridge is a
                weak key. High-confidence wrong-merge.
  REVIEW        3 <= n_cve < split threshold: needs per-entry evidence check.
  LIKELY_KEEP   n_cve == 2: frequently a single advisory listing two CVEs.

The script does NOT mutate data. Designing the one-way split/exclusion
migration (stable ID minting + deprecation records) is the v3.0-scale
follow-up the issue defers.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NVD_RE = re.compile(r"nvd\.nist\.gov/vuln/detail/(CVE-\d{4}-\d+)", re.I)

# Reuse the repo's single INCLUSION.md scope matcher when available so the
# scope-contamination signal matches validate.py exactly.
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from merge_and_dedupe import is_out_of_scope_malware
except Exception:  # pragma: no cover
    is_out_of_scope_malware = None  # type: ignore


def analyze(rec: dict) -> dict:
    cves = sorted({c for c in (rec.get("cve_ids") or []) if c})
    nvd_adv: set[str] = set()
    for ref in rec.get("references") or []:
        m = NVD_RE.search(ref.get("url") or "")
        if m:
            nvd_adv.add(m.group(1).upper())
    years = {c.split("-")[1] for c in cves if c.startswith("CVE-")}
    oos = bool(is_out_of_scope_malware(rec)) if is_out_of_scope_malware else False
    return {
        "id": rec.get("id"),
        "title": (rec.get("title") or "")[:72],
        "tier": rec.get("tier"),
        "n_cve": len(cves),
        "n_nvd_adv": len(nvd_adv),
        "year_spread": len(years),
        "out_of_scope": oos,
        "cves": cves,
    }


def classify(a: dict, split_cve: int) -> str:
    if a["n_cve"] >= split_cve:
        return "LIKELY_SPLIT"
    if a["n_cve"] >= 3:
        return "REVIEW"
    return "LIKELY_KEEP"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("data", nargs="?", default=str(ROOT / "data" / "incidents.json"),
                    help="path to incidents.json (default: data/incidents.json)")
    ap.add_argument("--split-cve", type=int, default=10,
                    help="CVE-count at/above which a bridge is LIKELY_SPLIT (default 10)")
    ap.add_argument("--json", dest="json_out", metavar="PATH",
                    help="also write the full machine-readable report to PATH")
    args = ap.parse_args()

    d = json.load(open(args.data, encoding="utf-8"))
    incidents = d["incidents"] if isinstance(d, dict) else d

    suspects = [analyze(r) for r in incidents if len({c for c in (r.get("cve_ids") or []) if c}) >= 2]
    for a in suspects:
        a["cls"] = classify(a, args.split_cve)

    buckets = collections.Counter()
    for a in suspects:
        n = a["n_cve"]
        b = ("2" if n == 2 else "3-4" if n < 5 else "5-9" if n < 10
             else "10-24" if n < 25 else "25-99" if n < 100 else "100+")
        buckets[b] += 1
    cls = collections.Counter(a["cls"] for a in suspects)
    splits = sorted((a for a in suspects if a["cls"] == "LIKELY_SPLIT"), key=lambda x: -x["n_cve"])
    oos_splits = [a for a in splits if a["out_of_scope"]]

    print(f"total incidents          : {len(incidents)}")
    print(f"multi-CVE bridge suspects: {len(suspects)}  (>=2 distinct cve_ids)")
    print()
    print("CVE-count distribution:")
    for b in ["2", "3-4", "5-9", "10-24", "25-99", "100+"]:
        print(f"  {b:>6}: {buckets[b]}")
    print()
    print(f"classification (split threshold n_cve >= {args.split_cve}):")
    for k in ["LIKELY_SPLIT", "REVIEW", "LIKELY_KEEP"]:
        print(f"  {k:<13}: {cls[k]}")
    print(f"  of LIKELY_SPLIT, flagged out-of-scope by INCLUSION.md matcher: {len(oos_splits)}")
    print()
    print("LIKELY_SPLIT entries (CVE count desc):")
    print(f"  {'id':<11} {'cve':>4} {'nvd':>4} {'yrs':>3} {'oos':>3} tier      title")
    for a in splits:
        print(f"  {a['id']:<11} {a['n_cve']:>4} {a['n_nvd_adv']:>4} {a['year_spread']:>3} "
              f"{'Y' if a['out_of_scope'] else '-':>3} {str(a['tier']):<9} {a['title']}")

    if args.json_out:
        report = {
            "total_incidents": len(incidents),
            "suspect_count": len(suspects),
            "split_cve_threshold": args.split_cve,
            "cve_count_distribution": dict(buckets),
            "classification": dict(cls),
            "likely_split": splits,
            "review": [a for a in suspects if a["cls"] == "REVIEW"],
        }
        Path(args.json_out).write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nwrote machine-readable report -> {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
