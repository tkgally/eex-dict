# The knowledge-base framework for this project

*How this project remembers, decides, verifies, and reports. This document is the framework the project runs on: a session follows it, and the project's own materials grow out of it. It is owner-supplied and stable — a session does not edit it; if the project's experience calls for changing something structural, the change is made in the project's own files with a logged reason, and this document stays as the reference point.*

## 0. The idea in one paragraph

The project's memory is a **persistent, incrementally built wiki**: a structured, interlinked collection of markdown files that the project's sessions write and maintain. Knowledge is compiled once and kept current, not re-derived from raw sources on every question — cross-references are already there, contradictions have already been flagged, and the synthesis already reflects everything read so far, so the wiki gets richer with every source ingested and every question answered. Because this project runs **unattended** — separately scheduled sessions, different models, no conversation history carried between them, an owner who reads reports rather than following the work — the wiki alone is not enough. Five structural components (§2–§6) carry state across sessions, keep a fresh session productive from a cold start, keep the owner informed, and keep the whole thing verifiable. Together they are deliberately minimal: add machinery beyond them only when a real, observed problem calls for it (§8).

## 1. The wiki

**Three layers.**

- **Raw sources** (`sources/` or a similar directory): the collected source material — saved articles, extracts, data files, notes on works consulted. Immutable once filed: sessions read from this layer but never modify it. Where a source is a live web page, the filed copy or extract (with title, URL, and access date) is the project's stable record of what was actually read.
- **The wiki** (`wiki/`): the project-written layer. Summaries, entity pages, concept pages, comparisons, syntheses, case files — whatever page types the subject calls for. Sessions own this layer entirely: create pages, update them when new information arrives, maintain cross-references, keep everything consistent.
- **The schema**: the conventions that make sessions disciplined maintainers rather than improvisers — page types, naming, linking style, provenance rules. Keep the schema written down (a `wiki/conventions.md` page works well) and evolve it deliberately, with a logged reason for each change, not by drift.

**Three operations.**

- **Ingest**: research comes in — a source is read, its key content is extracted and integrated: a source page filed, entity and concept pages updated, contradictions with existing pages noted explicitly, the index and log updated. A single source may properly touch many pages; that integration work is the point, not overhead.
- **Query**: questions are answered *from the wiki*, and **answers that took real work are filed back into the wiki as pages**. An analysis, a comparison, a connection discovered — these must not evaporate when the session ends; filing them is how exploration compounds.
- **Lint**: periodic health checks, mechanical (§6) and judgmental (§6), so growth does not rot into contradictions and stale claims.

**Two navigation files.**

- **`wiki/index.md`** — content-oriented: a catalog of every wiki page, each with a link and a one-line summary, organized by category. Updated in the same session as any page it lists. A session answering a question reads the index first, then drills into the specific pages it needs — never the whole wiki.
- **`wiki/log.md`** — chronological and append-only: one entry per session, newest first, each starting with a consistent header (`## [YYYY-MM-DD] <operation> | <title>`) so the log stays parseable with simple tools. The log is the project's timeline; the index is its map.

**Provenance is not optional.** Every factual claim on a wiki page cites its source (a source page, or an external reference with title, URL, and access date), or is explicitly labeled as the project's own inference or speculation. Under-claim when in doubt; record disagreements between sources rather than silently resolving them; write up negative findings with the same care as positive ones.

## 2. The baton — `NEXT.md`

One file at the project root carries working state between sessions. It is **rewritten from scratch at the end of every session — never appended to** — and hard-capped at **60 lines** (adjust the cap only by a logged decision; never leave it uncapped). It contains:

- **State**: a few lines on what is true right now, matching the repository as it actually is, not the plan. Detail lives in wiki pages; the baton is a cache over them, not a second record of truth.
- **Queue**: the next unblocked units of work, most important first.
- **Fences**: things already tried, already decided, or already ruled out — so a fresh session does not silently redo settled work. Often the most valuable section in the file; keep it current.
- **For the owner**: any open question awaiting the owner (with the working assumption being used meanwhile — see §5), or an explicit "nothing needs your input."

The discipline matters more than the format: rewrite (so stale lines die), cap (so it stays readable in one glance), and never let the baton carry facts the wiki doesn't — a baton lost to a bad session must cost bookkeeping, not knowledge.

## 3. The entry protocol — `resume-prompt.md`

One **stable** file tells any fresh session how to start; state lives in the baton, never here. It specifies, in order:

