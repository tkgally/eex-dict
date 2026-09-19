# Review-panel parse failures

*Observed 2026-09-19, review run. A tooling problem, not a rule change — logged here per the no-speculation rule (CLAUDE.md); a fix is a later run's unit, with its own reason.*

On `talk-v`, `tools/review_panel.py` recorded a **reviewer-b** review with `issues: 0`, `blocking: 0`, `ok: 0` — a record that looks clean but is empty. The raw model reply was truncated mid-JSON (the tool's own error output showed `no verdicts list in the reply`), so the parser silently fell back to an empty, "no issues" result instead of surfacing the failure to the session. A re-run of `review_panel.py talk-v --roles reviewer-b` immediately after produced a normal review (4 issues), so the failure was not the entry's fault.

**Risk:** an entry could pass "both reviewer records present" (`conventions.md` section 4, the `reviewed` gate) on the strength of a hollow record that never actually checked anything, if a session did not think to compare `ok` against the entry's real field count.

**Suggested fix for a later run** (not made now): `review_panel.py` should treat a reply with zero total verdicts as a hard error (matching its existing "no verdicts list" error path) rather than writing a review file with `ok: 0, issues: 0`, so the pipeline retries or blocks instead of silently accepting an empty pass. Session workaround until then: after any review run, spot-check that a reviewer's `ok` count is roughly consistent with the entry's field count before treating the pair of reviews as satisfying the gate.
