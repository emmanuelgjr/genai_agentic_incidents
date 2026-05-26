"""Tests for per-incident page generation."""

from __future__ import annotations

import render_markdown as r


def test_render_incident_page_front_matter():
    """Per-incident page must have correct Jekyll front matter."""
    entry = {
        "id": "INC-04853",
        "title": "Samsung employees leak source code",
        "date": "2023-04",
        "year": 2023,
        "category": "real-world",
        "severity": "High",
        "description": "Samsung employees leaked proprietary code.",
        "tags": ["insider", "data-leak"],
    }
    body = r.render_incident_page(entry)
    assert "layout: incident" in body
    assert "permalink: /incident/INC-04853.html" in body
    assert "incident_id: INC-04853" in body
    assert "year: 2023" in body
    assert "severity: High" in body


def test_render_incident_page_contains_content():
    """Per-incident page must contain the incident content block."""
    entry = {
        "id": "INC-00042",
        "title": "Test incident for page gen",
        "date": "2025-06-01",
        "year": 2025,
        "category": "real-world",
        "severity": "Medium",
        "description": "Description here.",
        "owasp_llm": ["LLM01", "LLM02"],
        "references": [{"title": "Ref", "url": "https://example.com"}],
    }
    body = r.render_incident_page(entry)
    assert "### INC-00042" in body
    assert "Test incident for page gen" in body
    assert "LLM01" in body
    assert "https://example.com" in body


def test_render_incident_page_escapes_title_in_front_matter():
    """Titles with quotes must be safely escaped in YAML front matter."""
    entry = {
        "id": "INC-00099",
        "title": 'Incident with "quotes" and colons: here',
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "Low",
        "description": "Test.",
    }
    body = r.render_incident_page(entry)
    assert "---" in body
    assert "INC-00099" in body
    lines = body.split("\n")
    title_line = [l for l in lines if l.startswith("title:")][0]
    assert '"' in title_line or "'" in title_line


def test_generate_incident_pages_writes_files(tmp_path):
    """generate_incident_pages should write one .md file per incident."""
    entries = [
        {
            "id": "INC-00001",
            "title": "First",
            "date": "2025-01-01",
            "year": 2025,
            "category": "real-world",
            "severity": "High",
            "description": "Desc 1.",
        },
        {
            "id": "INC-00002",
            "title": "Second",
            "date": "2025-02-01",
            "year": 2025,
            "category": "real-world",
            "severity": "Medium",
            "description": "Desc 2.",
        },
    ]
    r.generate_incident_pages(entries, tmp_path)
    assert (tmp_path / "INC-00001.md").exists()
    assert (tmp_path / "INC-00002.md").exists()
    content = (tmp_path / "INC-00001.md").read_text(encoding="utf-8")
    assert "permalink: /incident/INC-00001.html" in content


def test_generate_incident_pages_cleans_stale_files(tmp_path):
    """Stale .md files from previous runs should be removed."""
    stale = tmp_path / "INC-99999.md"
    stale.write_text("stale content", encoding="utf-8")
    entries = [
        {
            "id": "INC-00001",
            "title": "Only",
            "date": "2025",
            "year": 2025,
            "category": "real-world",
            "severity": "Low",
            "description": "Desc.",
        },
    ]
    r.generate_incident_pages(entries, tmp_path)
    assert not stale.exists()
    assert (tmp_path / "INC-00001.md").exists()
