# Band vote, 2026-10-31 (unbanded rows)

The ninety-fifth lint pass ran `tools/band_vote.py run --unbanded` on the 77 queue rows that tools had queued since the last vote (US$0.012). `votes-unbanded.tsv` holds the three word-list votes and the lower median. Two wide splits were settled in `settled.tsv`, both at the lower median: `kid-v` 2 and `knitwear-n` 4. `apply --votes votes-unbanded.tsv` turned all 77 rows to `pending` with their bands. The scale and the method are in [rebanding](../../wiki/decisions/rebanding.md).

The ninety-sixth lint pass (run 20261031T192241Z-0rh14y) voted on the 84 rows queued since then (US$0.011); the new votes were merged into `votes-unbanded.tsv`. One more wide split was settled at the lower median: `obtainable-adj` 4. All 84 rows are now `pending` with their bands.
