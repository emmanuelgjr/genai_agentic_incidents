"""Tests for the cross-entry integrity invariants in validate.py."""

from __future__ import annotations

import validate as v


def _data(*incidents):
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
