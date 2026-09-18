# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-18 by the second scheduled Routine run (build mode).*

## State

- 106 entries: 102 `reviewed`, 4 `draft` (*can*, *child*, *each other*, *explain*: unchanged again, still owed a first reviewer-a pass — see Queue). Fourteen new determiners this run: *least*, *less*, *little*, *many*, *more*, *most*, *much*, *my*, *neither*, *no*, *other*, *our*, *several*, *such*. Queue: 4,187 pending, 106 done.
- Pointers queued by this run's crossref pass: *least-adv*, *little-adj*, *many-pron*, *more-pron*, *more-adv*, *most-pron*, *most-adv*, *much-pron*, *much-adv*, *mine-pron*, *neither-pron*, *none-pron*, *no-interj*, *other-pron*, *ours-pron*, *several-pron* (most already existed in the queue from earlier crossrefs; 5 were newly added).
- `several-det` carries `provenance.flags: ["pronunciation-disputed"]` on both varieties: American settled in favor of the drafter's two-syllable form (CMU agrees); British has no open data and is left to the curator (`reviews/needs_curator.txt`, run `20260918T203317Z-6urxtt`).
- Two idioms relocated by the keyword rule during adjudication: *once more* dropped as adverbial; *more or less* moved from `less-det` to `more-det`.
- Pre-flight found no open pull request; one previously unlogged orphan branch (`claude/admiring-rubin-05mkcp`) was fully absorbed with no residue, logged in `reviews/needs_curator.txt`.
- Gate, caps, links, 289 unit tests, lint_vocab and crossref gates all pass. Spend today: US$0.62 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review**: the four `draft` entries first (`can-modal`, `child-n`, `each-other-pron`, `explain-v`; reviewer-a still owed on all four); `next_mode.py` now says review is the highest-debt mode. Then the 42 `markup-pending` entries in blocks of 20.
2. **build** from the queue in its order: the pos-split pronoun/adverb pointers listed above will surface soon, plus the remaining core determiners and quantifiers.
3. **closure**: cross-reference/family targets with no entry yet keep growing (about 390 open); they surface through the queue in due course.
4. First **lint** pass due after the fifth Routine run (`runs_since_lint` is now 4).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: a word's use in another part of speech gets its own entry and a pointer in `see_also`, never demonstrated with a worked example inside the determiner entry (the recurring *"det + of"* pronoun/fused-head trap this run fixed on **several**, **many**, **most**).
- Idiom placement follows the keyword rule (first noun, else first verb, else first content word) even when it cuts across part-of-speech lines: *either...or* and *at least*/*at most* stay under the determiner by that rule; *once more* does not.
- American IPA carries no length mark (`ː`); British keeps it. Compare a new entry against `few-det.json` or `any-det.json` before drafting.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- Reviewer flags that repeat a house convention already settled on a sibling entry (the **few**/**a few** ↔ **little**/**a little** split, the 2-vs-3-or-more comparative/superlative pattern across **less/least/more/most**) are rejected with that reason; do not relitigate them entry by entry.

## For the owner

- Three items remain open from earlier journals: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has three prune-branch lines and one pronunciation question (`several-det` British), all awaiting the owner; this tool set cannot delete branches.
