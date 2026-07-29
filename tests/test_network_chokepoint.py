"""Enforces invariant 5 (MASTER_IMPROVEMENT_PLAN.md: "All network fetching
goes through ingest/common.py", active as of WS0-T4) and the WS0-T4 Accept
criterion ("grep shows no requests./urllib/httpx usage outside
ingest/common.py").

The plan's Accept criterion, run as a literal substring grep, also matches
non-network stdlib usage that legitimately lives outside ingest/common.py --
``urllib.parse.urlencode()``, ``urllib.error.HTTPError`` in an ``except``
clause, and so on (see the classified inventory in
docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md for the full,
exhaustive list this project's own re-run of that grep produces today). What
the invariant actually cares about is narrower and more precise: the FETCH
SURFACE -- the specific calls that put a byte on the wire
(``urlopen()``, ``requests.get/post/put/delete/patch/head/options/request()``,
``requests.Session()``, the ``httpx`` equivalents) -- must have exactly one
home. This test enforces THAT property directly, by parsing each production
ingest script's AST and resolving call targets through their own import
bindings, rather than re-running the literal (and noisier) grep.

Scope: ``scripts/*.py`` and ``ingest/*.py`` -- the plan's own named file list
for this task (MASTER_IMPROVEMENT_PLAN.md WS0-T4 "Files:" line) plus the
chokepoint module's own package. ``tests/`` is deliberately NOT scanned: test
files patch ``"ingest.common.urllib.request.urlopen"`` by NAME (a string
argument to ``unittest.mock.patch``), which never executes the call being
referenced -- there is nothing here for this test to catch, and scanning
would only risk false positives on those very patch-target strings.
"""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The one legitimate home for a live fetch.
CHOKEPOINT_FILE = ROOT / "ingest" / "common.py"

# Named, justified exception: scrape_aiid.py still contains its own live
# fetch call inside fetch_one()/main(), but that function (and main()) is
# permanently disabled -- never invoked by `make ingest-all` (Makefile:87,
# commented out) or anything else that runs. ingest_aiid_snapshot.py (the
# ACTIVE AIID ingest path) imports only pure taxonomy-classification
# functions from this module (TAXONOMY_RULES, is_security_relevant,
# map_taxonomy, severity_for) -- never fetch_one or main. See
# scripts/scrape_aiid.py's own module docstring, ingest/common.py's module
# docstring, and docs/SOURCE_LICENSES.md Section 1.2.
#
# This is the ONLY entry in this allowlist. A new one requires the same
# standard: a reviewed commit explaining why the call is dead code, not
# merely unused today.
INERT_ALLOWLIST = {ROOT / "scripts" / "scrape_aiid.py"}

# Dotted call targets that constitute an actual network fetch. Anything
# resolving to one of these, outside CHOKEPOINT_FILE or INERT_ALLOWLIST, is a
# bypass of the chokepoint and fails this test.
NETWORK_CALL_TARGETS = {
    "urllib.request.urlopen",
    "requests.get", "requests.post", "requests.put", "requests.delete",
    "requests.patch", "requests.head", "requests.options", "requests.request",
    "requests.Session",
    "httpx.get", "httpx.post", "httpx.put", "httpx.delete", "httpx.patch",
    "httpx.head", "httpx.options", "httpx.request",
    "httpx.Client", "httpx.AsyncClient",
}


def _import_bindings(tree: ast.Module) -> dict[str, str]:
    """Map each local name introduced by an import statement to the dotted
    path it refers to, e.g. ``import urllib.request`` -> {"urllib":
    "urllib"} (the bound name for a plain `import a.b` is the top-level `a`,
    per Python's own import semantics) and ``from urllib.request import
    urlopen`` -> {"urlopen": "urllib.request.urlopen"}."""
    bindings: dict[str, str] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    # `import a.b.c as x` binds `x` directly to the `a.b.c`
                    # module object.
                    bindings[alias.asname] = alias.name
                else:
                    # `import a.b.c` binds only the top-level name `a` in
                    # the local namespace; `a.b.c.func()` still resolves
                    # correctly below because `a` maps to itself.
                    top = alias.name.split(".")[0]
                    bindings[top] = top
        elif isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                local = alias.asname or alias.name
                bindings[local] = f"{node.module}.{alias.name}"
    return bindings


def _dotted_name(node: ast.expr) -> str | None:
    """Reconstruct 'a.b.c' from a Name/Attribute chain, or None if the base
    isn't a simple Name (e.g. a call result, subscript, ...)."""
    parts: list[str] = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _resolve_call_target(call: ast.Call, bindings: dict[str, str]) -> str | None:
    dotted = _dotted_name(call.func)
    if dotted is None:
        return None
    head, _, rest = dotted.partition(".")
    resolved_head = bindings.get(head, head)
    return f"{resolved_head}.{rest}" if rest else resolved_head


