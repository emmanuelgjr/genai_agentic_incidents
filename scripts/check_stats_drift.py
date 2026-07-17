"""CI gate for invariant 6: docs pull counts from ``data/stats.json``;
hardcoded totals fail CI (WS6-T2).

Two independent failure modes, both checked:

1. **Marked drift** — a ``<!-- stats:KEY -->...<!-- /stats:KEY -->`` span (or
   a ``<!-- stats:KEY:line -->`` line marker) whose current value no longer
   matches what ``data/stats.json`` says it should be. This is what happens
   if ``data/stats.json`` changes but nobody re-ran ``render_docs_stats.py``
   (equivalently: ``make build``).
2. **Unmarked hardcoded total** — a thousands-grouped number literal
   (``12,986``, ``12,500+`` — the shape a published dataset total takes)
   sitting in a doc surface OUTSIDE any marker span. This is the case
   ``render_docs_stats.py`` structurally cannot catch on its own: it only
   ever rewrites text it already owns (inside a marker), so a stale count
   hand-typed straight into prose would sail through a "no diff after
   re-render" check with zero changes. This sweep is what actually
   satisfies "CI greps docs for hardcoded totals."

Run: ``python scripts/check_stats_drift.py``. Exits 1 with every offending
line printed on any failure; exits 0 (silent, one summary line) if every
surface is clean.
"""

from __future__ import annotations

import sys

from stats_docs_lib import (
    DOC_SURFACES,
    FORMATTERS,
    MARKER_RE,
    NUMBER_LITERAL_RE,
    ROOT,
    line_marker_key,
    load_stats,
    strip_marked_spans,
)


def check_marked_drift(path, text: str, stats: dict) -> list[str]:
    errors = []
    for m in MARKER_RE.finditer(text):
        key = m.group("key")
        if key not in FORMATTERS:
            errors.append(
                f"{path}: <!-- stats:{key} --> has no registered formatter "
                f"in scripts/stats_docs_lib.py (typo in the marker key?)"
            )
            continue
        expected = FORMATTERS[key](stats)
        actual = m.group("value")
        if actual != expected:
            errors.append(
                f"{path}: stats:{key} is {actual!r} but data/stats.json says "
                f"it should be {expected!r} — run `python "
                f"scripts/render_docs_stats.py` and commit the result"
            )

    lines = text.split("\n")
    for i, line in enumerate(lines):
        key = line_marker_key(line)
        if key is None:
            continue
        if key not in FORMATTERS:
            errors.append(
                f"{path}:{i + 1}: <!-- stats:{key}:line --> has no "
                f"registered formatter in scripts/stats_docs_lib.py"
            )
            continue
        if i + 1 >= len(lines):
            errors.append(f"{path}:{i + 1}: stats:{key}:line marker has no following line")
            continue
        expected = FORMATTERS[key](stats)
        found = NUMBER_LITERAL_RE.search(lines[i + 1])
        if found is None:
            errors.append(
                f"{path}:{i + 2}: no number literal found on the line "
                f"after stats:{key}:line — nothing to check"
            )
        elif found.group(0) != expected:
            errors.append(
                f"{path}:{i + 2}: stats:{key}:line following value is "
                f"{found.group(0)!r} but data/stats.json says it should "
                f"be {expected!r} — run `python "
                f"scripts/render_docs_stats.py` and commit the result"
            )
    return errors


def check_unmarked_totals(path, text: str) -> list[str]:
    stripped = strip_marked_spans(text)
    errors = []
    for i, line in enumerate(stripped.split("\n")):
        for m in NUMBER_LITERAL_RE.finditer(line):
            errors.append(
                f"{path}:{i + 1}: hardcoded total {m.group(0)!r} found "
                f"outside any <!-- stats:KEY --> marker — wrap it in a "
                f"marker (see scripts/stats_docs_lib.py) so it derives from "
                f"data/stats.json instead of drifting"
            )
    return errors


def main() -> int:
    stats = load_stats()
    all_errors: list[str] = []

    for path in DOC_SURFACES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(ROOT)
        all_errors.extend(check_marked_drift(rel, text, stats))
        all_errors.extend(check_unmarked_totals(rel, text))

    if all_errors:
        print("::error::Doc surfaces have drifted from data/stats.json (invariant 6):")
        for e in all_errors:
            print(f"  - {e}")
        return 1

    print(f"[check-stats-drift] clean: {len(DOC_SURFACES)} doc surfaces match data/stats.json, "
          f"no unmarked hardcoded totals")
    return 0


if __name__ == "__main__":
    sys.exit(main())
