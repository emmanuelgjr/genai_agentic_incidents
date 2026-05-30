"""Tests for the AIAAIC sheet ingest helpers."""

from __future__ import annotations

import ingest_aiaaic_sheet as a


def _row(headline="", ethical="", purpose=""):
    return {"headline": headline, "ethical": ethical, "purpose": purpose}


def test_detect_attack_vector_rce_requires_word_boundary():
    # Regression: "rce" must not match as a substring of common words, which
    # previously mislabelled harm incidents as remote-code-execution.
    for headline in (
        "Sora 2 generates false claim videos 80 percent of the time",
        "Buzzfeed AI-generated Barbies reinforce racist stereotyping",
        "OpenAI bot crushes small Ukrainian e-commerce website",
        "Ukraine robot-only force attacks Russian troops",
        "Anthropic accused of using fake AI source in copyright case",
    ):
        assert a.detect_attack_vector(_row(headline=headline)) != "rce", headline


def test_detect_attack_vector_rce_matches_real_signal():
    assert a.detect_attack_vector(_row(headline="RCE in the model server")) == "rce"
    assert a.detect_attack_vector(
        _row(headline="Remote code execution via crafted prompt")
    ) == "rce"


def test_detect_attack_vector_other_known_vectors():
    assert a.detect_attack_vector(_row(headline="Deepfake voice clone scam")) == "deepfake"
    assert a.detect_attack_vector(_row(ethical="prompt injection in agent")) == "prompt-injection"
    assert a.detect_attack_vector(_row(headline="Massive data breach exposed users")) == "data-exfiltration"
    assert a.detect_attack_vector(_row(headline="A perfectly ordinary AI mishap")) == "other"
