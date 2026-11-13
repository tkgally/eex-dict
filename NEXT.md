# NEXT.md — baton (cap 60 lines and 1,000 words; rewrite, don't append; history lives in wiki/log.md)

*Rewritten 2026-11-13 after run m3t3kf, cycle 4 (review).*

## State

- 4,293 entries, all `reviewed`. Site checked 2026-11-13 (79 of 79). Milestone 1 done; closure open, bands 1 and 2 only (A3); `closure` source empty; `family` rows now (built through `paste-n`, 2026-11-13), then `crossref`. Last weekly digest: `journal/digest-2026-11-07.md`; next due 2026-11-14.
- Bands re-voted 2026-10-24; later rows at lints.
- Spend 2026-11-13: US$2.24 of US$15 so far. Originality: last 2026-11-10 (1 rewrite, `tie-n`).
- Reviewer A: Claude, $0; on failure re-run `--roles reviewer-a`. Reviewer B and pronunciation-1: [model-refresh](wiki/decisions/model-refresh-2026-10-25.md).

## Queue (top-down)

0. **The owner's rulings of 2026-10-24** ([status](wiki/decisions/owner-rulings-2026-10-24.md)). For the Routine, in order:
   1. **C1 audit**: mirror links with no note, at most 40 a batch; `crossref.py --missing-senses` lists the candidates. A reference to a phrase goes in `see_also` with a note.
   2. **Build**: now closure ([build-order](wiki/decisions/build-order.md)).
   3. **Review** (E2): drafts, open entry reports, the B1 coverage pass (band-1 content words by senses, skipping those read since 2026-10-24; 319 done, last `smooth-adj` to `stage-n` (`out-prep` for the function-word round); next `station-n`, `tail-n`; phrasal verbs skipped so far; check new senses against subsenses). Then the backlog by band.
   4. **Weekly digest**: written 2026-11-07; next when `signals.digest_due`. Entry reports: pre-flight step 5.
