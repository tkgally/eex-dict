# Band vote: a second unbanded vote on one day overwrites the first

*Observed 2026-10-24 (eighty-sixth lint); recurred 2026-10-28.*

`tools/band_vote.py run --unbanded` wrote the day's `votes-unbanded.tsv` from scratch, losing an earlier vote's rows, and `apply --votes` resolved paths only against the vote directory. Fixed 2026-10-29 (ninety-third pass): `run` merges with an existing file (new votes win; unit test), and `--votes` accepts a path from the working directory.

## 2026-11-03, hundredth pass: stale cache

A second `run --unbanded` in one session reused the first run's cached replies (`.tmp/band-vote/unbanded/chunk000-*`, keyed by chunk number, not content) and failed with a `KeyError` on a slug no longer asked. Worked around by moving the cache aside. Fix due a later run.
