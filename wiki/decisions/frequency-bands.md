# Frequency bands and the defining-vocabulary flag

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** An editorial frequency band per headword, 1 to 5, estimated by several models and settled by the session, shown on the site in words (`very common`, `common`, `fairly common`, `less common`, `rare`) with a note that bands are the dictionary's own estimates, plus a defining-vocabulary flag. **No CEFR levels.**

**Consequence.** `frequency.band` and `frequency.defining_vocabulary` are script-owned, stamped from `headwords/queue.tsv` and `schema/defining-vocabulary.txt` by `tools/queue.py stamp`; `frequency.basis` is always `editorial`.
