# review_panel.py: a single-role re-run duplicates provenance records

*Observed 2026-09-23 (build run `20260923T004319Z-uh7a74`). `[tooling]`. Fix due a later run.*

**What happened.** On `unless-conj`, reviewer-b's first reply failed to parse (`no verdicts list in the reply`), leaving a hollow reviewer-b record (`ok: 0`, `issues: 0`). Re-running `python3 tools/review_panel.py unless-conj --roles reviewer-b` produced a good reviewer-b review, but `provenance.reviews` then held four records: the first reviewer-a, the hollow reviewer-b, a second copy of the reviewer-a record, and the new reviewer-b. The re-run appends a record for every role present in the review file, not only the role it called, and never replaces the hollow record.

**Workaround used.** Kept the last two records (one per role) by hand; `provenance.reviews` is script-owned, so this touched no semantic field. Noted in the entry's `provenance.notes`.

**Suggested fix.** On a `--roles` re-run, replace the existing record for the same `run_id` and role instead of appending, and write records only for the roles called. A unit test with a hollow first record would pin it.

**Recurred 2026-09-23** (review run `20260923T124315Z-orpgu2`) on `least-det`: same four-record result, same hand workaround.
