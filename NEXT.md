# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-third scheduled Routine run (build mode).*

## State

- 298 entries, all `reviewed` (0 `draft`). Queue: 4,092 pending, 32 claimed, 298 done, 9 declined, 4 duplicate.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Claimed 20 band-1 verbs; released 8 (*become, begin, believe, belong, bend, bite, bleed, blow*) back to `pending`, favoring fewer, better entries per the style guide. Drafted and fully reviewed 12: *answer, appeal, appear, apply, argue, arrest, arrive, ask, assume, attack, bake, beat*.
- Panel: 71 issues, 48 blocking, 63 applied, 8 rejected, 1 escalated. Rejected several confident-but-wrong reviewer claims (checked against schema/vocabularies.json and plain grammar) — see `wiki/log.md` for specifics.
- Escalated: whether *beat* as a past participle is "informal" (reviewer-a disputes the pre-existing `schema/inflection-exceptions.json` note) — logged to `reviews/needs_curator.txt`, entry flagged `inflection-disputed`.
- Fixed 11 defining-vocabulary violations by rewording (no entries added for out-of-vocabulary words this run).
- Spend: US$0.42 this run (under the $1.25 run budget), US$0.90 today of the $5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: continue band 1 verbs from *become* onward (`queue.py next` order; the 8 released words are first). The 11 band-1 conjunctions are still stuck at queue status `claimed` with no backing claim file ([queue-stale-claimed-rows](wiki/notes/queue-stale-claimed-rows.md)); `queue.py next` skips them automatically — work around by hand only if they need to jump the line.
2. **lint**: `runs_since_lint` is now 5 (was 4); lint is forced at the next scheduled run per `lint_every_runs`. Prior debt: lint debt was deeply negative (-4.05 at run 40); check `next_mode.py --explain` at the next run.
3. **review**: 220 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
4. **closure**: cross-reference/family targets with no entry now at 848 (crossref --gate), still growing; this run added 16 (mostly word-family members of the new verbs: *answer-n, appeal-n, question-n*, etc.).
5. Six pre-existing `link override target has no entry` warnings (*alone-adj, favorite-adj, that-pron, very-adv, whatever-det*, one `time-n` example-marking warning) are unchanged and harmless.
6. Next originality run due at run 50 (every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. A reviewer flagging this as wrong is itself wrong — check the house convention before applying such a fix (caught this run on *beat*: American `bit` is correct).
- The house core-idea form "To **X** is to..." is standard for verbs with 3+ senses (see *add-v, borrow-v, explain-v, take-v*); a reviewer calling this a style fault is noise — reject with the precedent cited.
- "usually passive" and "not used in continuous tenses" are valid `verb_patterns` values, not `grammar_codes`; check `schema/vocabularies.json` before rejecting a reviewer's code placement, but also before accepting a reviewer's claim that a value is invalid.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. The first sense of a defining-vocabulary word's own entry is exempt (warning only); `core_idea` and phrase/subsense definitions are never exempt.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field; the quote must match the review file's stored text exactly, not a paraphrase.
- Never mutate a list while iterating over it when patching entry JSON by script.
- A contraction or short form listed in `variants[]` (kind `form`) is auto-marked by the site in examples; it does not need a hand `**mark**`.
- An originality-check "copied" verdict from reviewer-a needs its cited source checked against the actual text — see [reviewer-noise](wiki/notes/reviewer-noise.md).
- After drafting, run `python3 tools/queue.py sync` before wrap-up so the queue's `done` count matches reality — easy to forget since it is not part of the pipeline in `CLAUDE.md` section on the pipeline itself, only in the build-mode instructions.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eleven open items (one new this run: *beat* past-participle register).
