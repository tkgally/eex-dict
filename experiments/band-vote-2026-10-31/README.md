# Band vote, 2026-10-31 (unbanded rows)

The ninety-fifth lint pass ran `tools/band_vote.py run --unbanded` on the 77 queue rows that tools had queued since the last vote (US$0.012). `votes-unbanded.tsv` holds the three word-list votes and the lower median. Two wide splits were settled in `settled.tsv`, both at the lower median: `kid-v` 2 and `knitwear-n` 4. `apply --votes votes-unbanded.tsv` turned all 77 rows to `pending` with their bands. The scale and the method are in [rebanding](../../wiki/decisions/rebanding.md).
