# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-16 by the founding session, Stage A. Read `resume-prompt.md` first.*

## State

- Stage A of the founding session is merged: scaffold, schema, vocabularies, decision pages, core tools, CI gate.
- No entries exist yet. The defining vocabulary, the queue, the style guide, the seed set, the site, and the Routine are still to be built (Stages B to D of the founding prompt).
- The Routine must not be scheduled until the founding session finishes Stage D and the owner has reviewed the seed set.

## Queue (work top-down, one unit at a time)

1. Stage B: `schema/defining-vocabulary.txt` from three models' judgment; `headwords/queue.tsv` bands 1 to 3; `tools/inflect.py` with `schema/inflection-exceptions.json` checked by two models; `tools/lint_vocab.py`; the pronunciation experiment (design frozen first) and `tools/pronounce_check.py`; complete the two pending decision pages.
2. Stage C: `wiki/style-guide.md`; 50 to 100 seed entries through the full pipeline (`tools/review_panel.py` needed first); `tools/build_site.py`, `pages.yml`, Playwright check; the seed review guide in `journal/`.
3. Stage D: `routine-prompt.md`, `tools/next_mode.py`, `config/routine-config.json`, `tools/claim.py`, `tools/queue.py`, `tools/originality_check.py`, `tools/metrics.py`, `tools/absorb_branch.py`, `tools/README.md`; dry-run five entries by the prompt; final journal.
4. First lint pass due after the fifth Routine run (framework section 6).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Model slugs live only in `config/models.md`; code names roles.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- `jsonschema` is not installed and must not be required: `tools/schema_check.py` is the validator.

## For the owner

- Nothing needs your input until the founding session reports at the end of Stage D. Open questions with working assumptions: `wiki/open-questions.md`.
