# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-25 by the seventy-second scheduled run (lint, twelfth pass).*

## State

- 483 entries, all `reviewed` (0 `draft`). Queue: 4,340 pending, 0 claimed, 483 done, 21 declined, 6 duplicate.
- This run: lint. 19 sense back-links added; five misplaced and not yet moved (item 2). Log header repaired.
- About 332 `reviewed` entries remain at one panel round.
- For the originality reviewer call, pass `--reasoning-effort low` (a default-effort call returned nothing on 2026-09-23).
- Spend: US$0 this run; US$2.76 today, of the US$5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs after *hate* (*hear, heat, help, hide, hire, hit, hold, hope, hug, hurt*...; `queue.py next` decides). Keep runs to eight to twelve entries when the batch holds large verbs (*hold*, *hit*, *help*).
2. **Back-links to move by hand**, one entry at a time, when any run opens these entries (or the next lint): `happen-v` `become-v` synonym sense 1 -> 2; `fit-v` `belong-v` synonym 1 -> 4; `fix-v` `cure-v` synonym 1 -> 2; `fire-v` `employ-v` antonym 1 -> 2; `give-v` `lend-v` synonym 1 -> 4 ([note](wiki/notes/crossref-first-sense-backlinks.md)).
3. **review**: one-round entries; the next oldest are the 2026-09-19 pronouns (*someone-pron, something-pron, theirs-pron, them-pron, themselves-pron, these-pron, they-pron, this-pron, those-pron, us-pron...*). Clear the signpost on any one-sense entry a review opens ([note](wiki/notes/one-sense-signposts.md); 42 left). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)).
4. **closure**: about 887 closure-gap lemmas.
5. **lint**: next due five runs after this one (`next_mode.py` decides). Originality is due soon. Every lint: check each BACKLINK line `crossref --all --apply` prints; about one in four is wrong. `reviewer-a` `pronunciation` precision is 0.33 over 96 decisions: re-measure; under 0.30 it is switched off.
6. When drafting or reviewing touches `break-v`: sense 4's definition becomes "begin suddenly", restriction moved to `explanation` (full pipeline). `boil-v` sense 1: move *(of a liquid)* to `explanation` likewise.
7. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; `crossref-first-sense-backlinks` partly fixed.
8. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection.
- *fire* is transcribed with two syllables (`ˈfaɪ.ɚ`), verified by the panel and CMU; reject one-syllable objections.
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
- Adaptation notes: an opening quoted headword is allowed; words named inside the sentence take `**...**`. Reject reviewer-b's recurring flag against it.
- Reflexive and emphatic *-self* entries: a wrong form such as *come with himself* never goes in italics; the learner-error box carries it. Stress marks after a syllable break (`hər.ˈsɛlf`) are house practice; reject flags.
- *Forgot my phone at home* and *follow after* are grammatical; do not add learner errors against them (2026-09-25).
- *give someone something* and *give her the chance* are two-object patterns; reject flags that call them anything else. *I'm hating this* is possible informally; do not list it as an error.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Six open questions; the ones that most need you: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged; nothing added this run.
- This run's report: `journal/2026-09-25-8.md`.
