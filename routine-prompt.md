# routine-prompt.md — the scheduled Routine

You are one unattended run of the **TKG English Learner's Dictionary**, an original English-English learner's dictionary of JSON entries published as a static site. Runs are scheduled every three hours and may overlap. A run lasts about two hours and is a series of **cycles**: each cycle does one unit of work chosen by a selector, verifies it, records it, and merges its own pull request, and the run starts cycle after cycle until the run clock says stop. Nobody answers questions; the record-assumption-and-proceed rule applies (`resume-prompt.md`). Follow this file literally, in order. It does not restate the rules: read `CLAUDE.md` first, then `resume-prompt.md`, `NEXT.md`, `wiki/index.md`, and `inbox/`; before drafting or reviewing an entry read `wiki/style-guide.md`, `wiki/conventions.md` section 2, `schema/entry.schema.json`, `schema/vocabularies.json`, and one existing entry of the same part of speech as a model of the shape.

## Run shape: cycles until the clock says stop

The run's first command is `python3 tools/run_clock.py start` (it records the start time; a repeat does not reset it).

1. **Cycle 1** is section 0 (once per run), then sections 1 to 6. Cycles 2, 3, ... start at section 1. Each cycle is complete on its own: its own run id, claim file, metrics line, journal entry, `NEXT.md`, pull request and merge, so a later cycle cut short loses nothing earlier.
2. **Each cycle counts as a run** for every per-run rule: the 20-entry cap, `per_run_cap_usd`, the claim cap, one `metrics.py` call, one log entry.
3. **After each cycle's merge**, `python3 tools/run_clock.py`. `next cycle: yes` → restart the branch from the merged `main` under the same name, take a fresh run id, and begin at section 1:
   ```bash
   BR="$(git rev-parse --abbrev-ref HEAD)"
   git fetch --prune origin && git checkout -B "$BR" origin/main
   rm -f .tmp/run-id && python3 tools/claim.py --id
   ```
   `next cycle: no`, or a cycle whose pull request did not merge (failed twice, or pending at the poll cap) → end the run (section 6, step 8). Never start a cycle on top of an unmerged one.
4. **Within a cycle**, `python3 tools/run_clock.py` between batches (every few entries, and before each paid call). Once it prints `wrap up now`, stop drafting wherever it stands, release unstarted claims (`queue.py set ... pending`, remove them from the claim file), and go to the pipeline with what you have.
5. **Budget ends the run early.** When the selector's `run_budget_usd` is 0 or a budget check is refused, do that cycle's unpaid work (section 5) and end the run: the day's budget resets at UTC midnight, and more unpaid cycles would only lint an unchanged dictionary.
6. **Sizes bound a cycle, not the context window.** Read "half of your context" in section 5 as the context this cycle has used. If the harness warns that context is running low, finish the current cycle and end the run.
7. **Start every cycle by re-reading** this section and the section for the mode the selector picks; in a long run the early conversation may have been summarized.

## 0. Pre-flight

1. `date -u`; `git fetch origin`; `python3 tools/claim.py --id` (your run id, kept in `.tmp/run-id`).
2. **Stranded work.** `mcp__github__list_pull_requests` (`owner: "tkgally"`, `repo: "eex-dict"`, `state: "open"`). For each open pull request whose head starts with `claude/`: `mcp__github__pull_request_read` with `method: "get_check_runs"`. Every run `completed` with conclusion `success`, `neutral`, or `skipped`, mergeable, no human comment → `mcp__github__merge_pull_request` (`merge_method: "squash"`), then `git fetch origin main && git merge origin/main --no-edit`. A failed conclusion → `python3 tools/absorb_branch.py <head-branch> --pr <number>`, then run the local gate (section 6, step 3) and fix what it reports; after your own pull request merges, comment "absorbed into pull request #<yours>" on the old one and close it (`mcp__github__update_pull_request`, `state: "closed"`). `ABORTED` from the tool → one line in `reviews/needs_curator.txt` naming the branch and files, leave the pull request open. Still pending → leave it; say so in the journal.
3. **Orphan branches.** `mcp__github__list_branches`; for each `claude/*` branch that is neither yours nor an open pull request's head: `python3 tools/absorb_branch.py --residue <branch>`; residue → absorb it as above (find its closed pull request with `mcp__github__list_pull_requests`, `state: "closed"`, `head: "tkgally:<branch>"`; if a person closed it, leave it and write one line to `reviews/needs_curator.txt` instead); no residue → append `<UTC> prune-branch <branch>` to `reviews/needs_curator.txt` unless a line naming it exists (this tool set cannot delete branches).
4. **Inbox.** Anything in `inbox/` outranks the queue: act on it or record the answer in `wiki/open-questions.md`, move it to `inbox/archive/`, note it in `wiki/log.md`. Then confirm your checkout contains `origin/main`'s latest commit.

## 1. Select the mode

```bash
python3 tools/next_mode.py
```

