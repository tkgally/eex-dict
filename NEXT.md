# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the twentieth scheduled Routine run (review mode).*

## State

- 199 entries, all `reviewed` (0 `draft`). Queue: 4,124 pending, 199 done, 407 closure-gap, 4 duplicate, 1 declined.
- Review mode (selector: highest scheduler debt; no draft entries existed). Pre-flight clean: no open pull request, no orphan branch, inbox empty, checkout already at `origin/main`.
- The unit: all 15 remaining `markup-pending` entries, the last of the 2026-09-18 inline-markup backlog — `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. No panel round needed (all already fully reviewed); hand markup only, field by field, against `wiki/style-guide.md` section 6 and the model entries. No wording changed. `markup-pending` now flags zero entries — the backlog opened 2026-09-18 is closed.
- One pre-existing, unrelated warning surfaced: `time-n` phrases[17] (`kill-time`)'s second example ("an hour to kill") doesn't literally contain "time" or a listed form, so `validate.py` flags it (not a markup issue, a content one; left for a future review run to judge whether it needs a hand mark or a different example).
- Gate, caps, links, 305 tests, `lint_vocab` (0 violations, only pre-existing out-of-vocabulary warnings) and `crossref` (0 errors, 728 expected closure-queue gaps) all pass. No new entries this run; not this mode's unit. Spend: US$0 this run, US$1.26 today.

## Queue (work top-down, one unit at a time)

1. **review**: no `draft` entries and no `markup-pending` entries remain. Next review unit is a second panel round on `reviewed` entries that have had only one (173 as of the last count) — pick the block by `params.block_size` when review is next selected.
2. **build**: 7 prepositions ready to claim — `as-well-as-prep`, `below-prep`, `beside-prep`, `beyond-prep`, `despite-prep`, `including-prep`, `inside-prep`.
3. **closure**: cross-reference/family targets with no entry (407+, growing, incl. `in-front-of-prep`, `until-prep`, `since-prep`, `on-prep`, `up-prep`, `besides-prep`, `whatever-pron`, `one-pron`, `yourselves-pron`, `as-conj`, `before-conj`, `other-det`, `what-det`).
4. Next **lint** due in about 4 runs (~run 24).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. No small tooling fixes remain open; watch `reviewer-a` `pronunciation` (0.36, 47) and `label` (0.55, 51) as precision candidates approaching or receding from the 30-percent line (unchanged since the last lint pass).

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
- Inline markup rules from 2026-09-18 stand as documented in the style guide section 6. The backlog they created is now fully converted; any new or rewritten entry gets marks at drafting time, not as a later pass.
- Don't call *whom* or restrictive *which* (no comma) "strictly correct" or "required"; American English treats *who*/*that* as standard, *whom*/restrictive-*which* as the more formal alternative.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
