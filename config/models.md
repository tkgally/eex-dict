# Models and roles

Code refers to roles; only this file names model slugs. Every OpenRouter slug below was checked against `https://openrouter.ai/api/v1/models` on the date in the Verified column. Prices are US dollars per million tokens (input / output) as listed on that date, for budgeting only. A slug starting `claude-cli/` is not an OpenRouter model: `tools/openrouter.py` runs it as one headless `claude -p` call on the owner's Claude subscription (no tools, the task's own system prompt, the effort `reasoning_for` sets), priced 0 / 0 because nothing is billed; the ledger records its tokens at $0. The two reviewers are from different labs: reviewer-a is Anthropic and reviewer-b is not (owner's ruling of 2026-10-25, [reviewer-a-claude](../wiki/decisions/reviewer-a-claude.md)). The drafter runs inside the session (the Routine's own model); switching drafting to an OpenRouter model is the `drafter_via_openrouter` setting in `config/routine-config.json`, which the owner decides after reading the seed set.

| Role | Model slug | Verified | Price in/out | Notes |
|---|---|---|---|---|
| drafter | anthropic/claude-sonnet-5 | 2026-09-16 | 2.00 / 10.00 | Drafts in-session. Used through OpenRouter only in the pronunciation experiment and when `drafter_via_openrouter` is true. |
| reviewer-a | claude-cli/claude-sonnet-5-5 | 2026-10-25 | 0.00 / 0.00 | Field-by-field reviewer, Anthropic, headless `claude -p` at high effort on the owner's subscription. Replaced openai/gpt-5.6-terra (2.00 / 12.00) by the owner's ruling of 2026-10-25 after `experiments/claude-reviewers-v1/`; precision is reported per model from then on. |
| reviewer-b | google/gemini-3.1-pro-preview | 2026-10-05 | 2.00 / 12.00 | Field-by-field reviewer, Google. Upgraded from google/gemini-3.8-flash (0.75 / 3.75) by the owner's ruling of 2026-10-05; precision is reported in the lint passes from then on. |
| pronunciation-1 | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | Pronunciation panel member. |
| pronunciation-2 | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Pronunciation panel member. |
| pronunciation-3 | deepseek/deepseek-v4-pro | 2026-09-16 | 1.60 / 3.20 | Pronunciation panel member, DeepSeek; kept or dropped by the result in `wiki/notes/pronunciation-model-test-v1.md`. |
| wordlist-1 | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | Defining-vocabulary and band panel, OpenAI. |
| wordlist-2 | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Defining-vocabulary and band panel, Google. |
| wordlist-3 | deepseek/deepseek-v4-pro | 2026-09-16 | 1.60 / 3.20 | Defining-vocabulary and band panel, DeepSeek. |

How to re-verify: fetch the model list (no key needed) and confirm each OpenRouter slug is present; for a `claude-cli/` slug, `python3 tools/openrouter.py --role reviewer-a --prompt "Say OK"` must answer. Update the Verified date. A slug that has disappeared is replaced by the nearest current model from the same lab, with a line in `wiki/log.md`.

Reasoning: OpenRouter panel and reviewer calls run without hidden reasoning (it is billed as output and counts against the reply limit, and the closed checklists do not need it); Google endpoints refuse to disable it and run at low effort, where they spend no reasoning tokens on these tasks. A `claude-cli/` reviewer runs at high effort: at the default effort it barely reasoned and its precision fell (`experiments/claude-reviewers-v1/README.md`). The panel calls send `usage: {"include": true}` and record the billed `usage.cost` in `config/budget-ledger.json` through `tools/spend.py`.
