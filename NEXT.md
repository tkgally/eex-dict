# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-27 by the fourth and last cycle (review) of the 18:44 UTC run (PRs #106 to #109).*

## State

- 661 entries, all `reviewed` (0 `draft`). Queue: 4,468 pending, 0 claimed, 661 done, 22 declined, 9 duplicate.
- First cycle: second panel round for 12 late-cycle verbs (*set* to *score*), with missing senses added by hand first; `set-adj` queued (the *be set to*, *all set* uses). Report: `journal/2026-09-27.md`. Second cycle: the eighteenth lint pass (`-2.md`). Third: second round for 11 verbs, *rule* to *rub* (`-3.md`); `rise-up-phrv` queued. Fourth: 16 verbs, *repeat* to *repair* (`-4.md`).
- 360 `reviewed` entries remain at one panel round. 39 one-sense entries still carry a signpost.
- Run shape: a run every six hours, at most four cycles, 12 entries a build; weights build 0.45, review 0.30. The selector owes review many cycles; that is intended.
- Spend: US$0.52 this cycle; US$1.51 today, of the US$15 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs after *share* (`queue.py next` decides). At most twelve entries, each as full as a 2026-09-25 verb (senses, idioms, learner errors, usage note where one helps). Check each definition covers every example and collocation in its sense; reviewer-a caught five that did not this run.
2. **review**: first the one-round entries created after 2026-09-26T19:40Z (later cycles of long runs; thinner): check each for missing common senses, idioms, learner errors; *set*–*score*, *rule*–*rub*, *repeat*–*rest*, *regret*–*repair* done 2026-09-27; next *read*–*refuse*, *push*–*reach*, then *need*–*punish* and the closure nouns and adjectives. Then the oldest one-round entries, the 2026-09-21T15:39 entries after `admire-v` (`python3` sort by `provenance.created`). When a run opens *anyone, anybody, anything*: check they agree with the new *someone/somebody/something* notes (those stay natural in questions expecting yes). Clear the signpost on any one-sense entry a review opens ([note](wiki/notes/one-sense-signposts.md); 39 left). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)).
3. **closure**: only `upward|adv` is left under `--source closure` (the ~1,100 gap lemmas appear to be mostly defining-vocabulary words, queued as `defining` rows); closure runs now draw on `--source family`, then `crossref`. Check each claimed row's part of speech first. The row `good looking|adj` (queued 2026-09-26) should read *good-looking*; draft it with the hyphen. *pen* the animal enclosure is an unrelated homograph: queue it as `pen-n-2` when a run can, never as a sense of `pen-n`.
4. **lint**: next due in five runs (after 2026-09-27's eighteenth pass) (`next_mode.py` decides). Every lint: check each BACKLINK line `crossref --all --apply` prints; about one in five is wrong. A review that removes a cross-reference removes its mirror too, or lint re-creates it (a dry `crossref --all` does not show pending back-links). `reviewer-a` `pronunciation` precision is 0.32 over 112 decisions; `inflection` 0.06 over 16: re-measure; a family under 0.30 at twenty decisions is switched off.
5. When drafting or reviewing touches `break-v`: sense 4's definition becomes "begin suddenly", restriction moved to `explanation` (full pipeline). `boil-v` sense 1: move *(of a liquid)* to `explanation` likewise.
6. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`, `homograph-queue-and-inflection` (`lie-v-2` *tell an untruth*, `pen-n-2`, and `ring-v-2` *put a circle around*, past **ringed**, need a hand claim and a check of the forms `inflect.py` writes); `crossref-first-sense-backlinks` partly fixed.
7. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, `ɔ`, and `ɑ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection (again on `heat-v`, 2026-09-26).
- *fire* and *hire* are transcribed with two syllables (`ˈfaɪ.ɚ`, `ˈhaɪ.ɚ`), verified by the panel and CMU; reject one-syllable objections.
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
- Call `metrics.py` once per run, in wrap-up only. Set hand-written provenance timestamps from `date -u`, never ahead of the clock.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Six open questions; the ones that most need you: 4 (split *be/have/do/one* by part of speech?), 5 (the look of the marks), and 6 (should infinitive *to* get an entry, and under what part of speech?). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: two prune-branch lines (`claude/relaxed-bell-ngyr08`, `claude/relaxed-bell-iujuq0`, both fully merged).
- Originality checks: reviewer-a now gives quotes for "copied" that web search cannot find (six on 2026-09-26, three of them our own wording); search alone decides the verdicts ([note](wiki/notes/reviewer-noise.md)).
- This session's reports: `journal/2026-09-26-20.md` to `-34.md`.
