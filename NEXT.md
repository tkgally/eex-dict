# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-fifth scheduled review run.*

## State

- 310 entries, all `reviewed` (0 `draft`). Queue: 4,118 pending, 32 claimed, 310 done, 9 declined, 4 duplicate (total 4,473).
- Review mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Took the 20 oldest `reviewed` entries with only one panel round (block size 20): *good, water, house, bank, head, thing, way, time, color, record* (n and v), *shit, people, news, family, x-ray, all, another, any, either*. `reviewed_once_only` now 224 (was 244).
- Panel: 113 issues (86 blocking), 70 applied, 43 rejected, 0 escalated. Precision 0.62 both roles this run.
- Real content fixes: false House-of-Lords claim in *house*; any/some overgeneralizations in *any*; a biology-only label on a sense covering languages too in *family*; raw IPA/jargon in several pronunciation notes; a countability bug in *water*. Moved four misplaced non-determiner uses out per the one-part-of-speech rule (*at all*/*all in all*, *either ... or*, *time* sense 7 the multiplication use); queued the three entries this needs: `all` (adv), `either` (conj), `times` (prep).
- Reviewer-suggested wording twice broke defining-vocabulary discipline (*ethnic*, *origin*, *album*, plus pre-existing *congress*, *gambling*, *shelter* already in *house*); reworded all six definitions to stay inside `schema/defining-vocabulary.txt` and queued the six words instead of drafting them mid-review.
- Mechanical checks all clean: gate, caps, links, 305 unit tests, lint_vocab (0 violations after the vocabulary fixes above), crossref (0 errors, 902 missing targets, growing as expected).
- Spend: US$1.54 of the US$1.25 run-budget guideline (the panel call for 19 entries alone cost $1.53; no further paid calls taken this run once over) of US$2.95 today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **closure** or **build**: `next_mode.py` now reports build=2.20 and closure=2.40 debt (closure highest, but the tool selected build last time it was checked here — re-run `next_mode.py --explain` fresh, do not assume). `queue_closure` is 533 and growing.
2. **review**: 224 `reviewed` entries remain at one panel round.
3. **lint**: 2 runs since the last one; check `next_mode.py --explain` for the forced threshold.
4. Six pre-existing `link override target has no entry` warnings, now seven with `all-adv` added this run (all harmless, all queued).
5. Next originality run due at run 50 (every 10th); we are at run 44 (metrics run counter) / run 35 (routine count) — check `next_mode.py --explain`'s `runs_total`.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. A reviewer flagging this is itself wrong — confirmed again this run on *any-det* (rejected).
- `tools/entry_path.py <slug>` always prints a deterministic path and exits 0, whether or not the file exists. Checking existence needs a real file test (`[ -f "$(...)" ]`), never the command's success alone — a wrong assumption here this run nearly mis-queued *gambling* as a duplicate of a nonexistent `gamble-v` (caught and reverted before commit).
- A word outside `schema/defining-vocabulary.txt` may go in a definition/explanation/core_idea only when its own entry exists; check the vocabulary file directly before accepting a reviewer's proposed rewording of a definition, or queue the word and use different phrasing instead.
- "Another one" is determiner + pro-noun "one" (like "another day"), not a pronoun use of *another* — a reviewer flagging this is wrong.
- Phrases/collocations that are genuinely a different part of speech than the host entry (adverb, conjunction) get removed and the missing entry queued with `queue.py add ... --source crossref`, per the *the* (adv) and *either* (adv) precedent.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` unchanged this run (twelve open items, no new escalations).
