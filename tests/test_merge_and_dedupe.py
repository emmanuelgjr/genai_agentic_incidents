"""Unit tests for the merge / normalize / dedupe primitives."""

from __future__ import annotations

import datetime
import json as _json

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


class _FrozenDate(datetime.date):
    """date subclass whose today() is pinned, for cross-day determinism tests."""
    _pinned = datetime.date(2099, 6, 1)

    @classmethod
    def today(cls):
        return cls._pinned


def _oecd_entry(sid, title):
    return {
        "source_id": sid,
        "title": title,
        "description": "A description long enough to pass the minimum length filter.",
        "year": 2026,
        "date": "2026-04-01",
        "attack_vector": "deepfake",
        "severity": "High",
        "references": [{"url": f"https://oecd.ai/en/incidents/{sid}"}],
        "tags": ["oecd-aim"],
    }


def _setup_tmp_repo(tmp_path, monkeypatch):
    data = tmp_path / "data"
    ingest = tmp_path / "ingest"
    data.mkdir()
    ingest.mkdir()
    monkeypatch.setattr(m, "DATA", data)
    monkeypatch.setattr(m, "INGEST", ingest)
    monkeypatch.setattr(m, "DEPRECATIONS_PATH", data / "id_deprecations.json")
    monkeypatch.setattr(m, "CURATION_OVERRIDES_PATH", data / "curation_overrides.json")
    return data, ingest


def test_retention_keeps_dropped_incident_with_stable_id(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)

    # First build: source emits two incidents.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")
    m.main()
    first = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    id_by_src = {
        s: e["id"] for e in first["incidents"] for s in e["source_ids"]
    }
    assert {"OECD-AIM-A", "OECD-AIM-B"} <= set(id_by_src)
    assert len(id_by_src) == 2
    b_id = id_by_src["OECD-AIM-B"]

    # Second build: source dropped incident B (aged out / removed upstream).
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A")]
    ), encoding="utf-8")
    m.main()
    second = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    src_ids_second = {s for e in second["incidents"] for s in e["source_ids"]}

    # B is retained, with the SAME id it had before.
    assert "OECD-AIM-B" in src_ids_second, "dropped incident must be retained"
    b_id_second = next(
        e["id"] for e in second["incidents"] if "OECD-AIM-B" in e["source_ids"]
    )
    assert b_id_second == b_id


def test_deprecated_id_is_not_resurrected(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    # Prior output contains INC-09999, which is recorded as deprecated.
    (data / "incidents.json").write_text(_json.dumps({
        "incidents": [{
            **m.normalize_entry(_oecd_entry("OECD-AIM-DEAD", "Dead dup")),
            "id": "INC-09999", "added": "2026-01-01", "updated": "2026-01-01",
        }]
    }), encoding="utf-8")
    (data / "id_deprecations.json").write_text(_json.dumps({
        "deprecations": [{"from": "INC-09999", "into": "INC-00001",
                          "reason": "merged", "date": "2026-01-01"}]
    }), encoding="utf-8")
    # Current ingest has one live incident.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-LIVE", "Live incident")]
    ), encoding="utf-8")
    m.main()
    out = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    src_ids = {s for e in out["incidents"] for s in e["source_ids"]}
    assert "OECD-AIM-DEAD" not in src_ids, "deprecated entry must not be resurrected"
    assert "OECD-AIM-LIVE" in src_ids, "live incident must still be present"


def test_build_is_deterministic_across_days(tmp_path, monkeypatch):
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")

    # Build on "day 1".
    monkeypatch.setattr(m, "date", _FrozenDate)
    monkeypatch.setattr(_FrozenDate, "_pinned", datetime.date(2099, 6, 1))
    m.main()
    day1 = (data / "incidents.json").read_text(encoding="utf-8")

    # Rebuild on a LATER calendar day with identical inputs.
    monkeypatch.setattr(_FrozenDate, "_pinned", datetime.date(2099, 6, 2))
    m.main()
    day2 = (data / "incidents.json").read_text(encoding="utf-8")

    assert day1 == day2, "rebuild on a later UTC day must be byte-identical"


