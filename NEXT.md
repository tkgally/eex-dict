# NEXT.md — baton (hard cap 60 lines; rewrite, don't append)

*Rewritten 2026-09-23 by the fiftieth scheduled run (originality).*

## State

- 342 entries, all `reviewed` (0 `draft`). Queue: 4,147 pending, 0 claimed, 342 done, 21 declined, 4 duplicate (total 4,514).
- This run: the fourth originality check (`reviews/originality/2026-09-23.md`). 10 sampled fields: 4 original, 4 generic-overlap, 2 rewritten (`airport-n` sense 1; `action-n` phrase *actions speak louder than words*), both through the full pipeline (2 minor issues, both applied).
- Repaired `wiki/log.md`'s header line, which the forty-ninth run's entry had been spliced into. Log entries go below the italic header line, never inside it.
- Pre-flight: no open pull request, no orphan branch, inbox empty.
- Spend: US$0.08 of this run's US$0.10; US$0.44 of today's US$5 cap.

## Queue (work top-down, one unit at a time)

1. **build**: the four remaining band-1 conjunctions *as, so, than, that* (each large; two or three per run is plenty), then the 16 band-1 prepositions (*on, over, such as, through, throughout, to, toward, towards, under, until, up, upon, via, with, within, without*). *towards* is the British form of *toward*: record it as a variant of `toward-prep` and mark its queue row `duplicate` rather than drafting a second entry.
2. **review**: 244 `reviewed` entries remain at one panel round.
3. **closure**: 552 closure-gap lemmas.
4. Next lint pass due at scheduler run 53; next originality run due at scheduler run 60 (this was run 50).
5. When drafting or reviewing touches `break-v`: fix sense 4's definition from "of weather, or of something that has been hidden: begin suddenly" to "begin suddenly", restriction moved to `explanation` (style guide section 4). Full pipeline required.
6. Tooling fixes due (notes in `wiki/notes/`): `review-panel-rerun-duplicate-records`, `queue-stale-claimed-rows`, `metrics-duplicate-calls`, `lint-vocab-queue-note-duplication`, `inflect-uncountable-plural-gap`; and consider adding the "quote the source or do not answer copied" sentence to the reviewer question in `tools/originality_check.py` (`wiki/notes/reviewer-noise.md`, 2026-09-23 update).

## Fences (do not re-grind)

- The charter decisions in `wiki/decisions/` are the owner's; do not reopen them.
- American IPA drops the length mark on `i`, `ɝ`, and `ɔ`; British keeps it.
- A claim about a word's origin lives only in `etymology`, never in an `adaptation` note.
- Illustration phrases (`*give permission*`) take a single asterisk; only a word named as a word (`**permission**`) takes double.
- A conjunction entry points to the preposition's **-ing** use (*after finishing*) only as the other part of speech, in one clause; reviewer-a flags anything more as mixing parts of speech (fixed on `after-conj` and `before-conj` this run).
- *if ... or not* is standard English; only directly before **or not** is **whether** required (a rejected reviewer claim on `if-conj`).
- A queue row's `claimed` status can go stale; check `queue.py counts` for `claimed > 0` between lint passes (workaround in `wiki/notes/queue-stale-claimed-rows.md`).
- Call `metrics.py` once per run, in wrap-up only.

## For the owner

- The public site is live: <https://tkgally.github.io/eex-dict/>.
- Two open questions remain: open question 4 (split *be/have/do/one* by part of speech?); open question 5 (the look of the marks). See `wiki/open-questions.md`.
- `reviews/needs_curator.txt`: unchanged this run, thirteen open items.
