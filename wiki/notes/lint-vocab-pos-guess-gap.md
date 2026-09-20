# lint_vocab.py: pos_guess defaults to noun for an unrecognized base form

*Observed 2026-09-19, closure run.*

`tools/lint_vocab.py --queue` queued **additional** as `additional-n` (source: closure, from `other-det`'s definition, which uses *additional* to mean *extra*). `pos_guess()` only recognizes a verb from an inflected form, an adjective from a comparative or superlative, or an adverb from a recognized `-ly` base; a base-form adjective with none of those morphological cues (*additional*, *former*, *sole*) falls through to its `n` default with no signal that the guess is unreliable.

The claiming run declined `additional-n` (`queue.py set additional n declined --note "..."`) and added `additional-adj` as a `crossref` row instead, per [drafting-and-review](../decisions/drafting-and-review.md) and `CLAUDE.md` rule 6. One line went to `reviews/needs_curator.txt` recording the decline, per the same rule.

No script writes a semantic field, and part of speech is one (`CLAUDE.md` field-ownership table): `pos_guess` is a queueing convenience, not an authority, so this is not a correctness bug in what gets published — only in what gets queued for a drafter to notice. A future lint session could narrow the default (a small closed list of adjective suffixes like `-al`, `-ive`, `-ous`, `-ent` checked before falling back to noun) or, more simply, tag every guessed `n` row with a `note` flagging it as a guess so a drafter double-checks before claiming. Either is a lint-mode change with a logged reason, not urgent: the drafter catching a wrong guess (as happened here) costs one declined row, not a wrong entry.

## 2026-09-20: both suggested fixes made

`pos_guess` now checks a small closed list of adjective suffixes (`-al`, `-ive`, `-ous`, `-ent`, `-ant`, `-ic`, `-ful`, `-less`, `-able`, `-ible`) before the noun default, so a base-form adjective like *additional* or *curious* is queued as `adj` directly. It also returns whether the guess had no morphological signal at all (still defaulting to `n`); `queue_lemmas` appends `"; pos guessed (no morphological signal), check before claiming"` to that row's note, so a drafter sees the flag without needing to re-derive it. Not exhaustive — a base-form adjective outside the suffix list (*former*, *sole*) still falls through to the flagged noun guess, which is the intended fallback, not a bug. Tests in `tools/tests/test_lint_vocab.py` (`test_pos_guess`, and the updated `test_queue`) cover both the suffix win and the flagged default.
