# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fifty-fourth scheduled run (lint, ninth pass).*

## State

- 361 entries, all `reviewed` (0 `draft`). Queue: 4,133 pending, 0 claimed, 361 done, 21 declined, 6 duplicate.
- This run: lint. Back-links added to 12 entries; three logged tooling gaps fixed with tests (stale queue claims, duplicated review records on a re-run, doubled metrics rows); *belong to* (phrasal verb) row marked duplicate.
- Run counting: `next_mode.py` now counts one metrics row per run id, so the count dropped from 53 rows to 48 runs (after this one). The originality check will fire again at true run 50, two runs after this one; that is expected, not a bug.
- 252 `reviewed` entries remain at one panel round.
- Spend: US$0 this run; US$1.86 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **build**: the rest of band 1 in queue order, starting with the verbs (*care, carry, catch, cause, celebrate, change, charge, check...*). Large verbs (*carry*, *catch*, *change*, *check*) need room: eight to twelve per run. `neither-conj` (band 1) belongs in an early build: model it on `either-conj`, then update `either-conj`'s compare note, which still points *neither ... nor* at `neither-det`.
2. **originality**: forced at true run 50.
3. **review**: 252 one-round entries; the next oldest are the 2026-09-19 pronouns and determiners (*all-pron, another-pron, any-pron, anybody-pron, that-det, their-det, these-det, this-det, those-det, what-det...*).
4. **closure**: 559 closure-gap lemmas.
5. **lint**: next due after five more runs (about run 53).
6. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
7. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words. A one-word synonym definition for a conjunction is reworded to the house pattern.
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- A verb + preposition pattern already covered by the verb's senses (*belong to*) is not a phrasal verb entry.
- Releasing a claimed word you will not draft: `queue.py set ... pending` and remove it from the claim file; `queue.py sync` now resets orphaned `claimed` rows on its own.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: twelve open items (one, the *belong to* queue row, resolved this run).
