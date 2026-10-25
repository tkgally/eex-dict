# Newer OpenRouter models at the same price or less (experiment, 2026-10-25)

**Question (the owner's, 2026-10-25):** OpenRouter now lists newer models than those in `config/models.md`. Can any that cost the same or less do the work as well? In particular, does `google/gemini-3.8-flash` review as well as `google/gemini-3.1-pro-preview` (reviewer-b)?

**Short answer:**
- **Gemini 3.8 Flash as reviewer-b:** nearly as good, at a quarter of the price.
  - On its own it is slightly weaker than Gemini 3.1 Pro. It caught the same number of planted errors (49 of 50) and was right as often when it called something blocking (0.98 against 0.99). It found fewer real blocking problems (54 against 58).
  - Paired with today's reviewer-a (the Claude model), the panel found every real blocking problem either way (63 of 63).
  - It costs $0.012 an entry against $0.051, and answers in 12 seconds against 31.
- **Gemini 4 Argon (new, $2 / $10):** the strongest reviewer tested, and a third cheaper than Gemini 3.1 Pro. It found all 50 planted errors and 59 real blocking problems, with 0.99 blocking precision.
- **Pronunciation panel:** GPT-6.1 Sol, which costs about the same as GPT-5.6 Terra (pronunciation-1) for this job, transcribed a little better.
- **Not good enough:** GPT-6 Luna, the cheapest model tested, is fine for pronunciation but useless as a reviewer.

Nothing outside this folder changes: switching a role needs the owner's ruling.

## What OpenRouter lists now (checked 2026-10-25 against `https://openrouter.ai/api/v1/models`)

Price in US dollars per million tokens, input / output.

| Role | Current model and price today | Newer at the same price or less | Tested here |
|---|---|---|---|
| reviewer-b | gemini-3.1-pro-preview, 2.00 / 12.00 | gemini-4-argon 2.00 / 10.00 (2026-10-13); gemini-3.8-flash 0.825 / 4.125; also gpt-6.1-sol 2 / 10, gpt-6-luna 0.10 / 0.50, grok-4.7 2 / 6, kimi-k3.1-pro 2 / 10, qwen3.8-max 2 / 6 | Argon, 3.8 Flash, GPT-6 Luna |
| pronunciation-1, wordlist-1 | gpt-5.6-terra, 2.00 / 12.00 | gpt-6.1-sol 2.00 / 10.00 (2026-09-29); gpt-6-luna 0.10 / 0.50 | both, pronunciation only |
| pronunciation-2, wordlist-2 | gemini-3.8-flash, now 0.825 / 4.125 (was 0.75 / 3.75) | none: it is still the newest Flash | — |
| pronunciation-3, wordlist-3 | deepseek-v4-pro, now 0.209 / 0.418 (was 1.60 / 3.20) | none cheaper: the newer deepseek-v4.1-flash costs more for output (0.02 / 1.00), and output is most of a pronunciation call | — |
| drafter (only via OpenRouter when `drafter_via_openrouter`) | claude-sonnet-5, 2.00 / 10.00 | claude-sonnet-5.5 at the same price | — |

The price column of `config/models.md` is out of date for DeepSeek and Gemini 3.8 Flash. It is used only to estimate a call before the budget check, so the DeepSeek estimate is now about eight times too high (on the safe side).

## Reviewer test

**Design.** The test reuses [claude-reviewers-v1](../claude-reviewers-v1/README.md): the same 28 entries and the same answer key (`planted.json`).
- 10 entries have 30 plain errors planted in them, and 10 have 20 subtle ones.
- 8 are fresh drafts with nothing planted.

Each new model got exactly the production `review_panel.py` call: the system prompt with the house rules, the checklist prompt, the reply schema, temperature 0.1, and reasoning as `openrouter.reasoning_for` sets it (low effort for Google; off for OpenAI). The baseline replies are the earlier experiment's. Gemini 3.1 Pro is that experiment's `reviewer-b` arm. Headless Sonnet at `xhigh` stands in for today's reviewer-a, which runs at `high`. The prompt has not changed since then (checked: identical system prompt).

All issues from the four arms were pooled per entry, shuffled and unlabelled. A headless Opus call at high effort judged them blind (the earlier experiment's `judge/INSTRUCTIONS.md`). It ruled each issue right, partly right or wrong, and grouped issues that name the same problem into "findings". GPT-6 Luna was judged on its own afterwards (`judge-luna/`), so its findings are not on the shared labels and it is left out of the panel rows.

**Results** (`results-review.json`, `results-judge-luna.json`; `python3 harness.py score`).

| Reviewer | Issues | Right | Blocking | Blocking right | Wrong blocking | Planted found (of 50) | Real blocking problems found (of 63) | All real problems found (of 143) | Cost per entry | Median time |
|---|---|---|---|---|---|---|---|---|---|---|
| Gemini 3.1 Pro (reviewer-b today) | 92 | 0.90 | 76 | 0.99 | 1 | 49 | 58 | 63 | $0.051 | 31 s |
| **Gemini 3.8 Flash** | 80 | **0.94** | 66 | 0.98 | 1 | 49 | 54 | 57 | **$0.012** | **12 s** |
| **Gemini 4 Argon** | 145 | 0.87 | 79 | **0.99** | 1 | **50** | **59** | **92** | $0.034 | 29 s |
| Sonnet headless (reviewer-a's model) | 234 | 0.76 | 80 | 0.96 | 3 | 48 | 60 | 132 | $0 | 67 s |
| GPT-6 Luna (judged alone) | 260 | 0.45 | 210 | 0.49 | 107 | 47 | — | — | $0.001 | 11 s |

| Panel (reviewer-a + reviewer-b) | Real blocking problems (of 63) | All real problems (of 143) | Wrong blocking flags to adjudicate |
|---|---|---|---|
| Sonnet + Gemini 3.1 Pro (today) | 63 | 137 | 4 |
| Sonnet + Gemini 3.8 Flash | 63 | 135 | 4 |
| Sonnet + Gemini 4 Argon | 63 | 142 | 4 |

What this means:
- **Flash against 3.1 Pro.** Both missed one planted error, a different one each.
  - Pro found five blocking problems that Flash did not:
    - a rule stated in three fields of *although*;
    - a grammar note on *ash* that contradicts a subsense;
    - a malformed definition in *behind*;
    - a wrong synonym in *look up*;
    - a usage note on *pregnant* that only repeats a learner error.
  - Flash found one that Pro did not: wrong American stress in *look up*.
  - Sonnet found all six. That is why the panel totals are equal.
- **What reviewer-b catches that Sonnet misses.** Sonnet missed three blocking problems: the missing *fewer*/*fewest* in *few*, and two planted errors in *ought*. All three Gemini models caught all three. The inflection one would be hidden in production anyway, because reviewer-b's inflection family is switched off (`DISABLED_FAMILIES`).
- **On the fresh drafts, the realistic case:** a second reviewer adds almost nothing beyond Sonnet in this sample. Flash raised 2 issues, both wrong. Pro raised 2, one right. Argon raised 15, 10 right, and only one of them (a minor markup point) was not also raised by Sonnet. Eight drafts is a small sample.
- **Argon** finds the most. It is the only arm that caught all 50 planted errors, and it adds about 30 real minor findings over Pro. Its extra issues are a little less often right (0.87 overall; 0.67 on the fresh drafts).
- **GPT-6 Luna** is not usable as a reviewer. Half its blocking calls were wrong (107 wrong blocking flags in 28 entries), and on the fresh drafts 41 of its 42 issues were wrong.
- **Not tested: GPT-6.1 Sol as a reviewer.** OpenRouter refuses it with reasoning switched off ("Reasoning is mandatory"), so it would need `reasoning_for` changed and would cost more than its price suggests. The day's budget was kept for the scheduled runs.

**Money.** Reviewer-b is nearly all of the OpenRouter bill now that reviewer-a is $0. At about 100 reviewed entries a day:
- Gemini 3.1 Pro: about $5.10;
- Argon: about $3.40;
- Flash: about $1.25.

## Pronunciation test

**Design.** The test reuses [pronunciation-model-test-v1](../pronunciation-model-test-v1/): its 500 words in five strata and its panel replies of 2026-09-16 as the baseline. The new models got the production `pronounce_check.py` prompt, chunking and temperature with reasoning off. GPT-6.1 Sol refuses that, so it ran at low effort. American answers were scored against CMU, fetched to `.tmp/` and not stored. British answers were scored against the drafter's British form in the baseline. The comparison uses the pipeline's N2 normalization.

| Model | US agrees with CMU | defining | band 2–3 | rare | heteronyms | loanwords | UK agrees with drafter | Cost for 500 words |
|---|---|---|---|---|---|---|---|---|
| GPT-5.6 Terra (pronunciation-1) | 91.9 | 98.0 | 93.8 | 81.8 | 88.0 | 85.1 | 92.6 | about $0.25 (from today's billed calls) |
| Gemini 3.8 Flash (pronunciation-2) | 90.7 | 97.5 | 93.8 | 75.0 | 92.0 | 83.0 | 89.8 | — |
| DeepSeek V4 Pro (pronunciation-3) | 93.6 | 98.5 | 97.9 | 84.1 | 90.0 | 85.1 | 92.8 | — |
| **GPT-6.1 Sol** | **94.0** | **98.5** | **97.9** | **86.4** | 90.0 | 85.1 | 92.6 | $0.21 |
| GPT-6 Luna | 91.3 | 96.5 | 93.8 | 83.0 | 88.0 | 83.0 | 91.6 | $0.01 |

- GPT-6.1 Sol is a little better than Terra in every stratum but loanwords, where they tie, at about the same cost.
- Luna is about as good as Terra overall at a twentieth of the cost, but weaker on the defining vocabulary, the words that matter most here.
- The pronunciation panel costs under a cent per entry either way, so this is a quality choice, not a money one.
- The baselines are from 2026-09-16, a month older than the new answers. The prompt is unchanged.

**Word-list panel:** not tested. It uses the same three models, but it runs only in lint cycles on unbanded rows. If pronunciation-1 moves to GPT-6.1 Sol, a band-vote comparison (as in `../band-vote-2026-10-24/`) should come before wordlist-1 follows.

## Options for the owner

1. **reviewer-b:**
   - **Gemini 3.8 Flash** for the lowest cost. In the panel it found exactly the same blocking problems, for about $4 a day less.
   - **Gemini 4 Argon** for the most findings at a third less than today.
   - Either is a one-line change to `config/models.md`. Both are Google models, so `reasoning_for` already runs them at low effort.
2. **pronunciation-1:** GPT-6.1 Sol in place of GPT-5.6 Terra, a small quality gain. It needs `reasoning_for` to send low effort for it, because the endpoint refuses `enabled: false`.
3. **Prices in `config/models.md`:** bring the DeepSeek and Gemini 3.8 Flash prices up to date.

## Files

- `harness.py`: every step; see its docstring.
- `outputs/<arm>/`: raw and normalized review replies.
- `outputs/pron/`: pronunciation replies.
- `judge/`: blind pools, keys and Opus verdicts for the four shared arms.
- `judge-luna/`: the same for GPT-6 Luna, judged alone.
- `results-*.json`: the scores.

**Spend:** US$1.55, recorded in `config/budget-ledger.json`:
- Argon $0.94;
- Flash $0.35;
- GPT-6.1 Sol pronunciation $0.21;
- Luna $0.05.

The Opus judge ran on the subscription.
