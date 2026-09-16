# Style guide

*The house style of the TKG English Learner's Dictionary. Every session reads this before drafting or reviewing an entry. Cap 3,500 words. The charter is [PROJECT.md](../PROJECT.md); the file formats are in [conventions](conventions.md); the reasons behind the rules are in the [decision pages](index.md).*

## 1. Who we are writing for

An intermediate learner (roughly B1) must be able to read every definition. An advanced learner (C2) must find the entry complete: every current sense, the grammar, the collocations, the traps. We get both by keeping definitions plain and putting the depth in the structure around them, never by making the definition harder.

## 2. Definitions

**Phrasal, not sentential.** A definition is a phrase that can replace the word in a sentence: a noun is defined by a noun phrase (*a business that keeps and lends money*), a verb by a verb phrase in the base form (*to move quickly on foot*, written without *to*: *move quickly on foot*), an adjective by an adjective phrase (*having a lot of money*), an adverb by an adverb phrase or *in a way that* (*in a way that shows respect*).

**Present tense, general truth.** *A bank is...* never appears; the definition itself is the predicate.

**No circularity.** The headword, its inflections, and its close derivatives do not appear in its own definition (*happiness*: not *the state of being happy* when *happy* is itself defined through *happiness*; define the base word in plain terms and let the derivative point to it).

**No padding.** Never *used to describe*, *a term for*, *the act of*, *refers to*, *is when*. Say the thing: not *used to describe a person who talks a lot* but *talking a lot*.

**Countable nouns take an article** in the definition (*a place where...*); uncountable nouns take none (*money that...*). Verbs are defined with their argument slots spelled out with *someone* and *something*: *to give something to someone so that they can use it for a time* (written *give something to someone so that they can use it for a time*).

**Defining-vocabulary discipline.** Write definitions from `schema/defining-vocabulary.txt`. The rule is soft: a word outside the list may be used only when its entry exists, and `tools/lint_vocab.py` reports every violation and queues the missing entry. Prefer the plain word even when a rarer one is more exact; put the exact word in the explanation or a synonym cross-reference. The first sense of a defining-vocabulary word itself is not held to the list: *water* may be defined with *liquid* even if *liquid* comes later.

**Length.** One line for most senses. A definition that needs a second clause of explanation is a sign that an explanation field is needed.

## 3. The explanation field

`explanation` is plain prose, one to three sentences, used only when a phrasal definition cannot do the job: function words (*the*, *of*, *however*), discourse markers (*well*, *anyway*), modal and auxiliary verbs, affixes, and words whose meaning is easy but whose use is hard (*actually*, *quite*). It says how and when the word is used, not what it means in other words. When both fields exist the definition still stands on its own, even if it is bare (*the*: *used before a noun to show which one is meant*, with the explanation carrying the detail). Leave `explanation` null everywhere else.

## 4. Senses

**The splitting principle.** Make a new sense only when learners need a different **definition**, different **grammar** (countability, transitivity, patterns), a different **collocation set**, or a different **translation** in most languages. A metaphorical extension that any reader would get from the first sense is not a new sense; a use that a learner would translate with a different word is. When in doubt, do not split: put the extension in an example with a note.

**Sub-senses** (`a`, `b`) hold variations that share the definition's core but differ in one of the four tests in a minor way (*bank* of a river versus *bank* of snow).

**Ordering.** Most useful first: the sense a learner is most likely to meet and need. Not historical order, not "literal first". The core meaning that the other senses depend on usually comes first anyway.

**Signposts.** Every sense of an entry with two or more senses carries a `signpost`: one to three words in plain English that let the reader pick the sense from a list (*for money*, *of a river*, *turn or lean*). Lowercase, no period. A one-sense entry has `signpost: null`.

**Core idea.** An entry with three or more senses opens with `core_idea`: one sentence, in the defining vocabulary, that says what the senses have in common (*A bank is a place or a raised edge where something is kept or piled up*). It is the one place where a sentence form is used. It is null for one-sense entries and optional for two-sense entries.

## 5. Examples

Two to four per sense (one to four per sub-sense, one to three per phrase). Each example earns its place by showing something the definition cannot: a typical collocation, a grammar pattern (mark it in `pattern` with the verb-pattern label), a typical subject or object, a register. Progress from simple to fuller.

Rules:

- **No checkable real-world facts.** No dates, statistics, named events, historical claims, science claims, prices, populations, records. *The river flooded last spring* is fine; *The river flooded in 1953* is not.
- **Settings culturally neutral.** Homes, work, school, shops, weather, travel, family, friends. Nothing that assumes one country's institutions (no *the DMV*, no *A levels*).
- **Names** only when a sentence needs one, and only from this list: Kim, Mari, Sam, Ana, Lee, Omar, Yuki, Ravi, Sara. No surnames, no brand names, no product names, no real companies, no place names smaller than a continent except in the entry for that kind of word.
- **Natural.** Examples are sentences a person would say or write, in American spelling, ending in a period, question mark, or exclamation mark. Avoid the headword's rarer collocates; show the common ones.
- **The `note`** on an example is for a short gloss of what the example shows (*passive*, *with a negative*), not for a translation or a paraphrase. Usually null.
- **The `pattern`** on an example names the verb pattern it illustrates, from the closed list, or is null.

