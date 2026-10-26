# Band vote, 2026-10-26 (unbanded rows)

The eighty-eighth lint pass ran `tools/band_vote.py run --unbanded` on the 64 queue rows that tools had queued since 2026-10-25 (US$0.011). `votes-unbanded.tsv` holds the three word-list votes and the lower median; two wide splits (`shampoo-v`, `thunder-v`, votes 4 3 2) were settled at the lower median, 3 (`settled.tsv`). `apply` turned all 64 rows to `pending` with their bands. The scale and the method are in [rebanding](../../wiki/decisions/rebanding.md).
