# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-10-30 by run 20261030T124352Z-k21ycc, cycle 2 (build).*

## State

- 3,365 entries, all `reviewed` (60 band-2 verbs built 2026-10-30, the last `flee-v` to `grind-v`). Site checked 2026-10-29 (79 of 79). **Milestone 1 has no queue rows left** (finished 2026-10-27); closure is open, bands 1 and 2 only (A3); the `closure` source is empty, so `family` and `crossref` rows follow. The five hand-claimed homographs are built (2026-10-27). Last weekly digest: `journal/digest-2026-10-24.md`.
- Bands re-voted 2026-10-24 ([record](experiments/band-vote-2026-10-24/README.md)); later rows voted at each lint (latest [2026-10-30](experiments/band-vote-2026-10-30/README.md)); rows queued since stay `unbanded` until the next vote.
- Spend 2026-10-30: US$2.42 of US$15 so far. Originality: last 2026-10-30 (no rewrites), next due in twenty runs.
- Reviewer A is a Claude model via headless `claude -p`, $0 ([reviewer-a-claude](wiki/decisions/reviewer-a-claude.md)); a failed call: re-run `--roles reviewer-a`. Reviewer B and pronunciation-1: [model-refresh](wiki/decisions/model-refresh-2026-10-25.md).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **B3**, **B4 (i)**: done; phrasal verbs get `separable` codes when next reviewed.
   2. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates. The `active-adj`/`passive-adj`, `alone-adj`/`lonely-adj`, `cut-v`/`chop-v` type mismatches belong here (792 pairs listed 2026-10-30). Five forward references name no real sense: `also-adv`/`too-adv` to `well-adv`, `look-after-phrv` to `look-v`, `slightly-adv` to `bit-n`, `whatever-pron` to `matter-n`.
   3. **Build** milestone 1: done 2026-10-27, and the five hand-claimed homographs; now closure ([build-order](wiki/decisions/build-order.md)).
   4. **Review** (E2): drafts, open entry reports, the B1 coverage pass (begun 2026-10-25: band-1 content words by senses and subsenses, skipping those read since 2026-10-24; 105 done, the last `home-n`, `hole-n`, `force-n`, `fine-adj`; next `fill-v` in the same order; check a new sense against the entry's subsenses before adding it), then the backlog by band.
   5. **Weekly digest**: next when `signals.digest_due`. Entry reports: pre-flight step 5.
   6. **E5**: milestone 1 is built (2026-10-27); when the first coverage block of about 100 entries is reviewed, say so under "For the owner" and in the digest.
1. **build**: band-2 verbs next in queue order (`flee` to `grind` built 2026-10-30). Add *let's face it* to `let-v` when it is next reviewed (keyword rule; rejected for `face-v`). Check transitivity against every example. Panel in chunks of four; place `NO-SENSE` back-links by hand and check every mirror. 
2. **originality**: ask reviewer-b (`openrouter.py --role reviewer-b`); it names sources without quoting them, so the search decides.
3. **review**: reject reviewer-b's objections to quotation marks around words in examples, and requests for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*), with the reason. `verb + adjective` is not a collocation type. Reviewer A: fix only clear minor issues; it calls `comparative with more` "not a grammar code": reject.
4. **closure**: open since 2026-10-27; paused above band 2 (A3). `family` rows `replace-v` to `star-v` built 2026-10-30; next in the queue order. Hand-claim `bat-n-2`, `pound-n-2`. Missing idioms: *not bat an eye* (`eye-n`), *blow someone's mind* and *spring to mind* (`mind-n`), *spring a leak* (`leak-n` when built), *defeat the purpose* (`purpose-n`), *mean business* (`business-n`); move *blow the whistle on* to `whistle-n`, add *blow someone a kiss* to `kiss-n` when built; add *anything but* to `anything-pron`, *nothing but* to `nothing-pron`. A comparison form (*better*) takes an exceptions-table line, not `not gradable`.
5. **lint**: every ten runs; last 2026-10-30 (ninety-fourth pass), next due in eight runs. Switched off: reviewer A `inflection` (2026-10-28), reviewer B `phrase` (2026-10-30, 0.20 over 20).
6. **Tooling notes still open** (`wiki/notes/`): `lint-vocab-pos-guess-gap` (fix due), `homograph-queue-and-inflection`, `inflect-uncountable-plural-gap`, `lint-vocab-queue-note-duplication`, `pronounce-check-word-break` (fix due), `phrasal-verb-stress-recheck`, `crossref-queue-capitalized-headword`. Wiki near cap.

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

- Latest run report: `journal/2026-10-30-3.md`. The first weekly digest: `journal/digest-2026-10-24.md` (ten entries to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- Your ruling of 2026-10-25 is in force: reviewer A is the Claude model, and reviewer B is unchanged. `PROJECT.md` still says "two non-Anthropic reviewers"; a session does not edit the charter, so that line is yours to update.
- For your judgment: your 2026-10-05 switch-off of reviewer A's pronunciation flags rested on the old model (0.26); it stays off until you say. The new model caught all four planted IPA errors.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt` (new: `ensure-v`).
- The public site: <https://tkgally.github.io/eex-dict/>.
