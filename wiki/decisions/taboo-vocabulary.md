# Taboo, vulgar, and offensive vocabulary

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** Vulgar and sexual vocabulary is included with clear labels (`vulgar`, `offensive`, domain `sex` where it is neutral). Slurs are excluded for now. If the drafting model declines to write an entry, the run records the headword and the reason in the curator queue, marks the queue item `declined`, and moves on. A run never stalls on a refusal and never argues with one or retries it in the same run.

**Consequence.** `queue_statuses` has `declined`; `provenance_flags` has `declined-in-part` for an entry written with a field left out.
