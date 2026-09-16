# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-16 by the founding session, Stage A. Read `resume-prompt.md` first.*

## State

- Stages A and B of the founding session are merged: scaffold, schema, vocabularies, decision pages, the defining vocabulary (2,394 lemmas), the queue (3,907 rows), the pronunciation test and its rule, every pipeline, Routine, and site tool, `routine-prompt.md`.
- Seventy-seven seed entries are drafted on the founding session's branch (claimed in `headwords/claims/`), not yet reviewed or merged; Stage C (reviews, site check, style-guide model entries) and Stage D (dry run, final baton and journal) follow, with the reviews after the UTC day rolls over because the daily budget is spent.
- The Routine must not be scheduled until the founding session finishes Stage D and the owner has reviewed the seed set.

## Queue (work top-down, one unit at a time)

1. Stage C: the 77 seed entries through the rest of the pipeline (pronunciation check, both reviewers, adjudication, lint, crossref), three of them into the style guide as model entries, the British hand check of the pronunciation test, site built and checked, the seed review guide; merge.
2. Stage D: dry-run a five-entry build cycle by `routine-prompt.md` and fix the prompt; final `NEXT.md` and journal; merge.
4. First lint pass due after the fifth Routine run (framework section 6).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Model slugs live only in `config/models.md`; code names roles.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- `jsonschema` is not installed and must not be required: `tools/schema_check.py` is the validator.

## For the owner

- Nothing needs your input until the founding session reports at the end of Stage D. Open questions with working assumptions: `wiki/open-questions.md`.
