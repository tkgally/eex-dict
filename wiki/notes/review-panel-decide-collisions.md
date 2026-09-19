# review_panel.py --decide collides on repeated fields

*Observed 2026-09-19, build run. A tooling problem, not a rule change — logged here per the no-speculation rule (CLAUDE.md); a fix is a later run's unit, with its own reason.*

`tools/review_panel.py --decide` looks up the issue to log by scanning a reviewer's verdicts for the last one matching `--field`/`--role` (`review_panel.py`, function `decide`). When a single reviewer raises **two or more separate issues on the same field** — as reviewer-a did on `they-pron`'s `adaptation` field (one blocking claim about scope, one minor claim about a typological hedge) — every `--decide` call for that field/role pair is logged against the *same last verdict*, regardless of which issue the session's `--note` actually addresses. The decision line's `severity` and `family` can therefore mismatch the issue the note describes, even though the note text itself is accurate.

**Risk:** `reviews/decisions.jsonl` undercounts how many distinct issues were adjudicated per field, and a family/severity breakdown built from it (`metrics.py --precision`) could misattribute a reviewer's minor note as blocking or vice versa when two issues share a field.

**Not a gate risk:** `validate.py`'s `--gate` check only compares the *total* decision-line count for a `(slug, run_id)` pair against the *total* blocking-issue count in the review file — it does not match decisions to specific verdicts — so this does not let an unadjudicated blocking issue slip through as long as enough decision lines exist overall.

**Suggested fix for a later run** (not made now): give `--decide` an optional `--quote` (or issue index) to disambiguate among multiple verdicts on the same field/role, and have it error instead of silently picking the last match when more than one is found and no disambiguator is given.