1. **build**: queue order (last built `may-n` to `pajamas-n`, 2026-11-13; `pace-v` queued). `word-n`: add *words fail me*; `dot-n`: *connect the dots*. Then `tap-n-2`, `wind-v-2`, `lead-n-2`, `launch-n-2`. `twin-adj` (queued) takes *twin bed*, *twin room*. `red-n` takes *see red*; `blue-adj` needs *a blue state*. Idioms, next review or build: `balance-n` *tip the balance*, *strike a balance*; `scale-n` *tip the scales*; `blood-n` *sweat blood*; `stuff-n` *sweat the small stuff*; `fear-n` *strike fear into someone*; `time-n` *waste no time*; `disbelief-n` *suspend disbelief*; `chord-n` *strike a chord*; `pose-n` *strike a pose*; `toast-n` *propose a toast*; `let-v` *let's face it*, *let's roll*, *let rip*, *let something slip*; `keep-v` *keep someone posted*; `be-v` *too good to be true*, *to be sure*, *have been around*; `ring-v` *ring true*; `form-n` *true to form*; `power-n` *power of attorney*; `chain-n` *chain of command*; `play-v` *play dead*; `dime-n` *a dime a dozen*; `apple-n` *upset the apple cart*; `rock-n` *rock bottom*; `pavement-n` *pound the pavement*; `trick-n` *the oldest trick in the book*; `exception-n` *the exception that proves the rule*; `deal-n` *no big deal*; `price-n` *pay the price*; `field-n` *out of left field*; `way-n` *pick your way*; `hole-n` *pick holes in*; House rules 16 and 18; phrasal verbs get `separable` codes when next reviewed (B4 i).
2. **originality**: ask reviewer-b once; search quoted wording and headword plus opening words.
3. **review**: given names after titles fixed 2026-11-05 (`lord-n`). `lord-v` (*lord it over*) queued. Reject reviewer-b on quotation marks in examples, phrasal verbs or compounds as senses, idioms keyed elsewhere, hand marks on listed forms. `verb + adjective` is not a collocation type; *usually passive* is a pattern, not a code. Reviewer A calls `comparative with more` "not a grammar code": reject.
4. **closure**: paused above band 2 (A3). `family` rows built through `paste-n` (2026-11-13). Hand-claim `rite-n` (*rite of passage*). `killer-adj` queued (crossref): takes *a killer smile*, *a killer app*. `goods-n`, `drug-n`: overlapping notes; fix at next review. Hand-claim `fit-n-2` (seizure; *have a fit*) and `fold-n-2` (sheep; *return to the fold*). Add *march to the beat of a different drummer* to `beat-n` at its next review. `designer-adj`, `graduate-adj`, `hit-and-run-n` queued (crossref). Move *make the best of a bad job* from `job-n` to `best-n` when built. `mushroom-n` built: add the mushroom-top subsense to `cap-n` at its next review. Hand-claim `match-n-2` (fire stick), `rocket-n-2`, `corn-n-2` (foot), `story-n-2` (floor), `file-v-2` (tool); link `bat-n`, `bit-n` to their `-2` homographs at next review. Missing idioms: *not bat an eye* (`eye-n`), *blow someone's mind* and *spring to mind* (`mind-n`), *spring a leak* (`leak-n` when built), *leave of absence* (`leave-n` when built), *defeat the purpose* (`purpose-n`); move *a state of affairs* from `affair-n` to `state-n` when `affair-n` is next reviewed; *blow the whistle on* to `whistle-n`; add *anything but* to `anything-pron`, *nothing but* to `nothing-pron`; add *God forbid* to `god-n` (*heaven forbid* is in `heaven-n`) (rejected for `forbid-v`). 
5. **lint**: every ten runs (each cycle counts); last 2026-11-13 (hundred-and-eleventh); next after ten runs. Switched off: reviewer A `inflection` (2026-10-28), reviewer B `phrase` (2026-10-30), reviewer B `pronunciation` (2026-11-05, 0.26 over 42). 
6. **Tooling notes** (`wiki/notes/`): `inflect-uncountable-plural-gap` fixed 2026-11-12; `queue-hyphen-loss` recurrences handled by hand; `band_vote.py apply` twice doubles notes.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- The reviewers' settled questions are in `config/reviewer-house-rules.md`; reject an objection to any of them.
- No script writes a model-owned field; the one exception is `tools/ipa_format.py` (periods beside stress marks only, ruling B4 iv).
- IPA house form: no period beside a stress mark. Bands come only from the band vote; never set one by hand.
- `crossref.py` no longer guesses a sense: place each `NO-SENSE` pair by hand. A review that removes a cross-reference removes its mirror too.
- Number entries (`-num`) hold their card, score, money, size, and *of* uses; reject requests for noun or pronoun entries. Tens carry a plural sense (*in her forties*); ordinals keep the date sense (*on the fourth*) but no adverbial *finished fourth*.
- Idioms with no noun go under their first verb even when another word carries the meaning: *make light of something* is under `make-v`, *fall flat* under `fall-v`; the adjective points to it in `see_also`.
- Cross-references to a slug with no entry are allowed; the site shows them grey or hides them (C2). `no_link_words` changes only by an owner ruling (C4).
- Rows and drafts keep their hyphens and periods. Unrelated homographs are separate entries (`-n-2`), never senses.
- Timestamps come from `date -u`. Call `metrics.py` once per cycle, at wrap-up.

## For the owner

- Latest report: `journal/2026-11-13-3.md`.
- Left for a session with you (ruling 6): pronunciation disputes in `reviews/needs_curator.txt`; the ten-entry samples in `journal/digest-2026-10-31.md` and `journal/digest-2026-11-07.md`. Routine runs do not settle them.
- Site: <https://tkgally.github.io/eex-dict/>
