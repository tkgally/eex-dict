#!/usr/bin/env python3
"""Keep a scheduled run short: record its start, count its merged cycles, and
say whether another cycle may begin.

    python3 tools/run_clock.py start    # first command of the run; a repeat keeps the first time
    python3 tools/run_clock.py done     # after each cycle's merge: count it, then report
    python3 tools/run_clock.py          # elapsed minutes, cycles, "next cycle: yes|no", "wrap up now" once due
    python3 tools/run_clock.py journal  # the run's one journal file: "new <path>" for the first cycle, else "append <path>"

A Routine run is a series of cycles (select a mode, do it, merge its PR). Entry
quality fell in the later cycles of long runs (2026-09-26: thirteen and fifteen
cycles), so a run stops after MAX_CYCLES merged cycles. A new cycle may also
begin only until NEW_CYCLE_UNTIL minutes have passed; from WRAP_UP_AT minutes
the cycle in progress stops its content work and wraps up. The start time and
the cycle count are kept outside the repository (they survive a compacted
conversation, never a new container); a start file older than STALE_AFTER
minutes belongs to an earlier run in the same container and is replaced.

One journal report per run, not per cycle (the owner's ruling E3 of 2026-10-24,
wiki/decisions/process-overhead.md): ``journal`` names the run's file once,
``journal/YYYY-MM-DD.md`` or the next free ``-2``, ``-3`` for the run's start
date, keeps the name with the start time, and prints ``new`` until a cycle has
written the file, then ``append``: each cycle adds a ``## Cycle N: <mode>``
section to that one file and merges it with its own pull request.
"""
import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

START_FILE = Path("/tmp") / f"{Path(__file__).resolve().parents[1].name}-run-start"
MAX_CYCLES = 4
NEW_CYCLE_UNTIL = 105
WRAP_UP_AT = 130
STALE_AFTER = 240


def read_state(path: Path, now: float, with_journal: bool = False):
    """Return (start, cycles done) (and the journal name with ``with_journal``), or None when there is no current run."""
    try:
        parts = path.read_text().split()
        start = float(parts[0])
        cycles = int(parts[1]) if len(parts) > 1 else 0
        journal = parts[2] if len(parts) > 2 else None
    except (OSError, ValueError, IndexError):
        return None
    if now - start > STALE_AFTER * 60 or start > now + 60:
        return None
    return (start, cycles, journal) if with_journal else (start, cycles)


def write_state(path: Path, start: float, cycles: int, journal: str | None = None) -> None:
    path.write_text(f"{start:.0f} {cycles}" + (f" {journal}" if journal else "") + "\n")


def journal_name(start: float, journal_dir: Path) -> str:
    """The first free journal name for the run's start date: YYYY-MM-DD.md, then -2, -3, ..."""
    day = time.strftime("%Y-%m-%d", time.gmtime(start))
    n = 1
    while True:
        name = f"{day}.md" if n == 1 else f"{day}-{n}.md"
        if not (journal_dir / name).exists():
            return name
        n += 1


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
    ap.add_argument("action", nargs="?", choices=["start", "check", "done", "journal"], default="check",
                    help="start the run, check it, count a merged cycle (done), or name the run's journal file")
    ap.add_argument("--journal-dir", type=Path, default=ROOT / "journal", help=argparse.SUPPRESS)
    ap.add_argument("--reset", action="store_true", help="with start: replace an existing start time")
    ap.add_argument("--new-cycle-until", type=int, default=NEW_CYCLE_UNTIL)
    ap.add_argument("--wrap-up-at", type=int, default=WRAP_UP_AT)
    ap.add_argument("--max-cycles", type=int, default=MAX_CYCLES)
    ap.add_argument("--file", type=Path, default=START_FILE, help=argparse.SUPPRESS)
    args = ap.parse_args(argv)

    now = time.time()
    if args.action == "journal":
        full = read_state(args.file, now, with_journal=True)
        if full is None:
            full = (now, 0, None)
        start, cycles, journal = full
        if not journal:
            journal = journal_name(start, args.journal_dir)
            write_state(args.file, start, cycles, journal)
        path = args.journal_dir / journal
        print(("append " if path.exists() else "new ") + f"journal/{journal}")
        return 0
    full = read_state(args.file, now, with_journal=True)
    journal = full[2] if full else None
    state = full[:2] if full else None
    if args.action == "start":
        if state is None or args.reset:
            state = (now, 0)
            journal = None
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
        write_state(args.file, *state, journal)
        print(f"cycle {state[1]} counted")
    start, cycles = state
    for line in report((now - start) / 60, args.new_cycle_until, args.wrap_up_at, cycles, args.max_cycles):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