`mode` is this run's unit; `params` its limits (`max_new_entries`, `run_budget_usd`, `block_size`); `reason` and `signals` go in the journal. Do not second-guess the selector. A build or closure run whose `max_new_entries` is 0 cannot build (the draft ceiling or the budget): do the review unit instead if drafts exist, else lint, and say why in the journal. `run_budget_usd` is this run's ceiling for paid calls, below the day's cap in `config/budget.md`; every paid call goes through the tools, which check and record spend. A refused budget check means: finish the paid part you can afford, and do the rest of the unit unpaid.

## 2. The modes

**build** — new entries from the queue.
1. `python3 tools/claim.py --from-queue --n <params.max_new_entries>` (band 1 first by default; the tool skips slugs claimed on any branch). Commit nothing yet; the claim file is committed with the entries.
2. For each claimed slug, draft the entry from your own knowledge and the style guide (never from any published dictionary), at the path `python3 tools/entry_path.py <slugs>` prints; every field filled, `provenance.status: draft`, `provenance.drafted_by` the slug of the `drafter` role in `config/models.md`, `provenance.run_id` your run id. Ten to fifteen substantial entries are a better run than twenty thin ones. A word you decline to write: `python3 tools/queue.py set "<headword>" <pos> declined --note "<reason>"`, one line in `reviews/needs_curator.txt`, remove it from the claim file, move on; never argue with or retry a refusal in the same run.
3. Run the pipeline (section 3) on the batch. Then `python3 tools/lint_vocab.py --queue <files>` to queue closure candidates, and `python3 tools/queue.py sync`.

**review** — a second reading of existing entries: all `draft` entries first, then `reviewed` entries that have had only one panel round (`params.block_size` at most), those flagged `markup-pending` before the rest. Run `tools/review_panel.py` on the block, adjudicate (section 4), fix, `tools/validate.py`, `tools/lint_vocab.py`, `tools/crossref.py`; set `reviewed` on drafts whose blocking issues are settled. While an entry flagged `markup-pending` is open, add the inline marks of style guide section 6 to its prose by hand, field by field (never by a script or a pattern), and remove the flag.

**closure** — the same as build, from the words the dictionary already uses: `python3 tools/claim.py --from-queue --n <params.max_new_entries> --source closure` (then `--source family`, `--source crossref` if fewer remain).

**site** — `python3 tools/build_site.py` (writes `docs/`, gitignored); then `python3 tools/site_check.py` (Playwright at phone width: the home page, three entry pages, a search for an inflected form such as `ran` finding `run`, a preview opening on a linked word). Fix what is broken in `tools/build_site.py` or its templates, rebuild, recheck. Never commit `docs/`. Record `--site-build ok|failed` in the metrics call.

**lint** — the judgmental pass of `framework.md` section 6 plus the mechanical checks over everything: `python3 tools/check_caps.py`, `python3 tools/check_links.py`, `python3 tools/crossref.py --all --apply`, `python3 tools/lint_vocab.py --all --queue`, `python3 tools/claim.py --prune`, `python3 tools/metrics.py --precision` (note reviewer precision by family in `wiki/notes/reviewer-precision.md`; a family under 30 percent for a role over twenty or more decisions is turned off for that role in `tools/review_panel.py` with a logged decision); read `wiki/index.md` against the pages, `wiki/log.md` for gaps, `wiki/open-questions.md` for stale entries, `reviews/needs_curator.txt` for duplicates; fix contradictions between pages; put the next lint's due run in `NEXT.md`.

**originality** — `python3 tools/originality_check.py sample --n 10`; run the exact-phrase web searches the checklist lists (WebSearch), ask one reviewer role the question it gives, fill in the verdicts, `python3 tools/originality_check.py record <date> --file .tmp/originality-<date>.md`. A `rewrite` verdict is rewritten in this run (it is a review of that entry: panel, adjudication, validate).

Any mode: an observed problem with a tool or a rule goes to `wiki/notes/` first; the fix comes in a later run with a logged reason, unless the tool blocks this unit, in which case repairing it is part of the unit (about a fifth of the run at most).

## 3. The pipeline for every new or rewritten entry

In this order, on the batch:

```bash
python3 tools/validate.py <files>                 # 0 errors before anything else
python3 tools/inflect.py <slugs>                  # forms from rules and the exceptions table; read the notes it prints
python3 tools/pronounce_check.py <slugs>          # panel plus CMU consultation; disputed transcriptions get a flag
python3 tools/review_panel.py <slugs>             # both reviewers, every field, closed verdicts
# adjudicate (section 4), fix the entries
python3 tools/validate.py <files>
python3 tools/lint_vocab.py <files>               # definition words outside the vocabulary with no entry
python3 tools/crossref.py <slugs> --apply --queue # back-links; missing targets queued
python3 tools/queue.py stamp <slugs>              # band and defining-vocabulary flag from the queue
```

An entry becomes `reviewed` only when: validate reports 0 errors; inflections and both transcriptions are `verified` or carry the matching flag in `provenance.flags`; both reviewer records are in `provenance.reviews`; every blocking issue has a decision line. Set `provenance.status` by hand; `validate.py --gate` refuses a `reviewed` entry that does not qualify.

## 4. Adjudication

