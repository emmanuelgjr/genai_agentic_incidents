"""Validate data/incidents.json against schema/incident.schema.json, and
data/source_freshness.json against schema/source_freshness.schema.json."""

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
    6.   Landmark-label gate (#74): `reversibility_class` and
         `discovery_method` are landmark-tier, evidence-gated labels. `tier`
         is re-derived every build, so an entry drifting out of the landmark
         set must fail loudly rather than ship a stale editorial judgment on
         a feed record.
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

    # 6) Landmark-label gate — evidence-gated labels only on the landmark tier.
    for label_field in ("reversibility_class", "discovery_method"):
        mislabeled = [e["id"] for e in incidents
                      if e.get(label_field) and e.get("tier") != "landmark"]
        if mislabeled:
            problems.append(
                f"{len(mislabeled)} entr(ies) carry {label_field} outside the "
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


def check_source_freshness(data: dict, registry: dict) -> list[str]:
    """Cross-check every entry's `source_freshness` marker against the
    published registry (data/source_freshness.json). Returns violation
    messages (empty == clean).

    The marker is DERIVED — inherited by reference from the registry, never
    authored per row — so every part of it must be reconstructable from the
    registry plus the entry's tags. These checks are what make that true
    rather than merely documented:

    1. Registry self-consistency: `coverage.tracked` must be exactly the key
       set of `sources`, so the stated coverage can't drift from the actual.
    2. Every key a row lists must exist in the registry.
    3. Every listed source must be `stale`. `degraded` deliberately does not
       propagate to rows (see the schema), and a source that is `ok` marking
       rows would be a straightforward falsehood.
    4. Every listed source must actually propagate — a row may not claim
       freshness from a source whose `row_marker` is null (enrichment-only).
    5. The row must carry each listed source's `row_marker` tag: a marker on
       an entry the source never touched is a fabricated provenance claim.
    6. `as_of` must equal the EARLIEST `last_success` among the listed
       sources — the conservative choice, and the only deterministic one.
    7. `sources` must be sorted, so the field is byte-stable across builds.

    NOT checked here, and deliberately: COMPLETENESS — that every entry
    carrying a stale source's `row_marker` tag actually has the marker. That
    gate belongs with the pipeline change that applies the marking; adding it
    before the data carries the markers would fail the build on the very
    state this task exists to describe. See the D8 application spec.
    """
    problems: list[str] = []
    sources = registry.get("sources") or {}

    tracked = registry.get("coverage", {}).get("tracked") or []
    if sorted(tracked) != sorted(sources):
        problems.append(
            "source_freshness registry: coverage.tracked "
            f"{sorted(tracked)} != sources keys {sorted(sources)}"
        )

    for e in data["incidents"]:
        marker = e.get("source_freshness")
        if not marker:
            continue
        listed = list(marker.get("sources") or [])
        if listed != sorted(listed):
            problems.append(f"{e['id']}: source_freshness.sources is not sorted")
        tags = set(e.get("tags") or [])
        last_successes = []
        for key in listed:
            src = sources.get(key)
            if src is None:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, which is not in "
                    "data/source_freshness.json"
                )
                continue
            if src.get("status") != "stale":
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, whose registry "
                    f"status is {src.get('status')!r}, not 'stale'"
                )
            row_marker = src.get("row_marker")
            if row_marker is None:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r}, which does not "
                    "propagate to rows (row_marker is null)"
                )
            elif row_marker.get("value") not in tags:
                problems.append(
                    f"{e['id']}: source_freshness names {key!r} but the entry does "
                    f"not carry its row_marker tag {row_marker.get('value')!r}"
                )
            if src.get("last_success"):
                last_successes.append(src["last_success"])
        if last_successes:
            expected = min(last_successes)
            if marker.get("as_of") != expected:
                problems.append(
                    f"{e['id']}: source_freshness.as_of is {marker.get('as_of')!r}; "
                    f"earliest last_success of its sources is {expected!r}"
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

    # Source-freshness registry: shape, then the row markers that inherit
    # from it. Freshness is a property of the SOURCE; the per-row marker is
    # a derived projection, so both halves are validated together.
    fresh_schema_path = ROOT / "schema" / "source_freshness.schema.json"
    fresh_path = ROOT / "data" / "source_freshness.json"
    if fresh_schema_path.exists() and fresh_path.exists():
        fresh_schema = json.loads(fresh_schema_path.read_text(encoding="utf-8"))
        registry = json.loads(fresh_path.read_text(encoding="utf-8"))
        shape_errs = list(
            jsonschema.Draft202012Validator(fresh_schema).iter_errors(registry)
        )
        for err in shape_errs:
            path = ".".join(str(p) for p in err.path)
            problems.append(f"source_freshness registry: {path}: {err.message}")
        if not shape_errs:
            problems.extend(check_source_freshness(data, registry))
            marked = sum(1 for e in data["incidents"] if e.get("source_freshness"))
            stale = sorted(
                k for k, v in (registry.get("sources") or {}).items()
                if v.get("status") == "stale"
            )
            print(
                f"source freshness: registry valid ({len(registry.get('sources') or {})} "
                f"source(s), observed_at {registry.get('observed_at')}); "
                f"{len(stale)} stale ({', '.join(stale) or 'none'}); "
                f"{marked} entr(ies) carry a source_freshness marker."
            )
    else:
        problems.append(
            "source_freshness: data/source_freshness.json or its schema is missing"
        )

    if problems:
        print(f"\n{len(problems)} integrity violation(s):")
        for p in problems[:20]:
            print(f"  - {p}")
    else:
        print("integrity: no duplicate CVE/source keys; all deprecations resolve.")

    sys.exit(1 if (errors or problems) else 0)


if __name__ == "__main__":
    main()
