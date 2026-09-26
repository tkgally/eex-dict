# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-26 by the seventy-fifth scheduled run (build).*

## State

- 515 entries, all `reviewed` (0 `draft`). Queue: 4,377 pending, 0 claimed, 515 done, 21 declined, 9 duplicate.
- This run: build, ten verbs (*imagine, improve, include, increase, inform, injure, install, intend, interest, introduce*); 16 adjudication decisions; three back-links, all right.
- About 354 `reviewed` entries remain at one panel round.
- For the originality reviewer call, pass `--reasoning-effort low` (a default-effort call returned nothing on 2026-09-23).
- Spend: US$0.31 this run; US$1.08 today, of the US$5 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs after *introduce* (*invest, invite, involve, join*...; `queue.py next` decides). Eight to twelve entries per run.
2. **Back-links to move by hand**, one entry at a time, when any run opens these entries (or the next lint): `happen-v` `become-v` synonym sense 1 -> 2; `fit-v` `belong-v` synonym 1 -> 4; `fix-v` `cure-v` synonym 1 -> 2; `fire-v` `employ-v` antonym 1 -> 2; `give-v` `lend-v` synonym 1 -> 4 ([note](wiki/notes/crossref-first-sense-backlinks.md)).
3. **review**: one-round entries; the next oldest are the 2026-09-19 pronouns (*someone-pron, something-pron, theirs-pron, them-pron, themselves-pron, these-pron, they-pron, this-pron, those-pron, us-pron...*). Clear the signpost on any one-sense entry a review opens ([note](wiki/notes/one-sense-signposts.md); 42 left). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)).
4. **closure**: about 924 closure-gap lemmas. Check each claimed row's part of speech first (three bogus rows this run). *pen* the animal enclosure is an unrelated homograph: queue it as `pen-n-2` when a run can, never as a sense of `pen-n`.
5. **lint**: next due in about two runs (`next_mode.py` decides). Originality is due soon. Every lint: check each BACKLINK line `crossref --all --apply` prints; about one in four is wrong. `reviewer-a` `pronunciation` precision is 0.33 over 96 decisions: re-measure; under 0.30 it is switched off.
6. When drafting or reviewing touches `break-v`: sense 4's definition becomes "begin suddenly", restriction moved to `explanation` (full pipeline). `boil-v` sense 1: move *(of a liquid)* to `explanation` likewise.
7. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`, `crossref-cross-type-backlinks` (new); `crossref-first-sense-backlinks` partly fixed.
8. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection (again on `heat-v`, 2026-09-26).
- *fire* and *hire* are transcribed with two syllables (`ˈfaɪ.ɚ`, `ˈhaɪ.ɚ`), verified by the panel and CMU; reject one-syllable objections.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Never put a wrong form in italics in prose; wrong forms live only in `incorrect`.
- *Which* before a noun is the determiner, relative uses included; reject flags that move them to `which-pron`.
- Relative *that* is a pronoun (`that-pron` sense 2); `that-conj` holds only the clause after *say/think* and the result after *so/such*.
- *used after ...* / *used before ...* definitions are allowed for function words. A one-word synonym definition for a conjunction is reworded to the house pattern.
- Infinitive *to* is not covered by `to-prep` (open question 6); do not add it as a sense.
- A verb + preposition pattern already covered by the verb's senses (*belong to*, *care for*, *hear from*, *hear of*) is not a phrasal verb entry.
- Idioms whose first noun is not the headword go under that noun (*catch fire* under *fire*, *hurt someone's feelings* under *feelings*), not under the verb.
- A region label means *mainly used there* (`check-v` sense 3, `hire-v` sense 2, British); reject objections that the word also occurs elsewhere.
- Releasing a claimed word you will not draft: `queue.py set ... pending` and remove it from the claim file; `queue.py sync` resets orphaned `claimed` rows on its own.
- A subject restriction (*of food*, *of a train*) goes in `explanation`, never as a prefix in the definition.
- A participle phrase (*badly damaged*, *well hidden*) is a `phrase` collocation (*be well hidden*), never "adverb + verb".
- Settled: *mix up* is a phrasal verb (`mix-up-phrv`); *cost* sense 3 past form **costed** lives in its explanation.
- Adaptation notes: an opening quoted headword is allowed; words named inside the sentence take `**...**` and illustrations `*...*` (draft them that way; reviewer-b flags plain quotation marks every time).
- Reflexive and emphatic *-self* entries: a wrong form never goes in italics; the learner-error box carries it. Stress marks after a syllable break are house practice; reject flags.
- *give someone something* and *give her the chance* are two-object patterns; reject flags that call them anything else. *I'm hating this* is possible informally.
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Six open questions; the ones that most need you: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged; nothing added this run.
- This run's report: `journal/2026-09-26-3.md`.
