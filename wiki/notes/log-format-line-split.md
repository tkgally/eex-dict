# Log entries inserted inside the format line

*Observed 2026-10-01, 2026-10-02 (twice); fixed 2026-10-06 (forty-seventh lint pass).*

`wiki/log.md`'s third line, the format line, itself contains the text `## [YYYY-MM-DD] ...`. A session that inserts a new entry before "the first `## [`" in the file (by hand or with a short script) lands inside that line and splits it; the entry then sits in the middle of the italic format sentence. It happened on 2026-10-01, at the 00:43 UTC run of 2026-10-02, and again in the 06:44 UTC run's first cycle; each time a later lint pass repaired it by hand.

A possible fix: reword the format line so that it does not begin a match for `## [` (for example, describe the header as "two hashes, the date in brackets, ..."), or add a `tools/log_entry.py` that inserts after the format line and checks the 200-word cap. Until then: insert after line 4, as `NEXT.md` says.

**Fixed 2026-10-06** (forty-seventh lint pass): the format line was reworded so that it no longer contains the header pattern; the first `## [` in the file is now the newest entry's header. No tool was added. Inserting after line 4 still works.
