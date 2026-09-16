# Name and home

*Decided by the owner in the founding prompt, 2026-09-16. Binding: a session may not reopen it; it may queue a question in [open-questions](../open-questions.md) with a working assumption. Charter: [PROJECT.md](../../PROJECT.md).*

**Ruling.** The dictionary is the **TKG English Learner's Dictionary**; the repository is `tkgally/eex-dict`. A domain name comes later. The site is built with relative links so that it works at any base URL, including the default GitHub Pages path and a future custom domain.

**Consequence for sessions.** `tools/build_site.py` never writes an absolute URL or a leading slash into a link; every page computes paths relative to its own location.
