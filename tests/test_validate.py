"""Tests for the cross-entry integrity invariants in validate.py."""

from __future__ import annotations

import validate as v


def _data(*incidents):
    # Default a resolvable reference so fixtures pass the evidence gate unless
    # a test is specifically exercising it.
    for e in incidents:
        e.setdefault("references", [{"url": "https://example.com/src"}])
    return {"incidents": list(incidents)}


def test_integrity_clean():
    data = _data(
        {"id": "INC-1", "cve_ids": ["CVE-1"], "source_ids": ["S-1"]},
        {"id": "INC-2", "cve_ids": ["CVE-2"], "source_ids": ["S-2"]},
    )
    assert v.check_integrity(data, []) == []


def test_integrity_duplicate_cve_flagged():
    data = _data(
        {"id": "INC-1", "cve_ids": ["CVE-1"], "source_ids": ["S-1"]},
        {"id": "INC-2", "cve_ids": ["CVE-1"], "source_ids": ["S-2"]},
    )
    problems = v.check_integrity(data, [])
    assert any("CVE-1" in p and "INC-1" in p and "INC-2" in p for p in problems)


def test_integrity_duplicate_source_flagged():
    data = _data(
        {"id": "INC-1", "source_ids": ["S-1"]},
        {"id": "INC-2", "source_ids": ["S-1"]},
    )
    assert any("S-1" in p for p in v.check_integrity(data, []))


def test_integrity_deprecation_resolves_via_chain():
    data = _data({"id": "INC-3", "cve_ids": [], "source_ids": []})
    deps = [
        {"from": "INC-1", "into": "INC-2"},
        {"from": "INC-2", "into": "INC-3"},  # chain INC-1 -> INC-2 -> INC-3 (live)
    ]
    assert v.check_integrity(data, deps) == []


def test_integrity_deprecation_dangling_flagged():
    data = _data({"id": "INC-3"})
    deps = [{"from": "INC-1", "into": "INC-9"}]  # INC-9 not live
    assert any("does not resolve" in p for p in v.check_integrity(data, deps))


def test_integrity_deprecated_id_still_live_flagged():
    data = _data({"id": "INC-1"})
    deps = [{"from": "INC-1", "into": "INC-1"}]
    assert any("still a live entry" in p for p in v.check_integrity(data, deps))


def test_integrity_deprecation_cycle_does_not_hang():
    data = _data({"id": "INC-3"})
    deps = [
        {"from": "INC-1", "into": "INC-2"},
        {"from": "INC-2", "into": "INC-1"},  # cycle, neither resolves to live
    ]
    problems = v.check_integrity(data, deps)
    assert any("does not resolve" in p for p in problems)


def test_integrity_evidence_gate_flags_sourceless():
    data = _data({"id": "INC-1", "references": []})
    assert any("primary source" in p for p in v.check_integrity(data, []))
    ok = _data({"id": "INC-1", "references": [{"url": "https://x.com/a"}]})
    assert not any("primary source" in p for p in v.check_integrity(ok, []))


def test_integrity_reversibility_gate_flags_non_landmark():
    data = _data({"id": "INC-1", "tier": "feed",
                  "reversibility_class": "irreversible"})
    assert any("reversibility_class" in p for p in v.check_integrity(data, []))


def test_integrity_reversibility_gate_allows_landmark():
    data = _data({"id": "INC-1", "tier": "landmark",
                  "reversibility_class": "read-only"})
    assert not any("reversibility_class" in p for p in v.check_integrity(data, []))
    # Unlabeled entries are fine on any tier — absence means unassessed.
    unlabeled = _data({"id": "INC-2", "tier": "feed"})
    assert not any("reversibility_class" in p for p in v.check_integrity(unlabeled, []))


def test_integrity_discovery_method_gate_flags_non_landmark():
    data = _data({"id": "INC-1", "tier": "feed",
                  "discovery_method": "security-researcher"})
    assert any("discovery_method" in p for p in v.check_integrity(data, []))


def test_integrity_discovery_method_gate_allows_landmark():
    data = _data({"id": "INC-1", "tier": "landmark",
                  "discovery_method": "actor-disclosure"})
    assert not any("discovery_method" in p for p in v.check_integrity(data, []))


def test_integrity_scope_gate_flags_out_of_scope_malware():
    data = _data({"id": "INC-1", "tags": ["malicious-package"],
                  "affected": "npm/chai-mocks",
                  "references": [{"url": "https://x.com/a"}]})
    assert any("out-of-scope" in p for p in v.check_integrity(data, []))
    ok = _data({"id": "INC-1", "tags": ["malicious-package"],
                "affected": "npm/@langchain/core",
                "references": [{"url": "https://x.com/a"}]})
    assert not any("out-of-scope" in p for p in v.check_integrity(ok, []))