def test_retention_topup_idempotent_after_drop(tmp_path, monkeypatch):
    """Once a dropped incident is carried forward, further rebuilds with the
    same inputs must be byte-stable (the top-up must not oscillate)."""
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")
    m.main()

    # B drops out of the source; it must be carried forward, then stay stable.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A")]
    ), encoding="utf-8")
    m.main()
    second = (data / "incidents.json").read_text(encoding="utf-8")
    m.main()
    third = (data / "incidents.json").read_text(encoding="utf-8")

    assert second == third, "retention top-up must be idempotent across rebuilds"
    d = _json.loads(third)
    assert d["incident_count"] == 2, "A (fresh) + B (carried forward)"
    srcs = {s for e in d["incidents"] for s in e["source_ids"]}
    assert {"OECD-AIM-A", "OECD-AIM-B"} <= srcs


def test_retention_no_duplicate_when_prior_still_covered(tmp_path, monkeypatch):
    """A prior whose source still emits it must NOT be carried as a duplicate —
    the fresh build already represents it."""
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A")]
    ), encoding="utf-8")
    m.main()
    m.main()  # second build: prior has A and ingest still has A
    d = _json.loads((data / "incidents.json").read_text(encoding="utf-8"))
    assert d["incident_count"] == 1
    assert sum(1 for e in d["incidents"] if "OECD-AIM-A" in e["source_ids"]) == 1


def test_retention_carry_is_deterministic_across_days(tmp_path, monkeypatch):
    """A carried-forward prior must not bump `generated`: rebuilding on a later
    UTC day with the same inputs is byte-identical (CI drift check stays green)."""
    data, ingest = _setup_tmp_repo(tmp_path, monkeypatch)
    monkeypatch.setattr(m, "date", _FrozenDate)
    monkeypatch.setattr(_FrozenDate, "_pinned", datetime.date(2099, 6, 1))
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A"),
         _oecd_entry("OECD-AIM-B", "Incident B")]
    ), encoding="utf-8")
    m.main()  # day 1: both present

    # B drops out; it is carried forward on day 2.
    (ingest / "src.json").write_text(_json.dumps(
        [_oecd_entry("OECD-AIM-A", "Incident A")]
    ), encoding="utf-8")
    monkeypatch.setattr(_FrozenDate, "_pinned", datetime.date(2099, 6, 2))
    m.main()
    day2 = (data / "incidents.json").read_text(encoding="utf-8")

    # Day 3: later calendar day, identical inputs -> must be byte-identical.
    monkeypatch.setattr(_FrozenDate, "_pinned", datetime.date(2099, 6, 3))
    m.main()
    day3 = (data / "incidents.json").read_text(encoding="utf-8")

    assert day2 == day3, "carried-prior rebuild on a later UTC day must be byte-identical"


# ---------------------------------------------------------------------------
# dedupe_entries — tombstone-resolution regressions
# (docs/superpowers/specs/2026-06-03-dedup-tombstone-bug.md)
# ---------------------------------------------------------------------------

def _dedupe_entry(title, year=2024, source_ids=None, cve_ids=None, references=None):
    return {
        "title": title,
        "year": year,
        "date": str(year),
        "severity": "Medium",
        "source_ids": source_ids or [],
        "cve_ids": cve_ids or [],
        "references": references or [],
    }


def test_dedupe_title_hit_on_tombstoned_entry_keeps_content():
    # A and B start as survivors; C shares a source_id with each, so B is
    # transitively absorbed into A and tombstoned — but by_title still points
    # at dead B. D's only match is that stale title key: its CVE must NOT be
    # silently dropped with the tombstone. Since the #36 disjoint-CVE guard,
    # D (a different CVE than the absorber now carries) survives as its own
    # entry instead of being folded in — content is preserved by survival.
    a = _dedupe_entry("Alpha incident", source_ids=["S-A"])
    b = _dedupe_entry("Beta incident", source_ids=["S-B"], cve_ids=["CVE-2024-7001"])
    c = _dedupe_entry("Gamma incident", source_ids=["S-A", "S-B"])
    d = _dedupe_entry("Beta incident", source_ids=["S-D"], cve_ids=["CVE-2024-7002"])

    surviving, tombstoned = m.dedupe_entries([a, b, c, d])

    surviving_cves = {cv for e in surviving for cv in (e.get("cve_ids") or [])}
    assert "CVE-2024-7001" in surviving_cves
    assert "CVE-2024-7002" in surviving_cves  # lost before the _live() fix
    surviving_srcs = {s for e in surviving for s in (e.get("source_ids") or [])}
    assert {"S-A", "S-B", "S-D"} <= surviving_srcs
    assert len(surviving) == 2 and len(tombstoned) == 1
    d_alone = next(e for e in surviving if "CVE-2024-7002" in (e.get("cve_ids") or []))
    assert d_alone.get("source_ids") == ["S-D"]  # not absorbed into A


