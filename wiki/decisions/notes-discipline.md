# Notes discipline (2026-10-24)

*The owner's ruling B2 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)). The rules are written into the [style guide](../style-guide.md) and bind drafting, review, and adjudication.*

## Why

The assessment found note fields filled because they existed: the same fact in a usage note, an adaptation note, and a learner error; invented learner errors (*weller*, *My tire is flatted*, *droped*); generic adaptation notes ("many languages use different words; translate each sense"); and a fix applied to one copy of a fact while another copy kept the error (`worry-v`, `tell-v`).

## The rules

1. **Null by default.** `usage_note`, `synonym_discrimination`, `learner_errors`, each `adaptation` kind, and `pronunciation.notes` stay null unless the drafter can name what a learner or translator would get wrong without the note.
2. **One fact, one field.** A fact lives in one field; other fields do not restate it.
3. **Real learner errors only.** No invented misspellings, no regularized forms (*weller*, *flatted*), no adjective-for-adverb swaps added to fill the field. The default is none for band 3 and above, and for words labeled formal or literary.
4. **An adaptation note names a specific trap.** Generic "translate each sense separately" notes are not written.
5. **Fix all copies.** When adjudication fixes a fact, the adjudicator searches the entry's other prose fields for the same fact and fixes every copy.
6. **A validator warning, not an error.** `tools/validate.py` warns when two prose fields of one entry share most of their content words (at least 70 percent of the shorter field's content words, both fields at least eight content words long; 179 pairs in 169 entries on 2026-10-24, so the session chose 70 percent over 60, which gave 341 pairs), so the adjudicator can look.
7. **No mass rewrite.** Existing entries are brought into line only when a review opens them (the B1 coverage pass and the E2 second rounds, [reviewer-house-rules](reviewer-house-rules.md)). The style guide stays under its 3,500-word cap; older text was trimmed to fit.
