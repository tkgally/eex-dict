# Wiki index

*One line per page. Update in the same session as any page listed here. Read this first; then open only the pages the unit needs.*

## Rules and style

- [conventions](conventions.md) — the schema of this knowledge base and every file format the tools read or write: slugs, shards, run ids, claims, the queue, review files, the decision ledger, the budget ledger, metrics.
- [style-guide](style-guide.md) — the house style every drafting session reads: definitions, senses, examples, the inline marks, grammar, labels, boxes, phrases, adaptation notes, originality; three model entries (section 17).
- [open-questions](open-questions.md) — questions for the owner with the working assumption in force.

## Decisions (one page each; binding)

- [name-and-home](decisions/name-and-home.md) — the name, the repository, relative links.
- [reader-level](decisions/reader-level.md) — B1 to C2; plain definitions, complete entries.
- [variety-and-world-englishes](decisions/variety-and-world-englishes.md) — American primary, British in structured fields, World Englishes later.
- [size-and-pace](decisions/size-and-pace.md) — milestone 1 (about 2,500 defining words), 10,000 headwords, 20 entries per run.
- [headword-selection](decisions/headword-selection.md) — no external lists; model judgment settled editorially.
- [what-counts-as-a-headword](decisions/what-counts-as-a-headword.md) — phrasal verbs, idioms as sub-entries, affixes, abbreviations, derived words.
- [entry-unit-and-homographs](decisions/entry-unit-and-homographs.md) — one entry per headword plus part of speech.
- [definitions-and-explanations](decisions/definitions-and-explanations.md) — phrasal definition primary, optional explanation.
- [defining-vocabulary-rule](decisions/defining-vocabulary-rule.md) — the soft rule and the closure queue.
- [defining-vocabulary](decisions/defining-vocabulary.md) — how the 2,326-lemma list and the frequency bands were built from three models' judgment, with counts.
- [senses](decisions/senses.md) — order, splitting principle, core idea.
- [examples](decisions/examples.md) — two to four per sense, no real-world facts, the names policy.
- [grammar-codes](decisions/grammar-codes.md) — closed codes; labels and codes both shown; no abbreviations.
- [usage-labels](decisions/usage-labels.md) — the five original label sets and why.
- [taboo-vocabulary](decisions/taboo-vocabulary.md) — vulgar words in, slurs out, refusals recorded.
- [extras-and-etymology](decisions/extras-and-etymology.md) — boxes on every entry where they apply; etymology only when verified and relevant.
- [frequency-bands](decisions/frequency-bands.md) — editorial bands 1 to 5, no CEFR.
- [adaptation-layer](decisions/adaptation-layer.md) — five language-neutral note kinds and the l1 slots.
- [pronunciation](decisions/pronunciation.md) — American and British IPA from model knowledge, checked by agreement.
- [pronunciation-pipeline](decisions/pronunciation-pipeline.md) — the panel, the votes, and the two-vote agreement rule adopted from the experiment.
- [licence-and-openness](decisions/licence-and-openness.md) — CC0 data, MIT code, nothing vendored.
- [drafting-and-review](decisions/drafting-and-review.md) — in-session drafting, two non-Anthropic reviewers, closed verdicts.
- [verification](decisions/verification.md) — what is checked how; adjudication rules.
- [cadence-and-model](decisions/cadence-and-model.md) — one to six runs a day; nothing depends on model or cadence.
- [knowledge-base-and-caps](decisions/knowledge-base-and-caps.md) — the framework and the word caps.
- [owner-involvement](decisions/owner-involvement.md) — journal, curator queue, open questions, inbox.
- [slugs-and-ids](decisions/slugs-and-ids.md) — the slug is the ID; deterministic paths; renames by redirect.
- [site](decisions/site.md) — static, mobile-first, built by CI, checked by a Routine mode.
- [inline-markup](decisions/inline-markup.md) — the owner's ruling of 2026-09-18: words named as words and quoted illustrations are marked in the prose (`**word**`, `*phrase*`); the headword in examples is marked by the site; how the seed set is converted.
- [part-of-speech-and-consistency](decisions/part-of-speech-and-consistency.md) — one part of speech per entry, the entry agrees with itself, origin claims only in etymology, grammar exceptions named as such, pronunciation notes in plain words (from the seed-set feedback of 2026-09-18).

## Notes (observed problems, method records, experiment results)

- [pronunciation-model-test-v1](notes/pronunciation-model-test-v1.md) — the experiment result: model transcriptions against the CMU dictionary, the amended normalization, the adopted two-vote rule.
- [routine-dry-run-v1](notes/routine-dry-run-v1.md) — a Sonnet-class dry run of the Routine prompt: what worked, what the prompt got wrong, what changed.
- [inflection-exceptions-check](notes/inflection-exceptions-check.md) — the two-model check of the inflection exceptions table: what was applied and what was rejected.
- [seed-set-drafting](notes/seed-set-drafting.md) — how the seed set was drafted and the judgment calls the drafters flagged.
- [reviewer-precision](notes/reviewer-precision.md) — the first measurement of the two reviewers' precision by issue family on the seed set, the noise patterns, and the families the lint run should switch off.
- [reviewer-noise](notes/reviewer-noise.md) — reviewer-a called all 10 sampled definitions "copied" in the first originality check, unsupported by search evidence in 7 of 10; watch for a repeat.
- [review-panel-parse-failures](notes/review-panel-parse-failures.md) — `review_panel.py` recorded a hollow, zero-verdict "pass" when a reviewer's reply was truncated; a re-run fixed it. Suggested tooling fix noted for a later run.
