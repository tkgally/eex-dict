# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the thirteenth scheduled Routine run (review mode).*

## State

- 164 entries, all `reviewed` (0 `draft`). Queue: 4,140 pending, 164 done, 388 closure-gap, 4 duplicate, 1 declined (unchanged this run: no new entries drafted).
- Review mode (selector: highest scheduler debt; 0 draft entries, so the block was the 23 `markup-pending` entries left from the 2026-09-18 inline-markup ruling). No panel round was needed: these entries already carry full reviews from earlier runs; the unit was hand markup only (`**word**` / `*phrase*`, `wiki/style-guide.md` section 6), never by script.
- Converted 8 of the 23 to full markup and removed their flag: `x-ray-n`, `record-v`, `record-n`, `news-n`, `people-n`, `family-n`, `big-adj`, `old-adj` (smallest files first; `big-adj` had one field already marked from an earlier partial pass). See `wiki/log.md` for the method settled on (bold a word/phrase named as a word, italicize illustrative usage, including placeholder patterns; compare notes bold only the introduced word).
- Validate, lint_vocab, crossref: 0 errors on the changed files (only pre-existing, non-blocking out-of-vocabulary warnings in examples/notes). Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass.
- Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit before starting.
- Spend today: US$3.20 of US$5.00 (this run: US$0 — hand markup needed no paid calls).

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: 15 entries remain, all large multi-sense — continue smallest-first: `house-n` (30.7K), `shit-n` (19.5K), `bank-n` (18.1K), `color-n` (16.9K), `water-n` (22.4K), `good-adj` (26.1K), `thing-n` (34.6K), `make-v` (36.8K), `see-v` (36.8K), `head-n` (42.2K), `go-v` (43.6K), `get-v` (45.0K), `way-n` (53.2K), `time-n` (57.0K), `take-v` (58.6K). No panel round needed, just hand markup and flag removal.
2. **review**: entries reviewed only once (one panel round) — none currently outstanding beyond the markup-pending set above; re-check after it clears.
3. **build/closure**: the released quantifier/indefinite pronouns (`neither`, `nobody`, `none`, `nothing`, `other`, `some`, `what`) are still pending — try one or two per run, per the last several runs' notes.
4. **closure**: cross-reference/family targets with no entry yet (388+, growing).
5. Next **lint** due in about 1 run (fix the `--decide` collision and `pos_guess` gaps noted below).
6. Next **originality** check due in 5 more runs (forced every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split (addition/extension).
- The adaptation-note word cap is 60 words, not 40 (`wiki/conventions.md`); a reviewer claiming otherwise is wrong.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- After trimming a claim file, also revert the dropped slugs' `headwords/queue.tsv` status to `pending`.
- Inline markup: a noun's "A/An X is..." core idea and sense definitions stay unmarked; a verb's "To X is to..." and an adjective's/function word's "X means/describes..." bold the headword; a compare note bolds only the introduced comparison word, never the headword itself; illustrative usage (including placeholder patterns like *record something*) is italicized even with no colon.
- `wiki/notes/lint-vocab-pos-guess-gap.md`: `pos_guess` defaults an unrecognized base form to noun with no signal it's a guess; double-check a closure-sourced claim's part of speech before drafting.
- `wiki/notes/reviewer-noise.md`, `review-panel-parse-failures.md`, `review-panel-decide-collisions.md`: open tooling notes for the next lint pass.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, already resolved).
- Two `review_panel.py` tooling gaps (parse failures, `--decide` collisions) plus the `pos_guess` gap are all still unfixed — worth the next lint session.
