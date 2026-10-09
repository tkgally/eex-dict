# reviewer-b low yield since 2026-10-08

*Observation, written by the fifty-sixth lint pass (2026-10-09). No change made; a later run decides.*

**What was seen.** Over the 50 entries put through the panel between the fifty-fifth lint (2026-10-08 20:50) and the fifty-sixth, reviewer-b raised 5 issues in all; 3 were applied (0.06 applied per entry). Over the 42 entries before the fifty-fifth lint it was 0.07. At the forty-eighth lint it was 0.24. Its replies are complete: every record holds a verdict for every field (34 to 72 fields each), so this is not the partial-reply fault of [reviewer-b-partial-verdicts](reviewer-b-partial-verdicts.md). Over the same entries reviewer-a raised dozens of issues, about 70 percent applied, many on fields reviewer-b marked `ok`.

**Why it matters.** The pipeline's second reading is now mostly one reviewer. A factual disagreement between reviewers, which is the trigger for open-data checks and curator flags, can hardly arise when one of them almost never objects.

**Possible causes, not tested.** The 2026-10-06 softening of the warning line in its prompt; the Pro-class model being more lenient than its predecessor; entries now drafted more carefully after reviewer-a's earlier catches.

**Possible remedies, for a later run with a logged reason.** Sample five entries reviewer-a found real faults in and check whether reviewer-b's `ok` verdicts on those fields were wrong; if so, a prompt line asking it to look for missing senses and unnatural examples, or a model change in `config/models.md` (an owner matter).
