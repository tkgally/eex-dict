# crossref puts sense back-links on the target's first sense

*Observed 2026-09-24, tenth lint pass (`20260924T094259Z-l97vvx`). [tooling]*

`crossref.py --all --apply` added 13 sense-level back-links to 11 entries. `add_backlink` puts a back-link on the target sense that already names the source, else on sense 1. Of the 13, five sat on the wrong sense: `get-v` (illness), `pick-up-phrv` (illness), `make-v` (make a train) and `take-v` (travel by bus) all went to `catch-v` sense 1 (catch a ball), and `chop-v` sense 3 (reduce) went to `cut-v` sense 1 (divide with a knife), leaving `chop-v` in both its `synonyms` and `compare`. This run moved the five by hand to `catch-v` senses 5 and 3 and `cut-v` sense 4; `crossref --gate` still passes, since a back-link on any sense counts.

A sixth has no right home: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense, so the back-link stays on `carry-v` sense 1. The next build or review run that opens `borrow-v` or `carry-v` should settle it (add the arithmetic sense to `carry-v`, or drop the compare).

The module docstring also says the tool writes the note "added as a back-link"; the code writes `null`, so a later session cannot tell a back-link from a drafted reference. Across the dictionary, 30 senses now name the same word under both `synonyms` and `compare`; some are drafted on purpose (*ought*/*should*), others are this effect.

Fix due a later run: write the promised note, or report each new sense back-link for a session to place. Until then, the lint run checks each back-link it adds.

## 2026-09-25: eleventh lint pass — recurred, partly fixed

`crossref --all --apply` added 11 back-links; two sat on sense 1 wrongly (`develop-v` <- `get-v`, illness, moved to sense 4; `drive-v` <- `run-v`, take someone in a car, moved to sense 3). Fix: when no target sense already names the source, `add_backlink` now picks the target sense sharing the most content words (definition and explanation) with the source sense, the source headword counting two, if the best score is at least 2; else sense 1. Measured on the 585 symmetric sense pairs already in the dictionary: first-sense placement matches 397 (68 percent), the new rule 451 (77 percent); the thresholds were chosen on the same pairs. It still misses cases with no shared wording (it would have placed `develop-v` <- `get-v` on sense 1 again) and can pick a wrong later sense (`examine-v` <- `check-v` scores sense 2). The note stays null (the docstring now says so); every lint pass still checks each BACKLINK line. Unit tests in `tools/tests/test_crossref.py`.
