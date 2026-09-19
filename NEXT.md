# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-19 by the sixth scheduled Routine run (build mode).*

## State

- 132 entries, all `reviewed` (0 `draft`). Queue: 4,163 pending, 132 done, 388 closure-gap, 4 duplicate.
- This run drafted and fully reviewed 12 pronouns (*anyone, anything, both, each, either, enough, everybody, everyone, everything, few, he, her*), continuing the determiner/pronoun pos-split set. Two-reviewer panel: 45 issues, 30 blocking; adjudicated 30 apply / 15 reject. Real catches: a "standing alone without a noun" grammar clause folded into the *definition* field on five entries (moved to the explanation); `each-pron`'s definition used the headword `each` circularly, and its "ten dollars each" example was a postposed-adverbial use, not a pronoun use, and was removed along with its collocation; `everything-pron`/`anything-pron` definitions restated the headword as `any`/`every` plus `thing`; three learner-error items and one collocation illustrated the determiner, not the pronoun, use. Rejected several reviewer-a pronunciation objections against `anyone`, `everybody`, and `few`'s American IPA, all contradicted by the CMU/panel agreement already on record or by house style (no American length mark); rejected two usage-note objections that would have contradicted the already-published, reviewed `both-det`/`few-det` entries.
- Pre-flight: no open pull request, no orphan branches, inbox empty (only `archive/`).
- Gate, caps, links, 292 unit tests, lint_vocab and crossref gates all pass. Spend today: US$0.93 of US$5.00 (this run: US$0.28).
- `next_mode.py` for the next run: **originality** (forced — run 10 is a multiple of 10). Debts otherwise: closure 0.90, review 0.80, site 0.45, originality 0.45, build -0.05, lint -0.55 (3 runs since last lint of 5).

## Queue (work top-down, one unit at a time)

1. **originality** is forced next run regardless of debt: `originality_check.py sample --n 10` over the 132 reviewed entries.
2. **review**: 120 entries reviewed only once (one panel round); 34 `markup-pending` entries unchanged since the lint run before last.
3. **build/closure**: pos-split pointers this run left open — `something-pron`, `neither-pron`, `enough-adv`, `she-pron`, `him-pron`, `his-pron`, `himself-pron`, `hers-pron`, `herself-pron` — are queued (mostly already were) and now referenced from live entries.
4. **closure**: cross-reference/family targets with no entry yet (388 open, still growing) surface through the queue in due course.
5. Next **lint** due in about two runs from now (runs_since_lint = 3); re-measure reviewer precision then.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- Marks: `**word**` and `*phrase*` only; the headword in an example is marked by the site, by hand only for an irregular, separated, or contracted form.
- Part of speech: watch for a pronoun standing where a determiner-like postposed adverbial reading is also possible (this run's `each-pron`: "ten dollars each" removed as adverbial, not pronoun).
- Definitions never fold in grammar/distribution facts ("standing alone without a noun"); that belongs in the explanation, not the definition (this run's fix across five entries).
- American IPA carries no length mark (`ː`); British keeps it. A reviewer claim to the contrary is always wrong.
- No external word list, frequency list, or pronouncing data is ever stored in the repository, whatever its licence.
- A claim that contradicts an already-published, reviewed sibling entry (`both-det`, `few-det`) is rejected for consistency unless open data settles it the other way.
- Do not re-enable a switched-off (role, family) pair without a fresh measurement showing it above 30 percent.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by the part-of-speech rule?); open question 5 (the look of the marks); open question 2 (reviewer-b's tier) stays "keep" — precision 0.37 over 222 decisions, not yet the twenty more the assumption waits for.
- `reviews/needs_curator.txt` has four prune-branch lines and one pronunciation question (*several-det* British), all awaiting the owner; this tool set cannot delete branches.
