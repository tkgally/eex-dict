# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the forty-eighth scheduled lint run.*

## State

- 330 entries, all `reviewed` (0 `draft`). Queue: 4,155 pending, 0 claimed, 330 done, 21 declined, 4 duplicate (total 4,510).
- Lint mode (selector: forced, 5 runs since the last). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Mechanical checks all clean: `check_caps`, `check_links`, 305 unit tests, `lint_vocab --all --queue` (0 violations), `crossref --all --apply` (6 entries gained back-links, 0 errors). `claim.py --prune` removed 3 stale claim files.
- Precision (`metrics.py --precision`, all-time): the five disabled `(role, family)` pairs unchanged (`reviewer-a` example-policy/grammar-code/sense-structure, `reviewer-b` example-policy/explanation). `reviewer-a` overall 0.69 (1138/1649, up from 0.68); `reviewer-b` 0.70 (442/630, up from 0.69). No new switch-offs; nearest live family to the 30-percent floor is `reviewer-a` `pronunciation` at 0.34. Logged in `wiki/notes/reviewer-precision.md`.
- Judgmental pass found and fixed two real problems: (1) `wiki/index.md` still described two tooling notes as "fix due a later run" when both fixes landed in code 2026-09-20 — corrected. (2) `queue-stale-claimed-rows` had spread past its first sighting: all 32 `claimed` queue rows (16 conjunctions, 16 prepositions) had zero backing claim file anywhere. Freed all 32 to `pending` by hand (the note's documented workaround); `queue.py counts` now shows `claimed=0`. The underlying tool gap (no automatic reset of an orphaned `claimed` row) is still unfixed and will recur.
- Confirmed still open, deliberately not touched (needs the paid review panel, this run's budget was $0): `break-v` sense 4's "of X:" definition-prefix style bug (`senses[3].definition`), first flagged by the last closure run.
- Spend: US$0 of this run's $0 budget; US$3.55 of the US$5 today's cap.

## Queue (work top-down, one unit at a time)

1. **build**: debt 3.40 (highest of all eligible modes per `next_mode.py --explain`), budget $1.25. The 32 just-freed rows include 16 high-value band-1 conjunctions and 16 band-1 prepositions (*after, although, as, before, but, if, nor, once, or, since, so, than, that, though, unless, until, on, over, such as, through, throughout, to, toward, towards, under, up, upon, via, with, within, without*) — good candidates for this run's claim.
2. **review**: debt 2.60; 244 `reviewed` entries remain at one panel round.
3. **closure**: debt 0.80.
4. Next lint pass due at scheduler run 53 (5 after this one, run 48).
5. Next originality run due at scheduler run 50 (every 10th); we are at run 48.
6. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly" with the restriction moved to `explanation` or left to the existing collocations, per style guide line 33 (no "of X:" prefix inside a definition). Full pipeline required (it's a semantic-field rewrite).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ` (not `iː`, `ɝː`, `ɔː`); British keeps the length mark.
- A claim about a word's or phrase's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Watch for this mixing up on drafts.
- A queue row's `claimed` status can go stale (orphaned branch, or a release that forgot to reset it to `pending`) with no tool to catch it yet; `wiki/notes/queue-stale-claimed-rows.md` has the workaround. Check `queue.py counts` for `claimed > 0` occasionally between lint passes.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks). Question 2 (reviewer-b's tier) now leans toward "no upgrade needed" — see `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged this run, thirteen open items.
