# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-24 by the fifty-seventh scheduled run (build).*

## State

- 381 entries, all `reviewed` (0 `draft`). Queue: 4,169 pending, 0 claimed, 381 done, 21 declined, 6 duplicate.
- This run: build, ten verbs (*choose, chop, clean, climb, close, collect, come, communicate, compare, compete*). 25 panel issues, 19 applied, 6 rejected.
- About 270 `reviewed` entries remain at one panel round.
- For the originality reviewer call, pass `--reasoning-effort low` (a default-effort call returned nothing on 2026-09-23).
- Spend: US$0.45 this run; US$0.45 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs: *confuse, connect, consider, consist, contain, continue, control, cook, cool, copy, cost, cough...* *Consider*, *continue*, and *control* are large; keep runs to eight to twelve entries when the batch holds large verbs.
2. **review**: one-round entries; the next oldest are the 2026-09-19 pronouns and determiners (*all-pron, another-pron, any-pron, anybody-pron, that-det, their-det, these-det, this-det, those-det, what-det...*).
3. **closure**: about 610 closure-gap lemmas (this run queued *axe* and *border*, among others).
4. **lint**: next due after five runs from the ninth pass (`next_mode.py` decides). Originality next at true run 60.
5. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
6. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-changed-base` (until fixed, run the local vocabulary gate with `--base origin/main`), `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and add the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (two checks now support it: `wiki/notes/reviewer-noise.md`).

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
- Settled this run: *chop* "reduce" keeps `informal`; *come from* and *come in* (colors, sizes) keep "not used in continuous tenses".
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged; nothing added this run.
- Ten new verbs; details in `journal/2026-09-24.md`.
