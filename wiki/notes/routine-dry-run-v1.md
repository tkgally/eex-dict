# Routine dry run v1: five entries by the prompt, as a Sonnet-class run

*Founding session, 2026-09-16. A Sonnet-class model followed `routine-prompt.md` literally through the unpaid half of a build cycle (pre-flight, selector, claims, drafting, validation, inflection, vocabulary lint, cross-references, queue sync), under run id `20260916T154500Z-dryrun`; the paid steps (pronunciation panel, reviewers) and the merge were left to the founding session because the day's budget was spent. Entries: *a*, *all*, *an*, *another*, *any* (all determiners, the queue's first rows after the queue order was changed to work function words first).*

**What worked.** The selector refused build correctly (draft ceiling reached, budget spent) and chose a free mode; forced to build, the claim, the drafting, and every tool ran; the five entries validated with no errors after one vocabulary fix (*extent* in a core idea); inflection, lint, cross-reference, and queue sync behaved as documented; the journal and log texts the run drafted met the framework's contract without any template.

**What the run found, and what changed.**
- The prompt's reading order omitted `resume-prompt.md` and did not name the schema and vocabulary files, which a drafter needs to produce a valid entry; both are now named, with the instruction to read one existing entry of the same part of speech as a model of the shape.
- `provenance.drafted_by` had no stated convention (the seed set records the founding model, the dry run wrote its own name); the convention is now the drafter role's slug from `config/models.md`, recorded in [conventions](../conventions.md).
- `tools/entry_path.py` took one slug where every other tool takes several; it now takes several.
- A forced build with `max_new_entries` 0 would have claimed nothing; the prompt now says what a run does in that case (review if drafts exist, else lint).
- The prompt now warns that reading and drafting is the expensive part of a run and that ten to fifteen substantial entries beat twenty thin ones.

**Left as designed.** The draft ceiling of 40 is a real limit: the founding session itself exceeded it with 82 drafts and must review them before its own merge, which is the rule working. The section-0 procedures are long for the common case of nothing to rescue, but a run that skips them is the failure mode they exist to prevent. Decision pages are read only when a rule is cited.

**Follow-up.** After the first real runs, compare their journal entries with the dry run's draft (kept in the founding session's transcript, not in the repository) and trim the prompt where the runs show it is not read.
