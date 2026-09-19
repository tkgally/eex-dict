# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the twelfth scheduled Routine run (closure mode).*

## State

- 164 entries, all `reviewed` (0 `draft`). Queue: 4,140 pending, 164 done, 388 closure-gap, 4 duplicate, 1 declined.
- Closure mode (selector: highest scheduler debt). Claimed 6 slugs from `--source closure`: `addition-n`, `article-n`, `exception-n`, `identity-n`, `thumb-n`, and `additional-adj` (see below). Full pipeline; gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass.
- `additional-n` declined: `lint_vocab.py`'s `pos_guess` queued *additional* as a noun (it defaults to noun when it can't infer part of speech from morphology), but it is an adjective. Requeued and claimed as `additional-adj`. Tooling gap logged, not fixed: `wiki/notes/lint-vocab-pos-guess-gap.md`.
- Pronunciation: 12 transcriptions, full agreement (4/4 American, 3/3 British), none disputed.
- Review: one reviewer-b parse failure on `addition-n` (the known truncated-reply pattern, `wiki/notes/review-panel-parse-failures.md`); a re-run fixed it. Across several adjudication rounds: 44 issues, 38 applied, 6 rejected (precision this run: reviewer-a 0.90, reviewer-b 0.80). Real catches: two `exception-n` phrase definitions were fragments, not phrasal definitions; `article-n`'s grammar explanation overstated that articles are chosen noun by noun (and one example wrongly implied every countable noun needs an article); `identity-n`'s countability was too narrow for both senses (recoded `countable or uncountable`) and mixed noun+noun with adjective+noun collocations.
- Rejected: reviewer-a's three-times-repeated claim that *addition*'s "built onto a house" sense isn't mainly American (a region label means "mainly," not "exclusively"; addition/extension is a genuine AmE/BrE split) and reviewer-b's fabricated 40-word adaptation-note cap (the real house rule is 60, `wiki/conventions.md`).
- Six defining-vocabulary violations fixed by rewording definitions (words like *extra*, *magazine*, *document*, *offended*, *identify*, *gripping* replaced with vocabulary words or moved out of definition fields).
- Crossref queued 13 missing targets: `add-v`, `subtraction-n`, `extra-adj`, `additionally-adv`, `item-n`, `except-prep`, `exceptional-adj`, `identify-v`, `identical-adj`, `identification-n`, `finger-n`, `thumb-v`, `thumbprint-n`.
- Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit before starting.
- Spend today: US$3.20 of US$5.00 (this run: US$0.85).

## Queue (work top-down, one unit at a time)

1. **review**: 23 `markup-pending` entries remain (unchanged): `big-adj`, `house-n`, `news-n`, `go-v`, `good-adj`, `bank-n`, `see-v`, `family-n`, `x-ray-n`, `people-n`, `shit-n`, `get-v`, `record-n`, `record-v`, `take-v`, `color-n`, `head-n`, `thing-n`, `old-adj`, `way-n`, `water-n`, `make-v`, `time-n`. All large, multi-sense.
2. **review**: entries reviewed only once (one panel round), most of the 23 above included, plus this run's 6.
3. **build/closure**: the released quantifier/indefinite pronouns (`neither`, `nobody`, `none`, `nothing`, `other`, `some`, `what`) are still pending — try one or two per run, per the last two runs' notes.
4. **closure**: cross-reference/family targets with no entry yet (388+, growing; 13 new this run).
5. Next **lint** due in about 2 runs (also: fix the `--decide` collision and `pos_guess` gaps noted below).
6. Next **originality** check due in 6 more runs (forced every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading of "also used elsewhere" override a genuine AmE/BrE split (addition/extension).
- The adaptation-note word cap is 60 words, not 40 (`wiki/conventions.md`); a reviewer claiming otherwise is wrong.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- After trimming a claim file, also revert the dropped slugs' `headwords/queue.tsv` status to `pending`.
- `wiki/notes/lint-vocab-pos-guess-gap.md` (new): `pos_guess` defaults an unrecognized base form to noun with no signal it's a guess; double-check a closure-sourced claim's part of speech before drafting.
- `wiki/notes/reviewer-noise.md`, `review-panel-parse-failures.md`, `review-panel-decide-collisions.md`: open tooling notes for the next lint pass.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, already resolved in this run).
- Two `review_panel.py` tooling gaps (parse failures, `--decide` collisions) plus the new `pos_guess` gap are all still unfixed — worth a lint session.
