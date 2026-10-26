# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-26 by scheduled run 20261026T125121Z-q4jhhd, cycle 3 (build: deodorant to orphan).*

## State

- 2,984 entries, all `reviewed`. Site checked 2026-10-26: 79 of 79 pass. Milestone 1: 54 rows left. Homographs to claim by hand when their turn comes: `bark-n-2` (a dog's bark), `ash-n-2` (the tree), `temple-n-2` (side of the head); `bill-n-2` (a bird's beak) is not yet queued: queue it by hand, then point `beak-n` to it. Last weekly digest: `journal/digest-2026-10-24.md`.
- Bands re-voted 2026-10-24 ([record](experiments/band-vote-2026-10-24/README.md)); 64 more voted 2026-10-26 ([record](experiments/band-vote-2026-10-26/README.md)). A row a tool queues is `unbanded` until the next vote.
- Spend 2026-10-26 so far: US$3.03 of US$15. Originality: last 2026-10-26 (`include-v` rewritten), next due in twenty runs.
- **Reviewer A is now a Claude model**, headless `claude -p` at high effort, $0 in the ledger ([reviewer-a-claude](wiki/decisions/reviewer-a-claude.md); [experiment](experiments/claude-reviewers-v1/README.md)). Both roles run side by side. A failed `claude -p` call is retried twice, then recorded as an error: re-run `--roles reviewer-a`. Its model label was fixed 2026-10-25 ([claude-cli-model-label](wiki/notes/claude-cli-model-label.md)).
- **Reviewer B is now Gemini 4 Argon and pronunciation-1 GPT-6.1 Sol** (owner's ruling 2026-10-25, [model-refresh](wiki/decisions/model-refresh-2026-10-25.md)).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **B3 review**: finished 2026-10-25. The missing senses opened the coverage pass; continue it under item 5.
   2. **B4 (i)**: done 2026-10-25; other phrasal verbs get the code when next reviewed.
   3. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates; eight references to ruled-out targets (`check_links.py`). The `active-adj`/`passive-adj`, `alone-adj`/`lonely-adj`, `cut-v`/`chop-v` type mismatches belong here (707 pairs listed 2026-10-26).
   4. **Build** milestone 1 in queue order (`claim.py --from-queue`). Closure waits until it is built ([build-order](wiki/decisions/build-order.md)).
   5. **Review** (E2): drafts, open entry reports, the B1 coverage pass (begun 2026-10-25: band-1 content words by number of senses, skipping those read since 2026-10-24; thirty-seven done; next the eight-sense words, oldest reading first: `good-adj`, `play-v`, `find-v`, `move-v`; add *going strong* to `go-v`, *look sharp* to `look-v`, and literal *hold your breath* to `breath-n` when next read), then the one-round backlog by band.
   6. **reviewer-b** (E1): settled 2026-10-25, no trial.
   7. **Weekly digest**: next when `signals.digest_due`. Entry reports: pre-flight step 5.
   8. **E5**: when milestone 1 is built and the first coverage block of about 100 entries is reviewed, say so under "For the owner" and in the digest.
1. **build**: check a verb + preposition row against the verb's senses and a `phr` row against the keyword entry's phrases; run the panel in chunks of four or five; place every `NO-SENSE` back-link by hand.
2. **originality**: ask reviewer-b (`openrouter.py --role reviewer-b`); it names sources without quoting them, so the search decides.
3. **review**: reviewer-b keeps objecting to quotation marks around words mentioned in examples, and reviewers ask for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*, *travel light*); reject all, with the reason. `verb + adjective` is not a collocation type. The new reviewer A raises many minor issues: fix the clear ones only; it calls `comparative with more` "not a grammar code": reject.
4. **closure**: blocked by milestone 1, then paused above band 2 (A3).
5. **lint**: every ten runs; last 2026-10-26 (eighty-eighth pass), next due in three runs. Judge both reviewers by their new rows (`reviewer-a:claude-sonnet-5-5`, `reviewer-b:gemini-4-argon`), not the old models' all-time figures; the 30-percent rule applies afresh.
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

- Latest run report: `journal/2026-10-26-3.md`. The first weekly digest: `journal/digest-2026-10-24.md` (ten entries to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- Your ruling of 2026-10-25 is in force: reviewer A is the Claude model, and reviewer B is unchanged. `PROJECT.md` still says "two non-Anthropic reviewers"; a session does not edit the charter, so that line is yours to update.
- For your judgment: your 2026-10-05 switch-off of reviewer A's pronunciation flags rested on the old model (0.26); it stays off until you say. The new model caught all four planted IPA errors.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- The public site: <https://tkgally.github.io/eex-dict/>.
