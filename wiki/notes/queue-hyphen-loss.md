# Queue rows lose hyphens

*Observed 2026-10-01; fix due a later run.*

When `lint_vocab.py --queue` or `crossref.py --queue` queues a target named only by its slug (a `word_family` or cross-reference entry), it turns the slug back into a headword by replacing every hyphen with a space. A hyphenated word therefore arrives as a new, wrong row: `brother-in-law-n` (from `brother-n`'s word family, 2026-10-01) was queued as `brother in law`, beside the correct `brother-in-law` row that already existed; `good looking|adj` (2026-09-26) is the same fault.

Handled by hand so far: the wrong row is marked `duplicate` when a correct one exists, or drafted with the hyphen. A possible fix is to look up an existing row whose slug matches before adding one, and to keep the hyphen when the slug is ambiguous, recording it in the row's note.

Recurred 2026-10-12 on `part-time-adj`: the old wrong row *part time* (adj, band 3) was marked `done` by `queue.py sync` instead of the right row, `crossref.py --queue` added *part time* (adv), and `queue.py stamp` still writes band 3 from the wrong row although the right row is band 1 (a validator warning). Rows fixed by hand; the stamped band stays wrong until the tool is fixed.

Recurred 2026-10-22 on suffixes: cross-references queued *ic*, *ing*, *ity*, *less* beside *-ic*, *-ing*, *-ity*, *-less*; `sync` left the real rows pending and `stamp` wrote band 3. Fixed by hand (wrong rows `duplicate`, band 1 forced). *ible*, *ee*, *est* have only hyphenless rows.
