"""Unit tests for the merge / normalize / dedupe primitives."""

from __future__ import annotations

import merge_and_dedupe as m


def test_classify_attack_vector_prompt_injection():
    assert m.classify_attack_vector("Indirect prompt injection in chatbot") == "indirect-prompt-injection"
    assert m.classify_attack_vector("Standard prompt injection variant") == "prompt-injection"


def test_classify_attack_vector_misc():
    assert m.classify_attack_vector("Path traversal in MLflow") == "path-traversal"
    assert m.classify_attack_vector("Command injection via shell") == "command-injection"
    assert m.classify_attack_vector("SSRF in Copilot") == "ssrf"
    assert m.classify_attack_vector("Voice clone scam targeted CFO") == "deepfake"
    assert m.classify_attack_vector("Supply-chain malicious package") == "supply-chain"


def test_classify_attack_vector_new_patterns():
    assert m.classify_attack_vector("ChatGPT hallucinated a court case") == "hallucination"
    assert m.classify_attack_vector("AI-generated misinformation campaign") == "misinformation"
    assert m.classify_attack_vector("Phishing email crafted by LLM") == "phishing"
    assert m.classify_attack_vector("Ransomware attack on hospital") == "ransomware"
    assert m.classify_attack_vector("Impersonating CEO via AI voice") == "deepfake"
    assert m.classify_attack_vector("Arbitrary code execution in TensorFlow") == "rce"
    assert m.classify_attack_vector("RAG poisoning via injected documents") == "memory-poisoning"
    assert m.classify_attack_vector("Resource exhaustion via token flooding") == "dos"
    assert m.classify_attack_vector("Dependency confusion in PyTorch package") == "supply-chain"


def test_classify_attack_vector_harm_vectors():
    # New high-precision AI-harm vectors (catch the AIAAIC "other" residue).
    assert m.classify_attack_vector(
        "CivitAI accused of generating synthetic 'child pornography' images"
    ) == "csam-generation"
    assert m.classify_attack_vector(
        "Purportedly AI-generated sexual images of at least 400 minors at a school"
    ) == "csam-generation"
    assert m.classify_attack_vector(
        "Character.AI companion encouraged a teen toward self-harm and suicide"
    ) == "unsafe-advice"
    assert m.classify_attack_vector(
        "Leonardo AI generates celebrity non-consensual porn images"
    ) == "deepfake"
    assert m.classify_attack_vector(
        "Clearview AI facial recognition scraped billions of faces (BIPA)"
    ) == "privacy-violation"
    assert m.classify_attack_vector(
        "Amazon scraps recruiting tool showing gender bias against women"
    ) == "algorithmic-bias"
    assert m.classify_attack_vector(
        "ChatGPT defamed a radio host by inventing an embezzlement case"
    ) == "misinformation"


def test_classify_attack_vector_harm_precision():
    # Regression guards: AIAAIC category-label tokens and non-generative
    # automated-decision errors must NOT be force-fit into a harm vector.
    # "Automation bias" (over-trust in automation) is not algorithmic bias.
    assert m.classify_attack_vector(
        "Amazon AI coding bot causes AWS outage. Ethical issues: Automation bias; "
        "Autonomy/agency. Response: Policy review/update."
    ) is None
    # A flawed RPA debt-recovery system is not generative-AI misinformation.
    assert m.classify_attack_vector(
        "Robodebt system falsely accused Australians of welfare debt via RPA"
    ) is None


def test_seed_frameworks_from_vector_security():
    e = {"attack_vector": "rce"}
    m.seed_frameworks_from_vector(e)
    assert e["owasp_llm"] == ["LLM05"]


def test_seed_frameworks_from_vector_harm_nist():
    e = {"attack_vector": "privacy-violation"}
    m.seed_frameworks_from_vector(e)
    assert e.get("nist_ai_rmf") and not e.get("owasp_llm")
    e2 = {"attack_vector": "algorithmic-bias"}
    m.seed_frameworks_from_vector(e2)
    assert e2["nist_ai_rmf"] == ["MEASURE-2.11"]


