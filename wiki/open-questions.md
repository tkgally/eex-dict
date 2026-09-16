# Open questions for the owner

*Each question carries the working assumption the project is using meanwhile (framework section 5). When an answer arrives through `inbox/`, record it here with the date and the files updated, and move the question to the Answered section.*

## Open

1. **Drafting model.** Should drafting move from the Routine's own model to a flagship model on OpenRouter (`drafter_via_openrouter` in `config/routine-config.json`)? *Assumption:* no; the Routine drafts in-session until the owner has read the seed set and says otherwise.
2. **Reviewer B tier.** `reviewer-b` is a Flash-class model (`config/models.md`). If its measured precision (`tools/metrics.py`) is well below reviewer A's after twenty runs, should it be upgraded to the Pro-class candidate named there? *Assumption:* keep it until the numbers say otherwise; the lint mode reports the precision.
3. **Milestone-1 order.** The defining vocabulary is worked in queue order (function words and light verbs first, then the rest alphabetically within band 1) unless the owner prefers semantic fields. *Assumption:* queue order.

## Answered

(none yet)
