# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the fifth scheduled Routine run (build mode).*

## State

- 120 entries, all `reviewed` (0 `draft`). Queue: 4,175 pending, 120 done, 391 closure-gap, 4 duplicate.
- This run drafted and fully reviewed 10 determiners (*that, their, these, this, those, what, whatever, which, whose, your*) and 4 pronouns (*all, another, any, anybody*). Two-reviewer panel: 38 issues, 28 blocking; adjudicated 28 apply / 10 reject. Rejected reviewer-a's repeated claim that `which-det`'s *in which case* / *by which time* sense and *which one* are pronoun, not determiner, use — checked against a grammar reference (relative determiners); kept as drafted. Applied fixes caught real pos-split drift in `whatever-det` (a clause-use sentence that belonged to `whatever-pron`) and `all-pron` (two examples using a following noun, which is `all-det`'s territory, not a personal pronoun). Queued `these-pron` and `those-pron`, missing targets the seed vote had not queued.
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass. Spend today: US$0.65 of US$5.00 (this run: US$0.33).
- `next_mode.py` debts: closure 0.80, review 0.60, build 0.40, originality 0.40, site 0.40, lint -0.60 (2 runs since last lint of 5).

## Queue (work top-down, one unit at a time)

1. **review**: 108 entries reviewed only once (one panel round); 34 `markup-pending` among the debt from before this run (unchanged this run — build was chosen over review by scheduler debt).
2. **build/closure**: the pos-split pointers this run created or left open — `that-pron`, `this-pron`, `these-pron`, `those-pron`, `what-pron`, `whatever-pron`, `which-pron`, `whose-pron`, `yours-pron`, `theirs-pron` — are all queued and now referenced from live entries; closure gap is 391 and growing, due for its own pass.
3. **closure**: cross-reference/family targets with no entry yet (391 open) surface through the queue in due course.
4. Next **lint** due in about three runs from now (runs_since_lint = 2); re-measure reviewer precision then.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: a word's use in another part of speech gets its own entry and a pointer in `see_also`, never demonstrated with a worked example inside another entry. Watch specifically for a determiner's word used before a clause or standing alone with no following noun — that belongs in the paired pronoun entry, not a sense/collocation here (this run's `whatever-det`/`all-pron` fixes).
- American IPA carries no length mark (`ː`); British keeps it.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- **asleep**, **afraid**, **alive**, **alone**, **awake** never come immediately before a noun, but do follow a noun with a complement (*the baby asleep in the crib*); carry forward if either is touched again.
- A reviewer's confident-sounding but wrong claim is rejected with a one-line reason, not applied for safety's sake (this run: `which-det` sense 2, checked against a grammar reference rather than rejected on instinct alone).
- Do not re-enable a switched-off (role, family) pair without a fresh measurement showing it above 30 percent.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision 0.37 over 222 decisions, not yet the twenty more the assumption waits for.
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
