"""Pytest setup: make scripts/ importable as a top-level package."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "real_robots: exercise ingest.common's real robots.txt logic "
        "instead of the autouse allow-everything stub below.",
    )


@pytest.fixture(autouse=True)
def _ingest_common_test_safety(request, monkeypatch):
    """Every test gets a clean, network-free ingest.common:

    - the per-host rate-limit and robots.txt caches are reset, so no test
      can leak a real time.sleep() (or a poisoned robots verdict) into
      another test via shared module state;
    - robots.txt checks default to "allowed", so tests exercising
      robust_fetch()/conditional_fetch()'s retry mechanics (which mock
      urllib.request.urlopen directly) don't ALSO have that same mock
      intercept an internal robots.txt sub-fetch and short-circuit
      differently than they expect.

    Tests that specifically exercise the real robots.txt logic mark
    themselves ``@pytest.mark.real_robots`` to opt out of the stub.
    """
    import ingest.common as common

    common._reset_state_for_tests()
    if not request.node.get_closest_marker("real_robots"):
        monkeypatch.setattr(common, "robots_allowed", lambda url: True)
    yield
    common._reset_state_for_tests()
