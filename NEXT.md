# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fifty-fifth scheduled run (build).*

## State

- 371 entries, all `reviewed` (0 `draft`). Queue: 4,147 pending, 0 claimed, 371 done, 21 declined, 6 duplicate.
- This run: build, ten entries: `neither-conj` and the verbs *care, carry, catch, cause, celebrate, change, charge, check, chew*. `either-conj`'s compare note now points at `neither-conj` (item closed).
- About 262 `reviewed` entries remain at one panel round (the ten new ones included).
- Reviewer-b truncated its reply on two large entries (`catch-v`, `chew-v`); the `--roles reviewer-b` re-run fixed both cleanly. Watch for it on large verbs.
- Spend: US$0.46 this run; US$2.32 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **originality**: due at true run 50, which is probably the next run (`next_mode.py` decides).
2. **build**: band 1 in queue order, continuing the verbs: *choose, chop, clean, climb, close, collect, come, communicate, compare, compete, confuse, connect, consider, consist, contain...* *Come* and *close* are large; keep runs to eight to twelve entries when the batch holds large verbs.
3. **review**: one-round entries; the next oldest are the 2026-09-19 pronouns and determiners (*all-pron, another-pron, any-pron, anybody-pron, that-det, their-det, these-det, this-det, those-det, what-det...*).
4. **closure**: about 580 closure-gap lemmas. The *gene* and *diaper* closure rows queued this run are no longer used in any definition (both definitions were reworded); treat them as ordinary band-3 rows.
5. **lint**: next due after five runs from the ninth pass (about run 53).
6. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
7. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Never put a wrong form in italics in prose; wrong forms live only in `incorrect`.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words. A one-word synonym definition for a conjunction is reworded to the house pattern.
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- A verb + preposition pattern already covered by the verb's senses (*belong to*, *care for*, *charge with*) is not a phrasal verb entry.
- Idioms whose first noun is not the headword go under that noun (*catch fire* under *fire*, *change your mind* under *mind*), not under the verb.
- A region label means *mainly used there* (`check-v` sense 3, American, with *tick* usual in British English); reject objections that the word also occurs elsewhere.
- Releasing a claimed word you will not draft: `queue.py set ... pending` and remove it from the claim file; `queue.py sync` resets orphaned `claimed` rows on its own.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged; nothing added this run.
