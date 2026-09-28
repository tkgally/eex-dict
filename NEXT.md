# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-28 by the first cycle (review) of the 18:43 UTC run.*

## State

- 661 entries, all `reviewed` (0 `draft`). Queue: 4,474 pending, 0 claimed, 661 done, 22 declined, 9 duplicate.
- 2026-09-28 18:43 run, first cycle: second panel round for *ask, boil, break, breathe, become, begin*, with senses, phrases, and learner errors added by hand first (`journal/2026-09-28-13.md`). The 12:44 run (`-9.md` to `-12.md`) did the eight modals, the twentieth lint pass, the conjunctions and *appeal*–*arrive*, and *assume*–*board*; the 06:44 run (`-5.md` to `-8.md`) and the 00:44 run (`2026-09-28.md` to `-4.md`) came before.
- 241 `reviewed` entries remain at one panel round. 38 one-sense entries still carry a signpost.
- Run shape: a run every six hours, at most four cycles, 12 entries a build; weights build 0.45, review 0.30. The selector owes review many cycles; that is intended.
- Spend: US$0.37 this cycle; US$4.68 today, of the US$15 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs after *share* (`queue.py next` decides). At most twelve entries, each as full as a 2026-09-25 verb (senses, idioms, learner errors, usage note where one helps). Check each definition covers every example and collocation in its sense; reviewer-a caught five that did not this run. `when-adv` and `where-adv` (queued, band 1) must hold the reported-question use (*I don't know where she lives*) and its word-order learner error (*where is the station* inside a question); both were taken out of the conjunctions 2026-09-28.
2. **review**: first the one-round entries created after 2026-09-26T19:40Z (later cycles of long runs; thinner): check each for missing common senses, idioms, learner errors; *set*–*score*, *rule*–*rub*, *repeat*–*rest*, *regret*–*repair* done 2026-09-27, *read*–*refuse*, *push*–*reach*, *need*–*pay*, *peel*–*protect*, *prove*–*punish* and the 21:45 closure words 2026-09-28; the 22:57 closure words, *adopt*–*ahead*, *act*–*alarm*, and the eight modals also done 2026-09-28. The conjunctions, *appeal*–*arrive*, *assume*–*board*, and *ask*, *boil*–*begin* also done 2026-09-28. Next the oldest one-round entries onward from *breed-v* (then *bring, brush, build, burn, bury, buy, calculate, call, calm*) by `provenance.created` (`python3` over `provenance.reviews` run ids lists them). Keyword rule: *bite the bullet* and *bite someone's head off* should move to `bullet-n` and `head-n` (both exist) in a run that reviews those; *blow off steam*, *blow your own horn*, *blow the whistle on* wait for `steam-n`, `horn-n`, `whistle-n`; *break the ice*, *break new ground*, *break someone's heart*, *break a leg* wait for `ice-n`, `ground-n`, `heart-n`, `leg-n`; *make someone's blood boil* for `blood-n`; *not breathe a word* for `word-n`. Early verbs lack learner errors and usage notes: add them. *can-modal* and *must-modal* were outside the modal block; check them against the others' *could have* notes. When a run opens *anyone, anybody, anything*: check they agree with the new *someone/somebody/something* notes (those stay natural in questions expecting yes). Clear the signpost on any one-sense entry a review opens ([note](wiki/notes/one-sense-signposts.md); 39 left). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)).
3. **closure**: only `upward|adv` is left under `--source closure` (the ~1,100 gap lemmas appear to be mostly defining-vocabulary words, queued as `defining` rows); closure runs now draw on `--source family`, then `crossref`. Check each claimed row's part of speech first. The row `good looking|adj` (queued 2026-09-26) should read *good-looking*; draft it with the hyphen. *pen* the animal enclosure is an unrelated homograph: queue it as `pen-n-2` when a run can, never as a sense of `pen-n`.
4. **lint**: next due in four runs (after 2026-09-28's twentieth pass) (`next_mode.py` decides). Every lint: check each BACKLINK line `crossref --all --apply` prints; about one in five is wrong, and each TYPE-MISMATCH (a review that changes one side's cross-reference type must change the mirror too). A review that removes a cross-reference removes its mirror too, or lint re-creates it. `reviewer-a` `inflection` switched off 2026-09-28 (0.05 over 21); `pronunciation` 0.33 over 119 is the nearest live family to the line: re-measure.
5. Back-links: `crossref --apply` attaches a mirror to the target's first sense; on 2026-09-28 it put *break* under *beat* "hit repeatedly" (moved to "defeat"). Check every back-link a review creates.
6. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`, `homograph-queue-and-inflection` (`lie-v-2` *tell an untruth*, `pen-n-2`, and `ring-v-2` *put a circle around*, past **ringed**, need a hand claim and a check of the forms `inflect.py` writes); `crossref-first-sense-backlinks` partly fixed.
7. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, `ɔ`, and `ɑ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection (again on `heat-v`, 2026-09-26).
- *could*, *should*, *would*, and *good* rhyme (`ʊd`); reject objections.
- *fire* and *hire* are transcribed with two syllables (`ˈfaɪ.ɚ`, `ˈhaɪ.ɚ`), verified by the panel and CMU; reject one-syllable objections.
- A wh-word in a reported question (*I don't know when it starts*) is the adverb entry, not the conjunction; *whether* and *if* stay conjunctions.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Never put a wrong form in italics in prose; wrong forms live only in `incorrect`.
- `out-prep` holds the *out of* senses and bare American *out the window*; *out of milk* stays prepositional, not adjectival.
- A preposition with a noun-phrase object stays a preposition (*above ours*, *below him*, *he's above that*); *during* can mean *all through*. Reject reviewer-a's adverb/adjective calls.
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
- Imperative *look*, *listen* as attention-getters ("Look, I'm sorry...") stay verb senses; reject flags that move them to an interjection.
- `core_idea` is a sentence by house style; reject reviewer-b's "not phrasal" flags. The not-continuous code stays where the learner-error note says "not normally" (*need*, *own*).
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Six open questions; the ones that most need you: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- Originality checks: reviewer-a now gives quotes for "copied" that web search cannot find (six on 2026-09-26, three of them our own wording); search alone decides the verdicts ([note](wiki/notes/reviewer-noise.md)).
- Latest reports: `journal/2026-09-28.md` to `-12.md`.
