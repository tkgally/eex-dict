# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fifty-second scheduled run (build).*

## State

- 361 entries, all `reviewed` (0 `draft`). Queue: 4,133 pending, 0 claimed, 361 done, 21 declined, 5 duplicate.
- This run: eight new entries, *as* (conjunction) and *on, over, such as, to, until, up, with* (prepositions). Every band-1 conjunction and preposition in the queue now has an entry.
- Panel: 42 issues (33 blocking), 29 applied, 13 rejected, 0 escalated.
- Spend: US$0.49 of this run's US$1.25; US$1.39 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **build**: the rest of band 1 in queue order, starting with the verbs (*care, carry, catch, cause, celebrate, change, charge, check...*). Large verbs (*carry*, *catch*, *change*, *check*) need room: eight to twelve per run.
2. **review**: about 272 `reviewed` entries remain at one panel round (the selector's likely next pick).
3. **closure**: 558 closure-gap lemmas.
4. Next lint pass due at scheduler run 53 (the next run if the selector agrees); next originality run due at run 60 (this was run 52).
5. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
6. Tooling fixes due (notes in `wiki/notes/`): `review-panel-rerun-duplicate-records`, `queue-stale-claimed-rows`, `metrics-duplicate-calls`, `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`).
7. Missing targets from this run: *as* (adverb) and *as if* (conjunction) newly queued by `crossref.py` (band 3); *on*, *over*, *up* (adverbs), *get over*, *take over* were already queued.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ`; British keeps it.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words; reject a reviewer who calls them banned. A one-word synonym definition for a conjunction is reworded to the house pattern (*because; for the reason that*; *despite the fact that*).
- *The same ... as* is a comparison (`as-conj` sense 2), not a determiner use; numbered street addresses take *at*, not *on*; *a quarter till five* is regional American (rejected reviewer claims, this run).
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- *if ... or not* is standard English; only directly before **or not** is **whether** required.
- A queue row's `claimed` status can go stale; check `queue.py counts` for `claimed > 0` between lint passes.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and new 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: fourteen open items (one added this run, the infinitive *to* question).
