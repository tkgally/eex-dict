# Knowledge base and caps

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** The knowledge-base framework (`framework.md`), kept deliberately small, with hard word caps enforced by a tool.

**Why.** The earlier project's prompts reached about 36,000 words and its wiki about 500,000, and the wiki was almost never consulted by runs that changed entries.

**Caps** (`tools/check_caps.py`, run in CI): `CLAUDE.md` 1,500 words; `resume-prompt.md` 800; `routine-prompt.md` 2,500; `NEXT.md` 60 lines; `wiki/style-guide.md` 3,500; the wiki excluding index, log, and decisions 30,000; each log entry 200. The wiki holds conventions, the style guide, decisions, notes, and open questions; it does not hold a research library on lexicography.
