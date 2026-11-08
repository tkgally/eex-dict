# Claim overflow across sources

*Observed 2026-11-07, run loylrr, cycle 2 (closure). Fixed 2026-11-08 (hundred-and-sixth lint): `claim.py --from-queue --n N` now treats N as the run's total, counting the slugs its claim file already holds, so repeating the same `--n` for the next source cannot pass the cap (test: `tools/tests/test_claim.py`).*

`routine-prompt.md` tells a closure cycle to claim from `--source closure`, then `--source family` and `--source crossref` "if fewer remain". `claim.py --from-queue --n 12 --source closure` returned one row; repeating the same `--n 12` with `--source family` claimed twelve more, so the claim file held thirteen, one over the cycle's cap. The extra row (`freezer-n`) was released by hand (`queue.py set ... pending` and an edit of the claim file).

Working practice until a fix: pass the remaining count to each later source (`--n 11` after one). Possible fix for a later run, with a logged reason: let `claim.py` take several `--source` values in order and stop at `--n` in total, or refuse a claim that would take the run's file past the cap.
