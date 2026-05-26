"""Tests for shared ingest utilities."""

from __future__ import annotations

import urllib.error
from unittest.mock import patch, MagicMock

import ingest_utils as u


def test_robust_fetch_returns_cached_content(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"x" * 2000)
    result = u.robust_fetch("https://example.com/data", cache, min_cache_bytes=1000)
    assert result == b"x" * 2000


def test_robust_fetch_skips_small_cache(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"tiny")
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"fresh data"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = u.robust_fetch("https://example.com/d", cache, min_cache_bytes=1000)
    assert result == b"fresh data"
    assert cache.read_bytes() == b"fresh data"


def test_robust_fetch_retries_on_failure(tmp_path):
    cache = tmp_path / "data.bin"
    with patch("ingest_utils.urllib.request.urlopen") as mock_open, \
         patch("ingest_utils.time.sleep"):
        mock_open.side_effect = urllib.error.URLError("connection refused")
        try:
            u.robust_fetch("https://example.com/x", cache, max_retries=3)
            assert False, "Should have raised"
        except RuntimeError as e:
            assert "connection refused" in str(e)
        assert mock_open.call_count == 3


def test_robust_fetch_succeeds_on_second_try(tmp_path):
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"ok"
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open, \
         patch("ingest_utils.time.sleep"):
        mock_open.side_effect = [urllib.error.URLError("timeout"), mock_resp]
        result = u.robust_fetch("https://example.com/x", cache, max_retries=3)
    assert result == b"ok"
    assert mock_open.call_count == 2


def test_conditional_fetch_cold_cache(tmp_path):
    cache = tmp_path / "data.bin"
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"payload"
    mock_resp.getheader.side_effect = lambda h, d=None: {
        "ETag": '"abc123"', "Last-Modified": "Sun, 25 May 2026 00:00:00 GMT"
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"payload"
    assert changed is True
    etag_file = tmp_path / "data.bin.etag"
    assert etag_file.exists()
    assert '"abc123"' in etag_file.read_text(encoding="utf-8")


def test_conditional_fetch_304_not_modified(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"cached payload")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "abc123"\n', encoding="utf-8")
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.side_effect = urllib.error.HTTPError(
            "https://example.com/d", 304, "Not Modified", {}, None
        )
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"cached payload"
    assert changed is False


def test_conditional_fetch_200_with_new_etag(tmp_path):
    cache = tmp_path / "data.bin"
    cache.write_bytes(b"old")
    etag_file = tmp_path / "data.bin.etag"
    etag_file.write_text('etag: "old"\n', encoding="utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = b"new data"
    mock_resp.getheader.side_effect = lambda h, d=None: {
        "ETag": '"new456"'
    }.get(h, d)
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    with patch("ingest_utils.urllib.request.urlopen") as mock_open:
        mock_open.return_value = mock_resp
        content, changed = u.conditional_fetch("https://example.com/d", cache)
    assert content == b"new data"
    assert changed is True
    assert '"new456"' in etag_file.read_text(encoding="utf-8")
