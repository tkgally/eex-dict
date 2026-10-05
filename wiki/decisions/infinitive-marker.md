# Infinitive *to*: the part of speech `inf`

*Ruled by the owner through `inbox/` on 2026-10-05 (open question 6; inbox file archived as `inbox/archive/20261005_owner_rulings.txt`). Implemented the same day, in the same pull request as the first entry that uses it, `to-inf`.*

**The problem.** **To** before the base form of a verb (*I want to go*) is not a preposition, and the closed list of parts of speech had no value for it, so the commonest use of one of the commonest words had no entry. `to-prep`'s usage note said so and pointed nowhere ([open question 6](../open-questions.md)).

**The ruling.** A new part-of-speech value, `inf`, label *infinitive marker*, in `schema/vocabularies.json`, and one entry, `to-inf`, built as a normal entry through the full pipeline. It covers *to* + base verb, *in order to*, *too ... to*, verbs such as *want*, *need*, *try* + *to*, and clause-final *to* (*I didn't want to*), with the learner errors *I want go* and *I must to go*. It cross-refers to `to-prep` for *look forward to* + *-ing*, where **to** is a preposition.

**What changed in the tools.** `tools/queue.py` orders `inf` with the function words, after `aux`. Slugs follow the usual rule (`to-inf`). Nothing else depends on the list.

**Scope.** `inf` is for infinitive **to** only. It is not a general *particle* value: the adverb parts of phrasal verbs stay inside `phrv` entries, and *not* stays an adverb.
