"""Tests for the Hugging Face exporter."""

from __future__ import annotations

import json

import export_huggingface as hf


def test_build_emits_jsonl_and_card(tmp_path):
    n, jsonl = hf.build(tmp_path)
    assert jsonl.exists() and n > 0
    lines = [l for l in jsonl.read_text(encoding="utf-8").split("\n") if l]
    assert len(lines) == n
    # every newline-delimited line is a valid JSON object with an id
    ids = {json.loads(l)["id"] for l in lines}
    assert len(ids) == n
    # dataset card has the required HF front matter
    card = (tmp_path / "README.md").read_text(encoding="utf-8")
    assert card.startswith("---")
    assert "license: cc-by-4.0" in card
    assert "configs:" in card and "incidents.jsonl" in card
