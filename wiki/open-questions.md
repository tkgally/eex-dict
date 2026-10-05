# Open questions for the owner

*Each question carries the working assumption the project is using meanwhile (framework section 5). When an answer arrives through `inbox/`, record it here with the date and the files updated, and move the question to the Answered section.*

## Open

(none at present)

## Answered

*All seven were answered by the owner on 2026-10-05 (inbox file archived as `inbox/archive/20261005_owner_rulings.txt`).*

1. **Drafting model.** Drafting stays in-session; `drafter_via_openrouter` stays false. A standing ruling; nothing changed.
2. **Reviewer B tier.** Upgrade now: `reviewer-b` moves from the Flash-class model to the Pro-class candidate, re-verified against the OpenRouter model list on 2026-10-05; only the reviewer-b role changes (the pronunciation and word-list panels keep theirs). The daily cap stays US$15. Files: `config/models.md`; [reviewer-b-upgrade](decisions/reviewer-b-upgrade.md). The lint passes report reviewer-b's precision from then on.
3. **Milestone-1 order.** Queue order stands. A standing ruling; nothing changed.
4. **Auxiliary and pronoun uses.** Split them: new entries `be-aux`, `have-aux`, `do-aux` (and `one-pron`, which already exists since 2026-09-21), one per run in review mode, each through the full pipeline; the auxiliary senses move out of `be-v`, `have-v`, `do-v`, the remaining pronoun uses out of `one-num`, with cross-references both ways. The queue rows *be aux*, *have aux*, *do aux* were reset to `pending` on 2026-10-05. Queued in `NEXT.md`. `be-aux` done 2026-10-05 (12:44 run, cycle 3): the -ing tenses, the passive, and *be to* moved out of `be-v`.
5. **The look of the marks.** Bold and italic stay as they are. A standing ruling; nothing changed.
6. **Infinitive *to*.** Yes: a new part-of-speech value `inf` (infinitive marker), added as a logged decision in the same pull request as the first entry that uses it, `to-inf`: *to* + base verb, *in order to*, *too ... to*, *want/need/try to*, clause-final *to* (*I didn't want to*), and the learner errors *I want go*, *I must to go*; it cross-refers to `to-prep` for *look forward to* + *-ing*. The `NEXT.md` fence against it was removed 2026-10-05; `to-inf` was built the same day ([infinitive-marker](decisions/infinitive-marker.md)).
7. **Proper names in definitions.** Yes: a short closed list, `proper_names` in `schema/vocabularies.json` (Jesus Christ, Muhammad, Buddha; a name added only when an entry needs it); `tools/lint_vocab.py` accepts their words in definitions and never queues them. Files: [proper-names-in-definitions](decisions/proper-names-in-definitions.md), `tools/lint_vocab.py`, its test. *Christian*, *Christianity*, *Islam*, *Muslim*, *Judaism*, *Buddhism*, and *Buddhist* were built the same day; **Moses** was added to the list for *Judaism*.
