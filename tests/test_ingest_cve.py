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
