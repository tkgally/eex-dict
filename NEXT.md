# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the seventh scheduled Routine run (originality mode).*

## State

- 132 entries, all `reviewed` (0 `draft`). Queue: 4,163 pending, 132 done, 388 closure-gap, 4 duplicate (unchanged this run — no new drafting).
- First originality check: `originality_check.py sample --n 10` over the 132 reviewed entries. No exact-phrase web search matched a published source for any of the 10, but reviewer-a called all 10 "copied" on style alone with no source cited — logged as reviewer overcall in new page `wiki/notes/reviewer-noise.md`. On my own reading against recalled published wording, three looked like real paraphrases of a specific dictionary's sentence shape: `be-v` `be-that-as-it-may`, `please-interj` sense 3, `person-n` `in-person`. Rewrote all three; full pipeline (validate, panel, adjudicate, validate, lint_vocab, crossref) on each: 17 issues, 7 blocking, 9 applied / 8 rejected. Two first-draft rewrites hit defining-vocabulary violations and were rewritten again to clear them. Also cleared `person-n`'s long-standing `markup-pending` flag while it was open.
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass. Spend today: US$1.09 of US$5.00 (this run: US$0.16).
- `next_mode.py` for the next run: not yet queried by this run's writer; the debt scheduler will likely pick **build** or **review** (both positive debt last measured). Re-run `next_mode.py --explain` at the start of the next session.

## Queue (work top-down, one unit at a time)

1. **review**: 120 entries reviewed only once (one panel round); 33 `markup-pending` entries remain (down from 34: `person-n` cleared this run).
2. **build/closure**: pos-split pointers queued from recent runs — `something-pron`, `neither-pron`, `enough-adv`, `she-pron`, `him-pron`, `his-pron`, `himself-pron`, `hers-pron`, `herself-pron`.
3. **closure**: cross-reference/family targets with no entry yet (still 388+, growing as new phrases/word-family entries are added).
4. Next **lint** due in about one run from now (runs_since_lint was 3 as of the last build run, plus this originality run = 4; lint is forced every 5).
5. Next **originality** check due in 10 more runs (forced every 10th run; this was run 10 of the cycle).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong (rejected again this run on `please-interj`).
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- Originality-check reviewer answers are a style-only signal (this run: 10/10 "copied," 7/10 unsupported by search) — weigh them against the session's own reading and the exact-phrase search, not at face value; watch `wiki/notes/reviewer-noise.md` for a repeat.
- A rewritten definition must still clear `lint_vocab.py`'s closed defining vocabulary before it is done — check candidate wording against `schema/defining-vocabulary.txt` early, not after the fact.
- Do not re-enable a switched-off (role, family) pair without a fresh measurement showing it above 30 percent.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision 0.37 over 222 decisions, not yet the twenty more the assumption waits for.
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
- New this run: `wiki/notes/reviewer-noise.md` flags that the originality-check reviewer role may over-call "copied" regardless of real resemblance; no action needed yet, just a watch item for the next originality run.
