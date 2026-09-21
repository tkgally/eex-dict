# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-eighth scheduled Routine run (build mode).*

## State

- 262 entries, all `reviewed` (0 `draft`). Queue: 4,119 pending, 262 done, 4 duplicate, 9 declined.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: twelve band-1 entries, diversifying the noun/verb/adjective backlog per the last run's note, still deferring *on*/*over*: *ability, accent, absorb, admire, active, alive, actor, adopt, adult* (adjective)*, age* (verb)*, agreement, ahead*.
- Panel: 42 issues, 24 blocking, 32 applied, 10 rejected. Precision this run: reviewer-a 0.812, reviewer-b 0.731. One reviewer-b parse failure (`actor-n`) re-ran cleanly.
- Structural fixes from adjudication: *active-adj*'s "in use" sense conflated volcano, membership, and technical uses under one definition; split into in-use, taking-part, and a volcano subsense. *age-v* conflated plain and causative aging; split into an intransitive and a transitive sense, folding the food-aging use into those.
- Fixed five defining-vocabulary violations in core ideas/definitions (*extra, distinguish, emphasis, organization, further/advanced*).
- Tried, then reverted, an `inflection-exceptions.json` note for British "ageing" on *age-v*: it marked a fully regular verb `exceptions`-sourced and broke `test_070_age_v`; rejected the reviewer issue instead (logged in decisions.jsonl).
- Pronunciation: *absorb-v* corrected American/British from *s* to *z* per cmudict, now verified both. *admire-v* American schwa kept, flagged `pronunciation-unverified` (cmudict is internally inconsistent between related forms). *adult-adj* disputed/kept, same open question as *adult-n*.
- 14 closure/crossref targets queued; back-link `adult-n` \<- `adult-adj` applied.
- Gate, caps, links, 305 tests, lint_vocab and crossref gates all pass. Spend: US$0.38 this run, US$3.58 today.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred; otherwise keep diversifying (e.g. *afford, angry* are done; try *aim, air, airport, alarm, activity, address, adjective, advertise, affect, agreement* siblings like *act, actual, actually*).
2. **review**: 196 `reviewed` entries remain at only one panel round (184 + 12 from this run); pick the next block by `params.block_size` when review is next selected.
3. **closure**: 450+ cross-reference/family targets with no entry, still growing; this run added *accented-adj, absorption-n, absorbent-adj, admiration-n, admirable-adj, admirer-n, activity-n, actively-adv, act-v, acting-n, adoption-n, adopted-adj, adulthood-n, passive-adj*.
4. Next **lint** due in about 1 run (run ~29, per the last lint's note).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-b` precision (0.731 this run, trending below `reviewer-a`); recheck against the 30-percent-per-family line at the next lint pass.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- A single reviewer repeatedly flagging the same field across rounds with inconsistent reasons, while the other reviewer never flags it, is noise.
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid — `often before another noun` and `usually passive` (as a pattern) are both valid; a reviewer claiming otherwise is wrong, not the entry.
- Do not add a note-only line to `schema/inflection-exceptions.json` for a fully regular verb just to record a spelling variant: it flips `source` to `exceptions` and `regular` to `false`, and can break existing unit tests (`test_070_age_v`). Reject the issue instead.
- core_idea and every sense's own `.definition` draw on the defining vocabulary; only a headword's own first sense is exempt. Check candidate words against `schema/defining-vocabulary.txt` before drafting technical/topic-specific definitions (e.g. volcano terminology).

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech? — `one-num`/`one-pron` answers the *one* half); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, two new this run: *admire-v* (American pronunciation, cmudict internally inconsistent), *adult-adj* (American stress, same pattern as *adult-n*, run 20). Eight unchanged: *several-det, ourselves-pron, themselves-pron, beyond-prep, per-prep, adult-n, accept-v* (pronunciation), *additional-n* (declined, resolved).
