# The defining vocabulary and the frequency bands: method and counts

*Built by the founding session on 2026-09-16 under the owner's ruling in [headword-selection](headword-selection.md): no external frequency data and no external word list, for anything. The list is closed; a change is a logged decision.*

## Method

1. **Three models, three labs, independent.** The roles `wordlist-1` (OpenAI), `wordlist-2` (Google), and `wordlist-3` (DeepSeek) in `config/models.md`, each told to answer from its own judgment of English as used today and not to reproduce any published list. Reasoning was set to low effort for the first two and switched off for the third, which otherwise spends its whole output budget on hidden reasoning (`experiments/defining-vocabulary-v1/harvest.py`).
2. **Chunks by semantic field and part of speech.** Thirty-seven chunks (`experiments/defining-vocabulary-v1/fields.json`): twenty-eight content fields (people and family, the body, food, the home, nature, materials, size and quantity, numbers and time, movement, work and money, thinking, feelings, society, and so on) and nine function-word and metalanguage chunks (determiners and pronouns, prepositions and conjunctions, adverbs, modal and light verbs, phrasal verbs, affixes, the words needed to write definitions, interjections, abbreviations). Each chunk asked for up to a stated number of lemmas, the most basic first. Every raw reply is kept under `experiments/defining-vocabulary-v1/raw/propose/`.
3. **Intersection as the core.** A lemma proposed by at least two of the three models, in any chunk and any part of speech, is in. Result: 1,671 lemmas (941 proposed by all three, 731 by two, after mapping British spellings to the American headword).
4. **Adjudication of the disagreements.** The 927 lemmas proposed by one model only were read one by one by the session and accepted when general enough to serve in definitions (682 accepted: for example *machine*, *laugh*, *average*, *temporary*, *these*, *those*, *an*, *ought*, *myself*); the rest (specific, technical, or easily defined items such as *compost*, *diabetes*, *pollinate*, *lotion*, and abbreviations such as *blvd*) were left for the band passes. The accepted list is in `experiments/defining-vocabulary-v1/adjudicate.py`.
5. **Gap filling.** A checklist of about 190 function words, light verbs, and defining metalanguage (*someone*, *something*, *particular*, *cause*, *become*, *used*) was compared with the result; only *used to* was missing.
6. **Abbreviations** proposed by two or more models (28: *a.m.*, *kg*, *tv*, ...) are headwords in band 1 but not members of the defining vocabulary, since a definition never uses them.

## Result

- **`schema/defining-vocabulary.txt`: 2,326 lemmas**, one per line, sorted. Multi-word lemmas are the basic phrasal verbs (*give up*, *look after*) and a few fixed phrases (*for example*, *of course*).
- **Band-1 queue rows: 2,606** (`headwords/queue.tsv`, source `defining`), one per lemma and part of speech: a part of speech proposed by two or more models, or the single one proposed. By part of speech: 1,161 nouns, 454 verbs, 387 adjectives, 173 adverbs, 117 phrasal verbs, 55 prepositions, 51 pronouns, 41 determiners, 28 suffixes, 28 abbreviations, 24 interjections, 24 conjunctions, 21 prefixes, 16 numbers, 12 modal verbs, 7 phrases, 6 combining forms, 3 auxiliaries.
- **Milestone 1** is therefore about 2,600 entries, not 2,326: a defining-vocabulary word with two common parts of speech needs two entries.

## Bands 2 and 3

The same three models were asked, chunk by chunk, for the next most useful words beyond the basic 2,500 (`raw/expand/`), and every candidate proposed by at least two of them, together with every single-vote proposal from the first pass, was then banded 1 to 5 by each model (`raw/band/`); the lower median of the three votes is the band. Candidates with a median band of 2 or 3 enter the queue with source `band`; a candidate the panel put in band 1 that is not in the defining vocabulary is queued as band 1 with source `band`. Bands 4 and 5 are not queued now; those words arrive through closure. The counts are in the section below once the passes have run.

## Band-pass counts (2026-09-16)

- Expansion pass: 6,741 distinct candidates proposed; 2,059 by two or more models. Banding pass: 4,347 items banded by all three models (the 2,059 plus every first-pass proposal); the three agreed exactly on 1,739 and were within one band on all but 80.
- The panel's view of the defining vocabulary itself: of its lemma-and-part-of-speech rows, 1,206 were placed in band 1, 1,340 in band 2, 261 in band 3, and 21 in bands 4 and 5 (mostly secondary parts of speech such as *hide* as a noun, and affixes). The defining vocabulary is the set of words needed to define, not the 2,326 most frequent words, so this spread is expected; the 228 defining rows whose part of speech the panel put in band 3 or lower keep source `defining` but carry the panel's band, so that milestone 1 works the main parts of speech first.
- Queue after the passes: **3,900 rows**: 2,606 with source `defining` and 1,294 with source `band` (23 in band 1, 490 in band 2, 783 in band 3, 18 in band 4 and 1 in band 5 from re-banded secondary parts of speech). British spellings proposed by the panel (*colour*, *centre*, *tyre*) were folded into their American headwords. The 4,682 single-vote expansion candidates were not banded; they, and everything in bands 4 and 5, arrive through closure or a later expansion pass.

## Additions by the founding session (2026-09-16), a logged decision

The first entries showed two gaps the harvest could not have found: the dictionary's own metalanguage, and transparent derivatives.

- **Metalanguage added (14 lemmas):** *adverb, clause, phrase, participle, preposition, infinitive, auxiliary, determiner, conjunction, syllable, vowel, consonant, countable, uncountable*. Explanations of function words and pronunciation notes cannot be written without them, and a dictionary that explains grammar must define its own terms.
- **Basic words the panel missed (4):** *receive, request, phone, lovely*, each used in the seed set's definitions and plainly basic.
- **Transparent derivatives count as listed** ([defining-vocabulary-rule](defining-vocabulary-rule.md)): a word formed from a listed word by *un-* or *non-* or by *-ly, -ness, -ful, -less, -able, -ish, -ment, -ous, -ed, -ing, -er, -est* (up to two suffixes, spelling changes reversed) is treated as in the vocabulary by `tools/lint_vocab.py`, since a learner who knows the base and the affix reads it without help (the affixes themselves are headwords). It still has no entry of its own unless its meaning is not predictable, per [what-counts-as-a-headword](what-counts-as-a-headword.md).

- **Gap fill (28 lemmas):** the number words *eleven* to *nineteen*, the tens *twenty* to *ninety*, *billion*, the ordinals *fourth* to *tenth*, and *thank*, *gentle*, and the suffixes *-est* and *-s*, all missed by the harvest's chunking.

- **Words the seed set's definitions needed (22):** *passive, base, quote, series, ordinary, exam, flag, bar, mess, lucky, chase, succeed, organize, frighten, hint, extend, responsible, annoy, newspaper, inch, centimeter, clap*: each plainly basic, each proposed by only one model in the harvest or by none, added rather than reworded around.

The list now holds **2394 lemmas**.
