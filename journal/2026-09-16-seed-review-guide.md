# How to review the seed set

*A one-page guide for Tom, written by the founding session on 2026-09-16. The seed set is the first batch of dictionary entries, written to be the standard that every later entry is measured against. Nothing else in the project needs your attention as urgently as this.*

## What the seed set is

About 75 entries chosen to exercise every part of the design: heavily polysemous verbs (*run*, *take*, *make*, *get*, *go*), the verbs *be*, *have*, *do*, speech and perception verbs with their confusable pairs (*say* / *tell*, *speak* / *talk*, *borrow* / *lend*), nouns with idioms (*hand*, *head*, *time*, *way*), grammar-trap nouns (*information*, *advice*, *news*, *scissors*, *police*, *people*, *family*), the heteronym pair *record* (noun and verb), a British-variant word (*color*), a vulgar word handled by the policy (*shit*), adjectives with position restrictions (*asleep*, *main*, *alone*, *afraid*), discourse adverbs (*however*, *actually*, *anyway*), function words with explanations (*the*, *of*, *and*, *because*, *it*, *some*, *one*, *in spite of*, *each other*), modals (*can*, *must*, *used to*), phrasal verbs (*give up*, *look after*, *pick up*), an affix pair (*un-*, *-ness*), abbreviations (*asap*, *tv*), and *o'clock*. Every one went through the full pipeline: validation, inflection rules, a pronunciation check by a panel of models, two reviewers reading every field, and adjudication by the session, with each decision logged.

## Where to read them

- **On the site**, once GitHub Pages is enabled (Settings, Pages, Source: GitHub Actions): the home page lists the entries; each entry page shows everything, and the "translator's view" toggle in the header reveals the adaptation notes.
- **In the repository**: one JSON file per entry under `entries/` (for example `entries/ru/run-v.json`); the reviewers' verdicts under `reviews/<run-id>/`; the session's decisions on every flagged field in `reviews/decisions.jsonl`; the house style in `wiki/style-guide.md`.

## What to look at, in order of value

1. **Definitions.** Are they plain enough for an intermediate reader and right? Is the phrasal style what you want, or would you rather have full-sentence definitions? (This is a charter-level choice; say so and the style guide changes before more entries are written.)
2. **Sense division and order.** Too many senses, too few, wrong order? The splitting principle is in the style guide, section 4; if the entries over-split or under-split, the principle needs rewording, not the entries.
3. **Examples.** Natural? Neutral in setting? Showing the patterns and collocations you would want? The names policy and the no-facts rule are in section 5.
4. **Grammar codes, patterns, and labels.** Wrong codes are the reviewers' most frequent finding; a code that is systematically wrong points at a vocabulary definition to fix.
5. **The extras**: collocation boxes, word families, synonym discrimination, learner errors, the five kinds of adaptation notes. Are they the right size? Are the adaptation notes useful to a translator, or padding?
6. **Pronunciation.** The panel check and its agreement rule are explained in the journal; a transcription marked `disputed` on the site is one the models disagreed about.
7. **The reviewers' precision.** `python3 tools/metrics.py --precision` prints, for each reviewer and issue family, how often the session accepted its flags. A family with very low precision can be switched off.

## How to respond

Drop a file into `inbox/` (any name, markdown or plain text). The next session reads it before anything else, acts on it or records your ruling, and moves it to `inbox/archive/`. Useful things to say:

- "Entry X, sense N: ..." for a specific correction; the session fixes it and logs the decision.
- "Rule: ..." for a change to the style guide or a vocabulary; the session changes the rule, records the decision page, and revises the seed entries that the rule affects.
- "Drafting: keep in-session / move to <model>" to settle the open question on the drafting model.
- "Start the Routine" when you are satisfied; until then the Routine is not scheduled.

You do not need to comment on every entry. Silence on an entry means it stands as the standard.
