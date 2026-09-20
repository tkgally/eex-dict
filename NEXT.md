# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-20 by the twenty-second scheduled Routine run (build mode).*

## State

- 227 entries, all `reviewed` (0 `draft`). Queue: 4,119 pending, 227 done, 430 closure-gap, 4 duplicate, 1 declined.
- Build mode (selector: highest scheduler debt). Pre-flight: run #25's pull request was already merged before this run started; checkout reset cleanly to `origin/main`; no orphan branch, inbox empty.
- The unit: diversified away from prepositions/pronouns (three straight runs) into the much larger band-1 noun/verb/adjective backlog. Claimed 13: *off-prep, out-prep, per-prep* (three of the five remaining band-1 prepositions; *on, over* still deferred, each wants a dedicated run) plus *account-n, adult-n, add-v, accept-v, apologize-v, able-adj, actual-adj, anxious-adj, awake-adj, bad-adj*.
- Panel: 35 issues, 21 blocking, 32 applied, 3 rejected (precision reviewer-a 0.95, reviewer-b 0.867). Both reviewers independently flagged *out-prep* for mixing bare-*out* and *out of* uses; kept the single-entry structure (matches major dictionary precedent) but removed the one adverbial example and tightened wording — a defensible editorial call, logged as two rejections. *actual-adj*'s false-friends note wrongly named specific languages (against the adaptation rule); fixed. *bad-adj* had two wrong attributive/predicative-only codes and a restriction embedded inside a subsense definition; both fixed.
- Three pronunciation disputes this run: *per-prep* (American) and *adult-n* (American) — panel disagreed but CMU agreed with the drafter, kept and flagged; *accept-v* (British) — no open data, kept and flagged. All three logged to the curator queue.
- Four defining-vocabulary violations fixed by rewording (*competent→skilled, arrangement→way, combine→put together, specified→particular*, plus three in *bad-adj*: *severe, behaving, spoiled, unfortunate*). Gate, caps, links, 305 tests, lint_vocab (0 violations) and crossref (0 errors, new back-links applied) all pass. Spend: US$0.45 this run, US$2.18 today.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions; give each a full dedicated run rather than folding into a mixed batch. The band-1 noun/verb/adjective backlog is still large (~1,000 nouns, ~400 verbs, ~340 adjectives pending) — keep diversifying rather than returning to prepositions/pronouns for a while.
2. **review**: ~190 `reviewed` entries have had only one panel round; pick the block by `params.block_size` when review is next selected.
3. **closure**: 430+ cross-reference/family targets with no entry, growing — this run added *unable-adj, capable-adj, skilled-adj, real-adj, imaginary-adj, worried-adj, nervous-adj, calm-adj, eager-adj, aware-adj, poor-adj, severe-adj, refuse-v, reject-v, remove-v, subtract-v* and more (word-family and antonym gaps from the 13 new entries).
4. Next **lint** due in about 3 runs (was pushed to run 24 last lint pass; unchanged).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a` `pronunciation` and `label` as precision candidates approaching or receding from the 30-percent line (unchanged since the last lint pass).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- A region label means "mainly used in," not "exclusively"; do not let a reviewer's literal reading override a genuine AmE/BrE split.
- "Off of", "out of" without "of" in informal American speech, "inside of", "outside of", "near to", "on to" are standard variants or common informal forms; do not flag them as learner errors, but do keep wording about them hedged (not absolute) — a reviewer caught over-prescriptive phrasing on *off-prep* this run.
- A single "out"/"out of" preposition entry, covering the *of*-optional pattern as one entry, matches major dictionary precedent; don't split it into a separate "out-of-prep" headword without an owner decision.
- Adaptation notes are language-neutral: never name a specific language (French, Spanish, Japanese...); hedge with "some/many languages" instead. Caught on *actual-adj* this run — check false-friends notes especially.
- A restriction on one variation of a sense (e.g., "of food") belongs in the subsense's `explanation`, never as a prefix inside its `definition`.
- Attributive-only / predicative-only codes are easy to over-apply; verify with a real counter-example before using either on a common adjective sense.
- Watch for a preposition's own headword slipping unmarked into its own definition.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items: *several-det*, *ourselves-pron*, *themselves-pron*, *beyond-prep* (British pronunciation, prior runs), and new this run — *per-prep* and *adult-n* (American pronunciation, CMU sided with the drafter), *accept-v* (British pronunciation, no open data); the `additional-n` decline (informational, resolved).
