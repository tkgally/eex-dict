# Open questions for the owner

*Each question carries the working assumption the project is using meanwhile (framework section 5). When an answer arrives through `inbox/`, record it here with the date and the files updated, and move the question to the Answered section.*

## Open

1. **Drafting model.** Should drafting move from the Routine's own model to a flagship model on OpenRouter (`drafter_via_openrouter` in `config/routine-config.json`)? *Assumption:* no; the Routine drafts in-session until the owner has read the seed set and says otherwise.
2. **Reviewer B tier.** `reviewer-b` is a Flash-class model (`config/models.md`). If its measured precision (`tools/metrics.py`) is well below reviewer A's after twenty runs, should it be upgraded to the Pro-class candidate named there? *Assumption:* keep it until the numbers say otherwise; the lint mode reports the precision.
3. **Milestone-1 order.** The defining vocabulary is worked in queue order (function words and light verbs first, then the rest alphabetically within band 1) unless the owner prefers semantic fields. *Assumption:* queue order.
4. **Auxiliary and pronoun uses inside the seed entries** (raised 2026-09-18 by the part-of-speech rule in [part-of-speech-and-consistency](decisions/part-of-speech-and-consistency.md)). `be-v`, `have-v`, and `do-v` carry their auxiliary uses as senses, and `one-num` carries the pronoun uses (*a red one*, *one should*), by a judgment call the seed drafters flagged; the queue rows *be aux*, *have aux*, *do aux*, *one pron* are marked duplicate. The rule now says a use of another part of speech gets its own entry. Should the four entries be split (four new entries through the full pipeline, the moved senses deleted from the old ones), or stay as they are as a recorded exception for the closed classes? *Assumption:* they stay as they are; every new entry follows the rule; a ruling to split is done by the review mode, one entry per run.
5. **The look of the marks.** The site shows a word named as a word in bold, a quoted illustration in italics, and the headword in an example sentence in bold (the example itself is in italics). If the owner prefers a colour or another weight, it is one line each in `tools/site/site.css` (`.mention`, `.illus`, `.ex-hw`); the data does not change. *Assumption:* bold and italic as described.

## Answered

(none yet)
