# claude-cli model label

*Observed 2026-10-25 (build run 20261025T065852Z-3r5wmk). Fix due a later run.*

`tools/openrouter.py` `chat_claude_cli` records the model as the first key of `claude -p`'s `modelUsage`. Claude Code also runs a small helper call on a smaller model, and that key comes first, so every reviewer-a call of this run was recorded as `claude-cli/claude-haiku-5-5` (ledger, review files, `provenance.reviews`, decision lines). A test call showed the helper used 16 output tokens and the requested model the rest: the review itself was done by the model in `config/models.md`.

Effect: `metrics.py --precision` would split reviewer-a's rows across two model names. Proposed fix: record the requested model when it is among the keys, else the key with the most output tokens; relabel this run's rows with a logged decision.
