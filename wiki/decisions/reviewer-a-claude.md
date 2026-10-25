# Reviewer A becomes a Claude model, called headless

*Ruled by the owner in an interactive session on 2026-10-25, after the experiment in [experiments/claude-reviewers-v1](../../experiments/claude-reviewers-v1/README.md). Implemented the same day in `config/models.md`, `tools/openrouter.py`, `tools/review_panel.py`, and `tools/metrics.py`.*

**Why.** The experiment had both reviewers and two Claude models check the same 28 entries with the production prompt: 50 errors planted in 20 entries, plus 8 fresh drafts. Every issue was judged blind, and two outside judges checked the Claude judge.

- The OpenRouter reviewer A was right on 65–87% of its blocking calls, depending on the judge. It raised about one false blocking issue per entry, and it missed 5 of the 20 subtle planted errors.
- The mid-size Claude model was right on 97–99% of its blocking calls and found all 50 planted errors.
- Paired with reviewer B, it found the most real blocking problems of any panel (63 of 71), with 2 false blocking issues. Today's panel found 62, with 33.

**The change.**
- `reviewer-a` is now the slug `claude-cli/<model id>`.
- `tools/openrouter.py` runs such a slug as one headless `claude -p` call: no tools, the review prompt as the whole system prompt, run outside the repository, high effort, and a JSON schema for the reply. It runs on the owner's Claude subscription. Nothing is billed, so the ledger records the call at $0 with its tokens.
- `tools/review_panel.py` runs the two roles side by side, so a batch takes about as long as the slower reviewer.
- Reviewer B is unchanged and stays non-Anthropic, so the panel still has one reviewer from another lab.
- `PROJECT.md` still says "two non-Anthropic reviewers". The owner edits the charter, not a session; this ruling stands in its place until then.

**Switched-off families.** The lint runs had switched off four (role, family) pairs for the old model: example-policy, grammar-code, sense-structure, and inflection. They are live again, because the measurement belonged to a different model. The pronunciation pair stays off, because it is the owner's ruling of 2026-10-05; it was based on the old model's precision of 0.26, so it is a question for the owner.

**Measuring it.** From 2026-10-25, decision lines carry the reviewer's `model`. `tools/metrics.py --precision` reports the new reviewer A as `reviewer-a:<model id>`, apart from its old model's all-time figures. The 30-percent switch-off rule applies to the new rows once they reach twenty decisions.

**Not changed.** The pronunciation and word-list panels keep their OpenRouter models. The originality check asks reviewer B (it used to ask reviewer A, with reasoning off).
