# reviewer-b low yield since 2026-10-08

*Observation, written by the fifty-sixth lint pass (2026-10-09). No change made; a later run decides.*

**What was seen.** Over the 50 entries put through the panel between the fifty-fifth lint (2026-10-08 20:50) and the fifty-sixth, reviewer-b raised 5 issues in all; 3 were applied (0.06 applied per entry). Over the 42 entries before the fifty-fifth lint it was 0.07. At the forty-eighth lint it was 0.24. Its replies are complete: every record holds a verdict for every field (34 to 72 fields each), so this is not the partial-reply fault of [reviewer-b-partial-verdicts](reviewer-b-partial-verdicts.md). Over the same entries reviewer-a raised dozens of issues, about 70 percent applied, many on fields reviewer-b marked `ok`.

**Why it matters.** The pipeline's second reading is now mostly one reviewer. A factual disagreement between reviewers, which is the trigger for open-data checks and curator flags, can hardly arise when one of them almost never objects.

**Possible causes, not tested.** The 2026-10-06 softening of the warning line in its prompt; the Pro-class model being more lenient than its predecessor; entries now drafted more carefully after reviewer-a's earlier catches.

**Possible remedies, for a later run with a logged reason.** Sample five entries reviewer-a found real faults in and check whether reviewer-b's `ok` verdicts on those fields were wrong; if so, a prompt line asking it to look for missing senses and unnatural examples, or a model change in `config/models.md` (an owner matter).

**Fifty-seventh lint (2026-10-09).** Over the 58 entries since the fifty-sixth lint, reviewer-b's yield was 0.26 applied per entry (15 of 30 decisions applied). The fall did not persist; no remedy is needed for now.

**2026-10-09 20:44 review cycle.** reviewer-b returned complete replies with no issues at all on twelve second-round nouns (*emergency*–*error*), where reviewer-a raised 23 and 11 were applied (several real: a misplaced example in `end-n`, regional verb agreement in `enemy-n`, `bug-n` as a false synonym in `error-n`). With the previous build's 2 issues over 12, that is two cycles in a row under the 0.10 line. The sampling check above is now worth running at the next lint.

**Fifty-ninth lint (2026-10-10): the sampling check.** Every blocking issue from reviewer-a that was applied between 2026-10-09 20:40 and this lint (four panel cycles, 48 entries) was matched against reviewer-b's verdict on the same field. Of 36 fields with a reviewer-b verdict, reviewer-b said `ok` on 34. Five read by hand were real faults it passed: an example that showed another sense (`end-n`), a wrong regional verb-agreement claim (`enemy-n`), a false synonym (`error-n`), a sense that was only a shortened phrase (`weather-n`), a translator note that excluded pocket watches (`watch-n`). So reviewer-b's `ok` is weak evidence that a field is sound; in practice the second reading is reviewer-a plus the session. Remedy for a later run, with a logged reason: a prompt line telling reviewer-b to test each example against its sense's definition and each note's claims for truth; whether to change the model is the owner's decision (`config/models.md`).

