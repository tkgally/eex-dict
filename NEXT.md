# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-22 by the thirty-seventh scheduled closure run.*

## State

- 330 entries, all `reviewed` (0 `draft`). Queue: 4,123 pending, 32 claimed, 330 done, 21 declined, 4 duplicate (total 4,510).
- Closure mode (selector: highest debt). Pre-flight: no open pull request, no orphan branch, inbox empty; checkout confirmed at `origin/main`'s latest commit.
- Claimed 20 closure-queue slugs; 12 were bogus `lint_vocab.py --queue` pos-guesses (wrong base form of an inflected word, no noun sense for a verb-only word, or a split artifact of "British English"). All 12 declined with reasons on their queue rows; correct replacement forms re-queued: `commit-v`, `gamble-v`, `achievement-n`, `resource-n`, `criticism-n`. See `reviews/needs_curator.txt` for the full account.
- Drafted the remaining 8: *aircraft, album, mathematics, mixture, origin, permission, responsibility, shelter* (1–2 senses each).
- Inflections 8/8 verified (rules, plus `aircraft` from the exceptions table). Pronunciation 16/16 verified, one disputed CMU vote on *responsibility* kept per the two-vote agreement rule.
- Panel: 18 issues (8 blocking), 17 applied, 1 rejected, 0 escalated. One reviewer-b call failed to parse for *permission* and was re-run cleanly. Precision this run: reviewer-a 1.0, reviewer-b 0.875.
- Real content fixes: several illustration phrases wrongly double-asterisked as words-named-as-words (style-guide section 6); an overclaimed *mixture* "keep their own properties" chemistry claim simplified; two absolute "*permission* is never plural" claims softened for technical uses (file permissions); a bad *responsibility* learner-error correction replaced with the natural to-infinitive pattern; a wrong "adjective + noun" collocation type on *shelter* corrected to "noun + noun". Five defining-vocabulary violations in definitions/core ideas reworded to zero (no new vocabulary entries added).
- Mechanical checks all clean: gate, caps, links, 305 unit tests, lint_vocab and crossref gates (0 errors).
- `metrics.py` was called twice this run (before and after `queue.py sync`), reproducing the documented duplicate-row bug (`wiki/notes/metrics-duplicate-calls.md`); left as is, not hand-edited (that file is append-only; a fix belongs in the tool, not a manual rewrite).
- Spend: US$0.21 of the US$1.25 run-budget guideline; US$3.55 of the US$5 today's cap.

## Queue (work top-down, one unit at a time)

1. **lint**: `next_mode.py` forces it now (5 runs since the last one, possibly inflated by 1 from the duplicate metrics row above — re-run `next_mode.py --explain` fresh, do not assume). Precision measurement, `check_caps.py`, `check_links.py`, `crossref.py --all --apply`, `lint_vocab.py --all --queue`, `claim.py --prune`.
2. **review**: 244 `reviewed` entries remain at one panel round (debt 2.40, second highest).
3. **build**: debt 2.85 (highest of all) but lint is forced first per the guard rule.
4. Next originality run due at scheduler run 50 (every 10th); we are at run 47.
5. Newly queued this run: `commit-v`, `gamble-v`, `achievement-n`, `resource-n`, `criticism-n` (closure, replacing bogus rows); plus crossref/family targets from the 8 new entries (`airplane-n`, `mathematical-adj`, `mix-v`, `mixed-adj`, `original-adj`, `originally-adv`, `originate-v`, `permit-v`, `permit-n`, `responsible-adj`, `responsibly-adv`, `shelter-v`, `sheltered-adj`, `record-n` already exists).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ` (not `iː`, `ɝː`, `ɔː`); British keeps the length mark.
- A claim about a word's or phrase's origin lives only in `etymology`, never in an `adaptation` note.
- `break-v` sense 4 still has an uncorrected "of X:" definition-prefix bug — a future lint or review pass should fix it.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double. Watch for this mixing up on drafts — caught repeatedly this run on my own new entries, not just by reviewers.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks).
- `reviews/needs_curator.txt`: one new line this run on the recurring pos-guess bug at scale (12/20 claimed slugs bogus); twelve older open items unchanged.
