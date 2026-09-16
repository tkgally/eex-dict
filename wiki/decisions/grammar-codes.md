# Grammar codes

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** A closed code set for countability, transitivity, verb patterns, gradability, adjective position, and number restrictions. On the site both the spelled-out label and the code are visible, the code linking to the grammar key page. In entries all terms are spelled out; no abbreviations ("someone", "something", "for example", never "sb", "sth", "e.g."). Inflections are generated programmatically from rules plus an exceptions table.

**Session's design (2026-09-16).** Stored values are the spelled-out labels (`"countable"`, `"verb + object"`); `schema/vocabularies.json` gives each its short code (`C`, `V + obj`). Twenty-nine verb patterns, ten adjective, noun, and adverb codes. The model decides gradability (`not gradable`, `comparative with more`); `tools/inflect.py` reads those codes and generates only the forms the codes allow.
