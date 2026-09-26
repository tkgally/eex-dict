# Cycle restart needs a force push the harness may refuse

*Observed 2026-09-26, run `20260926T153320Z-ngyr08`. Status: open; worked around.*

**What happened.** `routine-prompt.md` (Run shape, step 3, and section 6, step 6) restarts the branch from the merged `main` for each new cycle and pushes with `--force-with-lease`. In this session the harness's permission check refused a `--force-with-lease` push (it classes a force push as destructive), even on cycle 1, when the branch did not yet exist on the remote.

**Workaround.** Cycle 1 used a plain `git push -u`. From cycle 2 on, instead of `git checkout -B <branch> origin/main`, the session ran `git merge origin/main --no-edit` on the branch after each squash merge. The branch's tree then equals `main`'s, and the next pull request's diff holds only the new cycle's work, so no history is rewritten and a plain push works. Both later pull requests merged cleanly.

**Possible fix (a later run, with a logged reason).** Change the cycle-restart step to merge `origin/main` into the branch, with a plain push, when a force push is refused. `routine-prompt.md` is near its 2,500-word cap, so trim first.
