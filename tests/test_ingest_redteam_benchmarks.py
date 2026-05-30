"""Tests for the red-team benchmark catalogue."""

from __future__ import annotations

import re

import ingest_redteam_benchmarks as rt


def test_build_entries_are_well_formed():
    recs = rt.build()
    assert len(recs) >= 8
    seen = set()
    for r in recs:
        assert r["source_id"].startswith("REDTEAM-")
        assert r["source_id"] not in seen, "duplicate source_id"
        seen.add(r["source_id"])
        assert r["category"] == "red-team"
        assert len(r["title"]) >= 5 and len(r["description"]) >= 20
        assert r["references"], "every benchmark needs a citation"
        for ref in r["references"]:
            assert ref["url"].startswith("http")
        for code in r["owasp_llm"]:
            assert re.match(r"^LLM\d{2}$", code)
        for t in r["mitre_atlas"]:
            assert re.match(r"^AML\.T\d{4}(\.\d{3})?$", t)
