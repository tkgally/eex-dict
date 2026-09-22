# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-first scheduled Routine run (originality mode).*

## State

- 286 entries, all `reviewed` (0 `draft`). Queue: 4,081 pending, 32 claimed, 286 done, 9 declined, 4 duplicate. Unchanged this run.
- Originality mode (selector: forced, run 40 is a multiple of 10). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Sampled 10 definitions, ran an exact-phrase web search on each, put the standard question to reviewer-a in one combined call ($0.0052). No page anywhere matched any of the 10 texts verbatim. Reviewer-a said "copied" for 7/10, citing Cambridge Dictionary each time, but every citation failed on inspection (two were the reviewer echoing our own text back; five named a real Cambridge entry with different actual wording). Verdict: 4 original, 6 generic-overlap, 0 rewrite. Recorded to `reviews/originality/2026-09-22.md`; nothing rewritten.
- New note logged: [reviewer-noise](wiki/notes/reviewer-noise.md) third entry — reviewer-a's "copied" calls have taken three different shapes (blanket, unsupported-mixed, now confident-but-mismatched-citation) across three forced runs; not yet enough to change the tooling.
- The public site is confirmed **live**: <https://tkgally.github.io/eex-dict/>. `README.md`'s Site section now names the URL; the "enable GitHub Pages" owner item is closed.
- Spend: US$0.0052 this run (well under the $0.1 run budget), US$0.4760 today of the $5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: resume band 1. Per the 2026-09-22 build run: eleven band-1 conjunctions (*although, as, but, if, nor, once, or, since, so, though, unless*) are stuck at queue status `claimed` with no backing claim file ([queue-stale-claimed-rows](wiki/notes/queue-stale-claimed-rows.md)); work around by hand (`queue.py set "<word>" conj pending --note "..."`) before drafting them. Otherwise move to nouns/verbs/adjectives per `queue.py next` order.
2. **review**: 220 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
3. `runs_since_lint` is now 4 (lint debt still deeply negative, was -4.05); the duplicate-row metrics-call inflation from [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md) still applies, not yet fixed — this run called `metrics.py` exactly once, per the rule.
4. **closure**: 472 cross-reference/family targets with no entry, still growing (1,003 missing-target warnings as of the last lint pass, mostly repeats of the same targets).
5. Six pre-existing `link override target has no entry` warnings (*alone-adj, favorite-adj, that-pron, very-adv, whatever-det*, one `time-n` example-marking warning) are unchanged and harmless.
6. Next originality run due at run 50 (every 10th).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. The first sense of a defining-vocabulary word's own entry is exempt from the check (warning only); `core_idea` and phrase/subsense definitions are never exempt — check those fields too, not only `senses[].definition`.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field.
- Never mutate a list while iterating over it when patching entry JSON by script.
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid; `polite` is a valid register value, not a reviewer-b false positive.
- A contraction or short form listed in `variants[]` (kind `form`) is auto-marked by the site in examples; it does not need a hand `**mark**`.
- An originality-check "copied" verdict from reviewer-a needs its cited source checked against the actual text, not taken on trust — see [reviewer-noise](wiki/notes/reviewer-noise.md).

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, unchanged this run.
