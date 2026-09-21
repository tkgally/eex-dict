# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-ninth scheduled Routine run (lint mode).*

## State

- 262 entries, all `reviewed` (0 `draft`). Queue: 4,119 pending, 262 done, 4 duplicate, 9 declined.
- Lint mode (selector: forced, five runs since last lint — one of those five was an inflated duplicate row, see Fences). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Mechanical checks: caps, links, gate, 305 unit tests, lint_vocab and crossref gates all pass. `crossref.py --all --apply` back-filled `word_family` on six entries (`actor-n, adopt-v, age-v, ahead-adv, aware-adj, have-v`); 797 missing crossref targets remain queued-eligible (unchanged; no `--queue` this call). `lint_vocab.py --all --queue`: 0 violations. `claim.py --prune` removed 2 stale claim files.
- Reviewer precision: no family newly crosses under 30 percent at twenty-plus decisions; the five already switched off stay off. `reviewer-a` overall 0.67 (1347 decisions, up from 0.64); `reviewer-b` 0.65 (489, up from 0.62). `reviewer-a` `pronunciation` moved toward the 30-percent line for the first time (0.33, was 0.37) — the nearest live family to switch-off; watch it closely next lint pass.
- New tooling gap found and logged (not fixed): `metrics/history.jsonl` has five duplicate rows from past `build` runs calling `metrics.py` twice, inflating `next_mode.py`'s `runs_total`/`runs_since_lint` counts. Detail and proposed fix in [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md). Do not call `tools/metrics.py` more than once per run.
- Wiki index checked against pages on disk both ways: clean. `reviews/needs_curator.txt`: ten open items, no duplicates, all still awaiting the owner.
- Spend: US$0 this run; US$3.58 today (unchanged, lint mode did no paid calls; `run_budget_usd` was 0).

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred; otherwise keep diversifying (e.g. *aim, air, airport, alarm, activity, address, adjective, advertise, affect, agreement* siblings like *act, actual, actually*).
2. **review**: 196 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
3. **closure**: 450+ cross-reference/family targets with no entry, still growing (e.g. this run's own back-links did not add new ones; closure_gap is 454 per `metrics.py`).
4. Next **lint** due in about 5 real runs (run ~34 by true count, since the trigger fires on raw history rows — see the tooling-gap note above; do not assume run ~29 was exact).
5. Next **originality** check due around run 30 (forced: multiples of 10; also subject to the same inflation caveat).
6. A future lint or setup unit should dedupe `next_mode.py`'s `history()` by `run_id` and consider having `metrics.py` refuse/warn on a duplicate `run_id` for the current run.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- A single reviewer repeatedly flagging the same field across rounds with inconsistent reasons, while the other reviewer never flags it, is noise.
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid.
- Do not add a note-only line to `schema/inflection-exceptions.json` for a fully regular verb just to record a spelling variant (flips `source`/`regular`, can break unit tests). Reject the issue instead.
- core_idea and every sense's own `.definition` draw on the defining vocabulary; only a headword's own first sense is exempt.
- `runs_total`/`runs_since_lint` from `next_mode.py --explain` run about one-sixth high (5 duplicate rows of 30 real runs so far); do not trust them as an exact run count until the dedupe fix lands.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep, per-prep, adult-n, accept-v* (pronunciation), *admire-v, adult-adj* (pronunciation), *additional-n* (declined, resolved).
