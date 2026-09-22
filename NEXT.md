# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-second scheduled Routine run (build mode).*

## State

- 286 entries, all `reviewed` (0 `draft`). Queue: 4,081 pending, 32 claimed, 286 done, 9 declined, 4 duplicate.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Claimed and built the 13 entries the top of the queue offered: conjunctions *when, where, whether, while, yet* and modals *could, may, might, ought, shall, should, will, would* — completing both closed categories.
- Inflections: all `source: none` (expected for conj/modal). Pronunciation: 26/26 transcriptions verified by full panel agreement.
- Panel: 72 issues, 40 blocking, 64 applied, 5 rejected (precision reviewer-a 0.929, reviewer-b 0.926) — see `wiki/log.md` for the recurring patterns (softened absolute grammar claims, an overclaimed "formal" register, etymology-in-usage-note).
- Fixed 12 defining-vocabulary violations in definitions by rewording; 11 closure/crossref targets queued.
- Mechanical checks: `validate.py --gate` (0 errors, 6 pre-existing warnings, unchanged), caps, links, 305 unit tests, `lint_vocab.py --gate --changed` (0 violations), `crossref.py --gate` (0 errors, 1003 warnings — closure gap, growing as expected).
- New finding logged, not yet fixed: [queue-stale-claimed-rows](wiki/notes/queue-stale-claimed-rows.md) — eleven band-1 conjunctions (*although, as, but, if, nor, once, or, since, so, though, unless*) are stuck at queue status `claimed` with no backing claim file, so `queue.py next` permanently skips them. Work around by hand (`queue.py set "<word>" conj pending --note "..."`) until a tool fix lands.
- Spend: US$0.47 this run, well under the $1.25 run budget and $5 daily cap.

## Queue (work top-down, one unit at a time)

1. **originality**: the selector reports run 40 is a forced multiple of 10 — likely due next scheduled run (subject to the known duplicate-metrics-call miscount, see item 4).
2. **build**: after originality, resume band 1. The eleven stale-claimed conjunctions above are high-value defining-vocabulary words but need the queue-status workaround first; otherwise move to nouns/verbs/adjectives per `queue.py next` order (suffixes/affixes are next after conj/modal exhaust, so prefer hand-picking content words over them for now).
3. **review**: 220 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
4. `runs_since_lint` is now 3 (lint debt still deeply negative, -4.05); the duplicate-row metrics-call inflation from [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md) still applies, not yet fixed — this run called `metrics.py` exactly once, per the rule.
5. **closure**: 472 cross-reference/family targets with no entry, still growing (1,003 missing-target warnings, mostly repeats of the same targets).
6. Six pre-existing `link override target has no entry` warnings (*alone-adj, favorite-adj, that-pron, very-adv, whatever-det*, one `time-n` example-marking warning) are unchanged and harmless.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. The first sense of a defining-vocabulary word's own entry is exempt from the check (warning only); `core_idea` and phrase/subsense definitions are never exempt — check those fields too, not only `senses[].definition`.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field.
- Never mutate a list while iterating over it when patching entry JSON by script.
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid; `polite` is a valid register value, not a reviewer-b false positive.
- A contraction or short form listed in `variants[]` (kind `form`) is auto-marked by the site in examples; it does not need a hand `**mark**`.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, unchanged this run.
