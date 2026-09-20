# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the fifteenth scheduled Routine run (build mode).*

## State

- 174 entries, all `reviewed` (0 `draft`). Queue: 4,145 pending, 174 done, 403 closure-gap, 4 duplicate, 1 declined.
- Build mode (selector: highest scheduler debt). Claimed and finished 10 entries: `neither-pron`, `nobody-pron`, `about-prep`, `above-prep`, `across-prep`, `after-prep`, `against-prep`, `along-prep`, `among-prep`, `around-prep`. Full pipeline on all ten; panel 41 issues, 27 blocking, 33 applied, 8 rejected (precision reviewer-a 0.76, reviewer-b 0.92 this batch). Six defining-vocabulary violations fixed by rewording; the rest queued as closure candidates. `queue.py sync` marked all ten `done`.
- Real catches: `about` and `around` each wrongly folded an adverbial "approximately" sense (and, for `about`, an adjectival "be about to" phrase) into the preposition entry; removed and queued `about-adv`, `about-adj`, `around-adv` (already queued) separately — a pattern to watch for `over`, `near`, `round` too. `neither` overstated singular-only verb agreement; softened throughout. `around-prep`'s definition circularly reused its own signpost.
- Fixed a drafting slip before review: British `nobody` wrongly copied the American stress pattern; corrected and reverified.
- New tooling gap logged, not yet fixed: `pronounce_check.py` never clears a stale `pronunciation-disputed` flag after a later re-verification (`wiki/notes/pronounce-check-stale-flag.md`).
- Pre-flight: no open pull request, no orphan branch (pruned one stale local remote-tracking ref), inbox empty.
- Spend today: US$0.32 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: still 15 entries, unchanged — smallest first: `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. Hand markup only, no panel round.
2. **build/closure**: five quantifier/indefinite pronouns still pending — `none`, `nothing`, `other`, `some`, `what` — try one or two per run, not all at once.
3. **closure**: cross-reference/family targets with no entry (403+, growing); this run added `about-adv`, `about-adj`, `over-prep`, `before-prep`, `between-prep`, `regarding-prep`, others.
4. Next **lint** due in about 4 runs (last was run 14).
5. Next **originality** check due in about 3 runs (forced every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- The adaptation-note word cap is 60 words, not 40.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- A parenthetical linker (`along with`, `as well as`, `together with`) never changes the main verb's number; a reviewer's claim otherwise is prescriptively wrong, reject it.
- `about`/`around` before a number, amount, or time ("about ten dollars") is an adverb sense, not a preposition sense, matching major EFL dictionaries; keep new preposition entries free of it.
- Inline markup rules from 2026-09-18 stand as documented in the style guide section 6.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
