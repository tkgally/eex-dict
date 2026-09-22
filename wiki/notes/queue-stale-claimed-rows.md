# Stale `claimed` queue rows with no backing claim file

Caught 2026-09-22, build run 32. Eleven band-1, defining-vocabulary conjunctions — *although, as, but, if, nor, once, or, since, so, though, unless* — sit at `headwords/queue.tsv` status `claimed`, each with no `headwords/claims/*.json` file, on `main` or any branch, listing them (`claim.py --taken` does not report them as taken). `queue.py next` only ever returns rows with `status == "pending"` (`tools/queue.py` line 171), so these eleven are permanently invisible to `queue.py next` and `claim.py --from-queue`, even though nothing actually holds them.

Likely origin: a run claimed them (which calls `queue.py set <headword> <pos> claimed`) on a branch that was later abandoned before its entries were committed, and neither `claim.py --prune` nor `tools/absorb_branch.py --residue` resets the queue row to `pending` when a claim file disappears without a merge — both only prune stale *claim files*, not stale *queue statuses*.

Effect: eleven common conjunctions, several already referenced from existing entries (*because-conj*, *and-conj*, *when-conj*, *whether-conj*, *yet-conj* all name one or more of them in `compare`/`synonyms`/`see_also`), cannot be drafted through the normal build pipeline until their queue rows are corrected by hand or by a tool fix.

Fix due a later run: either a `queue.py` subcommand that resets a `claimed` row to `pending` when no claim file anywhere lists its slug (checked the same way `claim.py --taken` does), or have `claim.py --prune` do this as a second pass. Until fixed, a session can work around it with `python3 tools/queue.py set "<headword>" conj pending --note "stale claim, no backing file, see queue-stale-claimed-rows.md"` before claiming.
