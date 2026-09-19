# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the fourth scheduled Routine run (lint mode).*

## State

- 106 entries, all `reviewed` (0 `draft`). Queue: 4,187 pending, 106 done, 389 closure-gap.
- Lint ran on schedule (forced: five runs since the last one). `tools/metrics.py --precision` over all 798 logged decisions: reviewer-a 0.56 overall, reviewer-b 0.37. Five (role, family) pairs stayed under 30 percent over twenty-plus decisions — reviewer-a `example-policy` (0.16/44), `grammar-code` (0.27/75), `sense-structure` (0.29/48); reviewer-b `example-policy` (0.05/83), `explanation` (0.24/21) — and are now switched off in `tools/review_panel.py` (`DISABLED_FAMILIES`): those issues are downgraded to `ok` before they reach adjudication. See `wiki/notes/reviewer-precision.md` for the table and `wiki/log.md`'s 2026-09-19 lint entry.
- Pre-flight: no open pull request. Two owner-closed branches (`claude/admiring-rubin-05mkcp`, `claude/magical-dirac-ydspk3`) show file residue against `main` only because later runs keep editing the same entries; both already logged as absorbed. Other orphan branches confirmed absorbed. `claim.py --prune` removed four stale claim files.
- Mechanical checks: caps, links, `crossref --all --apply` (865 warnings, all expected missing closure targets), `lint_vocab --all --queue` (0 violations). Noted, not fixed (needs the full review pipeline, not a lint edit): `most-det` and `other-det` each use one out-of-vocabulary word in their sense-1 definition ("article", "additional").
- Wiki index checked against pages on disk: in sync, no orphans, no dead links.
- Gate, caps, links, 292 unit tests (289 plus 3 new for the switch-off), lint_vocab and crossref gates all pass. Spend today: US$0.33 of US$5.00 (this run: US$0, no paid calls).
- `next_mode.py` will choose from the debt table next run; review (34 remaining `markup-pending`) is the largest debt after lint.

## Queue (work top-down, one unit at a time)

1. **review**: the 34 remaining `markup-pending` entries (see `wiki/log.md`'s 2026-09-18 decision entry for the full list), in blocks of 20, oldest/simplest first; `time-n` carries one flagged example (missing headword form) to fix in the same pass.
2. **build** from the queue in its order: the pos-split pronoun/adverb pointers plus remaining core determiners and quantifiers.
3. **closure**: cross-reference/family targets with no entry yet keep growing (389 open); they surface through the queue in due course.
4. Next **lint** due in about five runs (roughly 2026-09-21/22 at this cadence); re-measure reviewer precision then and append to `wiki/notes/reviewer-precision.md`.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: a word's use in another part of speech gets its own entry and a pointer in `see_also`, never demonstrated with a worked example inside another entry.
- American IPA carries no length mark (`ː`); British keeps it. Compare a new entry against `few-det.json` or `any-det.json` before drafting.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- **asleep**, **afraid**, **alive**, **alone**, **awake** never come immediately before a noun, but do follow a noun with a complement (*the baby asleep in the crib*); carry forward if either is touched again.
- A reviewer's confident-sounding but wrong claim is rejected with a one-line reason, not applied for safety's sake.
- Do not re-enable a switched-off (role, family) pair without a fresh measurement showing it above 30 percent; this project runs no live A/B test to find out early.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision 0.37 over 222 decisions, five runs in, not yet the twenty the assumption waits for.
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
