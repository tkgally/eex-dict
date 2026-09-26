# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-26 by the ninetieth scheduled run (lint), the last of a twelve-cycle session.*

## State

- 583 entries, all `reviewed` (0 `draft`). Queue: 4,419 pending, 0 claimed, 583 done, 21 declined, 9 duplicate.
- This session: builds *invest*–*kiss* (PR #76), *know*–*light* (PR #77), *like*–*manage* (PR #78), review of 20 prepositions and pronouns (PR #79), build *marry*–*name* (PR #80), lint (PR #81), build *need*–*own* (PR #82), originality check (PR #83), build *pack*–*plan* (PR #84), review of 20 prepositions and pronouns (PR #85), build *play*–*produce* (PR #86), lint ([journal](journal/2026-09-26-18.md)).
- About 372 `reviewed` entries remain at one panel round.
- Branch restart between cycles: if the harness refuses `--force-with-lease`, merge `origin/main` into the branch instead ([note](wiki/notes/restart-branch-force-push.md)).
- Spend: US$0 this run; US$5.81 today, of the US$15 daily cap.

## Queue (work top-down, one unit at a time)

1. **build**: band 1 in queue order, continuing the verbs after *produce* (`queue.py next` decides). Eight to twelve entries per run. Check each definition covers every example and collocation in its sense; reviewer-a caught five that did not this run.
2. **review**: one-round entries; the next oldest are the 2026-09-20 entries after *including-prep* (`python3` sort by `provenance.created`). When a run opens *anyone, anybody, anything*: check they agree with the new *someone/somebody/something* notes (those stay natural in questions expecting yes). Clear the signpost on any one-sense entry a review opens ([note](wiki/notes/one-sense-signposts.md); 41 left). reviewer-a confuses determiner and pronoun uses on function words ([note](wiki/notes/reviewer-noise.md)).
3. **closure**: about 924 closure-gap lemmas. Check each claimed row's part of speech first (three bogus rows this run). *pen* the animal enclosure is an unrelated homograph: queue it as `pen-n-2` when a run can, never as a sense of `pen-n`.
4. **lint**: next due in five runs (`next_mode.py` decides). Every lint: check each BACKLINK line `crossref --all --apply` prints; about one in five is wrong. A review that removes a cross-reference removes its mirror too, or lint re-creates it (a dry `crossref --all` does not show pending back-links). `reviewer-a` `pronunciation` precision is 0.33 over 105 decisions: re-measure; under 0.30 it is switched off.
5. When drafting or reviewing touches `break-v`: sense 4's definition becomes "begin suddenly", restriction moved to `explanation` (full pipeline). `boil-v` sense 1: move *(of a liquid)* to `explanation` likewise.
6. Tooling fixes still due (notes in `wiki/notes/`): `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`, `restart-branch-force-push`, `homograph-queue-and-inflection` (new: `lie-v-2` *tell an untruth* and `pen-n-2` need a hand claim and a check of the forms `inflect.py` writes); `crossref-first-sense-backlinks` partly fixed.
7. When drafting or reviewing touches `borrow-v` or `carry-v`: `borrow-v` sense 3 (subtraction) compares with `carry-v`, which has no arithmetic sense; add the sense or drop the compare (full pipeline).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `u`, `ɝ`, and `ɔ`; British keeps it. Reject reviewer-a's recurring "long vowel" objection (again on `heat-v`, 2026-09-26).
- *fire* and *hire* are transcribed with two syllables (`ˈfaɪ.ɚ`, `ˈhaɪ.ɚ`), verified by the panel and CMU; reject one-syllable objections.
- *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner.
- Idioms stay under their keyword entry whatever its part of speech (*at least*, *more or less*); a correlative pair (*either ... or*, *neither ... nor*) gets a conjunction entry.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Never put a wrong form in italics in prose; wrong forms live only in `incorrect`.
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
- `reviews/needs_curator.txt`: one prune-branch line (`claude/relaxed-bell-ngyr08`, fully merged); this session's branch `claude/relaxed-bell-iujuq0` can be pruned too once its last PR merges.
- The daily cap is now US$15, but `per_run_cap_usd` in `config/routine-config.json` is still US$1.25 (set when six runs shared US$5). Raise it if you want runs to use the larger budget; the scheduler leaves it alone.
- The harness refused a force push this session; if you want the Routine's branch restart to keep using `--force-with-lease`, allow it in the environment's permissions ([note](wiki/notes/restart-branch-force-push.md)).
- This session's reports: `journal/2026-09-26-7.md` to `-18.md`.