def test_dedupe_keys_absorbed_mid_reindex_are_reclaimed():
    # When C triggers "B absorbed into A", the CVE that A just inherited from
    # B must be re-pointed at A (the old single-pass reindex iterated a stale
    # key list and left it on tombstoned B). D then matches on that CVE and
    # must merge into live A, keeping its second CVE.
    a = _dedupe_entry("Alpha incident", source_ids=["S-A"])
    b = _dedupe_entry("Beta incident", source_ids=["S-B"], cve_ids=["CVE-2024-7001"])
    c = _dedupe_entry("Gamma incident", source_ids=["S-A", "S-B"])
    d = _dedupe_entry("Delta incident", source_ids=["S-D"],
                      cve_ids=["CVE-2024-7001", "CVE-2024-7003"])

    surviving, _ = m.dedupe_entries([a, b, c, d])

    surviving_cves = {cv for e in surviving for cv in (e.get("cve_ids") or [])}
    assert "CVE-2024-7003" in surviving_cves  # lost before the _live() fix
    assert len(surviving) == 1


def test_dedupe_strips_internal_markers():
    a = _dedupe_entry("Alpha incident", source_ids=["S-A"])
    b = _dedupe_entry("Beta incident", source_ids=["S-B"])
    c = _dedupe_entry("Gamma incident", source_ids=["S-A", "S-B"])

    surviving, tombstoned = m.dedupe_entries([a, b, c])

    for e in surviving + tombstoned:
        assert "_tombstoned" not in e
        assert "_merged_into" not in e


# ---------------------------------------------------------------------------
# CISA KEV enrichment
# ---------------------------------------------------------------------------

def test_load_cisa_kev_missing_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(m, "CISA_KEV_PATH", tmp_path / "nope.json")
    assert m._load_cisa_kev() == {}


def test_load_cisa_kev_reads_snapshot(tmp_path, monkeypatch):
    import json as _j
    p = tmp_path / "cisa_kev.json"
    p.write_text(_j.dumps({"catalogVersion": "x", "count": 1, "vulnerabilities": {
        "CVE-2025-3248": {"dateAdded": "2025-05-12", "knownRansomwareCampaignUse": "Unknown"}
    }}), encoding="utf-8")
    monkeypatch.setattr(m, "CISA_KEV_PATH", p)
    kev = m._load_cisa_kev()
    assert kev["CVE-2025-3248"]["dateAdded"] == "2025-05-12"


def test_kev_fields_are_content_fields():
    # Must be in the content snapshot or KEV flagging would spuriously bump
    # `updated` on the build after the snapshot first lists a CVE.
    assert "exploited_in_wild" in m._CONTENT_FIELDS
    assert "kev_date_added" in m._CONTENT_FIELDS


def test_reversibility_class_is_content_field():
    # Labels land via curation_overrides.json (step 4d, before history
    # stamping) and must bump `updated` exactly once — the KEV precedent.
    assert "reversibility_class" in m._CONTENT_FIELDS


def test_discovery_method_is_content_field():
    # Same landmark-label mechanism as reversibility_class (#74).
    assert "discovery_method" in m._CONTENT_FIELDS


# ---------------------------------------------------------------------------
# Inclusion-policy scope purge (v2.3.1) — drop / don't-retain out-of-scope malware
# ---------------------------------------------------------------------------

def test_is_out_of_scope_malware_generic_npm():
    assert m.is_out_of_scope_malware(
        {"tags": ["malicious-package"], "affected": "npm/chai-mocks"}) is True
    assert m.is_out_of_scope_malware(
        {"tags": ["malicious-package"], "affected": "npm/@doaction/sudo-prompt"}) is True


