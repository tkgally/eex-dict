# Cross-references: back-links, missing targets, and display forms (2026-10-24)

*The owner's rulings C1, C2, and C3 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)).*

## C1. Back-links

- **No fallback.** `tools/crossref.py` puts a mirror link on a sense of the target only when one sense clearly matches: the target has only one sense, or exactly one sense already names the source under another relation, or exactly one sense uses the source headword in its definition or explanation. The fallback is removed. It used to put the link on the sense with the most shared definition words, or else on the first sense. When no sense clearly matches, the tool prints the pair (`NO-SENSE`) and writes nothing; a review cycle decides. This replaces the partial fix of [crossref-first-sense-backlinks](../notes/crossref-first-sense-backlinks.md). Word-family back-links are entry-level and are not affected.
- **Ruled-out targets are refused.** `crossref.py` and `check_links.py` refuse a target whose queue row is `duplicate`, or that a fence rules out (`out-of-prep`, `look-for-phrv`, `care-for-phrv`; the list `RULED_OUT` in `tools/eexlib.py`).
- **The audit** of every mirror synonym, antonym, and compare link that has no note is review work, in batches under the 40-entry systemic cap (`NEXT.md`). Known wrong links: `run-v` sense 1 lists *bleed* and *control*; `get-v` sense 1 lists *run*. Removing or moving a link is per-entry model work with review.

## C2. Cross-references to entries that do not exist yet (site only)

The data stays as it is: a cross-reference may name a slug with no entry, and that is how closure finds new words. Only the site changes.

- **Synonyms, antonyms, compare:** a missing target is shown as plain muted text, not underlined and not a link, and the entry carries a one-line legend: "Grey words have no entry yet."
- **Word family and see also:** a missing item is hidden until its entry exists.
- **Tooltips** never show a slug.

## C3. Hyphens and periods

Labels keep their hyphens and periods (*brother-in-law*, *co-author*, *a.m.*). A display form comes from the entry, the queue row, or a slug map, never from turning the hyphens of a slug into spaces. The same loss in the queueing tools ([queue-hyphen-loss](../notes/queue-hyphen-loss.md)) is fixed, and the affected queue rows are repaired.
