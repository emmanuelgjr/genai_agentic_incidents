"""Tests for the static TAXII 2.1 exporter."""

from __future__ import annotations

import json

import export_taxii as t


_INCIDENTS = [
    {
        "id": "INC-00001", "title": "Example RCE", "description": "A flaw.",
        "date": "2026-01-02", "year": 2026, "severity": "High",
        "attack_vector": "rce", "category": "vulnerability-disclosure",
        "mitre_atlas": ["AML.T0050"], "cve_ids": ["CVE-2026-0001"],
        "references": [{"title": "Advisory", "url": "https://example.com/a", "type": "advisory"}],
        "added": "2026-01-03", "updated": "2026-01-04",
    },
    {
        "id": "INC-00002", "title": "Example harm", "description": "Another.",
        "date": "2025", "year": 2025, "severity": "Medium", "attack_vector": "other",
        "mitre_atlas": ["AML.T0050"], "cve_ids": [], "references": [],
        "added": "2025-06-01", "updated": "2025-06-01",
    },
]


def _build(tmp_path, monkeypatch):
    monkeypatch.setattr(t, "OUT", tmp_path)
    n = t.build(_INCIDENTS)
    return tmp_path, n


def test_discovery_points_at_api_root(tmp_path, monkeypatch):
    out, _ = _build(tmp_path, monkeypatch)
    disc = json.loads((out / "discovery.json").read_text(encoding="utf-8"))
    assert disc["api_roots"] == [disc["default"]]
    assert disc["default"].endswith("/taxii2/api/")


def test_collection_objects_and_manifest_align(tmp_path, monkeypatch):
    out, n = _build(tmp_path, monkeypatch)
    cols = json.loads((out / "api" / "collections.json").read_text(encoding="utf-8"))
    cid = cols["collections"][0]["id"]
    assert cid == t.COLLECTION_ID
    coll = out / "api" / "collections" / cid
    objs = json.loads((coll / "objects.json").read_text(encoding="utf-8"))
    man = json.loads((coll / "manifest.json").read_text(encoding="utf-8"))
    assert objs["more"] is False
    assert len(objs["objects"]) == n == len(man["objects"])
    # every manifest id references a real object
    obj_ids = {o["id"] for o in objs["objects"]}
    assert all(m["id"] in obj_ids for m in man["objects"])


def test_deterministic(tmp_path, monkeypatch):
    out, _ = _build(tmp_path, monkeypatch)
    first = (out / "discovery.json").read_text(encoding="utf-8")
    coll = out / "api" / "collections" / t.COLLECTION_ID / "objects.json"
    first_obj = coll.read_text(encoding="utf-8")
    t.build(_INCIDENTS)  # rebuild into same dir
    assert (out / "discovery.json").read_text(encoding="utf-8") == first
    assert coll.read_text(encoding="utf-8") == first_obj
