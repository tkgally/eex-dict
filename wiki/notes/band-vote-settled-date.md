# band_vote.py writes a fixed date on settled rows

Observed 2026-10-31: `tools/band_vote.py apply` notes every settled row `band vote 2026-10-24, settled: ...` (line 260 hard-codes the date), so `kid-v`, settled 2026-10-31, shows the wrong date. The band is right. Fix due a later run: take the date from the votes directory.
