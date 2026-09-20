# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the sixteenth scheduled Routine run (originality mode).*

## State

- 174 entries, all `reviewed` (0 `draft`). Queue: 4,145 pending, 174 done, 403 closure-gap, 4 duplicate, 1 declined.
- Originality mode (forced: run 20 is a multiple of 10). Sampled and checked 10 definitions/notes; 5 original, 4 generic-overlap, 1 rewrite (`pick-up-phrv` sense 9, "continue" — echoed a Macmillan synonym-list phrase). Full pipeline re-run on `pick-up-phrv` after the rewrite surfaced 8 more genuine issues in the same entry (definition, cross-reference, and adaptation fixes); all applied, 0 rejected.
- Reviewer-a's originality answers were mixed this run (4 copied / 4 original / 2 cannot tell), not the prior 100 percent "copied" — see the update in `wiki/notes/reviewer-noise.md`. Still cites no source; verdicts keep resting on search plus the session's own reading.
- New tooling gap logged, not yet fixed: `review_panel.py --decide --quote` cannot disambiguate an issue whose quote is a substring of another issue's quote on the same field (`wiki/notes/review-panel-decide-substring-collision.md`); worked around with a manual `reviews/decisions.jsonl` line this run.
- Still open from run 15: `pronounce_check.py` never clears a stale `pronunciation-disputed` flag after re-verification (`wiki/notes/pronounce-check-stale-flag.md`).
- Pre-flight: no open pull request, no orphan branch, inbox empty.
- Spend today: US$0.43 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: still 15 entries, unchanged — smallest first: `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. Hand markup only, no panel round.
2. **build/closure**: five quantifier/indefinite pronouns still pending — `none`, `nothing`, `other`, `some`, `what` — try one or two per run, not all at once.
3. **closure**: cross-reference/family targets with no entry (403+, growing, incl. `about-adv`, `about-adj`, `over-prep`, `before-prep`, `between-prep`, `regarding-prep`).
4. Next **lint** due in about 3 runs (last was run 14; run 20 handled the forced originality check but not lint).
5. Next **originality** check due at run 30.
6. Small fix, low priority: add a `review_panel.py --decide --index N` option for the substring-collision case above.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- The adaptation-note word cap is 60 words, not 40.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- A parenthetical linker (`along with`, `as well as`, `together with`) never changes the main verb's number; reject a reviewer's claim otherwise.
- `about`/`around` before a number, amount, or time ("about ten dollars") is an adverb sense, not a preposition sense; keep preposition entries free of it.
- Inline markup rules from 2026-09-18 stand as documented in the style guide section 6.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
