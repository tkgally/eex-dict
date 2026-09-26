# crossref adds a back-link of a second type

*Observed 2026-09-26, build run `20260926T064312Z-c2ms4g`. Status: fixed 2026-09-26 (lint run `20260926T155426Z-ngyr08`).*

**What happened.** `tools/crossref.py --apply` mirrors every sense cross-reference onto its target. When the target already names the source under a different type, it adds a second link anyway. Two cases this run:

- `include-v` listed `contain-v` as a synonym; `contain-v` sense 1 already had `include-v` under `compare`. The tool added `include-v` to `contain-v`'s synonyms as well, so the same pair was both a synonym and a compare.
- `inform-v` listed `tell-v` under `compare`; `tell-v` sense 1 already had `inform-v` as a synonym. The tool added a compare link beside it.

**Workaround.** Reverted both target files and changed the new entries to use the type the older entry already had (the choice is a semantic one and stays with the drafter).

**Possible fix (later run, with a logged reason).** Before adding a back-link, check whether the target sense already names the source under any sense cross-reference type; if so, report a `TYPE-MISMATCH` line instead of writing. A test in `tools/tests/` should cover both cases.

**Fixed 2026-09-26** (thirteenth lint pass). `crossref.py` now prints `TYPE-MISMATCH <target> names <source> under <type>, ...` and writes nothing when the target already names the source under another sense relation; three tests cover it. A scan found 54 senses that name one slug under two types (for example `speak-v`/`talk-v`, synonym plus a compare note). They are symmetric in both entries, so they look like drafters' deliberate choices, not tool output; left as they are.
