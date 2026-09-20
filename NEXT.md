# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the seventeenth scheduled Routine run (build mode).*

## State

- 186 entries, all `reviewed` (0 `draft`). Queue: 4,136 pending, 186 done, 406 closure-gap, 4 duplicate, 1 declined.
- Build mode. Claimed and finished 12 entries: *none, some* (pronouns; only two of the five "try one or two per run" quantifiers), *which, who, whom, whose, you, yours, yourself* (pronouns), *as, at, before* (band-1 prepositions).
- Panel: 47 issues, 29 blocking, 43 applied, 4 rejected (precision reviewer-a 0.91, reviewer-b 0.93). Notable fixes: circular *at*-in-time definition; two mismarked adverbial collocations under *before*; *you*'s generic sense wrongly labelled informal; three entries (*who*, *whom*, *which*) overstated *whom*/restrictive-*which* as strictly correct where American usage is more permissive; *as*'s two senses merged into one (role and age/state are the same sense); *such as* removed from *as* (belongs under an entry for *such*).
- Three defining-vocabulary violations fixed by rewording (*target* → *aim*, *rank* → dropped); one first-sense exemption kept (*role* in *as-prep*, per the style-guide carve-out).
- Rejected: an over-broad claim that uncountable nouns sometimes take a plural verb after *none of*; a non-issue flagging an accurate but optional `core_idea`.
- Pre-flight: no open pull request, no orphan branch, inbox empty.
- Spend today: US$0.78 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: still 15 entries, unchanged — smallest first: `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. Hand markup only, no panel round.
2. **build/closure**: three quantifier/indefinite pronouns still pending — `nothing`, `other`, `what` — try one or two per run, not all at once.
3. **closure**: cross-reference/family targets with no entry (406+, growing, incl. `like-prep`, `in-prep`, `in-front-of-prep`, `one-pron`, `yourselves-pron`, `as-conj`, `before-conj`, `nothing-pron` itself).
4. Next **lint** due in about 2 runs (last was run 18; run 20 was the forced originality check, this run was build).
5. Next **originality** check due at run 30.
6. Small fixes, low priority: `review_panel.py --decide --index N` for the substring-collision case (`wiki/notes/review-panel-decide-substring-collision.md`); `pronounce_check.py` never clears a stale `pronunciation-disputed` flag after re-verification (`wiki/notes/pronounce-check-stale-flag.md`).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- The adaptation-note word cap is 60 words, not 40.
- American IPA carries no length mark (`ː`); British keeps it.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent.
- A parenthetical linker (`along with`, `as well as`, `together with`) never changes the main verb's number; reject a reviewer's claim otherwise.
- `about`/`around` before a number, amount, or time ("about ten dollars") is an adverb sense, not a preposition sense; keep preposition entries free of it.
- Inline markup rules from 2026-09-18 stand as documented in the style guide section 6.
- **New**: don't call *whom* or restrictive *which* (no comma) "strictly correct" or "required"; American English treats *who*/*that* as standard in these positions, and *whom*/restrictive-*which* as the more formal alternative. Word-alternate homographs (e.g. `which-det` from `which-pron`) go in `see_also`, not `word_family`; `word_family` is for morphological derivatives.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
