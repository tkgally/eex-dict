# Reviewers: house rules, two required checks, coverage, review order (2026-10-24)

*The owner's rulings B1, E1, and E2 of 2026-10-24 (`inbox/archive/20261024_owner_rulings.txt`; status in [owner-rulings-2026-10-24](owner-rulings-2026-10-24.md)).*

## E1. House rules and required checks

- **House rules.** Both reviewers receive a compact list of settled house rulings, `config/reviewer-house-rules.md`, drawn from `NEXT.md`'s fences and the style guide. `tools/review_panel.py` reads it into the prompt. They should stop raising settled questions: about 5,050 of 15,054 adjudicated decisions were rejections at commit 194fab1. The file changes when a fence or a style rule changes; it is not a second rule book, so each line names the rule and where it lives.
- **Two required checks**, permanent lines in both reviewers' prompt, each answered as a verdict on its own field:
  - **`coverage`** (B1): "List the most frequent present-day uses, function-word uses, and idioms of this word. Is each covered by a sense, subsense, or phrase? Name any that is missing."
  - **`examples-fit`**: "Does every example fit its sense's definition? Name any that does not."
  - An issue on either check takes the issue family `coverage` or `example-unnatural` respectively; `coverage` is a new value of the closed vocabulary `issue_families`, added by this decision.
- **reviewer-b.** After two lint passes under the new prompt, if `reviewer-b` still raises fewer than about 0.5 issues per entry (0.39 at commit 194fab1, with nothing found on 77 percent of entries), a different non-Anthropic model, verified on the OpenRouter model list, is trialed on 40 entries; whichever finds more applied fixes is kept; the result is a logged decision and `config/models.md` is updated.

## B1. Coverage

- **Adjudication.** The adjudicator adds what is truly missing, through the full pipeline. A `coverage` issue is judged like any other: a rare or dated use is not missing.
- **A free signal.** An incoming synonym or antonym with no matching sense in the target (*sharp* "clever" lists *dull*, and *dull* has no "slow to understand" sense) is evidence of a missing sense. `tools/crossref.py --missing-senses` lists such pairs; it writes nothing.
- **The coverage pass** over the 500 most important band-1 entries (after the re-banding, [rebanding](rebanding.md)) runs as the review mode: polysemous content words first (most senses first), then function words. The B3 entries with missing senses (`drop-v`, `service-n`, `like-prep`, `into-prep`, ...) start it.
- **Function words.** The `explanation` field (style guide section 3) is expected on prepositions where the use is hard.

## E2. Second-round reviews: the order

The review mode's queue, in this order (`tools/next_mode.py` and `NEXT.md`):

1. drafts;
2. the B3 list (the appendix of the rulings file);
3. the B1 top 500, whether reviewed once or twice;
4. the rest of the one-round backlog (963 entries at commit 194fab1) by band after the re-banding, polysemous entries first, each with the coverage check.
