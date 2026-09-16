# Log

*Append-only, newest first. Header: `## [YYYY-MM-DD] <operation> | <title>`. At most 200 words per entry.*

## [2026-09-16] setup | Founding session, Stage A: scaffold

Created the repository skeleton from the founding prompt: `framework.md` copied verbatim from the owner's knowledge-base framework; `PROJECT.md` (charter), `CLAUDE.md`, `resume-prompt.md`, `NEXT.md`, licences (data CC0 1.0, code MIT), README; `schema/entry.schema.json` and `schema/vocabularies.json` with the original usage-label sets; `wiki/` with conventions, index, this log, open questions, and 28 decision pages (two of them, defining-vocabulary and pronunciation-pipeline, to be completed in Stage B); `inbox/`, `journal/`, `reviews/`, `headwords/`, `metrics/`, `config/` (budget rule, ledger, model roles); tools `validate.py`, `schema_check.py`, `eexlib.py`, `entry_path.py`, `check_caps.py`, `check_links.py`, `spend.py`, `openrouter.py`, `wait.py` with unit tests; `.github/workflows/validate.yml`; a first version of `wiki/style-guide.md` (model entries to come from the seed set). Verified reachable and recorded in `sources/README.md`: OpenRouter's model list, the CMU Pronouncing Dictionary raw file, the Wiktionary API. Model roles chosen and verified against the OpenRouter list (`config/models.md`).
