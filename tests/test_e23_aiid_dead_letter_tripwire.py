"""Tripwire regression tests for the E23 finding
(docs/audits/E23-aiid-scope-measurement-2026-07-30.md Sec 3): a dormant
population of AIID-<n>-keyed content sits committed in this repository
(``ingest/aiid_incidents.json``'s 63 hand-curated rows that collide with the
sanctioned AIID snapshot; ``ingest/airi_navigator_incidents.json``'s own
composed titles) but never reaches the shipped corpus, because
``ingest/aiid_full.json`` always sorts first (alphabetical ``glob()`` order,
``scripts/merge_and_dedupe.py:1336``) and wins every AIID-<n> source-ID-keyed
dedup, and ``merge_into()``'s allow-list never touches ``title``/
``description``. E23's own words: "a dormant population protected only by
merge order and dedup -- an artifact, not a design." This file converts that
incidental protection into an enforced one, run against the REAL committed
ingest files (read-only, in-process repro of the actual
``normalize_entry``/``dedupe_entries`` pipeline -- no ``data/*.json`` write,
no network) so a future change to file naming, dedup key precedence, or
``merge_into()``'s allow-list is caught mechanically instead of silently
shipping hand-curated/AIRI-composed AIID text.

Only the three ingest files that can carry an ``AIID-<n>`` source_id
participate in this population -- ``data/legacy_consolidated.json`` carries
zero AIID references (E23 Sec 1, confirmed empty by grep) and is skipped,
both for speed and because including it could not change this population's
outcome.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import merge_and_dedupe as m

ROOT = Path(__file__).resolve().parents[1]
INGEST = ROOT / "ingest"

# The Unicode non-breaking space -- referenced explicitly (not a literal
# embedded character) so this file stays unambiguous under any editor/font.
_NBSP = " "

# The three files that can carry an AIID-<n> source_id, in the SAME sorted()
# order scripts/merge_and_dedupe.py's own main() loads ingest/*.json in --
# this is exactly the ordering the finding depends on (aiid_full.json first).
_AIID_RELEVANT_FILES = sorted(
    ("aiid_full.json", "aiid_incidents.json", "airi_navigator_incidents.json")
)


def _load(name: str) -> list[dict]:
    return json.loads((INGEST / name).read_text(encoding="utf-8"))


def _aiid_id_from_source_id(source_id: str) -> int | None:
    if not source_id or not source_id.startswith("AIID-"):
        return None
    try:
        return int(source_id.split("-", 1)[1])
    except ValueError:
        return None


def _nbsp_normalize(s: str) -> str:
    """Collapse NBSP to a plain space before comparing. Deliberately
    narrower than a full unicode NFKC normalization, which would also fold
    unrelated punctuation differences (e.g. hyphen variants) and could mask
    a real leak as a false "exception"."""
    return (s or "").replace(_NBSP, " ")


def _clean_like_normalize_entry(s: str) -> str:
    """Mirror merge_and_dedupe.py::normalize_entry()'s own nested _clean()
    (strip stray carriage returns, collapse runs of whitespace -- Python's
    "\\s" regex class is unicode-aware and DOES fold NBSP into the match,
    confirmed by E23 Sec 3(i): a non-breaking-space character present in the
    raw aiid_full.json title is "normalized away by normalize_entry() before
    it reaches the corpus"). _clean() itself isn't importable (nested, not
    module-level), so this is a deliberate, documented mirror -- used to make
    the leak check below an unambiguous POSITIVE assertion against AIID's
    own (post-normalization) title, rather than a negative comparison
    against AIRI's title. A negative comparison is exactly what makes the
    NBSP row a false "exception": both sides collapse to the same string
    once whitespace is normalized, which proves nothing about which source
    actually won the merge -- only a positive check against AIID's title
    does."""
    return re.sub(r"\s+", " ", (s or "").replace("\r", " ")).strip()


def _build_surviving_by_aiid_id() -> dict[int, dict]:
    """Read-only, in-process repro of the real merge pipeline (E23 Sec
    3(ii)'s own verification method), restricted to the AIID-relevant
    files."""
    raw: list[dict] = []
    for name in _AIID_RELEVANT_FILES:
        raw.extend(_load(name))
    normalized = [n for n in (m.normalize_entry(r) for r in raw) if n is not None]
    surviving, _tombstoned = m.dedupe_entries(normalized)
    by_id: dict[int, dict] = {}
    for e in surviving:
        aiid_id = e.get("aiid_id")
        if aiid_id is not None:
            by_id[int(aiid_id)] = e
    return by_id


def test_hand_curated_aiid_rows_never_ship_their_own_title_or_description():
    """E23 Sec 3(i): every ``ingest/aiid_incidents.json`` row whose
    ``AIID-<n>`` source_id collides with ``ingest/aiid_full.json``'s own
    AIID snapshot must lose the merge -- its own paraphrased title and
    unverified-provenance description text must never be the version that
    ships. Measured 2026-07-30: 63 colliding rows, 0 leaked. (AIID titles
    never exactly match the hand-curated titles to begin with -- E23 Sec 2b:
    "Exact string match: 0/63" -- so a plain equality check against the
    hand-curated row's own text, unlike the AIRI test below, carries no
    coincidental-equality ambiguity.)"""
    hand_curated_by_id: dict[int, dict] = {}
    for row in _load("aiid_incidents.json"):
        aid = _aiid_id_from_source_id(row.get("source_id") or "")
        if aid is not None:
            hand_curated_by_id[aid] = row

    surviving_by_id = _build_surviving_by_aiid_id()
    colliding = {
        aid: row for aid, row in hand_curated_by_id.items() if aid in surviving_by_id
    }

    # Positive control: the population this test protects must actually
    # exist (E23 measured 63), or the leak assertion below would pass
    # vacuously. A floor, not an exact match, so ordinary AIID-snapshot
    # growth (which can only ever ADD collisions, never remove one --
    # aiid_full.json's own ids are append-only per invariant 3) doesn't turn
    # this into a maintenance burden.
    assert len(colliding) >= 63, (
        f"expected at least the 63 colliding AIID-<n> rows E23 measured in "
        f"ingest/aiid_incidents.json, found {len(colliding)} -- the "
        f"protected population shrank unexpectedly"
    )

    leaked: list[tuple[int, str]] = []
    for aid, hc_row in colliding.items():
        survivor = surviving_by_id[aid]
        if _nbsp_normalize(survivor.get("title", "")) == _nbsp_normalize(
            hc_row.get("title", "")
        ):
            leaked.append((aid, "title"))
        if _nbsp_normalize(survivor.get("description", "")) == _nbsp_normalize(
            hc_row.get("description", "")
        ):
            leaked.append((aid, "description"))
    assert not leaked, (
        "ingest/aiid_incidents.json's own hand-curated title/description "
        "leaked into the merged output for the AIID-<n> id(s)/field(s) "
        f"below -- merge precedence no longer protects this population "
        f"(alphabetical file-load order, source-ID dedup precedence, or "
        f"merge_into()'s allow-list may have changed): {leaked[:10]}"
    )


def test_airi_navigators_own_composed_title_never_ships_when_it_differs_from_aiid():
    """E23 Sec 3: of the AIRI Navigator rows whose OWN composed title
    genuinely differs (strict string inequality) from AIID's own canonical
    title for the same ``AIID-<n>`` cross-reference (E23 Sec 1 path (f)),
    AIID's own title -- not AIRI's -- must be what ships. Measured
    2026-07-30: 147 rows genuinely differ, 0 leaked; exactly 1 apparent
    exception (aiid_id 164) is an NBSP-vs-space encoding artifact of
    normalize_entry()'s own whitespace collapsing, not a real content
    difference -- which is exactly why this test checks a POSITIVE match
    against AIID's (whitespace-normalized) title rather than a negative
    mismatch against AIRI's: for that one row, AIRI's title and AIID's title
    are literally indistinguishable after normalization, so a negative check
    could not tell which one actually won the merge."""
    aiid_title_by_id: dict[int, str] = {}
    for row in _load("aiid_full.json"):
        aid = _aiid_id_from_source_id(row.get("source_id") or "")
        if aid is not None:
            aiid_title_by_id[aid] = row.get("title") or ""

    genuinely_differs: list[int] = []
    for row in _load("airi_navigator_incidents.json"):
        aid = _aiid_id_from_source_id(row.get("source_id") or "")
        if aid is None or aid not in aiid_title_by_id:
            continue
        airi_title = row.get("title") or ""
        # Strict comparison on purpose: this defines the POPULATION under
        # test. Folding NBSP in here too would exclude the one known
        # apparent-exception row from the population entirely, instead of
        # exercising the (unambiguous, positive) leak check against it.
        if airi_title != aiid_title_by_id[aid]:
            genuinely_differs.append(aid)

    # Positive control, floored below the measured 147 to tolerate ordinary
    # AIRI-refresh drift (titles can be re-composed on re-ingest) without
    # becoming a brittle exact-count assertion.
    assert len(genuinely_differs) >= 100, (
        f"expected at least ~147 AIRI-Navigator rows with a composed title "
        f"genuinely differing from AIID's own (E23 baseline), found "
        f"{len(genuinely_differs)} -- the protected population shrank "
        f"unexpectedly"
    )

    surviving_by_id = _build_surviving_by_aiid_id()
    not_aiid: list[int] = []
    for aid in genuinely_differs:
        survivor = surviving_by_id.get(aid)
        if survivor is None:
            continue
        expected = _clean_like_normalize_entry(aiid_title_by_id[aid])
        if survivor.get("title", "") != expected:
            not_aiid.append(aid)
    assert not not_aiid, (
        "the merged output's title did not match AIID's own snapshot title "
        f"(post-normalization) for AIID id(s): {not_aiid[:10]} -- AIRI "
        "Navigator's own composed title (or something else) may have won "
        "the merge instead, meaning merge precedence no longer protects "
        "this population"
    )
