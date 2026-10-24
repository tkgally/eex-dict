# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-24 by the interactive session carrying out the owner's rulings of 2026-10-24 (group 3 of 6).*

## State

- 2,781 entries, all `reviewed`. Queue: about 5,490 pending; 963 entries have had one panel round.
- The owner's rulings of 2026-10-24 are in progress: status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md). Groups 1 (rulings), 2 (site), 3 (tools and rules) merged; 4 (band vote, build order), 5 (IPA format), 6 (this file, report) to come in the same session.
- Spend 2026-10-24: about US$3.21 of US$15 before the band vote.

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; they outrank the rest). Entry work for the Routine, in this order:
   1. **B3 review**: the appendix errors of the rulings file, full pipeline, normal caps (`run-v` and `get-v` misplaced back-links first).
   2. **B4 (i)**: add `separable`/`inseparable` to `grammar_codes` in the same pull request as the first phrasal verb that uses them, through the full pipeline ([consistency-rules](wiki/decisions/consistency-rules.md)).
   3. **C1 audit**: mirror synonym, antonym, and compare links with no note, 40 entries a batch; `crossref.py --missing-senses` and its `NO-SENSE` lines list candidates; nine references to ruled-out targets (`check_links.py`).
   4. **Build** in the order of [build-order](wiki/decisions/build-order.md) (milestone 1 first, grammar terms first) once group 4 lands; until then band order.
   5. **Review** in the order of [reviewer-house-rules](wiki/decisions/reviewer-house-rules.md) (E2): drafts, B3, the coverage pass over the top 500 band-1 entries, then the backlog by band.
   6. **reviewer-b check** after two lint passes under the new prompt (E1): under about 0.5 issues per entry → trial another non-Anthropic model on 40 entries.
   7. **Weekly digest**: due now (`tools/digest.py due`); the first run to see `signals.digest_due` writes it.
1. **build**: claim, draft, pipeline. Check any verb + preposition row against the verb's senses; check a `phr` row against the keyword entry's phrases; a clipping (*ad*, *app*) is a noun; flag disputed particle stress on phrasal verbs and keep stress on the particle; run the panel in chunks of four or five.
2. **review**: as item 0.5. Clear the signpost on any one-sense entry a review opens (36 left).
3. **closure**: paused above band 2 (A3); check every closure row for an inflected form or a guessed part of speech before drafting.
4. **lint**: every ten runs now (`config/routine-config.json`); the eighty-fifth pass ran 2026-10-24 01:10, so the next is due in about eight runs. Add the reports `lint_vocab.py --promises --circular` and `crossref.py --missing-senses`.
5. **Tooling notes still open** (`wiki/notes/`): `homograph-queue-and-inflection` (second homographs such as `rest-n-2`, `fan-n-2`, `rock-n-2`, `race-n-2` cannot be queued), `inflect-uncountable-plural-gap`, `lint-vocab-queue-note-duplication`, `pronounce-check-word-break`, `phrasal-verb-stress-recheck`. The wiki is at about 29,500 of 30,000 words: trim before adding.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them. Change a line there only when the rule it names changes.
- No script writes a model-owned field. The one exception is the IPA period script of ruling B4 (iv), [consistency-rules](wiki/decisions/consistency-rules.md).
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand in a review. A review that removes a cross-reference removes its mirror too.
- Cross-references to a slug with no entry are allowed (that is how closure finds words). The site shows them grey or hides them (ruling C2).
- Word links: the closed list `no_link_words` changes only by an owner ruling (C4).
- Rows a tool queues keep their hyphens and periods (`queue.py repair-forms`). Drafts keep them too (*T-shirt*, *-ible*, *a.m.*).
- *pen* the enclosure, *bat* the club, and other unrelated homographs are separate entries (`-n-2`), never senses.
- Set hand-written provenance timestamps from `date -u`, never ahead of the clock. Call `metrics.py` once per run, in wrap-up only.

## For the owner

- Your rulings of 2026-10-24 are being carried out. The status table above shows what is done. The final report of this session will say what remains.
- Still open from before: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`). The pronunciation disputes are in `reviews/needs_curator.txt`.
- The public site: <https://tkgally.github.io/eex-dict/>.
