"""Template ``data/stats.json`` counts into checked-in doc surfaces (WS6-T2).

``data/stats.json`` is the ONLY source of published counts (invariant 6).
This script never computes a count itself — it reads the already-built
``data/stats.json`` (produced by ``scripts/render_markdown.py`` as part of
``make build``/``make merge render``) and rewrites the marker-wrapped spans
in README.md, docs/DATASHEET.md, docs/index.html, docs/_config.yml, and
CITATION.cff to match it. See ``scripts/stats_docs_lib.py`` for the marker
syntax and the exact-vs-rounded decision.

Idempotent by construction: re-running with an unchanged stats.json produces
byte-identical output (the substitution is pure function of stats.json's
current values), so running it twice in a row is a no-op diff. Run it after
``make merge render`` (it is wired into ``make build``) whenever
data/stats.json changes.

Pure file I/O — no network, no model calls, safe in the deterministic build
path.
"""

from __future__ import annotations

import sys

from stats_docs_lib import DOC_SURFACES, ROOT, load_stats, render_text


def main() -> int:
    stats = load_stats()
    any_changed = False

    for path in DOC_SURFACES:
        if not path.exists():
            continue
        rel = path.relative_to(ROOT)
        original = path.read_text(encoding="utf-8")
        new_text, changes = render_text(original, stats)
        if changes:
            any_changed = True
            path.write_text(new_text, encoding="utf-8", newline="\n")
            for key, old, new in changes:
                print(f"[render-docs-stats] {rel}: stats:{key} {old!r} -> {new!r}")

    if not any_changed:
        print("[render-docs-stats] all doc surfaces already match data/stats.json (no-op)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