1. **Ground yourself**: check the date; check for a stranded pull request from this project's previous session (one may have stopped between push and merge — finish that first); fetch the main branch and confirm the working checkout contains its latest commit before trusting anything on disk.
2. **Read, in this order**: the schema and rules files; `NEXT.md`; `wiki/index.md`; the owner channel (§5); and then *only* the specific pages the chosen unit of work needs. Never load the whole wiki to start.
3. **Pick one unit**: take one coherent, completable unit of work from the queue, top-down. If the top unit is blocked, write down why and take the next unblocked one. **A session never ends having done nothing** — if a tool or file this framework names does not exist yet, building it *is* the unit.
4. **Wrap up, every session, no exceptions**: update `wiki/index.md` and `wiki/log.md`; rewrite `NEXT.md`; write the owner report (§4); run the integrity check (§6); then commit, push, and merge per the repository's session mechanics, confirming the merge actually landed.

## 4. The owner report — `journal/`

One dated, plain-language report to the owner per session, filed in `journal/` as `YYYY-MM-DD.md` (add a suffix if a day has several sessions). The report is a **translation of the session for its reader, not a transcript**. The style contract:

- **Self-contained.** Assume the reader has read nothing recent — not the wiki, not the queue, not the previous report — and reads this once, quickly, without opening other files.
- Every internal term, code, or id is reworded or glossed at first use in the same sentence. A reference to an earlier decision or idea gets a same-sentence reminder of what it was; a bare handle from a previous report does not stand on its own.
- Calendar dates, not session counts, for time.
- It states: what the session did; what it found, **including nulls, failures, and anything that went wrong**; what that means for the project's goal; what happens next; and explicitly what — if anything — needs the owner's decision.
- Never state a finding more strongly in the report than the wiki states it.
- Length: roughly 300–800 words; completeness and self-containment come first.

## 5. The owner channel — `inbox/`

A directory the owner can drop instructions, corrections, or notes into at any time. **Check it at the very start of every session**; anything there is unprocessed input from the owner and **outranks the queued work**. Process each item (act on it, or record the answer it gives), then move it to `inbox/archive/` and note the processing in the log.

Paired with the **record-assumption-and-proceed rule**: sessions run unattended, so an answer from the owner cannot arrive mid-session. A session never blocks on a question to the owner — it records the open question *and a stated working assumption* in a durable page (a `wiki/open-questions.md` page works well, with the question also surfaced in the baton's for-owner block), then proceeds on the assumption. When the owner's answer eventually arrives, the page records it and notes every file updated as a result.

## 6. The integrity check

- **Mechanical, before every commit**: run `tools/check_links.py` — every relative link inside the knowledge base must resolve; fix anything broken before committing. Zero broken links is the standing bar, not an aspiration. (Known limit of the tool, to compensate for by hand: it does not validate the `#section` fragment of a link, only that the target file exists.)
- **Judgmental, on a schedule**: roughly every five sessions, spend part of a session on a lint pass covering what a script cannot see — contradictions between pages, claims a later page superseded but never corrected, missing cross-links, orphaned or index-missing pages, and drift in the project's own tools and conventions documentation. **Put the next pass's due date in the baton's queue** — a periodic rule with no explicit trigger that a session actually checks is a rule that silently stops running.
- The index and log are part of integrity: `wiki/index.md` lists every page, and `wiki/log.md` has an entry for every session, before any session ends.

## 7. Starter kit and first-session bootstrap

Shipped alongside this document:

- `templates/NEXT.md` — a blank baton in the shape §2 describes.
- `templates/resume-prompt.md` — a blank entry protocol in the shape §3 describes, with the project-specific blanks marked.
- `tools/check_links.py` — the mechanical link checker from §6 (Python standard library only; defaults to checking `wiki/`).

If the project's knowledge base does not exist yet, the current session is the first session, and its unit of work is the bootstrap: (1) instantiate `NEXT.md` and `resume-prompt.md` from the templates at the project root, filling in the blanks and deleting the template comments; (2) create `wiki/` with a starting `index.md` and `log.md`, a `sources/` directory, `journal/`, and `inbox/` (with an empty `archive/` inside); (3) record the schema conventions being adopted; (4) confirm `tools/check_links.py` runs clean; and then (5) **begin real content work in the same session** — the scaffold is not a session's product, the subject matter is.

## 8. Growing beyond this framework

Do not add machinery on speculation. The five components above are deliberately minimal; the framework earns its keep by staying a small fraction of session effort, and every session's principal unit should move the project's actual subject forward — process work rides along, it is never the main event unless something is concretely broken. Add structure beyond this framework only when the project *observes* a real, repeated problem — an index that has stopped being trustworthy, a genuine staleness incident that propagated, reports the owner cannot follow — and then: write down the problem first, change one thing with a logged reason, and check later whether the change actually helped. The owner's explicit instructions override anything here; honesty about what the project actually knows and how well it is actually working overrides everything.