def test_seed_frameworks_never_overrides_existing():
    e = {"attack_vector": "rce", "owasp_llm": ["LLM01"]}
    m.seed_frameworks_from_vector(e)
    assert e["owasp_llm"] == ["LLM01"]  # untouched


def test_seed_frameworks_skips_unmappable_vector():
    e = {"attack_vector": "other"}
    m.seed_frameworks_from_vector(e)
    assert not e.get("owasp_llm") and not e.get("nist_ai_rmf")


def test_quality_tier_aiaaic_slug_vs_numeric():
    # Hand-picked AIAAIC slug entries are reviewed; the numeric bulk sheet is auto.
    assert m._classify_quality_tier({"source_ids": ["AIAAIC-arup-25m-cfo"]}) == "reviewed"
    assert m._classify_quality_tier({"source_ids": ["AIAAIC2257"]}) == "auto"


def test_quality_tier_cve_cvss_is_reviewed():
    # NVD-analyst-scored CVEs are reviewed; unscored raw pulls stay auto.
    assert m._classify_quality_tier(
        {"source_ids": ["CVE-2026-1"], "cvss_score": 9.8}
    ) == "reviewed"
    assert m._classify_quality_tier({"source_ids": ["CVE-2026-1"]}) == "auto"


def test_curation_overrides_file_loads_and_is_valid():
    ov = m._load_curation_overrides()
    assert isinstance(ov, dict)
    # Every override must be a dict; quality_tier (if set) must be valid.
    for sid, fields in ov.items():
        assert isinstance(fields, dict), sid
        if "quality_tier" in fields:
            assert fields["quality_tier"] in ("curated", "reviewed", "auto"), sid


def test_fill_taxonomy_populates_atlas_tactics():
    e = {"owasp_llm": [], "owasp_asi": [], "mitre_atlas": ["AML.T0048"], "nist_ai_rmf": []}
    m.fill_taxonomy(e)
    # AML.T0048 (External Harms) maps to the Impact tactic in current ATLAS.
    assert e.get("mitre_atlas_tactics"), "tactics should be populated"
    assert all(t.startswith("AML.TA") for t in e["mitre_atlas_tactics"])


def test_fill_taxonomy_subtechnique_inherits_parent_tactics():
    parent = {"mitre_atlas": ["AML.T0048"]}
    child = {"mitre_atlas": ["AML.T0048.003"]}
    m.fill_taxonomy(parent)
    m.fill_taxonomy(child)
    assert child.get("mitre_atlas_tactics") == parent.get("mitre_atlas_tactics")


def test_classify_attack_vector_no_match():
    assert m.classify_attack_vector("Generic AI failure with no specifics") is None


def test_normalize_url_strips_protocol_and_query():
    assert m.normalize_url("https://www.Example.com/path/?utm=1") == "example.com/path"
    assert m.normalize_url("http://example.com/a#frag") == "example.com/a"
    assert m.normalize_url("") == ""


def test_title_key_collapses_punctuation():
    a = m.title_key("LangChain RCE — CVE-2026-12345!")
    b = m.title_key("LangChain rce CVE 2026 12345")
    assert a == b


def test_normalize_entry_handles_source_id_or_source_ids():
    base = {
        "title": "Test incident",
        "description": "This is a long enough description for the normaliser to accept.",
        "year": 2026,
        "date": "2026-04-01",
        "references": [{"url": "https://example.com/inc/1"}],
    }
    e1 = m.normalize_entry({**base, "source_id": "AIID-99"})
    e2 = m.normalize_entry({**base, "source_ids": ["AIID-99", "OECD-AIM-x"]})
    e3 = m.normalize_entry({**base, "source_id": "AIID-99", "extra_source_ids": ["OECD-AIM-x"]})
    assert e1["source_ids"] == ["AIID-99"]
    assert set(e2["source_ids"]) == {"AIID-99", "OECD-AIM-x"}
    assert set(e3["source_ids"]) == {"AIID-99", "OECD-AIM-x"}


