# Band vote, 2026-10-30 (unbanded rows)

The ninety-fourth lint pass ran `tools/band_vote.py run --unbanded` on the 81 queue rows that tools had queued since the last vote (US$0.013). `votes-unbanded.tsv` holds the three word-list votes and the lower median. Two wide splits were settled in `settled.tsv`, both at the lower median: `maam-n` 3 and `underestimate-v` 3. `apply --votes votes-unbanded.tsv` turned all 81 rows to `pending` with their bands. No built entry was among them, so no restamp was needed. The scale and the method are in [rebanding](../../wiki/decisions/rebanding.md).
