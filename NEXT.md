# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the eighth scheduled Routine run (review mode).*

## State

- 132 entries, all `reviewed` (0 `draft`). Queue: 4,163 pending, 132 done, 388 closure-gap, 4 duplicate (unchanged this run).
- Review mode (selector: highest debt). Took the 10 markup-pending, reviewed-once entries with the fewest senses for a thorough pass: `alone-adj`, `quickly-adv`, `sorry-adj`, `borrow-v`, `lend-v`, `speak-v`, `happy-adj`, `tell-v`, `talk-v`, `say-v`. Full panel + adjudication (86 decisions: 68 applied, 18 rejected), inline marks hand-added field by field, flag cleared, full pipeline (validate/lint_vocab/crossref) green on each.
- Real content fixes: `alone-adj` sense 1 had adverbial examples wrongly used as adjective ones; `quickly-adv` sense 2 was defined like *soon* instead of a duration; `say-v`'s parenthetical *say, six o'clock* use is now its own subsense; several entries had "never/only" claims hedged to "usually" per style rule.
- Tooling problem found and logged (not fixed): `review_panel.py` can silently record an empty, zero-verdict reviewer pass when a reply is truncated (`talk-v`, this run). New page `wiki/notes/review-panel-parse-failures.md`.
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass. Spend today: US$1.71 of US$5.00 (this run: US$0.61).
- `next_mode.py` not yet queried by the next session; re-run `--explain` at the start.

## Queue (work top-down, one unit at a time)

1. **review**: 23 `markup-pending` entries remain (down from 33): `big-adj`, `house-n`, `news-n`, `go-v`, `good-adj`, `bank-n`, `see-v`, `family-n`, `x-ray-n`, `people-n`, `shit-n`, `get-v`, `record-n`, `record-v`, `take-v`, `color-n`, `head-n`, `thing-n`, `old-adj`, `way-n`, `water-n`, `make-v`, `time-n`. All are large, multi-sense entries (5–14 senses) — expect fewer per run than this one.
2. **review**: 107 entries reviewed only once (one panel round), most of the 23 above included.
3. **build/closure**: pos-split pointers queued from recent runs — `something-pron`, `neither-pron`, `enough-adv`, `she-pron`, `him-pron`, `his-pron`, `himself-pron`, `hers-pron`, `herself-pron`.
4. **closure**: cross-reference/family targets with no entry yet (388+, growing).
5. Next **lint** due in about one run (runs_since_lint was 4 plus this review run = 5; forced every 5).
6. Next **originality** check due in 9 more runs (forced every 10th; this was run 1 of the new cycle).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- A rewritten definition must still clear `lint_vocab.py`'s closed defining vocabulary — check wording against `schema/defining-vocabulary.txt` early (`say-v`'s new subsense hit "commas"/"approximate"/"react" this run, all fixed).
- `wiki/notes/reviewer-noise.md`: originality-check reviewer over-calls "copied"; watch for a repeat.
- `wiki/notes/review-panel-parse-failures.md`: spot-check a reviewer's `ok` count isn't suspiciously 0 before trusting a review pair.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision 0.37 over 222 decisions.
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
- New this run: a real tooling gap in `review_panel.py` (see above) — worth a fix in a future session, not urgent (the workaround caught it this time).