def test_normalize_entry_lifts_aiid_id_from_source_id():
    entry = m.normalize_entry(
        {
            "title": "Deepfake spread on TikTok",
            "description": "A long enough description to pass the minimum length filter.",
            "year": 2026,
            "source_id": "AIID-1234",
            "references": [{"url": "https://incidentdatabase.ai/cite/1234/"}],
        }
    )
    assert entry["aiid_id"] == 1234


def test_normalize_entry_classifies_attack_vector_when_other():
    entry = m.normalize_entry(
        {
            "title": "SSRF in MLflow tracking server",
            "description": "A server-side request forgery flaw was patched in MLflow 3.9.",
            "year": 2026,
            "attack_vector": "other",
            "source_id": "CVE-2026-1",
            "references": [{"url": "https://nvd.nist.gov/vuln/detail/CVE-2026-1"}],
        }
    )
    assert entry["attack_vector"] == "ssrf"


def test_normalize_entry_keeps_explicit_attack_vector():
    entry = m.normalize_entry(
        {
            "title": "Voice clone scam at a bank",
            "description": "An attacker used an AI voice clone to authorise a wire transfer.",
            "year": 2026,
            "attack_vector": "deepfake",
            "source_id": "RES-x",
            "references": [{"url": "https://example.com/r"}],
        }
    )
    assert entry["attack_vector"] == "deepfake"


def test_normalize_entry_widens_cve_pattern():
    entry = m.normalize_entry(
        {
            "title": "A 9-digit CVE issued",
            "description": "Some CVE pipelines now assign 8-9 digit numbers.",
            "year": 2026,
            "source_id": "CVE-2026-100000001",
            "cve_ids": ["CVE-2026-100000001"],
            "references": [{"url": "https://example.com/cve"}],
        }
    )
    assert entry["cve_ids"] == ["CVE-2026-100000001"]


def test_merge_into_takes_more_specific_date():
    target = {"date": "2024", "year": 2024, "severity": "Medium"}
    src = {"date": "2024-03-18", "year": 2024, "severity": "Medium", "references": []}
    m.merge_into(target, src)
    assert target["date"] == "2024-03-18"


def test_merge_into_overrides_future_year():
    target = {"date": "2027", "year": 2027, "severity": "Medium"}
    src = {"date": "2024-03-18", "year": 2024, "severity": "Medium", "references": []}
    m.merge_into(target, src)
    assert target["date"] == "2024-03-18"
    assert target["year"] == 2024


def test_merge_into_merges_cwe_ids():
    target = {"cwe_ids": ["CWE-79"], "severity": "Medium", "references": []}
    src = {"cwe_ids": ["CWE-918", "CWE-79"], "severity": "Medium", "references": []}
    m.merge_into(target, src)
    assert target["cwe_ids"] == ["CWE-79", "CWE-918"]


def test_maybe_rewrite_cve_title():
    entry = {
        "title": "A flaw has been found in MLflow up to 3.8.0.",
        "attack_vector": "ssrf",
        "cve_ids": ["CVE-2026-2393"],
        "description": "SSRF in MLflow",
    }
    m.maybe_rewrite_cve_title(entry)
    assert entry["title"] == "MLflow — Ssrf (CVE-2026-2393)"


def test_classify_quality_tier_curated_legacy():
    assert m._classify_quality_tier({"source_ids": ["LEGACY-INC-00012"]}) == "curated"


def test_classify_quality_tier_curated_with_mitigations():
    entry = {"source_ids": ["RES-x", "AIID-1"], "mitigations": ["patch", "scan"]}
    assert m._classify_quality_tier(entry) == "curated"


def test_classify_quality_tier_reviewed():
    entry = {"source_ids": ["AIID-1"]}
    assert m._classify_quality_tier(entry) == "reviewed"


def test_classify_quality_tier_auto():
    entry = {"source_ids": ["CVE-2026-1234"]}
    assert m._classify_quality_tier(entry) == "auto"


def test_classify_corpus_security_wins_via_cve():
    entry = {"cve_ids": ["CVE-2026-1"], "title": "Discrimination via biased model"}
    assert m._classify_corpus(entry) == "security"


