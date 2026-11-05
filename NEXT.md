# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-11-05 by run 20261105T124402Z-1i8gd4, cycle 2 (build).*

## State

- 3,792 entries, all `reviewed`. Site checked 2026-11-05 (79 of 79). Milestone 1 done; closure open, bands 1 and 2 only (A3); `closure` source empty; `family` rows now, then `crossref`. Last weekly digest: `journal/digest-2026-10-31.md`; next due 2026-11-07.
- Bands re-voted 2026-10-24; later rows at lints.
- Spend 2026-11-05: US$2.51 of US$15 so far. Originality: last 2026-11-04.
- Reviewer A: Claude, $0; on failure re-run `--roles reviewer-a`. Reviewer B and pronunciation-1: [model-refresh](wiki/decisions/model-refresh-2026-10-25.md).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** ([status](wiki/decisions/owner-rulings-2026-10-24.md)). For the Routine, in order:
   1. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates. A reference to a phrase goes in `see_also` with a note.
   2. **Build**: now closure ([build-order](wiki/decisions/build-order.md)).
   3. **Review** (E2): drafts, open entry reports, the B1 coverage pass (band-1 content words by senses, skipping those read since 2026-10-24; 203 done, the last `box-n`; next the 7 unread six-sense ones from `bottom-n` descending, then the five-sense ones; check new senses against subsenses). Then the backlog by band.
   4. **Weekly digest**: written 2026-10-31; next when `signals.digest_due`. Entry reports: pre-flight step 5.
1. **build**: queue order (last built `crossing-n`). Hand-claim `count-n-2` (nobleman), `clip-n-2` (the fastener; `clip-v-2` points to it). At `black-adj`'s review, consider moving *in black and white* to `black-n`. Hand-claim later `tap-n-2`, `wind-v-2` (*winded*); homographs take no queue row. Idioms, at next review or build: `balance-n` *tip the balance*, *strike a balance*; `scale-n` *tip the scales*; `blood-n` *sweat blood*; `stuff-n` *sweat the small stuff*; `fear-n` *strike fear into someone*; `time-n` *waste no time*; `face-n` *stare someone in the face*; `disbelief-n` *suspend disbelief*; `chord-n` *strike a chord*; `pose-n` *strike a pose*; `toast-n` *propose a toast*; `right-n` *reserve the right to*; `let-v` *let's face it*, *let rip*, *let something slip*; `keep-v` *keep someone posted*; `be-v` *too good to be true*, *to be sure*; `ring-v` *ring true*; `form-n` *true to form*; `power-n` *power of attorney*; `chain-n` *chain of command*; `play-v` *play dead*; `drama-n` *drama queen* (when built); `apple-n` *upset the apple cart*; House rules 16 and 18; phrasal verbs get `separable` codes when next reviewed (B4 i).
2. **originality**: ask reviewer-b in one call; search any wording it quotes, and headword plus opening words.
3. **review**: reject reviewer-b's objections to quotation marks around words in examples, and requests for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*), with the reason. `verb + adjective` is not a collocation type; *usually passive* is a pattern, not a code. Reviewer A calls `comparative with more` "not a grammar code": reject.
4. **closure**: open since 2026-10-27; paused above band 2 (A3). `family` rows built through `contribution-n` (2026-11-05); then queue order. `mushroom-n` built: add the mushroom-top subsense to `cap-n` at its next review. Hand-claim `rocket-n-2`, `corn-n-2` (foot), `story-n-2` (floor), `file-v-2` (tool); link `bat-n`, `bit-n` to their `-2` homographs at next review. Missing idioms: *not bat an eye* (`eye-n`), *blow someone's mind* and *spring to mind* (`mind-n`), *spring a leak* (`leak-n` when built), *leave of absence* (`leave-n` when built), *defeat the purpose* (`purpose-n`), *mean business* (`business-n`); *a small fortune* (`fortune-n` when built); move *a state of affairs* from `affair-n` to `state-n` when `affair-n` is next reviewed; *blow the whistle on* to `whistle-n`, *blow someone a kiss* to `kiss-n` when built; add *anything but* to `anything-pron`, *nothing but* to `nothing-pron`; add *God forbid* (and *heaven forbid* to `heaven-n` when built) to `god-n` (rejected for `forbid-v`). A comparison form (*better*) takes an exceptions-table line.
5. **lint**: every ten runs; last 2026-11-05 (hundred-and-second pass), next due in eight runs. Wiki 27,262 of 30,000 words. Switched off: reviewer A `inflection` (2026-10-28), reviewer B `phrase` (2026-10-30), reviewer B `pronunciation` (2026-11-05, 0.26 over 42).
6. **Tooling notes** (`wiki/notes/`): fixes due: `queue-hyphen-loss`; a repeated `band_vote.py apply` doubles its note.

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

- Latest report: `journal/2026-11-05-3.md`. Digest: `journal/digest-2026-10-31.md` (ten to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- `PROJECT.md` still says "two non-Anthropic reviewers" (reviewer A is Claude since your 2026-10-25 ruling); yours to update.
- For your judgment: no reviewer checks pronunciation now (B off at the 2026-11-05 lint; A by your 2026-10-05 ruling, on its old model). The panel plus CMU still checks every transcription.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt`.
- Site: <https://tkgally.github.io/eex-dict/>
