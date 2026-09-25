# One-sense entries carrying a signpost

*Observed 2026-09-25 (review run, reviewer-b on `everything-pron`).*

The style guide (section 4) says a one-sense entry has `signpost: null`. A scan on 2026-09-25 found 45 one-sense entries with a signpost set, mostly function words (*anybody-pron* "any person", *my-det* "belonging to me", *every-det* "each one") but also *admire-v*, *advantage-n*, *begin-v*, *calm-v*. `tools/validate.py` does not check it, so drafters and reviewers have let it through.

This run cleared it by hand on the three entries in its block (*everybody-pron*, *everyone-pron*, *everything-pron*). The other 42 are fixed when a review touches them (the signpost is a semantic field: no script may clear it).

Possible later change, with a logged reason: a `validate.py` warning for a signpost on a one-sense entry, so the drafter sees it. Not done here (no new machinery on speculation).
