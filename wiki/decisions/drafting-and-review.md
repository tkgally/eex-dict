# Drafting and review

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** The Routine's model drafts entries in-session from its own knowledge and the style guide. Two non-Anthropic reviewers on OpenRouter, from different labs, check every field with closed verdicts. Switching to flagship drafting via OpenRouter is a decision the owner makes after seeing the seed set; the drafter is a configuration setting (`drafter_via_openrouter` in `config/routine-config.json`, roles in `config/models.md`).

**Why closed verdicts.** In the earlier project the reviewer's free-text flags ran at 4 to 17 percent precision and never read the notes, where the factual errors were. Here every field gets `ok` or `issue` with the exact claim quoted, a severity, and a family, so precision is measured per family and noise can be switched off.
