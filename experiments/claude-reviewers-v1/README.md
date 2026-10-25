# Claude reviewers against the OpenRouter reviewers (experiment, 2026-10-25)

**Question (the owner's, 2026-10-25):** can the two OpenRouter reviewers (`reviewer-a` GPT-5.6, `reviewer-b` Gemini 3.1 Pro) be replaced by Claude models running inside the owner's Claude subscription (Sonnet or Haiku), and what does it cost in quality, money, subscription tokens, and time?

**Short answer:** yes. Measured on blocking issues, Sonnet reviewed as well as the better OpenRouter reviewer (Gemini) and clearly better than GPT. It caught every planted error, and nearly all its blocking calls were right. The best panel was Sonnet plus Gemini. An all-Claude panel (Sonnet plus Haiku) found as many real blocking problems as today's panel, with far fewer false alarms. The cheap way to call Claude is a headless `claude -p` call from `tools/review_panel.py`, at a high effort setting, not Agent-tool subagents. Subagents used about thirteen times more tokens per review. Nothing here changes `main`: switching reviewers needs the owner's ruling, because the charter (`PROJECT.md`) names "two non-Anthropic reviewers".

## Design

- **Same prompt for everyone.** Every reviewer got exactly `tools/review_panel.py`'s system prompt (with `config/reviewer-house-rules.md`) and per-entry checklist prompt (`prompts/`). Replies were normalized by its own `normalize_verdicts`. The production `DISABLED_FAMILIES` filter was *not* applied, so all reviewers are compared raw; its effect is reported separately.
- **28 entries** (`inputs/`), in three sets:
  - *obvious*: 10 reviewed entries with 3 plain errors planted in each (30 errors: a wrong IPA, "a few money", a false etymology, brand names in an example, *sb/sth*, and so on; `plant.py`);
  - *subtle*: 10 reviewed entries with 2 harder errors planted in each (20 errors: "promoted to a manager", "strongly pregnant", verb stress on *record*, "Kim wants also to come", a usage note claiming *during* takes a clause; `plant.py`);
  - *natural*: 8 fresh drafts of queued milestone-1 words, written the way a build run writes them (one Opus subagent drafting from the style guide). They exist only in this folder, not in `entries/`, and no headword was claimed.
  The answer key is `planted.json`.
- **Six reviewer arms:** `reviewer-a` and `reviewer-b` through OpenRouter (production settings); Sonnet 5.5 and Haiku 5.5 as Agent-tool subagents (one subagent per entry); and Sonnet and Haiku as headless `claude -p` calls (`--tools ""`, the review prompt as the whole system prompt). Sonnet headless ran twice: at default effort and at `--effort xhigh`.
- **Blind adjudication.** For each entry, all issues from the four main arms were pooled, shuffled, and stripped of reviewer names (`judge/*.pool.json`; the key is in `*.key.json`). An Opus judge with the style guide ruled each issue `yes`/`partly`/`no` and grouped duplicates into "findings" (`judge/INSTRUCTIONS.md`, `judge/*.verdicts.json`).
  - Because the judge is a Claude model, the same pools were also judged by GPT-5.6 and by Gemini 3.1 Pro (`judge/x-*`).
  - The headless arms were judged by a headless Opus judge (`judge-cli*`), calibrated by re-judging the four original arms the same way (`judge-cli-calib`).
- **Usage** was read from the OpenRouter bills (`spend.json`) and from the subagent transcripts (`agent_usage.py`, `usage_summary.py`, `usage.json`). Scores are produced by `harness.py score | xscore | cliscore` (`results.json`).

## Results

### Quality

| Reviewer (28 entries) | Issues raised | of them blocking | Blocking precision: Claude / GPT / Gemini judge | All-issue precision: Claude / GPT / Gemini judge | Planted errors found (of 50) | Distinct real blocking problems found (of 71) |
|---|---|---|---|---|---|---|
| GPT-5.6 (`reviewer-a`) | 159 | 125 | 0.65 / 0.87 / 0.81 | 0.63 / 0.86 / 0.79 | 45 | 50 |
| Gemini 3.1 Pro (`reviewer-b`) | 92 | 76 | **0.99 / 0.97 / 1.00** | **0.90 / 0.95 / 1.00** | 49 | **56** |
| Sonnet 5.5, subagent | 270 | 90 | **0.98 / 0.97 / 0.99** | 0.73 / 0.78 / 0.91 | **50** | 55 |
| Haiku 5.5, subagent | 244 | 86 | 0.87 / 0.93 / 0.98 | 0.64 / 0.74 / 0.86 | 48 | 51 |

Headless arms (headless Opus judge; under that judge, the subagent arms above scored Sonnet 0.96 blocking and 0.70 overall, Haiku 0.86 and 0.60, GPT 0.62 and 0.60, Gemini 0.95 and 0.87):

| Reviewer | Issues | Blocking | Blocking precision | All-issue precision | Planted found |
|---|---|---|---|---|---|
| Sonnet headless, default effort | 238 | 84 | 0.90 | 0.54 | 49 |
| Sonnet headless, `--effort xhigh` | 234 | 80 | **0.97** | **0.70** | 48 (both misses are one malformed reply) |
| Haiku headless | 230 | 92 | 0.83 | 0.57 | 48 |

Panels (Claude judge; "false blocking" = blocking issues judged wrong (+ partly wrong), which the session must still read and reject):

| Panel | Distinct real blocking problems (of 71) | False blocking flags to adjudicate |
|---|---|---|
| GPT + Gemini (today) | 62 | 33 (+12) |
| Sonnet + Haiku | 62 | 7 (+6) |
| **Sonnet + Gemini** | **63** | **2 (+1)** |

What this means:
- **The two easiest planted sets were too easy to separate the reviewers:** everyone found 29–30 of the 30 obvious errors. The subtle set did separate them. GPT missed five errors that Sonnet caught: "promoted to a manager", both *also* errors, a schwa written as /æ/, and an *e.g.* in prose.
- **The outside judges each rated their own model highest.** The GPT judge rated GPT 0.86, against 0.63 from the Claude judge; the Gemini judge rated Gemini 1.00. The Claude judge was the strictest of the three, on the Claude reviewers too. Still, all three judges agree on the shape: Gemini and Sonnet are nearly always right when they call something blocking, Haiku is a little lower, and GPT is clearly lowest. I read a sample of 14 GPT blocking issues that the Claude judge rejected. In most of them GPT asked for something the house rules rule out, for example an idiom under the wrong keyword (*twist someone's arm* belongs under *arm*) or a phrasal verb as a sense. The outside judges do not know those rulings.
- **Sonnet's extra volume is in minor issues** (180 minor against 90 blocking). About 60% of them are right: repeated facts, signposts over three words, a missing word-family member. They are useful, but they are optional work for the adjudicating session. Haiku's minor issues are noisier (about half right), and Haiku spends a lot of hidden reasoning (about 15,000 thinking tokens per entry).
- **Effort matters for headless Sonnet.** At default effort it did almost no thinking (about 500 tokens per entry), and its precision fell to 0.90 on blocking and 0.54 overall. At `xhigh` it matched the subagent Sonnet. `high` was not tested.
- **The fresh drafts were already clean.** The eight drafts produced only 15 real findings in all, nearly all minor. GPT and Gemini found 1 each, Sonnet 8, Haiku 11. This sample shows no sign of an Anthropic blind spot that only the non-Anthropic reviewers catch. But it is a small sample, and the risk that one model family shares blind spots is the reason the charter asks for non-Anthropic reviewers.
- **Production filter:** the switched-off (role, family) pairs in `review_panel.py` would have hidden 30 GPT issues (17 of them valid) and 5 Gemini issues (all 5 valid). As a result, three planted errors would have reached the session from neither reviewer: a date and a statistic in an example, a melting point in an example, and brand names in an example. These are the example-policy family, switched off for both reviewers. Sonnet caught all three.

### Cost, subscription tokens, time (per entry reviewed)

| Reviewer | Money billed | Tokens processed | API-equivalent value | Median wall time |
|---|---|---|---|---|
| GPT-5.6 via OpenRouter | $0.025 | 6,400 | — | 8.5 s |
| Gemini 3.1 Pro via OpenRouter | $0.051 | 8,500 | — | 31.5 s |
| Sonnet subagent | $0 (subscription) | 192,000 | $0.27 | 44 s |
| Haiku subagent | $0 (subscription) | 228,000 | $0.02 | 85 s |
| Sonnet headless, default effort | $0 (subscription) | 14,500 | $0.06 | 22 s |
| Sonnet headless, `xhigh` | $0 (subscription) | 21,000 | $0.10 | 67 s |
| Haiku headless | $0 (subscription) | 23,000 | $0.008 | 49 s |

- **Subagents are the wrong way to call a reviewer.** Each one loads the whole Claude Code system prompt (about 53,000 tokens) and takes three turns. The review itself is about 5,000 tokens in and 6,000 out. Each finished subagent also sends a notification into the main session's context. A headless call costs about a thirteenth of the tokens, runs in parallel from Python, and fits the existing `review_panel.py` flow (a subprocess in place of an HTTP call).
- **Reliability.**
  - OpenRouter: 56 of 56 calls parsed.
  - Subagents: 56 of 56 parsed, but one Haiku subagent made an unrequested tool call (it listed other sessions) before answering.
  - Headless `xhigh`: one reply in 28 was malformed JSON. `claude -p --json-schema` (untested here) should remove that.
- **Subscription share.** I cannot read the owner's usage meter from inside a session. At about 100 reviewed entries a day, Sonnet headless at `xhigh` is about 2 million tokens a day, roughly $10 a day at API list prices. That is small next to what each run's Opus session already uses. The experiment as a whole (drafter, 56 subagents, 56 headless calls, 84 judge runs) used about $45 of API-equivalent Claude usage, plus this session.
- **Money.** Reviews are most of the OpenRouter spend: about 95% of the ledger, roughly $5–6 of a typical $6–11 day. Replacing GPT alone saves about a third of that, and replacing both saves nearly all of it. The pronunciation panel ($0.007 per entry) and the band votes are small and were not tested.
- **This experiment's OpenRouter bill:** $3.60 (`spend.json`). It is not in `main`'s ledger, because the branch's ledger change was not committed.

## Recommendation

1. **Best results:** make `reviewer-a` Sonnet 5.5 through headless `claude -p` at `--effort xhigh` (or `high` after a check), with `--json-schema`. Keep Gemini 3.1 Pro as `reviewer-b`. This panel found the most real problems (63 of 71), raised the fewest false blocking flags (2), keeps one reviewer from another lab as the charter intends, and cuts OpenRouter review spend by about a third.
2. **Lowest cost:** Sonnet plus Haiku, both headless. It matched today's panel on blocking problems (62 against 62) with a fifth of the false alarms, at $0 billed. The price is two reviewers from one family reviewing a drafter from the same family, plus Haiku's noisier minor issues and slower replies.
3. **Not recommended:** Agent-tool subagents as reviewers. The quality is the same as headless, the token use is thirteen times higher, and the orchestration is more fragile.

Either change needs the owner's ruling (the charter line on non-Anthropic reviewers, `config/models.md`, and the routine's budget logic, which counts only OpenRouter dollars). It also needs a small change to `tools/review_panel.py`: a `claude-cli` provider for a role, with tokens recorded in place of dollars.

## Files

`plant.py`, `plant2.py` (planted sets) · `inputs/` (the 28 entries reviewed) · `prompts/` · `outputs/<arm>/` (raw and normalized replies; `meta.json` = subagent usage) · `judge/` (blind pools, keys, Claude verdicts; `x-reviewer-a/`, `x-reviewer-b/` = the outside judges) · `judge-cli*/` (headless judge) · `harness.py` (every step) · `results.json`, `usage.json`, `spend.json`.
