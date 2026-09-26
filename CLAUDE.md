# CLAUDE.md — ground rules for every session

**TKG English Learner's Dictionary**: an original English-English learner's dictionary, one JSON file per entry in `entries/`, published as a static site built by GitHub Actions from `docs/` (never committed). The charter is `PROJECT.md` (owner-set, never edited by a session). The knowledge base runs on `framework.md`. Sessions are unattended: nobody answers questions mid-run.

**Read, in this order, every session:** this file; `resume-prompt.md`; `NEXT.md`; `wiki/index.md`; `inbox/` (anything there outranks the queue); then only the pages the chosen unit needs. Before drafting or reviewing entries, read `wiki/style-guide.md` and `wiki/conventions.md`. A scheduled run follows `routine-prompt.md`. Never load the whole wiki.

## Non-negotiables

1. **No more than 20 new entries per run**, each through the full pipeline below before it is marked `reviewed`. A scheduled run is a series of cycles, each merged before the next (`routine-prompt.md`); every per-run rule applies to each cycle. Fewer, better entries beat the cap. At most 40 `draft` entries may exist at once; above that, building stops until reviewing catches up.
2. **No script writes a semantic field.** See the ownership table. A "systemic fix" to a semantic field is a per-entry model pass with review, at most 40 entries per run.
3. **Every classifying field is a closed vocabulary** (`schema/vocabularies.json`). Adding a value is a logged decision in the same pull request as the first entry that needs it.
4. **Nothing from any external data set is stored in the repository**, whatever its licence: no frequency lists, word lists, pronouncing dictionaries, WordNet, Wiktionary. Open resources may be consulted at run time, in a temporary directory outside the repository, to check a fact; the entry records only the verdict. Copyrighted dictionaries are never consulted while drafting. `sources/` holds markdown only.
5. **Slugs are permanent.** Nothing is renumbered or deleted; a rename goes through `headwords/redirects.json` with a stub file left behind.
6. **A refusal is recorded, never argued with.** If the model declines to write an entry, `tools/queue.py set <headword> <pos> declined --note "<reason>"`, one line in `reviews/needs_curator.txt`, move on.
7. **Never print, log, or commit `OPENROUTER_API_KEY`.** Check `config/budget.md` and the ledger before any paid call and record the billed actual after (`tools/spend.py`).
8. **No model identifiers** in commit messages, pull-request text, or wiki prose. Model names in entry provenance, review files, and `config/models.md` are data and belong there.
9. **Caps are enforced by CI** (`tools/check_caps.py`): this file 1,500 words; `resume-prompt.md` 800; `routine-prompt.md` 2,500; `NEXT.md` 60 lines; the style guide 3,500; the wiki 30,000 excluding index, log, and decisions; a log entry 200. Trim before adding.
10. **No new machinery on speculation.** An observed problem is written to `wiki/notes/` first; the change comes in a later run with a logged reason.

## Field ownership

| Written by a script (may be regenerated) | Written per entry by a model, then reviewed |
|---|---|
| `id`, `slug`, `homograph`, the shard path (`tools/entry_path.py`) | `headword`, `pos`, `variants` |
| `inflections` (`tools/inflect.py`: rules plus `schema/inflection-exceptions.json`) | `pronunciation.*.ipa` and `source`; `pronunciation.variants`, `notes` |
| `pronunciation.*.checked_by` and `status` (`tools/pronounce_check.py`) | `labels` at every level, `core_idea` |
| `frequency.band`, `frequency.defining_vocabulary` (`tools/queue.py stamp`) | every `senses[]` field: definition, explanation, grammar, examples, collocations, cross-references, subsenses, adaptation |
| `provenance.created`, `modified`, `run_id`, `reviews`, `status`, `flags` | `phrases`, `word_family`, `synonym_discrimination`, `usage_note`, `learner_errors`, `etymology`, `see_also`, entry-level `adaptation` |
| build-time links (`tools/link_words.py`, in `docs/` only) and back-links that mirror an existing forward reference (`tools/crossref.py`) | `l1` |
| JSON key order and formatting (`tools/validate.py --fix-format`) | |

