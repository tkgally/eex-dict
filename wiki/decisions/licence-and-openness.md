# Licence and openness

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** Data CC0 1.0, code MIT, and the dictionary is to be as open and unencumbered as possible. The repository contains only the project's own work: **no data file under any other licence is vendored, copied, or derived from**, however permissive that licence is. That excludes frequency lists (wordfreq, Google Books Ngrams), word lists (the New General Service List, the Oxford lists), pronouncing dictionaries (CMU), WordNet, and Wiktionary as data. Such resources may be consulted at run time to check a fact, in a temporary location outside the repository, and the entry then records only the verdict. Copyrighted dictionaries are never consulted while drafting. A periodic originality check confirms that definitions, labels, and notes are not inadvertently reproducing another dictionary.

**Consequence.** `sources/` is markdown only and CI enforces it; tools download to `.tmp/`; `tools/originality_check.py` runs about every tenth Routine run.
