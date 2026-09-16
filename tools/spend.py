#!/usr/bin/env python3
"""spend.py -- the OpenRouter spending ledger (wiki/conventions.md section 5).

The ledger is config/budget-ledger.json, written only by this tool:

    {"_doc": "...",
     "daily_cap_usd": 5.0,
     "date": "YYYY-MM-DD",            # the UTC day the running totals belong to
     "spent_usd": 0.0,
     "calls": [{"ts", "run_id", "purpose", "model", "cost_usd",
                "tokens_in", "tokens_out"}, ...],
     "history": {"YYYY-MM-DD": spent_usd, ...}}

At the first use after UTC midnight the old day's total moves into "history"
and "spent_usd"/"calls" reset (the rollover is persisted by whichever
subcommand notices it). Money is rounded to 6 decimals. This tool never reads
or prints OPENROUTER_API_KEY.

Usage:
    python3 tools/spend.py check --cost 0.05
        exit 0 and print the remaining budget when today's spend plus the
        estimate stays within the cap; exit 1 with a message otherwise.
    python3 tools/spend.py record --cost 0.0123 --purpose review --model openai/x \\
        [--tokens-in N] [--tokens-out N] [--run-id R]
        append the billed call and print the new daily total. --run-id
        defaults to the content of .tmp/run-id when present, else "local".
    python3 tools/spend.py status
        print date, spent, cap, remaining, number of calls and the last 7
        days of history.
    --ledger PATH (before the subcommand) overrides the ledger file, for tests.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LEDGER = ROOT / "config" / "budget-ledger.json"
DEFAULT_CAP_USD = 5.0
DOC = ("OpenRouter spending ledger, see wiki/conventions.md section 5. Written only by "
       "tools/spend.py: 'check --cost' refuses an estimate that would exceed daily_cap_usd "
       "for the current UTC day, 'record --cost' appends the billed usage.cost of a call. "
       "At UTC midnight the day's total moves into history and spent_usd/calls reset. "
       "Amounts are US dollars rounded to 6 decimals.")


def money(x: float) -> float:
    return round(float(x), 6)


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_ledger(date: str | None = None, cap: float = DEFAULT_CAP_USD) -> dict:
    return {
        "_doc": DOC,
        "daily_cap_usd": money(cap),
        "date": date or today_utc(),
        "spent_usd": 0.0,
        "calls": [],
        "history": {},
    }


def default_run_id(root: Path = ROOT) -> str:
    """The content of .tmp/run-id (repository root, then the current directory), else 'local'."""
    for cand in (root / ".tmp" / "run-id", Path(".tmp") / "run-id"):
        try:
            text = cand.read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if text:
            return text
    return "local"


def save_ledger(path: Path, ledger: dict) -> None:
    """Write atomically: a temp file in the same directory, then os.replace."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".budget-ledger.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(ledger, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def rollover(ledger: dict, today: str) -> str | None:
    """Move an old day's total into history in place. Return the old date if rolled over."""
    old = ledger.get("date")
    if old == today:
        return None
    if old and old > today:
        print(f"warning: ledger date {old} is later than today {today}; clock skew? "
              f"leaving the ledger as it is", file=sys.stderr)
        return None
    history = ledger.setdefault("history", {})
    if old:
        history[old] = money(history.get(old, 0.0) + float(ledger.get("spent_usd", 0.0)))
    ledger["date"] = today
    ledger["spent_usd"] = 0.0
    ledger["calls"] = []
    return old


def load_ledger(path: Path, today: str | None = None, create: bool = True) -> tuple[dict, bool]:
    """Load the ledger, apply a day rollover if due, and persist any change.

    Returns (ledger, changed). A missing file is created fresh when create is
    true (a note goes to stderr), else FileNotFoundError is raised.
    """
    path = Path(path)
    today = today or today_utc()
    changed = False
    if path.is_file():
        with open(path, encoding="utf-8") as fh:
            ledger = json.load(fh)
        for key, default in new_ledger(today).items():
            if key not in ledger:
                ledger[key] = default
                changed = True
    elif create:
        ledger = new_ledger(today)
        changed = True
        print(f"note: {path} did not exist; created a fresh ledger "
              f"(cap ${DEFAULT_CAP_USD:.2f}/day)", file=sys.stderr)
    else:
        raise FileNotFoundError(path)
    old = rollover(ledger, today)
    if old is not None:
        changed = True
        print(f"note: day rollover {old} -> {today}; "
              f"${ledger['history'][old]:.6f} moved into history", file=sys.stderr)
    if changed:
        save_ledger(path, ledger)
    return ledger, changed


def remaining(ledger: dict) -> float:
    return money(float(ledger["daily_cap_usd"]) - float(ledger["spent_usd"]))


def check(path: Path, cost: float, today: str | None = None) -> tuple[bool, float, dict]:
    """Return (ok, remaining_after, ledger): ok when spent + cost <= cap."""
    if cost < 0:
        raise ValueError("cost must be >= 0")
    ledger, _ = load_ledger(path, today)
    projected = money(float(ledger["spent_usd"]) + cost)
    ok = projected <= float(ledger["daily_cap_usd"])
    return ok, money(float(ledger["daily_cap_usd"]) - projected), ledger


def record(path: Path, cost: float, purpose: str, model: str, tokens_in: int = 0,
           tokens_out: int = 0, run_id: str | None = None, today: str | None = None,
           ts: str | None = None) -> dict:
    """Append a billed call, add it to today's total, save, and return the ledger."""
    if cost < 0:
        raise ValueError("cost must be >= 0")
    ledger, _ = load_ledger(path, today)
    entry = {
        "ts": ts or now_iso(),
        "run_id": run_id or default_run_id(),
        "purpose": purpose,
        "model": model,
        "cost_usd": money(cost),
        "tokens_in": int(tokens_in),
        "tokens_out": int(tokens_out),
    }
    ledger["calls"].append(entry)
    ledger["spent_usd"] = money(float(ledger["spent_usd"]) + cost)
    save_ledger(path, ledger)
    return ledger


def status_text(ledger: dict) -> str:
    cap = float(ledger["daily_cap_usd"])
    spent = float(ledger["spent_usd"])
    lines = [
        f"date:      {ledger['date']}",
        f"spent:     ${spent:.6f}",
        f"cap:       ${cap:.6f}",
        f"remaining: ${remaining(ledger):.6f}",
        f"calls:     {len(ledger['calls'])}",
        "history (last 7 days):",
    ]
    history = ledger.get("history", {})
    recent = sorted(history.items(), reverse=True)[:7]
    if recent:
        for date, amount in recent:
            lines.append(f"  {date}  ${float(amount):.6f}")
    else:
        lines.append("  (none)")
    return "\n".join(lines)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="OpenRouter spending ledger (config/budget-ledger.json). "
                    "'check' refuses when an estimate would exceed the daily cap, "
                    "'record' appends a billed call, 'status' prints the day and history. "
                    "The day rolls over at UTC midnight. Never touches OPENROUTER_API_KEY.")
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER,
                        help=f"ledger file (default: {DEFAULT_LEDGER.relative_to(ROOT)})")
    sub = parser.add_subparsers(dest="command", required=True)

    p_check = sub.add_parser("check", help="exit 0 if today's spend plus --cost fits the cap")
    p_check.add_argument("--cost", type=float, required=True, help="estimated cost in USD")

    p_rec = sub.add_parser("record", help="append a billed call and add it to today's total")
    p_rec.add_argument("--cost", type=float, required=True, help="billed cost in USD (usage.cost)")
    p_rec.add_argument("--purpose", required=True, help="what the call was for")
    p_rec.add_argument("--model", required=True, help="model slug that answered")
    p_rec.add_argument("--tokens-in", type=int, default=0)
    p_rec.add_argument("--tokens-out", type=int, default=0)
    p_rec.add_argument("--run-id", default=None,
                       help="run id (default: content of .tmp/run-id, else 'local')")

    sub.add_parser("status", help="print date, spent, cap, remaining, calls and history")

    args = parser.parse_args(argv)

    if args.command == "check":
        if args.cost < 0:
            parser.error("--cost must be >= 0")
        ok, left, ledger = check(args.ledger, args.cost)
        cap = float(ledger["daily_cap_usd"])
        spent = float(ledger["spent_usd"])
        if ok:
            print(f"ok: ${left:.6f} remaining today after this ${args.cost:.6f} call "
                  f"(spent ${spent:.6f} of ${cap:.2f} on {ledger['date']})")
            return 0
        print(f"refused: estimated ${args.cost:.6f} would bring today's spend to "
              f"${spent + args.cost:.6f}, over the ${cap:.2f} cap "
              f"(spent ${spent:.6f}, ${remaining(ledger):.6f} left on {ledger['date']})")
        return 1

    if args.command == "record":
        if args.cost < 0:
            parser.error("--cost must be >= 0")
        ledger = record(args.ledger, args.cost, args.purpose, args.model,
                        args.tokens_in, args.tokens_out, args.run_id)
        cap = float(ledger["daily_cap_usd"])
        spent = float(ledger["spent_usd"])
        print(f"recorded ${args.cost:.6f} for {args.purpose} ({args.model}); "
              f"today's total ${spent:.6f} of ${cap:.2f}, {len(ledger['calls'])} call(s)")
        if spent > cap:
            print(f"warning: today's spend ${spent:.6f} is over the ${cap:.2f} cap",
                  file=sys.stderr)
        return 0

    if args.command == "status":
        ledger, _ = load_ledger(args.ledger)
        print(status_text(ledger))
        return 0

    parser.error("unknown command")
    return 2


if __name__ == "__main__":
    sys.exit(main())
