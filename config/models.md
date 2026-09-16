# Models and roles

Code refers to roles; only this file names model slugs. Every slug below was checked against `https://openrouter.ai/api/v1/models` on the date in the Verified column. Prices are US dollars per million tokens (input / output) as listed on that date, for budgeting only. Reviewers are from different labs and neither is Anthropic. The drafter runs inside the session (the Routine's own model); switching drafting to an OpenRouter model is the `drafter_via_openrouter` setting in `config/routine-config.json`, which the owner decides after reading the seed set.

| Role | Model slug | Verified | Price in/out | Notes |
|---|---|---|---|---|
| drafter | anthropic/claude-sonnet-5 | 2026-09-16 | 2.00 / 10.00 | Drafts in-session. Used through OpenRouter only in the pronunciation experiment and when `drafter_via_openrouter` is true. |
| reviewer-a | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | Field-by-field reviewer, OpenAI. |
| reviewer-b | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Field-by-field reviewer, Google. Upgrade candidate if its precision is low: google/gemini-3.1-pro-preview (2.00 / 12.00). |
| pronunciation-1 | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | Pronunciation panel member. |
| pronunciation-2 | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Pronunciation panel member. |
| pronunciation-3 | deepseek/deepseek-v4-pro | 2026-09-16 | 1.60 / 3.20 | Pronunciation panel member, DeepSeek; kept or dropped by the result in `wiki/notes/pronunciation-model-test-v1.md`. |
| wordlist-1 | openai/gpt-5.6-terra | 2026-09-16 | 2.00 / 12.00 | Defining-vocabulary and band panel, OpenAI. |
| wordlist-2 | google/gemini-3.8-flash | 2026-09-16 | 0.75 / 3.75 | Defining-vocabulary and band panel, Google. |
| wordlist-3 | deepseek/deepseek-v4-pro | 2026-09-16 | 1.60 / 3.20 | Defining-vocabulary and band panel, DeepSeek. |

How to re-verify: fetch the model list (no key needed) and confirm each slug is present; update the Verified date. A slug that has disappeared is replaced by the nearest current model from the same lab, with a line in `wiki/log.md`.

Reasoning: the reviewers get `reasoning: {"effort": "low"}` where the model supports it, so a review costs about the same as the entry it reads. The panel calls send `usage: {"include": true}` and record the billed `usage.cost` in `config/budget-ledger.json` through `tools/spend.py`.