def _find_network_calls(py_file: Path) -> list[tuple[int, str]]:
    tree = ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
    bindings = _import_bindings(tree)
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            resolved = _resolve_call_target(node, bindings)
            if resolved in NETWORK_CALL_TARGETS:
                hits.append((node.lineno, resolved))
    return hits


def _production_py_files() -> list[Path]:
    files = sorted((ROOT / "scripts").glob("*.py")) + sorted((ROOT / "ingest").glob("*.py"))
    assert files, "expected to find .py files under scripts/ and ingest/ -- scan setup is broken"
    return files


def test_no_network_fetch_calls_outside_the_chokepoint():
    offenders: list[str] = []
    for py_file in _production_py_files():
        if py_file == CHOKEPOINT_FILE or py_file in INERT_ALLOWLIST:
            continue
        for lineno, target in _find_network_calls(py_file):
            offenders.append(f"{py_file.relative_to(ROOT)}:{lineno} calls {target}()")
    assert not offenders, (
        "Found live network-fetch call(s) outside ingest/common.py (invariant "
        "5 violation). Route through ingest.common.fetch_once() / "
        "robust_fetch() / conditional_fetch() instead, or -- if this really "
        "is dead code like scrape_aiid.py's disabled main() -- add it to "
        "INERT_ALLOWLIST above with the same justification standard as the "
        "existing entry:\n  " + "\n  ".join(offenders)
    )


def test_the_inert_allowlist_entry_is_still_actually_inert():
    """A cheap tripwire against the allowlist silently going stale: if
    scrape_aiid.py's main() (or the ingest-aiid Makefile target) is ever
    re-enabled, this should fail loudly rather than have the allowlist
    quietly cover a live bypass."""
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "python scripts/scrape_aiid.py" not in makefile.splitlines(), (
        "scripts/scrape_aiid.py appears to be invoked from the Makefile again -- "
        "if scrape_aiid.py's main() is back in the live ingest path, it must "
        "route through ingest.common instead of remaining on "
        "INERT_ALLOWLIST in this test."
    )
    # The commented-out reference documenting the disabled target should
    # still be present -- if it disappears, someone removed the historical
    # note this allowlist entry depends on for its own justification.
    assert "scrape_aiid.py" in makefile


def test_chokepoint_file_itself_still_contains_the_fetch_surface():
    """Positive control: if this ever finds zero network calls in
    ingest/common.py, the AST resolution logic above is broken (import
    aliasing changed, etc.), and the "no bypass" result from the main test
    would be meaningless rather than reassuring."""
    hits = _find_network_calls(CHOKEPOINT_FILE)
    assert hits, (
        "Expected to find at least one urllib.request.urlopen() call in "
        "ingest/common.py -- if this fails, the AST-resolution logic in this "
        "test file no longer recognizes it, and the 'no bypass elsewhere' "
        "test above is not actually testing anything."
    )


def test_literal_accept_criterion_grep_is_documented_not_silently_clean():
    """The plan's Accept criterion, run VERBATIM as a literal grep for
    `requests.|urllib|httpx` under scripts/, is NOT clean today -- it matches
    non-network stdlib helpers (urllib.parse, urllib.error) plus
    scrape_aiid.py's inert fetch. This is expected and documented, not a
    silent gap: see docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md
    for the full classified list. This test only pins that the documented
    set of files still matches reality -- if a NEW file starts matching the
    literal grep, that's worth a human look even if it turns out to be
    another non-network helper, so this fails loudly rather than silently
    absorbing it."""
    import re

    pattern = re.compile(r"requests\.|urllib|httpx")
    expected_files = {
        ROOT / "scripts" / "ingest_aiaaic_sheet.py",
        ROOT / "scripts" / "ingest_cve_nvd_expanded.py",
        ROOT / "scripts" / "scrape_aiid.py",
    }
    actual_files = set()
    for py_file in sorted((ROOT / "scripts").glob("*.py")):
        text = py_file.read_text(encoding="utf-8")
        if any(pattern.search(line) for line in text.splitlines()):
            actual_files.add(py_file)
    assert actual_files == expected_files, (
        "The set of scripts/*.py files matching the plan's literal Accept-"
        "criterion grep changed. If this is a NEW file, classify each hit "
        "(live-fetch / inert-fetch-in-disabled-code / non-network-helper) "
        "in docs/audits/WS0-T4-network-chokepoint-inventory-2026-07-29.md "
        "and update `expected_files` here; if it's a REMOVED file (e.g. a "
        "urllib.parse import was refactored away), update `expected_files` "
        "too so this test keeps pinning the real, current set.\n"
        f"expected: {sorted(p.name for p in expected_files)}\n"
        f"actual:   {sorted(p.name for p in actual_files)}"
    )
