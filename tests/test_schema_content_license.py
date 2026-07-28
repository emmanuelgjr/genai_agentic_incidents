"""Regression test for the D11(b) schema conditional
(docs/specs/WS0-T3-marker-shape-2026-07-27.md Sec 1): every entry with
description_source == "aiaaic" must carry content_license.

This guards against the allOf block being silently deleted or weakened in a
future edit — with no such assertion, all existing tests would stay green
(the conditional is vacuous today: no entry carries description_source),
which is exactly the gap the WS0-T3 link-1 gate flagged as owed at the
pipeline link (PROGRESS.md WS0-T3 row, ruling (ii))."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schema" / "incident.schema.json"

_BASE_ENTRY = {
    "id": "INC-00001",
    "title": "Test entry title long enough",
    "date": "2025-01-01",
    "year": 2025,
    "category": "real-world",
    "description": "x" * 30,
    "severity": "Low",
    "references": [{"url": "https://example.org"}],
}

_MARKER = {
    "source": "aiaaic",
    "license": "CC-BY-SA-4.0",
    "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
    "attribution": "AIAAIC Repository",
    "attribution_url": "https://www.aiaaic.org/aiaaic-repository",
    "obligations": ["attribution", "share-alike"],
}


def _validator() -> jsonschema.Draft202012Validator:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft202012Validator(schema)


def test_aiaaic_row_without_marker_is_rejected():
    v = _validator()
    entry = dict(_BASE_ENTRY, description_source="aiaaic")
    errors = [e.message for e in v.iter_errors(entry)]
    assert any("content_license" in msg for msg in errors), errors


def test_aiaaic_row_with_marker_validates():
    v = _validator()
    entry = dict(_BASE_ENTRY, description_source="aiaaic", content_license=_MARKER)
    assert list(v.iter_errors(entry)) == []


def test_non_aiaaic_row_without_marker_still_validates():
    # No-regression case for every pre-existing non-AIAAIC entry.
    v = _validator()
    assert list(v.iter_errors(dict(_BASE_ENTRY))) == []


def test_obligations_attribution_only_validates():
    # The Sec 6.4 waiver-downgrade case: dropping "share-alike" is a value
    # change on the existing shape, not a shape change.
    v = _validator()
    marker = dict(_MARKER, obligations=["attribution"])
    entry = dict(_BASE_ENTRY, description_source="aiaaic", content_license=marker)
    assert list(v.iter_errors(entry)) == []


def test_bare_string_content_license_is_rejected():
    v = _validator()
    entry = dict(_BASE_ENTRY, description_source="aiaaic", content_license="CC-BY-SA-4.0")
    assert list(v.iter_errors(entry)) != []


def test_empty_obligations_is_rejected():
    v = _validator()
    marker = dict(_MARKER, obligations=[])
    entry = dict(_BASE_ENTRY, description_source="aiaaic", content_license=marker)
    assert list(v.iter_errors(entry)) != []
