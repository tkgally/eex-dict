# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fifty-third scheduled run (review).*

## State

- 361 entries, all `reviewed` (0 `draft`). Queue: 4,134 pending, 0 claimed, 361 done, 21 declined, 5 duplicate.
- This run: a second panel round on the 20 oldest one-round entries, all determiners (*each* through *such*). 252 `reviewed` entries remain at one panel round.
- Panel: 42 issues (32 blocking), 25 applied, 17 rejected, 0 escalated. Seven entries drew no issue.
- Spend: US$0.47 of this run's US$1.25; US$1.86 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **lint**: due now (five runs since the last lint; the selector should pick it next).
2. **build**: the rest of band 1 in queue order, starting with the verbs (*care, carry, catch, cause, celebrate, change, charge, check...*). Large verbs (*carry*, *catch*, *change*, *check*) need room: eight to twelve per run. `neither-conj` (band 1, newly queued) belongs in an early build: model it on `either-conj`, then update `either-conj`'s compare note, which still points *neither ... nor* at `neither-det`.
3. **review**: 252 one-round entries; the next oldest are the 2026-09-19 pronouns and determiners (*all-pron, another-pron, any-pron, anybody-pron, that-det, their-det, these-det, this-det, those-det, what-det...*).
4. **closure**: 559 closure-gap lemmas.
5. Next originality run due at run 60.
6. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
7. Tooling fixes due (notes in `wiki/notes/`): `review-panel-rerun-duplicate-records` (recurred this run on `least-det`), `queue-stale-claimed-rows`, `metrics-duplicate-calls`, `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection.
- *X of* before a noun phrase (*each of us*, *neither of them*, *most of the students*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *at most*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words. A one-word synonym definition for a conjunction is reworded to the house pattern.
- *Several* means more than two ("three or more" is right); bare *much* before a noun is normal after *so*, *too*, *as*, not *very*.
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- A queue row's `claimed` status can go stale; check `queue.py counts` for `claimed > 0` between lint passes.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: fourteen open items, none added this run.
