# tools/ — every command, grouped by job

All tools are Python 3 standard library only and run from the repository root. Every tool has `--help`. Nothing here writes a semantic field of an entry (`CLAUDE.md`, ownership table); tools that consult an open resource download it to `.tmp/` (gitignored) and record only a verdict.

## Entries: shape and paths

| Command | Job |
|---|---|
| `python3 tools/entry_path.py <slug>` | the file path for a slug; `--slug "<headword>" <pos> [homograph]` computes the slug; `--sub-id "<phrase>"` a phrase sub_id; `--shard <slug>` the shard |
| `python3 tools/validate.py [files] [--all] [--changed] [--gate] [--fix-format]` | schema, vocabularies, slug and path agreement, no abbreviations, well-formed inline marks, an example that lacks the headword (warning), plain words in pronunciation notes, example counts, adaptation caps, pronunciation presence, reviewed-status requirements, draft ceiling (`--gate`); `--fix-format` normalizes key order |
| `python3 tools/schema_check.py <file>` | the JSON-schema-subset checker validate.py uses (no external library) |
| `python3 tools/inflect.py <slugs> [--dry-run]` | writes `inflections` from the rules and `schema/inflection-exceptions.json`; `--word W --pos P [--code C]` shows forms; `--confirm <slugs>` marks them verified after review |
| `python3 tools/queue.py stamp <slugs>` | writes `frequency.band` and `frequency.defining_vocabulary` from the queue and the defining vocabulary |

## Verification pipeline

| Command | Job |
|---|---|
| `python3 tools/pronounce_check.py <slugs> [--no-cmu] [--threshold N]` | panel of models plus a run-time CMU consultation; sets each transcription's `status` and `checked_by` |
| `python3 tools/review_panel.py <slugs>` | both reviewers, every field, closed verdicts; writes `reviews/<run-id>/<slug>.json` and the provenance record |
| `python3 tools/review_panel.py --report <slug>` | the open issues from the latest review file |
| `python3 tools/review_panel.py --decide <slug> --field F --role R --decision apply\|reject\|escalate --note "..."` | one adjudication line in `reviews/decisions.jsonl` |
| `python3 tools/lint_vocab.py [files] [--changed --gate] [--all --queue]` | definition words outside the defining vocabulary with no entry; `--gate` is the CI ratchet on changed entries; `--queue` files closure candidates |
| `python3 tools/crossref.py [slugs] [--apply] [--queue] [--gate]` | referenced slugs exist; symmetric back-links added with `--apply`; missing targets queued |
| `python3 tools/originality_check.py sample [--n N]` / `record <date> --file F` | the periodic originality checklist and its record in `reviews/originality/` |

## Queue and claims

| Command | Job |
|---|---|
| `python3 tools/queue.py list\|add\|add-batch\|set\|next\|sync\|counts` | the headword queue (`headwords/queue.tsv`); only this tool edits it |
| `python3 tools/claim.py --id` | this run's id (`.tmp/run-id`) |
| `python3 tools/claim.py --from-queue --n N [--band B] [--source S]` or `"<headword>\|<pos>" ...` | claim slugs for this run in `headwords/claims/<run-id>.json`, skipping slugs claimed on any branch |
| `python3 tools/claim.py --taken` / `--prune` | every taken slug; delete claim files whose entries exist on main |

## The Routine

| Command | Job |
|---|---|
| `python3 tools/next_mode.py [--explain] [--simulate N]` | pick the mode from `config/routine-config.json`, the budget, and the run history |
| `python3 tools/spend.py check --cost X` / `record --cost X --purpose P --model M` / `status` | the daily OpenRouter ledger (`config/budget-ledger.json`) |
| `python3 tools/openrouter.py --role R --prompt "..."` / `--list-roles` | the model client; roles from `config/models.md` |
| `python3 tools/metrics.py --mode M --changed N [--site-build S]` / `--summary` / `--precision` | one metrics line per run; reviewer precision by role and family |
| `python3 tools/absorb_branch.py <branch> [--pr N]` / `--residue <branch>` | take over a stranded run's branch with a per-file merge policy |
| `python3 tools/wait.py [seconds]` | foreground wait between CI polls |

## Site

| Command | Job |
|---|---|
| `python3 tools/build_site.py [--out docs]` | render the site from `entries/`, `journal/`, and `metrics/` (never committed; GitHub Actions runs it on merge) |
| `python3 tools/link_words.py` | the build-time linker: links every word that has an entry, renders the inline marks, and marks the headword in example sentences (library used by build_site.py; `--text "..."` shows links for a string) |
| `python3 tools/site_check.py` | Playwright checks at phone and desktop widths (home page, three entry pages, search of an inflected form, a preview) |

## Integrity and caps

| Command | Job |
|---|---|
| `python3 tools/check_caps.py` | word and line caps on the instruction files and the wiki |
| `python3 tools/check_links.py [dirs or files]` | every relative markdown link resolves (anchors not validated) |
| `python3 -m unittest discover -s tools/tests -t .` | the unit tests (run in CI) |

## The local gate (what CI runs on a pull request)

```bash
python3 -m unittest discover -s tools/tests -t . && python3 tools/validate.py --gate && python3 tools/check_caps.py && python3 tools/check_links.py && python3 tools/lint_vocab.py --changed --gate && python3 tools/crossref.py --gate
```
