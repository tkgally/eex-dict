# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-fourth scheduled Routine run (lint mode).*

## State

- 239 entries, all `reviewed` (0 `draft`). Queue: 4,109 pending, 239 done, 5 duplicate, 9 declined.
- Lint mode (selector: forced, 5 runs since the last lint pass). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: full mechanical sweep. `check_caps`, `check_links` clean. `crossref --all --apply`: 0 errors, 928 warnings (all expected missing closure-queue targets), 5 entries got mirrored back-links. `lint_vocab --all --queue`: 0 violations across 239 entries. `claim.py --prune` removed 3 stale claim files.
- `metrics.py --precision`: the five (role, family) pairs switched off 2026-09-19 are unchanged in count — confirms the downgrade-to-`ok` mechanism still holds after two more build/closure runs. Nothing newly crosses 30 percent at twenty-plus decisions. `reviewer-a` overall precision is now 0.64 (up from 0.62), `reviewer-b` 0.62 (up from 0.58); `reviewer-a` `pronunciation` (0.37, 49 decisions) stays the nearest live family to the switch-off line, unchanged since the last pass. Full table in `wiki/notes/reviewer-precision.md`.
- Wiki check: `index.md` matches all 30 decision pages and 11 notes on disk both ways; `log.md` has no gaps; `open-questions.md`'s five items and `reviews/needs_curator.txt`'s eight lines are unchanged, no duplicates found. The two tooling notes previously flagged "due a later run" (`pronounce-check-stale-flag`, `review-panel-decide-substring-collision`) already carry a 2026-09-20 fix; nothing outstanding to repair this pass.
- No entries were touched this run (lint's unit is mechanical/judgmental checks, not drafting). Gate, caps, links, 305 tests, lint_vocab and crossref gates all pass. Spend: US$0 this run; US$0.48 today so far.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred for dedicated runs; otherwise keep diversifying into the band-1 noun/verb/adjective backlog.
2. **review**: roughly 195 `reviewed` entries have had only one panel round; pick the block by `params.block_size` when review is next selected.
3. **closure**: 400+ cross-reference/family/example-vocabulary targets with no entry, still growing; check for more mistagged closure-queue rows the way this run's predecessor found (verb-shaped surface forms that are really adjectives, or stale rows for words no longer in any entry).
4. Next **lint** due in about 5 runs (run ~29).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a`'s `pronunciation` family (0.37, 49) against the 30-percent line as it accumulates; nothing actionable yet.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. Check new transcriptions against `see-v`, `these-det`, `person-n` before claiming they're wrong.
- A single reviewer repeatedly flagging the same field across review rounds with inconsistent reasons, while the other reviewer never flags it, is noise — same standard as one reviewer flagging one round, just compounded (`surround-v`'s `core_idea`, 2026-09-21).
- Adaptation notes are language-neutral: never name a specific language; hedge with "some/many languages."
- A restriction on one variation of a sense belongs in the subsense's or sense's `explanation`, never as a prefix inside the `definition`.
- Attributive-only / predicative-only codes are easy to over-apply; verify with a real counter-example first.
- `lint_vocab.py`'s pos-guess from a verb-shaped (-ing/-ed) surface form is not more reliable than its flagged noun default; check context before claiming a word tagged `v`.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep* (pronunciation, prior runs), *per-prep, adult-n, accept-v* (pronunciation, run 22), *additional-n* decline (informational, resolved).
