# Reviewer precision: the seed set (first measurement)

*Founding session, 2026-09-17. `python3 tools/metrics.py --precision` over the 798 adjudication lines for the 82 seed entries (run `20260916T134425Z-1yir52`). Precision is the share of a reviewer's issues that the session accepted (`apply`) rather than rejected; no issue was escalated. The lint run reads this page and switches off a family whose precision is under 30 percent for a role over twenty or more decisions (`routine-prompt.md`, lint mode).*

## Headline numbers

| role | issues decided | applied | precision |
|---|---|---|---|
| reviewer-a | 634 | 333 | 0.53 |
| reviewer-b | 164 | 34 | 0.21 |

Blocking issues: 525 (261 applied); minor: 273 (106 applied).

## Families under 30 percent with twenty or more decisions (candidates for switching off)

- reviewer-a **example-policy** 0.16 (44): almost every flag was a phrase with one example (the style guide allows one to three) or a generic example called a "checkable real-world claim" (*the wettest spring on record*, *a way of life for hundreds of years*).
- reviewer-a **grammar-code** 0.26 (73): patterns asked for adjectives, nouns, determiners, and modals that the closed verb-pattern list does not have; *often before another noun* read as a restriction; *comparative with more* read as missing the superlative.
- reviewer-a **sense-structure** 0.29 (42): sense splits the splitting principle does not license; one flag withdrew itself mid-sentence.
- reviewer-b **example-policy** 0.02 (81): the one-example-per-phrase flag, repeated on every phrase of every entry.
- reviewer-b **explanation** 0.06 (17, under the threshold): the explanation field on high-frequency verbs, modals, and abbreviations, which style guide section 3 allows.

The strongest families: definition-meaning 0.78, usage-note 0.75, synonym-discrimination 0.75 (reviewer-a); every reviewer-b collocation, cross-reference, and example-unnatural flag was applied, but there were few of them.

## Noise patterns, and what was done about them

Both reviewers were told the house conventions in the prompt and still flagged them. The list in `tools/review_panel.py` (`SYSTEM`) was extended after this run with the conventions the seed set exposed: entry-level labels cover every sense and phrase; monosyllables carry no stress mark; British transcriptions mark no linking r; respellings in pronunciation notes; etymologies name languages; explanations on use-hard verbs and modals; the closed pattern list; compounds in word families; a subsense with its own countability; generic examples. Two rules the flags exposed as real gaps went into the style guide: a subsense limited to one form (*look after yourself*) states the form in its explanation, not as a prefix in the definition; adaptation notes hedge claims about other languages (*often*, *many languages*), never *most* or *all*.

The largest genuine family was **adaptation** (reviewer-a, 0.65 over 130): unsupported "most languages" claims, and a few plain errors (*a hand, never hands*; *English always needs it*). The reviewers were also right about a dozen circular or prefixed subsense definitions, about *smell of* under the cause sense of *of*, and about *take someone to court* hiding in a movement sense.

## What the next lint run should do

Apply the 30-percent rule to reviewer-a example-policy and grammar-code and to reviewer-b example-policy, unless the extended prompt has already brought them above the line on the next twenty decisions; re-measure after each review run and append the table here.
