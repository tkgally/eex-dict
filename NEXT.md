# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fifty-first scheduled run (build).*

## State

- 353 entries, all `reviewed` (0 `draft`). Queue: 4,138 pending, 0 claimed, 353 done, 21 declined, 5 duplicate (total 4,517).
- This run: eleven new entries, *so, than, that* (conjunctions) and *through, throughout, toward, under, upon, via, within, without* (prepositions); *towards* marked `duplicate`, recorded as the British variant of `toward-prep`.
- Relative *that* (*the book that I read*) now lives in `that-pron` sense 2, not in `that-conj` (both reviewers: it is a pronoun use). `that-pron` was re-reviewed this run.
- Panel: 50 issues (42 blocking), 40 applied, 10 rejected, 0 escalated.
- Spend: US$0.46 of this run's US$1.25; US$0.89 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **build**: the last band-1 conjunction *as* (large: time, reason, manner, *as ... as* comparisons; *as* the preposition already exists, so keep to clause uses), then the remaining band-1 prepositions *on, over, such as, to, until, up, with* (each large; *on*, *to*, *with* are very large: two or three per run), then the rest of band 1 in queue order.
2. **review**: about 254 `reviewed` entries remain at one panel round.
3. **closure**: 556 closure-gap lemmas.
4. Next lint pass due at scheduler run 53; next originality run due at scheduler run 60 (this was run 51).
5. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
6. Tooling fixes due (notes in `wiki/notes/`): `review-panel-rerun-duplicate-records`, `queue-stale-claimed-rows`, `metrics-duplicate-calls`, `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`, 2026-09-23 update).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ`; British keeps it.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double.
- A conjunction entry points to the preposition's **-ing** use (*after finishing*) only as the other part of speech, in one clause.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- Demonstrative *that* (determiner and pronoun sense 1) keeps the full vowel; only clause-linking *that* weakens to *thut* (a rejected reviewer claim, this run).
- *used after ...* / *used before ...* definitions are allowed for function words (style guide section 2); reject a reviewer who calls them banned.
- *if ... or not* is standard English; only directly before **or not** is **whether** required.
- A queue row's `claimed` status can go stale; check `queue.py counts` for `claimed > 0` between lint passes.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock (validate rejects `modified` earlier than `created`).

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged this run, thirteen open items.
