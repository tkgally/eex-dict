# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the third scheduled Routine run (review mode).*

## State

- 106 entries, all 106 `reviewed` (0 `draft`): the four entries orphaned since the founding session (*can*, *child*, *each other*, *explain*) got their missing reviewer-a pass, adjudication, and promotion this run. Queue: 4,187 pending, 106 done.
- *can* gained a missing sense (**can't** for logical impossibility) and a corrected **could** vs **was able to** contrast; *child*'s "product of" sense was narrowed; *each other*'s collocations were retyped (pronoun, not noun).
- Eight of the 42 `markup-pending` entries were fully hand-marked and cleared this run: *favorite*, *information*, *main*, *police*, *scissors*, *advice*, *afraid*, *asleep*. 34 remain, in file order after these: `advice-n` onward in `wiki/log.md`'s 2026-09-18 decision entry lists all 42; the un-cleared ones are the big polysemous verbs and nouns (*go*, *get*, *make*, *take*, *see*, *say*, *talk*, *tell*, *speak*, *good*, *water*, *house*, *thing*, *head*, *way*, *time*, *record*, *news*, *color*, *shit*, *family*, *person*, *people*, *sorry*, *happy*, *big*, *old*, *quickly*).
- `information-n`'s "help desk" use was miscoded as an uncountable subsense; promoted to its own countable sense 2. `asleep-adj`'s etymology misstated the Old English source and over-claimed that etymology explains today's word order; corrected, and the postpositive exception (*the baby asleep in the crib*) was added consistently for **asleep**/**afraid**/**alive**/**alone**/**awake**.
- Pre-flight: no open pull request; the merged `claude/admiring-rubin-6urxtt` branch confirmed fully absorbed with no residue, logged (four prune-branch lines now await the owner, plus one pronunciation question).
- 108 adjudication decisions this run (101 applied, 7 rejected — mostly reviewer-a claims that were wrong against the closed vocabulary or well-established facts). Reviewer precision: 0.875 / 0.944.
- Gate, caps, links, 289 unit tests, lint_vocab and crossref gates all pass. Spend today: US$0.33 of US$5.00.
- `next_mode.py` now calls **lint** for the next run (forced: five runs since the last one).

## Queue (work top-down, one unit at a time)

1. **lint** is due and forced next run: `check_caps.py`, `check_links.py`, `crossref.py --all --apply`, `lint_vocab.py --all --queue`, `claim.py --prune`, `metrics.py --precision`, reviewer-precision review, wiki consistency pass.
2. **review**: the remaining 34 `markup-pending` entries (see State), in blocks of 20, oldest/simplest first.
3. **build** from the queue in its order: the pos-split pronoun/adverb pointers plus remaining core determiners and quantifiers.
4. **closure**: cross-reference/family targets with no entry yet keep growing (389 open); they surface through the queue in due course.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: a word's use in another part of speech gets its own entry and a pointer in `see_also`, never demonstrated with a worked example inside another entry.
- American IPA carries no length mark (`ː`); British keeps it. Compare a new entry against `few-det.json` or `any-det.json` before drafting.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- **asleep**, **afraid**, **alive**, **alone**, **awake** never come immediately before a noun, but do follow a noun with a complement (*the baby asleep in the crib*); this postpositive exception is now stated consistently in both entries — carry it forward if either is touched again.
- A reviewer's confident-sounding but wrong claim (contradicted by the closed vocabulary, a sibling entry's settled convention, or plain fact) is rejected with a one-line reason, not applied for safety's sake.

## For the owner

- Three items remain open from earlier journals: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
