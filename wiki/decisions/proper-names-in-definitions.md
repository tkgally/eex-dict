# Proper names in definitions

*Ruled by the owner through `inbox/` on 2026-10-05 (open question 7; inbox file archived as `inbox/archive/20261005_owner_rulings.txt`). Implemented the same day in `schema/vocabularies.json` and `tools/lint_vocab.py`.*

**The problem.** An accurate definition of *Christian* needs *Jesus Christ*; *Muslim*, *Buddhist*, *Islam*, and *Judaism* meet the same wall. The defining-vocabulary gate (`tools/lint_vocab.py --gate`) accepts only words on the defining list and entry headwords, and the dictionary has no entries for people, so such a definition could never pass ([note](../notes/lint-vocab-proper-names.md)).

**The ruling.** A short, closed list of proper names may appear in definitions. It is the vocabulary `proper_names` in `schema/vocabularies.json`, starting with three names: **Jesus Christ**, **Muhammad**, **Buddha**. A name is added only when an entry needs it, as a logged decision in the same pull request as that entry, like any other closed-vocabulary value.

**Added.** **Moses**, 2026-10-05, for `judaism-n`: the plain accurate definition (*the religion of the Jewish people*) needs a word with no entry, and the alternative names the law that, Jews believe, God gave to Moses.

**What the tools do.** `tools/lint_vocab.py` reads the list and accepts each word of a listed name wherever it meets it in prose, so `--gate` passes a definition that uses one, and `--queue` never queues one as a headword. A name not on the list is still reported. The names are not headwords and get no entries.

**Writing with them.** Use a listed name only where no plain wording is accurate (a religion and its followers, defined by the person it is named after or follows). Keep the definition neutral: what followers believe or follow, not whether it is true.
