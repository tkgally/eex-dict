# Reviewer B and the first pronunciation panel member move to newer models

*Ruled by the owner in an interactive session on 2026-10-25, after the experiment in [experiments/model-refresh-v1](../../experiments/model-refresh-v1/README.md). Implemented the same day in `config/models.md`, `tools/openrouter.py`, `tools/review_panel.py`, and `tools/metrics.py`.*

**Why.** The experiment tested the newer OpenRouter models that cost the same or less as the ones in use.

- **Reviewers.** The test used the 28 entries of `claude-reviewers-v1`, which have 50 planted errors, and the production review prompt. Every issue was judged blind.
  - Gemini 4 Argon found all 50 planted errors and 59 of the 63 real blocking problems, with 0.99 blocking precision, at $0.034 an entry.
  - Gemini 3.1 Pro found 49 planted errors and 58 blocking problems, at $0.051 an entry.
- **Pronunciation.** On the 500-word pronunciation set, GPT-6.1 Sol agreed with CMU on 94.0 percent of American transcriptions. GPT-5.6 Terra agreed on 91.9 percent. Both agreed with the drafter's British forms on 92.6 percent, at about the same cost.

**The change.**
- `reviewer-b` is `google/gemini-4-argon`, priced at $2 per million input tokens and $10 per million output. It is still Google, so the panel keeps one reviewer from a lab other than Anthropic. It runs at low reasoning effort, as the Google endpoints require.
- `pronunciation-1` is `openai/gpt-6.1-sol`, at the same price.
  - Its endpoint refuses calls with reasoning switched off, so `tools/openrouter.py` lists it in `REASONING_REQUIRED` and runs it at low effort. In the test it answered all 500 words within the usual output limit.
  - The pronunciation pipeline's rule that "calls run with reasoning switched off" therefore has this one exception.
- `wordlist-1` stays `openai/gpt-5.6-terra` until a band-vote comparison shows that GPT-6.1 Sol votes as well.
- The prices in `config/models.md` were brought up to date: DeepSeek V4 Pro is now 0.209 / 0.418 and Gemini 3.8 Flash 0.825 / 4.125. Every slug there was re-verified on 2026-10-25.

**Switched-off families.** Earlier lint runs had switched off three pairs for reviewer B's old models: example-policy (0.05 over 83 decisions), explanation (0.24 over 21) and inflection (0.10 over 21). Those measurements belonged to other models. By the rule the owner set when reviewer A changed model ([reviewer-a-claude](reviewer-a-claude.md)), the pairs are live again and are measured afresh. In the earlier experiment, the example-policy switch-off had hidden three planted errors: dates, statistics and brand names in examples. The 30-percent rule applies to the new rows once they reach twenty decisions.

**Measuring it.** Decision lines already carry the reviewer's `model`. `tools/metrics.py --precision` now reports `reviewer-b:gemini-4-argon` apart from reviewer B's all-time figures.
