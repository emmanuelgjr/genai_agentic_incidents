"""Validate data/incidents.json against schema/incident.schema.json."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

try:
    import jsonschema
except ImportError:
    print(
        "jsonschema is required. Run `pip install -r requirements.txt`.",
        file=sys.stderr,
    )
    sys.exit(2)

# Inclusion-policy gate: reuse the one strict matcher (INCLUSION.md §4).
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from merge_and_dedupe import is_out_of_scope_malware
except Exception:  # pragma: no cover - keep validate runnable in isolation
    is_out_of_scope_malware = None  # type: ignore

_RESOLVABLE_URL = re.compile(r"^(https?://|mailto:)", re.I)


def _has_primary_source(entry: dict) -> bool:
    return any(_RESOLVABLE_URL.match((r.get("url") or "").strip())
              for r in (entry.get("references") or []))


def check_integrity(data: dict, deprecations: list[dict] | None = None) -> list[str]:
    """Cross-entry invariants the JSON schema can't express. Returns a list
    of violation messages (empty == clean).

    1+2. No CVE id or source_id may be held by two live entries. Dedupe
         guarantees each maps to exactly one incident; a duplicate means
         content was silently split across records — the failure mode of the
         2026-06 dedupe tombstone bug. This is the machine check for the
         audit done by hand when that bug was fixed.
    3.   id_deprecations referential integrity: every deprecated `from` id
         must resolve through its `into` chain to a live entry (or be an
         `into:null` removal), and no deprecated id may still be live.
    4.   Evidence gate (INCLUSION.md): every entry must carry at least one
         resolvable http(s)/mailto primary-source reference.
    5.   Scope gate (INCLUSION.md): no out-of-scope malicious-package entry
         may survive — makes the v2.3.1 scope-purge a hard, enforced
         invariant so the generic-malware noise can never return.
    6.   Reversibility gate (#74): `reversibility_class` is a landmark-tier,
         evidence-gated label. `tier` is re-derived every build, so an entry
         drifting out of the landmark set must fail loudly rather than ship
         a stale editorial judgment on a feed record.
    """
    problems: list[str] = []
    incidents = data["incidents"]
    live_ids = {e["id"] for e in incidents}

    for field in ("cve_ids", "source_ids"):
        holders: dict[str, str] = {}
        for e in incidents:
            for key in e.get(field) or []:
                if key in holders:
                    problems.append(
                        f"{field} {key!r} held by both {holders[key]} and {e['id']}"
                    )
                else:
                    holders[key] = e["id"]

    # 4) Evidence gate — every entry needs a resolvable primary source.
    no_source = [e["id"] for e in incidents if not _has_primary_source(e)]
    if no_source:
        problems.append(
            f"{len(no_source)} entr(ies) lack a resolvable primary source "
            f"(e.g. {', '.join(no_source[:5])})"
        )

    # 5) Scope gate — no out-of-scope malicious-package entry may survive.
    if is_out_of_scope_malware is not None:
        oos = [e["id"] for e in incidents if is_out_of_scope_malware(e)]
        if oos:
            problems.append(
                f"{len(oos)} out-of-scope malicious-package entr(ies) survived the "
                f"scope purge (e.g. {', '.join(oos[:5])})"
            )

    # 6) Reversibility gate — labels only on the landmark tier.
    mislabeled = [e["id"] for e in incidents
                  if e.get("reversibility_class") and e.get("tier") != "landmark"]
    if mislabeled:
        problems.append(
            f"{len(mislabeled)} entr(ies) carry reversibility_class outside the "
            f"landmark tier (e.g. {', '.join(mislabeled[:5])})"
        )

    if deprecations is not None:
        into_map = {d.get("from"): d.get("into") for d in deprecations}
        # 'removal' deprecations (into=null, e.g. reason 'out-of-scope') legitimately
        # don't resolve to a live entry — the incident was dropped, not merged.
        removed_ids = {d.get("from") for d in deprecations if d.get("into") is None}
        for frm, into in into_map.items():
            if frm in live_ids:
                problems.append(f"deprecated id {frm} is still a live entry")
            if into is None:
                continue  # removal, not a merge — nothing to resolve
            seen: set[str] = set()
            cur = into
            while cur in into_map and cur not in live_ids and cur not in seen:
                seen.add(cur)
                cur = into_map[cur]
            if cur not in live_ids and cur not in removed_ids:
                problems.append(
                    f"deprecation {frm} -> {into} does not resolve to a live entry"
                )
    return problems


def main():
    schema = json.loads((ROOT / "schema" / "incident.schema.json").read_text(encoding="utf-8"))
    data = json.loads((ROOT / "data" / "incidents.json").read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)

    errors = 0
    for i, entry in enumerate(data["incidents"]):
        errs = list(validator.iter_errors(entry))
        if errs:
            errors += 1
            if errors <= 20:
                print(f"\n{entry.get('id','?')}: {entry.get('title','')[:60]}")
                for e in errs:
                    path = ".".join(str(p) for p in e.path)
                    print(f"  - {path}: {e.message}")
    total = len(data["incidents"])
    print(f"\n{total - errors}/{total} entries valid; {errors} with errors.")

    dep_path = ROOT / "data" / "id_deprecations.json"
    deprecations: list[dict] = []
    if dep_path.exists():
        deprecations = json.loads(dep_path.read_text(encoding="utf-8")).get(
            "deprecations", []
        )
    problems = check_integrity(data, deprecations)
    if problems:
        print(f"\n{len(problems)} integrity violation(s):")
        for p in problems[:20]:
            print(f"  - {p}")
    else:
        print("integrity: no duplicate CVE/source keys; all deprecations resolve.")

    sys.exit(1 if (errors or problems) else 0)


if __name__ == "__main__":
    main()
