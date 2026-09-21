# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-21 by the thirtieth scheduled Routine run (build mode).*

## State

- 273 entries, all `reviewed` (0 `draft`). Queue: 4,093 pending, 273 done, 32 claimed, 9 declined, 4 duplicate.
- Build mode (selector: highest scheduler debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Drafted eleven band-1 entries: *act* (noun and verb), *activity, address, adjective, advertise, affect, aim, air, airport, alarm*. First `claim.py --from-queue` call grabbed the whole remaining band-1 preposition set including *on* and *over* (the two heaviest words this file had flagged for deferral); discarded it and hand-claimed the diversified list `NEXT.md` itself suggested.
- Panel: 38 issues, 18 blocking, 35 applied, 3 rejected (precision this run: reviewer-a 0.905, reviewer-b 0.941). Two reviewer-b parse failures (*activity-n*, *alarm-n*) re-ran cleanly with `--roles reviewer-b`. Rejected two reviewer-a label complaints on *adjective-n* and one reviewer-b markup complaint on the same entry — both cited style-guide rules (entry-level labels, word-named-as-word marks) the reviewer had misread; notes on each decision line.
- Fixed seven defining-vocabulary violations by rewording definitions (*opera, behave* x2, *identifies, aircraft* x2, *broadcast*) rather than adding entries; no script touched a semantic field.
- *affect-v*'s first usage-note draft wrongly implied the word is never a noun; narrowed the claim to the everyday verb sense and queued *affect-n* (the specialized psychology noun) with a `see_also` link.
- All eleven pass `validate.py --gate`, `lint_vocab.py`, `crossref.py --apply --queue`, `queue.py stamp`; status `reviewed`. 28 closure/crossref targets queued (*law-n, behave-v, perform-v, hobby-n, speech-n, affected-adj, airline-n, airplane-n, alarm-v*, and others).
- Mechanical checks: caps, links, gate, 305 unit tests, lint_vocab and crossref gates all pass.
- Spend: US$0.35 this run (pronunciation panel + review panel; both reviewer-b reruns included), US$3.93 today.

## Queue (work top-down, one unit at a time)

1. **build**: keep diversifying band 1; avoid claiming the whole remaining preposition set in one grab (*on, over, up, to, under, through* are all still heavy and unbuilt) — mix in a handful at a time with nouns/verbs/adjectives, as this run did.
2. **review**: 207 `reviewed` entries remain at only one panel round; pick the next block by `params.block_size` when review is next selected.
3. **closure**: 471 cross-reference/family targets with no entry, still growing.
4. Next **lint** due in about 5 real runs from here (`runs_since_lint` reset to 1 this run; the duplicate-row inflation noted previously still applies — see [metrics-duplicate-calls](wiki/notes/metrics-duplicate-calls.md), not yet fixed).
5. Next **originality** check due around run 40 (forced: multiples of 10).
6. `next_mode.py --explain` picked **site** as the highest-debt mode after this run finished; the next scheduled run should expect that unless its own signals move it.

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i` (not `iː`) and `ɝ` (not `ɝː`); British keeps `iː`/`ɜː`. IPA stress marks precede the stressed syllable.
- Words inside `schema/defining-vocabulary.txt` may be used in a definition even with no entry yet; only words *outside* that list require an existing entry. The first sense of a defining-vocabulary word's own entry is exempt from the check entirely (warning only); `core_idea` and phrase definitions are never exempt.
- `--decide` needs `--quote` or `--index` when a role raised two distinct issues on the same field; `write_record` merges a role rerun with the earlier successful role's record, so a single-role rerun (e.g. `--roles reviewer-b`) is the fix for a parse failure, not a full rerun.
- Never mutate a list while iterating over it when patching entry JSON by script (caused one runaway process this run, killed before it wrote anything).
- Closed-vocabulary grammar codes must be checked against `schema/vocabularies.json` before rejecting a code as invalid.

## For the owner

- Three items remain open: enable GitHub Pages; open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt` has ten open items, unchanged this run: *several-det, ourselves-pron, themselves-pron, beyond-prep, per-prep, adult-n, accept-v* (pronunciation), *admire-v, adult-adj* (pronunciation), *additional-n* (declined, resolved).
