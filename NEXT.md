# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the tenth scheduled Routine run (build mode).*

## State

- 145 entries, all `reviewed` (0 `draft`). Queue: 4,150 pending, 145 done, 387 closure-gap, 4 duplicate.
- Build mode (selector: highest scheduler debt). Claimed 20 pronoun slugs, drafted 13, released 7 back to pending: `neither-pron`, `nobody-pron`, `none-pron`, `nothing-pron`, `other-pron`, `some-pron`, `somebody-pron`.
- New entries: `i-pron`, `me-pron`, `she-pron`, `him-pron`, `his-pron`, `hers-pron`, `mine-pron`, `ours-pron`, `myself-pron`, `himself-pron`, `herself-pron`, `itself-pron`, `ourselves-pron`. Full pipeline run; gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass.
- Pronunciation: 26 transcriptions checked; `ours-pron` American disputed but settled by CMU agreement; `ourselves-pron` American stays `disputed` and flagged — neither the panel nor CMU agreed with the drafter's one-syllable *our* form. Curator line added.
- Review: 34 issues, 18 blocking, 30 applied, 4 rejected (precision this run: reviewer-a 0.81, reviewer-b 1.0). Real catch, repeated across four reflexive entries: a usage note wrongly claimed the reflexive-object restriction entrywide, contradicting each entry's own emphatic sense — rescoped. `itself-pron` and `she-pron` each had a note that contradicted one of their own senses; fixed.
- Two defining-vocabulary violations fixed (*target*, *emphasize*, *literary* replaced with vocabulary words). Queued `we-pron`, `us-pron` as new family/crossref targets.
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Spend today: US$2.04 of US$5.00 (this run: US$0.34).

## Queue (work top-down, one unit at a time)

1. **review**: 23 `markup-pending` entries remain (unchanged this run): `big-adj`, `house-n`, `news-n`, `go-v`, `good-adj`, `bank-n`, `see-v`, `family-n`, `x-ray-n`, `people-n`, `shit-n`, `get-v`, `record-n`, `record-v`, `take-v`, `color-n`, `head-n`, `thing-n`, `old-adj`, `way-n`, `water-n`, `make-v`, `time-n`. All large, multi-sense — expect fewer per run than a typical pass.
2. **review**: 120 entries reviewed only once (one panel round), most of the 23 above included, plus this run's 13.
3. **build/closure**: pronoun words released this run (`neither`, `nobody`, `none`, `nothing`, `other`, `some`, `somebody`) are pending again and ready to claim; also `we-pron`, `us-pron` (new), and the earlier pos-split queue: `enough-adv`, `something-pron`.
4. **closure**: cross-reference/family targets with no entry yet (387+, growing).
5. Next **lint** due in about 4 runs.
6. Next **originality** check due in 8 more runs (forced every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form. Illustrative phrases (*her book*) take single asterisks, not bold — a mistake this run caught and fixed.
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- A reflexive pronoun's usage note must not claim the subject-object restriction applies to its emphatic sense too — only the reflexive sense.
- `wiki/notes/reviewer-noise.md`: originality-check reviewer over-calls "copied"; watch for a repeat.
- `wiki/notes/review-panel-parse-failures.md`: spot-check a reviewer's `ok` count isn't suspiciously 0 before trusting a review pair.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" (0.49 over 280 decisions).
- `reviews/needs_curator.txt` has two open items: *several-det* British pronunciation, and now *ourselves-pron* American pronunciation (panel and CMU both favor a fuller two-syllable form; drafter's one-syllable form kept meanwhile).
- The `review_panel.py` parse-failure gap noted earlier is still unfixed — worth a session, not urgent.
