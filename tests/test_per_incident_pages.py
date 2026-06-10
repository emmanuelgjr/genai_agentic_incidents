"""Tests for per-incident page pruning (standalone pages were retired).

The per-incident standalone pages (docs/incident/INC-*.html) were removed:
at 12k+ incidents the Jekyll build of that many files was the deploy
bottleneck. Detail now lives in the year-shard blocks (reachable at
#<slug>) and the client-side detail view in app.js. render_markdown now
prunes the legacy directory instead of generating it.
"""

from __future__ import annotations

import render_markdown as r


def test_prune_incident_pages_removes_dir(tmp_path):
    d = tmp_path / "incident"
    d.mkdir()
    for i in range(3):
        (d / f"INC-0000{i}.md").write_text("x", encoding="utf-8")
    removed = r.prune_incident_pages(d)
    assert removed == 3
    assert not d.exists()


def test_prune_incident_pages_noop_when_absent(tmp_path):
    assert r.prune_incident_pages(tmp_path / "nope") == 0


def test_shard_block_self_anchors_not_pagelink():
    # The detail block must self-link to its #<slug> anchor, not to a
    # retired /incident/INC-*.html standalone page.
    block = "\n".join(r.render_incident_block({
        "id": "INC-00042", "title": "Test incident", "year": 2025,
        "date": "2025-01-01", "severity": "Medium", "description": "d",
        "references": [], "tags": [],
    }))
    assert "(#inc-00042)" in block
    assert "/incident/INC-00042.html" not in block
