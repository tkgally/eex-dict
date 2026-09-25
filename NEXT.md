# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-25 by the sixty-fifth scheduled run (review).*

## State

- 443 entries, all `reviewed` (0 `draft`). Queue: 4,276 pending, 0 claimed, 443 done, 21 declined, 6 duplicate.
- This run: review, second panel round on 20 pronouns and determiners (*all-pron* through *enough-pron*). 45 issues, 21 applied, 24 rejected, none escalated.
- About 312 `reviewed` entries remain at one panel round.
- For the originality reviewer call, pass `--reasoning-effort low` (a default-effort call returned nothing on 2026-09-23).
- Spend: US$0.44 this run and today, of the US$5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs: *exercise, exist, expand, expect, express, fall, farm, fear, feed, feel...* Keep runs to eight to twelve entries when the batch holds large verbs (*expect*, *fall*, *feel*). `end-up-phrv` and the *employ*/*examine*/*excite* families (*employee*, *exam*, *excited*, *exciting*) are queued from this run.
2. **review**: one-round entries; the next oldest are the 2026-09-19 pronouns (*everybody-pron, everyone-pron, everything-pron, few-pron, he-pron, her-pron, hers-pron, herself-pron, him-pron, himself-pron...*). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)); check each such flag against the fences below.
3. **closure**: about 610 closure-gap lemmas (this run queued *axe* and *border*, among others).
4. **lint**: due next run (five after the tenth pass of 2026-09-24) (`next_mode.py` decides). Originality is due next or soon. Every lint: check each back-link `crossref --all --apply` adds (it lands on sense 1 when no sense names the source).
5. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
6. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`, `crossref-first-sense-backlinks`.
7. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Never put a wrong form in italics in prose; wrong forms live only in `incorrect`.
- *Which* before a noun is the determiner, relative uses included (*in which case*, *which one*); reject flags that move them to `which-pron`.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words. A one-word synonym definition for a conjunction is reworded to the house pattern.
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- A verb + preposition pattern already covered by the verb's senses (*belong to*, *care for*, *charge with*) is not a phrasal verb entry.
- Idioms whose first noun is not the headword go under that noun (*catch fire* under *fire*, *change your mind* under *mind*), not under the verb.
- A region label means *mainly used there* (`check-v` sense 3, American, with *tick* usual in British English); reject objections that the word also occurs elsewhere.
- Releasing a claimed word you will not draft: `queue.py set ... pending` and remove it from the claim file; `queue.py sync` resets orphaned `claimed` rows on its own.
- A subject restriction (*of food*, *of a train*) goes in `explanation`, never as a prefix in the definition; reviewer-b flags it reliably.
- A participle phrase (*badly damaged*, *crushed to death*) is a `phrase` collocation (*be badly damaged*), never "adverb + verb"; reviewer-a flags it every time.
- Settled: *mix up* is a phrasal verb (`mix-up-phrv`); *cost* sense 3 past form **costed** lives in its explanation.
- Adaptation notes: an opening quoted headword is allowed; words named inside the sentence take `**...**`.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Three open questions: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged; nothing added this run.
- This run's report: `journal/2026-09-25.md`.
