# Band vote, 2026-11-02 (unbanded rows)

The ninety-eighth lint pass (run 20261102T124658Z-rscqyg) ran `tools/band_vote.py run --unbanded` on the 48 queue rows that tools had queued since the last vote (US$0.008). `votes-unbanded.tsv` holds the three word-list votes and the lower median. No split was wider than one band, so nothing needed settling. `apply --votes votes-unbanded.tsv` turned all 48 rows to `pending` with their bands. None of them has an entry yet, so no entry needed restamping. The scale and the method are in [rebanding](../../wiki/decisions/rebanding.md).
