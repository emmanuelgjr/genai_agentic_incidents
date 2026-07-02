"""Tests for NVD CVE record extraction (CWE + CVSS vector)."""

from __future__ import annotations

import ingest_cve_nvd_expanded as ing


_NVD_VULN = {
    "cve": {
        "id": "CVE-2099-0001",
        "descriptions": [
            {"lang": "en",
             "value": "Prompt injection in an LLM agent enables remote code execution."}
        ],
        "published": "2099-01-02T00:00:00.000",
        "metrics": {
            "cvssMetricV31": [{
                "cvssData": {
                    "baseScore": 9.8, "baseSeverity": "CRITICAL",
                    "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H",
                }
            }]
        },
        "weaknesses": [
            {"description": [{"value": "NVD-CWE-noinfo"}, {"value": "CWE-94"}]}
        ],
        "references": [{"url": "https://example.com/adv"}],
        "configurations": [],
    }
}


def test_nvd_to_record_extracts_cwe_and_vector():
    rec = ing.nvd_to_record(_NVD_VULN)
    assert rec is not None
    assert rec["cve_id"] == "CVE-2099-0001"
    assert rec["cvss_score"] == 9.8
    assert rec["cvss_vector"] == "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    # NVD-CWE-noinfo filtered out; real CWE kept
    assert rec["cwe_ids"] == ["CWE-94"]


def test_malware_filter_rejects_substring_false_positives():
    """Generic npm malware must NOT be classed AI just because a weak token
    (ai/prompt/nemo) appears as a substring (v2.3.0 regression)."""
    for name in ("chai-mocks", "@doaction/sudo-prompt", "nemo-reporter",
                 "@breezeai-frontend/tailwind-config", "email-validator"):
        assert not ing.package_is_strongly_ai(name), name


def test_malware_filter_accepts_real_ai_packages():
    for name in ("langchain-core", "@langchain/openai", "vllm", "ollama",
                 "llama-cpp-python", "@modelcontextprotocol/sdk", "comfyui-x",
                 "anythingllm", "litellm"):
        assert ing.package_is_strongly_ai(name), name


def test_ghsa_openclaw_passes_without_ai_text():
    # Regression: CVE-2026-44112 (GHSA-wppj-c6mr-83jj) was missed because its
    # summary ("OpenShell FS bridge writes ... sandbox mount root") carries no
    # AI-context token — the openclaw package itself must be the signal.
    node = {"vulnerabilities": {"nodes": [{"package": {"ecosystem": "npm", "name": "openclaw"}}]},
            "summary": "OpenShell FS bridge writes stay pinned to the sandbox mount root",
            "description": ""}
    assert ing.ghsa_is_ai(node) is True


def test_ghsa_malware_uses_strict_name_gate():
    # Strict gate ignores the description-token fallback for malware.
    node = {"vulnerabilities": {"nodes": [{"package": {"ecosystem": "npm", "name": "chai-mocks"}}]},
            "summary": "malware contains prompt agent ai", "description": "ai agent prompt"}
    assert ing.ghsa_malware_is_ai(node) is False
    node2 = {"vulnerabilities": {"nodes": [{"package": {"ecosystem": "npm", "name": "@langchain/core"}}]},
             "summary": "malware", "description": ""}
    assert ing.ghsa_malware_is_ai(node2) is True
