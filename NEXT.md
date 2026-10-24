# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-24 09:30 UTC by scheduled run 20261024T085738Z-jiwbqq, cycle 2 (review: the B3 appendix, first block).*

## State

- 2,793 entries, all `reviewed`. Queue: 5,490 pending; 963 entries have had one panel round. Milestone 1: 270 rows left.
- Bands re-voted 2026-10-24 ([record](experiments/band-vote-2026-10-24/README.md)): bands 1 to 5 hold 1,539, 3,157, 2,813, 753, 21 items. A row a tool queues is now `unbanded` until the next vote.
- Spend 2026-10-24: US$7.50 of US$15.

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; they outrank the rest; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). **Done:** the rulings file and decision pages; C2, C3, C4, D1 to D4 (site); C1 (the tools), A3, B2, B4 (ii) and (iii), E1, E3, E4, E5 (the wording); A1, A2 (the order), A4; B4 (iv). **Left for the Routine, in this order:**
   1. **B3 review**: the appendix errors of the rulings file, full pipeline, normal caps. **Done 2026-10-24:** the misplaced back-links and the "wrong or doubtful notes" group (except the numbers *two* to *ten*). **Left, in order:** the numbers *two* to *ten*; "wrong examples, collocations or synonyms" from `deal-n` on (`carefully-adv`, `entertainment-n` done); "definitions and codes"; the invented learner errors; the missing senses (these start the coverage pass).
   2. **B4 (i)**: add `separable`/`inseparable` to `grammar_codes` in the same pull request as the first phrasal verb that uses them, through the full pipeline ([consistency-rules](wiki/decisions/consistency-rules.md)).
   3. **C1 audit**: mirror synonym, antonym, and compare links with no note, at most 40 entries a batch. `crossref.py --missing-senses` lists 678 candidate pairs; nine references to ruled-out targets (`check_links.py` lists them).
   4. **Build** milestone 1: the first twelve grammar terms are built (2026-10-24); `claim.py --from-queue` gives the rest, then *receive*, *bar*, *exam*, *newspaper*... Closure waits until milestone 1 is built ([build-order](wiki/decisions/build-order.md)). A review of `word-n` should add the phrase *in words of one syllable*.
   5. **Review** (E2): drafts, the B3 list, the B1 coverage pass over the 500 most important band-1 entries (most senses first, then function words; start with `drop-v`, `service-n`, `like-prep`, `into-prep`, `go-on-phrv`, `hard-adj`), then the one-round backlog by band.
   6. **reviewer-b** (E1): after two lint passes under the new prompt, if it raises fewer than about 0.5 issues per entry, trial another non-Anthropic model on 40 entries.
   7. **Weekly digest** (E3, E4): the first was written 2026-10-24 (`journal/digest-2026-10-24.md`); next when `signals.digest_due`. Entry reports: pre-flight step 5 of `routine-prompt.md`.
   8. **E5**: when milestone 1 is built and the first coverage block of about 100 entries is reviewed, say so under "For the owner" and in the digest.
1. **build**: check a verb + preposition row against the verb's senses and a `phr` row against the keyword entry's phrases; a clipping (*ad*) is a noun; flag disputed particle stress on phrasal verbs, keep stress on the particle; run the panel in chunks of four or five; place every `NO-SENSE` back-link by hand.
2. **review**: as item 0.5; clear the signpost on any one-sense entry a review opens (36 left).
3. **closure**: blocked by milestone 1, then paused above band 2 (A3); check each row for an inflected form or a guessed part of speech.
4. **lint**: every ten runs now; next due in about seven runs. Add `lint_vocab.py --promises --circular` (11 broken promises, 319 circular definitions), `crossref.py --missing-senses`, and `band_vote.py run --unbanded` when rows are unbanded.
5. **Tooling notes still open** (`wiki/notes/`): `homograph-queue-and-inflection` (second homographs such as `rest-n-2`, `fan-n-2`, `rock-n-2` cannot be queued), `inflect-uncountable-plural-gap`, `lint-vocab-queue-note-duplication`, `pronounce-check-word-break`, `phrasal-verb-stress-recheck`. The wiki is at about 29,500 of 30,000 words: trim before adding.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them, and change a line there only when the rule it names changes.
- No script writes a model-owned field; the one exception is `tools/ipa_format.py` (periods beside stress marks only, ruling B4 iv).
- IPA house form: no period beside a stress mark (`prɪˈvɛnt`). Bands come only from the band vote; never set one by hand.
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand. A review that removes a cross-reference removes its mirror too.
- Cross-references to a slug with no entry are allowed; the site shows them grey or hides them (C2). `no_link_words` changes only by an owner ruling (C4).
- Rows and drafts keep their hyphens and periods (*T-shirt*, *-ible*, *a.m.*).
- Unrelated homographs are separate entries (`-n-2`), never senses.
- Hand-written provenance timestamps come from `date -u`. Call `metrics.py` once per run, in wrap-up only.

## For the owner

- Your rulings of 2026-10-24: every tooling, site, configuration, and rule part is done and merged; the entry work above is queued for the Routine (`journal/2026-10-24-5.md`).
- Still open from before: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- The public site: <https://tkgally.github.io/eex-dict/>.
