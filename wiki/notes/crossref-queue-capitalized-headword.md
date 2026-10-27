# A queue row with a capitalized headword

*Observed 2026-10-27, ninetieth lint pass.*

`crossref.py --queue` added the row `Determinant n` (from `determiner-n`'s reference to `determinant-n`). The slug was right; the headword was capitalized, so a later draft would carry a wrong headword. Fixed by hand in the queue. Possible fix for a later run: lowercase the headword when a row is queued from a slug. No change yet.