def test_is_out_of_scope_malware_keeps_real_ai_and_mcp():
    assert m.is_out_of_scope_malware(
        {"tags": ["malicious-package"], "affected": "npm/@langchain/core"}) is False
    assert m.is_out_of_scope_malware(  # MCP-ecosystem supply chain is in scope
        {"tags": ["malicious-package"], "affected": "npm/nextmove-mcp"}) is False


def test_is_out_of_scope_malware_ignores_non_malware():
    # A real CVE in a non-AI-looking package is governed elsewhere, not purged here.
    assert m.is_out_of_scope_malware(
        {"tags": ["cve"], "affected": "npm/chai-mocks"}) is False
    assert m.is_out_of_scope_malware(
        {"tags": ["malicious-package"], "affected": ""}) is False


# ---------------------------------------------------------------------------
# Provenance fields (Pillar 1 trust layer)
# ---------------------------------------------------------------------------

def test_derive_confidence_rule():
    assert m._derive_confidence({"quality_tier": "curated"}) == "high"
    assert m._derive_confidence({"quality_tier": "reviewed"}) == "high"
    assert m._derive_confidence({"quality_tier": "auto", "source_ids": ["A", "B"],
                                 "cve_ids": ["CVE-1"]}) == "high"
    assert m._derive_confidence({"quality_tier": "auto", "source_ids": ["A", "B"]}) == "medium"
    assert m._derive_confidence({"quality_tier": "auto", "source_ids": ["A"],
                                 "cvss_score": 7.5}) == "medium"
    assert m._derive_confidence({"quality_tier": "auto", "source_ids": ["A"]}) == "low"


def test_provenance_fields_not_in_content_snapshot():
    # Must stay out of the snapshot so they never spuriously bump `updated`.
    for f in ("source_count", "confidence", "source_status", "first_seen", "last_seen"):
        assert f not in m._CONTENT_FIELDS


# ---------------------------------------------------------------------------
# #36: weak-key merges must never bridge disjoint-CVE incidents
# ---------------------------------------------------------------------------

def _mk(title, year=2026, cves=None, srcs=None, urls=None):
    return {
        "title": title, "year": year, "date": str(year),
        "cve_ids": cves or [], "source_ids": srcs or [],
        "references": [{"url": u, "type": "advisory"} for u in (urls or [])],
        "tags": [],
    }


def test_cve_disjoint_predicate():
    assert m.cve_disjoint(_mk("a", cves=["CVE-1"]), _mk("b", cves=["CVE-2"]))
    assert not m.cve_disjoint(_mk("a", cves=["CVE-1"]), _mk("b", cves=["CVE-1", "CVE-2"]))
    assert not m.cve_disjoint(_mk("a", cves=["CVE-1"]), _mk("b"))
    assert not m.cve_disjoint(_mk("a"), _mk("b"))


