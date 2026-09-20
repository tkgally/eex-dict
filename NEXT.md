# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the nineteenth scheduled Routine run (lint mode).*

## State

- 199 entries, all `reviewed` (0 `draft`). Queue: 4,124 pending, 199 done, 407 closure-gap, 4 duplicate, 1 declined.
- Lint mode (selector: forced, 5 runs since the last lint). Pre-flight clean: no open pull request, no orphan branch, inbox empty (checkout already at `origin/main`).
- Mechanical checks: `check_caps`, `check_links` clean; `crossref --all --apply` updated 6 entries (`except-prep, for-prep, none-pron, nothing-pron, pick-up-phrv, you-pron`) with missing back-links, 0 errors, 728 missing targets (expected closure-queue gaps); `lint_vocab --all --queue` 0 violations; `claim.py --prune` removed 3 stale claim files.
- `metrics.py --precision`: the five families switched off 2026-09-19 stayed at their seed-set figures (mechanism confirmed working again); nothing newly crossed 30 percent at twenty-plus decisions. `reviewer-a` overall now 0.62 (665/1064), `reviewer-b` 0.58 (211/363), both up. Recorded in `wiki/notes/reviewer-precision.md`.
- Wiki check: `index.md` matches the filesystem both ways; `log.md` has no gaps; `open-questions.md` and `needs_curator.txt` unchanged, no duplicates or staleness found.
- Fixed the two remaining logged tooling gaps: `review_panel.py --decide` now takes `--index N` to disambiguate a quote nested inside another quote on the same field/role (`wiki/notes/review-panel-decide-substring-collision.md`); `pronounce_check.py` now clears a stale `pronunciation-disputed` flag once every checked variety re-verifies (`wiki/notes/pronounce-check-stale-flag.md`). Eight new tests, 305 passing (was 297).
- No new entries; not this mode's unit. Spend: US$0 this run, US$1.26 today.

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: still 15 entries, unchanged — smallest first: `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. Hand markup only, no panel round.
2. **build**: 7 prepositions ready to claim — `as-well-as-prep`, `below-prep`, `beside-prep`, `beyond-prep`, `despite-prep`, `including-prep`, `inside-prep`.
3. **closure**: cross-reference/family targets with no entry (407+, growing, incl. `in-front-of-prep`, `until-prep`, `since-prep`, `on-prep`, `up-prep`, `besides-prep`, `whatever-pron`, `one-pron`, `yourselves-pron`, `as-conj`, `before-conj`, `other-det`, `what-det`).
4. Next **lint** due in about 5 runs (~run 24).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. No small tooling fixes remain open; watch `reviewer-a` `pronunciation` (0.36, 47) and `label` (0.55, 51) as precision candidates approaching or receding from the 30-percent line.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- The adaptation-note word cap is 60 words, not 40.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- A parenthetical linker (`along with`, `as well as`, `together with`) never changes the main verb's number; reject a reviewer's claim otherwise.
- `about`/`around` before a number, amount, or time ("about ten dollars") is an adverb sense, not a preposition sense; keep preposition entries free of it.
- Prepositions have adverbial/predicative look-alikes ("fell behind", "close by", "behind on rent") that take no direct object; keep those out of the preposition entry (queue a separate adverb entry instead).
- Watch for a preposition's own headword slipping unmarked into its own definition; a second look at every definition catches this that `lint_vocab.py`'s defining-vocabulary check does not.
- Inline markup rules from 2026-09-18 stand as documented in the style guide section 6.
- Don't call *whom* or restrictive *which* (no comma) "strictly correct" or "required"; American English treats *who*/*that* as standard, *whom*/restrictive-*which* as the more formal alternative.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
