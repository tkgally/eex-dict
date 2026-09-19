# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the eleventh scheduled Routine run (build mode).*

## State

- 158 entries, all `reviewed` (0 `draft`). Queue: 4,138 pending, 158 done, 386 closure-gap, 4 duplicate.
- Build mode (selector: highest scheduler debt). Claimed 20 pronoun slugs, drafted 13, released 7 back to pending: `neither-pron`, `nobody-pron`, `none-pron`, `nothing-pron`, `other-pron`, `some-pron`, `what-pron`.
- New entries: `we-pron`, `us-pron` (completes the 1st-person-plural set), `they-pron`, `them-pron`, `theirs-pron`, `themselves-pron` (completes the 3rd-person-plural set), `someone-pron`, `somebody-pron`, `something-pron`, and the standalone demonstratives `this-pron`, `that-pron`, `these-pron`, `those-pron` (companions to the existing determiners). Full pipeline run; gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass.
- Pronunciation: 26 transcriptions checked; `themselves-pron` British disputed and flagged — panel favors a reduced first syllable over the drafter's full-vowel `ðemˈselvz`. Curator line added.
- Review: 29 issues, 18 blocking, 24 applied, 4 rejected (precision this run: reviewer-a 0.94, reviewer-b 0.70). Two real, substantive catches: singular `they`/`them` wrongly restricted to "unstated sex," missing the established use for a known nonbinary referent — broadened in both entries; `themselves` wrongly allowed a singular "thing" as antecedent — fixed to plural throughout. `that-pron`'s definition overstated physical distance as the core meaning, missing ordinary discourse reference (*that's a great idea*) — broadened. Rejected a reviewer's claim that `that-pron` needs a relative-pronoun sense: that use is filed at the already-queued `that-conj`, per the one-part-of-speech-per-entry rule.
- Three defining-vocabulary violations fixed (*relevant*, *identify*, *British* replaced or removed from definitions; labels field already carries the region).
- Tooling gap found and logged (not fixed, per no-speculation rule): `review_panel.py --decide` collides when a reviewer raises two issues on the same field — see `wiki/notes/review-panel-decide-collisions.md`.
- Own slip caught and fixed this run: after trimming a 20-slug claim down to 13, the 7 released slugs' `headwords/queue.tsv` rows were still marked `claimed` (claim.py sets that status per slug); reset to `pending` before wrap-up.
- Pre-flight: no open pull request; one stale remote-tracking ref (`origin/claude/funny-goodall-fzpnak`, already deleted upstream) pruned locally; inbox empty.
- Spend today: US$2.35 of US$5.00 (this run: US$0.31).

## Queue (work top-down, one unit at a time)

1. **review**: 23 `markup-pending` entries remain (unchanged this run): `big-adj`, `house-n`, `news-n`, `go-v`, `good-adj`, `bank-n`, `see-v`, `family-n`, `x-ray-n`, `people-n`, `shit-n`, `get-v`, `record-n`, `record-v`, `take-v`, `color-n`, `head-n`, `thing-n`, `old-adj`, `way-n`, `water-n`, `make-v`, `time-n`. All large, multi-sense.
2. **review**: 133 entries reviewed only once (one panel round), most of the 23 above included, plus this run's 13.
3. **build/closure**: the released quantifier/indefinite pronouns (`neither`, `nobody`, `none`, `nothing`, `other`, `some`) plus `what-pron` are pending again — try a smaller batch next time, one or two per run, since two runs now have found them heavier than a typical entry.
4. **closure**: cross-reference/family targets with no entry yet (386+, growing), including `that-conj` (queued this run).
5. Next **lint** due in about 3 runs (also: fix the `--decide` collision noted above).
6. Next **originality** check due in 7 more runs (forced every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- Singular `they`/`them`/`themselves` cover both unstated/unknown sex and a known nonbinary referent — don't narrow the wording back to "unstated sex" alone.
- After trimming a claim file, also revert the dropped slugs' `headwords/queue.tsv` status to `pending` with `queue.py set`; `claim.py` marks them `claimed` at claim time and nothing reverts that automatically.
- `wiki/notes/reviewer-noise.md`: originality-check reviewer over-calls "copied"; watch for a repeat.
- `wiki/notes/review-panel-parse-failures.md` and `review-panel-decide-collisions.md`: two open `review_panel.py` tooling gaps for the next lint pass.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" (0.49 over 280 decisions).
- `reviews/needs_curator.txt` has three open items: *several-det* British pronunciation, *ourselves-pron* American pronunciation, and now *themselves-pron* British pronunciation (panel favors a reduced first syllable; drafter's full-vowel form kept meanwhile).
- The `review_panel.py` parse-failure gap noted earlier, plus the new `--decide` collision gap, are both still unfixed — worth a lint session.
