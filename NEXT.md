# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-fifth scheduled Routine run (review mode).*

## State

- 240 entries, all `reviewed` (0 `draft`). Queue: 4,110 pending, 240 done, 4 duplicate, 9 declined.
- Review mode (selector: highest scheduler debt; 213 entries had only one panel round, now 194). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: second panel round on the 20 oldest one-round entries (*see, make, get, and, in-spite-of, of, big, old, run, take, go, because, it, one, some, actually, ago, give-up, look-after, well*). 121 issues, 80 blocking, 95 applied, 26 rejected. Precision this round: reviewer-a 0.76, reviewer-b 0.905 (both above their running averages). Two reviewer-b parse failures (`because-conj`, `actually-adv`) re-ran cleanly on the documented fix.
- Structural fixes from both reviewers converging on the one-part-of-speech rule: `one-num` split into `one-num` (the number) and a new `one-pron` (replacing/generic/"a person" pronoun senses), full pipeline run on the new entry; `because-conj`'s `because + noun` sense removed and `because-prep` queued; `it-pron`'s game sense ("you're it") moved to a phrase, matching the `see-v`/`go-v` precedent (fixed expressions need not share the headword's part of speech).
- Rejected: 5 `see-v` phrase-definition-style flags that contradict 40+ existing "used to" phrase precedents; 2 cases of reviewer-a confusing **one** with **won** in a pronunciation note (logged to `wiki/notes/reviewer-noise.md`); a handful of already-hedged or already-correct claims. Fixed several raw-IPA-in-prose and unhedged most/all-languages violations of house style caught along the way, beyond what reviewers flagged.
- Gate, caps, links, 305 tests, lint_vocab and crossref gates all pass. Spend: US$1.55 this run, US$2.02 today so far.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred; otherwise keep diversifying into the band-1 noun/verb/adjective backlog.
2. **review**: 194 `reviewed` entries have had only one panel round; pick the next block by `params.block_size` when review is next selected.
3. **closure**: 400+ cross-reference/family/example-vocabulary targets with no entry, still growing; `because-prep` (band 3) is a new, concrete one from this run.
4. Next **lint** due in about 4 runs (run ~29).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a`'s `pronunciation` family (0.37, 49 at the last lint pass) against the 30-percent line; this run's overall precision (0.76) is a good sign but was not measured by family.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. Check new transcriptions against `see-v`, `these-det`, `person-n` before claiming they're wrong.
- Fixed-expression phrases (greetings, discourse markers, commands) may use the "used to" definition formula and need not share the headword's part of speech — established practice across 40+ entries (`hand-n`, `well-interj`, `time-n`...) and reaffirmed this run for `see-v` and `it-pron`.
- A single reviewer repeatedly flagging the same field across rounds with inconsistent reasons, while the other reviewer never flags it, is noise (`surround-v`'s `core_idea`, 2026-09-21).
- Adaptation notes are language-neutral: never name a specific language; hedge with "often/many languages," never "most/all."
- Pronunciation/adaptation notes use plain respelling (capitals for stress), never raw IPA symbols — caught and fixed on several entries this run.
- A restriction on one variation of a sense belongs in the subsense's or sense's `explanation`, never as a prefix inside the `definition`.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech? — this run's `one-num`/`one-pron` split answers the *one* half); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep* (pronunciation, prior runs), *per-prep, adult-n, accept-v* (pronunciation, run 22), *additional-n* decline (informational, resolved).
