# A second homograph cannot be queued or inflected correctly

*Observed 2026-09-26, run `20260926T185648Z-iujuq0`. Status: open.*

**What happened.** `lie-v` was drafted as *be in a flat position* (past **lay**, past participle **lain**). Its `see_also` names `lie-v-2`, *say something that is not true* (past **lied**), an unrelated homograph that needs its own entry (conventions section 2). `crossref.py --queue` did not add a row for it: `headwords/queue.tsv` is keyed by headword and part of speech, with no homograph column, so `lie v` already counted as queued. The same will happen for `pen-n-2` (NEXT.md).

A second problem waits for the drafter: `tools/inflect.py` looks up `schema/inflection-exceptions.json` by headword, so `lie-v-2` would get **lay**/**lain** instead of **lied**/**lied**/**lying**.

**Working assumption.** Until fixed, a run that drafts a second homograph queues nothing, claims by hand, and checks the inflections `inflect.py` writes before the panel; `lie-v-2` and `pen-n-2` are listed in `NEXT.md`.

**Possible fix (a later run, with a logged reason).** A homograph column (or a slug column) in `queue.tsv`, and slug-keyed exceptions (`"lie-v-2": {...}`) that take precedence over the headword key.
