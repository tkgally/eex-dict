# band_vote.py writes a fixed date on settled rows

Observed 2026-10-31: `tools/band_vote.py apply` noted every settled row `band vote 2026-10-24, settled: ...` (a hard-coded date), so `kid-v` (settled 2026-10-31) and `real-adv` (2026-11-03) showed the wrong date. **Fixed 2026-11-04** (hundred-and-first lint): the date comes from the votes directory's name (unit test); the three rows corrected by hand.

Still open: a second `apply` of one vote appends the settled note again instead of replacing it (seen on `buy-n`, fixed by hand).
