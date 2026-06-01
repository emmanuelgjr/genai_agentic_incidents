"""Unit tests for the OECD AIM ingester's union-with-existing behaviour."""

from __future__ import annotations

import ingest_oecd_aim as o


def _entry(sid, title):
    return {"source_id": sid, "title": title, "year": 2026,
            "references": [{"url": "https://oecd.ai/en/incidents/x"}]}


def test_union_keeps_aged_out_existing_entries():
    # Fresh fetch lost OLD-2 (it aged out of the 3000-URL window).
    fresh = [_entry("OECD-AIM-NEW-1", "new one")]
    existing = [_entry("OECD-AIM-OLD-2", "old two")]
    out = o.union_with_existing(fresh, existing)
    ids = {e["source_id"] for e in out}
    assert ids == {"OECD-AIM-NEW-1", "OECD-AIM-OLD-2"}


def test_union_fresh_wins_on_conflict():
    fresh = [_entry("OECD-AIM-1", "fresh title")]
    existing = [_entry("OECD-AIM-1", "stale title")]
    out = o.union_with_existing(fresh, existing)
    assert len(out) == 1
    assert out[0]["title"] == "fresh title"


def test_union_output_sorted_by_source_id():
    fresh = [_entry("OECD-AIM-3", "c"), _entry("OECD-AIM-1", "a")]
    existing = [_entry("OECD-AIM-2", "b")]
    out = o.union_with_existing(fresh, existing)
    assert [e["source_id"] for e in out] == [
        "OECD-AIM-1", "OECD-AIM-2", "OECD-AIM-3"
    ]


def test_union_drops_entries_without_source_id():
    fresh = [{"title": "no id", "references": []}]
    existing = []
    assert o.union_with_existing(fresh, existing) == []