def test_shared_url_disjoint_cves_do_not_merge():
    a = _mk("MLflow path traversal", cves=["CVE-2025-1111"], srcs=["GHSA-a"],
            urls=["https://example.com/shared-advisory", "https://nvd.nist.gov/vuln/detail/CVE-2025-1111"])
    b = _mk("MLflow command injection", cves=["CVE-2025-2222"], srcs=["GHSA-b"],
            urls=["https://example.com/shared-advisory", "https://nvd.nist.gov/vuln/detail/CVE-2025-2222"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 2 and not tombstones


def test_transitive_url_bridge_is_blocked():
    # The #36 MLflow shape: a CVE-less row shares URLs with two distinct-CVE
    # entries; it may merge into one, but must not drag the other in.
    a = _mk("MLflow LFI", cves=["CVE-2025-1111"], srcs=["S-a"],
            urls=["https://example.com/adv-1"])
    c = _mk("MLflow SSRF", cves=["CVE-2025-2222"], srcs=["S-c"],
            urls=["https://example.com/adv-2"])
    bridge = _mk("MLflow security roundup", srcs=["S-b"],
                 urls=["https://example.com/adv-1", "https://example.com/adv-2"])
    surviving, tombstones = m.dedupe_entries([a, c, bridge])
    ids = {tuple(sorted(s["cve_ids"])) for s in surviving}
    assert ("CVE-2025-1111",) in ids or ("CVE-2025-1111", "CVE-2025-2222") not in ids
    assert len(surviving) == 2, [s["title"] for s in surviving]
    assert ("CVE-2025-2222",) in ids  # C kept its own identity


def test_shared_cve_still_merges_via_url_and_cve():
    a = _mk("Advisory view", cves=["CVE-2025-1111"], srcs=["S-a"],
            urls=["https://example.com/adv-1"])
    b = _mk("Vendor view", cves=["CVE-2025-1111", "CVE-2025-3333"], srcs=["S-b"],
            urls=["https://example.com/adv-1"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 1
    assert sorted(surviving[0]["cve_ids"]) == ["CVE-2025-1111", "CVE-2025-3333"]


def test_templated_title_disjoint_cves_do_not_merge():
    a = _mk("A command injection vulnerability exists in mlflow", cves=["CVE-2025-1111"], srcs=["S-a"])
    b = _mk("A command injection vulnerability exists in mlflow", cves=["CVE-2025-2222"], srcs=["S-b"])
    surviving, tombstones = m.dedupe_entries([a, b])
    assert len(surviving) == 2 and not tombstones


def test_grandfathered_prior_merge_still_allowed():
    # Disjoint CVEs, but both sides' keys map to the same previously
    # published entry — the historical merge must reproduce (#36 stays
    # backward-compatible with committed data).
    a = _mk("Roundup A", cves=["CVE-2025-1111"], srcs=["S-a"],
            urls=["https://example.com/adv-1"])
    b = _mk("Roundup B", cves=["CVE-2025-2222"], srcs=["S-b"],
            urls=["https://example.com/adv-1"])
    prior = {"S-a": "INC-00042", "S-b": "INC-00042",
             "CVE-2025-1111": "INC-00042", "CVE-2025-2222": "INC-00042"}
    surviving, tombstones = m.dedupe_entries([a, b], prior)
    assert len(surviving) == 1
    assert sorted(surviving[0]["cve_ids"]) == ["CVE-2025-1111", "CVE-2025-2222"]


def test_new_bridge_blocked_even_when_one_side_has_prior():
    a = _mk("Old entry", cves=["CVE-2025-1111"], srcs=["S-a"],
            urls=["https://example.com/adv-1"])
    b = _mk("New feed row", cves=["CVE-2025-2222"], srcs=["S-new"],
            urls=["https://example.com/adv-1"])
    prior = {"S-a": "INC-00042", "CVE-2025-1111": "INC-00042"}
    surviving, tombstones = m.dedupe_entries([a, b], prior)
    assert len(surviving) == 2 and not tombstones


# ---------------------------------------------------------------------------
# CWE -> attack_vector reclassification (unanimity rule)
# ---------------------------------------------------------------------------

def test_vector_from_cwes_unanimous_and_ignores_unmapped():
    cmap = {"CWE-79": "xss", "CWE-89": "sql-injection"}
    assert m.vector_from_cwes(["CWE-79", "CWE-20"], cmap) == "xss"


def test_vector_from_cwes_conflict_stays_unclassified():
    cmap = {"CWE-79": "xss", "CWE-89": "sql-injection"}
    assert m.vector_from_cwes(["CWE-79", "CWE-89"], cmap) is None


def test_vector_from_cwes_empty_inputs():
    cmap = {"CWE-79": "xss"}
    assert m.vector_from_cwes(None, cmap) is None
    assert m.vector_from_cwes([], cmap) is None
    assert m.vector_from_cwes(["CWE-20"], cmap) is None
    assert m.vector_from_cwes(["CWE-79"], {}) is None


def test_cwe_vector_map_targets_known_vectors_only():
    cmap = m.load_cwe_vector_map()
    assert cmap, "mappings/cwe_attack_vector.json missing or empty"
    veris = _json.loads((m.MAPPINGS / "veris.json").read_text(encoding="utf-8"))
    vocab = set(veris["attack_vector_to_veris"])
    assert set(cmap.values()) <= vocab
    for generic in ("CWE-20", "CWE-74", "CWE-352", "CWE-611", "CWE-125", "CWE-787"):
        assert generic not in cmap
