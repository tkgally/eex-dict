# Process overhead: lint spacing, the baton's word cap, one journal per run, the weekly digest, pace (2026-10-24)

*The owner's rulings E3 and E5 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)).*

## E3. Overhead

1. **Spacing.** In `config/routine-config.json`, `lint_every_runs` goes from 5 to 10 and `originality_every_runs` from 10 to 20.
2. **`NEXT.md` is capped at 1,000 words as well as 60 lines**, enforced by `tools/check_caps.py`; `CLAUDE.md` rule 9 and `resume-prompt.md` say so. The run-by-run history lives in `wiki/log.md`, which already holds it; `NEXT.md` keeps state, queue, fences, and what awaits the owner, and nothing else. This changes the 60-line rule of [knowledge-base-and-caps](knowledge-base-and-caps.md) by adding a second cap; the line cap stays.
3. **One journal report per run, not per cycle**, which matches the charter's "a journal entry per session". Each cycle still merges on its own, so each cycle adds its own section to the run's single file: the first cycle creates `journal/YYYY-MM-DD.md` (or the next free `-2`, `-3`) and records its name with `tools/run_clock.py journal`, and each later cycle appends a section headed `## Cycle N: <mode>`. The 300-to-800-word range applies to each cycle's section. `routine-prompt.md` section 6 says so; `framework.md` already asks for one report per session and needs no change.
4. **A weekly digest** for the owner, `journal/digest-YYYY-MM-DD.md`. It is written by the first run that starts seven days or more after the last digest; `tools/next_mode.py` reports `signals.digest_due`, and pre-flight writes it before the cycle's unit. `tools/digest.py` gathers the numbers. The session writes the digest in plain English, at most 800 words, and covers:
   - entries built and reviewed;
   - quality numbers: applied fixes per entry and reviewer yield;
   - the owner's sample and the escalation list ([owner-in-the-loop](owner-in-the-loop.md));
   - open questions;
   - anything that needs the owner.

## E5. Pace

- The run schedule lives outside the repository, and nothing in the repository depends on it. `routine-prompt.md` no longer says how often runs happen. This applies [cadence-and-model](cadence-and-model.md).
- When A1 and A2 are done ([rebanding](rebanding.md), [build-order](build-order.md)) and the first coverage block of about 100 entries has been reviewed ([reviewer-house-rules](reviewer-house-rules.md)), the session that sees it says so under "For the owner" in `NEXT.md` and in the next digest. The owner will then raise the cadence to three or four runs a day.
