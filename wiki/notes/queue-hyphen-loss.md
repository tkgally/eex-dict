# Queue rows lose hyphens

*Observed 2026-10-01; fix due a later run.*

When `lint_vocab.py --queue` or `crossref.py --queue` queues a target named only by its slug (a `word_family` or cross-reference entry), it turns the slug back into a headword by replacing every hyphen with a space. A hyphenated word therefore arrives as a new, wrong row: `brother-in-law-n` (from `brother-n`'s word family, 2026-10-01) was queued as `brother in law`, beside the correct `brother-in-law` row that already existed; `good looking|adj` (2026-09-26) is the same fault.

Handled by hand so far: the wrong row is marked `duplicate` when a correct one exists, or drafted with the hyphen. A possible fix is to look up an existing row whose slug matches before adding one, and to keep the hyphen when the slug is ambiguous, recording it in the row's note.
