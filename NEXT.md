# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-first scheduled Routine run (site mode).*

## State

- 273 entries, all `reviewed` (0 `draft`). Queue: 4,093 pending, 273 done, 32 claimed, 9 declined, 4 duplicate. No content changed this run.
- Site mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit (build #34 had just merged).
- `build_site.py`: 273 entries, 247 headword pages, 0 drafts withheld, 0 redirects, 568 files, no errors.
- `site_check.py`: 54 of 54 checks passed at phone (360x780) and desktop (1280x900) widths plus dark mode — no JS errors, no horizontal overflow, viewport meta and disclosure everywhere sampled, inflected-form search (*ran* → *run*), hover/tap preview, translator's-view toggle persisting through reload. Nothing needed fixing in the templates or entries.
- Mechanical checks: `validate.py --gate` (0 errors, 6 pre-existing warnings), caps, links, 305 unit tests, `lint_vocab.py --gate --changed` (nothing to check, no entries changed), `crossref.py --gate` (0 errors, 988 warnings — all missing closure targets, unchanged).
- `docs/` not committed, as required.
- Spend: US$0 this run.

## Queue (work top-down, one unit at a time)

1. **build**: keep diversifying band 1; avoid claiming the whole remaining preposition set in one grab (*on, over, up, to, under, through* are all still heavy and unbuilt) — mix in a handful at a time with nouns/verbs/adjectives.
2. **review**: 207 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
3. **closure**: 471 cross-reference/family targets with no entry, still growing (817 missing targets across all warnings, most repeats of the same 471).
4. `runs_since_lint` is now 2 (lint debt still deeply negative, -4.10, so not imminent by the selector's own scoring); the duplicate-row inflation noted previously still applies — see [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md), not yet fixed.
5. Next **originality** check due around run 40 (forced: multiples of 10).
6. Six pre-existing `link override target has no entry` warnings on *alone-adj, favorite-adj, that-pron, very-adv, whatever-det* (and one time-n example-marking warning) are unchanged and harmless until those target entries or forms exist; not a gate failure.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. The first sense of a defining-vocabulary word's own entry is exempt from the check entirely (warning only); `core_idea` and phrase definitions are never exempt.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field; `write_record` merges a role rerun with the earlier successful role's record, so a single-role rerun (e.g. `--roles reviewer-b`) is the fix for a parse failure, not a full rerun.
- Never mutate a list while iterating over it when patching entry JSON by script (caused one runaway process in an earlier run, killed before it wrote anything).
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep, per-prep, adult-n, accept-v* (pronunciation), *admire-v, adult-adj* (pronunciation), *additional-n* (declined, resolved).
