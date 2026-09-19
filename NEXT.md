# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the ninth scheduled Routine run (lint mode).*

## State

- 132 entries, all `reviewed` (0 `draft`). Queue: 4,163 pending, 132 done, 388 closure-gap, 4 duplicate (unchanged this run).
- Lint mode (selector: forced, 5 runs since last lint). Mechanical checks all clean: `check_caps.py`, `check_links.py` both green; `crossref.py --all --apply` (723 missing targets, all expected closure gaps, not errors; back-filled 6 entries' back-links); `lint_vocab.py --all --queue` (0 violations); `claim.py --prune` (2 stale claim files removed).
- `metrics.py --precision`: no (role, family) pair newly crosses under 30% at 20+ decisions. The five already switched off (`tools/review_panel.py` `DISABLED_FAMILIES`) stay off. `reviewer-a` overall 0.57 (892 decisions), `reviewer-b` 0.49 (280, up from 0.37/222) — open question 2 stays "keep". Watch `definition-style` (both roles) and `reviewer-a` `pronunciation` as they approach the threshold. Detail in `wiki/notes/reviewer-precision.md`.
- Wiki checked: index matches pages on disk both ways; log has no gaps; open questions has no stale items.
- `reviews/needs_curator.txt`: four stale prune-branch lines resolved (the remote now shows only `main`, confirming the owner already deleted them); one open pronunciation question remains (`several-det` British).
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass. Spend today: US$1.71 of US$5.00 (this run: US$0, no paid calls).

## Queue (work top-down, one unit at a time)

1. **review**: 23 `markup-pending` entries remain: `big-adj`, `house-n`, `news-n`, `go-v`, `good-adj`, `bank-n`, `see-v`, `family-n`, `x-ray-n`, `people-n`, `shit-n`, `get-v`, `record-n`, `record-v`, `take-v`, `color-n`, `head-n`, `thing-n`, `old-adj`, `way-n`, `water-n`, `make-v`, `time-n`. All are large, multi-sense entries (5–14 senses) — expect fewer per run than a typical review pass.
2. **review**: 107 entries reviewed only once (one panel round), most of the 23 above included.
3. **build/closure**: pos-split pointers queued from recent runs — `something-pron`, `neither-pron`, `enough-adv`, `she-pron`, `him-pron`, `his-pron`, `himself-pron`, `hers-pron`, `herself-pron`.
4. **closure**: cross-reference/family targets with no entry yet (388+, growing; this run's crossref pass added more, all expected).
5. Next **lint** due in about 5 runs.
6. Next **originality** check due in 8 more runs (forced every 10th; this was run 2 of the current cycle).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- A rewritten definition must still clear `lint_vocab.py`'s closed defining vocabulary — check wording against `schema/defining-vocabulary.txt` early.
- `wiki/notes/reviewer-noise.md`: originality-check reviewer over-calls "copied"; watch for a repeat.
- `wiki/notes/review-panel-parse-failures.md`: spot-check a reviewer's `ok` count isn't suspiciously 0 before trusting a review pair.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision now 0.49 over 280 decisions, up from 0.37/222.
- `reviews/needs_curator.txt` now has only the one open item (a pronunciation question, *several-det* British) — the four stale prune-branch lines were resolved this run since the branches are already gone from the remote.
- The `review_panel.py` parse-failure gap noted last run (a truncated reply can silently record a hollow, zero-verdict pass) is still unfixed — worth a session, not urgent.
