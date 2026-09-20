# [tooling] `--decide --quote` cannot disambiguate a quote that is a substring of another quote on the same field

*Originality run, 2026-09-20 (`20260920T033331Z-pnzdne`), adjudicating `pick-up-phrv`.*

`review_panel.py --decide` matches `--quote` by substring containment (`a.quote in v["quote"]`, `wiki/notes/review-panel-decide-collisions.md`'s 2026-09-20 fix). On `pick-up-phrv`, reviewer-a raised two issues on `core_idea`: one quoting the full sentence (`"To pick up is to lift something ... and starting something."`) and one quoting just its tail (`"starting something"`). Any `--quote` text specific enough to match the second issue is, by construction, also a substring of the first, so both remain ambiguous no matter what is passed — the collision fix does not cover a quote nested inside another quote on the same field.

Worked around this run by logging the second decision directly to `reviews/decisions.jsonl` in the documented format (`wiki/conventions.md` section 4) instead of through the tool, noting the workaround in the decision's own note. Not fixed here (about a fifth-of-the-run guard did not apply; this was one line, not worth the budget mid-adjudication). A future lint or tooling run could add an optional `--index N` (position among the matches, as `--report` lists them) alongside `--quote`, for the rare case where one issue's quote is nested in another's.
