#!/usr/bin/env python3
"""Keep a scheduled run short: record its start, count its merged cycles, and
say whether another cycle may begin.

    python3 tools/run_clock.py start    # first command of the run; a repeat keeps the first time
    python3 tools/run_clock.py done     # after each cycle's merge: count it, then report
    python3 tools/run_clock.py          # elapsed minutes, cycles, "next cycle: yes|no", "wrap up now" once due

A Routine run is a series of cycles (select a mode, do it, merge its PR). Entry
quality fell in the later cycles of long runs (2026-09-26: thirteen and fifteen
cycles), so a run stops after MAX_CYCLES merged cycles. A new cycle may also
begin only until NEW_CYCLE_UNTIL minutes have passed; from WRAP_UP_AT minutes
the cycle in progress stops its content work and wraps up. The start time and
the cycle count are kept outside the repository (they survive a compacted
conversation, never a new container); a start file older than STALE_AFTER
minutes belongs to an earlier run in the same container and is replaced.
"""
import argparse
import sys
import time
from pathlib import Path

START_FILE = Path("/tmp") / f"{Path(__file__).resolve().parents[1].name}-run-start"
MAX_CYCLES = 4
NEW_CYCLE_UNTIL = 105
WRAP_UP_AT = 130
STALE_AFTER = 240


def read_state(path: Path, now: float):
    """Return (start, cycles done), or None when there is no current run."""
    try:
        parts = path.read_text().split()
        start = float(parts[0])
        cycles = int(parts[1]) if len(parts) > 1 else 0
    except (OSError, ValueError, IndexError):
        return None
    if now - start > STALE_AFTER * 60 or start > now + 60:
        return None
    return start, cycles


def write_state(path: Path, start: float, cycles: int) -> None:
    path.write_text(f"{start:.0f} {cycles}\n")


def report(elapsed_min: float, new_cycle_until: int, wrap_up_at: int,
           cycles: int = 0, max_cycles: int = MAX_CYCLES) -> list:
    lines = [f"elapsed: {elapsed_min:.0f} min", f"cycles merged: {cycles} of at most {max_cycles}"]
    if cycles >= max_cycles:
        lines.append(f"next cycle: no ({max_cycles} cycles merged): end the run")
    elif elapsed_min < new_cycle_until:
        lines.append(f"next cycle: yes (a new cycle may start until {new_cycle_until} min)")
    else:
        lines.append(f"next cycle: no (past {new_cycle_until} min): finish this cycle and end the run")
    if elapsed_min >= wrap_up_at:
        lines.append(f"wrap up now: past {wrap_up_at} min, stop content work and go to the wrap-up")
    else:
        lines.append(f"content work may continue until {wrap_up_at} min")
    return lines


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Run clock for multi-cycle Routine runs.")
    ap.add_argument("action", nargs="?", choices=["start", "check", "done"], default="check",
                    help="start the run, check it, or count a merged cycle (done)")
    ap.add_argument("--reset", action="store_true", help="with start: replace an existing start time")
    ap.add_argument("--new-cycle-until", type=int, default=NEW_CYCLE_UNTIL)
    ap.add_argument("--wrap-up-at", type=int, default=WRAP_UP_AT)
    ap.add_argument("--max-cycles", type=int, default=MAX_CYCLES)
    ap.add_argument("--file", type=Path, default=START_FILE, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    now = time.time()
    state = read_state(args.file, now)
    if args.action == "start":
        if state is None or args.reset:
            state = (now, 0)
            write_state(args.file, *state)
            print(f"run clock started {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(now))}")
        else:
            print(f"run clock already running since "
                  f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(state[0]))}; kept")
    elif state is None:
        state = (now, 0)
        write_state(args.file, *state)
        print("no start time recorded: the clock starts now")
    if args.action == "done":
        state = (state[0], state[1] + 1)
        write_state(args.file, *state)
        print(f"cycle {state[1]} counted")
    start, cycles = state
    for line in report((now - start) / 60, args.new_cycle_until, args.wrap_up_at, cycles, args.max_cycles):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
