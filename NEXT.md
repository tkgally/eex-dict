# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-fourth scheduled build run.*

## State

- 310 entries, all `reviewed` (0 `draft`). Queue: 4,109 pending, 32 claimed, 310 done, 9 declined, 4 duplicate.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Claimed 20 band-1 verbs; released 8 (*breed, bring, brush, build, burn, bury, buy, calculate*) to `pending`, favoring fewer, better entries. Drafted *become, begin, believe, belong, bend, bite, bleed, blow, board, boil, break, breathe*.
- Pipeline: inflections 12/12 verified, pronunciation 24/24 verified. Panel: 99 decisions (91 applied, 8 rejected, 0 escalated) across 56 blocking issues; *break-v* needed a second reviewer-b pass (first reply parsed with zero verdicts, matching the known review-panel-parse-failures pattern — this instance resolved cleanly, no new tooling gap).
- Mechanical checks all clean: caps, links, 305 unit tests, `lint_vocab` (0 violations), `crossref` (0 errors, 2 back-links auto-applied, 56 new missing targets queued from this batch).
- New tooling observation logged in [queue-stale-claimed-rows](wiki/notes/queue-stale-claimed-rows.md): the prior run's "claim more than you draft, release the rest" step left the 8 released words at queue status `claimed` instead of `pending` (harmless this time — `claim.py --from-queue` doesn't gate on that column — but a latent trap). Fix suggested: spell out `queue.py set ... pending` in routine-prompt.md's build-mode guard text.
- Spend: US$0.51 this run of the US$1.25 run budget; US$1.40 today of the US$5 daily cap.

## Queue (work top-down, one unit at a time)

1. **review**: next mode selected (highest debt, 2.60). 244 `reviewed` entries remain at only one panel round; take the block by `params.block_size` (20).
2. **build**: continue band 1 verbs from *breed* onward (`queue.py next` order; released words first).
3. **closure**: `crossref --gate` (full repo) reports 898 missing cross-reference/family targets, up from 848 at last lint; `metrics.py`'s own `closure_gap` figure (524) is a different, narrower count — still growing either way.
4. **lint**: due when `runs_since_lint` next crosses the forced threshold; check `next_mode.py --explain`.
5. Six pre-existing `link override target has no entry` warnings (*alone-adj, favorite-adj, that-pron, very-adv, whatever-det*, one `time-n` example-marking warning) are unchanged and harmless.
6. Next originality run due at run 50 (every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. A reviewer flagging this as wrong is itself wrong — check the house convention before applying such a fix. Confirmed again this run on *bleed-v*.
- A subsense/sense definition with a subject restriction uses a parenthetical prefix, `(of a liquid) ...`, never a colon, `of a liquid: ...` — both reviewers flag the colon form; fix it on sight in review mode wherever it still appears.
- `schema/vocabularies.json`'s domain value is `theatre` (not `theater`) even in American-primary entries; it is the exact closed-vocabulary string, not a spelling choice.
- "usually passive" and "not used in continuous tenses" are valid `verb_patterns` values, not `grammar_codes`; "not gradable" is for adjectives/adverbs only, never a verb. Check `schema/vocabularies.json` before accepting or rejecting a reviewer's claim about a code's placement.
- Never mutate a list while iterating over it when patching entry JSON by script.
- Run `python3 tools/queue.py sync` after drafting, before wrap-up, in build mode — easy to forget, not part of the pipeline proper. When releasing part of a claimed batch, use `queue.py set ... pending`, never `claimed`.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has twelve open items (one new: whether the queued `belong-to-phrv` row is a misclassification, since ordinary `belong to` is already covered by `belong-v`).