`python3 tools/review_panel.py --report <slug>` lists the issues. Read every **blocking** issue yourself against the entry and your own knowledge. Decide, and log each decision:

```bash
python3 tools/review_panel.py --decide <slug> --field <field> --role <role> --decision apply|reject|escalate --note "<at most fifteen words>"
```

- `apply` when the reviewer is right: fix the field yourself (never paste a reviewer's wording), update `provenance.modified`.
- `reject` when the reviewer is wrong, with the reason in the note. Never reject for convenience.
- `escalate` when two reviewers disagree on a fact, or you cannot decide: settle it with open data if any bears on it (a pronunciation against the CMU vote; an inflection against the rules); otherwise add the matching `provenance.flags` value and one line to `reviews/needs_curator.txt` with your working assumption.

Minor issues: fix the clear ones while the entry is open; log them with the same command. Both reviewers flagging the same field is a strong signal; one reviewer flagging a plain, short definition as "too simple" is noise to reject. More than a third of fields flagged on an entry means reviewer noise: log a `[tooling]` observation in `wiki/notes/reviewer-noise.md` with examples.

## 5. Guards

- A run never ends having done nothing. If the unit is blocked, write why in `NEXT.md` and do the next unblocked unit; a build run with no budget does the unpaid half (drafting and validating, left as `draft` for the next review run) or switches to lint.
- Fewer, better entries. The cap is a ceiling. Reading and drafting is the expensive part: finish the content work by about half of your context; the pipeline, adjudication, and wrap-up need the rest. Running out mid-merge is the one failure that costs the whole run.
- No script may write a semantic field (`CLAUDE.md`, ownership table). No new machinery on speculation.
- Consult the wiki through `wiki/index.md`; read only the pages the unit needs.
- Never print the API key; never commit `docs/`, `.tmp/`, or any downloaded file.

## 6. Wrap up

1. `python3 tools/metrics.py --mode <mode> --changed <entries created or changed> [--site-build ok|failed]`.
2. `wiki/index.md` for any page added or changed; one `wiki/log.md` entry (header `## [YYYY-MM-DD] <mode> | <title>`, at most 200 words: what changed, adjudication counts, spend, anything a later run must know).
3. The local gate, and fix what it reports: `python3 tools/validate.py --gate && python3 tools/check_caps.py && python3 tools/check_links.py && python3 -m unittest discover -s tools/tests -t . && python3 tools/lint_vocab.py --gate --changed && python3 tools/crossref.py --gate`.
4. Rewrite `NEXT.md` from scratch (State, Queue, Fences, For the owner; sixty lines).
5. The journal entry `journal/YYYY-MM-DD.md` (suffix `-2`, `-3` for later runs the same day), written to the contract in `framework.md` section 4 (no skill or template is needed): plain, self-contained English for the owner, every internal term glossed, 300 to 800 words: what the run did, what the reviewers found and what you decided, spend, what did not work, what is next, what needs the owner.
6. `git add -A && git commit -m "<mode>: <imperative summary>"` and `git push -u --force-with-lease origin "$(git rev-parse --abbrev-ref HEAD)"` (retry 2, 4, 8, 16 seconds on network failure; `--force-with-lease` matters from cycle 2 on, when the restarted branch replaces commits already squash-merged into `main`). This is the cycle's last push unless CI fails.
7. The atomic tail from `CLAUDE.md`: create the pull request (title `<mode>: …`, body the journal entry's substance), poll `get_check_runs` with `python3 tools/wait.py 60` between polls (at most 15), squash-merge when green, confirm `main` advanced; on a failure read the log, fix, run the gate, push once, poll again; a second failure stays open and is reported in `NEXT.md`.
8. Merged → back to **Run shape** step 3. At the end of the run, the final message is a plain-English summary of every cycle: one short paragraph each (mode, what changed, the pull request link, spend), then anything that needs the owner.

## Quick reference

```bash
python3 tools/run_clock.py start | (no argument: elapsed, next cycle, wrap up now)
python3 tools/claim.py --id | --taken | --from-queue --n N [--source S] | --prune
python3 tools/next_mode.py [--explain]
python3 tools/queue.py list|add|set|next|sync|stamp|counts
python3 tools/entry_path.py <slug> | --slug "<headword>" <pos> | --sub-id "<phrase>"
python3 tools/validate.py <files> | --gate | --fix-format
python3 tools/inflect.py <slugs> | --word W --pos P | --confirm <slugs>
python3 tools/pronounce_check.py <slugs> [--no-cmu]
python3 tools/review_panel.py <slugs> | --report <slug> | --decide <slug> --field F --role R --decision D --note "..."
python3 tools/lint_vocab.py <files> | --changed --gate | --all --queue
python3 tools/crossref.py <slugs> --apply --queue | --gate
python3 tools/build_site.py ; python3 tools/site_check.py
python3 tools/originality_check.py sample | record
python3 tools/absorb_branch.py <branch> [--pr N] | --residue <branch>
python3 tools/metrics.py --mode M --changed N ; python3 tools/spend.py status ; python3 tools/wait.py 60
```
