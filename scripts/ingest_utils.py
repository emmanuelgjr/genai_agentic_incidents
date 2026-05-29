"""Shared utilities for ingest scripts: retry logic and conditional fetching."""

from __future__ import annotations

import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_AGENT = "Mozilla/5.0 (genai_incidents/2.0; +https://github.com/emmanuelgjr)"


def robust_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
) -> bytes:
    """Fetch URL content with retry logic and disk caching.

    Returns cached content if the cache file exists and is at least
    *min_cache_bytes* large.  Otherwise fetches from *url* with up to
    *max_retries* attempts using exponential backoff (2 s, 4 s, 8 s, …).
    """
    if cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes:
        return cache_path.read_bytes()

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            return data
        except (urllib.error.URLError, urllib.error.HTTPError,
                TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                delay = 2 ** attempt
                print(
                    f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}",
                    file=sys.stderr,
                )
                time.sleep(delay)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")


def _read_etag_sidecar(etag_path: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not etag_path.exists():
        return result
    for line in etag_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("etag: "):
            result["etag"] = line[6:].strip()
        elif line.startswith("last-modified: "):
            result["last-modified"] = line[15:].strip()
    return result


def _write_etag_sidecar(etag_path: Path, etag: str | None, last_mod: str | None) -> None:
    lines: list[str] = []
    if etag:
        lines.append(f"etag: {etag}")
    if last_mod:
        lines.append(f"last-modified: {last_mod}")
    if lines:
        etag_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def conditional_fetch(
    url: str,
    cache_path: Path,
    *,
    timeout: int = 60,
    max_retries: int = 3,
    min_cache_bytes: int = 1000,
    headers: dict[str, str] | None = None,
) -> tuple[bytes, bool]:
    """Fetch URL with ETag/Last-Modified conditional request support.

    Returns ``(content, changed)`` where *changed* is False if the server
    returned 304 Not Modified (cache is still valid).
    """
    etag_path = Path(str(cache_path) + ".etag")
    cache_warm = cache_path.exists() and cache_path.stat().st_size >= min_cache_bytes

    hdrs = {"User-Agent": USER_AGENT}
    if headers:
        hdrs.update(headers)

    if cache_warm:
        saved = _read_etag_sidecar(etag_path)
        if saved.get("etag"):
            hdrs["If-None-Match"] = saved["etag"]
        if saved.get("last-modified"):
            hdrs["If-Modified-Since"] = saved["last-modified"]

    last_err: Exception | None = None
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                etag = resp.getheader("ETag")
                last_mod = resp.getheader("Last-Modified")
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_bytes(data)
            _write_etag_sidecar(etag_path, etag, last_mod)
            return data, True
        except urllib.error.HTTPError as e:
            if e.code == 304:
                return cache_path.read_bytes(), False
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries:
                time.sleep(2 ** attempt)
                print(f"  [retry] attempt {attempt}/{max_retries} for {url}: {e}", file=sys.stderr)

    raise RuntimeError(f"Failed to fetch {url} after {max_retries} attempts: {last_err}")
