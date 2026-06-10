"""Smoke tests for the renderer's helpers."""

from __future__ import annotations

import render_markdown as r


def test_sort_key_full_date_beats_year_only():
    a = {"date": "2026-05-10", "year": 2026, "title": "a"}
    b = {"date": "2026", "year": 2026, "title": "b"}
    assert r.sort_key(a) < r.sort_key(b)


def test_sort_key_newer_first():
    a = {"date": "2026-04-01", "year": 2026, "title": "a"}
    b = {"date": "2025-12-31", "year": 2025, "title": "b"}
    assert r.sort_key(a) < r.sort_key(b)


def test_truncate_title_short():
    assert r.truncate_title("short title", limit=80) == "short title"


def test_truncate_title_long():
    out = r.truncate_title("A" * 200, limit=80)
    assert len(out) == 80
    assert out.endswith("…")


def test_md_escape_pipes_and_newlines():
    assert r.md_escape("a|b\nc") == "a\\|b c"


def test_shard_rel_format():
    assert r.shard_rel(2026) == "docs/incidents/2026.md"


def test_year_bar_chart_produces_svg(tmp_path):
    from collections import Counter
    out = tmp_path / "year.svg"
    r.render_year_bar_chart(Counter({2024: 5, 2025: 8, 2026: 12}), out)
    body = out.read_text(encoding="utf-8")
    assert body.startswith("<svg")
    assert body.rstrip().endswith("</svg>")
    assert "2024" in body and "2026" in body


def test_owasp_bar_chart_uses_codes(tmp_path):
    from collections import Counter
    out = tmp_path / "owasp.svg"
    r.render_owasp_bar_chart(
        Counter({"LLM01": 10, "LLM05": 4}),
        {"LLM01": "Prompt Injection", "LLM05": "Improper Output Handling"},
        "OWASP LLM coverage",
        out,
    )
    body = out.read_text(encoding="utf-8")
    assert "LLM01" in body and "LLM05" in body
    assert "Prompt Injection" in body


def test_render_incident_block_produces_card():
    """The shared helper should produce an incident card with anchor div."""
    entry = {
        "id": "INC-00001",
        "title": "Test incident",
        "date": "2025-01-15",
        "year": 2025,
        "category": "real-world",
        "severity": "High",
        "description": "A test description.",
        "attack_vector": "prompt-injection",
        "owasp_llm": ["LLM01"],
        "references": [{"title": "Source", "url": "https://example.com", "type": "news"}],
        "tags": ["test"],
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert 'id="inc-00001"' in body
    assert "### INC-00001" in body
    assert "Test incident" in body
    assert "prompt-injection" in body
    assert "LLM01" in body
    assert "https://example.com" in body


def test_render_incident_block_handles_minimal_entry():
    """Minimal entry with only required fields should not crash."""
    entry = {
        "id": "INC-99999",
        "title": "Minimal",
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "Medium",
        "description": "",
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert "### INC-99999" in body
    assert "Minimal" in body


def test_render_incident_block_contains_permalink():
    """Incident block should include a link to the per-incident page."""
    entry = {
        "id": "INC-00001",
        "title": "Test",
        "date": "2025",
        "year": 2025,
        "category": "real-world",
        "severity": "High",
        "description": "Desc.",
    }
    lines = r.render_incident_block(entry)
    body = "\n".join(lines)
    assert "/incident/INC-00001.html" in body


def test_severity_stack_renders_legend(tmp_path):
    from collections import Counter
    out = tmp_path / "sev.svg"
    r.render_severity_stack_chart(
        {2025: Counter({"Critical": 3, "High": 5, "Low": 1}),
         2026: Counter({"High": 7, "Medium": 4})},
        out,
    )
    body = out.read_text(encoding="utf-8")
    assert "Critical" in body and "High" in body
    assert "2025" in body and "2026" in body


def test_liquid_raw_block_wraps_and_defangs_endraw():
    body = [
        "Advisory text with {{ user.input }} and {% for x in y %} examples",
        "attempt to break out: {% endraw %} and {%- endraw -%}",
    ]
    wrapped = r.liquid_raw_block(body)
    assert wrapped[0] == "{% raw %}"
    assert wrapped[-1] == "{% endraw %}"
    inner = "\n".join(wrapped[1:-1])
    assert "{{ user.input }}" in inner          # benign Liquid left as-is
    assert "{% endraw %}" not in inner          # break-out sequences defanged
    assert "{ % endraw %}" in inner


def test_incident_page_body_is_liquid_safe():
    e = {
        "id": "INC-99999", "title": "SSTI demo {{ 7*7 }}", "year": 2026,
        "severity": "High", "date": "2026-01-01",
        "description": "Exploit uses {% for i in (1..9) %} loops.",
        "source_ids": ["TEST-1"], "references": [], "tags": [],
    }
    page = r.render_incident_page(e)
    front, _, body = page.partition("---\n\n")
    assert body.lstrip().startswith("{% raw %}")
    assert body.rstrip().endswith("{% endraw %}")
