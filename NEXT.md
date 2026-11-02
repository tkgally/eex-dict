# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-11-02 by run 20261102T004425Z-gk88ch, cycle 1 (originality).*

## State

- 3,533 entries, all `reviewed` (latest band-2 verbs `award-v` to `react-v`). Site checked 2026-10-31 (79 of 79). **Milestone 1 has no queue rows left** (finished 2026-10-27); closure is open, bands 1 and 2 only (A3); the `closure` source is empty, so `family` and `crossref` rows follow. Last weekly digest: `journal/digest-2026-10-31.md`; next due 2026-11-07.
- Bands re-voted 2026-10-24; later rows voted at each lint (latest [2026-11-01](experiments/band-vote-2026-11-01/README.md), 133 rows); newer rows stay `unbanded` until the next vote.
- Spend 2026-11-02: US$0.06 of US$15 so far. Originality: last 2026-11-02 (one rewrite, `character-n`), next due in twenty runs.
- Reviewer A is a Claude model via headless `claude -p`, $0 ([reviewer-a-claude](wiki/decisions/reviewer-a-claude.md)); a failed call: re-run `--roles reviewer-a`. Reviewer B and pronunciation-1: [model-refresh](wiki/decisions/model-refresh-2026-10-25.md).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** (`inbox/archive/20261024_owner_rulings.txt`; status table [owner-rulings-2026-10-24](wiki/decisions/owner-rulings-2026-10-24.md)). Left for the Routine, in this order:
   1. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates. Type mismatches such as `alone-adj`/`lonely-adj` belong here (904 pairs listed 2026-11-01). Five forward references name no real sense: `also-adv`/`too-adv` to `well-adv`, `look-after-phrv` to `look-v`, `slightly-adv` to `bit-n`, `whatever-pron` to `matter-n`.
   2. **Build**: milestone 1 done; now closure ([build-order](wiki/decisions/build-order.md)).
   3. **Review** (E2): drafts, open entry reports, the B1 coverage pass (begun 2026-10-25: band-1 content words by senses and subsenses, skipping those read since 2026-10-24; 139 done, the last `wing-n`, `wide-adj`, `weight-n`; next the 63 unread six-sense entries (`use-v`, `unit-n`, `turn-n`, `true-adj`, ...), then the five-sense ones; check a new sense against the entry's subsenses before adding it), then the backlog by band.
   4. **Weekly digest**: written 2026-10-31; next when `signals.digest_due`. Entry reports: pre-flight step 5.
1. **build**: band-2 verbs next in queue order (built through `react`; `phone-in-phrv`, `plug-away-phrv`, `chord-n` queued). Add *strike a balance* to `balance-n`, *strike fear into someone* to `fear-n`, *stare someone in the face* to `face-n`, *suspend disbelief* to `disbelief-n` when reviewed; give `chord-n` *strike a chord* and `pose-n` *strike a pose* when built. Give `toast-n`, when built, *propose a toast*; add *reserve the right to* to `right-n` when reviewed. Add *let's face it*, *let rip*, *let something slip* to `let-v` and *keep someone posted* to `keep-v` when next reviewed (keyword rule; rejected for `face-v`, `post-v`). Panel in chunks; place `NO-SENSE` pairs by hand. Follow house rules 16 and 18; phrasal verbs get `separable` codes when next reviewed (B4 i).
2. **originality**: ask reviewer-b (`openrouter.py --role reviewer-b`, all ten rows in one call); read its reasons as well as its verdicts: on 2026-11-02 it quoted the Oxford wording behind the one rewrite under an *original* answer. Search the quotation it gives.
3. **review**: reject reviewer-b's objections to quotation marks around words in examples, and requests for phrasal verbs and compounds as senses, and for idioms whose keyword is another word (*do someone proud*), with the reason. `verb + adjective` is not a collocation type. Reviewer A: fix only clear minor issues; it calls `comparative with more` "not a grammar code": reject.
4. **closure**: open since 2026-10-27; paused above band 2 (A3). `family` rows built through `auntie-n` (2026-11-01); then queue order. Hand-claim `bat-n-2`, `pound-n-2`, `bit-n-2` (computing). Missing idioms: *not bat an eye* (`eye-n`), *blow someone's mind* and *spring to mind* (`mind-n`), *spring a leak* (`leak-n` when built), *defeat the purpose* (`purpose-n`), *mean business* (`business-n`); move *blow the whistle on* to `whistle-n`, add *blow someone a kiss* to `kiss-n` when built; add *anything but* to `anything-pron`, *nothing but* to `nothing-pron`; add *God forbid* (and *heaven forbid* to `heaven-n` when built) to `god-n` (rejected for `forbid-v`). A comparison form (*better*) takes an exceptions-table line.
5. **lint**: every ten runs; last 2026-11-01 (ninety-seventh pass), next due in ten runs. Switched off: reviewer A `inflection` (2026-10-28), reviewer B `phrase` (2026-10-30, 0.20 over 20).
6. **Tooling notes still open** (`wiki/notes/`): fixes due for `lint-vocab-pos-guess-gap` and `pronounce-check-word-break`; seven more listed in `wiki/index.md`.

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
- Hand-written timestamps come from `date -u`. Call `metrics.py` once per cycle, in wrap-up only.

## For the owner

- Latest run report: `journal/2026-11-02.md`. This week's digest: `journal/digest-2026-10-31.md` (ten entries to sample).
- Curator line still open: list names used as family names after a title (*Ms. Kim*, *Dr. Lee*) in `teacher-n`, `title-n`, `dr-abbr`, `doctor-n`; working assumption: allowed there until you rule.
- `PROJECT.md` still says "two non-Anthropic reviewers" (reviewer A is Claude since your 2026-10-25 ruling); the charter line is yours to update.
- For your judgment: your 2026-10-05 switch-off of reviewer A's pronunciation flags rested on the old model (0.26); it stays off until you say. The new model caught all four planted IPA errors.
- Still open: continent names in definitions; *the former*/*the following* as nouns or pronouns (`wiki/open-questions.md`); pronunciation disputes in `reviews/needs_curator.txt` (new: `ensure-v`, `insure-v`).
- Public site: <https://tkgally.github.io/eex-dict/>.
