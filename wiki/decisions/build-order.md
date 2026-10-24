# Build order: milestone 1 first, closure paused above band 2 (2026-10-24)

*The owner's rulings A2 and A3 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)). They supersede the standing ruling of 2026-10-05 that "queue order stands" for milestone 1 ([open-questions](../open-questions.md), Answered 3).*

## A2. Finish milestone 1

Milestone 1 is the defining vocabulary ([size-and-pace](size-and-pace.md)). A **milestone-1 row** is a pending queue row whose headword is in `schema/defining-vocabulary.txt` and has no entry in any part of speech (276 such words at commit 194fab1, for example *receive*, *liquid*, *succeed*, *newspaper*, *exam*, *eleven* to *ninety*, *fourth* to *tenth*). A word that already has an entry in one part of speech (*about*, preposition) is not a milestone-1 word; its other rows are banded and built in band order ([rebanding](rebanding.md)).

The order `tools/queue.py next` and `tools/claim.py --from-queue` follow:

1. **The grammar terms the dictionary's own notes use**, first, whatever their band: *noun*, *plural*, *singular*, *syllable*, *preposition*, *pronoun*, *countable*, *uncountable*, *infinitive*, *participle*, *passive*, *tense*, *vowel*, *consonant* (the list `GRAMMAR_TERMS` in `tools/queue.py`).
2. **The other milestone-1 rows**, by band, then the part-of-speech order of [conventions](../conventions.md) section 3, then alphabetically.
3. **Everything else**, by band, then part of speech, then alphabetically.

"Before any other new word": while milestone-1 rows remain, `tools/next_mode.py` does not pick `closure`, and its share goes to `build`.

## A3. Closure of rare words is paused

`claim.py --from-queue --source closure` and `--source family` hand out only rows at band 1 or 2 until band 2 is finished (no `pending` or `claimed` row at band 1 or 2 is left). The session reads the ruling as covering closure mode's third source too, `--source crossref`, so that closure mode builds no band-3 word through it; `tools/next_mode.py` counts only the rows the pause allows as closure candidates. Rows at bands 3 to 5 wait; nothing is deleted. Rows still `unbanded` wait for the next band vote ([rebanding](rebanding.md)). When band 2 is finished, the pause lifts by itself; the tool prints which rule applied.
