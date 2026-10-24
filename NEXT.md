# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-24 by scheduled run 20261024T164356Z-ofeeve, cycle 3 (build: twelve entries, *twelve* to *bore*). Cycles 1 (build) and 2 (site) merged.*

## State

- 2,828 entries, all `reviewed`. Milestone 1: about 234 rows left (the grammar terms are done). The first weekly digest is `journal/digest-2026-10-24.md`.
- Bands re-voted 2026-10-24 ([record](experiments/band-vote-2026-10-24/README.md)). A row a tool queues is `unbanded` until the next vote.
- Spend 2026-10-24: about US$11.35 of US$15.

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **B3 review**, the rest of the appendix: `manner-n` (the *Dr. Lee* example); `proud-adj` s4, `light-adj` s2 and *make light of*, `dull-adj` s4 and a "slow to understand" sense; the invented learner errors in `transport-v`, `recent-adj`, `well-adj`, `sign-n`, `drop-v`; then the missing senses, which open the coverage pass (`drop-v`, `service-n`, `into-prep`, `hard-adj`, `word-n` *have words* and *in words of one syllable*, `low-adj`, `fly-v`, `everything-pron`, `ours-pron`). Done 2026-10-24: back-links, the notes group, the numbers, the examples group, and the surname cases outside title entries.
   2. **B4 (i)**: add `separable`/`inseparable` to `grammar_codes` in the same pull request as the first phrasal verb that uses them ([consistency-rules](wiki/decisions/consistency-rules.md)). `go-on-phrv` sense 7 (*go on about*) and `give-up-phrv` are candidates.
   3. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates; nine references to ruled-out targets (`check_links.py`). The `active-adj`/`passive-adj` type mismatch (compare against antonym) belongs here.
   4. **Build** milestone 1 in queue order (`claim.py --from-queue`). Closure waits until it is built ([build-order](wiki/decisions/build-order.md)).
   5. **Review** (E2): first two small fixes from 2026-10-24: `fifty-num` sense 3 to *with a value of 50* (as `twenty-num`); `eleven-num`/`ten-num` word family (no shared form: move to see_also, both sides). Then drafts, the B3 list, the B1 coverage pass over the 500 most important band-1 entries, then the one-round backlog by band.
   6. **reviewer-b** (E1): after two lint passes under the new prompt, if it raises fewer than about 0.5 issues per entry, trial another non-Anthropic model on 40 entries.
   7. **Weekly digest**: next when `signals.digest_due`. Entry reports: pre-flight step 5.
   8. **E5**: when milestone 1 is built and the first coverage block of about 100 entries is reviewed, say so under "For the owner" and in the digest.
1. **build**: check a verb + preposition row against the verb's senses and a `phr` row against the keyword entry's phrases (*of course* adverb was such a row: set `duplicate` 2026-10-24); run the panel in chunks of four or five; place every `NO-SENSE` back-link by hand.
2. **review**: reviewer-b keeps objecting to quotation marks around words mentioned in examples, and both reviewers ask for phrasal verbs and compounds as senses; reject both, with the reason. `verb + adjective` is not a collocation type.
3. **closure**: blocked by milestone 1, then paused above band 2 (A3).
4. **lint**: every ten runs; next due in about three runs. Add `lint_vocab.py --promises --circular`, `crossref.py --missing-senses`, and `band_vote.py run --unbanded` (rows are unbanded: `passive-n`, `my-interj`, `fourth-n`, `fifth-n`, `fifty-fifty-adj`, the ordinals *eleventh* to *ninetieth*, and others).
5. **Tooling notes still open** (`wiki/notes/`): `homograph-queue-and-inflection`, `inflect-uncountable-plural-gap`, `lint-vocab-queue-note-duplication`, `pronounce-check-word-break`, `phrasal-verb-stress-recheck`. The wiki is at about 29,500 of 30,000 words: trim before adding.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them.
- No script writes a model-owned field; the one exception is `tools/ipa_format.py` (periods beside stress marks only, ruling B4 iv).
- IPA house form: no period beside a stress mark. Bands come only from the band vote; never set one by hand.
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand. A review that removes a cross-reference removes its mirror too.
- Number entries (`-num`) hold their card, score, and size uses and their uses before **of** (*three of us*); reviewers asking for noun or pronoun entries for these are rejected. Tens (*forty* to *ninety*) carry a plural sense, *in her forties*; ordinals keep the date sense (*on the fourth*) but no adverbial *finished fourth*.
- Cross-references to a slug with no entry are allowed; the site shows them grey or hides them (C2). `no_link_words` changes only by an owner ruling (C4).
- Rows and drafts keep their hyphens and periods. Unrelated homographs are separate entries (`-n-2`), never senses.
- Hand-written provenance timestamps come from `date -u`. Call `metrics.py` once per cycle, in wrap-up only.

## For the owner

- The first weekly digest is ready: `journal/digest-2026-10-24.md` (ten entries to sample). Today's runs: `journal/2026-10-24-6.md`, `journal/2026-10-24-7.md` (cycles 1 to 3).
- New curator line: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; the names policy has no rule for title entries. Working assumption: allowed there until you rule.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- The public site: <https://tkgally.github.io/eex-dict/>.
