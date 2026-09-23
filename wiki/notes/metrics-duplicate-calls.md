# `metrics.py` sometimes runs twice in one session, inflating the run count

*Sixth lint pass, 2026-09-21. Caught while reading `wiki/log.md` against `metrics/history.jsonl` for gaps.*

## What was found

`metrics/history.jsonl` has 35 rows but only 30 distinct `run_id`s: five run ids each appear twice, always in a `build`-mode run, always about one to two minutes apart (`20260919T033309Z-kxdv7t`, `20260919T153326Z-fzpnak`, `20260920T063327Z-1rtv3d`, `20260920T213316Z-u156ny`, `20260921T093324Z-b8bp7v`). In every pair the first row carries the run's real review counts (`reviews.issues` 29-47); the second, near-identical row shows `reviews.issues: 0` and an empty `precision_by_role`, with the same `entries_changed`, `spend_run_usd`, and queue snapshot as the first.

The cause is visible in `review_stats()` (`tools/metrics.py`): it counts only decisions and reviewer verdicts timestamped after the previous history row's `ts`. The first call in a run correctly counts everything since the last logged run; a second call minutes later, with nothing new decided in between, correctly counts zero — so the second row is not corrupt data, just a redundant, near-empty row. The likely mechanism: a build-mode session ran `metrics.py` once per `routine-prompt.md` section 6 step 1, then ran it again from `CLAUDE.md`'s own generic "Finish, every session" checklist, which also lists `python3 tools/metrics.py` — the two files' wrap-up lists overlap and a session that followed both literally calls it twice. It has only ever happened in `build`-mode runs, consistent with a session finishing the mode-specific pipeline and then separately re-running the general closing checks.

## Why it matters

`tools/next_mode.py`'s `signals()` uses `len(history())` — every row, not distinct run ids — for `runs_total`, and counts rows (not runs) back to the last `lint` row for `runs_since_lint`. Both periodic triggers (`lint` forced every 5 runs, `originality` forced on run numbers that are multiples of 10) key off these counts, so five inflated rows mean both triggers can fire one run earlier than the true run count would call for. This run's own selection (`forced: 5 runs since the last lint`) was itself inflated by one: only 4 distinct runs (`review oqku5d`, `build b8bp7v`, `review 8t05x6`, `build vegr13`) happened since the last lint row, not 5.

## What was not done

No fix this run (`CLAUDE.md` rule 10 and the lint-mode guard: an observed problem is written up first; the fix is a later run's unit with a logged reason). A fix needs a design call this pass didn't make: dedupe `history()` by `run_id` (keep the row with the larger `reviews.issues`, or the last one, or sum them) in `next_mode.py`, or have `metrics.py --mode` refuse or overwrite a second row for a `run_id` already in the file. Either touches shared tooling, not a semantic field, so it is in scope for a script — just not this run's unit.

## What the next session should do

Keep this in mind when reading `next_mode.py --explain`'s `runs_total` / `runs_since_lint`: they run about one-sixth high on average (5 inflated of 30 real runs so far). Do not call `tools/metrics.py` more than once per run — follow `routine-prompt.md` section 6 step 1 only; `CLAUDE.md`'s generic finish checklist is superseded by the mode-specific wrap-up for a scheduled Routine run. A future lint or setup unit should dedupe `history()` by `run_id` in `next_mode.py` (and consider having `metrics.py` warn or refuse on a duplicate `run_id`).

## Fixed 2026-09-23 (ninth lint pass)

`next_mode.py`'s `history()` now keeps one row per `run_id` (`dedupe_runs`; test in `tools/tests/test_next_mode.py`), so a doubled `metrics.py` call no longer advances the lint or originality trigger. `metrics/history.jsonl` itself is unchanged (53 rows, 47 runs at the fix). One consequence: the run count dropped by six, so the originality check forced at inflated "run 50" earlier today will fire again at true run 50, three runs after this one.
