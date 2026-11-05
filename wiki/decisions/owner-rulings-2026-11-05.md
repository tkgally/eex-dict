# Owner's rulings of 2026-11-05

*Given by the owner in an interactive session on 2026-11-05, in answer to the "For the owner" items of `NEXT.md`; the text is archived as `inbox/archive/20261105_owner_rulings.txt`. Binding. Carried out the same day.*

**1. Family names after a title.** Allowed. An example may pair a title (*Mr.*, *Ms.*, *Mrs.*, *Dr.*, *Professor*, *President*, *Lady*, *Lord*) with a family name from a closed list of short names of various origins: **Chen, Diallo, Diaz, Ito, Khan, Kim, Lee, Mensah, Novak, Okafor, Park, Rossi, Sato, Shah, Silva, Weber**. *Kim* and *Lee* serve as both given and family names. Given names (Kim, Mari, Sam, Ana, Lee, Omar, Yuki, Ravi, Sara) stay the only names used alone. A family name appears only after a title; a title that takes a given name (*Sir Omar*, *Aunt Sara*, *Uncle Ravi*) keeps one. Recorded in [examples](examples.md), the style guide (section 5), the reviewer prompt in `tools/review_panel.py`, and [config/reviewer-house-rules.md](../../config/reviewer-house-rules.md) rule 26. Existing examples that put a given name after *Mr.*, *Mrs.*, or *Dr.* (*Mr. Sam*, *Mrs. Ana*, *Dr. Mari*, *Mr. Ravi*, *Lord Ravi*) are fixed at their next review.

**2. `PROJECT.md`.** Line 31 now says two reviewers from different labs, reviewer A Anthropic and reviewer B non-Anthropic, matching [reviewer-a-claude](reviewer-a-claude.md). Edited by this session on the owner's instruction.

**3. Pronunciation checking.** The present arrangement is confirmed: every transcription is checked by the pronunciation panel plus the CMU dictionary (`tools/pronounce_check.py`, [pronunciation-pipeline](pronunciation-pipeline.md)); neither reviewer checks pronunciation (reviewer A off by the ruling of 2026-10-05, reviewer B off since the hundred-and-second lint pass). Lint passes keep measuring nothing for that family and do not raise it again.

**4. Continent names in definitions.** Allowed. *Africa, Antarctica, Asia, Australia, Europe, North America, South America* join `proper_names` in `schema/vocabularies.json` ([proper-names-in-definitions](proper-names-in-definitions.md)). Answers open question of 2026-10-10.

**5. *The former*, *the latter*, *the following* standing alone** are nouns: `former-n`, `latter-n`, `following-n`. Answers open question of 2026-10-11; house rule 23 now cites this ruling. `latter-n` was queued (source `owner`) beside the two rows already queued.

**6. Left for a session with the owner:** the pronunciation disputes in `reviews/needs_curator.txt` and the ten-entry spot-check sample of `journal/digest-2026-10-31.md`. Routine runs do not settle them.
