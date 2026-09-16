# Seed set: how it was drafted, and the doubts the drafters raised

*Founding session, 2026-09-16. A method record and a list of judgment calls for the owner's review and for later review runs. The entries themselves are the record; this page keeps what is not visible in them.*

## Method

Seventy-seven headwords were chosen to exercise every part of the design ([the review guide](../../journal/2026-09-16-seed-review-guide.md) lists them). Eight parallel drafting sessions of the founding model each took a coherent group (heavy verbs; light verbs; speech and perception verbs; be, have, do and modals; nouns with idioms; grammar-trap nouns and the heteronym pair; adjectives and adverbs; function words, phrasal verbs, affixes, abbreviations) and followed one written brief: the style guide, the schema, the fixture entry for shape, the defining vocabulary for definition wording, and the rule that nothing is drafted from a published dictionary. Every file passed `tools/validate.py` with no errors before it was handed over. The pipeline (inflections, pronunciation panel, two reviewers, adjudication) ran afterwards; its results are in the entries' provenance and in `reviews/`.

## Judgment calls the drafters flagged

- **Auxiliary and pronoun uses as senses.** *be*, *have*, *do* carry their auxiliary uses as senses with the explanation field; *one* carries its pronoun uses as senses of the number entry. The queue rows `be aux`, `have aux`, `do aux`, `one pron` were marked `duplicate` accordingly.
- **Keyword rule tensions.** *big deal* sits under *big* although the rule's first noun is *deal*; *very well* under *well*; *I'm afraid* and *I'm sorry* under the adjective; *don't get me wrong* under *get*; *make the most of* under *make*; *go without saying* under *go*. The rule in the style guide (section 9) is deterministic on purpose; a later review run may move a phrase when the noun's entry exists.
- **Sense splits the drafters were least sure of.** *run*: "run a red light" as a subsense of the hurry sense; "run in the family" under the road sense; *take*: "take a photo" under measure or record; *afraid* frightened versus worried; *good* "valid" as its own sense; *anyway* "despite that" versus "besides"; *because* + noun (the online joke use) as a very informal sense; *it* "Tag, you're it".
- **Region labels left off where the drafter was unsure**: *look after* (more British; Americans say *take care of*), *go* "work" of a machine, *get the bus*, *run for office* (labelled American).
- **Gradability codes with mixed senses**: *alone* and *quickly* have gradable and non-gradable senses; *sorry* is uncoded (a rules tool yields *sorrier*); *asleep* coded not gradable although "more asleep than awake" occurs. The inflection tool's rule: any sense with `not gradable` or `comparative with more` suppresses the -er forms.
- **Pronunciation conventions the brief did not state**: multi-word headwords carry a space between words in the IPA; function words give the strong form as the main transcription and the weak form as a variant, except *the*, whose main form is the weak ðə; British *because* is bɪˈkɒz.
- **Words outside the defining vocabulary used in definitions** (the soft rule; each deserves an entry): *advertisement*, *newspaper*, *exam*, *preposition*, *mess*, *enjoyable*, *lucky*. `tools/lint_vocab.py` queues them.
- **Headword capitalization**: *ASAP* and *TV* are written in capitals as headwords (slugs `asap-abbr`, `tv-abbr`); *asap* is a spelling variant.
- **Etymologies** were included only where both style-guide tests passed and the origin was checked in two open sources (*asleep*, *alone*, *ago*, *o'clock*); null everywhere else.
- **Inflections**: drafters left the placeholder; irregular verbs (*run*, *take*, *make*, *get*, *go*, *give up*, *pick up*) depend on `schema/inflection-exceptions.json`.
