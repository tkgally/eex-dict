# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-sixth scheduled Routine run (build mode).*

## State

- 250 entries, all `reviewed` (0 `draft`). Queue: 4,118 pending, 250 done, 4 duplicate, 9 declined.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: 10 band-1 defining-vocabulary entries, diversified into the noun/verb/adjective backlog per the last run's note, still deferring the heavy prepositions *on*/*over*: *accident, action, advantage, age, agree, allow, afford, angry, aware, available*.
- Panel: 31 issues, 17 blocking, 30 applied, 2 rejected. Precision this run: reviewer-a 1.0, reviewer-b 0.857 (both strong). One full reviewer-b parse failure on `allow-v` re-ran cleanly on the documented fix (`review-panel-parse-failures`).
- Structural fix: `age-n` was missing the common informal plural sense "a very long time" (*I haven't seen you for ages*) — added as sense 3; its `of age` phrase was wrongly defined as "old enough for one activity" rather than legal adulthood — corrected, with a `formal` register label.
- Regional-accuracy fixes: `agree-v`'s bare transitive "agree a price" example is chiefly British and was unlabeled; rather than add an unverified region label to the whole sense, replaced the example with the universal "agree on" pattern and narrowed `usage_note` to state the British/American split in prose. `angry-adj`'s adaptation note wrongly called "angry at" American-only; removed the claim.
- Rejected: reviewer-b's flag that "usually passive" isn't a valid pattern on `allow-v` (it is, in the closed `verb_patterns` list) and a stale core-idea nit on two-sense `age-n` (core_idea is optional there).
- Three core_idea/definition fields drafted with words that had no entry yet (*history*, *permission*, *obtain*) — reworded to defining-vocabulary-safe phrasing rather than left as lint violations. 14 new closure/crossref targets queued from this batch (incl. *permit-v*, *disagree-v*, *agreement-n*, *unaware-adj*, *disadvantage-n*).
- Gate, caps, links, 305 tests, lint_vocab and crossref gates all pass. Spend: US$0.29 this run, US$2.31 today.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred; otherwise keep diversifying into the band-1 noun/verb/adjective backlog (e.g. *ability, accent, absorb, admire, active, alive*).
2. **review**: 194 `reviewed` entries had only one panel round as of run 25; now +10 more from this run's new entries (all single-round). Pick the next block by `params.block_size` when review is next selected.
3. **closure**: 400+ cross-reference/family/example-vocabulary targets with no entry, still growing; this run added *permit-v, disagree-v, agreement-n, agreeable-adj, allowance-n, affordable-adj, anger-n, angrily-adv, mad-adj, furious-adj, unaware-adj, conscious-adj, awareness-n, unavailable-adj, availability-n, advantageous-adj, disadvantage-n* and more (see `headwords/queue.tsv` source=crossref/closure rows added today).
4. Next **lint** due in about 3 runs (run ~29).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a`'s `pronunciation` family (0.37, 49 at the last lint pass) against the 30-percent line.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. Check new transcriptions against `see-v`, `these-det`, `person-n` before claiming they're wrong.
- Fixed-expression phrases (greetings, discourse markers, commands) may use the "used to" definition formula and need not share the headword's part of speech; a base-form imperative-verb phrase (*act your age*) must NOT use that formula — reaffirmed this run on `age-n`.
- A single reviewer repeatedly flagging the same field across rounds with inconsistent reasons, while the other reviewer never flags it, is noise (`surround-v`'s `core_idea`, 2026-09-21).
- Adaptation notes are language-neutral: never name a specific language; hedge with "often/many languages," never "most/all." Regional claims about English itself (American vs. British) need the same care — verify before labelling a pattern "especially American" (`angry-adj`, this run).
- core_idea and every sense's own `.definition` (not the phrase/entry-level fields) draw on the defining vocabulary; only a headword's own first sense is exempt.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech? — `one-num`/`one-pron` answers the *one* half); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep* (pronunciation, prior runs), *per-prep, adult-n, accept-v* (pronunciation, run 22), *additional-n* decline (informational, resolved).
