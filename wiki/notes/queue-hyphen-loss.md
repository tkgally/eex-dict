# Queue rows lose hyphens

*Observed 2026-10-01. Fixed 2026-10-24 under the owner's ruling C3 ([cross-reference-display](../decisions/cross-reference-display.md)): `queue.py add` matches an existing row by slug, `sync` and `stamp` read the real row, `crossref.py --queue` and the site take the display form from a queue row or the referring entry's prose (`eexlib.guess_display_form`), and `queue.py repair-forms --apply` fixed 26 rows (12 lossy twins marked duplicate; *-ible*, *-ee*, *-est*, *-th*, *T-shirt*, *well-known* and eight more renamed).*

When `lint_vocab.py --queue` or `crossref.py --queue` queues a target named only by its slug (a `word_family` or cross-reference entry), it turns the slug back into a headword by replacing every hyphen with a space. A hyphenated word therefore arrives as a new, wrong row: `brother-in-law-n` (from `brother-n`'s word family, 2026-10-01) was queued as `brother in law`, beside the correct `brother-in-law` row that already existed; `good looking|adj` (2026-09-26) is the same fault.

Handled by hand so far: the wrong row is marked `duplicate` when a correct one exists, or drafted with the hyphen. A possible fix is to look up an existing row whose slug matches before adding one, and to keep the hyphen when the slug is ambiguous, recording it in the row's note.

Recurred 2026-10-12 on `part-time-adj`: the old wrong row *part time* (adj, band 3) was marked `done` by `queue.py sync` instead of the right row, `crossref.py --queue` added *part time* (adv), and `queue.py stamp` still writes band 3 from the wrong row although the right row is band 1 (a validator warning). Rows fixed by hand; the stamped band stays wrong until the tool is fixed.

Recurred 2026-10-22 on suffixes: cross-references queued *ic*, *ing*, *ity*, *less* beside *-ic*, *-ing*, *-ity*, *-less*; `sync` left the real rows pending and `stamp` wrote band 3. Fixed by hand (wrong rows `duplicate`, band 1 forced). *ible*, *ee*, *est* have only hyphenless rows.

**2026-10-23.** Periods are lost the same way: rows `am`, `pm` (for *a.m.*, *p.m.*) and `sion` (for *-sion*). `queue.py sync` and `stamp` then read the wrong row: *p.m.* was stamped band 3, and *-less* and *a.m.* were not marked done until set by hand.
