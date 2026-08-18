"""Tests for the MISP feed exporter."""

from __future__ import annotations

import json

import export_misp as m


_INCIDENTS = [
    {
        "id": "INC-00001", "title": "Example RCE", "description": "A flaw.",
        "date": "2026-01-02", "year": 2026, "severity": "High",
        "attack_vector": "rce", "corpus": "security", "tier": "feed",
        "owasp_llm": ["LLM10"], "owasp_asi": [], "mitre_atlas": ["AML.T0050"],
        "cve_ids": ["CVE-2026-0001"],
        "references": [{"title": "Advisory", "url": "https://example.com/a", "type": "advisory"}],
    },
    {
        "id": "INC-00002", "title": "Older harm", "description": "Another.",
        "date": "2025", "year": 2025, "severity": "Medium", "attack_vector": "other",
        "corpus": "ai-harm", "tier": "landmark", "cve_ids": [],
        "references": [{"url": "https://example.com/b", "type": "news"}],
    },
]


def _build(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "OUT", tmp_path)
    n_events, n_attr = m.build(_INCIDENTS)
    return tmp_path, n_events, n_attr


def test_manifest_matches_event_files(tmp_path, monkeypatch):
    out, n_events, _ = _build(tmp_path, monkeypatch)
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert len(manifest) == n_events == 2  # one event per distinct year
    for ev_uuid in manifest:
        ev = json.loads((out / f"{ev_uuid}.json").read_text(encoding="utf-8"))["Event"]
        assert ev["uuid"] == ev_uuid
        assert ev["published"] is True
        assert isinstance(ev["Attribute"], list) and ev["Attribute"]


def test_incident_tags_and_attribute_types(tmp_path, monkeypatch):
    out, _, _ = _build(tmp_path, monkeypatch)
    # find the 2026 event and its incident's title attribute
    events = [json.loads(p.read_text(encoding="utf-8"))["Event"]
              for p in out.glob("*.json") if p.name != "manifest.json"]
    attrs = [a for ev in events for a in ev["Attribute"]]
    types = {a["type"] for a in attrs}
    assert {"text", "vulnerability", "link"} <= types
    # INC-00001's title attribute carries its taxonomy tags (incl. ATLAS)
    title = next(a for a in attrs
                 if a["type"] == "text" and a["comment"].startswith("INC-00001"))
    tagnames = {tg["name"] for tg in title["Tag"]}
    assert 'genai-incidents:incident-id="INC-00001"' in tagnames
    assert 'genai-incidents:owasp-llm="LLM10"' in tagnames
    assert 'mitre-atlas:technique="AML.T0050"' in tagnames


def test_veris_tags_from_attack_vector(tmp_path, monkeypatch):
    out, _, _ = _build(tmp_path, monkeypatch)
    events = [json.loads(p.read_text(encoding="utf-8"))["Event"]
              for p in out.glob("*.json") if p.name != "manifest.json"]
    attrs = [a for ev in events for a in ev["Attribute"]]
    # INC-00001 (attack_vector=rce) carries the crosswalked VERIS machinetag.
    title1 = next(a for a in attrs
                  if a["type"] == "text" and a["comment"].startswith("INC-00001"))
    assert 'veris:action:hacking:variety="Exploit vuln"' in {
        t["name"] for t in title1["Tag"]}
    # INC-00002 (attack_vector=other) is deliberately unmapped — no veris tags.
    title2 = next(a for a in attrs
                  if a["type"] == "text" and a["comment"].startswith("INC-00002"))
    assert not any(t["name"].startswith("veris:") for t in title2["Tag"])


def test_veris_mapping_file_is_well_formed():
    # Every row: known attack_vector key, "predicate=value" entries with a
    # colon-pathed predicate and a non-empty value, no stray quotes (values
    # are interpolated into veris:<pred>="<value>" machinetags).
    import re
    from pathlib import Path
    root = Path(m.__file__).resolve().parents[1]
    mapping = json.loads((root / "mappings" / "veris.json").read_text(
        encoding="utf-8"))["attack_vector_to_veris"]
    schema = json.loads((root / "schema" / "incident.schema.json").read_text(
        encoding="utf-8"))
    known = set(schema["properties"]["attack_vector"]["examples"])
    assert mapping, "empty mapping"
    for av, entries in mapping.items():
        assert av in known, f"unknown attack_vector key {av!r}"
        assert entries, f"{av}: empty entry list"
        for ent in entries:
            pred, sep, val = ent.partition("=")
            assert sep and val, f"{av}: malformed entry {ent!r}"
            assert re.fullmatch(r"[a-z_]+(:[a-z_]+)*", pred), \
                f"{av}: bad predicate {pred!r}"
            assert '"' not in ent, f"{av}: quote in entry {ent!r}"


def test_hashes_csv_covers_every_attribute(tmp_path, monkeypatch):
    out, _, n_attr = _build(tmp_path, monkeypatch)
    lines = [l for l in (out / "hashes.csv").read_text(encoding="utf-8").splitlines() if l]
    assert len(lines) == n_attr
    assert all("," in l for l in lines)


def test_deterministic(tmp_path, monkeypatch):
    out, _, _ = _build(tmp_path, monkeypatch)
    before = (out / "manifest.json").read_text(encoding="utf-8")
    m.build(_INCIDENTS)
    assert (out / "manifest.json").read_text(encoding="utf-8") == before