Nothing in the right-hand column may be generated, rewritten, or bulk-edited by a script, ever.

## The pipeline for every new or rewritten entry

In this order: `tools/validate.py <files>` → `tools/inflect.py <slugs>` → `tools/pronounce_check.py <slugs>` → `tools/review_panel.py <slugs>` (both reviewers, every field) → adjudication: read every blocking issue yourself, decide `apply` / `reject` / `escalate`, log each to `reviews/decisions.jsonl`, fix the entry → `tools/validate.py` again → `tools/lint_vocab.py <files>` → `tools/crossref.py <slugs>` → set `provenance.status: reviewed`. Never apply a reviewer's fix blindly; never reject one without a logged reason. A factual disagreement between reviewers is settled by open data when any bears on it; otherwise the entry gets a `provenance.flags` entry and the question goes to `reviews/needs_curator.txt`.

## Session mechanics

**Start.** `date -u`. `git fetch origin`. If an open pull request from this project exists (head `claude/*`), a predecessor stopped between push and merge: if its checks are green and it is mergeable, merge it (squash) and `git merge origin/main`; if a check failed, absorb its branch with `python3 tools/absorb_branch.py <branch> --pr <n>` and fix what CI reported; if still pending, leave it and note it. Sweep orphan `claude/*` branches the same way (`--residue` first). Confirm your checkout contains `origin/main`'s latest commit.

**Work** on the harness-assigned `claude/*` branch, never on `main`. Claim headwords before drafting (`tools/claim.py`); claims on unmerged branches count as taken.

**Finish, every session.** `python3 tools/validate.py --gate`; `python3 tools/check_caps.py`; `python3 tools/check_links.py`; `python3 -m unittest discover -s tools/tests -t .`; `python3 tools/metrics.py`; update `wiki/index.md` and `wiki/log.md`; rewrite `NEXT.md`; write the journal entry (`clear-reports` style: plain, self-contained English). Commit with an imperative subject prefixed by the mode or stage (`build: …`, `site: …`, `setup: …`). `git push -u origin <branch>` (on network failure retry 4 times: 2, 4, 8, 16 seconds). Then the atomic tail, with no other work in between:

1. `mcp__github__create_pull_request` (`owner: "tkgally"`, `repo: "eex-dict"`, `base: "main"`, ready, not draft); the body is a report to the owner in plain English.
2. Poll `mcp__github__pull_request_read` with `method: "get_check_runs"` (never `get_status`). Green = `total_count >= 1` and every run `completed` with conclusion `success`, `neutral`, or `skipped`; failed = any other completed conclusion; pending = anything else. While pending, `python3 tools/wait.py 60` in the foreground (a backgrounded `sleep` returns at once), then re-poll; at most 15 polls.
3. Green → `mcp__github__merge_pull_request` with `merge_method: "squash"`, then confirm `main` advanced (`git fetch origin main`, the merge commit is there). Failed → read the failing step (`mcp__github__get_job_logs`, `failed_only: true`), fix, run the local checks, push once, poll again; a second failure leaves the pull request open and is reported in `NEXT.md` for the next session to absorb. Pending at the cap → leave it open and say so.
4. Never enable auto-merge, never check out `main`, never delete a branch, never push to a pull request that is green and waiting.

If the merge cannot land, say so at the top of `NEXT.md` before stopping. Kill background processes; leave a clean tree.

## Tools

Python 3 standard library only, so any container can run them. `tools/README.md` lists every command by job; every tool has `--help`. A tool that consults an open resource downloads it to `.tmp/` (gitignored), records only a verdict, and works without it when it is unreachable. Unit tests live in `tools/tests/` and run in CI.
