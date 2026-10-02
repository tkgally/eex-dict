# lint_vocab blocks proper names in definitions

*Observed 2026-10-02; fix due a later run.*

`tools/lint_vocab.py --gate --changed` fails on any definition word that is neither in the defining vocabulary nor an entry headword. A proper name can be neither: the dictionary has no entries for people. On 2026-10-02 the closure row *christians* (from `church-n`) was drafted as `christian-n`, "a person who believes in Jesus Christ and follows the religion based on his life and what he taught"; the gate failed on **jesus** and **christ**, and no accurate definition avoids them (**Christianity** would need the same name). The entry was withdrawn before merge, the row set back to `pending` with a note, and `--queue` rows `jesus|n` and `christ|n` set to `deferred`. The `Christian` row also lost its capital in the family rows it queued (`christian|adj`, `christianity|n`), like the hyphen loss in [queue-hyphen-loss](queue-hyphen-loss.md).

A possible fix: a short, logged allowlist of proper names permitted in definitions (a closed vocabulary added by decision), which `--gate` accepts and `--queue` never queues. Words for other religions (*Muslim*, *Buddhist*, *Jewish*) will meet the same wall.
