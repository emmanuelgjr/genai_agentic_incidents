"""Parser-contract tests for scripts/ingest_aiid_snapshot.py.

These assert FIELD EXTRACTION from a frozen fixture shaped exactly like a
row of AIID's official-snapshot `incidents.csv` (WS4-T6 style: not just
"doesn't crash"), and the license-driven exclusions this ingest exists to
enforce:
  - `row["description"]` (AIID's own free-text field) must never appear,
    verbatim or as a substring, in the persisted `description` -- it may
    only be used as an ephemeral classification signal.
  - the persisted `description` is always the original templated sentence.
  - invariant 3: a non-"security-relevant" row is still kept if its
    incident_id is already present in the corpus (`existing_ids`).
"""

from __future__ import annotations

from ingest_aiid_snapshot import (
    build_entry,
    index_duplicates,
    index_mit_classifications,
    _parse_json_list,
    _prettify_slug,
)


def _row(**over):
    base = {
        "incident_id": "6",
        "date": "2016-03-24",
        "reports": "[1,2,3]",
        "Alleged deployer of AI system": '["microsoft"]',
        "Alleged developer of AI system": '["microsoft"]',
        "Alleged harmed or nearly harmed parties": '["twitter-users"]',
        "description": (
            "Microsoft's AI chatbot Tay was deployed on Twitter and within "
            "16 hours posted racist, sexist, and anti-Semitic content after "
            "a coordinated poisoning attack exploiting its online learning."
        ),
        "title": "Microsoft's TayBot Allegedly Posts Racist Content to Twitter",
    }
    base.update(over)
    return base


def test_build_entry_extracts_required_fields():
    entry, relevant, preserved = build_entry(_row(), {}, {}, set())
    assert entry is not None
    assert entry["source_id"] == "AIID-6"
    assert entry["aiid_id"] == 6
    assert entry["title"] == "Microsoft's TayBot Allegedly Posts Racist Content to Twitter"
    assert entry["date"] == "2016-03-24"
    assert entry["year"] == 2016
    assert entry["category"] == "real-world"
    assert entry["references"] == [
        {
            "title": "AIID incident #6",
            "url": "https://incidentdatabase.ai/cite/6/",
            "type": "report",
        }
    ]
    assert "aiid" in entry["tags"]


def test_description_never_contains_upstream_narrative():
    """License-driven exclusion: AIID's own free-text `description` field
    is a transient classification signal only -- it must never leak into
    the persisted description, verbatim or as a recognizable substring."""
    row = _row()
    entry, _, _ = build_entry(row, {}, {}, set())
    assert entry is not None
    # The distinctive upstream phrase must not appear in what we persist.
    assert "16 hours" not in entry["description"]
    assert "anti-Semitic" not in entry["description"]
    assert "coordinated poisoning attack" not in entry["description"]
    # The persisted description is the original templated sentence.
    assert entry["description"].startswith("AI Incident Database (AIID) entry #6:")
    assert "See the linked AIID entry" in entry["description"]


def test_reports_text_field_is_never_referenced():
    """This ingest must never even accept a `reports.text`-shaped field --
    the row shape from the sanctioned snapshot's incidents.csv has no such
    key, and build_entry must not error or synthesize one if a caller
    accidentally passes one through."""
    row = _row()
    row["reports.text"] = "some third-party news article body that must never appear"
    entry, _, _ = build_entry(row, {}, {}, set())
    assert entry is not None
    assert "third-party news article" not in entry["description"]
    assert "reports.text" not in entry


def test_taxonomy_signal_uses_transient_description_not_persisted():
    """The security-relevance / attack_vector / severity heuristics may use
    the upstream description as signal (better classification), but the
    signal text itself is discarded after use."""
    row = _row(description="A prompt injection jailbreak exfiltrated data.")
    entry, relevant, _ = build_entry(row, {}, {}, set())
    assert relevant is True
    assert entry is not None
    assert "prompt injection" not in entry["description"]
    assert "exfiltrated" not in entry["description"]
    assert entry["attack_vector"] in ("prompt-injection", "jailbreak", "data-exfiltration")


_NON_RELEVANT_TITLE = "Automated Grading Tool Shows Inconsistent Results Across School Districts"
_NON_RELEVANT_DESC = "An automated essay-grading tool produced inconsistent scores for equivalent student submissions across different school districts."


def test_non_relevant_row_dropped_when_not_previously_present():
    row = _row(title=_NON_RELEVANT_TITLE, description=_NON_RELEVANT_DESC)
    entry, relevant, preserved = build_entry(row, {}, {}, set())
    assert relevant is False
    assert preserved is False
    assert entry is None


def test_invariant3_preserves_previously_present_non_relevant_row():
    """A row that would NOT pass today's security-relevance filter is still
    emitted if its incident_id already backs a corpus entry -- the swap
    must never silently drop a previously-present AIID incident."""
    row = _row(incident_id="18", title=_NON_RELEVANT_TITLE, description=_NON_RELEVANT_DESC)
    entry, relevant, preserved = build_entry(row, {}, {}, {18})
    assert relevant is False
    assert preserved is True
    assert entry is not None
    assert entry["aiid_id"] == 18


def test_missing_incident_id_or_title_or_year_dropped():
    assert build_entry(_row(incident_id="not-a-number"), {}, {}, set())[0] is None
    assert build_entry(_row(title=""), {}, {}, set())[0] is None
    assert build_entry(_row(date=""), {}, {}, set())[0] is None


def test_entity_slugs_prettified_into_affected():
    row = _row(**{
        "Alleged deployer of AI system": '["uber", "keolis-north-america"]',
        "Alleged developer of AI system": '["uber"]',
    })
    entry, _, _ = build_entry(row, {}, {}, set())
    assert entry is not None
    assert entry["affected"] == "Keolis North America, Uber"


def test_mit_classification_becomes_structured_tag_not_narrative():
    mit_by_id = {
        6: {
            "Incident ID": "6",
            "Risk Domain": "1. Discrimination and Toxicity",
        }
    }
    entry, _, _ = build_entry(_row(), mit_by_id, {}, set())
    assert entry is not None
    assert "mit-risk-domain:1-discrimination-and-toxicity" in entry["tags"]


def test_duplicate_row_tagged_not_dropped():
    entry, _, _ = build_entry(_row(incident_id="88"), {}, {88: 1057}, set())
    assert entry is not None
    assert "aiid-duplicate-of:1057" in entry["tags"]


def test_index_duplicates_and_mit_classifications():
    dup = index_duplicates([
        {"duplicate_incident_number": "88", "true_incident_number": "1057"},
        {"duplicate_incident_number": "bad", "true_incident_number": "x"},
    ])
    assert dup == {88: 1057}

    mit = index_mit_classifications([
        {"Incident ID": "6", "Risk Domain": "1. Discrimination and Toxicity"},
        {"Incident ID": "not-a-number", "Risk Domain": "x"},
    ])
    assert set(mit.keys()) == {6}


def test_parse_json_list_and_prettify_slug():
    assert _parse_json_list('["uber", "keolis-north-america"]') == ["uber", "keolis-north-america"]
    assert _parse_json_list("") == []
    assert _parse_json_list("not json") == []
    assert _prettify_slug("keolis-north-america") == "Keolis North America"
