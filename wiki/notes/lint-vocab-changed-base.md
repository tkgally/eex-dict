# lint_vocab --changed misses violations without --base

*Observed 2026-09-24, build run 20260924T004259Z-o9up51. [tooling]*

`python3 tools/lint_vocab.py --gate --changed`, run locally as `routine-prompt.md` section 6 step 3 says, passed while `close-v` sense 4 still used **border** (outside the defining vocabulary, no entry). CI runs the same gate against `origin/main` and failed the pull request on it. `--changed --base origin/main` reproduced the failure locally. It looks as if the default base did not count new, uncommitted entry files as changed, though the same local run did catch `chop-v`. Workaround: run the local gate with `--base origin/main`. Fix due a later run: make the default base match CI, or add `--base origin/main` to the gate line in `routine-prompt.md`, with a logged reason.
