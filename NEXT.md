# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-third scheduled Routine run (closure mode).*

## State

- 239 entries, all `reviewed` (0 `draft`). Queue: 4,109 pending, 239 done, 5 duplicate, 9 declined.
- Closure mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: claimed 14 band-3 closure candidates. Found 7 wrong on part of speech or lemma (`lint_vocab.py`'s -ing/-ed verb guess is confident but unreliable) and 2 stale (word no longer in any entry): declined *concerning-v, enclosed-v, opposed-v, surrounded-v, leaning-v, surrounding-v, arrangement-adj, honor-n, rank-n*; requeued the corrected ones and logged the pattern in `wiki/notes/lint-vocab-pos-guess-gap.md`. Drafted 11 plus one editorial add-on: *role-n, feature-n, contact-n, opposition-n, pressure-n, concerning-prep, concerning-adj, enclosed-adj, opposed-adj, surround-v, arrangement-n, lean-v*.
- Panel: 44 issues, 44 applied, 8 rejected, 0 escalated. Several senses added mid-review on real gaps a reviewer caught (feature film/article, contact's touch sense, arrangement's placement sense, enclosed's letter sense). *pressure-n* got a second panel pass after a truncated reviewer-b reply (the 2026-09-20 parse-failure gate caught the hollow record). *surround-v*'s `core_idea` drew four rounds of inconsistent, single-reviewer complaints (reviewer-b never flagged it); rejected the last two rounds and logged the pattern to `wiki/notes/reviewer-noise.md` — worth watching for a per-field round cap in a future lint pass.
- All American pronunciations checked against the house convention of dropping the length mark on `i`/`ɝ` (caught on three entries, `feature-n`, `lean-v`, `concerning-prep`/`-adj`); one late reviewer-a pronunciation complaint on `lean-v` was rejected against its own CMU-agreed transcription. Gate, caps, links, 305 tests, lint_vocab (0 violations) and crossref (0 errors) all pass. Spend: US$0.48 this run and today.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred for dedicated runs; still worth diversifying into the band-1 noun/verb/adjective backlog otherwise.
2. **review**: roughly 195 `reviewed` entries have had only one panel round; pick the block by `params.block_size` when review is next selected.
3. **closure**: 400+ cross-reference/family/example-vocabulary targets with no entry, still growing — this run added *contact-v, support-n, oppose-v, enclose-v, surroundings-n, surrounding-adj, arrange-v* (word-family/antonym gaps) plus many example-only out-of-vocabulary words (*magazine, dollars, cream, ladder, committee*, and others) via `lint_vocab.py --queue`.
4. Next **lint** due in about 2 runs (was pushed to run 24 at the last lint pass; unchanged, now closer).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a`'s precision this run (0.774, lower than usual, driven by the `surround-v` core-idea disputes) against the 30-percent-noise line at the next lint pass; not yet a pattern across families.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. Caught on three entries this run — check new transcriptions against `see-v`, `these-det`, `person-n` before claiming they're wrong.
- A single reviewer repeatedly flagging the same field across review rounds with inconsistent reasons, while the other reviewer never flags it, is noise (`surround-v`'s `core_idea`, this run) — same standard as one reviewer flagging one round, just compounded.
- Adaptation notes are language-neutral: never name a specific language; hedge with "some/many languages."
- A restriction on one variation of a sense belongs in the subsense's or sense's `explanation`, never as a prefix inside the `definition`.
- Attributive-only / predicative-only codes are easy to over-apply; verify with a real counter-example first (dropped a wrong "predicative only" call on `concerning-adj` this run — "a concerning rise" is natural attributive use).
- `lint_vocab.py`'s pos-guess from a verb-shaped (-ing/-ed) surface form is not more reliable than its flagged noun default; check context before claiming a word tagged `v`.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep* (pronunciation, prior runs), *per-prep, adult-n, accept-v* (pronunciation, run 22), *additional-n* decline (informational, resolved).
