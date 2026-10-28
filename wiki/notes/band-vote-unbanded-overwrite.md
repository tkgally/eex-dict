# Band vote: a second unbanded vote on one day overwrites the first

*Observed 2026-10-24, eighty-sixth lint pass.*

`tools/band_vote.py run --unbanded` writes `experiments/band-vote-<date>/votes-unbanded.tsv` from scratch. The day's second unbanded vote replaced the 16 rows of the first, which had already been applied. Those votes are now kept only in git history. The lint pass merged the old rows back by hand, so the file holds all 65.

A second problem: `apply --votes` takes a path relative to the vote directory, not the working directory. A path from the repository root fails with a doubled path.

Recurred 2026-10-28 (ninety-second pass): the day's second vote overwrote the first lint's 45 rows; the old file was restored from git and the new 54 rows kept as `votes-unbanded-2.tsv`. Fix due.

Possible fix for a later run: append to or merge with an existing file of the same name (new votes win), and accept either kind of path. No change yet.