## 6. Grammar

Every sense carries `grammar`: `countability` for nouns (else null), `transitivity` for verbs and phrasal verbs (else null), `codes` from the grammar codes, `patterns` from the verb patterns, most typical first, at most five. Codes and patterns are chosen by the drafter and reviewed; the site shows the spelled-out label with its short code beside it. In prose, everything is spelled out: *someone*, *something*, *for example*, *that is*, *and so on*, *usually*, *especially*; never `sb`, `sth`, `e.g.`, `i.e.`, `etc.`, `usu.`, `esp.`, `vs.`, `cf.`, `approx.`, `NB`. The validator rejects them.

Gradability is the drafter's call, recorded as a code (`not gradable`, `comparative with more`); `tools/inflect.py` then generates only the forms the codes allow. Never write inflections by hand.

## 7. Labels

Labels come from the five closed sets ([usage-labels](decisions/usage-labels.md)). Entry-level `labels` apply to every sense; sense-level labels apply to that sense only; do not repeat an entry-level label at sense level. A label is used when the word would be out of place without it: `informal` when the word would jar in a report, `technical` when only specialists use it, a domain only when the word belongs to the field. `vulgar` and `offensive` are never omitted where they apply. Region labels say where a word is *mainly* used; a word used everywhere gets none. Variants (`variants[]`) record a British spelling or form with its region; the headword and every prose field stay American.

## 8. The boxes

**Collocations** (`collocations[]` per sense): two to six items per type, only types that are genuinely typical, in the order a learner would meet them. Items are short phrases with the headword in them (*open a bank account*), not sentences. A verb collocation shows the object slot with *something* or *someone* only when the phrase is unclear without it.

**Word family** (`word_family[]`, entry level): every derived or related word that has or should have an entry, as a slug (`banker-n`, `banking-n`). Words whose meaning is predictable from the base (*bankable*) may be listed without an entry; the site shows them unlinked. Symmetric: `tools/crossref.py` adds the back-link.

**Synonyms, antonyms, compare** (per sense): slugs of entries that exist or should exist. `compare` is for words learners confuse with this one (*borrow* / *lend*, *say* / *tell*); a `note` may say the difference in a few words. Symmetric.

**Synonym discrimination** (`synonym_discrimination`, entry level): for the two to five near-synonyms a learner must choose between, one short paragraph that gives the rule of choice with one example each. Only where the choice is a real problem (*big* / *large* / *great*; *begin* / *start*; *speak* / *talk*). Otherwise null.

**Usage note** (`usage_note`): one short paragraph on a point of use that does not fit elsewhere: a politeness trap, a grammatical restriction that needs prose, a shift in meaning between varieties. Otherwise null.

**Learner errors** (`learner_errors[]`): the one to three mistakes learners of many backgrounds actually make with this word, as an `incorrect` phrase, the `correct` phrase, and a one-line `note` on why. Mark the wrong form only in `incorrect`; never write an asterisk in a prose field. Only where the error is common; most entries have none.

**See also** (`see_also[]`): related entries worth reading that are not synonyms or family (*bank* to *account*). Sparingly.

## 9. Phrases

