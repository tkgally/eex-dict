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
- [reviewer-noise](notes/reviewer-noise.md) — reviewer-a called all 10 sampled definitions "copied" in the first originality check, unsupported by search evidence in 7 of 10; updates through the fifth check (2026-09-23), where asking for a quoted source ended the false calls and produced the first verified "copied" call; the quote requirement joined the checklist question 2026-09-24; reviewer-a's determiner/pronoun confusion on `which-det` (2026-09-25); reviewer-b's repeated flag against the quoted headword in adaptation notes (2026-09-25).
- [review-panel-parse-failures](notes/review-panel-parse-failures.md) — `review_panel.py` recorded a hollow, zero-verdict "pass" when a reviewer's reply was truncated. Fixed 2026-09-20: `validate.py`'s `reviewed` gate now rejects a reviewer record that logged an error with zero verdicts instead of silently counting it.
- [review-panel-decide-collisions](notes/review-panel-decide-collisions.md) — `--decide` matched the last verdict for a field/role, so two distinct issues on the same field collided in the decision ledger. Fixed 2026-09-20: `--decide --quote "<text>"` disambiguates; ambiguous with no `--quote` now errors and logs nothing.
- [lint-vocab-pos-guess-gap](notes/lint-vocab-pos-guess-gap.md) — `lint_vocab.py --queue`'s `pos_guess` defaulted an unrecognized base form to noun with no signal it was a guess (caught when *additional*, an adjective, was queued as `additional-n`). Fixed 2026-09-20: a closed adjective-suffix list catches more cases directly; the remaining noun default is flagged in the queue row's note.
- [pronounce-check-stale-flag](notes/pronounce-check-stale-flag.md) — `pronounce_check.py` added `pronunciation-disputed` to `provenance.flags` on a disputed verdict but never removed it once a later run re-verified the transcription; caught 2026-09-20 on `nobody-pron`. Fixed 2026-09-20: a new `update_disputed_flag` helper syncs the flag once both varieties are checked.
- [review-panel-decide-substring-collision](notes/review-panel-decide-substring-collision.md) — `--decide --quote` could not disambiguate two issues on the same field when one's quote was a substring of the other's; caught 2026-09-20 adjudicating `pick-up-phrv`, worked around with a manual decisions.jsonl line. Fixed 2026-09-20: `--decide --index N` selects by position among the numbered candidates.
- [inflect-uncountable-plural-gap](notes/inflect-uncountable-plural-gap.md) — `tools/inflect.py` can never record a rare recognized plural (*monies*) for a noun whose countability forces `NO_PLURAL`, even via the exceptions table; caught 2026-09-21 on `money-n`, worked around in `usage_note`. Fix due a later run.
- [metrics-duplicate-calls](notes/metrics-duplicate-calls.md) — `metrics.py` has been called twice in five past `build` runs (once per `routine-prompt.md`, once from `CLAUDE.md`'s generic checklist), leaving near-empty duplicate rows in `metrics/history.jsonl` that inflate `next_mode.py`'s run counts and can trigger `lint`/`originality` one run early. Caught 2026-09-21. Fixed 2026-09-23: `next_mode.py` counts one row per run id.
- [queue-stale-claimed-rows](notes/queue-stale-claimed-rows.md) — a queue row orphaned by an abandoned branch or an unreset release stays `claimed` forever, so `queue.py next` skips it; neither `claim.py --prune` nor `absorb_branch.py --residue` resets it. Caught 2026-09-22 on eleven conjunctions, recurred and spread (32 rows, all of `queue.tsv`'s `claimed` total, freed by hand in the eighth lint pass). Fixed 2026-09-23: `queue.py sync`, run by `claim.py --prune` and every build, resets them to `pending`.
- [lint-vocab-queue-note-duplication](notes/lint-vocab-queue-note-duplication.md) — `lint_vocab.py --all --queue` regenerates each queue row's note from the current scan, and `queue.py`'s literal-substring dedup misses near-duplicate rewordings, so a lemma still `pending` across repeat lint passes accumulates overlapping note text. Caught 2026-09-22. Fix due a later run.
- [review-panel-rerun-duplicate-records](notes/review-panel-rerun-duplicate-records.md) — re-running `review_panel.py <slug> --roles reviewer-b` after a hollow parse failure appended a duplicate reviewer-a record and kept the hollow reviewer-b one in `provenance.reviews`; caught 2026-09-23 on `unless-conj`, recurred the same day on `least-det`, both cleaned by hand. Fixed 2026-09-23: a re-run replaces that run's provenance lines.
- [lint-vocab-changed-base](notes/lint-vocab-changed-base.md) — the local `lint_vocab.py --gate --changed` passed a definition violation (*border* in `close-v`) that CI's gate, run against `origin/main`, caught; caught 2026-09-24. Fixed 2026-09-24: the cause was `git status` listing a new, untracked shard directory without its files; the tools now pass `--untracked-files=all`.
- [crossref-first-sense-backlinks](notes/crossref-first-sense-backlinks.md) — `crossref.py` put a sense back-link on the target's first sense when no sense named the source; five of 13 wrong 2026-09-24, two of 11 on 2026-09-25. Partly fixed 2026-09-25: the tool now picks the sense with the most shared definition words (77 percent right on the dictionary's 585 pairs, against 68); lint runs still check each back-link.
- [one-sense-signposts](notes/one-sense-signposts.md) — 45 one-sense entries carry a signpost against style guide section 4; `validate.py` does not check it. Three cleared by hand 2026-09-25; the rest are fixed when a review touches them; a validator warning is a possible later change.
