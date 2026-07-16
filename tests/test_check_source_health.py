"""Tests for scripts/check_source_health.py (WS4-T9).

The load-bearing assertion (test_source_fails_loudly_after_threshold_consecutive_failures)
is the one the plan asks for explicitly: a source that has 404'd every week
for N consecutive refreshes must no longer be able to pass a refresh as a
mere ``::warning::`` — the check must return a failing exit status. This is
exactly the AIRI Navigator situation (dead since 2026-06-07, 6 consecutive
failures as of 2026-07-12) that a same-run ``continue-on-error`` +
all-three-must-fail abort threshold could not catch.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_source_health as h  # noqa: E402


def test_single_failure_is_only_degraded_not_stale():
    state, stale, degraded = h.update_source_health(
        {}, {"airi_navigator": "failure"}, today="2026-06-07", threshold=3
    )
    assert state["airi_navigator"]["consecutive_failures"] == 1
    assert state["airi_navigator"]["status"] == "degraded"
    assert stale == []
    assert degraded == ["airi_navigator"]


def test_source_fails_loudly_after_threshold_consecutive_failures():
    """The core WS4-T9 fix: N consecutive failures can no longer pass as a warning."""
    state: dict = {}
    dates = ["2026-06-07", "2026-06-14", "2026-06-21"]
    stale: list[str] = []
    for d in dates:
        state, stale, _degraded = h.update_source_health(
            state, {"airi_navigator": "failure"}, today=d, threshold=3
        )
    assert state["airi_navigator"]["consecutive_failures"] == 3
    assert state["airi_navigator"]["status"] == "stale"
    assert stale == ["airi_navigator"], (
        "a source at/above the consecutive-failure threshold must be reported "
        "as stale (loud), not silently folded into a warning"
    )


def test_success_resets_consecutive_failures():
    state, _, _ = h.update_source_health(
        {"airi_navigator": {"consecutive_failures": 5, "status": "stale"}},
        {"airi_navigator": "success"},
        today="2026-07-19",
        threshold=3,
    )
    assert state["airi_navigator"]["consecutive_failures"] == 0
    assert state["airi_navigator"]["status"] == "ok"
    assert state["airi_navigator"]["last_success"] == "2026-07-19"


def test_paused_stale_source_does_not_report_as_newly_stale():
    """A hand-edited, reasoned pause silences the loud gate without hiding status."""
    prior = {
        "airi_navigator": {
            "consecutive_failures": 6,
            "status": "stale",
            "paused": True,
            "paused_reason": "WS4-T9 triage in progress, retire-or-replace decision pending",
        }
    }
    state, stale, degraded = h.update_source_health(
        prior, {"airi_navigator": "failure"}, today="2026-07-19", threshold=3
    )
    assert state["airi_navigator"]["status"] == "stale"
    assert state["airi_navigator"]["consecutive_failures"] == 7
    assert stale == [], "a paused source must not trip the loud-failure gate"
    assert degraded == []


def test_independent_sources_tracked_independently():
    state, stale, degraded = h.update_source_health(
        {}, {"airi_navigator": "failure", "aiaaic_sheet": "success", "oecd_aim": "failure"},
        today="2026-06-07", threshold=3,
    )
    assert state["aiaaic_sheet"]["status"] == "ok"
    assert state["airi_navigator"]["status"] == "degraded"
    assert state["oecd_aim"]["status"] == "degraded"
    assert stale == []
    assert set(degraded) == {"airi_navigator", "oecd_aim"}


def test_state_round_trips_through_disk(tmp_path):
    state_file = tmp_path / "source_health.json"
    state, _, _ = h.update_source_health({}, {"kev": "failure"}, today="2026-06-07")
    h.save_state(state_file, state)
    reloaded = h.load_state(state_file)
    assert reloaded == state
    assert json.loads(state_file.read_text(encoding="utf-8")) == state


def test_cli_exits_nonzero_when_a_source_crosses_threshold(tmp_path):
    state_file = tmp_path / "source_health.json"
    # Prime the state file with 2 prior consecutive failures, then feed a 3rd.
    h.save_state(
        state_file,
        {"airi_navigator": {"consecutive_failures": 2, "status": "degraded"}},
    )
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"airi_navigator": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-06-21",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 1, result.stdout + result.stderr
    assert "::error::" in result.stdout
    new_state = json.loads(state_file.read_text(encoding="utf-8"))
    assert new_state["airi_navigator"]["status"] == "stale"


def test_cli_exits_zero_and_warns_when_below_threshold(tmp_path):
    state_file = tmp_path / "source_health.json"
    result = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve().parents[1] / "scripts" / "check_source_health.py"),
            "--outcomes-json", json.dumps({"aiaaic_sheet": "failure"}),
            "--state-file", str(state_file),
            "--threshold", "3",
            "--today", "2026-06-07",
        ],
        capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "::warning::" in result.stdout
    assert "::error::" not in result.stdout


@pytest.mark.parametrize("outcome", ["failure", "cancelled", "skipped"])
def test_any_non_success_outcome_counts_as_a_failure(outcome):
    state, _, degraded = h.update_source_health(
        {}, {"src": outcome}, today="2026-06-07", threshold=3
    )
    assert state["src"]["consecutive_failures"] == 1
    assert degraded == ["src"]
