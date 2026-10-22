# Queue rows with part of speech `phr`

*Observed 2026-10-22 (build cycle 1 and the eighty-third lint pass). No tool change proposed.*

The founding word lists queued fixed expressions as `phr` rows, but the house rule ([what-counts-as-a-headword](../decisions/what-counts-as-a-headword.md), style guide section 10) puts idioms and fixed phrases in `phrases[]` of their keyword entry. Of the fifteen `phr` rows, twelve are now marked `duplicate`: nine were already covered by a keyword entry (*good morning*, *for example*, *in fact*, *of course*, *see you*, *take care*, *by the way*, *my pleasure*, *go to bed*), and two were added as phrases on 2026-10-22 (*excuse me* to `excuse-v`, *good night* to `night-n`). The twelfth, *thank you*, became `thank-you-interj`, following `thanks-interj`.

Three rows remain `pending`; a build that claims one should not draft a `phr` entry but add the phrase to the keyword entry (a rewrite, through the full pipeline), or draft that entry if it is missing:

- *you are welcome*: under `welcome-adj` (queued, band 3), or point to the note in `welcome-interj`.
- *never mind*: under `mind-v` (queued, band 3; first verb).
- *bless you*: under `bless-v` (queued 2026-10-22, band 3).

Working rule until a decision says otherwise: before drafting any `phr` row, check the keyword entry's phrases.
