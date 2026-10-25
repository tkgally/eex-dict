# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-25 by scheduled run 20261025T013145Z-6h9f7u, cycle 4 of 4 (originality, forty-fourth check). Cycles 1 to 3 merged.*

## State

- 2,840 entries, all `reviewed`. Milestone 1: about 220 rows left. Last weekly digest: `journal/digest-2026-10-24.md`.
- Bands re-voted 2026-10-24 ([record](experiments/band-vote-2026-10-24/README.md)). A row a tool queues is `unbanded` until the next vote.
- Spend 2026-10-25 so far: about US$3.36 of US$15. Originality: last 2026-10-25, next due in twenty runs.

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **B3 review**: finished 2026-10-25. The missing senses opened the coverage pass; continue it under item 5.
   2. **B4 (i)**: add `separable`/`inseparable` to `grammar_codes` in the same pull request as the first phrasal verb that uses them ([consistency-rules](wiki/decisions/consistency-rules.md)). `go-on-phrv` sense 7 (*go on about*) and `give-up-phrv` are candidates.
   3. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates; eight references to ruled-out targets (`check_links.py`). The `active-adj`/`passive-adj` and `alone-adj`/`lonely-adj` type mismatches belong here.
   4. **Build** milestone 1 in queue order (`claim.py --from-queue`). Closure waits until it is built ([build-order](wiki/decisions/build-order.md)).
   5. **Review** (E2): drafts, open entry reports, the B1 coverage pass over the 500 most important band-1 entries, then the one-round backlog by band.
   6. **reviewer-b** (E1): after two lint passes under the new prompt, if it raises fewer than about 0.5 issues per entry, trial another non-Anthropic model on 40 entries.
   7. **Weekly digest**: next when `signals.digest_due`. Entry reports: pre-flight step 5.
   8. **E5**: when milestone 1 is built and the first coverage block of about 100 entries is reviewed, say so under "For the owner" and in the digest.
1. **build**: check a verb + preposition row against the verb's senses and a `phr` row against the keyword entry's phrases; run the panel in chunks of four or five; place every `NO-SENSE` back-link by hand.
2. **originality**: ask reviewer-a with `--reasoning-effort off` (with reasoning on it spends every token before answering); it still quotes our own text back as Cambridge's, so the search decides.
3. **review**: reviewer-b keeps objecting to quotation marks around words mentioned in examples, and both reviewers ask for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*, *travel light*); reject all, with the reason. `verb + adjective` is not a collocation type.
4. **closure**: blocked by milestone 1, then paused above band 2 (A3).
5. **lint**: every ten runs; last 2026-10-24 (eighty-sixth pass), next due in six runs. `reviewer-a` `coverage` precision is low but stays live (ruling B1).
6. **Tooling notes still open** (`wiki/notes/`): `homograph-queue-and-inflection`, `inflect-uncountable-plural-gap`, `lint-vocab-queue-note-duplication`, `pronounce-check-word-break`, `phrasal-verb-stress-recheck`, `band-vote-unbanded-overwrite`. The wiki is at about 29,800 of 30,000 words: trim before adding.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them.
- No script writes a model-owned field; the one exception is `tools/ipa_format.py` (periods beside stress marks only, ruling B4 iv).
- IPA house form: no period beside a stress mark. Bands come only from the band vote; never set one by hand.
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand. A review that removes a cross-reference removes its mirror too.
- Number entries (`-num`) hold their card, score, money, and size uses and their uses before **of** (*three of us*); reviewers asking for noun or pronoun entries for these are rejected. Tens (*forty* to *ninety*) carry a plural sense, *in her forties*; ordinals keep the date sense (*on the fourth*) but no adverbial *finished fourth*.
- Idioms with no noun go under their first verb even when another word carries the meaning: *make light of something* is under `make-v`, *fall flat* under `fall-v`; the adjective points to it in `see_also`.
- Cross-references to a slug with no entry are allowed; the site shows them grey or hides them (C2). `no_link_words` changes only by an owner ruling (C4).
- Rows and drafts keep their hyphens and periods. Unrelated homographs are separate entries (`-n-2`), never senses.
- Hand-written provenance timestamps come from `date -u`. Call `metrics.py` once per cycle, in wrap-up only.

## For the owner

- Today's run report: `journal/2026-10-25.md`. The first weekly digest: `journal/digest-2026-10-24.md` (ten entries to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- For your judgment: `reviewer-a`'s coverage check is right about a quarter of the time. It stays on, because ruling B1 requires it. Most rejected calls ask for compounds, phrasal verbs, or idioms that belong under another keyword.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- The public site: <https://tkgally.github.io/eex-dict/>.
