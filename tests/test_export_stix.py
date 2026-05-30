"""Tests for the STIX 2.1 exporter."""

from __future__ import annotations

import export_stix as s


_INCIDENTS = [
    {
        "id": "INC-00001", "title": "Example RCE", "description": "A flaw.",
        "date": "2026-01-02", "year": 2026, "severity": "High",
        "attack_vector": "rce", "category": "vulnerability-disclosure",
        "quality_tier": "reviewed", "corpus": "security",
        "owasp_llm": ["LLM05"], "owasp_asi": [], "nist_ai_rmf": ["MEASURE-2.7"],
        "mitre_atlas": ["AML.T0050"], "cve_ids": ["CVE-2026-0001"],
        "references": [{"title": "Advisory", "url": "https://example.com/a", "type": "advisory"}],
        "tags": ["x"], "added": "2026-01-03", "updated": "2026-01-04",
    },
    {
        "id": "INC-00002", "title": "Example harm", "description": "Another.",
        "date": "2025", "year": 2025, "severity": "Medium", "attack_vector": "other",
        "mitre_atlas": ["AML.T0050"], "cve_ids": [], "references": [],
        "added": "2025-06-01", "updated": "2025-06-01",
    },
]


def _bundle():
    return s.build_bundle(_INCIDENTS)


def test_bundle_shape_and_counts():
    b = _bundle()
    assert b["type"] == "bundle" and b["id"].startswith("bundle--")
    from collections import Counter
    by = Counter(o["type"] for o in b["objects"])
    assert by["x-genai-incident"] == 2
    assert by["attack-pattern"] == 1          # AML.T0050 shared across both
    assert by["vulnerability"] == 1           # one CVE
    assert by["relationship"] == 3            # 2 'uses' + 1 'exploits'


def test_ids_are_deterministic():
    assert s.build_bundle(_INCIDENTS) == s.build_bundle(_INCIDENTS)


def test_incident_sdo_has_required_stix_and_custom_fields():
    b = _bundle()
    inc = next(o for o in b["objects"] if o["type"] == "x-genai-incident")
    for k in ("spec_version", "id", "created", "modified", "name"):
        assert inc.get(k), k
    assert inc["created"] == "2026-01-03T00:00:00.000Z"   # from `added`
    assert inc["x_incident_id"] == "INC-00001"
    assert inc["x_severity"] == "High"
    # year-only date is normalised to a full RFC3339 timestamp
    inc2 = next(o for o in b["objects"]
                if o["type"] == "x-genai-incident" and o["x_incident_id"] == "INC-00002")
    assert inc2["created"] == "2025-06-01T00:00:00.000Z"


def test_relationship_refs_resolve():
    b = _bundle()
    ids = {o["id"] for o in b["objects"]}
    for rel in (o for o in b["objects"] if o["type"] == "relationship"):
        assert rel["source_ref"] in ids and rel["target_ref"] in ids
