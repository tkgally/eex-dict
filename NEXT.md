# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the twenty-first scheduled Routine run (build mode).*

## State

- 214 entries, all `reviewed` (0 `draft`). Queue: 4,118 pending, 214 done, 416 closure-gap, 4 duplicate, 1 declined.
- Build mode (selector: highest scheduler debt). Pre-flight clean: no open pull request, no orphan branch, inbox empty, checkout already at `origin/main`.
- The unit: 15 new preposition entries — *as well as, below, beside, beyond, despite, including, inside, like, minus, near, onto, outside, past, plus, since*. Claimed 20, trimmed to 15 for quality; *off, on, out, over, per* returned to the queue, not drafted (the three heaviest — *on, over, off* — deliberately deferred for a run with more room).
- Panel: 53 issues, 37 blocking, 48 applied, 5 rejected (precision reviewer-a 0.87, reviewer-b 1.0). *plus-prep* restructured: its second sense mixed in a conjunction use, merged into one general-addition preposition sense. Four entries had a standard American/British variant wrongly called a learner error (*inside of, near to, on to* ×2); all removed. *despite-prep* wrongly labelled formal by both reviewers; label removed, synonym note softened to match.
- *beyond-prep*'s British pronunciation is `disputed` after two tries (with and without the /j/ glide); flagged (`pronunciation-disputed`) and logged to the curator queue.
- Three defining-vocabulary violations fixed by rewording (*relevant, resembles, responsibility*). Gate, caps, links, 305 tests, lint_vocab (0 violations) and crossref (0 errors, new back-links applied) all pass. Spend: US$0.46 this run, US$1.73 today.

## Queue (work top-down, one unit at a time)

1. **build**: 5 prepositions ready to claim — *off, on, out, over, per* (the last two, *on* and *over*, are heavy multi-sense entries; give them a full run each rather than folding into a mixed batch).
2. **review**: 188 `reviewed` entries have had only one panel round; pick the block by `params.block_size` when review is next selected.
3. **closure**: cross-reference/family targets with no entry (416+, growing — this run added several: *in-addition-to-prep, next-to-prep, compared-to-prep, unlike-prep, close-to-prep, far-from-prep, such-as-prep, within-prep, to-prep*, and more).
4. Next **lint** due in about 3 runs (~run 24, was pushed one run by this build).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. No small tooling fixes remain open; watch `reviewer-a` `pronunciation` and `label` as precision candidates approaching or receding from the 30-percent line (unchanged since the last lint pass).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- Plain phrasal definitions (no "used to" wrapper) are correct house style for concrete/spatial prepositions (*behind, above, near*); reserve "used to..." for true function words (*including, minus*) per the style guide's own exception.
- "Inside of", "outside of", "near to", "on to" are standard, grammatical variants (American primary, or British for "on to"); do not flag them as learner errors.
- A parenthetical linker (`along with`, `as well as`, `together with`) never changes the main verb's number; reject a reviewer's claim otherwise.
- `about`/`around` before a number, amount, or time ("about ten dollars") is an adverb sense, not a preposition sense; keep preposition entries free of it.
- Prepositions have adverbial/predicative look-alikes ("fell behind", "close by") that take no direct object; keep those out of the preposition entry.
- Watch for a preposition's own headword slipping unmarked into its own definition; a second look at every definition catches this that `lint_vocab.py`'s defining-vocabulary check does not.
- Don't call *whom* or restrictive *which* (no comma) "strictly correct" or "required"; American English treats *who*/*that* as standard.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has five open items: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, *beyond-prep* British pronunciation (new this run), and the `additional-n` decline (informational, resolved).
