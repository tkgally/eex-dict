# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the seventh scheduled lint pass.*

## State

- 298 entries, all `reviewed` (0 `draft`). Queue: 4,092 pending, 32 claimed, 298 done, 9 declined, 4 duplicate.
- Lint mode (selector: forced, 5 runs since the last lint). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Mechanical checks all clean: caps, links, 305 unit tests, `crossref --all --apply` (0 errors, 848 missing closure targets, unchanged trend), `lint_vocab --all --queue` (0 violations). `claim.py --prune` removed 3 stale claim files.
- `metrics.py --precision`: no new switch-offs; the five disabled (role, family) pairs unchanged. `reviewer-b`'s overall precision (0.69) has now caught up to and edged past `reviewer-a`'s (0.68) for the first time — see updated open question 2 and [reviewer-precision](wiki/notes/reviewer-precision.md).
- New tooling gap logged, not fixed: `lint_vocab.py --all --queue` accumulates overlapping duplicate note text on a queue row across repeat lint passes ([note](wiki/notes/lint-vocab-queue-note-duplication.md)).
- Spend: US$0 this run; US$0.90 today of the US$5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: continue band 1 verbs from *become* onward (`queue.py next` order; released words first). The 11 band-1 conjunctions are still stuck at queue status `claimed` with no backing claim file ([queue-stale-claimed-rows](wiki/notes/queue-stale-claimed-rows.md)); `queue.py next` skips them automatically — work around by hand only if they need to jump the line.
2. **lint**: next pass forced in 5 scheduled runs; check `next_mode.py --explain` (note: `runs_total`/`runs_since_lint` run about one-sixth high, see [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md) — call `metrics.py` once per run only).
3. **review**: 220 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
4. **closure**: cross-reference/family targets with no entry now at 848 (crossref --gate), still growing; unchanged this run (lint made no content edits beyond auto-applied symmetric back-links on 4 entries).
5. Six pre-existing `link override target has no entry` warnings (*alone-adj, favorite-adj, that-pron, very-adv, whatever-det*, one `time-n` example-marking warning) are unchanged and harmless.
6. Next originality run due at run 50 (every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. A reviewer flagging this as wrong is itself wrong — check the house convention before applying such a fix.
- The house core-idea form "To **X** is to..." is standard for verbs with 3+ senses; a reviewer calling this a style fault is noise — reject with the precedent cited.
- "usually passive" and "not used in continuous tenses" are valid `verb_patterns` values, not `grammar_codes`; check `schema/vocabularies.json` before rejecting or accepting a reviewer's claim about a code's placement or validity.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. A defining-vocabulary word's own first sense is exempt (warning only); `core_idea` and phrase/subsense definitions are never exempt.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field; the quote must match the review file's stored text exactly.
- Never mutate a list while iterating over it when patching entry JSON by script.
- A contraction or short form listed in `variants[]` (kind `form`) is auto-marked by the site in examples; no hand `**mark**` needed.
- Run `python3 tools/queue.py sync` after drafting, before wrap-up, in build mode — easy to forget, not part of the pipeline proper.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks). Open question 2 (reviewer-b's tier) now has fresh data suggesting no upgrade is needed.
- `reviews/needs_curator.txt` has eleven open items, unchanged this run.
