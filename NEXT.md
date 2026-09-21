# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the twenty-seventh scheduled Routine run (review mode).*

## State

- 250 entries, all `reviewed` (0 `draft`). Queue: 4,119 pending, 250 done, 4 duplicate, 9 declined.
- Review mode (selector: highest scheduler debt; 204 entries reviewed only once, no drafts, no markup-pending). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- The unit: second panel round on the 20 oldest one-round entries from the seed set: *the, an, a, hand, money, have, do, used-to, must, un-, however, -ness, very, o'clock, TV, anyway, ASAP, both, enough, every*.
- Panel: 74 issues, 53 blocking, 58 applied, 16 rejected. Precision this run: reviewer-a 0.797, reviewer-b 0.733.
- Structural fix (both reviewers agreed): *the*'s correlative "the more, the better" is an adverb, not a determiner; removed from *the-det*, queued *the-adv* (band 1, source crossref), style guide's model-entry description updated to match. *very-adv* lost "very own"/"very same" from sense 2 for the same reason (those are adjective uses, per Merriam-Webster); *very-adj* was already queued.
- Fact-check via web search found three *-ness* learner-error entries (*curiousness, strongness, difficultness*) are all real, if rare, dictionary words, not errors — removed. Also verified "quite" (British/American split) and "could do with" (current in American English too, region label removed from *do-v*) before editing.
- New tooling note: `inflect.py`'s uncountable-noun short-circuit means a rare recognized plural (*monies* for *money*) can never be recorded via the exceptions table; documented in `wiki/notes/inflect-uncountable-plural-gap.md`, fix due later.
- Notable rejections: reviewer-a's stress-mark complaints on `tv-abbr` and `asap-abbr` (both transcriptions were already correct); the `-ness` stress-neutral pronunciation claim (genuinely exceptionless); `both-det`'s "both sides"/"both ways" collocations (genuine determiner+noun phrases, like "every day").
- Gate, caps, links, 305 tests, lint_vocab and crossref gates all pass. Spend: US$0.89 this run, US$3.20 today.

## Queue (work top-down, one unit at a time)

1. **build**: *on* and *over* — the two heaviest remaining band-1 prepositions, still deferred; otherwise keep diversifying into the band-1 noun/verb/adjective backlog (e.g. *ability, accent, absorb, admire, active, alive*).
2. **review**: 184 `reviewed` entries remain at only one panel round (204 minus this run's 20); pick the next block by `params.block_size` when review is next selected.
3. **closure**: 440+ cross-reference/family targets with no entry, still growing; this run added *the-adv* (band 1, split from *the-det*).
4. Next **lint** due in about 2 runs (run ~29).
5. Next **originality** check due around run 30 (forced: multiples of 10).
6. Watch `reviewer-a`'s `pronunciation` family (0.37, 49 at the last lint pass) against the 30-percent line; this run added two more rejected pronunciation claims from reviewer-a, worth checking at the next lint pass.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable and need no extra period before them (`however-adv`'s `haʊˈɛv.ɚ`, `tv-abbr`'s `ˌtiˈvi`); reviewer-a has repeatedly misread this as a placement error — reject on sight unless the entry's own notes disagree.
- A single reviewer repeatedly flagging the same field across rounds with inconsistent reasons, while the other reviewer never flags it, is noise.
- Adaptation notes are language-neutral: never name a specific language; hedge with "often/many languages," never "most/all." A claim about where a word or form comes from (origin, not present-day use) belongs only in `etymology`, never `adaptation` — verified with two open sources this run for `un-prefix`.
- core_idea and every sense's own `.definition` draw on the defining vocabulary; only a headword's own first sense is exempt.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech? — `one-num`/`one-pron` answers the *one* half); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has eight open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep* (pronunciation, prior runs), *per-prep, adult-n, accept-v* (pronunciation, run 22), *additional-n* decline (informational, resolved).
