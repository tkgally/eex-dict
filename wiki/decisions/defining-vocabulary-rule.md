# The defining-vocabulary rule

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** A soft rule. A definition may use a word outside the defining vocabulary (`schema/defining-vocabulary.txt`) only if that word's entry exists and is linked; CI flags violations. Examples and notes are looser. The first sense of basic words is not held to the strict list.

**Consequence.** `tools/lint_vocab.py` lemmatizes definition text with the inflection tables the entries carry, checks each lemma against the defining vocabulary and the set of existing entries, and writes words with no entry to the queue as `closure` candidates. `--gate` fails a pull request that adds a new violation in a definition; examples and notes produce warnings. Every violation therefore becomes a queued headword rather than a blocked entry. **Refinement (session, 2026-09-16):** a transparent derivative of a listed word (*politely*, *unkind*, *successful*, *enjoyable*, *carelessly*) counts as listed; the rule and the affix list are in [defining-vocabulary](defining-vocabulary.md).
