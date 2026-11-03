# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-11-03 by run 20261103T070618Z-g0ufhy, cycle 3 (build).*

## State

- 3,631 entries, all `reviewed`. Site checked 2026-11-02 (79 of 79). **Milestone 1 has no queue rows left**; closure is open, bands 1 and 2 only (A3); the `closure` source is empty; `family` rows now, then `crossref`. Last weekly digest: `journal/digest-2026-10-31.md`; next due 2026-11-07.
- Bands re-voted 2026-10-24; later rows at each lint.
- Spend 2026-11-03: US$2.16 of US$15 so far. Originality: last 2026-11-03 (rewrote `closet-n`, `temper-n`); next in twenty runs.
- Reviewer A: Claude via `claude -p`, $0; on failure, re-run `--roles reviewer-a`. Reviewer B and pronunciation-1: [model-refresh](wiki/decisions/model-refresh-2026-10-25.md).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates. Five forward references name no real sense: `also-adv`/`too-adv` to `well-adv`, `look-after-phrv` to `look-v`, `slightly-adv` to `bit-n`, `whatever-pron` to `matter-n`. `birthday-n` lists `anniversary-n` as a synonym.
   2. **Build**: milestone 1 done; now closure ([build-order](wiki/decisions/build-order.md)).
   3. **Review** (E2): drafts, open entry reports, the B1 coverage pass (band-1 content words by senses, skipping those read since 2026-10-24; 169 done, the last `place-v`, `piece-n`; next the 41 unread six-sense content entries (from `period-n`), then the five-sense ones; check new senses against subsenses), then the backlog by band.
   4. **Weekly digest**: written 2026-10-31; next when `signals.digest_due`. Entry reports: pre-flight step 5.
1. **build**: band-2 verbs done (last `yell`); now band-2 nouns in queue order (built through `basement`). Queue `tap-n-2` and `wind-v-2` (*winded*). Idioms to add at each entry's next review or build `balance-n` *tip the balance*, *strike a balance*; `scale-n` *tip the scales*; `blood-n` *sweat blood*; `stuff-n` *sweat the small stuff*; `fear-n` *strike fear into someone*; `time-n` *waste no time*; `face-n` *stare someone in the face*; `disbelief-n` *suspend disbelief*; `chord-n` *strike a chord*; `pose-n` *strike a pose*; `toast-n` *propose a toast*; `right-n` *reserve the right to*; `let-v` *let's face it*, *let rip*, *let something slip*; `keep-v` *keep someone posted*; `be-v` *too good to be true*, *to be sure*; `ring-v` *ring true*; `form-n` *true to form*; `power-n` *power of attorney*; `drama-n` *drama queen* (when built). House rules 16 and 18; phrasal verbs get `separable` codes when next reviewed (B4 i).
2. **originality**: ask reviewer-b in one call; search any wording it quotes. Also search headword plus opening words.
3. **review**: reject reviewer-b's objections to quotation marks around words in examples, and requests for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*), with the reason. `verb + adjective` is not a collocation type; *usually passive* is a pattern, not a code. Reviewer A calls `comparative with more` "not a grammar code": reject.
4. **closure**: open since 2026-10-27; paused above band 2 (A3). `family` rows built through `banking-n` (2026-11-02); then queue order. Hand-claim `rocket-n-2`; link `bat-n`, `bit-n` to their `-2` homographs at next review. Missing idioms: *not bat an eye* (`eye-n`), *blow someone's mind* and *spring to mind* (`mind-n`), *spring a leak* (`leak-n` when built), *leave of absence* (`leave-n` when built), *defeat the purpose* (`purpose-n`), *mean business* (`business-n`); *a small fortune* (`fortune-n` when built); move *a state of affairs* from `affair-n` to `state-n` when `affair-n` is next reviewed; move *blow the whistle on* to `whistle-n`, add *blow someone a kiss* to `kiss-n` when built; add *anything but* to `anything-pron`, *nothing but* to `nothing-pron`; add *God forbid* (and *heaven forbid* to `heaven-n` when built) to `god-n` (rejected for `forbid-v`). A comparison form (*better*) takes an exceptions-table line.
5. **lint**: every ten runs; last 2026-11-03 (ninety-ninth pass), next due in ten runs. Reviewer B `pronunciation` (0.40) nearest the line. Switched off: reviewer A `inflection` (2026-10-28), reviewer B `phrase` (2026-10-30, 0.20 over 20).
6. **Tooling notes** (`wiki/notes/`): fixes due for `lint-vocab-pos-guess-gap`, `pronounce-check-word-break`; more in `wiki/index.md`.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them.
- No script writes a model-owned field; the one exception is `tools/ipa_format.py` (periods beside stress marks only, ruling B4 iv).
- IPA house form: no period beside a stress mark. Bands come only from the band vote; never set one by hand.
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand. A review that removes a cross-reference removes its mirror too.
- Number entries (`-num`) hold their card, score, money, size, and *of* uses; reject requests for noun or pronoun entries. Tens (*forty* to *ninety*) carry a plural sense, *in her forties*; ordinals keep the date sense (*on the fourth*) but no adverbial *finished fourth*.
- Idioms with no noun go under their first verb even when another word carries the meaning: *make light of something* is under `make-v`, *fall flat* under `fall-v`; the adjective points to it in `see_also`.
- Cross-references to a slug with no entry are allowed; the site shows them grey or hides them (C2). `no_link_words` changes only by an owner ruling (C4).
- Rows and drafts keep their hyphens and periods. Unrelated homographs are separate entries (`-n-2`), never senses.
- Timestamps come from `date -u`. Call `metrics.py` once per cycle, in wrap-up only.

## For the owner

- Latest report: `journal/2026-11-03-3.md`. Digest: `journal/digest-2026-10-31.md` (ten to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- `PROJECT.md` still says "two non-Anthropic reviewers" (reviewer A is Claude since your 2026-10-25 ruling); yours to update.
- For your judgment: your 2026-10-05 switch-off of reviewer A's pronunciation flags rested on the old model (0.26); off until you say. The new model caught all four planted IPA errors.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- Site: <https://tkgally.github.io/eex-dict/>.
