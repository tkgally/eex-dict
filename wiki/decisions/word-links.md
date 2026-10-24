# Word links: every word links, except a closed list (2026-10-24)

*The owner's own ruling C4 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)). It replaces the options the assessment offered.*

**What is linked.** Every word in definitions, explanations, examples, and notes that has an entry stays linked, as `tools/link_words.py` does now, except the words on the closed list below, in any capitalization.

**Why so much stays linked.** A learner may know a basic word but not all its forms and senses, so even defining-vocabulary words stay linked.

**The list** holds common words that have no inflected forms and no other part of speech in common use, plus the articles and the core prepositions and conjunctions the owner named. It is the closed vocabulary `no_link_words` in `schema/vocabularies.json`. A word is added or removed only by an owner ruling:

> a, an, the, about, against, among, at, between, by, during, for, from, in, into, of, on, onto, to, toward, towards, upon, with, within, without, and, or, but, nor, if, because, than, whether, although, unless, it, its, not, also, very

(39 words.)

**Unchanged.** The words' own entries and pages exist and are unchanged. Search finds them, and they may still be linked where a cross-reference names them, or where an author forces a link with `[[slug|text]]`.

**Keyboard.** Word links are taken out of the Tab order (`tabindex="-1"`), so a keyboard user tabs through the page's controls and cross-references, not through every word. Hover and tap previews are unchanged.

**Site text.** The site text that said every word is a link now names the exceptions.
