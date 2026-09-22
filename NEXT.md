# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-sixth scheduled build run.*

## State

- 322 entries, all `reviewed` (0 `draft`). Queue: 4,130 pending, 32 claimed, 322 done, 9 declined, 4 duplicate (total 4,497).
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Claimed 20 band-1 words; released 8 verbs (*care, carry, catch, cause, celebrate, change, charge, check*) back to `pending`, favoring fewer, better entries. Drafted *times* (prep) and *either* (conj) — both queued by the prior review run for the crossref split-outs — plus ten verbs: *breed, bring, brush, build, burn, bury, buy, calculate, call, calm*.
- Inflections 12/12 verified (*breed, bring, build, buy* from the exceptions table, the rest by rule). Pronunciation 24/24 verified, all agreement, no disputes.
- Panel: 38 issues (32 blocking), 28 applied, 10 rejected, 0 escalated. Precision this run: reviewer-a 0.72, reviewer-b 0.78.
- Real content fixes: circularity and an overstated exclusivity claim in *times*/*either*; a house-style definition-prefix bug in *breed*; a disputed *bring*/*take* learner error rewritten unambiguously; an unverifiable etymological claim pulled from *bury the hatchet*'s adaptation note (etymology claims belong only in `etymology`, never adaptation, per the style guide); *call* sense 4 unified after two readings conflicted. Rejected a request to split *times* into two part-of-speech entries — kept combined per the prior run's explicit queue note.
- Fixed three defining-vocabulary violations (*gradually*, *intensely*, *prepare*) by rewording.
- Mechanical checks all clean: gate, caps, links, 305 unit tests, lint_vocab and crossref gates (0 violations, 0 errors).
- Spend: US$0.40 of the US$1.25 run-budget guideline; US$3.35 of the US$5 today's cap.

## Queue (work top-down, one unit at a time)

1. **closure**: `next_mode.py` now reports closure debt 2.50 (highest); `queue_closure` is 555 and growing. Re-run `next_mode.py --explain` fresh at the next session start, do not assume.
2. **review**: 236 `reviewed` entries remain at one panel round (debt 2.00).
3. **lint**: 3 runs since the last one; forced at 5.
4. Next originality run due at scheduler run 50 (every 10th); we are at run 45.
5. 37 new closure/crossref targets queued this run (phrasal verbs, word-family members, synonym/antonym targets for the ten new verbs and *times*/*either*); seven pre-existing `link override target has no entry` warnings, all harmless, all queued.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ` (not `iː`, `ɝː`, `ɔː`); British keeps the length mark. Confirmed again this run on *burn*, *call*.
- A claim about a word's or phrase's origin lives only in `etymology` (with two verified sources), never in an `adaptation` note — caught this run on *bury the hatchet*'s culture note, which was unverifiable and removed rather than kept as a hedge.
- `times` (prep) intentionally bundles the arithmetic "multiplied by" sense and the comparative "that much more" sense in one entry, per the review run that queued it (2026-09-22); a reviewer proposing to split them by part of speech was rejected on that basis.
- A full sense's definition may not open with an "of X:" restrictive prefix (that pattern is reserved, and only loosely, for subsenses); state the restriction in the sense's `explanation` instead. *break-v* sense 4 still has this bug uncorrected — a future lint or review pass should fix it.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` unchanged this run (twelve open items, no new escalations).
