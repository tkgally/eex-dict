# House rulings for the reviewers

*Read by `tools/review_panel.py` and sent to both reviewers with every entry (the owner's ruling E1 of 2026-10-24, `wiki/decisions/reviewer-house-rules.md`). Each line is a settled question: an objection to it is not an issue. Sources: the fences in `NEXT.md` and `wiki/style-guide.md`. Change a line here when the rule it names changes, and only then.*

## Settled questions: do not raise them

1. American IPA drops the length mark on i, u, ɝ, ɔ, ɑ; British keeps it. A "long vowel" objection to American IPA is not an issue.
2. *could*, *should*, *would*, *good* rhyme (ʊd). *fire* and *hire* have two syllables (ˈfaɪ.ɚ).
3. In IPA the stress mark opens its syllable and is itself the syllable break; no period stands beside it.
4. Particle stress on a two-word phrasal verb (*give ˈup*) is house practice.
5. A wh-word in a reported question (*I don't know when it starts*) belongs to the adverb entry, not the conjunction; *whether* and *if* stay conjunctions.
6. *X of* before a noun phrase (*each of us*, *neither of them*) is the pronoun entry, never the determiner. *Which* before a noun is the determiner, relative uses included.
7. Idioms stay under their keyword entry (the first noun, else the first verb, else the first content word), whatever its part of speech: *at least* under *least*, *more or less* under *more*, *catch fire* under *fire*. Do not ask to move them.
8. A correlative pair (*either ... or*, *neither ... nor*) has a conjunction entry. *I don't like either tea or coffee* is standard.
9. A claim about a word's origin belongs only in `etymology`, never in an adaptation note.
10. A preposition with a noun-phrase object stays a preposition (*above ours*, *he's above that*); *during* can mean *all through*. `out-prep` holds the *out of* senses.
11. Existential *there* (*there is*) is a sense of `there-adv`. Relative *that* is a pronoun; `that-conj` holds only the clause after *say*/*think* and the result after *so*/*such*.
12. *used to ...* / *used before ...* definitions are house style for function words, discourse markers, and interjections. Infinitive *to* has its own entry, `to-inf`.
13. A verb + preposition pattern covered by the verb's senses (*belong to*, *care for*, *look for*) is not a phrasal-verb entry. *Mix up* is a phrasal verb.
14. A region label means *mainly used there*. That a word also occurs elsewhere is not an issue.
15. A subject restriction (*of food*, *of a train*) goes in `explanation`, never as a prefix in the definition.
16. A participle phrase (*badly damaged*) is a `phrase` collocation (*be well hidden*), never "adverb + verb". Verb + adverb pairs such as *fall over* may stay collocations.
17. `core_idea` is a sentence by house style. A not-continuous code stays where a learner-error note says "not normally" (*need*, *own*).
18. Adaptation notes: an opening quoted headword is allowed; words named later take double asterisks and illustrations single ones. "Some languages" and "many languages" are language-neutral.
19. *give someone something* and *give her the chance* are two-object patterns. *I'm hating this* is possible informally.
20. Imperative *look*, *listen* used to get attention ("Look, I'm sorry") stay verb senses. *say hello*, *say goodbye* stay in the interjection entries.
21. Clippings (*ad*, *app*, *info*) are nouns, not abbreviations. Affix definitions in the form "added to ..." are house style.
22. Passive *be convinced* and *where X is concerned* are verb uses, not adjective entries. Adverbs before adjectives (*near impossible*, *the next best*) are not adjective uses.
23. *the former*, *the latter*, *the following* standing alone are treated as nouns (working assumption, `wiki/open-questions.md`).
24. *axe* is the headword with *ax* as an American variant.
25. A word in `word_family` or a cross-reference may name an entry that does not exist yet. That is how new words are queued, and it is not an issue.

## Notes discipline (style guide, notes rules of 2026-10-24)

- A note field stays null unless it names what a learner or translator would get wrong without it. An empty note field is never an issue; a note that only restates another field is.
- One fact lives in one field. Flag a fact stated twice, and above all a fact stated two different ways.
- Learner errors must be errors learners really make: flag invented misspellings, regularized forms (*weller*, *flatted*), and adjective-for-adverb swaps added to fill the field.
- An adaptation note must name a specific trap. A generic "translate each sense separately" note is an issue.
