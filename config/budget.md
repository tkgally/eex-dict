# Budget

- **Cap:** US$5.00 per UTC day for paid model calls, all runs combined, measured by the billed `usage.cost` that OpenRouter returns when a request includes `usage: {"include": true}`.
- **Before any paid call:** `python3 tools/spend.py check --cost <estimate>`; the tool refuses an estimate that would take the day over the cap, and the run then does a $0 unit instead.
- **After every paid call:** `python3 tools/spend.py record --cost <actual> --purpose <what> --model <slug>` (the tool library `tools/openrouter.py` does both when called through `call_with_budget`).
- **Per run:** `config/routine-config.json` sets a per-run ceiling (`per_run_cap_usd`) below the daily cap so that six runs can share a day.
- **The ledger:** `config/budget-ledger.json`, written only by `tools/spend.py`; the day resets at UTC midnight and the previous day's total moves to `history`.
- **The key** is `OPENROUTER_API_KEY` in the environment. Never print, log, or commit it. No `OPENROUTER_API_KEY` means no paid calls: the run does an unpaid unit and says so.
- **The founding session** (2026-09-16) worked under the same cap; its pronunciation test and seed-set reviews were allowed to spread across two UTC days.
