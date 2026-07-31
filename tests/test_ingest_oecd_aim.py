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
    existing = [{"title": "also no id"}]
    assert o.union_with_existing(fresh, existing) == []


# --- E21 narrative-reduction: build_description() / classify_corpus_signal() /
# --- reclassify_attack_vector_from_narrative() ------------------------------


def test_build_description_never_contains_narrative_text():
    """The whole point of the reduction: no summary/evidences text reaches
    the template, only structural facts."""
    narrative = "This scandalous incident shocked regulators worldwide."
    desc = o.build_description(
        "OECD-AIM-2026-01-01-aaaa", "2026-01-01",
        "https://oecd.ai/en/incidents/2026-01-01-aaaa",
        "Acme Corp", "deepfake",
    )
    assert narrative not in desc
    assert "OECD-AIM-2026-01-01-aaaa" in desc
    assert "2026-01-01" in desc
    assert "Acme Corp" in desc
    assert "deepfake" in desc
    assert "https://oecd.ai/en/incidents/2026-01-01-aaaa" in desc


def test_build_description_omits_optional_fields_when_absent():
    desc = o.build_description(
        "OECD-AIM-2026-01-01-bbbb", "", "https://oecd.ai/en/incidents/2026-01-01-bbbb", "", "other"
    )
    assert "Classified attack vector" not in desc  # "other" is not informative
    assert "Entities named" not in desc
    assert "OECD-AIM-2026-01-01-bbbb" in desc


def test_build_description_respects_length_cap():
    desc = o.build_description(
        "OECD-AIM-x", "2026-01-01", "https://oecd.ai/en/incidents/x",
        "A" * 2000, "deepfake",
    )
    assert len(desc) <= 1500


def test_classify_corpus_signal_security_keyword_wins():
    assert o.classify_corpus_signal(
        "Voice clone scam", "Fraudsters used an AI voice clone to steal money.", ["oecd-aim"]
    ) == "security"


def test_classify_corpus_signal_ai_harm_when_no_security_keyword():
    assert o.classify_corpus_signal(
        "Biased hiring tool", "The AI system showed discriminatory bias against candidates.", ["oecd-aim"]
    ) == "ai-harm"


def test_classify_corpus_signal_defaults_to_security():
    assert o.classify_corpus_signal("Neutral incident", "Nothing keyword-worthy here.", ["oecd-aim"]) == "security"


def test_classify_corpus_signal_matches_merge_and_dedupe_classifier():
    """classify_corpus_signal() must agree with merge_and_dedupe.py's own
    _classify_corpus() on the identical text -- this IS the decoupling
    guarantee (0 unintended corpus moves): the persisted ingest-time value
    must be exactly what the merge-time classifier would have produced from
    the same pre-reduction narrative."""
    import merge_and_dedupe as m

    title = "Deepfake voice clone targets bank"
    narrative = "Scammers used an AI-generated voice clone to authorize a fraudulent wire transfer."
    tags = ["oecd-aim"]
    signal_result = o.classify_corpus_signal(title, narrative, tags)
    merge_result = m._classify_corpus({"title": title, "description": narrative, "tags": tags})
    assert signal_result == merge_result == "security"


def test_reclassify_attack_vector_from_narrative_rescues_other():
    rescued = o.reclassify_attack_vector_from_narrative(
        "other", "AI incident", "The chatbot spread misinformation about a public figure."
    )
    assert rescued == "misinformation"


def test_reclassify_attack_vector_from_narrative_leaves_non_other_untouched():
    assert o.reclassify_attack_vector_from_narrative(
        "deepfake", "AI incident", "Completely unrelated narrative text."
    ) == "deepfake"


def test_reclassify_attack_vector_from_narrative_stays_other_with_no_match():
    assert o.reclassify_attack_vector_from_narrative(
        "other", "AI incident", "Nothing keyword-worthy in this narrative at all."
    ) == "other"


def test_normalize_body_description_never_contains_summary_or_evidences():
    """End-to-end normalize_body(): summary/evidences text must never reach
    the persisted description, and corpus must be set from that same
    (discarded) narrative signal."""
    body = {
        "id": "2026-01-01-dead",
        "title": "Deepfake voice clone scam targets bank customers",
        "date": "2026-01-01",
        "summary": (
            "Fraudsters used an AI-generated voice clone to impersonate a "
            "bank executive and authorize a fraudulent wire transfer of "
            "USD 500,000, exploiting deepfake technology and stolen credentials."
        ),
        "evidences": ["A police report confirmed the scam."],
        "company": ["Example Bank"],
        "articles": [],
        "aiid_ids": [],
    }
    entry = o.normalize_body(body, "https://oecd.ai/en/incidents/2026-01-01-dead")
    assert entry is not None
    assert "Fraudsters used an AI-generated voice clone" not in entry["description"]
    assert "police report" not in entry["description"]
    assert entry["source_id"] in entry["description"]
    assert entry["corpus"] == "security"  # "voice clone" is a security keyword
    assert entry["attack_vector"] == "deepfake"
