# crossref.py lists NO-SENSE pairs only with --apply

*Observed 2026-10-30, run 20261030T191618Z-ivde44 (build). No change yet.*

`python3 tools/crossref.py <slugs>` without `--apply` printed `0 back-links left for a person (NO-SENSE)` right after an `--apply` run had listed nine. A session checking its hand placements with the plain run would wrongly see none left. Working practice: list and re-check NO-SENSE pairs with `--apply` (it is idempotent). A later run may make the plain run report them too, with a logged reason.
