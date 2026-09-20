# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the eighteenth scheduled Routine run (build mode).*

## State

- 199 entries, all `reviewed` (0 `draft`). Queue: 4,124 pending, 199 done, 407 closure-gap, 4 duplicate, 1 declined.
- Build mode (selector: highest scheduler debt). Claimed 20 band-1 slugs, drafted 13: *nothing, other, what* (pronouns — the three "try one or two per run" quantifiers from the last baton are now all done), *behind, between, by, down, during, except, for, from, in, into* (prepositions). The other 7 claimed (*as well as, below, beside, beyond, despite, including, inside*) were returned to the queue as `pending`, not drafted — kept the batch to 13 for quality.
- Panel: 52 issues, 33 blocking, 50 applied, 2 rejected (precision reviewer-a 0.97, reviewer-b 0.95). Notable fixes: *behind*'s "less advanced" sense had two adverbial (not prepositional) examples, removed; *except*'s "except for" was wrongly given its own idiom block with an invented conditional meaning belonging to *but for*; *into*'s "bump into" example showed a chance meeting, not a collision, moved to a phrase entry; *for* and *in* each had a sense definition that literally reused the headword.
- Nine defining-vocabulary violations (*role, advanced, destination, favor, origin, originates, separation, arrangement, contact, collision, enthusiastic*) fixed by rewording, found by a second `lint_vocab.py` pass after adjudication.
- Rejected: a pronunciation nitpick on *into* already covered by a listed weak-form variant; a markup call on *what* already matching the style guide's own bold-phrase example.
- Pre-flight: no open pull request, no orphan branch, inbox empty.
- Spend today: US$1.26 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review (markup-pending)**: still 15 entries, unchanged — smallest first: `house-n`, `shit-n`, `bank-n`, `color-n`, `water-n`, `good-adj`, `thing-n`, `make-v`, `see-v`, `head-n`, `go-v`, `get-v`, `way-n`, `time-n`, `take-v`. Hand markup only, no panel round.
2. **build**: the 7 prepositions set aside this run — `as-well-as-prep`, `below-prep`, `beside-prep`, `beyond-prep`, `despite-prep`, `including-prep`, `inside-prep` — are `pending` again, ready to claim.
3. **closure**: cross-reference/family targets with no entry (407+, growing, incl. `in-front-of-prep`, `until-prep`, `since-prep`, `on-prep`, `up-prep`, `besides-prep`, `whatever-pron`, `one-pron`, `yourselves-pron`, `as-conj`, `before-conj`, `other-det`, `what-det`).
4. Next **lint** due in about 1–2 runs.
5. Next **originality** check due around run 30.
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
- Don't call *whom* or restrictive *which* (no comma) "strictly correct" or "required"; American English treats *who*/*that* as standard, *whom*/restrictive-*which* as the more formal alternative.
- **New**: `behind`, `by`, and similar prepositions have adverbial/predicative look-alikes ("fell behind", "close by", "behind on rent") that take no direct object; keep those out of the preposition entry (queue a separate adverb entry instead), per the one-part-of-speech-per-entry rule.
- **New**: watch for a preposition's own headword slipping unmarked into its own definition (e.g. defining *for* with "for", *in* with "in"); a second look at every definition catches this that `lint_vocab.py`'s defining-vocabulary check does not.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four open items, unchanged: *several-det* British pronunciation, *ourselves-pron* American pronunciation, *themselves-pron* British pronunciation, and the `additional-n` decline (informational, resolved).