Idioms and fixed phrases live in `phrases[]` of the keyword entry: the first noun in the phrase, else the first verb, else the first content word (*break the bank* under *bank*; *make up one's mind* under *mind*; *by and large* under *large*). A phrase gets a phrasal definition, an explanation only if it needs one, its own labels, and one to three examples. Write the phrase with *someone* and *something* in the slots (*give someone a hand*); the `sub_id` is the phrase text slugified (`give-someone-a-hand`). Phrasal verbs are not phrases: they are entries (`give-up-phrv`).

## 10. Pronunciation, inflections, variants

The drafter writes `pronunciation.american.ipa` and `pronunciation.british.ipa` with the symbol set in `tools/pronounce_check.py` (primary stress `ˈ`, secondary `ˌ`, syllable breaks with a period, no slashes), and `source: "model:<its slug>"`. A heteronym puts the sense-specific pronunciation in `senses[].pronunciation`. `checked_by` and `status` are written by the checker, never by hand. Prefixes, suffixes, combining forms, and abbreviations may leave both transcriptions null when no fixed pronunciation exists. Inflections come from `tools/inflect.py`; the drafter only supplies the gradability codes and, for a verb with an unpredictable form, a line in `schema/inflection-exceptions.json` in the same pull request.

## 11. Etymology

Include an `etymology` only when both tests pass: (1) the origin was checked in two open sources during verification (name them in `sources_consulted`; nothing is copied from them), and (2) knowing it helps a learner use the word today: a Greek or Latin root that recurs (*tele-*, *-graph*), a transparent compound, a borrowing that explains an odd spelling or pronunciation (*ballet*, *yacht*) or a sense (*salary*). Two sentences at most, in the defining vocabulary. Otherwise `null`. Folk etymologies and disputed origins are omitted, not hedged.

## 12. Taboo and offensive vocabulary

Vulgar words for sex, the body, and body functions are included, defined plainly, labelled `vulgar` (and `offensive` when they insult). Slurs against groups are not included for now. If you decline to write an entry or a field, do not argue with yourself: record it (`declined` in the queue with a one-line reason, or `declined-in-part` in `provenance.flags` with the field named in `provenance.notes`) and move on. Examples for vulgar words are still natural and still neutral in setting.

## 13. Adaptation notes

Five kinds, each at most 60 words, language-neutral (never *in Japanese...*), null when nothing needs saying. They exist so that a translator adapting the entry into any language knows where the traps are.

- **semantic**: how the senses split or merge in other languages. *"bank": the money sense and the river sense are unrelated words in most languages; do not translate with one word.* *"brother": many languages must choose older or younger; English does not.*
- **grammar**: a countability, argument-structure, tense, or preposition trap. *"information" is uncountable: no plural, no "an information".* *"explain" takes "to someone", never a bare indirect object: "explain it to me", not "explain me it".*
- **culture**: background a reader outside the English-speaking world needs. *"bank holiday" is a public holiday, not a day banks are open.* *A "pub" serves food and families as well as drink.*
- **false_friends**: internationalisms that mean something else. *"actually" means "in fact", not "currently".* *"eventually" means "in the end", not "possibly".*
- **pronunciation**: a sound, stress, or spelling trap for learners in general. *"record": stress on the first syllable for the noun, the second for the verb.* *"comfortable" has three syllables in American English, the second "o" is silent.*

## 14. Originality

Draft from your own knowledge and this guide. Never open a commercial or copyrighted dictionary while drafting, and never reproduce a definition, example, or note you remember from one. Open resources are consulted only afterwards, to check a fact, and nothing is copied from them. The periodic originality check searches the web for our definitions phrase by phrase; a definition that matches a published one is rewritten. A definition that is short and plain will often resemble others by necessity (*a young dog*); that is not copying. A distinctive turn of phrase or an unusual example that matches is.

## 15. Before you submit an entry

Read it as the learner: can a B1 reader follow every definition? Read it as the reviewer: is every fact in every note true? Then run the pipeline in `CLAUDE.md`. The three model entries in section 16 show what a finished entry looks like.

## 16. Model entries

Three finished entries from the seed set, each the model for its kind. Read the JSON, not just this summary.

**A polysemous verb: [run](../entries/ru/run-v.json).** Fourteen senses, each with a signpost (*move fast*, *hurry or escape*, *manage*, *work or operate*, *buses and trains*, *of liquid*...), opened by a core idea that names what they share: movement forward that does not stop. The first sense is the physical one a learner meets first; the extensions follow in order of use, with subsenses for variations that share a definition (*run a red light* under *hurry or escape*). Every sense carries its transitivity and its patterns (*verb + object* for *run a restaurant*, *verb + adjective* for *run low*), examples that show those patterns, and collocations by type. Phrases hold only the idioms whose keyword is *run* (*run for it*, *up and running*); phrasal verbs (*run out*, *run into*) are entries of their own and appear under see also. The word family lists the derived entries (*runner*, *running*, *runaway*); the synonym discrimination settles *run* / *jog* / *sprint*; the learner errors are the ones learners of many languages make (*I have ran*, *runs during two hours*); the adaptation notes tell a translator where the senses split.

**A noun with idioms: [hand](../entries/ha/hand-n.json).** Nine senses from the body part outward (*help*, *control or care*, *of a clock*, *worker*, *handwriting*...), each with its countability and codes (*usually singular* for *a hand* meaning help, *usually plural* for *in the hands of*), and thirty-two phrases under the keyword rule (*give someone a hand*, *on the other hand*, *by hand*, *get out of hand*), each phrase with its own definition, labels, and one to three examples, and an explanation only where a phrase needs one. Note what is not here: *off the top of your head* is under *head*, *know something like the back of your hand* is under *back*, because the keyword is the first noun.

**A function word: [the](../entries/th/the-det.json).** Seven senses that are really seven uses (*particular one*, *only one*, *whole kind*, *best, first, only*, *groups of people*, *the more the better*, *with names*), each with a short phrasal definition that stands on its own and an explanation field that carries what a learner actually needs: when the use occurs, what it contrasts with, what a learner from a language without articles gets wrong. Examples show the use in the plainest possible sentence. The pronunciation notes give the weak forms; the learner errors (*I love the nature*) and the adaptation notes do the work that a translation could not.
