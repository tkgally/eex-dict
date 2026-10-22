# Queue rows with part of speech `phr`

*Observed 2026-10-22 (build cycle 1 and the eighty-third lint pass). No tool change proposed.*

The founding lists queued fixed expressions as `phr` rows, but the house rule ([what-counts-as-a-headword](../decisions/what-counts-as-a-headword.md), style guide section 10) puts them in `phrases[]` of the keyword entry. Of fifteen `phr` rows, twelve are now `duplicate`: nine were already phrases of a keyword entry, *excuse me* and *good night* were added to `excuse-v` and `night-n`, and *thank you* became `thank-you-interj`.

Three remain `pending`. Do not draft a `phr` entry: add the phrase to its keyword entry (a rewrite, full pipeline), drafting that entry first if missing: *you are welcome* (`welcome-adj`), *never mind* (`mind-v`), *bless you* (`bless-v`, queued 2026-10-22).
