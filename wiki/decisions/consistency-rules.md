# Consistency rules: phrasal-verb separability, promised entries, circular definitions, IPA format (2026-10-24)

*The owner's ruling B4 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)).*

## (i) Separable and inseparable phrasal verbs

- Two closed values are added to `grammar_codes` in `schema/vocabularies.json`: **`separable`** (the object may go between the verb and the particle, and a pronoun object must: *give it up*) and **`inseparable`** (the object always follows the whole verb: *look after her*). Both are values for phrasal-verb senses only.
- **Settled once:** a *verb + particle + preposition + object* phrasal verb (*look forward to*, *go back to*, *get on with*) is **transitive**, with the pattern `verb + preposition + object` and the code `inseparable`. Its object is the object of the whole verb. The rule is written in the [style guide](../style-guide.md), section 7.
- Under `CLAUDE.md` rule 3 the two values are added to the vocabulary in the same pull request as the first entry that uses them. That entry is a phrasal verb reviewed through the full pipeline, and that pull request also logs the decision line. The first review cycle after 2026-10-24 does it (`NEXT.md`).

## (ii) Promised entries

A prose field that promises an entry ("has its own entry", "a separate entry", "see the entry for") must name a word that has an entry or a live queue row. `tools/lint_vocab.py --promises` lists every promise that is broken (56 at commit 194fab1, for example the *my* interjection and `physical-n`). It reports only. A review cycle fixes each case by queueing the word or rewording the field through the pipeline.

## (iii) Circular definitions

`tools/lint_vocab.py --circular` lists the definitions that contain their own headword or one of its forms (about 260 at commit 194fab1, mostly harmless, such as *a flat note* defined with "flat"). It reports only. Review cycles judge each case.

## (iv) IPA format: one house form

- **The house form:** a stress mark stands at the start of its syllable and is itself the syllable break. A period never stands directly before or after a stress mark. So the house writes `prɪˈvɛnt` and `ˈdɪf.ər.ənt`, not `prɪ.ˈvɛnt`. Periods between unstressed syllables are written as the drafter chose. They are not required, because adding them would be a judgment about syllables that a script cannot make. Before 2026-10-24 about 290 strings had a period before a stress mark, against several thousand without one.
- **A narrow, owner-approved exception to `CLAUDE.md` rule 2.** A script, `tools/ipa_format.py`, may rewrite one thing in `pronunciation.american.ipa`, `pronunciation.british.ipa`, and `pronunciation.variants[].ipa`, and in the same fields under `senses[].pronunciation`: the position of `.` next to `ˈ` or `ˌ`. So that an owner's ruling still finds its transcription, it also reformats the copy of the string inside an `owner-ruling:` part of `checked_by`, a script-owned field. It must prove the change is only formatting: with every `.` removed, each new string must equal the old one character for character, so every segment and every stress mark stays where it was. The script refuses any other change. No other field and no other character may be touched.
- `tools/validate.py` warns when a string breaks the house form. `tools/pronounce_check.py` already ignored syllable periods when it compared votes. It now warns on a string not in the house form, compares owner rulings in the house form, and writes them in it.
- **Carried out 2026-10-24.** 292 transcriptions in 147 entries and 4 owner-ruling references. The script proved each change, and a second check over the whole diff agreed: 296 changed lines, each equal to the old line once its periods are removed.
- The NEXT.md fence "stress marks after a syllable break are house practice" is withdrawn by this ruling.
