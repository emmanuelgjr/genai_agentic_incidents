"""Track per-source consecutive-failure counts across weekly refreshes and
turn a persistently-dead ingest into a loud, unmissable signal instead of a
per-run ``::warning::`` that nobody reads.

Why this exists (WS4-T9): ``auto-refresh.yml`` runs every ingest step with
``continue-on-error: true`` so one flaky source doesn't block the others, and
only aborts the whole job if ALL of them fail on the SAME run. A single
source that 404s every week forever is invisible to that logic — the job
keeps reporting overall ``success`` while one source silently rots. See
MASTER_IMPROVEMENT_PLAN.md WS4-T9 for the AIRI Navigator instance of this
pattern; this module is the general fix.

State is persisted (committed to the repo, alongside the ingest/*.json
snapshots it watches over) at ``ingest/_state/source_health.json`` — a
subdirectory of ``ingest/`` so it is invisible to
``merge_and_dedupe.py``'s ``INGEST.glob("*.json")`` (non-recursive: it only
matches direct children of ``ingest/``, never ``ingest/_state/*``).

A source can be deliberately silenced past the threshold by hand-editing its
entry in the state file to add ``"paused": true``, a non-empty
``"paused_reason"``, and a ``"paused_until"`` (ISO date) — a visible,
git-blamed, auditable, TIME-BOXED override for a source under active
triage/remediation, not a silent bypass. This is not "never hand-edit" data
(it is pipeline health state, not corpus data); the override is required to
say *why* and *until when* in the same commit that pauses it. All three are
mandatory: ``"paused": true`` with a missing/empty reason, a missing
``paused_until``, or a ``paused_until`` that has already passed is an
INVALID or EXPIRED pause and is deliberately NOT honored — the source goes
back to failing loudly, exactly like an un-paused one, until someone renews
the pause with a fresh reason and date. A silence switch nobody has to
re-justify is indistinguishable from the ``::warning::`` this task exists to
abolish.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE_PATH = ROOT / "ingest" / "_state" / "source_health.json"
DEFAULT_THRESHOLD = 3  # consecutive failed refreshes before a source goes "stale"


def utc_today() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_state(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def pause_status(entry: dict, today: str) -> str:
    """Classify a source's pause request. Returns one of:

    ``"none"``      — not paused, nothing to honor.
    ``"active"``     — paused, with a reason and an unexpired ``paused_until``.
    ``"invalid"``    — ``paused: true`` but missing/empty reason or expiry.
    ``"expired"``    — otherwise-valid pause whose ``paused_until`` has passed.

    Only ``"active"`` silences the loud-failure gate. ``"invalid"`` and
    ``"expired"`` are surfaced as errors, not silently ignored, so a stale
    or malformed pause can't hide a source forever.
    """
    if not entry.get("paused"):
        return "none"
    reason = (entry.get("paused_reason") or "").strip()
    until = (entry.get("paused_until") or "").strip()
    if not reason or not until:
        return "invalid"
    if until < today:
        return "expired"
    return "active"


def update_source_health(
    state: dict,
    outcomes: dict[str, str],
    *,
    today: str,
    threshold: int = DEFAULT_THRESHOLD,
) -> tuple[dict, list[str], list[str], dict[str, str]]:
    """Apply this run's per-source outcomes to ``state``.

    Returns ``(new_state, stale_sources, degraded_sources, pause_notices)``:

    - ``stale_sources``: sources at/above ``threshold`` consecutive failures
      whose pause (if any) is NOT ``"active"`` (see :func:`pause_status`) —
      the "fail loudly" case.
    - ``degraded_sources``: failed this run, below threshold — still just a
      warning.
    - ``pause_notices``: ``{source: pause_status}`` for every stale source
      whose pause status is ``"active"``, ``"invalid"``, or ``"expired"`` —
      so callers can report *why* a stale source did or didn't trip the gate.

    ``state`` is not mutated in place; a new dict is returned so callers can
    diff old vs. new easily in tests.
    """
    new_state: dict = {k: dict(v) for k, v in state.items()}
    stale: list[str] = []
    degraded: list[str] = []
    pause_notices: dict[str, str] = {}

    for source, outcome in outcomes.items():
        entry = dict(new_state.get(source, {}))
        succeeded = outcome == "success"

        if succeeded:
            entry["consecutive_failures"] = 0
            entry["last_success"] = today
            entry["last_outcome"] = "success"
            entry["status"] = "ok"
        else:
            entry["consecutive_failures"] = int(entry.get("consecutive_failures", 0)) + 1
            entry["last_attempt"] = today
            entry["last_outcome"] = outcome
            if entry["consecutive_failures"] >= threshold:
                entry["status"] = "stale"
            else:
                entry["status"] = "degraded"

        entry.setdefault("consecutive_failures", 0)
        new_state[source] = entry

        if not succeeded:
            if entry["status"] == "stale":
                p = pause_status(entry, today)
                if p == "active":
                    pause_notices[source] = p
                else:
                    stale.append(source)
                    if p in ("invalid", "expired"):
                        pause_notices[source] = p
            else:
                degraded.append(source)

    return new_state, stale, degraded, pause_notices


def render_summary(state: dict, outcomes: dict[str, str]) -> str:
    lines = ["### Source health (consecutive-failure tracking)", "", "| Source | This run | Consecutive failures | Status | Paused |", "|---|---|---|---|---|"]
    for source in sorted(outcomes):
        entry = state.get(source, {})
        lines.append(
            f"| {source} | {outcomes[source]} | {entry.get('consecutive_failures', 0)} "
            f"| {entry.get('status', 'unknown')} | {'yes' if entry.get('paused') else 'no'} |"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--outcomes-json", required=True,
        help='JSON object mapping source name -> step outcome, e.g. '
             '\'{"airi_navigator": "failure", "aiaaic_sheet": "success"}\'',
    )
    parser.add_argument("--state-file", type=Path, default=DEFAULT_STATE_PATH)
    parser.add_argument("--threshold", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--today", default=None, help="Override for tests; defaults to UTC today")
    parser.add_argument(
        "--summary-file", type=Path, default=None,
        help="Append the markdown summary here (e.g. $GITHUB_STEP_SUMMARY)",
    )
    args = parser.parse_args(argv)

    outcomes = json.loads(args.outcomes_json)
    today = args.today or utc_today()

    state = load_state(args.state_file)
    new_state, stale, degraded, pause_notices = update_source_health(
        state, outcomes, today=today, threshold=args.threshold
    )
    save_state(args.state_file, new_state)

    summary = render_summary(new_state, outcomes)
    print(summary)
    if args.summary_file:
        with args.summary_file.open("a", encoding="utf-8") as f:
            f.write(summary + "\n")

    for s, p in pause_notices.items():
        entry = new_state[s]
        if p == "active":
            print(f"::warning::{s} has failed {entry['consecutive_failures']} consecutive "
                  f"refreshes and is stale, but alerting is paused until {entry.get('paused_until')} "
                  f"({entry.get('paused_reason')}).")
        elif p == "invalid":
            print(f"::error::{s} is marked paused but the pause is INVALID (missing "
                  f"paused_reason or paused_until in ingest/_state/source_health.json) — "
                  "not honoring it. Add both, or this source keeps failing loudly.")
        elif p == "expired":
            print(f"::error::{s}'s pause EXPIRED on {entry.get('paused_until')} — not honoring "
                  "it. Renew paused_until with a fresh reason, or resolve the source.")

    for s in degraded:
        print(f"::warning::{s} failed this refresh ({new_state[s]['consecutive_failures']}/"
              f"{args.threshold} consecutive failures so far).")

    if stale:
        names = ", ".join(sorted(stale))
        print(
            f"::error::{names} — {len(stale)} source(s) failed {args.threshold}+ consecutive "
            "refreshes. This is no longer a per-run warning: the source is stale and the run "
            "is failing loudly on purpose. Investigate, retire the source (tombstone its "
            "corpus entries per Invariant 3, don't delete), or pause this check with a recorded "
            "reason in ingest/_state/source_health.json while remediation is tracked."
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
