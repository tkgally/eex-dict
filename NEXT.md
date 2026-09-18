# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-18 by the first scheduled Routine run (build mode).*

## State

- 92 entries: 88 `reviewed`, 4 `draft` (*can*, *child*, *each other*, *explain*: unchanged this run, still need a first reviewer-a pass — see Queue). Ten new determiners this run: *both*, *each*, *either*, *enough*, *every*, *few*, *half*, *her*, *his*, *its*. Queue: 4,194 pending, 92 done.
- Nine pos-split pointers queued: *both/each/either/enough/few/her/his*-pron, *either/enough*-adv (plus *little*-det via crossref, already queued by the word-list panel).
- `her-det` carries `provenance.flags: ["pronunciation-disputed"]`: the panel favored a weak/unstressed American form; kept the drafter's stressed citation form, which CMU agrees with (`reviews/decisions.jsonl`, run `20260918T163256Z-05mkcp`).
- Pre-flight found no open pull request; pull request #4's branch (`claude/magical-dirac-ydspk3`) was closed by the owner without an API merge but its content is fully absorbed on `main` (no residue) — logged in `reviews/needs_curator.txt`, not yet deleted.
- Gate, caps, links, 289 unit tests, lint_vocab and crossref gates all pass. Spend today: US$0.26 of US$5.00.

## Queue (work top-down, one unit at a time)

1. **review**: the four `draft` entries first (`can-modal`, `child-n`, `each-other-pron`, `explain-v`; reviewer-a is still owed on all four); then the 42 `markup-pending` entries in blocks of 20 (panel, adjudicate, add the marks by hand, remove the flag).
2. **build** from the queue in its order; `python3 tools/next_mode.py` currently says build again. Nine pos-split pronoun/adverb entries from this run are now queued and will surface soon: *both-pron*, *each-pron*, *either-pron*, *either-adv*, *enough-pron*, *enough-adv*, *few-pron*, *her-pron*, *his-pron*.
3. **closure**: 382 cross-reference/family targets have no entry yet, including *half-n*, *little-det*, *everybody-pron* and its siblings, *hers-pron* — they surface through the queue in due course.
4. First **lint** pass due after the fifth Routine run (`runs_since_lint` is now 3).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: a word's use in another part of speech gets its own entry and a pointer in `see_also` (not `word_family`, which is for derived/related *different* words — a same-spelling pos-split pointer goes in `see_also` per style guide section 4; the its/it and record-n/record-v style pairs, being different spellings or long-established separate headwords, keep `word_family`).
- American IPA carries no length mark (`ː`); British keeps it. Compare an entry against `any-det.json` or `afraid-adj.json` before drafting a new one.
- Adaptation and usage notes never contain raw IPA; describe pronunciation in plain words with a capitalized respelling.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- Reviewer flags that repeat a house convention are rejected with that reason; do not relitigate them entry by entry. A single, uncorroborated reviewer claim that contradicts an already-accepted pattern elsewhere (see *half*'s predeterminer structure, matched by *both*/*these*) is fair to reject with that reasoning.

## For the owner

- Three items remain open from `journal/2026-09-17.md` and `2026-09-18.md`: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` now has two prune-branch lines (`claude/new-session-1yir52`, `claude/magical-dirac-ydspk3`), both fully merged/absorbed; this tool set cannot delete branches.
