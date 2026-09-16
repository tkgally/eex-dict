# Size, milestones, and the per-run cap

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** Milestone 1 is a closed defining vocabulary of about 2,500 words, every one with a complete entry, so the dictionary is self-contained. Then expansion by frequency band toward roughly 10,000 headwords, then by internal closure and learner need. **Cap: 20 new entries per run**, each fully verified before it is published; the cap is a ceiling, not a target.

**Why.** The owner's earlier dictionary created entries by the thousand before its standards existed and spent months repairing semantics. Here every entry is drafted, reviewed by two other models, and adjudicated before publication.

**Consequence.** `tools/claim.py` refuses a claim of more than 20 slugs; `tools/validate.py --gate` refuses more than 40 `draft` entries in the repository.
