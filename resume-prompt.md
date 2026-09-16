# resume-prompt.md — session entry point

You are starting a session of the **TKG English Learner's Dictionary**, an original English-English learner's dictionary written by language models, one JSON file per entry, published as a static site. You have no memory of previous sessions: **the repository is the memory**. This file stays stable; current state lives in `NEXT.md`.

## 0. Ground yourself

- `date -u`. Dates in this project are ISO, UTC.
- `git fetch origin`. Check for stranded work: an open pull request against `main` with a `claude/*` head means a predecessor stopped between push and merge. Merge it if green, absorb it if red, note it if pending (`CLAUDE.md`, "Session mechanics"). Sweep orphan `claude/*` branches the same way.
- Confirm your checkout contains `origin/main`'s latest commit before trusting anything on disk.
- Note your run id: `python3 tools/claim.py --id` prints it and writes `.tmp/run-id`.

## 1. Read, in this order

1. `CLAUDE.md` — the rules (short; every session).
2. `NEXT.md` — state, queue, fences, and what awaits the owner.
3. `wiki/index.md` — the catalog, one line per page.
4. `inbox/` — anything there is unprocessed input from the owner and **outranks the queue**. Act on it or record the answer it gives, move it to `inbox/archive/`, note it in `wiki/log.md`.
5. Only then the pages the chosen unit needs: `wiki/style-guide.md` and `wiki/conventions.md` before touching an entry; a decision page before citing a rule. Never load the whole wiki.

## 2. Work one unit

A scheduled run follows `routine-prompt.md`, whose selector picks the mode. An interactive session takes its assignment from the person who started it, or the top unblocked unit of `NEXT.md`'s queue. If the top unit is blocked, write down why and take the next. **A session never ends having done nothing**: if a tool or file the rules name does not exist, building it is the unit.

Questions for the owner cannot be answered mid-session. Record the question and a working assumption in `wiki/open-questions.md`, surface it in `NEXT.md`, and proceed on the assumption.

## 3. Wrap up, every session, no exceptions

1. Run the pipeline's closing checks: `python3 tools/validate.py --gate`, `python3 tools/check_caps.py`, `python3 tools/check_links.py`, `python3 -m unittest discover -s tools/tests -t .`, `python3 tools/metrics.py`.
2. Update `wiki/index.md` and `wiki/log.md` for anything added or changed (log header `## [YYYY-MM-DD] <operation> | <title>`, at most 200 words).
3. Rewrite `NEXT.md` from scratch: State, Queue (with the next lint pass's due date), Fences, For the owner. Sixty lines at most.
4. Write the owner report `journal/YYYY-MM-DD.md` (add `-2` if the day has one): plain, self-contained English, every internal term glossed at first use, dates not session counts, 300 to 800 words: what was done, what was found including failures, what it means, what is next, what needs the owner.
5. Commit, push, open a pull request, poll its checks, squash-merge, confirm `main` advanced — the exact procedure is in `CLAUDE.md`. If the merge cannot land, say so at the top of `NEXT.md` before stopping.
6. Kill background processes. Leave a clean tree.
