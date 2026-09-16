#!/usr/bin/env python3
"""wait.py -- block in the foreground for N seconds, then print "waited Ns".

Used between CI poll attempts in the merge procedure (poll a check run, wait,
poll again) so a session pauses without a shell-specific sleep.

Usage:
    python3 tools/wait.py          # 60 seconds
    python3 tools/wait.py 120      # 120 seconds; the maximum is 600

Exit 0 after waiting; 2 for a value outside 0..600; 130 if interrupted.
"""

from __future__ import annotations

import argparse
import sys
import time

DEFAULT_SECONDS = 60
MAX_SECONDS = 600


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description=f"Block for N seconds (default {DEFAULT_SECONDS}, maximum {MAX_SECONDS}) "
                    "and print 'waited Ns'. Used between CI polls.")
    parser.add_argument("seconds", nargs="?", type=float, default=DEFAULT_SECONDS,
                        help=f"seconds to wait, 0 to {MAX_SECONDS} (default {DEFAULT_SECONDS})")
    args = parser.parse_args(argv)
    if not (0 <= args.seconds <= MAX_SECONDS):
        parser.error(f"seconds must be between 0 and {MAX_SECONDS}, got {args.seconds:g}")
    started = time.monotonic()
    try:
        time.sleep(args.seconds)
    except KeyboardInterrupt:
        print(f"interrupted after {time.monotonic() - started:.0f}s", file=sys.stderr)
        return 130
    print(f"waited {args.seconds:g}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
