# reviewer-b's new model returns partial verdict lists

*Observed 2026-10-05 (`20261005T085206Z-cp7jp7`, the first review after the reviewer-b upgrade). Fix due a later run.*

`tools/review_panel.py` asks each reviewer for one verdict per checklist field. On its first day the Pro-class model that now fills the `reviewer-b` role ([reviewer-b-upgrade](../decisions/reviewer-b-upgrade.md)) answered with only its issues on three of eleven entries. Those three were *inside-n* (4 of 44 fields), *ourselves-pron* (1 of 39), and *time-n* (1 of 282, three times running). On the other eight entries it returned a full list. Its replies end normally, so they are not cut short. The tool stores such a reply with an error ("no verdict for N fields") beside the verdicts it got. `validate.py --gate` refuses only a record with *no* verdicts, so a partial record passes. On the large *time-n* entry, `reviewer-a` (an existing model) also returned only its issues (about 30 of 282 fields), as it may have done before on long entries.

A second problem showed up while retrying. A re-run with `--roles reviewer-b` merges into the review file and keeps only the *error-free* records of the other role. When the other role's record was also partial, the re-run dropped it from the file. `--report` and `--decide` then lose those issues, although the entry's provenance still lists them. The workaround was to re-run both roles together.

Possible fixes, for a later run with a logged reason:

1. Treat a field that is missing from a reply that otherwise parsed as `ok`, and record the count. This is honest only if the model did read those fields.
2. Strengthen the prompt: say that an `ok` verdict is required for every field, or ask for the list of issues plus an explicit list of fields checked.
3. Keep a partial record of the other role when merging a re-run.

Until then, adjudicate whatever issues a partial record holds. A review run counts the entry as read by that role, but says in its journal how many fields the reply covered.

**Recurrence, 2026-10-05 12:44 (`20261005T124424Z-wa1mcj`).** Three of twelve new entries again: *a-lot-adv* (2 of 43 fields), *man-n* (4 of 94), *manner-n* (17 of 58). Re-running both roles together gave full lists for *man-n* and *manner-n*; *a-lot-adv* stayed partial (5 of 43). Twice in one day: the fix should come in the next lint run.

**Recurrence, 2026-10-05 16:48 (`20261005T164836Z-kb063q`).** Worse: six of ten new nouns on the first pass, two of them (*middle-n*, *midnight-n*) with no verdict list at all (`finish=error`, the reply cut off mid-list). One re-run of both roles filled *midnight* and *milk*; *middle* needed a third call. *message-n* (0 of 38), *minister-n* (0 of 34), and *minute-n* (2 of 77) stayed partial, issues only. Three runs running: fix 2 (a stronger prompt) or fix 1 should be the next lint's first job.
