# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the fourteenth scheduled Routine run (lint mode).*

## State

- 164 entries, all `reviewed` (0 `draft`). Queue: 4,140 pending, 164 done, 388 closure-gap, 4 duplicate, 1 declined (unchanged this run: lint mode drafts nothing).
- Lint mode (selector: forced, 5 runs since the last lint pass). Mechanical checks all clean: `check_caps`, `check_links` OK; `crossref --all --apply` updated 2 entries (`something-pron`, `themselves-pron`) with missing back-links, 0 errors, 716 missing targets (unchanged, all queued); `lint_vocab --all --queue` 0 violations; `claim.py --prune` removed 3 stale claim files.
- `metrics.py --precision`: the five families switched off 2026-09-19 (`reviewer-a` example-policy/grammar-code/sense-structure, `reviewer-b` example-policy/explanation) are still at their seed-set figures — the switch-off is working (no new decisions accrue once downgraded). No family newly crossed under 30 percent at twenty-plus decisions.
- Fixed the three tooling gaps that were due this lint pass (see `wiki/notes/`, each now has a "2026-09-20: fixed" section): `review_panel.py --decide --quote` disambiguates two issues on one field/role instead of silently colliding; `validate.py`'s `reviewed` gate now rejects a reviewer record that logged an error with zero verdicts; `lint_vocab.py`'s `pos_guess` checks a closed adjective-suffix list before defaulting to noun, and flags the remaining guessed default. Five new/updated tests; 297 pass (was 292).
- `wiki/index.md` checked against the filesystem (matches); `wiki/log.md` has one entry per run (18 now); `open-questions.md` and `reviews/needs_curator.txt` read, no duplicates, nothing stale beyond what's already recorded there.
- Pre-flight: no open pull request, no orphan branch, inbox empty; checkout was already at `origin/main`'s latest commit (no stranded work from the last run).
- Spend today: US$0 of US$5.00 (lint mode made no paid calls).

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: 15 entries remain, unchanged since 2026-09-19, all large multi-sense — smallest first: `house-n` (30.7K), `shit-n` (19.5K), `bank-n` (18.1K), `color-n` (16.9K), `water-n` (22.4K), `good-adj` (26.1K), `thing-n` (34.6K), `make-v` (36.8K), `see-v` (36.8K), `head-n` (42.2K), `go-v` (43.6K), `get-v` (45.0K), `way-n` (53.2K), `time-n` (57.0K), `take-v` (58.6K). No panel round needed, just hand markup and flag removal.
2. **review**: entries reviewed only once — none outstanding beyond the markup-pending set above; re-check after it clears.
3. **build/closure**: the released quantifier/indefinite pronouns (`neither`, `nobody`, `none`, `nothing`, `other`, `some`, `what`) are still pending — try one or two per run.
4. **closure**: cross-reference/family targets with no entry yet (388+, growing; `way-n`, `x-ray-n`, `water-n`, and the pronoun `see_also` pairs have the densest gaps).
5. Next **lint** due in about 5 runs.
6. Next **originality** check due in 4 more runs (forced every 10th; last was run 11 of 17... recheck `next_mode.py --explain` signals next time).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split (addition/extension).
- The adaptation-note word cap is 60 words, not 40 (`wiki/conventions.md`); a reviewer claiming otherwise is wrong.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- After trimming a claim file, also revert the dropped slugs' `headwords/queue.tsv` status to `pending`.
- Inline markup: a noun's "A/An X is..." core idea and sense definitions stay unmarked; a verb's "To X is to..." and an adjective's/function word's "X means/describes..." bold the headword; a compare note bolds only the introduced comparison word, never the headword itself; illustrative usage (including placeholder patterns like *record something*) is italicized even with no colon.
- `they-pron`'s three already-logged `adaptation` decisions (all recorded `minor`, though two source issues were `blocking`) predate the `--decide --quote` fix and are left as historical ledger lines, not rewritten — the gate was never at risk, only that one field's precision breakdown.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, already resolved).