def test_classify_corpus_security_via_keyword():
    entry = {"title": "Deepfake CEO scam at a bank", "description": "..."}
    assert m._classify_corpus(entry) == "security"


def test_classify_corpus_ai_harm():
    entry = {
        "title": "Hiring algorithm discriminates against women",
        "description": "Algorithmic bias in resume screening.",
    }
    assert m._classify_corpus(entry) == "ai-harm"


def test_classify_corpus_default_security():
    entry = {"title": "Some neutral entry", "description": "No keywords."}
    assert m._classify_corpus(entry) == "security"


def test_normalise_severity_handles_garbage_inputs():
    assert m._normalise_severity("None") == "Medium"
    assert m._normalise_severity(None) == "Medium"
    assert m._normalise_severity("") == "Medium"
    assert m._normalise_severity("not a severity") == "Medium"
    assert m._normalise_severity("HIGH") == "High"
    assert m._normalise_severity("critical") == "Critical"


def test_aiid_oecd_source_id_normalised():
    """`AIID-N-OECD` (legacy bridge file) collapses to canonical `AIID-N`."""
    entry = m.normalize_entry(
        {
            "title": "Some Old AIID incident",
            "description": "A long enough description to pass the minimum length filter.",
            "year": 2020,
            "source_ids": ["AIID-74-OECD"],
            "references": [{"url": "https://incidentdatabase.ai/cite/74/"}],
        }
    )
    assert "AIID-74" in entry["source_ids"]
    assert "AIID-74-OECD" not in entry["source_ids"]


def test_maybe_rewrite_cve_title_leaves_curated_titles_alone():
    entry = {
        "title": "Microsoft Copilot Studio indirect prompt injection (CVE-2026-21520)",
        "attack_vector": "indirect-prompt-injection",
        "cve_ids": ["CVE-2026-21520"],
        "description": "Detailed write-up",
    }
    m.maybe_rewrite_cve_title(entry)
    assert entry["title"].startswith("Microsoft Copilot Studio")


def test_maybe_rewrite_cve_title_handles_product_blurb():
    """`<Product> is a/an <description>.` titles from NVD get rewritten when we
    have a CVE to anchor the resulting title."""
    entry = {
        "title": "Gradio is an open-source Python package designed for quick prototyping.",
        "attack_vector": "path-traversal",
        "cve_ids": ["CVE-2024-1234"],
        "description": "Path traversal in Gradio.",
    }
    m.maybe_rewrite_cve_title(entry)
    assert entry["title"] == "Gradio — Path Traversal (CVE-2024-1234)"


def test_maybe_rewrite_cve_title_skips_blurb_without_cve():
    """Don't invent a generic title when there's no CVE to ground it."""
    entry = {
        "title": "Some Tool is a productivity helper for developers.",
        "attack_vector": "other",
        "description": "Some Tool is a productivity helper for developers.",
    }
    m.maybe_rewrite_cve_title(entry)
    assert entry["title"].startswith("Some Tool is a")


def test_load_retained_priors_excludes_deprecated():
    prev = [
        {"id": "INC-00001", "title": "kept"},
        {"id": "INC-00002", "title": "deprecated"},
    ]
    out = m.load_retained_priors(prev, {"INC-00002"})
    assert [e["id"] for e in out] == ["INC-00001"]


def test_load_retained_priors_keeps_all_when_none_deprecated():
    prev = [{"id": "INC-00001"}, {"id": "INC-00002"}]
    out = m.load_retained_priors(prev, set())
    assert len(out) == 2


def test_load_retained_priors_skips_entries_without_id():
    prev = [{"title": "no id"}, {"id": "INC-00003", "title": "ok"}]
    out = m.load_retained_priors(prev, set())
    assert [e["id"] for e in out] == ["INC-00003"]


def test_load_retained_priors_all_deprecated_returns_empty():
    prev = [{"id": "INC-00001"}, {"id": "INC-00002"}]
    out = m.load_retained_priors(prev, {"INC-00001", "INC-00002"})
    assert out == []
